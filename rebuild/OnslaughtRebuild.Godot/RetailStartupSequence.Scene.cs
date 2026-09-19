// SPDX-License-Identifier: GPL-3.0-or-later

using System.Globalization;
using System.Text.Json;
using Godot;

namespace OnslaughtRebuild.GodotClient;

public sealed partial class RetailStartupSequence
{
    public const string ProductionScenePath = "res://Scenes/Frontend/Startup.tscn";

    private Control _stage = null!;
    private RetailTextureRect _videoSurface = null!;
    private Control _splashFade = null!;
    private RetailTextureRect _splashSurface = null!;
    private string? _editorProblem;
    private RetailStartupCue _editorCue = RetailStartupCue.Splash;

    /// <summary>
    /// Selects one actual decoded still/frame for inspection. It never advances
    /// the schedule, reads audio, emits completion or creates a game session.
    /// </summary>
    [Export]
    public RetailStartupCue EditorCue
    {
        get => _editorCue;
        set
        {
            _editorCue = value;
            if (Engine.IsEditorHint() && _stage is not null) ShowEditorStill();
        }
    }

    public static RetailStartupSequence InstantiateScene() =>
        GD.Load<PackedScene>(ProductionScenePath).Instantiate<RetailStartupSequence>();

    private void BindSceneSurface()
    {
        _stage = GetNode<Control>("Stage");
        _videoSurface = GetNode<RetailTextureRect>("Stage/Video");
        _splashFade = GetNode<Control>("Stage/SplashFade");
        _splashSurface = GetNode<RetailTextureRect>("Stage/SplashFade/Splash");
        Resized += FitSceneStage;
        FitSceneStage();
    }

    private void FitSceneStage()
    {
        float scale = Mathf.Min(Size.X / DesignWidth, Size.Y / DesignHeight);
        _stage.Position = new Vector2(
            (Size.X - (DesignWidth * scale)) * 0.5f,
            (Size.Y - (DesignHeight * scale)) * 0.5f);
        _stage.Scale = new Vector2(scale, scale);
    }

    private new void QueueRedraw()
    {
        if (Engine.IsEditorHint() || !_initialized || _stage is null) return;
        RetailStartupFrame frame = _schedule.Sample(_elapsedSeconds);
        _videoSurface.Visible = false;
        _splashFade.Visible = false;
        if (frame.Kind == RetailStartupFrameKind.Splash)
        {
            _splashSurface.Texture = _splashTexture;
            // The fade wrapper owns animation, leaving the actual texture's
            // native Position/Size/tint editable and safe to save at any phase.
            _splashFade.Modulate = new Color(1f, 1f, 1f, frame.Alpha);
            _splashFade.Visible = _splashTexture is not null;
        }
        else if (frame.Kind == RetailStartupFrameKind.Video && frame.Cue is { } cue &&
                 EnsureFrameResident(cue, frame.FrameIndex))
        {
            // The actual scene owns the measured (0,40)-(640,440) quad and
            // 0xFFFEFEFE tint. Native Mix blending is SRCALPHA/INVSRCALPHA.
            // Frame selection and the two reused buffers remain unchanged.
            _videoSurface.Texture = _videoBuffers[_presentedBuffer];
            _videoSurface.Visible = true;
        }
    }

    public override string[] _GetConfigurationWarnings() =>
        Engine.IsEditorHint() && _editorProblem is { } problem ? [problem] : [];

    private void ShowEditorStill()
    {
        _videoSurface.Visible = false;
        _splashFade.Visible = false;
        _videoSurface.Texture = null;
        _splashSurface.Texture = null;
        _editorProblem = null;
        try
        {
            string mediaRoot = ResolveMediaRoot(OS.GetCmdlineUserArgs());
            if (string.IsNullOrWhiteSpace(mediaRoot))
                throw new InvalidDataException("Set BEA_LOCAL_LAB or ONSLAUGHT_STARTUP_MEDIA to inspect decoded startup media.");
            // Read only the existing routing manifest and one selected image.
            // Runtime still uses the full verified RetailStartupMediaIndex; an
            // editor illustration is not a claim that the clip cache validates.
            using JsonDocument manifest = JsonDocument.Parse(File.ReadAllText(
                Path.Combine(mediaRoot, "startup-media.json")));
            JsonElement root = manifest.RootElement;
            if (root.GetProperty("schema").GetString() != RetailStartupMediaIndex.Schema)
                throw new InvalidDataException("Startup media manifest has an unsupported schema.");
            bool splash = _editorCue == RetailStartupCue.Splash;
            string relative = splash
                ? root.GetProperty("stills").GetProperty(nameof(RetailStartupCue.Splash)).GetProperty("path").GetString()!
                : string.Format(CultureInfo.InvariantCulture,
                    root.GetProperty("clips").GetProperty(_editorCue.ToString()).GetProperty("framePathFormat").GetString()!, 1);
            string mediaDirectory = Path.GetFullPath(mediaRoot).TrimEnd(Path.DirectorySeparatorChar) + Path.DirectorySeparatorChar;
            string imagePath = Path.GetFullPath(Path.Combine(mediaDirectory, relative));
            if (!imagePath.StartsWith(mediaDirectory, StringComparison.Ordinal))
                throw new InvalidDataException("Startup image routing must stay inside its selected media cache.");
            Texture2D texture = LoadImageTexture(imagePath)
                ?? throw new InvalidDataException("The selected decoded startup image is unavailable.");
            if (splash)
            {
                _splashSurface.Texture = texture;
                _splashFade.Modulate = Colors.White;
                _splashFade.Visible = true;
            }
            else
            {
                _videoSurface.Texture = texture;
                _videoSurface.Visible = true;
            }
        }
        catch (Exception error) when (error is IOException or UnauthorizedAccessException or
                                     JsonException or KeyNotFoundException or InvalidOperationException or
                                     ArgumentException or FormatException)
        {
            _editorProblem = error.Message;
        }
        UpdateConfigurationWarnings();
    }
}
