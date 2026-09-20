// SPDX-License-Identifier: GPL-3.0-or-later

using System.Runtime.ExceptionServices;
using Godot;
using OnslaughtRebuild.Client;

namespace OnslaughtRebuild.GodotClient;

/// <summary>
/// FEP_OPTIONS and its three subpages.
///
/// <para><b>Provenance split, stated once here so every constant below is
/// attributable.</b></para>
/// <list type="bullet">
/// <item><b>SOURCE (pinned GPL drop):</b> nothing about the widget layer -
/// <c>FEPOptions.cpp</c>, <c>MenuItem.cpp</c> and <c>PauseMenu.cpp</c> are all
/// absent. What IS ported is the page chrome (<c>FrontEnd.cpp:1101-1105</c>
/// header-bar constants, already consumed by <see cref="DrawHeaderBarTitle"/>)
/// and everything behind the rows (see <see cref="RetailOptionsMenu"/>).</item>
/// <item><b>BYTES (pristine specimen
/// <c>local-lab/safe-copy-bea-pristine/BEA.exe.original.backup</c>, sha256
/// <c>74154bfa…</c>):</b> the row inventory, the exact English labels, the row
/// height 20, the range origin 300, the mouse-sensitivity law, the value-row
/// seed bias 0.48, and the three apply timings. All of it is written up in
/// <c>local-lab/OPTIONS-PAGE-RECOVERY-2026-07-27.md</c>.</item>
/// <item><b>PIXELS
/// (<c>local-lab/retail-captures-options-pause-2026-07-27/</c>):</b> every
/// geometry constant in this file, every colour, the bindings-grid font
/// identity, and the fact that "Screen shape:" is absent from the shipped Video
/// page.</item>
/// </list>
///
/// <para><b>Known gaps, drawn nowhere rather than faked.</b></para>
/// The top-left Forseti emblem and the metal header end-caps are the same
/// unidentified art every other page in this lane lacks. The retail root page's
/// title plate is 390px wide and its title reads (215,215,217) where the three
/// subpages are 395px and (254,254,254); that difference is unexplained and the
/// tracked 395/253 treatment is used for all four.
/// </summary>
public sealed partial class RetailFrontendFlow
{
    private Control _optionsView = null!;
    private Godot.Collections.Dictionary _optionsSettings = new();
    private readonly Dictionary<int, ExceptionDispatchInfo> _optionsEffectFailures = [];
    private int _optionsEffectFailureSequence;

    // Detached, cached settings. No property or drawing read crosses languages.
    internal RetailOptionsSettings OptionsSettings => ReadOptionsSettings(_optionsSettings);
    internal Control OptionsView => _optionsView;

    private void InitializeOptions()
    {
        _optionsView = GetNode<Control>("Stage/Options");
        if (!Engine.IsEditorHint())
            _optionsView.Call("set_effect_handler", Callable.From<Godot.Collections.Dictionary,
                Godot.Collections.Dictionary, Godot.Collections.Dictionary>(DispatchOptionsEffect));
        using var paths = new Godot.Collections.Dictionary
        {
            ["body_font"] = AssetPaths.TexturePath("Hud", "font-13ps"),
            ["title_font"] = AssetPaths.TexturePath("Hud", "font-22"),
            ["system_font"] = AssetPaths.TexturePath("Frontend", "system-font"),
            ["bracket"] = AssetPaths.TexturePath("Frontend", "level-bracket-01"),
            ["arrow"] = AssetPaths.TexturePath("Frontend", "fe-arrow"),
        };
        using var frames = new Godot.Collections.Array();
        foreach (Texture2D frame in _feBackFrames)
        {
            using Variant texture = frame;
            frames.Add(texture);
        }
        // Resource-bearing Variants own a native reference independently of
        // the Array/Dictionary wrappers. Dispose the temporary batch carriers,
        // while the view and decoded C# texture handles keep their own owners.
        using Variant pathBatch = paths;
        using Variant frameBatch = frames;
        using Variant configuredAssets = _optionsView.Call("configure_assets", pathBatch, frameBatch);
        using Godot.Collections.Dictionary assetResult = configuredAssets.AsGodotDictionary();
        RequireOptionsResult(assetResult);
        // All frontend glyph users share these production pages and widths.
        using Variant bodyTexture = _optionsView.Call("font_texture", false);
        using Variant titleTexture = _optionsView.Call("font_texture", true);
        _titleFont = bodyTexture.As<Texture2D>();
        _font22 = titleTexture.As<Texture2D>();
        _glyphWidths = _optionsView.Call("font_widths", false).AsInt32Array();
        _font22Widths = _optionsView.Call("font_widths", true).AsInt32Array();
        RetailOptionsHostCapabilities host = DescribeHost();
        ApplyOptionsResult(_optionsView.Call("configure_host", new Godot.Collections.Dictionary
        {
            ["screen_modes"] = new Godot.Collections.Array(host.ScreenModes.Select(static x => (Variant)x)),
            ["video_adapters"] = new Godot.Collections.Array(host.VideoAdapters.Select(static x => (Variant)x)),
            ["anti_aliasing_levels"] = new Godot.Collections.Array(host.AntiAliasingLevels.Select(static x => (Variant)x)),
            ["sound_devices"] = new Godot.Collections.Array(host.SoundDevices.Select(static x => (Variant)x)),
            ["recommended_texture_resolution"] = host.RecommendedTextureResolution,
            ["recommended_enable32_bit_textures"] = host.RecommendedEnable32BitTextures,
        }).AsGodotDictionary());
        if (!Engine.IsEditorHint()) ApplyOptionsToHost();
    }

    // Preserve the current device enumeration and admitted recommendation gap.
    // No new D3D recommendation, display mode, sound device or binding law.
    private static RetailOptionsHostCapabilities DescribeHost()
    {
        Vector2I window = DisplayServer.WindowGetSize();
        string adapter = RenderingServer.GetVideoAdapterName();
        return new RetailOptionsHostCapabilities(
            [$"{window.X} x {window.Y}"],
            [string.IsNullOrWhiteSpace(adapter) ? "Unknown" : adapter],
            ["None"], ["Primary Sound Driver"],
            RecommendedTextureResolution: 0,
            RecommendedEnable32BitTextures: 2);
    }

    private void ApplyOptionsToHost()
    {
        if (Engine.IsEditorHint()) return;
        RetailOptionsSettings settings = OptionsSettings;
        DisplayServer.WindowSetVsyncMode(settings.VSync
            ? DisplayServer.VSyncMode.Enabled : DisplayServer.VSyncMode.Disabled);
        OptionsSettingsChanged?.Invoke(settings);
    }

    public event Action<RetailOptionsSettings>? OptionsSettingsChanged;

    private void UpdateOptionsFrame()
    {
        if (_optionsView is not null && _optionsView.Visible)
            _optionsView.Call("set_frame", _animationSeconds, _feBackSeconds);
    }

    private void ResetOptions() => ApplyOptionsResult(_optionsView.Call("reset_menu").AsGodotDictionary());

    internal void SelectOptionsRowForCapture(int index)
    {
        ApplyOptionsResult(_optionsView.Call("select_row", index).AsGodotDictionary());
        QueueRedraw();
    }

    internal void ConfirmOptionsForCapture() => ConfirmOptions();
    internal void BackFromOptionsForCapture() => BackFromOptions();
    internal bool CancelOptionsForCapture() => HandleOptionsPointerCancel(rightDown: true);

    private bool HandleOptionsKey(InputEventKey key) => ApplyOptionsResult(_optionsView.Call(
        "handle_key", IsKey(key, Key.Up), IsKey(key, Key.Down), IsKey(key, Key.Left), IsKey(key, Key.Right),
        IsKey(key, Key.Enter) || IsKey(key, Key.KpEnter) || IsKey(key, Key.Space), IsKey(key, Key.Escape))
        .AsGodotDictionary());

    private void ConfirmOptions() => ApplyOptionsResult(_optionsView.Call(
        "handle_key", false, false, false, false, true, false).AsGodotDictionary());

    private void BackFromOptions() => ApplyOptionsResult(_optionsView.Call(
        "handle_key", false, false, false, false, false, true).AsGodotDictionary());

    private bool HandleOptionsPointerMotion(Vector2 design) =>
        ApplyOptionsResult(_optionsView.Call("pointer_motion", design).AsGodotDictionary());

    private bool HandleOptionsPointerConfirm(Vector2 design) =>
        ApplyOptionsResult(_optionsView.Call("pointer_confirm", design).AsGodotDictionary());

    private bool HandleOptionsPointerCancel(bool rightDown) =>
        ApplyOptionsResult(_optionsView.Call("pointer_cancel", rightDown).AsGodotDictionary());

    private bool ApplyOptionsResult(Godot.Collections.Dictionary result)
    {
        if (result.TryGetValue("settings", out Variant settings))
            _optionsSettings = settings.AsGodotDictionary().Duplicate(true);
        // User-action effects already ran at their original source points in
        // the narrow callback below. They must never be replayed after mutation.
        if (result.TryGetValue("host_exception_id", out Variant failureId)
            && _optionsEffectFailures.Remove(failureId.AsInt32(), out ExceptionDispatchInfo? error))
            error.Throw();
        RequireOptionsResult(result);
        return result.TryGetValue("value", out Variant value) && value.VariantType == Variant.Type.Bool && value.AsBool();
    }

    private Godot.Collections.Dictionary DispatchOptionsEffect(
        Godot.Collections.Dictionary effect, Godot.Collections.Dictionary settings)
    {
        // Synchronous user-action boundary: an audio/settings observer can
        // throw or reenter. Native control flow stops at a returned failure;
        // ExceptionDispatchInfo preserves the exact host exception on return.
        _optionsSettings = settings.Duplicate(true);
        try
        {
            switch (effect["kind"].AsString())
            {
                case "audio": RequestAudioCue((RetailFrontendAudioCue)effect["cue"].AsInt32()); break;
                case "apply_settings": ApplyOptionsToHost(); break;
                case "redraw": QueueRedraw(); break;
                case "frontend_back":
                    if (_session.TryBackPage(startupMediaActive: false, out RetailFrontendSignal frontend))
                    {
                        RequestAudioCue(RetailFrontendAudioCue.Back);
                        HandleNavigationSignal(frontend);
                        QueueRedraw();
                    }
                    break;
                default: throw new InvalidDataException("Unknown native options effect.");
            }
            return new Godot.Collections.Dictionary { ["ok"] = true };
        }
        catch (Exception error)
        {
            int id = ++_optionsEffectFailureSequence;
            _optionsEffectFailures.Add(id, ExceptionDispatchInfo.Capture(error));
            return new Godot.Collections.Dictionary
            {
                ["ok"] = false, ["error_type"] = error.GetType().Name,
                ["error"] = error.Message, ["host_exception_id"] = id,
            };
        }
    }

    private static void RequireOptionsResult(Godot.Collections.Dictionary result)
    {
        if (result.TryGetValue("ok", out Variant ok) && ok.AsBool()) return;
        string message = result.TryGetValue("error", out Variant error) ? error.AsString() : "Native options operation failed.";
        string kind = result.TryGetValue("error_type", out Variant type) ? type.AsString() : "InvalidOperationException";
        string? parameter = result.TryGetValue("parameter", out Variant param) ? param.AsString() : null;
        throw kind switch
        {
            "ArgumentOutOfRangeException" => new ArgumentOutOfRangeException(parameter, message),
            "ArgumentNullException" => new ArgumentNullException(parameter, message),
            "ArgumentException" => new ArgumentException(message, parameter),
            "NullReferenceException" => new NullReferenceException(message),
            _ => new InvalidOperationException(message),
        };
    }

    private static RetailOptionsSettings ReadOptionsSettings(Godot.Collections.Dictionary value) => new()
    {
        SoundVolume = value["sound_volume"].AsSingle(),
        MusicVolume = value["music_volume"].AsSingle(),
        MouseSensitivity = value["mouse_sensitivity"].AsSingle(),
        ControllerConfiguration = value["controller_configuration"].AsInt32(),
        InvertYWalkerPlayer1 = value["invert_y_walker_player1"].AsBool(),
        InvertYWalkerPlayer2 = value["invert_y_walker_player2"].AsBool(),
        InvertYFlightPlayer1 = value["invert_y_flight_player1"].AsBool(),
        InvertYFlightPlayer2 = value["invert_y_flight_player2"].AsBool(),
        OverallDetail = value["overall_detail"].AsInt32(),
        ShadowDetail = value["shadow_detail"].AsInt32(),
        GeometryDetail = value["geometry_detail"].AsInt32(),
        TrilinearMipmapping = value["trilinear_mipmapping"].AsBool(),
        VSync = value["v_sync"].AsBool(),
        LandscapeResolution = value["landscape_resolution"].AsInt32(),
        TextureResolution = value["texture_resolution"].AsInt32(),
        Enable32BitTextures = value["enable32_bit_textures"].AsInt32(),
        SwapSpeakers = value["swap_speakers"].AsBool(),
        HardwareSound = value["hardware_sound"].AsBool(),
        SoundQuality = value["sound_quality"].AsInt32(),
        SoundMethod3D = value["sound_method3_d"].AsInt32(),
    };
}
