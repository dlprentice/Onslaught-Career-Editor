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

    private Control? _stage;

    public static RetailFrontendFlow InstantiateScene() =>
        GD.Load<PackedScene>(ProductionScenePath).Instantiate<RetailFrontendFlow>();

    private void BindSceneStage()
    {
        _stage = GetNode<Control>("Stage");
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
        UpdateQuitConfirmFrame();
        UpdateCareerNameFrame();
        UpdateLevelSelectFrame();
        UpdateBriefingFrame();
        UpdateConfigurationFrame();
        UpdateClickFrame();
        UpdateOptionsFrame();
        UpdateLoadingFrame();
        UpdateDebriefingFrame();
    }
}
