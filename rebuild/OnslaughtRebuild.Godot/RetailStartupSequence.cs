// SPDX-License-Identifier: GPL-3.0-or-later

using Godot;
using GDictionary = Godot.Collections.Dictionary;

namespace OnslaughtRebuild.GodotClient;

/// <summary>The presentation clock: capture ticks are silent; wall time can play verified audio.</summary>
public enum RetailStartupClockMode { FixedTick, Wall }

/// <summary>
/// Temporary host bridge. The standard-Godot Startup.tscn owns the complete
/// presentation, schedule, input, two frame buffers and audio lifecycle.
/// This bridge asks the GDScript media provider to admit one cache and forwards
/// completion; it never drives frames, parses media or handles input.
/// </summary>
public sealed partial class RetailStartupSequence : Node
{
    internal AudioPlaybackRetirement PlaybackRetirement { get; set; } = null!;
    public Control Presentation { get; private set; } = null!;
    public event Action? Completed;

    public IReadOnlyList<RetailStartupCue> MissingCues => Presentation.Call("get_missing_cues")
        .AsGodotArray().Select(value => (RetailStartupCue)value.AsInt32()).ToArray();
    public string? MediaUnavailableReason
    {
        get
        {
            string reason = Presentation.Call("get_media_unavailable_reason").AsString();
            return reason.Length == 0 ? null : reason;
        }
    }
    public double ScheduledSeconds => Presentation.Call("get_scheduled_seconds").AsDouble();

    /// <summary>The cache remains outside res:// so exported scenes contain no decoded retail media.</summary>
    public static string ResolveMediaRoot(IReadOnlyList<string> arguments)
    {
        ArgumentNullException.ThrowIfNull(arguments);
        foreach (string argument in arguments)
            if (argument.StartsWith("--startup-media=", StringComparison.Ordinal))
                return argument["--startup-media=".Length..];

        string? configured = System.Environment.GetEnvironmentVariable("ONSLAUGHT_STARTUP_MEDIA");
        if (!string.IsNullOrWhiteSpace(configured)) return configured;
        string? canonicalLab = System.Environment.GetEnvironmentVariable("BEA_LOCAL_LAB");
        if (!string.IsNullOrWhiteSpace(canonicalLab)) return Path.Combine(canonicalLab, "startup-media");
        string? local = System.Environment.GetEnvironmentVariable("LOCALAPPDATA");
        return string.IsNullOrWhiteSpace(local)
            ? string.Empty : Path.Combine(local, "OnslaughtToolkit", "startup-media");
    }

    public void Initialize(string mediaRoot, RetailStartupClockMode clock) =>
        InitializePresentation(mediaRoot, route: 0, RetailStartupCue.Splash, clock);

    public void InitializeForAttract(string mediaRoot, RetailStartupClockMode clock) =>
        InitializePresentation(mediaRoot, route: 1, RetailStartupCue.Splash, clock);

    public void InitializeForClip(string mediaRoot, RetailStartupCue cue, RetailStartupClockMode clock) =>
        InitializePresentation(mediaRoot, route: 2, cue, clock);

    public void AbortForHarness() => Presentation.Call("abort_for_harness");

    private void InitializePresentation(string mediaRoot, int route, RetailStartupCue cue,
        RetailStartupClockMode clock)
    {
        // Preserve the old admission order: a repeated initialization rejects
        // before rereading any input, even if its newly supplied cache is bad.
        if (Presentation.Call("is_initialized").AsBool())
            throw new InvalidOperationException("The startup sequence is already initialized.");
        GDictionary result = Presentation.Call("configure_from_cache", mediaRoot, route,
            (int)cue, (int)clock, Callable.From<AudioStreamPlayer>(ObserveVoiceStart)).AsGodotDictionary();
        if (!result["ok"].AsBool())
            throw new InvalidOperationException(result["error"].AsString());
    }

    private void ObserveVoiceStart(AudioStreamPlayer player) => PlaybackRetirement.Observe(player);
}
