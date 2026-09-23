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

    [Export] public Resource AssetPaths { get; set; } = RetailFrontendAssetPathBridge.Create();
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
        UpdateMouseCursorFrame();
    }
}

/// <summary>Temporary marshalling boundary; the native routing resource is the sole owner.</summary>
internal static class RetailFrontendAssetPathBridge
{
    internal static Resource Create()
    {
        using GDScript script = GD.Load<GDScript>("res://Scenes/Frontend/retail_frontend_asset_paths.gd")
            ?? throw new InvalidDataException("The native frontend asset-path resource is unavailable.");
        using Variant created = script.New();
        return created.AsGodotObject() as Resource
            ?? throw new InvalidDataException("The frontend asset-path owner must be a Resource.");
    }

    public static string TexturePath(this Resource owner, string? folder, string? name)
    {
        if (owner is null) throw new NullReferenceException();
        ObjectDisposedException.ThrowIf(!GodotObject.IsInstanceValid(owner), owner);
        if (!owner.HasMethod("texture_path_units"))
            throw new InvalidDataException("The frontend asset-path resource has no checked resolver.");
        using Variant folderUnits = Units(folder);
        using Variant nameUnits = Units(name);
        using Variant returned = owner.Call("texture_path_units", folderUnits, nameUnits);
        if (returned.VariantType != Variant.Type.Dictionary)
            throw new InvalidDataException("The frontend asset-path resolver returned no result.");
        using Godot.Collections.Dictionary result = returned.AsGodotDictionary();
        if (!result.TryGetValue("ok", out Variant ok) || ok.VariantType != Variant.Type.Bool)
            throw new InvalidDataException("The frontend asset-path resolver returned no completion flag.");
        using (ok)
        {
            if (!ok.AsBool())
            {
                string type = result["error_type"].AsString();
                string message = result["error"].AsString();
                throw type switch
                {
                    "ArgumentOutOfRangeException" => new ArgumentOutOfRangeException("folder"),
                    "NullReferenceException" => new NullReferenceException(message),
                    "ArgumentException" => new ArgumentException(message, result["parameter"].AsString()),
                    _ => new InvalidDataException(message),
                };
            }
        }
        using Variant value = result["value"];
        if (value.VariantType != Variant.Type.PackedInt32Array)
            throw new InvalidDataException("The frontend asset path is missing its UTF-16 units.");
        int[] units = value.AsInt32Array();
        var characters = new char[units.Length];
        for (int index = 0; index < units.Length; index++)
        {
            if (units[index] is < 0 or > ushort.MaxValue)
                throw new InvalidDataException("The frontend asset path contains an invalid UTF-16 unit.");
            characters[index] = (char)units[index];
        }
        return new string(characters);
    }

    private static Variant Units(string? value) => value is null
        ? default(Variant) : value.Select(character => (int)character).ToArray();
}
