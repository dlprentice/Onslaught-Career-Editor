// SPDX-License-Identifier: GPL-3.0-or-later

using Godot;

namespace OnslaughtRebuild.GodotClient;

/// <summary>
/// Which clock drives the startup media.
/// </summary>
public enum RetailStartupClockMode
{
    /// <summary>
    /// One <c>_Process</c> call advances the sequence by exactly
    /// <c>1 / TicksPerSecond</c> seconds, regardless of the delta the engine
    /// reports. Used for capture and for any parity comparison: the frame
    /// chosen at tick N is then a pure function of N.
    /// </summary>
    FixedTick,

    /// <summary>
    /// The engine's own frame delta advances the sequence. Used for interactive
    /// play, where a dropped frame must cost time rather than slow the movie
    /// down. This is the released behaviour: retail's Bink path is clock-paced
    /// and logs "%i frames played, %i frames skipped".
    /// </summary>
    Wall,
}

/// <summary>
/// The cold-start media sequence retail plays before the interactive frontend:
/// the Lost Toys logo movie, the opening montage, and the static splash card.
///
/// <para><b>This is presentation only.</b></para>
/// It touches textures, the filesystem and a clock, so it can never be
/// referenced from <c>OnslaughtRebuild.Core</c>. The deterministic part — which
/// beat is on screen at time t, and which video frame — lives in
/// <see cref="RetailStartupSchedule"/>, which has no Godot types and is unit
/// tested directly.
///
/// <para><b>Residency.</b></para>
/// Exactly ONE decoded frame is resident at a time. The frame is read from the
/// media cache as a PNG and pushed into a single reused <see cref="ImageTexture"/>.
/// Building a texture per frame — the pattern the FEBack strip loader uses for
/// its 286 128² frames — would mean 2,054 textures at 480×300 for the montage
/// alone, and is deliberately not done here.
///
/// <para><b>Nothing is imitated.</b></para>
/// If a clip was not decoded, its beat does not exist and nothing is drawn in
/// its place. If NO media at all is available the sequence reports that and
/// hands straight over to the frontend; it never substitutes hand-made motion
/// for retail footage.
/// </summary>
public sealed partial class RetailStartupSequence : Control
{
    private const float DesignWidth = 640f;
    private const float DesignHeight = 480f;

    /// <summary>
    /// Where a 480×300 clip lands on the 640×480 stage.
    ///
    /// Measured, not assumed: across the eight 2026-07-25 intro reference frames
    /// the per-pixel maximum over all frames is zero above y=40 and below y=440
    /// and non-zero across the full width, so the drawn rectangle is
    /// (0,40)-(640,440). 480×300 is 1.6:1, which at 640 wide is 400 tall, so the
    /// 40-pixel bars are a consequence of the source aspect rather than a
    /// separate authored border.
    /// </summary>
    private const float VideoTop = 40f;
    private const float VideoHeight = 400f;

    /// <summary>
    /// The capture tick. <c>FrontendCaptureRig</c> launches the engine with
    /// <c>--fixed-fps 60</c>, so this matches one <c>_Process</c> call to
    /// 1/60 s of sequence time exactly.
    /// </summary>
    private const double FixedTicksPerSecond = 60d;

    private RetailStartupMediaIndex _media = RetailStartupMediaIndex.Missing("not initialized");
    private RetailStartupSchedule _schedule = null!;
    private RetailStartupClockMode _clock = RetailStartupClockMode.Wall;
    private ImageTexture? _videoTexture;
    private Texture2D? _splashTexture;
    private (RetailStartupCue Cue, int Index)? _residentFrame;
    private double _elapsedSeconds;
    private bool _aborted;
    private bool _completed;
    private bool _initialized;

    /// <summary>Raised once, on the frame the sequence stops owning the screen.</summary>
    public event Action? Completed;

    /// <summary>The cues that had no decoded media. Empty when everything played.</summary>
    public IReadOnlyList<RetailStartupCue> MissingCues => _schedule.MissingCues;

    /// <summary>Why no media was available, or null when the cache was readable.</summary>
    public string? MediaUnavailableReason => _media.Unavailable;

    /// <summary>Total scheduled length in seconds, before any user skip.</summary>
    public double ScheduledSeconds => _schedule.TotalSeconds;

    /// <summary>
    /// Resolves the media cache root. It is deliberately never under
    /// <c>res://</c> — see <see cref="RetailStartupMediaIndex"/> for why.
    /// </summary>
    /// <param name="arguments">Engine user arguments; <c>--startup-media=DIR</c> wins.</param>
    public static string ResolveMediaRoot(IReadOnlyList<string> arguments)
    {
        ArgumentNullException.ThrowIfNull(arguments);

        foreach (string argument in arguments)
        {
            if (argument.StartsWith("--startup-media=", StringComparison.Ordinal))
            {
                return argument["--startup-media=".Length..];
            }
        }

        string? configured = System.Environment.GetEnvironmentVariable("ONSLAUGHT_STARTUP_MEDIA");
        if (!string.IsNullOrWhiteSpace(configured))
        {
            return configured;
        }

        string? local = System.Environment.GetEnvironmentVariable("LOCALAPPDATA");
        return string.IsNullOrWhiteSpace(local)
            ? string.Empty
            : Path.Combine(local, "OnslaughtToolkit", "startup-media");
    }

    public void Initialize(string mediaRoot, RetailStartupClockMode clock)
    {
        if (_initialized)
        {
            throw new InvalidOperationException("The startup sequence is already initialized.");
        }

        _clock = clock;
        _media = RetailStartupMediaIndex.Load(mediaRoot, File.Exists);
        _schedule = new RetailStartupSchedule(_media.Clips, _media.HasSplash);

        if (_media.HasSplash && _media.SplashRelativePath is { } splash)
        {
            _splashTexture = LoadImageTexture(Path.Combine(_media.Root, splash));
            if (_splashTexture is null)
            {
                // The index said it was there and the read failed. Rebuild the
                // schedule without it rather than drawing a stand-in.
                _schedule = new RetailStartupSchedule(_media.Clips, false);
            }
        }

        _initialized = true;
    }

    public override void _Ready()
    {
        if (!_initialized)
        {
            throw new InvalidOperationException(
                "Initialize the startup sequence before adding it to the tree.");
        }

        AnchorRight = 1f;
        AnchorBottom = 1f;
        MouseFilter = MouseFilterEnum.Ignore;
        // Above the frontend flow's ZIndex of 100: while the sequence owns the
        // screen the frontend is not processing, but this makes the ordering
        // explicit rather than dependent on child order.
        ZIndex = 200;

        if (_schedule.IsEmpty)
        {
            if (_media.Unavailable is { } reason)
            {
                GD.PushWarning(
                    $"Startup media unavailable, so splash and intro FMV are absent: {reason}");
            }

            Finish();
            return;
        }

        QueueRedraw();
    }

    public override void _Process(double delta)
    {
        if (_completed)
        {
            return;
        }

        _elapsedSeconds += _clock == RetailStartupClockMode.FixedTick
            ? 1d / FixedTicksPerSecond
            : Math.Max(0d, delta);

        if (_aborted || _elapsedSeconds >= _schedule.TotalSeconds)
        {
            Finish();
            return;
        }

        QueueRedraw();
    }

    public override void _Input(InputEvent inputEvent)
    {
        if (_completed)
        {
            return;
        }

        // Retail's Play() returns non-zero when the user aborts, and the
        // sequencer's `test eax,eax / jne done` after each call means one abort
        // skips every remaining clip rather than only the current one.
        bool abort = inputEvent switch
        {
            InputEventMouseButton button => button.Pressed,
            InputEventKey key => key.Pressed && !key.Echo,
            InputEventJoypadButton pad => pad.Pressed,
            _ => false,
        };

        if (!abort)
        {
            return;
        }

        _aborted = true;
        GetViewport().SetInputAsHandled();
    }

    /// <summary>Skips the sequence from code. Used by the smoke harness.</summary>
    public void AbortForHarness() => _aborted = true;

    public override void _Draw()
    {
        DrawRect(new Rect2(Vector2.Zero, Size), Colors.Black);

        RetailStartupFrame frame = _schedule.Sample(_elapsedSeconds);
        if (frame.Kind is RetailStartupFrameKind.Black or RetailStartupFrameKind.Finished)
        {
            return;
        }

        float scale = Mathf.Min(Size.X / DesignWidth, Size.Y / DesignHeight);
        var offset = new Vector2(
            (Size.X - (DesignWidth * scale)) * 0.5f,
            (Size.Y - (DesignHeight * scale)) * 0.5f);
        DrawSetTransform(offset, 0f, new Vector2(scale, scale));

        if (frame.Kind == RetailStartupFrameKind.Splash)
        {
            if (_splashTexture is { } splash)
            {
                DrawTextureRect(
                    splash,
                    new Rect2(0f, 0f, DesignWidth, DesignHeight),
                    false,
                    new Color(1f, 1f, 1f, frame.Alpha));
            }
        }
        else if (frame.Cue is { } cue && EnsureFrameResident(cue, frame.FrameIndex))
        {
            DrawTextureRect(
                _videoTexture!,
                new Rect2(0f, VideoTop, DesignWidth, VideoHeight),
                false);
        }

        DrawSetTransform(Vector2.Zero, 0f, Vector2.One);
    }

    /// <summary>
    /// Brings one decoded frame into the single resident texture. Returns false
    /// if the frame could not be read, in which case NOTHING is drawn for it —
    /// the letterbox stays black rather than repeating the previous frame,
    /// because a held frame would read as a stall in the footage that retail
    /// does not have.
    /// </summary>
    private bool EnsureFrameResident(RetailStartupCue cue, int frameIndex)
    {
        if (_residentFrame == (cue, frameIndex) && _videoTexture is not null)
        {
            return true;
        }

        string path;
        try
        {
            path = Path.Combine(_media.Root, _media.FrameRelativePath(cue, frameIndex));
        }
        catch (Exception exception)
        {
            GD.PushWarning($"Startup media {cue} frame {frameIndex}: {exception.Message}");
            return false;
        }

        var image = new Image();
        if (image.Load(path) != Error.Ok)
        {
            GD.PushWarning($"Startup media {cue} frame {frameIndex} unreadable at {path}.");
            return false;
        }

        if (_videoTexture is null ||
            _videoTexture.GetWidth() != image.GetWidth() ||
            _videoTexture.GetHeight() != image.GetHeight())
        {
            _videoTexture = ImageTexture.CreateFromImage(image);
        }
        else
        {
            _videoTexture.Update(image);
        }

        _residentFrame = (cue, frameIndex);
        return true;
    }

    private static Texture2D? LoadImageTexture(string path)
    {
        var image = new Image();
        if (image.Load(path) != Error.Ok)
        {
            GD.PushWarning($"Startup splash unreadable at {path}.");
            return null;
        }

        return ImageTexture.CreateFromImage(image);
    }

    private void Finish()
    {
        if (_completed)
        {
            return;
        }

        _completed = true;
        Visible = false;
        SetProcess(false);
        SetProcessInput(false);
        _videoTexture = null;
        _splashTexture = null;
        _residentFrame = null;
        Completed?.Invoke();
    }
}
