// SPDX-License-Identifier: GPL-3.0-or-later

using System.Globalization;
using System.Text.RegularExpressions;

namespace OnslaughtRebuild.Client.Tests;

/// <summary>Routes existing MainMenu consumer guards to the production native
/// scene and renderers. Numerical C# owners remain independent oracles; no
/// retained reference renderer can satisfy these production assertions.</summary>
internal static class NativeMainMenuSource
{
    public static string Read(string name) => File.ReadAllText(Path.Combine(AppContext.BaseDirectory, "godot-main-menu-source", name));
    public static string Controller => Read("main_menu_presentation.gd");
    public static string Laws => Read("main_menu_laws.gd");
    public static string Scene => Read("MainMenu.tscn");
    public static string Label => Read("main_menu_label.gd");
    public static string Selector => Read("main_menu_selector.gd");
    public static string Reflection => Read("main_menu_reflection.gd") + "\n" + Read("main_menu_reflection.gdshader");
    public static string Presentation => string.Join('\n', new[] { Controller, Laws, Scene, Label, Selector, Reflection,
        Read("main_menu_texture.gd"), Read("main_menu_rotated_image.gd"), Read("main_menu_underlay.gd"), Read("main_menu_preview.gd") });

    public static string Function(string file, string method)
    {
        string source = Read(file), signature = "func " + method + "(";
        int start = source.IndexOf(signature, StringComparison.Ordinal);
        Assert.True(start >= 0, file + ": " + signature);
        int next = source.IndexOf("\nfunc ", start, StringComparison.Ordinal);
        int nextStatic = source.IndexOf("\nstatic func ", start, StringComparison.Ordinal);
        if (next < 0 || nextStatic >= 0 && nextStatic < next) next = nextStatic;
        return next < 0 ? source[start..] : source[start..next];
    }
    public static string Node(string path)
    {
        string[] parts = path.Split('/'); string name = parts[^1], parent = parts.Length == 1 ? "." : string.Join('/', parts[..^1]);
        string source = Scene; int start = 0;
        while ((start = source.IndexOf("[node name=\"" + name + "\"", start, StringComparison.Ordinal)) >= 0)
        {
            int headerEnd = source.IndexOf('\n', start);
            if (source[start..headerEnd].Contains("parent=\"" + parent + "\"", StringComparison.Ordinal))
            {
                int end = source.IndexOf("\n[node ", headerEnd, StringComparison.Ordinal);
                return end < 0 ? source[start..] : source[start..end];
            }
            start = headerEnd;
        }
        throw new InvalidOperationException("Missing production MainMenu node: " + path);
    }
    public static float Number(string source, string name)
    {
        Match match = Regex.Match(source, @"(?m)^" + Regex.Escape(name) + @"\s*=\s*(?<value>[-+0-9.eE]+)\s*$", RegexOptions.None, TimeSpan.FromSeconds(2));
        Assert.True(match.Success, "Missing authored numeric property: " + name);
        return float.Parse(match.Groups["value"].Value, CultureInfo.InvariantCulture);
    }
    public static float[] Vector(string source, string name, string type)
    {
        Match match = Regex.Match(source, @"(?m)^" + Regex.Escape(name) + @"\s*=\s*" + Regex.Escape(type) + @"\((?<values>[^)]+)\)", RegexOptions.None, TimeSpan.FromSeconds(2));
        Assert.True(match.Success, "Missing authored vector: " + name);
        return match.Groups["values"].Value.Split(',').Select(v => float.Parse(v.Trim(), CultureInfo.InvariantCulture)).ToArray();
    }
    public static void HasBounds(string path, float left, float top, float right, float bottom)
    {
        string source = Node(path);
        Assert.Equal(new[] { left, top, right, bottom }, new[] { Number(source, "offset_left"), Number(source, "offset_top"), Number(source, "offset_right"), Number(source, "offset_bottom") });
    }
    public static void HasAnchor(string path, float x, float y) => Assert.Equal(new[] { x, y }, Vector(Node(path), "source_anchor", "Vector2"));
    public static void HasColor(string path, uint argb)
    {
        static float Channel(uint value) => Math.Min(255u, ((value & 255u) * 255u) >> 7) / 255f;
        float[] expected = [Channel(argb >> 16), Channel(argb >> 8), Channel(argb), (argb >> 24) / 255f];
        Assert.Equal(expected, Vector(Node(path), "ink_color", "Color"));
    }
    public static void HasNoPresentationSideEffects()
    {
        string source = Presentation;
        foreach (string token in new[] { "func _process(", "func _input(", "func _unhandled_input(", "set_process(true)",
            "set_process_input(true)", "set_process_unhandled_input(true)", "Input.", "Time.", "OS.get_ticks", "RandomNumberGenerator",
            "SetLanguage", "set_language(", "AcceptsTwinFade", "HandleKey", "HandlePointerConfirm", "HandlePointerMotion",
            "DrawLoading", "DrawQuitConfirm", "RetailFrontendSession", "frontend_session.gd", "options_controller.gd", "options_laws.gd",
            "level_select", "GetTextExtent", "GetFileVersionInfo", "RetailOptionsApplyPulse", "RetailOptionsMenuItemColor" })
            Assert.DoesNotContain(token, source, StringComparison.Ordinal);
        Assert.Contains("set_process(false)", Controller, StringComparison.Ordinal);
        Assert.Contains("set_process_input(false)", Controller, StringComparison.Ordinal);
        Assert.Contains("set_process_unhandled_input(false)", Controller, StringComparison.Ordinal);
    }
    public static void HasMeasuredReflectionOnly()
    {
        string refresh = Function("main_menu_presentation.gd", "_refresh_reflection");
        Assert.Contains("_facts.reflection_visible", refresh, StringComparison.Ordinal);
        Assert.Contains("get_node(\"TitleLogo/Body\")", refresh, StringComparison.Ordinal);
        Assert.DoesNotContain("Decoration", refresh, StringComparison.Ordinal);
        Assert.DoesNotContain("SelectedIcon", refresh, StringComparison.Ordinal);
        Assert.Contains("render_mode blend_add, unshaded", Reflection, StringComparison.Ordinal);
        Assert.Contains("step(8.0 / 255.0, texture(TEXTURE, UV).a)", Reflection, StringComparison.Ordinal);
        Assert.Contains("Laws.reflection_scroll(seconds)", Reflection, StringComparison.Ordinal);
        Assert.Contains("126.0 / 255.0", Reflection, StringComparison.Ordinal);
    }

    public static void HasNativeHostBridge()
    {
        string bridge = Read("RetailFrontendFlow.MainMenu.cs");
        Assert.Contains("GetNode<Control>(\"Stage/MainMenu\")", bridge, StringComparison.Ordinal);
        Assert.Single(Regex.Matches(bridge, @"\.Call\(""set_frame""", RegexOptions.None, TimeSpan.FromSeconds(2)));
        foreach (string fact in new[] { "[\"transition\"] = MainMenuTransition", "[\"animation_seconds\"] = _animationSeconds",
            "[\"background_seconds\"] = _feBackSeconds", "[\"selected_index\"] = _session.SelectedMainIndex",
            "[\"language\"] = (int)_session.Language", "[\"available\"] = item.IsAvailable",
            "[\"reflection_visible\"] = _session.Screen == RetailFrontendScreen.MainMenu" })
            Assert.Contains(fact, bridge, StringComparison.Ordinal);
        Assert.Contains("Engine.IsEditorHint()", bridge, StringComparison.Ordinal);
        Assert.Contains(".Call(\"show_editor_preview\")", bridge, StringComparison.Ordinal);
        foreach (string forbidden in new[] { "DrawTexture", "DrawString", "DrawRect", "new Control", "new TextureRect",
            "new RetailFrontendSession", "RetailMainMenuLabelColor", "RetailMainMenuLeftDecorOverlay", "MathF.", "ShaderMaterial" })
            Assert.DoesNotContain(forbidden, bridge, StringComparison.Ordinal);
    }
}
