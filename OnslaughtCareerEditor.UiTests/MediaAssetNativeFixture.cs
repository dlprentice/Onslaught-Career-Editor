using System.Drawing;
using System.Security.Cryptography;
using System.Text;
using Onslaught___Career_Editor;

namespace OnslaughtCareerEditor.UiTests;

internal static class MediaAssetNativeFixtureContract
{
    internal const int SchemaVersion = 1;

    internal static readonly IReadOnlyList<string> ExpectedRelativePaths =
    [
        "asset-bundle/asset_catalog/catalog.json",
        "asset-bundle/exports/body00_binary.fbx",
        "asset-bundle/exports/fixture_mesh_binary.fbx",
        "asset-bundle/exports/fixture_texture.png",
        "media-game/BEA.exe",
        "media-game/data/Music/battle_theme (Master).ogg",
        "media-game/data/sounds/english/MessageBox/110_arrival.ogg",
        "media-game/data/sounds/english/MessageBox/HEALTH_low.ogg",
        "media-game/data/sounds/english/MessageBox/TUTORIAL_intro.ogg",
        "media-game/data/video/OpeningFMV.vid",
        "media-game/data/video/UsTheMovie.vid",
        "media-game/data/video/briefings/PC_101_exact.vid",
        "media-game/data/video/cutscenes/02.vid",
    ];
}

internal sealed record MediaAssetNativeFixtureFile(
    string RelativePath,
    long Length,
    string Sha256);

internal sealed record MediaAssetNativeFixture(
    string RootPath,
    string MediaGameDirectory,
    string AssetCatalogPath,
    IReadOnlyList<MediaAssetNativeFixtureFile> Files);

internal static class MediaAssetNativeFixtureBuilder
{
    private static readonly byte[] FixturePng =
    [
        137, 80, 78, 71, 13, 10, 26, 10,
        0, 0, 0, 13, 73, 72, 68, 82,
        0, 0, 0, 8, 0, 0, 0, 8,
        8, 6, 0, 0, 0, 196, 15, 190,
        139, 0, 0, 0, 1, 115, 82, 71,
        66, 0, 174, 206, 28, 233, 0, 0,
        0, 4, 103, 65, 77, 65, 0, 0,
        177, 143, 11, 252, 97, 5, 0, 0,
        0, 9, 112, 72, 89, 115, 0, 0,
        14, 195, 0, 0, 14, 195, 1, 199,
        111, 168, 100, 0, 0, 0, 51, 73,
        68, 65, 84, 40, 83, 99, 248, 24,
        165, 242, 31, 132, 245, 27, 222, 130,
        241, 175, 95, 191, 192, 88, 66, 66,
        26, 140, 25, 8, 42, 192, 37, 1,
        211, 72, 88, 1, 46, 9, 152, 70,
        194, 10, 112, 73, 192, 52, 18, 84,
        0, 0, 105, 52, 164, 1, 119, 41,
        241, 130, 0, 0, 0, 0, 73, 69,
        78, 68, 174, 66, 96, 130,
    ];

    private const string CatalogJson = """
        {
          "schema_version": 2,
          "path_contract": "bundle-root-relative",
          "summary": {
            "texture_catalog_entries": 1,
            "loose_mesh_catalog_entries": 1,
            "embedded_mesh_catalog_entries": 1,
            "video_catalog_entries": 0,
            "language_catalog_entries": 0,
            "goodie_catalog_entries": 1,
            "total_catalog_entries": 4
          },
          "textures": [
            {
              "catalog_id": "texture:fixture/texture_one.tga",
              "kind": "texture",
              "canonical_ref": "fixture/texture_one.tga",
              "source_roots": ["fixture"],
              "export_png_paths": ["exports/fixture_texture.png"],
              "source_aya_count": 1,
              "export_png_count": 1,
              "packed_text_ref_count": 1,
              "gdie_ref_count": 0
            }
          ],
          "loose_meshes": [
            {
              "catalog_id": "mesh:fixture_mesh.msh",
              "kind": "loose_mesh",
              "canonical_ref": "fixture_mesh.msh",
              "export_fbx_paths": ["exports/fixture_mesh_binary.fbx"],
              "source_aya_count": 1,
              "export_fbx_count": 1,
              "packed_reference_count": 1,
              "gdie_ref_count": 0
            }
          ],
          "embedded_meshes": [
            {
              "catalog_id": "embedded_mesh:fixture/body00",
              "kind": "embedded_mesh",
              "source_archive": "fixture",
              "body_name": "body00",
              "export_fbx_path": "exports/body00_binary.fbx"
            }
          ],
          "videos": [],
          "language_rows": [],
          "goodies": [
            {
              "catalog_id": "goodie:008",
              "kind": "goodie",
              "index": 8,
              "display_name": "Goodie 008 - Synthetic Unit",
              "content_kind": "Model",
              "source_title": "Synthetic Unit",
              "source_archive": "fixture.aya",
              "gdie_family": "fixture.aya",
              "texture_refs": ["fixture/texture_one.tga"],
              "mesh_refs": ["fixture_mesh.msh"],
              "primary_texture_ref": "fixture/texture_one.tga",
              "primary_mesh_ref": "fixture_mesh.msh",
              "video_sequence_id": "",
              "video_catalog_id": "",
              "video_relative_path": ""
            }
          ]
        }
        """;

    internal static MediaAssetNativeFixture Build(string fixtureRoot)
    {
        string root = Path.GetFullPath(fixtureRoot);
        if (Directory.Exists(root) || File.Exists(root))
        {
            throw new InvalidOperationException("Media/Asset fixture root must be fresh and caller-owned.");
        }

        Directory.CreateDirectory(root);
        string mediaRoot = Path.Combine(root, "media-game");
        string assetRoot = Path.Combine(root, "asset-bundle");
        string catalogPath = Path.Combine(assetRoot, "asset_catalog", "catalog.json");
        string exportsRoot = Path.Combine(assetRoot, "exports");

        WriteFile(Path.Combine(mediaRoot, "BEA.exe"), []);
        WriteFile(Path.Combine(mediaRoot, "data", "Music", "battle_theme (Master).ogg"), []);
        WriteFile(Path.Combine(mediaRoot, "data", "sounds", "english", "MessageBox", "110_arrival.ogg"), []);
        WriteFile(Path.Combine(mediaRoot, "data", "sounds", "english", "MessageBox", "HEALTH_low.ogg"), []);
        WriteFile(Path.Combine(mediaRoot, "data", "sounds", "english", "MessageBox", "TUTORIAL_intro.ogg"), []);
        WriteFile(Path.Combine(mediaRoot, "data", "video", "OpeningFMV.vid"), []);
        WriteFile(Path.Combine(mediaRoot, "data", "video", "UsTheMovie.vid"), []);
        WriteFile(Path.Combine(mediaRoot, "data", "video", "briefings", "PC_101_exact.vid"), []);
        WriteFile(Path.Combine(mediaRoot, "data", "video", "cutscenes", "02.vid"), []);

        byte[] binaryFbx = BuildMinimalBinaryFbx("texture_one.tga");
        WriteFile(catalogPath, new UTF8Encoding(encoderShouldEmitUTF8Identifier: false).GetBytes(CatalogJson));
        WriteFile(Path.Combine(exportsRoot, "body00_binary.fbx"), binaryFbx);
        WriteFile(Path.Combine(exportsRoot, "fixture_mesh_binary.fbx"), binaryFbx);
        WriteFile(Path.Combine(exportsRoot, "fixture_texture.png"), FixturePng);

        var fixture = new MediaAssetNativeFixture(
            root,
            mediaRoot,
            catalogPath,
            MediaAssetNativeFixtureContract.ExpectedRelativePaths
                .Select(relativePath =>
                {
                    string fullPath = ResolveRelative(root, relativePath);
                    return new MediaAssetNativeFixtureFile(
                        relativePath,
                        new FileInfo(fullPath).Length,
                        Hash(fullPath));
                })
                .ToArray());
        Validate(fixture);
        return fixture;
    }

    internal static void Validate(MediaAssetNativeFixture fixture)
    {
        string root = Path.GetFullPath(fixture.RootPath);
        if (!Directory.Exists(root))
        {
            throw new InvalidOperationException("Media/Asset fixture root is missing.");
        }

        RequireConfined(root, fixture.MediaGameDirectory, "media game directory");
        RequireConfined(root, fixture.AssetCatalogPath, "asset catalog");
        RequireReparseFreeTree(root);

        string[] actualPaths = Directory.EnumerateFiles(root, "*", SearchOption.AllDirectories)
            .Select(path => NormalizeRelative(Path.GetRelativePath(root, path)))
            .OrderBy(path => path, StringComparer.Ordinal)
            .ToArray();
        if (!actualPaths.SequenceEqual(MediaAssetNativeFixtureContract.ExpectedRelativePaths, StringComparer.Ordinal))
        {
            throw new InvalidOperationException("Media/Asset fixture file inventory is not exact.");
        }

        if (fixture.Files.Count != MediaAssetNativeFixtureContract.ExpectedRelativePaths.Count ||
            !fixture.Files.Select(row => row.RelativePath)
                .SequenceEqual(MediaAssetNativeFixtureContract.ExpectedRelativePaths, StringComparer.Ordinal))
        {
            throw new InvalidOperationException("Media/Asset fixture receipt inventory is not canonical.");
        }

        foreach (MediaAssetNativeFixtureFile receipt in fixture.Files)
        {
            string path = ResolveRelative(root, receipt.RelativePath);
            if (!File.Exists(path) ||
                new FileInfo(path).Length != receipt.Length ||
                !string.Equals(Hash(path), receipt.Sha256, StringComparison.Ordinal))
            {
                throw new InvalidOperationException($"Media/Asset fixture receipt changed: {receipt.RelativePath}");
            }
        }

        foreach (string relativePath in MediaAssetNativeFixtureContract.ExpectedRelativePaths.Where(
            path => path.StartsWith("media-game/", StringComparison.Ordinal)))
        {
            if (new FileInfo(ResolveRelative(root, relativePath)).Length != 0)
            {
                throw new InvalidOperationException($"Synthetic media marker must remain zero length: {relativePath}");
            }
        }

        MediaCatalogSnapshot media = new MediaCatalogService().Load(fixture.MediaGameDirectory);
        if (!MediaCatalogService.LooksLikeGameDirectory(fixture.MediaGameDirectory) ||
            media.AudioItems.Count != 4 ||
            media.VideoItems.Count != 4 ||
            media.AudioItems.SingleOrDefault(row => row.Name == "TUTORIAL_intro") is null ||
            media.VideoItems.SingleOrDefault(row => row.Name == "Credits Video") is null)
        {
            throw new InvalidOperationException("Synthetic Media fixture did not independently reparse to the canonical catalog.");
        }

        AssetCatalogSnapshot assets = new AssetCatalogService().Load(fixture.AssetCatalogPath);
        AssetModelSummary? model = assets.LooseMeshes.SingleOrDefault()?.ModelSummary;
        if (assets.Summary != new AssetCatalogSummary(1, 1, 1, 0, 0, 1, 4) ||
            assets.Textures.SingleOrDefault()?.CatalogId != "texture:fixture/texture_one.tga" ||
            assets.LooseMeshes.SingleOrDefault()?.CatalogId != "mesh:fixture_mesh.msh" ||
            assets.EmbeddedMeshes.SingleOrDefault()?.CatalogId != "embedded_mesh:fixture/body00" ||
            assets.Goodies.SingleOrDefault()?.CatalogId != "goodie:008" ||
            model is null || !model.MetadataAvailable || model.VertexCount != 3 ||
            model.PolygonIndexCount != 3 || !model.GeometryPreview.Available)
        {
            throw new InvalidOperationException("Synthetic Asset fixture did not independently reparse to the canonical catalog and triangle.");
        }

        using var texture = new Bitmap(assets.Textures.Single().ExportPath);
        int distinctColors = Enumerable.Range(0, texture.Width)
            .SelectMany(x => Enumerable.Range(0, texture.Height).Select(y => texture.GetPixel(x, y).ToArgb()))
            .Distinct()
            .Count();
        if (texture.Size != new Size(8, 8) || distinctColors < 4)
        {
            throw new InvalidOperationException("Synthetic Asset fixture PNG contrast contract changed.");
        }
    }

    private static void WriteFile(string path, ReadOnlySpan<byte> bytes)
    {
        string? directory = Path.GetDirectoryName(path);
        if (string.IsNullOrWhiteSpace(directory))
        {
            throw new InvalidOperationException("Fixture file requires an owned parent directory.");
        }

        Directory.CreateDirectory(directory);
        using FileStream stream = new(path, FileMode.CreateNew, FileAccess.Write, FileShare.None);
        stream.Write(bytes);
        stream.Flush(flushToDisk: true);
    }

    private static string ResolveRelative(string root, string relativePath)
    {
        if (Path.IsPathRooted(relativePath) ||
            relativePath.Contains('\\') ||
            relativePath.Split('/').Any(segment => segment is "" or "." or ".."))
        {
            throw new InvalidOperationException("Fixture paths must be normalized relative paths.");
        }

        string fullPath = Path.GetFullPath(Path.Combine(root, relativePath.Replace('/', Path.DirectorySeparatorChar)));
        RequireConfined(root, fullPath, $"fixture file {relativePath}");
        return fullPath;
    }

    private static void RequireConfined(string root, string path, string label)
    {
        string relative = Path.GetRelativePath(Path.GetFullPath(root), Path.GetFullPath(path));
        if (relative == ".." || relative.StartsWith($"..{Path.DirectorySeparatorChar}", StringComparison.Ordinal))
        {
            throw new InvalidOperationException($"{label} escaped the fixture root.");
        }
    }

    private static void RequireReparseFreeTree(string root)
    {
        IEnumerable<string> paths = new[] { root }
            .Concat(Directory.EnumerateFileSystemEntries(root, "*", SearchOption.AllDirectories));
        foreach (string path in paths)
        {
            if ((File.GetAttributes(path) & FileAttributes.ReparsePoint) != 0)
            {
                throw new InvalidOperationException($"Media/Asset fixture tree must be reparse-free: {path}");
            }
        }
    }

    private static string NormalizeRelative(string relativePath) =>
        relativePath.Replace(Path.DirectorySeparatorChar, '/');

    private static string Hash(string path) =>
        Convert.ToHexString(SHA256.HashData(File.ReadAllBytes(path)));

    private static byte[] BuildMinimalBinaryFbx(string textureFileName)
    {
        using MemoryStream stream = new();
        using BinaryWriter writer = new(stream, Encoding.ASCII, leaveOpen: true);

        writer.Write(Encoding.ASCII.GetBytes("Kaydara FBX Binary  "));
        writer.Write((byte)0);
        writer.Write((byte)0x1A);
        writer.Write((byte)0);
        writer.Write(7400);
        WriteNode(
            writer,
            "Objects",
            props: [],
            children:
            [
                () => WriteNode(
                    writer,
                    "Geometry",
                    props:
                    [
                        () => WriteLongProperty(writer, 1),
                        () => WriteStringProperty(writer, "Fixture\0\u0001Geometry"),
                        () => WriteStringProperty(writer, "Mesh"),
                    ],
                    children:
                    [
                        () => WriteNode(
                            writer,
                            "Vertices",
                            props: [() => WriteDoubleArrayProperty(writer, [0, 0, 0, 1, 0, 0, 0, 1, 0])],
                            children: []),
                        () => WriteNode(
                            writer,
                            "PolygonVertexIndex",
                            props: [() => WriteIntArrayProperty(writer, [0, 1, -3])],
                            children: []),
                    ]),
                () => WriteNode(writer, "Model", [() => WriteLongProperty(writer, 2), () => WriteStringProperty(writer, "Fixture\0\u0001Model"), () => WriteStringProperty(writer, "Mesh")], []),
                () => WriteNode(writer, "Material", [() => WriteLongProperty(writer, 3), () => WriteStringProperty(writer, "Material1\0\u0001Material"), () => WriteStringProperty(writer, string.Empty)], []),
                () => WriteNode(writer, "Texture", [() => WriteLongProperty(writer, 4), () => WriteStringProperty(writer, "base_color_texture\0\u0001Texture"), () => WriteStringProperty(writer, string.Empty), () => WriteStringProperty(writer, textureFileName)], []),
            ]);
        WriteSentinel(writer);
        return stream.ToArray();
    }

    private static void WriteNode(BinaryWriter writer, string name, Action[] props, Action[] children)
    {
        long headerPosition = writer.BaseStream.Position;
        writer.Write((uint)0);
        writer.Write((uint)props.Length);
        writer.Write((uint)0);
        writer.Write((byte)name.Length);
        writer.Write(Encoding.ASCII.GetBytes(name));

        long propertyStart = writer.BaseStream.Position;
        foreach (Action prop in props)
        {
            prop();
        }

        long propertyEnd = writer.BaseStream.Position;
        foreach (Action child in children)
        {
            child();
        }

        if (children.Length > 0)
        {
            WriteSentinel(writer);
        }

        long endPosition = writer.BaseStream.Position;
        writer.BaseStream.Position = headerPosition;
        writer.Write((uint)endPosition);
        writer.Write((uint)props.Length);
        writer.Write((uint)(propertyEnd - propertyStart));
        writer.Write((byte)name.Length);
        writer.BaseStream.Position = endPosition;
    }

    private static void WriteLongProperty(BinaryWriter writer, long value)
    {
        writer.Write((byte)'L');
        writer.Write(value);
    }

    private static void WriteStringProperty(BinaryWriter writer, string value)
    {
        byte[] bytes = Encoding.UTF8.GetBytes(value);
        writer.Write((byte)'S');
        writer.Write((uint)bytes.Length);
        writer.Write(bytes);
    }

    private static void WriteDoubleArrayProperty(BinaryWriter writer, double[] values)
    {
        writer.Write((byte)'d');
        writer.Write((uint)values.Length);
        writer.Write((uint)0);
        writer.Write((uint)(values.Length * sizeof(double)));
        foreach (double value in values)
        {
            writer.Write(value);
        }
    }

    private static void WriteIntArrayProperty(BinaryWriter writer, int[] values)
    {
        writer.Write((byte)'i');
        writer.Write((uint)values.Length);
        writer.Write((uint)0);
        writer.Write((uint)(values.Length * sizeof(int)));
        foreach (int value in values)
        {
            writer.Write(value);
        }
    }

    private static void WriteSentinel(BinaryWriter writer) => writer.Write(new byte[13]);
}
