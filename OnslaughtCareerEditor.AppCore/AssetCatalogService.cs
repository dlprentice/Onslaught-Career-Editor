using System.Text.Json;

namespace Onslaught___Career_Editor
{
    public sealed class AssetCatalogService
    {
        public const int SupportedSchemaVersion = 2;
        public const string SupportedPathContract = "bundle-root-relative";
        private const int MaxCatalogRowsPerSection = 100_000;

        public AssetCatalogSnapshot Load(string? catalogPathOrDirectory)
        {
            AssetCatalogSelection? selection = AssetCatalogFileSafety.ResolveSelection(catalogPathOrDirectory);
            if (selection == null)
            {
                return AssetCatalogSnapshot.Empty;
            }

            try
            {
                using AssetCatalogLoadSession session = AssetCatalogFileSafety.BeginLoad(selection);
                using JsonDocument document = JsonDocument.Parse(session.CatalogStream);
                JsonElement root = document.RootElement;
                if (!HasSupportedCatalogContract(root))
                    return AssetCatalogSnapshot.Empty;

                IReadOnlyList<AssetTextureItem> textures = ReadArray(root, "textures")
                    .Select(row => BuildTextureItem(row, session))
                    .OrderBy(static item => item.DisplayName, StringComparer.OrdinalIgnoreCase)
                    .ToList();

                IReadOnlyList<AssetLooseMeshItem> looseMeshes = ReadArray(root, "loose_meshes")
                    .Select(row => BuildLooseMeshItem(row, session))
                    .OrderBy(static item => item.DisplayName, StringComparer.OrdinalIgnoreCase)
                    .ToList();

                IReadOnlyList<AssetEmbeddedMeshItem> embeddedMeshes = ReadArray(root, "embedded_meshes")
                    .Select(row => BuildEmbeddedMeshItem(row, session))
                    .OrderBy(static item => item.SourceArchive, StringComparer.OrdinalIgnoreCase)
                    .ThenBy(static item => item.DisplayName, StringComparer.OrdinalIgnoreCase)
                    .ToList();

                IReadOnlyList<AssetGoodieItem> goodies = ReadArray(root, "goodies")
                    .Select(BuildGoodieItem)
                    .OrderBy(static item => item.Index)
                    .ToList();
                ValidateUniqueCatalogRows(textures, looseMeshes, embeddedMeshes, goodies);

                IReadOnlyDictionary<string, IReadOnlyList<AssetModelSidecarTexture>> sealedSidecars =
                    AssetModelTextureLinkService.CaptureSnapshotSidecars(
                        session,
                        looseMeshes.Select(static item => item.ExportPath)
                            .Concat(embeddedMeshes.Select(static item => item.ExportPath)));

                AssetCatalogSnapshot snapshot = new(
                    session.CatalogFilePath,
                    BuildSummary(root, textures.Count, looseMeshes.Count, embeddedMeshes.Count, goodies.Count),
                    textures,
                    looseMeshes,
                    embeddedMeshes,
                    goodies,
                    session.TrustedExportRoot);
                return snapshot with
                {
                    TrustEvidence = session.CaptureTrustEvidence(),
                    SealedSidecarTexturesByModelPath = sealedSidecars,
                };
            }
            catch (JsonException)
            {
                return AssetCatalogSnapshot.Empty;
            }
            catch (IOException)
            {
                return AssetCatalogSnapshot.Empty;
            }
            catch (Exception ex) when (ex is ArgumentException or InvalidOperationException or NotSupportedException or UnauthorizedAccessException)
            {
                return AssetCatalogSnapshot.Empty;
            }
        }

        public static string? ResolveCatalogFilePath(string? catalogPathOrDirectory)
        {
            AssetCatalogSelection? selection = AssetCatalogFileSafety.ResolveValidatedSelection(catalogPathOrDirectory);
            if (selection is null)
                return null;

            try
            {
                using AssetCatalogLoadSession session = AssetCatalogFileSafety.BeginLoad(selection);
                using JsonDocument document = JsonDocument.Parse(session.CatalogStream);
                return HasSupportedCatalogContract(document.RootElement)
                    ? session.CatalogFilePath
                    : null;
            }
            catch (Exception ex) when (ex is ArgumentException or IOException or InvalidOperationException or JsonException or NotSupportedException or UnauthorizedAccessException)
            {
                return null;
            }
        }

        public static IReadOnlyList<string> FindCatalogCandidates(params string?[] catalogPathOrDirectoryCandidates)
        {
            List<string> candidates = new();
            HashSet<string> seen = new(StringComparer.OrdinalIgnoreCase);
            foreach (string? candidate in catalogPathOrDirectoryCandidates)
            {
                string? catalogFilePath = ResolveCatalogFilePath(candidate);
                if (string.IsNullOrWhiteSpace(catalogFilePath))
                {
                    continue;
                }

                string normalized = Path.GetFullPath(catalogFilePath);
                if (seen.Add(normalized))
                {
                    candidates.Add(normalized);
                }
            }

            return candidates;
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

        private static void ValidateUniqueCatalogRows(
            IReadOnlyList<AssetTextureItem> textures,
            IReadOnlyList<AssetLooseMeshItem> looseMeshes,
            IReadOnlyList<AssetEmbeddedMeshItem> embeddedMeshes,
            IReadOnlyList<AssetGoodieItem> goodies)
        {
            IReadOnlyList<string> catalogIds = textures.Select(static row => row.CatalogId)
                .Concat(looseMeshes.Select(static row => row.CatalogId))
                .Concat(embeddedMeshes.Select(static row => row.CatalogId))
                .Concat(goodies.Select(static row => row.CatalogId))
                .ToList();
            if (catalogIds.Any(string.IsNullOrWhiteSpace) ||
                catalogIds.Distinct(StringComparer.OrdinalIgnoreCase).Count() != catalogIds.Count)
            {
                throw new InvalidOperationException("Asset catalog IDs must be non-empty and unique.");
            }

            IReadOnlyList<string> exportPaths = textures.Select(static row => row.ExportPath)
                .Concat(looseMeshes.Select(static row => row.ExportPath))
                .Concat(embeddedMeshes.Select(static row => row.ExportPath))
                .Where(static path => !string.IsNullOrWhiteSpace(path))
                .ToList();
            if (exportPaths.Distinct(FileMutationSafety.PathComparer).Count() != exportPaths.Count)
                throw new InvalidOperationException("Asset catalog primary export paths must be unique.");
            if (goodies.Select(static row => row.Index).Distinct().Count() != goodies.Count)
                throw new InvalidOperationException("Asset catalog Goodie indexes must be unique.");
        }

        private static bool HasSupportedPathContract(JsonElement root)
        {
            return root.ValueKind == JsonValueKind.Object &&
                root.TryGetProperty("schema_version", out JsonElement schemaVersion) &&
                schemaVersion.ValueKind == JsonValueKind.Number &&
                schemaVersion.TryGetInt32(out int parsedSchemaVersion) &&
                parsedSchemaVersion == SupportedSchemaVersion &&
                root.TryGetProperty("path_contract", out JsonElement pathContract) &&
                pathContract.ValueKind == JsonValueKind.String &&
                string.Equals(
                    pathContract.GetString(),
                    SupportedPathContract,
                    StringComparison.Ordinal);
        }

        private static bool HasSupportedCatalogContract(JsonElement root)
        {
            if (!HasSupportedPathContract(root))
                return false;

            foreach (string propertyName in new[] { "textures", "loose_meshes", "embedded_meshes", "goodies" })
            {
                if (!root.TryGetProperty(propertyName, out JsonElement section) ||
                    section.ValueKind != JsonValueKind.Array ||
                    section.GetArrayLength() > MaxCatalogRowsPerSection ||
                    section.EnumerateArray().Any(static row => row.ValueKind != JsonValueKind.Object))
                {
                    return false;
                }
            }

            return true;
        }

        private static AssetTextureItem BuildTextureItem(JsonElement row, AssetCatalogLoadSession session)
        {
            string canonicalRef = GetString(row, "canonical_ref");
            using AssetCatalogSourceRead export = ResolveFirstPath(session, ReadStringArray(row, "export_png_paths"), "Catalog texture export");
            return new AssetTextureItem(
                GetString(row, "catalog_id"),
                canonicalRef,
                BuildTextureDisplayName(canonicalRef),
                FirstOrDefault(ReadStringArray(row, "source_roots"), "Textures"),
                export.Path,
                Path.GetFileName(export.Path),
                export.Exists,
                GetInt(row, "source_aya_count"),
                GetInt(row, "export_png_count"),
                GetInt(row, "packed_text_ref_count") + GetInt(row, "gdie_ref_count"));
        }

        private static AssetLooseMeshItem BuildLooseMeshItem(JsonElement row, AssetCatalogLoadSession session)
        {
            string canonicalRef = GetString(row, "canonical_ref");
            using AssetCatalogSourceRead export = ResolveFirstPath(session, ReadStringArray(row, "export_fbx_paths"), "Catalog loose-mesh export");
            return new AssetLooseMeshItem(
                GetString(row, "catalog_id"),
                canonicalRef,
                string.IsNullOrWhiteSpace(canonicalRef) ? "Loose mesh" : canonicalRef,
                export.Path,
                Path.GetFileName(export.Path),
                export.Exists,
                GetInt(row, "source_aya_count"),
                GetInt(row, "export_fbx_count"),
                GetInt(row, "packed_reference_count") + GetInt(row, "gdie_ref_count"),
                export.Exists
                    ? FbxModelSummaryReader.Read(export.Stream)
                    : AssetModelSummary.Unavailable(0, "FBX export is not available at the recorded local path."));
        }

        private static AssetEmbeddedMeshItem BuildEmbeddedMeshItem(JsonElement row, AssetCatalogLoadSession session)
        {
            string bodyName = GetString(row, "body_name");
            using AssetCatalogSourceRead export = ResolvePath(session, GetString(row, "export_fbx_path"), "Catalog embedded-mesh export");
            return new AssetEmbeddedMeshItem(
                GetString(row, "catalog_id"),
                GetString(row, "source_archive"),
                bodyName,
                string.IsNullOrWhiteSpace(bodyName) ? "Embedded mesh" : bodyName,
                export.Path,
                Path.GetFileName(export.Path),
                export.Exists,
                export.Exists
                    ? FbxModelSummaryReader.Read(export.Stream)
                    : AssetModelSummary.Unavailable(0, "FBX export is not available at the recorded local path."));
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
                : string.Empty;
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
                !element.TryGetProperty(propertyName, out JsonElement value))
            {
                return Array.Empty<string>();
            }

            if (value.ValueKind != JsonValueKind.Array ||
                value.EnumerateArray().Any(static item => item.ValueKind != JsonValueKind.String))
            {
                throw new InvalidOperationException($"Asset catalog property '{propertyName}' must be an array of strings.");
            }

            return value
                .EnumerateArray()
                .Where(static item => item.ValueKind == JsonValueKind.String)
                .Select(static item => item.GetString() ?? string.Empty)
                .Where(static item => !string.IsNullOrWhiteSpace(item))
                .ToList();
        }

        private static AssetCatalogSourceRead ResolveFirstPath(
            AssetCatalogLoadSession session,
            IReadOnlyList<string> paths,
            string label)
        {
            if (paths.Count == 0)
                return AssetCatalogSourceRead.Missing(string.Empty);

            AssetCatalogSourceRead primary = ResolvePath(session, paths[0], label);
            try
            {
                for (int index = 1; index < paths.Count; index++)
                {
                    using AssetCatalogSourceRead ignored = ResolvePath(
                        session,
                        paths[index],
                        $"{label} alternative {index + 1}");
                }

                return primary;
            }
            catch
            {
                primary.Dispose();
                throw;
            }
        }

        private static AssetCatalogSourceRead ResolvePath(
            AssetCatalogLoadSession session,
            string path,
            string label)
        {
            if (string.IsNullOrWhiteSpace(path))
            {
                return AssetCatalogSourceRead.Missing(string.Empty);
            }

            return session.OpenSource(path, label, requireRelative: true);
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
        IReadOnlyList<AssetGoodieItem> Goodies,
        string TrustedExportRoot = "")
    {
        internal AssetCatalogTrustEvidence TrustEvidence { get; init; } =
            AssetCatalogTrustEvidence.Empty;

        internal IReadOnlyDictionary<string, IReadOnlyList<AssetModelSidecarTexture>>
            SealedSidecarTexturesByModelPath { get; init; } =
                new Dictionary<string, IReadOnlyList<AssetModelSidecarTexture>>(
                    FileMutationSafety.PathComparer);

        public static AssetCatalogSnapshot Empty { get; } = new(
            string.Empty,
            AssetCatalogSummary.Empty,
            Array.Empty<AssetTextureItem>(),
            Array.Empty<AssetLooseMeshItem>(),
            Array.Empty<AssetEmbeddedMeshItem>(),
            Array.Empty<AssetGoodieItem>(),
            string.Empty);
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
