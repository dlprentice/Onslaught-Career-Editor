// SPDX-License-Identifier: GPL-3.0-or-later
namespace OnslaughtRebuild.Client.Tests;

/// <summary>Source wiring for the actual native frontend owner and its page batches.
/// Executed scene, callback and rendering checks remain separate.</summary>
internal static class NativeFrontendSource
{
    public static string Read(string name) => File.ReadAllText(Path.Combine(AppContext.BaseDirectory, "godot-frontend-source", name));
    public static string Root => Read("frontend_flow.gd");
    public static string Pages => Read("frontend_pages.gd");
    public static string RootFunction(string method) => Function(Root, method);
    public static string PageFunction(string method) => Function(Pages, method);
    private static string Function(string source, string method)
    {
        int start = source.IndexOf("func " + method + "(", StringComparison.Ordinal);
        Assert.True(start >= 0, "Missing production native function: " + method);
        int end = source.Length;
        foreach (string marker in new[] { "\nfunc ", "\nstatic func " })
        {
            int next = source.IndexOf(marker, start, StringComparison.Ordinal);
            if (next >= 0) end = Math.Min(end, next);
        }
        return source[start..end];
    }
    public static string PageBranch(string owner)
    {
        string source = PageFunction("redraw");
        int start = source.IndexOf("\tif _" + owner + " != null and _" + owner + ".visible:", StringComparison.Ordinal);
        Assert.True(start >= 0, "Missing production page branch: " + owner);
        int end = source.IndexOf("\n\tif ", start, StringComparison.Ordinal);
        return end < 0 ? source[start..] : source[start..end];
    }
    public static string PointerArm(string screen)
    {
        string source = RootFunction("handle_pointer_confirm");
        string marker = "\n\t\tFrontend.Screen." + screen + ":";
        int start = source.IndexOf(marker, StringComparison.Ordinal);
        Assert.True(start >= 0, "Missing native pointer arm: " + screen);
        int end = source.IndexOf("\n\t\tFrontend.Screen.", start + marker.Length, StringComparison.Ordinal);
        return end < 0 ? source[start..] : source[start..end];
    }
}
