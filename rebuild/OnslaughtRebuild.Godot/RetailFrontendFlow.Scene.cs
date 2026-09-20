// SPDX-License-Identifier: GPL-3.0-or-later

using Godot;
using OnslaughtRebuild.Client;

namespace OnslaughtRebuild.GodotClient;

public enum RetailFrontendEditorPage
{
    ClickToStart, MainMenu, QuitConfirm, CareerName, LevelSelect,
    MissionBriefing, SelectConfiguration, Loading, Options, Debriefing,
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
        if (_sceneParts.Count == 0)
            throw new InvalidDataException("Frontend must be instantiated from its production scene.");
        Resized += FitSceneStage;
        FitSceneStage();
    }

    private void FitSceneStage()
    {
        if (_stage is null) return;
        (float scale, Vector2 offset) = DesignTransform();
        _stage.Position = offset;
        _stage.Scale = new Vector2(scale, scale);
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
        if (_editorPage is RetailFrontendEditorPage.ClickToStart or RetailFrontendEditorPage.Debriefing) return;
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
        // Debriefing's editor fixture is display data, not a manufactured Won
        // transition. The actual Session remains at its cold click page.
        RetailFrontendScreen screen = Engine.IsEditorHint() && _editorPage == RetailFrontendEditorPage.Debriefing
            ? RetailFrontendScreen.Debriefing : _session.Screen;
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
        UpdateMainMenuFrame();
        UpdateClickFrame();
        UpdateOptionsFrame();
        UpdateLoadingFrame();
        UpdateDebriefingFrame();
        foreach (RetailFrontendPart part in _sceneParts.Values)
            part.QueueRedraw();
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
                case "Career": DrawDevSelect(); break;
                case "Briefing": DrawMissionBriefing(); break;
                case "Configuration": DrawSelectConfiguration(); break;
                case "Quit": DrawQuitConfirm(); break;
                case "LevelSelect": DrawLevelSelect(); break;
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
