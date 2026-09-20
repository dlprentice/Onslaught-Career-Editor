// SPDX-License-Identifier: GPL-3.0-or-later
using System.Globalization;

namespace OnslaughtRebuild.Client.Tests;

/// <summary>Routes the existing Click isolation guards to its live native
/// scene, expressions and one host fact bridge. The retained C# reference is
/// kept separate so dead drawing code cannot satisfy a production guard.</summary>
internal static class NativeClickSource
{
    public static string Read(string name) => File.ReadAllText(Path.Combine(
        AppContext.BaseDirectory, "godot-click-source", name));

    public static string Controller => Read("click_presentation.gd");
    public static string Laws => Read("click_to_start_laws.gd");
    public static string Scene => Read("ClickToStart.tscn");
    public static string Bridge => Read("RetailFrontendFlow.Click.cs");
    public static string Presentation => Controller + "\n" + Laws + "\n" + Scene +
        "\n" + Read("click_preview.gd") + "\n" + Read("frontend_image.gd") +
        "\n" + Read("frontend_bitmap_label.gd") + "\n" + Bridge;

    public static string Node(string path)
    {
        string[] components = path.Split('/');
        string name = components[^1];
        string parent = components.Length == 1 ? "." : string.Join('/', components[..^1]);
        string scene = Scene;
        int start = 0;
        while ((start = scene.IndexOf("[node name=\"" + name + "\"", start, StringComparison.Ordinal)) >= 0)
        {
            int headerEnd = scene.IndexOf('\n', start);
            string header = scene[start..headerEnd];
            if (header.Contains("parent=\"" + parent + "\"", StringComparison.Ordinal))
            {
                int end = scene.IndexOf("\n[node ", headerEnd, StringComparison.Ordinal);
                return end < 0 ? scene[start..] : scene[start..end];
            }
            start = headerEnd;
        }
        throw new InvalidOperationException("Missing production Click node: " + path);
    }

    public static void HasContentOrigin(string path, float x, float y) => Assert.Contains(
        "content_origin = Vector2(" + x.ToString("R", CultureInfo.InvariantCulture) + ", " +
        y.ToString("R", CultureInfo.InvariantCulture) + ")", Node(path), StringComparison.Ordinal);

    public static void HasCenter(string path, float x, float y) => Assert.Contains(
        "center = Vector2(" + x.ToString("R", CultureInfo.InvariantCulture) + ", " +
        y.ToString("R", CultureInfo.InvariantCulture) + ")", Node(path), StringComparison.Ordinal);

    public static void HasNoPresentationSideEffects()
    {
        string source = Presentation;
        foreach (string token in new[] { "func _process(", "func _input(", "func _unhandled_input(",
            "set_process(true)", "set_process_input(true)", "set_process_unhandled_input(true)",
            "Input.", "Time.", "OS.get_ticks", "ConfirmForSmoke", "DispatchConfirm", "dispatch_confirm",
            "ResetFlags", "reset_flags", "WriteAttractResult", "write_attract_result",
            "StashPageField", "stash_page_field", "ResetPageFields", "reset_page_fields",
            "WriteConsumedLatch", "write_consumed_latch", "RetailFrontendSession", "frontend_session.gd" })
            Assert.DoesNotContain(token, source, StringComparison.Ordinal);
        Assert.Contains("set_process(false)", Controller, StringComparison.Ordinal);
        Assert.Contains("set_process_input(false)", Controller, StringComparison.Ordinal);
        Assert.Contains("set_process_unhandled_input(false)", Controller, StringComparison.Ordinal);
    }
}
