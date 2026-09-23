// SPDX-License-Identifier: GPL-3.0-or-later

using Godot;

namespace OnslaughtRebuild.GodotClient;

public sealed partial class RetailFrontendFlow
{
    private Control _careerNameView = null!;

    private void InitializeCareerName()
    {
        _careerNameView = GetNode<Control>("Stage/CareerName");
        using var paths = new Godot.Collections.Dictionary
        {
            ["bracket"] = AssetPaths.TexturePath("Frontend", "level-bracket-01"),
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
        using Variant returned = _careerNameView.Call("configure_assets", pathBatch, fontBatch, frameBatch);
        RequireCareerNameResult(returned);
    }

    private void UpdateCareerNameFrame()
    {
        if (_careerNameView is null || !_careerNameView.Visible) return;
        if (Engine.IsEditorHint())
        {
            using Variant preview = _careerNameView.Call("show_editor_preview");
            RequireCareerNameResult(preview);
            return;
        }

        using var names = new Godot.Collections.Array();
        foreach (string name in _session.CareerNames)
        {
            // The original renderer stops before row eleven. Keep an offscreen
            // null untouched instead of reading or normalizing it in transport.
            using Variant units = name is null ? default(Variant) : name.Select(character => (int)character).ToArray();
            names.Add(units);
        }
        using var facts = new Godot.Collections.Dictionary
        {
            ["career_names"] = names,
            ["selected_career_index"] = _session.SelectedCareerIndex,
            ["game_name"] = _session.GameName.Select(character => (int)character).ToArray(),
            ["game_name_is_fresh"] = _session.GameNameIsFresh,
            ["background_seconds"] = _feBackSeconds,
        };
        // One detached display batch; the native controls do not discover
        // careers, mutate names, read saves, or perform a navigation handoff.
        using Variant batch = facts;
        using Variant returned = _careerNameView.Call("set_frame", batch);
        RequireCareerNameResult(returned);
    }

    private int CareerNameTargetAt(Vector2 designPosition) =>
        _careerNameView.Call("hit_test", designPosition).AsInt32();

    private int MeasureGameNameExtent(string text)
    {
        using Variant units = text.Select(character => (int)character).ToArray();
        return _careerNameView.Call("measure_name_extent", units).AsInt32();
    }

    private static void RequireCareerNameResult(Variant returned)
    {
        if (returned.VariantType != Variant.Type.Dictionary)
            throw new InvalidDataException("Native career-name presentation returned no completion result.");
        using Godot.Collections.Dictionary result = returned.AsGodotDictionary();
        if (!result["ok"].AsBool())
            throw new InvalidDataException(result["error"].AsString());
    }
}
