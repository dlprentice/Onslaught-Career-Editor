// SPDX-License-Identifier: GPL-3.0-or-later

using Godot;
using OnslaughtRebuild.Client;

namespace OnslaughtRebuild.GodotClient;

public enum RetailFrontendEditorPage
{
    ClickToStart, MainMenu, QuitConfirm, CareerName, LevelSelect,
    MissionBriefing, SelectConfiguration, Loading, Options,
}

public sealed partial class RetailFrontendFlow
{
    public const string ProductionScenePath = "res://Scenes/Frontend/Frontend.tscn";

    [Export] public RetailFrontendAssetPaths AssetPaths { get; set; } = new();
    private RetailFrontendEditorPage _editorPage = RetailFrontendEditorPage.MainMenu;
    [Export]
    public RetailFrontendEditorPage EditorPage
    {
        get => _editorPage;
        set
        {
            _editorPage = value;
            if (Engine.IsEditorHint() && _initialized)
            {
                SetEditorPage();
                QueueRedraw();
            }
        }
    }

    private readonly Dictionary<string, RetailFrontendPart> _sceneParts = new(StringComparer.Ordinal);
    private readonly Dictionary<string, RetailTextureRect> _nativeTextures = new(StringComparer.Ordinal);
    private readonly Dictionary<string, Color> _nativeTints = new(StringComparer.Ordinal);
    private Control? _stage;
    private RetailFrontendPart? _paintingPart;
    private string _drawingSection = string.Empty;

    public static RetailFrontendFlow InstantiateScene() =>
        GD.Load<PackedScene>(ProductionScenePath).Instantiate<RetailFrontendFlow>();

    private void BindSceneParts()
    {
        _stage = GetNode<Control>("Stage");
        foreach (Node node in _stage.FindChildren("*", nameof(Control), true, false))
        {
            if (node is RetailFrontendPart part)
            {
                if (!_sceneParts.TryAdd(part.Section, part))
                    throw new InvalidDataException($"Duplicate frontend scene section '{part.Section}'.");
            }
        }
        foreach (Node node in _stage.FindChildren("*", "TextureRect", true, false))
        {
            if (node is RetailTextureRect texture)
            {
                string key = _stage.GetPathTo(texture).ToString();
                _nativeTextures.Add(key, texture);
                _nativeTints.Add(key, texture.SelfModulate);
            }
        }
        if (_sceneParts.Count == 0)
            throw new InvalidDataException("Frontend must be instantiated from its production scene.");
        _nativeTextures["MainMenu/TitleLogo/Body"].ItemRectChanged += UpdateTitleLogoReflection;
        Resized += FitSceneStage;
        FitSceneStage();
    }

    private void FitSceneStage()
    {
        if (_stage is null) return;
        (float scale, Vector2 offset) = DesignTransform();
        _stage.Position = offset;
        _stage.Scale = new Vector2(scale, scale);
        UpdateTitleLogoReflection();
    }

    private void SetEditorPage()
    {
        // Construct only the frontend's in-memory navigation model. No host
        // events, input polling, career files, playback or game session runs.
        _session?.Dispose();
        _session = new GdFrontendSession();
        _clickPulseTimer = 5d;
        _clickPageSeconds = 5d;
        _animationSeconds = 0d;
        _feBackSeconds = 0d;
        _mainTransitionCount = 0;
        _mainTransitionTime = 0;
        if (_editorPage == RetailFrontendEditorPage.ClickToStart) return;
        _session.Confirm();
        if (_editorPage == RetailFrontendEditorPage.MainMenu) return;
        if (_editorPage is RetailFrontendEditorPage.QuitConfirm or RetailFrontendEditorPage.Options)
        {
            _session.SelectMainIndex(_editorPage == RetailFrontendEditorPage.QuitConfirm ? 6 : 5);
            _session.Confirm();
            return;
        }
        _session.Confirm();
        if (_editorPage == RetailFrontendEditorPage.CareerName) return;
        _session.Confirm();
        if (_editorPage == RetailFrontendEditorPage.LevelSelect) return;
        _session.Confirm();
        if (_editorPage == RetailFrontendEditorPage.MissionBriefing) return;
        _session.Confirm();
        if (_editorPage == RetailFrontendEditorPage.SelectConfiguration) return;
        _session.Confirm();
    }

    private new void QueueRedraw()
    {
        base.QueueRedraw();
        if (_stage is null || !_initialized) return;
        RetailFrontendScreen screen = _session.Screen;
        foreach (Control page in _stage.GetChildren().OfType<Control>())
        {
            page.Visible = page.Name.ToString() switch
            {
                "MainMenu" => screen is RetailFrontendScreen.MainMenu or RetailFrontendScreen.QuitConfirm,
                "ClickToStart" => screen == RetailFrontendScreen.ClickToStart,
                "QuitConfirm" => screen == RetailFrontendScreen.QuitConfirm,
                "CareerName" => screen == RetailFrontendScreen.DevSelect,
                "LevelSelect" => screen == RetailFrontendScreen.LevelSelect,
                "MissionBriefing" => screen == RetailFrontendScreen.MissionBriefing,
                "SelectConfiguration" => screen == RetailFrontendScreen.SelectConfiguration,
                "Loading" => screen == RetailFrontendScreen.Loading,
                "Options" => screen == RetailFrontendScreen.Options,
                "Debriefing" => screen == RetailFrontendScreen.Debriefing,
                _ => false,
            };
        }
        UpdateNativeTextures();
        UpdateOptionsFrame();
        foreach (RetailFrontendPart part in _sceneParts.Values)
            part.QueueRedraw();
        UpdateTitleLogoReflection();
    }

    private void UpdateNativeTextures()
    {
        float fade = Clamp01((MainMenuTransition - 0.75f) * 4f);
        float iconFade = Clamp01((MainMenuTransition - 0.8f) * 5f);
        for (int index = 0; index < 3; index++)
            BindNativeTexture($"MainMenu/Writing/Tile{index}", _forsetiWritingLarge, fade);
        int language = Math.Clamp((int)_session.Language, 0, _languageFlags.Length - 1);
        BindNativeTexture("MainMenu/Language/Flag", _languageFlags[language], fade);
        bool arrows = RetailMainMenuLanguageBlink.ShouldDraw(
            RetailMainMenuLanguageBlink.ImageInitialCounter, RetailMainMenuLanguageBlink.ImageInitialTimer);
        BindNativeTexture("MainMenu/Language/LeftChevron", _feArrow, arrows ? fade : 0f);
        BindNativeTexture("MainMenu/Language/RightChevron", _feArrow, arrows ? fade : 0f);
        Texture2D icon = _menuIcons[_session.SelectedMainIndex];
        BindNativeTexture("MainMenu/SelectedIcon/ShadowMotion/Shadow", icon, iconFade);
        BindNativeTexture("MainMenu/SelectedIcon/Body", icon, iconFade);
        if (!_session.SelectedMainItem.IsAvailable)
            _nativeTextures["MainMenu/SelectedIcon/Body"].SelfModulate =
                new Color(ReleasedUnavailable, ReleasedUnavailable.A * iconFade);
        BindNativeTexture("MainMenu/TitleLogo/ShadowMotion/Shadow", _titleLogo, 1f);
        BindNativeTexture("MainMenu/TitleLogo/Body", _titleLogo, 1f);
        var shadow = RetailFrontendDecorShadow.OffsetAtPhase(
            RetailFrontendDecorShadow.PhaseAtSeconds(_animationSeconds));
        Vector2 offset = new((float)shadow.X, (float)shadow.Y);
        // Animation owns only the motion wrapper. The texture's authored
        // Position/Size remain editable, and saving/reopening cannot accumulate
        // the current phase offset into the next run's baseline.
        _stage!.GetNode<Control>("MainMenu/SelectedIcon/ShadowMotion").Position = offset;
        _stage.GetNode<Control>("MainMenu/TitleLogo/ShadowMotion").Position = offset;
        BindNativeTexture("Loading/Background", _loadingScreen, 1f);
    }

    private void BindNativeTexture(string key, Texture2D texture, float fade)
    {
        RetailTextureRect control = _nativeTextures[key];
        control.Texture = texture;
        Color tint = _nativeTints[key];
        control.SelfModulate = new Color(tint, tint.A * fade);
    }

    internal void DrawScenePart(RetailFrontendPart part)
    {
        if (!_initialized || part.SourceRect.Size.X <= 0f || part.SourceRect.Size.Y <= 0f) return;
        _paintingPart = part;
        _drawingSection = string.Empty;
        try
        {
            DrawSetTransform(Vector2.Zero, 0f, Vector2.One);
            string prefix = part.Section.Split('.')[0];
            switch (prefix)
            {
                case "Main": DrawMainMenu(); break;
                case "Click": DrawClickToStart(); break;
                case "Career": DrawDevSelect(); break;
                case "Briefing": DrawMissionBriefing(); break;
                case "Configuration": DrawSelectConfiguration(); break;
                case "Loading": DrawLoading(); break;
                case "Quit": DrawQuitConfirm(); break;
                case "LevelSelect": DrawLevelSelect(); break;
                case "Debriefing": DrawDebriefing(); break;
                default: throw new InvalidDataException($"Unknown frontend scene section '{part.Section}'.");
            }
        }
        finally
        {
            _paintingPart = null;
            _drawingSection = string.Empty;
        }
    }

    private void SelectSceneSection(string section) => _drawingSection = section;
    private bool DrawsSceneSection => _paintingPart is not null && _paintingPart.Section == _drawingSection;
    private string SceneText(string importedText) =>
        DrawsSceneSection && _paintingPart!.OverrideText ? _paintingPart.Text : importedText;

    private new void DrawSetTransform(Vector2 position, float rotation = 0f, Vector2? scale = null)
    {
        if (_paintingPart is null) return;
        Vector2 ratio = _paintingPart.Size / _paintingPart.SourceRect.Size;
        var authored = new Transform2D(new Vector2(ratio.X, 0f), new Vector2(0f, ratio.Y),
            -_paintingPart.SourceRect.Position * ratio);
        var measured = new Transform2D(rotation, scale ?? Vector2.One, 0f, position);
        _paintingPart.DrawSetTransformMatrix(authored * measured);
    }

    private new void DrawRect(Rect2 rect, Color color, bool filled = true, float width = -1f, bool antialiased = false)
    {
        if (DrawsSceneSection) _paintingPart!.DrawRect(rect, color, filled, width, antialiased);
    }

    private new void DrawTextureRect(Texture2D texture, Rect2 rect, bool tile, Color? modulate = null, bool transpose = false)
    {
        if (DrawsSceneSection) _paintingPart!.DrawTextureRect(texture, rect, tile, modulate, transpose);
    }

    private new void DrawTextureRectRegion(Texture2D texture, Rect2 rect, Rect2 source, Color? modulate = null,
        bool transpose = false, bool clipUv = true)
    {
        if (DrawsSceneSection) _paintingPart!.DrawTextureRectRegion(texture, rect, source, modulate, transpose, clipUv);
    }

    private new void DrawLine(Vector2 from, Vector2 to, Color color, float width = -1f, bool antialiased = false)
    {
        if (DrawsSceneSection) _paintingPart!.DrawLine(from, to, color, width, antialiased);
    }

    private new void DrawArc(Vector2 center, float radius, float startAngle, float endAngle, int pointCount,
        Color color, float width = -1f, bool antialiased = false)
    {
        if (DrawsSceneSection) _paintingPart!.DrawArc(center, radius, startAngle, endAngle, pointCount, color, width, antialiased);
    }

    private new void DrawPolyline(Vector2[] points, Color color, float width = -1f, bool antialiased = false)
    {
        if (DrawsSceneSection) _paintingPart!.DrawPolyline(points, color, width, antialiased);
    }
}
