// SPDX-License-Identifier: GPL-3.0-or-later

using Godot;

namespace OnslaughtRebuild.GodotClient;

public sealed partial class RetailFrontendFlow
{
    private Control _loadingView = null!;
    private int[] _loadingCaptionUnits = [];

    private void InitializeLoading()
    {
        _loadingView = GetNode<Control>("Stage/Loading");
        _loadingCaptionUnits = _loadingText.Select(character => (int)character).ToArray();
        using var paths = new Godot.Collections.Dictionary();
        string route = AssetPaths.TexturePath("Frontend", "loading-screen");
        if (route != "res://Assets/Frontend/loading-screen.texture.aya") paths["background"] = route;
        // The standalone scene uses the same public asset/font recipes. A
        // live host shares its already-admitted font and exact UTF-16 caption
        // once; no draw, glyph or row calls cross this temporary boundary.
        using Variant title = _optionsView.Get("title_font");
        using Variant caption = _loadingCaptionUnits;
        using Variant routes = paths;
        using Variant returned = _loadingView.Call("configure_assets", routes, title, caption);
        using Godot.Collections.Dictionary result = returned.AsGodotDictionary();
        RequireLoadingResult(result, configuringAssets: true);
    }

    private void UpdateLoadingFrame()
    {
        if (_loadingView is null || !_loadingView.Visible) return;
        if (Engine.IsEditorHint())
        {
            using Variant frozen = _loadingView.Call("show_editor_progress");
            using Godot.Collections.Dictionary preview = frozen.AsGodotDictionary();
            RequireLoadingResult(preview);
            return;
        }
        // These existing host facts remain observations. Native Loading never
        // consumes a launch request, advances a frame, reports readiness or
        // invents progress fill. Original two-frame/root-hide ordering stays
        // in _Process and TryRaiseGameplayActivation.
        using var facts = new Godot.Collections.Dictionary
        {
            ["loading_frames"] = _loadingFrames,
            ["launch_requested"] = _loadRequestRaised,
            ["ready"] = _level100Ready,
        };
        using Variant batch = facts;
        using Variant caption = _loadingCaptionUnits;
        using Variant returned = _loadingView.Call("set_frame", batch, caption);
        using Godot.Collections.Dictionary result = returned.AsGodotDictionary();
        RequireLoadingResult(result);
    }

    private static void RequireLoadingResult(Godot.Collections.Dictionary result, bool configuringAssets = false)
    {
        bool hasOk = result.TryGetValue("ok", out Variant ok);
        using (ok)
            if (hasOk && ok.AsBool()) return;
        bool hasError = result.TryGetValue("error", out Variant error);
        string message;
        using (error)
            message = hasError ? error.AsString() : "Native Loading failed.";
        if (configuringAssets) throw new InvalidDataException(message);
        bool hasKind = result.TryGetValue("error_type", out Variant kind);
        using (kind)
            if (hasKind && kind.AsString() == "InvalidDataException") throw new InvalidDataException(message);
        throw new InvalidOperationException(message);
    }
}
