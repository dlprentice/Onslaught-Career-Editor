using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Security.Cryptography;
using System.Text;
using System.Text.Json;
using System.Text.Json.Serialization;

namespace OnslaughtCareerEditor.AppCore
{
    /// <summary>One selected catalog row, named by its stable catalog identity.</summary>
    public sealed record ModProjectSelectionEntry(string Kind, string CatalogId);

    /// <summary>How many selected rows belong to one asset kind.</summary>
    public sealed record ModProjectKindCount(string Kind, int Count);

    /// <summary>
    /// One planned entry: catalog identity plus the state of the player's own
    /// local export file. No content bytes ever travel inside this record.
    /// </summary>
    public sealed record ModProjectPlannedAsset(
        string CatalogId,
        string DisplayName,
        string Kind,
        string CanonicalRef,
        string? SourceArchive,
        string ExportFileName,
        bool ExportPresent,
        string? ExpectedExportSha256,
        string? ExportSha256,
        long? ExportLengthBytes)
    {
        /// <summary>True when the row has no verifiable local export or hash.</summary>
        public bool IsUnresolved => !ExportPresent || ExportSha256 is null;
    }

    /// <summary>The versioned, deterministic mod project plan document.</summary>
    public sealed record ModProjectPlan(
        string ManifestVersion,
        string CatalogFileName,
        int CatalogSchemaVersion,
        string CatalogPathContract,
        string CatalogSha256,
        int SelectedCount,
        IReadOnlyList<ModProjectPlannedAsset> Assets,
        IReadOnlyList<ModProjectKindCount> KindCounts,
        int UnresolvedMetadataCount,
        string ContentBoundary);

    /// <summary>Outcome of one project-manifest export attempt.</summary>
    public sealed record ModProjectPlanExportResult(
        bool Success,
        string Message,
        string? ManifestPath,
        string? TsvPath,
        int AssetCount)
    {
        public static ModProjectPlanExportResult Failed(string message) =>
            new(false, message, null, null, 0);
    }

    /// <summary>
    /// Plans a bounded, shareable mod project from selected rows of an already
    /// loaded generated catalog. The plan is metadata only - names, ids,
    /// references, and hashes of the player's own exported files. It never
    /// copies game assets or retail bytes, so sharing it cannot substitute for
    /// owning the game. Every export revalidates the sealed catalog provenance
    /// and fails closed on drift, ambiguity, or game-tree outputs.
    /// </summary>
    public static class ModProjectPlannerService
    {
        public const string ManifestVersion = "mod-project-plan.v1";
        public const int MaxSelectedAssets = 100;

        public const string ContentBoundary =
            "Metadata only. This mod project plan is a receipt of names, ids, references, and " +
            "hashes from your own generated catalog and exported files. It contains no game " +
            "assets; it is not an asset pack, not an installer, and not a compatibility guarantee.";

        public const string PlanTsvHeader =
            "catalog_id\tdisplay_name\tkind\tcanonical_ref\tsource_archive\texport_file_name\texport_present\texpected_export_sha256\texport_sha256\texport_length_bytes";

        public const string PlanJsonFileName = "mod-project-plan.json";
        public const string PlanTsvFileName = "mod-project-plan.tsv";

        private const string NeedsLoadedCatalog =
            "Load a generated catalog first, then select rows to plan a mod project.";

        private static readonly JsonSerializerOptions s_writeOptions = new()
        {
            WriteIndented = true,
            DefaultIgnoreCondition = JsonIgnoreCondition.WhenWritingNull,
            PropertyNamingPolicy = JsonNamingPolicy.CamelCase,
        };

        /// <summary>
        /// Builds the plan document for a bounded selection without writing
        /// anything, so callers can show exactly what an export would contain.
        /// Fails closed when the catalog is not loaded or a selection names a
        /// row the catalog cannot uniquely identify.
        /// </summary>
        public static ModProjectPlan BuildPlan(
            AssetCatalogSnapshot snapshot,
            IReadOnlyList<ModProjectSelectionEntry> selection)
        {
            ArgumentNullException.ThrowIfNull(snapshot);
            ArgumentNullException.ThrowIfNull(selection);
            if (string.IsNullOrWhiteSpace(snapshot.CatalogFilePath))
            {
                throw new InvalidOperationException(NeedsLoadedCatalog);
            }

            ValidateCatalogProvenance(snapshot);

            if (selection.Count == 0)
            {
                throw new InvalidOperationException(
                    "Select at least one catalog row before planning a mod project.");
            }

            if (selection.Count > MaxSelectedAssets)
            {
                throw new InvalidOperationException(
                    $"Select at most {MaxSelectedAssets} catalog rows for one mod project plan.");
            }

            var duplicates = selection
                .GroupBy(
                    entry => $"{NormalizeKind(entry.Kind)}\0{entry.CatalogId}",
                    StringComparer.OrdinalIgnoreCase)
                .FirstOrDefault(group => group.Count() > 1);
            if (duplicates is not null)
            {
                ModProjectSelectionEntry duplicate = duplicates.First();
                throw new InvalidOperationException(
                    $"The selection names \"{duplicate.CatalogId}\" more than once. Each planned row must be unique.");
            }

            var assets = new List<ModProjectPlannedAsset>(selection.Count);
            foreach (ModProjectSelectionEntry entry in selection)
            {
                string kind = NormalizeKind(entry.Kind);
                assets.Add(kind switch
                {
                    "texture" => PlanTexture(snapshot, entry.CatalogId),
                    "mesh" => PlanLooseMesh(snapshot, entry.CatalogId),
                    "embedded-mesh" => PlanEmbeddedMesh(snapshot, entry.CatalogId),
                    "goodie" => PlanGoodie(snapshot, entry.CatalogId),
                    _ => throw new InvalidOperationException(
                        $"\"{entry.Kind}\" is not a plannable catalog kind."),
                });
            }

            // Deterministic output regardless of how the player selected rows.
            assets.Sort(static (left, right) =>
            {
                int byKind = KindRank(left.Kind).CompareTo(KindRank(right.Kind));
                return byKind != 0 ? byKind : string.CompareOrdinal(left.CatalogId, right.CatalogId);
            });

            var kindCounts = assets
                .GroupBy(asset => asset.Kind, StringComparer.Ordinal)
                .OrderBy(group => KindRank(group.Key))
                .Select(group => new ModProjectKindCount(group.Key, group.Count()))
                .ToArray();

            return new ModProjectPlan(
                ManifestVersion,
                Path.GetFileName(snapshot.CatalogFilePath),
                AssetCatalogService.SupportedSchemaVersion,
                AssetCatalogService.SupportedPathContract,
                Convert.ToHexString(snapshot.TrustEvidence.CatalogSha256).ToLowerInvariant(),
                assets.Count,
                assets,
                kindCounts,
                assets.Count(asset => asset.IsUnresolved),
                ContentBoundary);
        }

        internal static void ValidateCatalogProvenance(AssetCatalogSnapshot snapshot)
        {
            AssetCatalogSelection? selection = AssetCatalogFileSafety.ResolveSelection(snapshot.CatalogFilePath);
            if (selection is null)
            {
                throw new InvalidOperationException(
                    "The loaded catalog file or its generated export folder is missing or changed.");
            }

            using AssetCatalogLoadSession session = AssetCatalogFileSafety.BeginLoad(selection);
            string expectedRoot = FileMutationSafety.NormalizeLocalPath(
                snapshot.TrustedExportRoot,
                "generated export folder");
            if (!string.Equals(
                    session.TrustedExportRoot,
                    expectedRoot,
                    FileMutationSafety.PathComparison))
            {
                throw new InvalidOperationException(AssetCatalogFileSafety.ExportFolderChanged);
            }

            session.ValidateTrust(snapshot.TrustEvidence);
        }

        /// <summary>
        /// Revalidates a previously previewed plan, then writes its metadata-only
        /// JSON receipt to the exact path chosen by the player. An optional TSV is
        /// written beside it with the same base name. No source asset is copied.
        /// </summary>
        public static ModProjectPlanExportResult Export(
            AssetCatalogSnapshot snapshot,
            ModProjectPlan plan,
            string outputPath,
            bool includeTsv)
        {
            ArgumentNullException.ThrowIfNull(snapshot);
            ArgumentNullException.ThrowIfNull(plan);

            try
            {
                string normalizedOutput = FileMutationSafety.NormalizeLocalPath(
                    outputPath,
                    "Mod project plan output");
                if (!string.Equals(Path.GetExtension(normalizedOutput), ".json", StringComparison.OrdinalIgnoreCase))
                {
                    return ModProjectPlanExportResult.Failed(
                        "Choose a .json path for the mod project plan receipt.");
                }

                string? outputDirectory = Path.GetDirectoryName(normalizedOutput);
                if (string.IsNullOrWhiteSpace(outputDirectory) || !Directory.Exists(outputDirectory))
                {
                    return ModProjectPlanExportResult.Failed(
                        "The chosen mod project plan folder could not be found. Nothing was written.");
                }

                string? tsvPath = includeTsv ? Path.ChangeExtension(normalizedOutput, ".tsv") : null;
                if (File.Exists(normalizedOutput) || (tsvPath is not null && File.Exists(tsvPath)))
                {
                    return ModProjectPlanExportResult.Failed(
                        "A mod project plan receipt already exists at the chosen JSON or TSV file. Choose a new file name; nothing was replaced.");
                }

                ModProjectPlan current = BuildPlan(
                    snapshot,
                    plan.Assets
                        .Select(asset => new ModProjectSelectionEntry(asset.Kind, asset.CatalogId))
                        .ToArray());
                byte[] previewBytes = SerializePlan(plan);
                byte[] currentBytes = SerializePlan(current);
                if (!previewBytes.AsSpan().SequenceEqual(currentBytes))
                {
                    return ModProjectPlanExportResult.Failed(
                        "The catalog selection or local export metadata changed after this plan was previewed. Review the plan again; nothing was written.");
                }

                byte[]? tsvBytes = includeTsv ? Encoding.UTF8.GetBytes(BuildTsv(current)) : null;

                using GuardedFileMutation jsonTransaction = FileMutationSafety.BeginGenerated(normalizedOutput);
                using GuardedFileMutation? tsvTransaction = tsvPath is not null
                    ? FileMutationSafety.BeginGenerated(tsvPath)
                    : null;
                jsonTransaction.Commit(currentBytes);
                tsvTransaction?.Commit(tsvBytes!);

                return new ModProjectPlanExportResult(
                    true,
                    includeTsv
                        ? $"Wrote the mod project plan receipt and optional TSV with {current.SelectedCount} selected rows. No game assets were copied."
                        : $"Wrote the mod project plan receipt with {current.SelectedCount} selected rows. No game assets were copied.",
                    normalizedOutput,
                    tsvPath,
                    current.SelectedCount);
            }
            catch (Exception exception) when (
                exception is ArgumentException or IOException or InvalidOperationException or NotSupportedException or UnauthorizedAccessException)
            {
                string message = FileMutationSafety.TryGetKnownRefusal(exception, out string? known) &&
                    !string.IsNullOrWhiteSpace(known)
                        ? known
                        : "The mod project plan receipt could not be written. Nothing was changed.";
                return ModProjectPlanExportResult.Failed(message);
            }
        }

        /// <summary>Builds deterministic, spreadsheet-shaped metadata for the same selected rows.</summary>
        public static string BuildTsv(ModProjectPlan plan)
        {
            ArgumentNullException.ThrowIfNull(plan);
            var builder = new StringBuilder();
            builder.AppendLine(PlanTsvHeader);
            foreach (ModProjectPlannedAsset asset in plan.Assets)
            {
                builder.Append(EscapeTsv(asset.CatalogId)).Append('\t');
                builder.Append(EscapeTsv(asset.DisplayName)).Append('\t');
                builder.Append(EscapeTsv(asset.Kind)).Append('\t');
                builder.Append(EscapeTsv(asset.CanonicalRef)).Append('\t');
                builder.Append(EscapeTsv(asset.SourceArchive ?? string.Empty)).Append('\t');
                builder.Append(EscapeTsv(asset.ExportFileName)).Append('\t');
                builder.Append(asset.ExportPresent ? "true" : "false").Append('\t');
                builder.Append(EscapeTsv(asset.ExpectedExportSha256 ?? string.Empty)).Append('\t');
                builder.Append(EscapeTsv(asset.ExportSha256 ?? string.Empty)).Append('\t');
                builder.Append(asset.ExportLengthBytes?.ToString() ?? string.Empty).AppendLine();
            }

            return builder.ToString();
        }

        private static byte[] SerializePlan(ModProjectPlan plan) =>
            JsonSerializer.SerializeToUtf8Bytes(plan, s_writeOptions);

        private static string EscapeTsv(string value) =>
            string.IsNullOrEmpty(value)
                ? string.Empty
                : value.Replace('\t', ' ').Replace('\r', ' ').Replace('\n', ' ');

        private static string NormalizeKind(string kind)
        {
            return kind switch
            {
                "texture" => "texture",
                "mesh" or "loose-mesh" => "mesh",
                "embedded-mesh" => "embedded-mesh",
                "goodie" => "goodie",
                _ => kind.Trim().ToLowerInvariant(),
            };
        }

        private static int KindRank(string kind)
        {
            return kind switch
            {
                "texture" => 0,
                "mesh" => 1,
                "embedded-mesh" => 2,
                _ => 3,
            };
        }

        private static ModProjectPlannedAsset PlanTexture(AssetCatalogSnapshot snapshot, string catalogId)
        {
            AssetTextureItem? texture = FindUnique(
                snapshot.Textures.Where(item => string.Equals(item.CatalogId, catalogId, StringComparison.OrdinalIgnoreCase)),
                catalogId);
            if (texture is null)
            {
                throw UnknownRow("texture", catalogId);
            }

            ExportInspection export = InspectExport(snapshot, texture.ExportPath);

            return new ModProjectPlannedAsset(
                texture.CatalogId,
                texture.DisplayName,
                "texture",
                texture.CanonicalRef,
                null,
                texture.ExportFileName,
                export.Exists,
                NormalizeExpectedHash(texture.ExpectedExportSha256, export, texture.CatalogId),
                export.Sha256,
                export.LengthBytes);
        }

        private static ModProjectPlannedAsset PlanLooseMesh(AssetCatalogSnapshot snapshot, string catalogId)
        {
            AssetLooseMeshItem? mesh = FindUnique(
                snapshot.LooseMeshes.Where(item => string.Equals(item.CatalogId, catalogId, StringComparison.OrdinalIgnoreCase)),
                catalogId);
            if (mesh is null)
            {
                throw UnknownRow("mesh", catalogId);
            }

            ExportInspection export = InspectExport(snapshot, mesh.ExportPath);

            return new ModProjectPlannedAsset(
                mesh.CatalogId,
                mesh.DisplayName,
                "mesh",
                mesh.CanonicalRef,
                null,
                mesh.ExportFileName,
                export.Exists,
                NormalizeExpectedHash(mesh.ExpectedExportSha256, export, mesh.CatalogId),
                export.Sha256,
                export.LengthBytes);
        }

        private static ModProjectPlannedAsset PlanEmbeddedMesh(AssetCatalogSnapshot snapshot, string catalogId)
        {
            AssetEmbeddedMeshItem? mesh = FindUnique(
                snapshot.EmbeddedMeshes.Where(item => string.Equals(item.CatalogId, catalogId, StringComparison.OrdinalIgnoreCase)),
                catalogId);
            if (mesh is null)
            {
                throw UnknownRow("embedded-mesh", catalogId);
            }

            ExportInspection export = InspectExport(snapshot, mesh.ExportPath);

            return new ModProjectPlannedAsset(
                mesh.CatalogId,
                mesh.DisplayName,
                "embedded-mesh",
                $"{mesh.SourceArchive}#{mesh.BodyName}",
                mesh.SourceArchive,
                mesh.ExportFileName,
                export.Exists,
                NormalizeExpectedHash(mesh.ExpectedExportSha256, export, mesh.CatalogId),
                export.Sha256,
                export.LengthBytes);
        }

        private static ModProjectPlannedAsset PlanGoodie(AssetCatalogSnapshot snapshot, string catalogId)
        {
            AssetGoodieItem? goodie = FindUnique(
                snapshot.Goodies.Where(item => string.Equals(item.CatalogId, catalogId, StringComparison.OrdinalIgnoreCase)),
                catalogId);
            if (goodie is null)
            {
                throw UnknownRow("goodie", catalogId);
            }

            string canonicalRef = !string.IsNullOrWhiteSpace(goodie.PrimaryMeshRef)
                ? goodie.PrimaryMeshRef
                : !string.IsNullOrWhiteSpace(goodie.PrimaryTextureRef)
                    ? goodie.PrimaryTextureRef
                    : !string.IsNullOrWhiteSpace(goodie.VideoCatalogId)
                        ? goodie.VideoCatalogId
                        : $"{goodie.SourceArchive}#{goodie.Index}";
            return new ModProjectPlannedAsset(
                goodie.CatalogId,
                goodie.DisplayName,
                "goodie",
                canonicalRef,
                string.IsNullOrWhiteSpace(goodie.SourceArchive) ? null : goodie.SourceArchive,
                goodie.ExportFileName,
                false,
                null,
                null,
                null);
        }

        private static string? NormalizeExpectedHash(
            string expectedSha256,
            ExportInspection export,
            string catalogId)
        {
            if (string.IsNullOrWhiteSpace(expectedSha256))
            {
                return null;
            }

            if (export.Exists &&
                !string.Equals(expectedSha256, export.Sha256, StringComparison.OrdinalIgnoreCase))
            {
                throw new InvalidOperationException(
                    $"The local export for \"{catalogId}\" no longer matches the SHA-256 recorded by the catalog.");
            }

            return expectedSha256.ToLowerInvariant();
        }

        private static T? FindUnique<T>(IEnumerable<T> matches, string catalogId) where T : class
        {
            List<T> found = matches.ToList();
            return found.Count switch
            {
                1 => found[0],
                0 => null,
                _ => throw new InvalidOperationException(
                    $"The catalog lists \"{catalogId}\" more than once; its identity is ambiguous, so it cannot be planned."),
            };
        }

        private static InvalidOperationException UnknownRow(string kind, string catalogId)
        {
            return new InvalidOperationException(
                $"The loaded catalog has no {kind} row with catalog id \"{catalogId}\".");
        }

        private static ExportInspection InspectExport(AssetCatalogSnapshot snapshot, string exportPath)
        {
            using AssetCatalogSourceLease lease = AssetCatalogSourceAccessService.Open(
                snapshot,
                exportPath,
                "Mod project catalog export");
            if (!lease.Exists)
            {
                return new ExportInspection(false, null, null);
            }

            long length = lease.Stream.Length;
            lease.Stream.Position = 0;
            string sha256 = Convert.ToHexString(SHA256.HashData(lease.Stream)).ToLowerInvariant();
            return new ExportInspection(true, sha256, length);
        }

        private sealed record ExportInspection(bool Exists, string? Sha256, long? LengthBytes);
    }
}
