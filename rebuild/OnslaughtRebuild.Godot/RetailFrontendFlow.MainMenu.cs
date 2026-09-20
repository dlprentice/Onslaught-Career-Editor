// SPDX-License-Identifier: GPL-3.0-or-later

using Godot;
using OnslaughtRebuild.Client;

namespace OnslaughtRebuild.GodotClient;

public sealed partial class RetailFrontendFlow
{
    private Control _mainMenuView = null!;
    private readonly Dictionary<RetailFrontendMenuItemKind, int[]> _mainMenuLabelUnits = [];

    private void InitializeMainMenu()
    {
        _mainMenuView = GetNode<Control>("Stage/MainMenu");
        using var paths = new Godot.Collections.Dictionary();
        foreach (string name in new[]
        {
            "forseti-writing-large", "fe-arrow", "title-text-box", "title-bracket-01", "title-bracket-02",
            "symbol-bracket-01", "symbol-bracket-02", "title-logo", "reflection-map",
            "Flags/flag-uk", "Flags/flag-fr", "Flags/flag-gr", "Flags/flag-it", "Flags/flag-sp",
            "Icons/new-game", "Icons/continue-game", "Icons/load-game", "Icons/multiplayer",
            "Icons/goodies", "Icons/options", "Icons/quit",
        })
        {
            string route = AssetPaths.TexturePath("Frontend", name);
            if (route != $"res://Assets/Frontend/{name}.texture.aya") paths["Frontend/" + name] = route;
        }
        using var labels = new Godot.Collections.Array();
        foreach (RetailFrontendMenuItem item in _session.Items)
        {
            int[] units = _menuText[item.Kind].Select(character => (int)character).ToArray();
            _mainMenuLabelUnits.Add(item.Kind, units);
            using Variant text = units;
            labels.Add(text);
        }
        using Variant font = _optionsView.Get("body_font");
        using Resource underlay = GD.Load<Resource>("res://Scenes/Frontend/FrontendUnderlay.tres");
        using Variant routes = paths;
        using Variant labelBatch = labels;
        using Variant returned = _mainMenuView.Call("configure_assets", routes, font, underlay, labelBatch);
        RequireMainMenuResult(returned);
    }

    private void UpdateMainMenuFrame()
    {
        if (_mainMenuView is null || !_mainMenuView.Visible) return;
        if (Engine.IsEditorHint() && _editorPage == RetailFrontendEditorPage.MainMenu)
        {
            using Variant frozen = _mainMenuView.Call("show_editor_preview");
            RequireMainMenuResult(frozen);
            return;
        }
        using var rows = new Godot.Collections.Array();
        foreach (RetailFrontendMenuItem item in _session.Items)
        {
            using var row = new Godot.Collections.Dictionary
            {
                ["text"] = _mainMenuLabelUnits[item.Kind],
                ["available"] = item.IsAvailable,
            };
            using Variant value = row;
            rows.Add(value);
        }
        // One fact batch crosses the temporary host boundary. Navigation,
        // clocks, hover gates and audio ordering stay with the existing session.
        using var facts = new Godot.Collections.Dictionary
        {
            ["transition"] = MainMenuTransition,
            ["animation_seconds"] = _animationSeconds,
            ["background_seconds"] = _feBackSeconds,
            ["selected_index"] = _session.SelectedMainIndex,
            ["language"] = (int)_session.Language,
            ["rows"] = rows,
            ["reflection_visible"] = _session.Screen == RetailFrontendScreen.MainMenu,
        };
        using Variant batch = facts;
        using Variant returned = _mainMenuView.Call("set_frame", batch);
        RequireMainMenuResult(returned);
    }

    private static void RequireMainMenuResult(Variant returned)
    {
        if (returned.VariantType != Variant.Type.Dictionary)
            throw new InvalidDataException("Native Main Menu returned no completion result.");
        using Godot.Collections.Dictionary result = returned.AsGodotDictionary();
        if (result["ok"].AsBool()) return;
        throw new InvalidDataException(result["error"].AsString());
    }
}
