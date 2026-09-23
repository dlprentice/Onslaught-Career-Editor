// SPDX-License-Identifier: GPL-3.0-or-later

using Godot;
using OnslaughtRebuild.Client;

namespace OnslaughtRebuild.GodotClient;

public sealed partial class RetailFrontendFlow
{
    private Control _quitConfirmView = null!;

    private void InitializeQuitConfirm()
    {
        _quitConfirmView = GetNode<Control>("Stage/QuitConfirm");
        using var paths = new Godot.Collections.Dictionary
        {
            ["blank"] = AssetPaths.TexturePath("PauseMenu", "blank"),
        };
        using Variant body = _optionsView.Get("body_font");
        using Variant choice = _optionsView.Get("title_font");
        using Variant routes = paths;
        using Variant result = _quitConfirmView.Call("configure_assets", routes, body, choice);
        RequireQuitConfirmResult(result);
    }

    private void UpdateQuitConfirmFrame()
    {
        if (_quitConfirmView is null || !_quitConfirmView.Visible) return;
        if (Engine.IsEditorHint())
        {
            using Variant preview = _quitConfirmView.Call("show_editor_preview");
            RequireQuitConfirmResult(preview);
            return;
        }
        // Navigation and the actual quit signal remain with the existing
        // session. The scene receives only its detached display selection.
        using var facts = new Godot.Collections.Dictionary
        {
            ["selected_index"] = _session.SelectedQuitConfirmIndex,
        };
        using Variant batch = facts;
        using Variant result = _quitConfirmView.Call("set_frame", batch);
        RequireQuitConfirmResult(result);
    }

    private int QuitConfirmIndexAt(Vector2 designPosition)
    {
        if (_stage is null) return -1;
        // This point already passed through the original viewport-to-design
        // conversion. A canvas round-trip can move a half-open row boundary.
        return _quitConfirmView.Call("hit_test", designPosition).AsInt32();
    }

    private static void RequireQuitConfirmResult(Variant returned)
    {
        if (returned.VariantType != Variant.Type.Dictionary)
            throw new InvalidDataException("Native quit confirmation returned no completion result.");
        using Godot.Collections.Dictionary result = returned.AsGodotDictionary();
        if (!result["ok"].AsBool())
            throw new InvalidDataException(result["error"].AsString());
    }
}
