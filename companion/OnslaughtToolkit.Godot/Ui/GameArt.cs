// SPDX-License-Identifier: MIT
using Godot;

namespace OnslaughtToolkit.Companion.Ui;

/// <summary>
/// Pictures read from the player's own install at run time and never bundled: the Battle Engine render
/// and the map of Allium from the game's manual, and the game's splash screen. Missing or unreadable
/// files simply mean no picture.
/// </summary>
internal static class GameArt
{
    internal const string Banner = "Manuals/Images/image003.png";
    internal const string Map = "Manuals/Images/gamemap.jpg";
    internal const string Splash = "data/textures/splash.tga";
    private const long MaxBytes = 16L << 20;

    private static readonly Dictionary<string, Texture2D?> Cache = [];

    /// <summary>A picture from the game folder, or null.</summary>
    internal static Texture2D? Load(string? gameRoot, string relative)
    {
        if (gameRoot is null) return null;
        string path = System.IO.Path.Combine(gameRoot, relative);
        if (Cache.TryGetValue(path, out Texture2D? cached)) return cached;
        Texture2D? texture = null;
        try
        {
            FileInfo file = new(path);
            if (file.Exists && file.Length is > 0 and <= MaxBytes && file.LinkTarget is null)
            {
                byte[] bytes = File.ReadAllBytes(path);
                Image image = new();
                Error loaded = System.IO.Path.GetExtension(path).ToLowerInvariant() switch
                {
                    ".png" => image.LoadPngFromBuffer(bytes),
                    ".jpg" or ".jpeg" => image.LoadJpgFromBuffer(bytes),
                    ".tga" => image.LoadTgaFromBuffer(bytes),
                    _ => Error.FileUnrecognized,
                };
                if (loaded == Error.Ok && !image.IsEmpty())
                {
                    image.GenerateMipmaps();
                    texture = ImageTexture.CreateFromImage(image);
                }
            }
        }
        catch (Exception error) when (error is IOException or UnauthorizedAccessException)
        {
        }
        Cache[path] = texture;
        return texture;
    }

    /// <summary>The game's manual page for a language the install has, preferring English.</summary>
    internal static string? Manual(string? gameRoot)
    {
        if (gameRoot is null) return null;
        foreach (string language in new[] { "English", "French", "German", "Italian", "Spanish" })
        {
            string page = System.IO.Path.Combine(gameRoot, "Manuals", language, language + ".htm");
            if (File.Exists(page)) return page;
        }
        return null;
    }

    internal static void Clear() => Cache.Clear();
}
