// SPDX-License-Identifier: GPL-3.0-or-later

using Godot;

namespace OnslaughtRebuild.GodotClient;

/// <summary>
/// Test-only adapter for the unchanged verified media provider. The actual
/// scene check may persist the resulting plain Variant dictionary to its
/// explicitly selected, owned local-data fixture, then rerun with the standard
/// engine. This adapter never reads a permissive replacement manifest.
/// </summary>
public sealed partial class StartupSceneCheckMedia : RefCounted
{
    private readonly AudioPlaybackRetirement _retirement = new();
    private int _completions;

    public Godot.Collections.Dictionary LoadVerifiedMedia(string mediaRoot) =>
        RetailStartupSequence.LoadVerifiedMediaBatch(mediaRoot);

    public Node CreateInitializedBridge(string mediaRoot)
    {
        var bridge = RetailStartupSequence.InstantiateScene();
        bridge.PlaybackRetirement = _retirement;
        bridge.Completed += () => _completions++;
        bridge.InitializeForClip(mediaRoot, RetailStartupCue.Level100IntroCutscene, RetailStartupClockMode.Wall);
        return bridge;
    }

    public Godot.Collections.Dictionary BridgeSnapshot(Node node)
    {
        var bridge = (RetailStartupSequence)node;
        return new()
        {
            ["scheduled_seconds"] = bridge.ScheduledSeconds,
            ["missing_count"] = bridge.MissingCues.Count,
            ["unavailable"] = bridge.MediaUnavailableReason ?? string.Empty,
            ["presentation"] = bridge.Presentation,
            ["completions"] = _completions,
            ["pending_audio"] = _retirement.PendingCount,
        };
    }

    public void AbortBridge(Node node) => ((RetailStartupSequence)node).AbortForHarness();
    public void DisposeRetirement() => _retirement.Dispose();
}
