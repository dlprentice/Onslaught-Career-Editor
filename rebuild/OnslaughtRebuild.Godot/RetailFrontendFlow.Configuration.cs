// SPDX-License-Identifier: GPL-3.0-or-later

using Godot;

namespace OnslaughtRebuild.GodotClient;

public sealed partial class RetailFrontendFlow
{
    private Control _configurationView = null!;

    private void InitializeConfiguration()
    {
        _configurationView = GetNode<Control>("Stage/SelectConfiguration");
        using var paths = new Godot.Collections.Dictionary
        {
            ["rock"] = AssetPaths.TexturePath("Frontend", "Backgrounds/rock"),
            ["ring"] = AssetPaths.TexturePath("Frontend", "level-bracket-02"),
            ["arrow"] = AssetPaths.TexturePath("Frontend", "fe-arrow"),
        };
        using Variant body = _optionsView.Get("body_font");
        using Variant title = _optionsView.Get("title_font");
        using var fonts = new Godot.Collections.Dictionary { ["body_font"] = body, ["title_font"] = title };
        using Variant pathBatch = paths;
        using Variant fontBatch = fonts;
        using Variant returned = _configurationView.Call("configure_assets", pathBatch, fontBatch);
        RequireConfigurationResult(returned);
    }

    private void UpdateConfigurationFrame()
    {
        if (_configurationView is null || !_configurationView.Visible) return;
        if (Engine.IsEditorHint())
        {
            using Variant preview = _configurationView.Call("show_editor_preview");
            RequireConfigurationResult(preview);
            return;
        }

        var configuration = _session.SelectedConfiguration;
        using var facts = new Godot.Collections.Dictionary
        {
            ["unit_name"] = ConfigurationTextUnits(configuration.DisplayName),
            ["walker_primary"] = ConfigurationTextUnits(configuration.WalkerPrimary.DisplayName),
            ["walker_secondary"] = ConfigurationTextUnits(configuration.WalkerSecondary.DisplayName),
            ["jet_primary"] = ConfigurationTextUnits(configuration.JetPrimary.DisplayName),
            ["jet_secondary"] = ConfigurationTextUnits(configuration.JetSecondary.DisplayName),
        };
        // One display batch from the existing selection owner. The native page
        // neither chooses another configuration nor requests a loading handoff.
        using Variant batch = facts;
        using Variant returned = _configurationView.Call("set_frame", batch);
        RequireConfigurationResult(returned);
    }

    private int ConfigurationTargetAt(Vector2 designPosition) =>
        _configurationView.Call("hit_test", designPosition).AsInt32();

    private static int[] ConfigurationTextUnits(string text) =>
        text.Select(character => (int)character).ToArray();

    private static void RequireConfigurationResult(Variant returned)
    {
        if (returned.VariantType != Variant.Type.Dictionary)
            throw new InvalidDataException("Native configuration presentation returned no completion result.");
        using Godot.Collections.Dictionary result = returned.AsGodotDictionary();
        if (!result["ok"].AsBool())
            throw new InvalidDataException(result["error"].AsString());
    }
}
