// SPDX-License-Identifier: GPL-3.0-or-later

namespace OnslaughtRebuild.Client.Tests;

/// <summary>Existing quit consumer/isolation guards inspect the actual native
/// component; retained C# comparison drawing cannot satisfy these checks.</summary>
internal static class NativeQuitSource
{
    private static string DirectoryPath => Path.Combine(AppContext.BaseDirectory, "godot-quit-source");
    public static string Read(string name) => File.ReadAllText(Path.Combine(DirectoryPath, name));
    public static string Scene => Read("QuitConfirm.tscn");
    public static string Controller => Read("quit_confirm_presentation.gd");
    public static string Bridge => NativeFrontendSource.PageBranch("quit");
    public static string Node(string path) => NativeMainMenuSource.Node(path, Scene);
    public static void HasColor(string path, uint argb) => NativeMainMenuSource.HasColorIn(Node(path), argb);
    public static string Presentation
    {
        get
        {
            string[] scripts = Directory.GetFiles(DirectoryPath, "quit_confirm_*.gd");
            Assert.NotEmpty(scripts);
            return Scene + "\n" + string.Join('\n', scripts.Order(StringComparer.Ordinal).Select(File.ReadAllText));
        }
    }
}
