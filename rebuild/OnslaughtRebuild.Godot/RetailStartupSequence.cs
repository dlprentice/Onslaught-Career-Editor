// SPDX-License-Identifier: GPL-3.0-or-later

using Godot;
using GDictionary = Godot.Collections.Dictionary;

namespace OnslaughtRebuild.GodotClient;

/// <summary>The presentation clock: capture ticks are silent; wall time can play verified audio.</summary>
public enum RetailStartupClockMode { FixedTick, Wall }

/// <summary>
/// Temporary host bridge. The standard-Godot Startup.tscn owns the complete
/// presentation, schedule, input, two frame buffers and audio lifecycle.
/// This bridge supplies one batch from the existing verified media index and
/// forwards completion; it never drives frames or handles input.
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
        GDictionary batch = LoadVerifiedMediaBatch(mediaRoot);
        GDictionary result = Presentation.Call("configure_verified_media", batch, route,
            (int)cue, (int)clock, Callable.From<AudioStreamPlayer>(ObserveVoiceStart)).AsGodotDictionary();
        if (!result["ok"].AsBool())
            throw new InvalidOperationException(result["error"].AsString());
    }

    private void ObserveVoiceStart(AudioStreamPlayer player) => PlaybackRetirement.Observe(player);

    /// <summary>
    /// One-time language boundary. Only the existing index admits media: its
    /// schema, complete frame inventory, hashes, image envelopes and canonical
    /// WAV checks remain authoritative. The GDScript player receives explicit
    /// admitted paths and never interprets a runtime JSON manifest.
    /// </summary>
    internal static GDictionary LoadVerifiedMediaBatch(string mediaRoot)
    {
        RetailStartupMediaIndex media = RetailStartupMediaIndex.Load(mediaRoot, File.Exists);
        var clips = new GDictionary();
        var frames = new GDictionary();
        var audio = new GDictionary();
        foreach ((RetailStartupCue cue, RetailStartupClip clip) in media.Clips)
        {
            clips[(int)cue] = new GDictionary
            {
                ["frame_count"] = clip.FrameCount,
                ["fps_numerator"] = clip.FramesPerSecondNumerator,
                ["fps_denominator"] = clip.FramesPerSecondDenominator,
                ["width"] = clip.Width,
                ["height"] = clip.Height,
            };
            var paths = new string[clip.FrameCount];
            for (int index = 0; index < paths.Length; index++)
                paths[index] = Path.GetFullPath(Path.Combine(media.Root, media.FrameRelativePath(cue, index)));
            frames[(int)cue] = paths;
        }
        foreach ((RetailStartupCue cue, RetailStartupClipAudio track) in media.ClipAudio)
        {
            audio[(int)cue] = new GDictionary
            {
                ["path"] = Path.GetFullPath(Path.Combine(media.Root, media.AudioRelativePath(cue))),
                ["sample_rate"] = track.SampleRate,
                ["channels"] = track.Channels,
            };
        }
        return new GDictionary
        {
            ["schema"] = "onslaught-startup-verified-batch.v1",
            ["clips"] = clips,
            ["frame_paths"] = frames,
            ["audio"] = audio,
            ["splash_path"] = media.SplashRelativePath is { } splash
                ? Path.GetFullPath(Path.Combine(media.Root, splash)) : string.Empty,
            ["unavailable"] = media.Unavailable ?? string.Empty,
        };
    }
}
