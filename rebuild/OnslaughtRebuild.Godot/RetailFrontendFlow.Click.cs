// SPDX-License-Identifier: GPL-3.0-or-later
using Godot;

namespace OnslaughtRebuild.GodotClient;

public sealed partial class RetailFrontendFlow
{
    private Control _clickView = null!;

    private void InitializeClick()
    {
        _clickView = GetNode<Control>("Stage/ClickToStart");
        using var paths = new Godot.Collections.Dictionary();
        foreach ((string key, string name) in new[]
        {
            ("splash", "Backgrounds/click-to-start"), ("slide", "click-slide"), ("title", "title-logo"),
        })
        {
            string route = AssetPaths.TexturePath("Frontend", name);
            if (route != $"res://Assets/Frontend/{name}.texture.aya") paths[key] = route;
        }
        using Variant bodyFont = _optionsView.Get("body_font");
        using Variant routes = paths;
        using Variant returned = _clickView.Call("configure_assets", routes, bodyFont);
        RequireClickResult(returned);
    }

    private void UpdateClickFrame()
    {
        if (_clickView is null || !_clickView.Visible) return;
        if (Engine.IsEditorHint())
        {
            using Variant frozen = _clickView.Call("show_editor_preview");
            RequireClickResult(frozen);
            return;
        }
        // The existing host retains its clocks, input and idle transition.
        // One fact batch updates the same scene that opens in the editor.
        using var facts = new Godot.Collections.Dictionary
        {
            ["pulse_timer"] = _clickPulseTimer,
            ["page_seconds"] = _clickPageSeconds,
        };
        using Variant batch = facts;
        using Variant returned = _clickView.Call("set_frame", batch);
        RequireClickResult(returned);
    }

    private static void RequireClickResult(Variant returned)
    {
        if (returned.VariantType != Variant.Type.Dictionary)
            throw new InvalidDataException("Native Click page returned no completion result.");
        using Godot.Collections.Dictionary result = returned.AsGodotDictionary();
        using Variant ok = result["ok"];
        if (ok.AsBool()) return;
        using Variant error = result["error"];
        throw new InvalidDataException(error.AsString());
    }
}
