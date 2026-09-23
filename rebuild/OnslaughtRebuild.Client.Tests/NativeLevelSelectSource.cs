// SPDX-License-Identifier: GPL-3.0-or-later

namespace OnslaughtRebuild.Client.Tests;

/// <summary>Separates the retained 51477f62 renderer's evidence calls from
/// production native ownership guards. Actual geometry and pixel comparisons
/// belong to the Level Select scene harness, not these source assertions.</summary>
internal static class NativeLevelSelectSource
{
    public static string Read(string name) => File.ReadAllText(Path.Combine(
        AppContext.BaseDirectory, "godot-level-select-source", name));
    public static string Reference => Read("LevelSelectReference.cs");
    public static string Bridge => Read("RetailFrontendFlow.LevelSelect.cs");
    public static string Controller => Read("level_select_presentation.gd");
    public static string Scene => Read("LevelSelect.tscn");
    public static string Presentation => string.Join('\n', Controller, Scene,
        Read("level_select_arc.gd"), Read("level_select_link.gd"));

    public static string Function(string method)
    {
        string source = Controller, signature = "func " + method + "(";
        int start = source.IndexOf(signature, StringComparison.Ordinal);
        Assert.True(start >= 0, "level_select_presentation.gd: " + signature);
        int next = source.IndexOf("\nfunc ", start, StringComparison.Ordinal);
        int nextStatic = source.IndexOf("\nstatic func ", start, StringComparison.Ordinal);
        if (next < 0 || nextStatic >= 0 && nextStatic < next) next = nextStatic;
        return next < 0 ? source[start..] : source[start..next];
    }
}
