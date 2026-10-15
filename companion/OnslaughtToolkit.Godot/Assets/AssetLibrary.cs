// SPDX-License-Identifier: MIT
namespace OnslaughtToolkit.Companion.Assets;

public enum AssetKind { Model, Texture }

/// <summary>One of the game's model or texture files, found in the player's install. Nothing is copied or bundled.</summary>
public sealed record GameAsset(AssetKind Kind, string Title, string Path, string Group, long Size);

/// <summary>
/// The models (<c>data/resources/meshes/*.aya</c>) and textures (<c>data/resources/dxtntextures</c> and
/// <c>data/resources/textures</c>) in the player's install, and the lookup from a model's texture name to its file.
/// Read-only.
/// </summary>
public sealed class AssetLibrary
{
    private readonly Dictionary<string, string> _textureByPrefix = new(StringComparer.OrdinalIgnoreCase);

    public IReadOnlyList<GameAsset> Models { get; }
    public IReadOnlyList<GameAsset> Textures { get; }

    private AssetLibrary(IReadOnlyList<GameAsset> models, IReadOnlyList<GameAsset> textures)
    {
        (Models, Textures) = (models, textures);
        foreach (GameAsset texture in textures)
        {
            // "meshtex%warspite-PAGE2.tga(0)X8R8G8B8.aya": the requested name with "\" flattened to "%", then the frame
            // and the requested format. The first file per name wins; the name is what a model asks for.
            string name = System.IO.Path.GetFileName(texture.Path);
            int bracket = name.LastIndexOf("(0)", StringComparison.Ordinal);
            if (bracket > 0) _textureByPrefix.TryAdd(name[..bracket], texture.Path);
        }
    }

    public static AssetLibrary Scan(string gameRoot)
    {
        string resources = System.IO.Path.Combine(gameRoot, "data", "resources");
        List<GameAsset> models = [], textures = [];
        foreach (FileInfo file in Files(System.IO.Path.Combine(resources, "meshes")))
            models.Add(new GameAsset(AssetKind.Model, ModelTitle(file.Name), file.FullName, "Models", file.Length));
        foreach ((string folder, string group) in new[] { ("dxtntextures", "Textures"), ("textures", "Interface textures") })
            foreach (FileInfo file in Files(System.IO.Path.Combine(resources, folder)))
                textures.Add(new GameAsset(AssetKind.Texture, TextureTitle(file.Name), file.FullName, group, file.Length));
        return new AssetLibrary(models, textures);
    }

    /// <summary>The texture file for a name a model asks for (for example <c>meshtex\warspite-PAGE2.tga</c>), or null.</summary>
    public string? FindTexture(string requested)
    {
        if (string.IsNullOrWhiteSpace(requested)) return null;
        return _textureByPrefix.TryGetValue(requested.Replace('\\', '%').Replace('/', '%'), out string? path) ? path : null;
    }

    /// <summary>"m_arachnid.msh.aya" → "arachnid".</summary>
    public static string ModelTitle(string file)
    {
        string name = file.EndsWith(".msh.aya", StringComparison.OrdinalIgnoreCase) ? file[..^8] : System.IO.Path.GetFileNameWithoutExtension(file);
        return name.StartsWith("m_", StringComparison.OrdinalIgnoreCase) ? name[2..] : name;
    }

    /// <summary>"meshtex%warspite-PAGE2.tga(0)X8R8G8B8.aya" → "meshtex/warspite-PAGE2".</summary>
    public static string TextureTitle(string file)
    {
        string name = file;
        int bracket = name.LastIndexOf('(');
        if (bracket > 0) name = name[..bracket];
        if (name.EndsWith(".tga", StringComparison.OrdinalIgnoreCase)) name = name[..^4];
        if (name.StartsWith("mustbe_", StringComparison.OrdinalIgnoreCase)) name = name[7..];
        return name.Replace('%', '/');
    }

    private static IEnumerable<FileInfo> Files(string folder)
    {
        if (!Directory.Exists(folder)) return [];
        return new DirectoryInfo(folder).EnumerateFiles("*.aya", new EnumerationOptions { IgnoreInaccessible = true, RecurseSubdirectories = false })
            .Where(file => file.LinkTarget is null)
            .OrderBy(file => file.Name, StringComparer.OrdinalIgnoreCase);
    }
}
