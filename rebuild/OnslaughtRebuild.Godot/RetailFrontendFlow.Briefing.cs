// SPDX-License-Identifier: GPL-3.0-or-later

using Godot;

namespace OnslaughtRebuild.GodotClient;

public sealed partial class RetailFrontendFlow
{
    private Control _briefingView = null!;

    private void InitializeBriefing()
    {
        _briefingView = GetNode<Control>("Stage/MissionBriefing");
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
        using Variant returned = _briefingView.Call("configure_assets", pathBatch, fontBatch);
        RequireBriefingResult(returned);
    }

    private void UpdateBriefingFrame()
    {
        if (_briefingView is null || !_briefingView.Visible) return;
        if (Engine.IsEditorHint())
        {
            using Variant preview = _briefingView.Call("show_editor_preview");
            RequireBriefingResult(preview);
            return;
        }

        using var paragraphs = new Godot.Collections.Array();
        foreach (string paragraph in _session.SelectedBriefingBody)
            paragraphs.Add(BriefingTextUnits(paragraph));
        using var facts = new Godot.Collections.Dictionary
        {
            ["level_name"] = BriefingTextUnits(_session.SelectedLevelName),
            ["paragraphs"] = paragraphs,
        };
        // The existing session owns the selected world. Native presentation
        // owns wrapping and the retained empty-body fallback, without choosing
        // another world or requesting a configuration/loading transition.
        using Variant batch = facts;
        using Variant returned = _briefingView.Call("set_frame", batch);
        RequireBriefingResult(returned);
    }

    private int BriefingTargetAt(Vector2 designPosition) =>
        _briefingView.Call("hit_test", designPosition).AsInt32();

    private static int[] BriefingTextUnits(string text) =>
        text.Select(character => (int)character).ToArray();

    private static void RequireBriefingResult(Variant returned)
    {
        if (returned.VariantType != Variant.Type.Dictionary)
            throw new InvalidDataException("Native briefing presentation returned no completion result.");
        using Godot.Collections.Dictionary result = returned.AsGodotDictionary();
        if (!result["ok"].AsBool())
            throw new InvalidDataException(result["error"].AsString());
    }
}
