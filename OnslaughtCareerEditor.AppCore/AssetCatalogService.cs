using System.Text.Json;

namespace Onslaught___Career_Editor
{
    public sealed class AssetCatalogService
    {
        private const string CatalogFileName = "catalog.json";
        private const string AssetCatalogDirectoryName = "asset_catalog";

        public AssetCatalogSnapshot Load(string? catalogPathOrDirectory)
        {
            string? catalogFilePath = ResolveCatalogFilePath(catalogPathOrDirectory);
            if (catalogFilePath == null)
            {
                return AssetCatalogSnapshot.Empty;
            }

            try
            {
                using JsonDocument document = JsonDocument.Parse(File.ReadAllText(catalogFilePath));
                JsonElement root = document.RootElement;

                IReadOnlyList<AssetTextureItem> textures = ReadArray(root, "textures")
                    .Select(row => BuildTextureItem(row, catalogFilePath))
                    .OrderBy(static item => item.DisplayName, StringComparer.OrdinalIgnoreCase)
                    .ToList();

                IReadOnlyList<AssetLooseMeshItem> looseMeshes = ReadArray(root, "loose_meshes")
                    .Select(row => BuildLooseMeshItem(row, catalogFilePath))
                    .OrderBy(static item => item.DisplayName, StringComparer.OrdinalIgnoreCase)
                    .ToList();

                IReadOnlyList<AssetEmbeddedMeshItem> embeddedMeshes = ReadArray(root, "embedded_meshes")
                    .Select(row => BuildEmbeddedMeshItem(row, catalogFilePath))
                    .OrderBy(static item => item.SourceArchive, StringComparer.OrdinalIgnoreCase)
                    .ThenBy(static item => item.DisplayName, StringComparer.OrdinalIgnoreCase)
                    .ToList();

                IReadOnlyList<AssetGoodieItem> goodies = ReadArray(root, "goodies")
                    .Select(BuildGoodieItem)
                    .OrderBy(static item => item.Index)
                    .ToList();

                return new AssetCatalogSnapshot(
                    catalogFilePath,
                    BuildSummary(root, textures.Count, looseMeshes.Count, embeddedMeshes.Count, goodies.Count),
                    textures,
                    looseMeshes,
                    embeddedMeshes,
                    goodies);
            }
            catch (JsonException)
            {
                return AssetCatalogSnapshot.Empty;
            }
            catch (IOException)
            {
                return AssetCatalogSnapshot.Empty;
            }
        }

        public static string? ResolveCatalogFilePath(string? catalogPathOrDirectory)
        {
            if (string.IsNullOrWhiteSpace(catalogPathOrDirectory))
            {
                return null;
            }

            string fullPath = Path.GetFullPath(catalogPathOrDirectory);
            if (File.Exists(fullPath))
            {
                return fullPath;
            }

            if (!Directory.Exists(fullPath))
            {
                return null;
            }

            string directCatalog = Path.Combine(fullPath, CatalogFileName);
            if (File.Exists(directCatalog))
            {
                return directCatalog;
            }

            string nestedCatalog = Path.Combine(fullPath, AssetCatalogDirectoryName, CatalogFileName);
            return File.Exists(nestedCatalog) ? nestedCatalog : null;
        }

        private static AssetCatalogSummary BuildSummary(
            JsonElement root,
            int textureCount,
            int looseMeshCount,
            int embeddedMeshCount,
            int goodieCount)
        {
            JsonElement summary = TryGetObject(root, "summary");
            return new AssetCatalogSummary(
                GetInt(summary, "texture_catalog_entries", textureCount),
                GetInt(summary, "loose_mesh_catalog_entries", looseMeshCount),
                GetInt(summary, "embedded_mesh_catalog_entries", embeddedMeshCount),
                GetInt(summary, "video_catalog_entries"),
                GetInt(summary, "language_catalog_entries"),
                GetInt(summary, "goodie_catalog_entries", goodieCount),
                GetInt(summary, "total_catalog_entries", textureCount + looseMeshCount + embeddedMeshCount + goodieCount));
        }

        private static AssetTextureItem BuildTextureItem(JsonElement row, string catalogFilePath)
        {
            string canonicalRef = GetString(row, "canonical_ref");
            string exportPath = ResolveFirstPath(catalogFilePath, ReadStringArray(row, "export_png_paths"));
            return new AssetTextureItem(
                GetString(row, "catalog_id"),
                canonicalRef,
                BuildTextureDisplayName(canonicalRef),
                FirstOrDefault(ReadStringArray(row, "source_roots"), "Textures"),
                exportPath,
                Path.GetFileName(exportPath),
                File.Exists(exportPath),
                GetInt(row, "source_aya_count"),
                GetInt(row, "export_png_count"),
                GetInt(row, "packed_text_ref_count") + GetInt(row, "gdie_ref_count"));
        }

        private static AssetLooseMeshItem BuildLooseMeshItem(JsonElement row, string catalogFilePath)
        {
            string canonicalRef = GetString(row, "canonical_ref");
            string exportPath = ResolveFirstPath(catalogFilePath, ReadStringArray(row, "export_fbx_paths"));
            return new AssetLooseMeshItem(
                GetString(row, "catalog_id"),
                canonicalRef,
                string.IsNullOrWhiteSpace(canonicalRef) ? "Loose mesh" : canonicalRef,
                exportPath,
                Path.GetFileName(exportPath),
                File.Exists(exportPath),
                GetInt(row, "source_aya_count"),
                GetInt(row, "export_fbx_count"),
                GetInt(row, "packed_reference_count") + GetInt(row, "gdie_ref_count"),
                FbxModelSummaryReader.Read(exportPath));
        }

        private static AssetEmbeddedMeshItem BuildEmbeddedMeshItem(JsonElement row, string catalogFilePath)
        {
            string bodyName = GetString(row, "body_name");
            string exportPath = ResolvePath(catalogFilePath, GetString(row, "export_fbx_path"));
            return new AssetEmbeddedMeshItem(
                GetString(row, "catalog_id"),
                GetString(row, "source_archive"),
                bodyName,
                string.IsNullOrWhiteSpace(bodyName) ? "Embedded mesh" : bodyName,
                exportPath,
                Path.GetFileName(exportPath),
                File.Exists(exportPath),
                FbxModelSummaryReader.Read(exportPath));
        }

        private static AssetGoodieItem BuildGoodieItem(JsonElement row)
        {
            int index = GetInt(row, "index");
            string contentKind = GetString(row, "content_kind");
            string displayName = GetString(row, "display_name");
            IReadOnlyList<string> textureRefs = ReadStringArray(row, "texture_refs");
            IReadOnlyList<string> meshRefs = ReadStringArray(row, "mesh_refs");
            string videoSequenceId = GetString(row, "video_sequence_id");
            GoodieUnlockRequirement unlockRequirement = GoodieUnlockRequirementService.Describe(index);
            GoodieWallVisibility wallVisibility = GoodieWallVisibilityService.Describe(index);
            GoodieWallSlot? wallSlot = GoodieWallGridMappingService.Locate(index);
            return new AssetGoodieItem(
                GetString(row, "catalog_id"),
                index,
                string.IsNullOrWhiteSpace(displayName) ? $"Goodie {index:000}" : displayName,
                string.IsNullOrWhiteSpace(contentKind) ? "Unknown" : contentKind,
                GetString(row, "source_title"),
                GetString(row, "source_archive"),
                GetString(row, "gdie_family"),
                GetString(row, "primary_texture_ref"),
                GetString(row, "primary_mesh_ref"),
                videoSequenceId,
                GetString(row, "video_catalog_id"),
                GetString(row, "video_relative_path"),
                textureRefs,
                meshRefs,
                unlockRequirement.Summary,
                unlockRequirement.EvidenceLabel,
                wallVisibility.Summary,
                wallVisibility.EvidenceLabel,
                wallVisibility.IsSourceGridVisible,
                wallSlot?.GroupLabel ?? "Not on known wall",
                wallSlot?.PositionLabel ?? "No wall position");
        }

        private static IReadOnlyList<JsonElement> ReadArray(JsonElement root, string propertyName)
        {
            if (!root.TryGetProperty(propertyName, out JsonElement element) ||
                element.ValueKind != JsonValueKind.Array)
            {
                return Array.Empty<JsonElement>();
            }

            return element.EnumerateArray().ToList();
        }

        private static JsonElement TryGetObject(JsonElement root, string propertyName)
        {
            return root.TryGetProperty(propertyName, out JsonElement element) &&
                   element.ValueKind == JsonValueKind.Object
                ? element
                : default;
        }

        private static string GetString(JsonElement element, string propertyName)
        {
            if (element.ValueKind != JsonValueKind.Object ||
                !element.TryGetProperty(propertyName, out JsonElement value))
            {
                return string.Empty;
            }

            return value.ValueKind == JsonValueKind.String
                ? value.GetString() ?? string.Empty
                : value.ToString();
        }

        private static int GetInt(JsonElement element, string propertyName, int fallback = 0)
        {
            if (element.ValueKind != JsonValueKind.Object ||
                !element.TryGetProperty(propertyName, out JsonElement value))
            {
                return fallback;
            }

            return value.ValueKind switch
            {
                JsonValueKind.Number when value.TryGetInt32(out int number) => number,
                JsonValueKind.True => 1,
                JsonValueKind.False => 0,
                _ => fallback
            };
        }

        private static IReadOnlyList<string> ReadStringArray(JsonElement element, string propertyName)
        {
            if (element.ValueKind != JsonValueKind.Object ||
                !element.TryGetProperty(propertyName, out JsonElement value) ||
                value.ValueKind != JsonValueKind.Array)
            {
                return Array.Empty<string>();
            }

            return value
                .EnumerateArray()
                .Where(static item => item.ValueKind == JsonValueKind.String)
                .Select(static item => item.GetString() ?? string.Empty)
                .Where(static item => !string.IsNullOrWhiteSpace(item))
                .ToList();
        }

        private static string ResolveFirstPath(string catalogFilePath, IReadOnlyList<string> paths)
        {
            return paths.Count == 0 ? string.Empty : ResolvePath(catalogFilePath, paths[0]);
        }

        private static string ResolvePath(string catalogFilePath, string path)
        {
            if (string.IsNullOrWhiteSpace(path))
            {
                return string.Empty;
            }

            if (Path.IsPathRooted(path))
            {
                return Path.GetFullPath(path);
            }

            string normalized = path.Replace('/', Path.DirectorySeparatorChar);
            string catalogDirectory = Path.GetDirectoryName(catalogFilePath) ?? Environment.CurrentDirectory;
            foreach (string candidateRoot in EnumerateCandidateRoots(catalogDirectory))
            {
                string candidate = Path.GetFullPath(Path.Combine(candidateRoot, normalized));
                if (File.Exists(candidate))
                {
                    return candidate;
                }
            }

            return Path.GetFullPath(Path.Combine(catalogDirectory, normalized));
        }

        private static IEnumerable<string> EnumerateCandidateRoots(string catalogDirectory)
        {
            yield return catalogDirectory;

            DirectoryInfo? directory = new(catalogDirectory);
            while (directory.Parent != null)
            {
                directory = directory.Parent;
                yield return directory.FullName;
            }

            yield return Environment.CurrentDirectory;
        }

        private static string BuildTextureDisplayName(string canonicalRef)
        {
            string stem = Path.GetFileNameWithoutExtension(canonicalRef.Replace('\\', Path.DirectorySeparatorChar).Replace('/', Path.DirectorySeparatorChar));
            if (string.IsNullOrWhiteSpace(stem))
            {
                return "Texture";
            }

            return string.Join(
                " ",
                stem.Split(['_', '-', '.'], StringSplitOptions.RemoveEmptyEntries | StringSplitOptions.TrimEntries)
                    .Select(static part => part.Length == 0 ? part : char.ToUpperInvariant(part[0]) + part[1..]));
        }

        private static string FirstOrDefault(IReadOnlyList<string> values, string fallback)
        {
            return values.Count == 0 || string.IsNullOrWhiteSpace(values[0]) ? fallback : values[0];
        }
    }

    public sealed record AssetCatalogSnapshot(
        string CatalogFilePath,
        AssetCatalogSummary Summary,
        IReadOnlyList<AssetTextureItem> Textures,
        IReadOnlyList<AssetLooseMeshItem> LooseMeshes,
        IReadOnlyList<AssetEmbeddedMeshItem> EmbeddedMeshes,
        IReadOnlyList<AssetGoodieItem> Goodies)
    {
        public static AssetCatalogSnapshot Empty { get; } = new(
            string.Empty,
            AssetCatalogSummary.Empty,
            Array.Empty<AssetTextureItem>(),
            Array.Empty<AssetLooseMeshItem>(),
            Array.Empty<AssetEmbeddedMeshItem>(),
            Array.Empty<AssetGoodieItem>());
    }

    public sealed record AssetCatalogSummary(
        int TextureCount,
        int LooseMeshCount,
        int EmbeddedMeshCount,
        int VideoCount,
        int LanguageRowCount,
        int GoodieCount,
        int TotalCatalogEntries)
    {
        public static AssetCatalogSummary Empty { get; } = new(0, 0, 0, 0, 0, 0, 0);
    }

    public sealed record AssetTextureItem(
        string CatalogId,
        string CanonicalRef,
        string DisplayName,
        string SourceGroup,
        string ExportPath,
        string ExportFileName,
        bool ExportExists,
        int SourceFileCount,
        int ExportFileCount,
        int PackedReferenceCount);

    public sealed record AssetLooseMeshItem(
        string CatalogId,
        string CanonicalRef,
        string DisplayName,
        string ExportPath,
        string ExportFileName,
        bool ExportExists,
        int SourceFileCount,
        int ExportFileCount,
        int PackedReferenceCount,
        AssetModelSummary ModelSummary);

    public sealed record AssetEmbeddedMeshItem(
        string CatalogId,
        string SourceArchive,
        string BodyName,
        string DisplayName,
        string ExportPath,
        string ExportFileName,
        bool ExportExists,
        AssetModelSummary ModelSummary);

    public sealed record AssetGoodieItem(
        string CatalogId,
        int Index,
        string DisplayName,
        string ContentKind,
        string SourceTitle,
        string SourceArchive,
        string GdieFamily,
        string PrimaryTextureRef,
        string PrimaryMeshRef,
        string VideoSequenceId,
        string VideoCatalogId,
        string VideoRelativePath,
        IReadOnlyList<string> TextureRefs,
        IReadOnlyList<string> MeshRefs,
        string UnlockRequirement,
        string UnlockEvidenceLabel,
        string WallVisibilitySummary,
        string WallVisibilityEvidenceLabel,
        bool IsSourceGridVisible,
        string WallGroupLabel,
        string WallPositionLabel)
    {
        public string ExportFileName
        {
            get
            {
                if (!string.IsNullOrWhiteSpace(PrimaryMeshRef))
                {
                    return PrimaryMeshRef;
                }

                if (!string.IsNullOrWhiteSpace(PrimaryTextureRef))
                {
                    return PrimaryTextureRef;
                }

                return !string.IsNullOrWhiteSpace(VideoRelativePath) ? VideoRelativePath : SourceArchive;
            }
        }

        public bool HasTexture => !string.IsNullOrWhiteSpace(PrimaryTextureRef);

        public bool HasModel => !string.IsNullOrWhiteSpace(PrimaryMeshRef);

        public bool HasVideo => !string.IsNullOrWhiteSpace(VideoCatalogId);
    }
}
