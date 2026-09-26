// SPDX-License-Identifier: MIT
using Godot;

namespace OnslaughtToolkit.Companion.Ui;

/// <summary>
/// The companion's line icons, written as SVG in code and rendered at twice their drawn size so they
/// stay sharp on high-density screens. Drawn in white; buttons tint them through the theme's icon colours.
/// </summary>
internal static class Icons
{
    /// <summary>Logical size an icon occupies in a button.</summary>
    internal const int Size = 20;

    private const string Frame = "<svg xmlns=\"http://www.w3.org/2000/svg\" width=\"24\" height=\"24\" viewBox=\"0 0 24 24\" " +
        "fill=\"none\" stroke=\"#ffffff\" stroke-width=\"1.8\" stroke-linecap=\"round\" stroke-linejoin=\"round\">{0}</svg>";

    private static readonly Dictionary<string, string> Shapes = new()
    {
        ["home"] = "<path d=\"M3 11.5 12 4l9 7.5\"/><path d=\"M5.5 9.5V20h13V9.5\"/><path d=\"M10 20v-5.5h4V20\"/>",
        ["summary"] = "<path d=\"M4 20h16\"/><path d=\"M7 16.5V11\"/><path d=\"M12 16.5V6\"/><path d=\"M17 16.5v-8\"/>",
        ["goodies"] = "<path d=\"M12 3.5l2.6 5.3 5.9.9-4.3 4.1 1 5.8L12 16.9l-5.2 2.7 1-5.8-4.3-4.1 5.9-.9z\"/>",
        ["edit"] = "<path d=\"M4 20h4L19.5 8.5l-4-4L4 16z\"/><path d=\"M13.5 6.5l4 4\"/>",
        ["cheats"] = "<path d=\"M12 3v4M12 17v4M3 12h4M17 12h4\"/><path d=\"M6.3 6.3l2.2 2.2M15.5 15.5l2.2 2.2M6.3 17.7l2.2-2.2M15.5 8.5l2.2-2.2\"/>",
        ["settings"] = "<path d=\"M4 7h9M17 7h3M4 12h3M11 12h9M4 17h11M19 17h1\"/><circle cx=\"15\" cy=\"7\" r=\"2\"/>" +
            "<circle cx=\"9\" cy=\"12\" r=\"2\"/><circle cx=\"17\" cy=\"17\" r=\"2\"/>",
        ["backups"] = "<path d=\"M12 3.5l7.5 2.8v5.4c0 4.6-3.2 7.6-7.5 8.8-4.3-1.2-7.5-4.2-7.5-8.8V6.3z\"/><path d=\"M8.8 12.2l2.2 2.2 4.3-4.6\"/>",
        ["music"] = "<path d=\"M9 18V5.5l11-2V16\"/><circle cx=\"6.5\" cy=\"18\" r=\"2.5\"/><circle cx=\"17.5\" cy=\"16\" r=\"2.5\"/>",
        ["lore"] = "<path d=\"M5 4.5A1.5 1.5 0 0 1 6.5 3H19v15H6.5A1.5 1.5 0 0 0 5 19.5z\"/><path d=\"M5 19.5A1.5 1.5 0 0 0 6.5 21H19v-3\"/>" +
            "<path d=\"M9 7.5h6\"/>",
        ["compare"] = "<rect x=\"3.5\" y=\"4\" width=\"7\" height=\"16\" rx=\"1\"/><rect x=\"13.5\" y=\"4\" width=\"7\" height=\"16\" rx=\"1\"/>" +
            "<path d=\"M6 9h2M16 9h2M6 13h2M16 13h2\"/>",
        ["raw"] = "<path d=\"M8 3.5c-2 0-2.8 1-2.8 2.8v2.9L3.5 12l1.7 2.8v2.9c0 1.8.8 2.8 2.8 2.8\"/>" +
            "<path d=\"M16 3.5c2 0 2.8 1 2.8 2.8v2.9l1.7 2.8-1.7 2.8v2.9c0 1.8-.8 2.8-2.8 2.8\"/>",
        ["folder"] = "<path d=\"M3.5 6.5a1 1 0 0 1 1-1h5l2 2h8a1 1 0 0 1 1 1v9.5a1 1 0 0 1-1 1h-15a1 1 0 0 1-1-1z\"/>",
        ["play"] = "<path d=\"M8 5l11 7-11 7z\" fill=\"#ffffff\"/>",
        ["open"] = "<path d=\"M3.5 7a1 1 0 0 1 1-1h4.5l2 2h8a1 1 0 0 1 1 1v1\"/><path d=\"M3.5 7v11l2.5-7h15l-2.5 7h-15\"/>",
        ["restore"] = "<path d=\"M4 12a8 8 0 1 0 2.4-5.7\"/><path d=\"M4 4v4h4\"/><path d=\"M12 8v4.5l3 1.8\"/>",
        ["external"] = "<path d=\"M14 4h6v6M20 4l-9 9\"/><path d=\"M18 14v5a1 1 0 0 1-1 1H5a1 1 0 0 1-1-1V7a1 1 0 0 1 1-1h5\"/>",
        ["check"] = "<path d=\"M5 12.5l4.5 4.5L19 7.5\"/>",
        ["warning"] = "<path d=\"M12 4l9 16H3z\"/><path d=\"M12 10v4.5M12 17.5v.5\"/>",
        ["down"] = "<path d=\"M6 9l6 6 6-6\"/>",
        ["right"] = "<path d=\"M9 6l6 6-6 6\"/>",
        ["save"] = "<path d=\"M5 4h11l3 3v12a1 1 0 0 1-1 1H6a1 1 0 0 1-1-1z\"/><path d=\"M8 4v5h7V4\"/><path d=\"M8 20v-6h8v6\"/>",
        ["book"] = "<path d=\"M12 6.5C10 5 7 4.5 4 5v13c3-.5 6 0 8 1.5 2-1.5 5-2 8-1.5V5c-3-.5-6 0-8 1.5z\"/><path d=\"M12 6.5v13\"/>",
    };

    private static readonly Dictionary<string, Texture2D> Cache = [];

    /// <summary>The named icon as a texture, rendered once and reused.</summary>
    internal static Texture2D Get(string name)
    {
        if (Cache.TryGetValue(name, out Texture2D? texture)) return texture;
        Image image = new();
        Error loaded = image.LoadSvgFromString(string.Format(Frame, Shapes[name]), 2f);
        texture = loaded == Error.Ok ? ImageTexture.CreateFromImage(image) : new PlaceholderTexture2D { Size = new Vector2(48, 48) };
        Cache[name] = texture;
        return texture;
    }

    internal static IReadOnlyCollection<string> Names => Shapes.Keys;

    /// <summary>Drops the rendered textures; called when the application closes so nothing outlives the engine.</summary>
    internal static void Clear() => Cache.Clear();
}
