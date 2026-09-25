// SPDX-License-Identifier: GPL-3.0-or-later

using Godot;
using GDictionary = Godot.Collections.Dictionary;

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
        LoadReferenceBatch(mediaRoot);

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

    // Temporary C# oracle: production admission lives in startup_media_batch.gd.
    private static GDictionary LoadReferenceBatch(string mediaRoot)
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
