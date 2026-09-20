// SPDX-License-Identifier: GPL-3.0-or-later

using Godot;
using OnslaughtRebuild.Client;

namespace OnslaughtRebuild.GodotClient;

public sealed partial class RetailFrontendFlow
{
    private Control _debriefingView = null!;
    private RetailDebriefingProjection? _lastDebriefingProjection;
    private string? _lastDebriefingLevelName;
    private Godot.Collections.Dictionary? _debriefingFrame;
    private int[] _debriefingFallbackUnits = [];

    private void InitializeDebriefing()
    {
        _debriefingView = GetNode<Control>("Stage/Debriefing");
        using var paths = new Godot.Collections.Dictionary();
        // Default paths belong to the editable scene recipes. An explicit host
        // route preserves the existing AssetPaths override contract.
        foreach ((string key, string name) in new (string, string)[]
        {
            ("metal_ring", "Debriefing/metal-ring-transition"),
            ("writing", "forseti-writing-large"), ("symbol_bracket", "symbol-bracket-01"),
            ("grade_a", "Debriefing/ranking-a"), ("grade_b", "Debriefing/ranking-b"),
            ("grade_c", "Debriefing/ranking-c"), ("grade_d", "Debriefing/ranking-d"),
            ("grade_e", "Debriefing/ranking-e"), ("grade_s", "Debriefing/ranking-s"),
        })
        {
            string route = AssetPaths.TexturePath("Frontend", name);
            if (route != $"res://Assets/Frontend/{name}.texture.aya") paths[key] = route;
        }
        // A single initialization batch shares the same native font resources
        // and decoded FEBack frames used by every frontend page. Disposing the
        // temporary Variant carriers does not dispose their live texture owner.
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
        using Variant returned = _debriefingView.Call("configure_assets", pathBatch, fontBatch, frameBatch);
        using Godot.Collections.Dictionary result = returned.AsGodotDictionary();
        RequireDebriefingResult(result);
    }

    private void UpdateDebriefingFrame()
    {
        if (_debriefingView is null || !_debriefingView.Visible) return;
        if (Engine.IsEditorHint())
        {
            // Display only the explicitly authored frozen projection. Opening
            // this page never fabricates a Won handoff or a gameplay session.
            using Variant preview = _debriefingView.Call("show_editor_projection");
            using Godot.Collections.Dictionary result = preview.AsGodotDictionary();
            RequireDebriefingResult(result);
            return;
        }

        RetailDebriefingProjection projection = _session.Debriefing
            ?? throw new InvalidOperationException("The debriefing screen has no END_LEVEL_DATA projection.");
        string levelName = _session.SelectedLevelName;
        if (_debriefingFrame is null || projection != _lastDebriefingProjection || levelName != _lastDebriefingLevelName)
        {
            _debriefingFrame?.Dispose();
            _debriefingFrame = DebriefingFrame(projection);
            _debriefingFallbackUnits = levelName.Select(character => (int)character).ToArray();
            _lastDebriefingProjection = projection;
            _lastDebriefingLevelName = levelName;
        }
        // One page snapshot/clock batch. Native Controls own every draw; reads
        // do not cross to the Session per row, glyph, texture or draw callback.
        using Variant snapshot = _debriefingFrame;
        using Variant fallback = _debriefingFallbackUnits;
        using Variant returned = _debriefingView.Call("set_frame", snapshot, fallback, _feBackSeconds);
        using Godot.Collections.Dictionary frameResult = returned.AsGodotDictionary();
        RequireDebriefingResult(frameResult);
    }

    internal static Godot.Collections.Dictionary DebriefingFrame(RetailDebriefingProjection value) => new()
    {
        ["world_finished"] = value.WorldFinished,
        ["mission_status"] = (int)value.MissionStatus,
        ["primary_objectives"] = (int)value.PrimaryObjectives,
        ["secondary_objectives"] = (int)value.SecondaryObjectives,
        ["grade_byte"] = value.GradeByte is byte grade ? Variant.From((int)grade) : default,
        ["new_goodie_count"] = value.NewGoodieCount,
        ["first_goodie"] = value.FirstGoodie,
    };

    private static void RequireDebriefingResult(Godot.Collections.Dictionary result)
    {
        if (result.TryGetValue("ok", out Variant ok) && ok.AsBool()) return;
        string error = result.TryGetValue("error", out Variant message) ? message.AsString() : "Native debriefing failed.";
        if (result.TryGetValue("error_type", out Variant kind) && kind.AsString() == "InvalidDataException")
            throw new InvalidDataException(error);
        throw new InvalidOperationException(error);
    }
}
