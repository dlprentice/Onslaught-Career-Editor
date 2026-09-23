// SPDX-License-Identifier: GPL-3.0-or-later

using Godot;

namespace OnslaughtRebuild.GodotClient;

public sealed partial class RetailFrontendFlow
{
    private Control _levelSelectView = null!;

    private void InitializeLevelSelect()
    {
        _levelSelectView = GetNode<Control>("Stage/LevelSelect");
        using var paths = new Godot.Collections.Dictionary
        {
            ["bracket"] = AssetPaths.TexturePath("Frontend", "level-bracket-01"),
            ["ring_outer"] = AssetPaths.TexturePath("Frontend", "level-ring-01"),
            ["ring_inner"] = AssetPaths.TexturePath("Frontend", "level-ring-02"),
            ["arrow"] = AssetPaths.TexturePath("Frontend", "fe-arrow"),
        };
        using Variant body = _optionsView.Get("body_font");
        using Variant title = _optionsView.Get("title_font");
        using var fonts = new Godot.Collections.Dictionary { ["body_font"] = body, ["title_font"] = title };
        using var frames = new Godot.Collections.Array();
        foreach (Texture2D texture in _feBackFrames)
        {
            using Variant frame = texture;
            frames.Add(frame);
        }
        using Variant pathBatch = paths;
        using Variant fontBatch = fonts;
        using Variant frameBatch = frames;
        using Variant titleUnits = _selectLevelText.Select(character => (int)character).ToArray();
        using Variant returned = _levelSelectView.Call("configure_assets", pathBatch, fontBatch, frameBatch, titleUnits);
        RequireLevelSelectResult(returned);
    }

    private void UpdateLevelSelectFrame()
    {
        if (_levelSelectView is null || !_levelSelectView.Visible) return;
        if (Engine.IsEditorHint())
        {
            using Variant preview = _levelSelectView.Call("show_editor_preview");
            RequireLevelSelectResult(preview);
            return;
        }

        using var facts = new Godot.Collections.Dictionary
        {
            ["level_name"] = _session.SelectedLevelName.Select(character => (int)character).ToArray(),
            ["background_seconds"] = _feBackSeconds,
        };
        // The existing session selects worlds. The settled graph has always
        // highlighted node zero; supplying a different name does not invent
        // new graph selection, animation, progression or input behavior.
        using Variant batch = facts;
        using Variant returned = _levelSelectView.Call("set_frame", batch);
        RequireLevelSelectResult(returned);
    }

    private int LevelSelectTargetAt(Vector2 designPosition) =>
        _levelSelectView.Call("hit_test", designPosition).AsInt32();

    private static void RequireLevelSelectResult(Variant returned)
    {
        if (returned.VariantType != Variant.Type.Dictionary)
            throw new InvalidDataException("Native level-select presentation returned no completion result.");
        using Godot.Collections.Dictionary result = returned.AsGodotDictionary();
        if (!result["ok"].AsBool())
            throw new InvalidDataException(result["error"].AsString());
    }
}
