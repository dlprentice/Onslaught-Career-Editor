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
    /// <summary>The mutually exclusive outcome assigned to one manifest row during review.</summary>
    public enum ModProjectRevalidationStatus
    {
        Unchanged,
        CatalogDrifted,
        Missing,
        AmbiguousOrDuplicate,
        LocalExportMissing,
        LocalHashMismatch,
    }

    /// <summary>Original planner-manifest identity and the catalog provenance it recorded.</summary>
    public sealed record ModProjectManifestProvenance(
        string ManifestFileName,
        string ManifestSha256,
        string ManifestVersion,
        string CatalogFileName,
        int CatalogSchemaVersion,
        string CatalogPathContract,
        string CatalogSha256);

    /// <summary>Current generated-catalog provenance used for the comparison.</summary>
    public sealed record ModProjectCatalogProvenance(
        string CatalogFileName,
        int CatalogSchemaVersion,
        string CatalogPathContract,
        string CatalogSha256);

    /// <summary>One bounded, metadata-only row in a manifest drift review.</summary>
    public sealed record ModProjectRevalidationEntry(
        string CatalogId,
        string DisplayName,
        string Kind,
        ModProjectRevalidationStatus Status,
        string Detail,
        bool CatalogDrifted,
        bool Missing,
        bool AmbiguousOrDuplicate,
        bool LocalExportMissing,
        bool LocalHashMismatch,
        string? ManifestExpectedExportSha256,
        string? CurrentExpectedExportSha256,
        bool ManifestExportPresent,
        bool CurrentExportPresent,
        string? ManifestExportSha256,
        string? CurrentExportSha256);

    /// <summary>
    /// A deterministic preview of how one versioned planner manifest compares with
    /// one currently loaded generated catalog. It contains metadata only.
    /// </summary>
    public sealed record ModProjectRevalidationReview(
        string ReceiptVersion,
        ModProjectManifestProvenance OriginalManifest,
        ModProjectCatalogProvenance CurrentCatalog,
        bool CatalogProvenanceChanged,
        int ReviewedCount,
        int UnchangedCount,
        int CatalogDriftedCount,
        int MissingCount,
        int AmbiguousOrDuplicateCount,
        int LocalExportMissingCount,
        int LocalHashMismatchCount,
        IReadOnlyList<ModProjectRevalidationEntry> Entries,
        string ContentBoundary);

    /// <summary>Outcome of one metadata-only revalidation receipt export attempt.</summary>
    public sealed record ModProjectRevalidationExportResult(
        bool Success,
        string Message,
        string? ReceiptPath,
        string? TsvPath,
        int ReviewedCount)
    {
        public static ModProjectRevalidationExportResult Failed(string message) =>
            new(false, message, null, null, 0);
    }

    internal sealed record ModProjectRevalidationExportTestHooks(
        Action<string>? BeforeJsonPublish = null,
        Action<string>? BeforeTsvPublish = null);

    /// <summary>
    /// Opens an existing planner JSON manifest as read-only metadata and compares
    /// its normalized row identities, expected hashes, and local-export state with
    /// a currently loaded generated catalog. No catalog or asset bytes are copied.
    /// </summary>
    public static class ModProjectManifestRevalidationService
    {
        public const string ReceiptVersion = "mod-project-revalidation-receipt.v1";
        public const int MaxManifestBytes = 4 * 1024 * 1024;
        public const string ReceiptTsvHeader =
            "catalog_id\tdisplay_name\tkind\tstatus\tdetail\tcatalog_drifted\tmissing\tambiguous_or_duplicate\tlocal_export_missing\tlocal_hash_mismatch\tmanifest_expected_export_sha256\tcurrent_expected_export_sha256\tmanifest_export_present\tcurrent_export_present\tmanifest_export_sha256\tcurrent_export_sha256";
        public const string ContentBoundary =
            "Metadata-only manifest revalidation review. This receipt records catalog identities, " +
            "provenance, and hashes; it contains no game assets and is not an asset pack, installer, " +
            "repair tool, or compatibility guarantee.";

        private static readonly JsonSerializerOptions s_readOptions = new()
        {
            PropertyNamingPolicy = JsonNamingPolicy.CamelCase,
            PropertyNameCaseInsensitive = false,
        };

        private static readonly JsonSerializerOptions s_writeOptions = new()
        {
            WriteIndented = true,
            DefaultIgnoreCondition = JsonIgnoreCondition.WhenWritingNull,
            PropertyNamingPolicy = JsonNamingPolicy.CamelCase,
            Converters = { new JsonStringEnumConverter(JsonNamingPolicy.KebabCaseLower) },
        };

        public static ModProjectRevalidationReview Review(
            AssetCatalogSnapshot snapshot,
            string manifestPath)
        {
            ArgumentNullException.ThrowIfNull(snapshot);
            ModProjectPlannerService.ValidateCatalogProvenance(snapshot);

            LoadedManifest loaded = LoadManifest(manifestPath);
            ModProjectPlan manifest = loaded.Plan;
            string currentCatalogSha256 = Convert.ToHexString(
                snapshot.TrustEvidence.CatalogSha256).ToLowerInvariant();
            var currentCatalog = new ModProjectCatalogProvenance(
                Path.GetFileName(snapshot.CatalogFilePath),
                AssetCatalogService.SupportedSchemaVersion,
                AssetCatalogService.SupportedPathContract,
                currentCatalogSha256);
            var originalManifest = new ModProjectManifestProvenance(
                Path.GetFileName(loaded.Path),
                loaded.Sha256,
                manifest.ManifestVersion,
                manifest.CatalogFileName,
                manifest.CatalogSchemaVersion,
                manifest.CatalogPathContract,
                manifest.CatalogSha256);

            HashSet<string> duplicateManifestIdentities = manifest.Assets
                .GroupBy(
                    static asset => IdentityKey(asset.Kind, asset.CatalogId),
                    StringComparer.OrdinalIgnoreCase)
                .Where(static group => group.Count() > 1)
                .Select(static group => group.Key)
                .ToHashSet(StringComparer.OrdinalIgnoreCase);

            ModProjectRevalidationEntry[] entries = manifest.Assets
                .Select(asset => ReviewEntry(snapshot, asset, duplicateManifestIdentities))
                .OrderBy(static entry => KindRank(entry.Kind))
                .ThenBy(static entry => entry.CatalogId, StringComparer.Ordinal)
                .ToArray();

            bool provenanceChanged =
                !string.Equals(
                    originalManifest.CatalogFileName,
                    currentCatalog.CatalogFileName,
                    StringComparison.OrdinalIgnoreCase) ||
                originalManifest.CatalogSchemaVersion != currentCatalog.CatalogSchemaVersion ||
                !string.Equals(
                    originalManifest.CatalogPathContract,
                    currentCatalog.CatalogPathContract,
                    StringComparison.Ordinal) ||
                !string.Equals(
                    originalManifest.CatalogSha256,
                    currentCatalog.CatalogSha256,
                    StringComparison.OrdinalIgnoreCase);

            return new ModProjectRevalidationReview(
                ReceiptVersion,
                originalManifest,
                currentCatalog,
                provenanceChanged,
                entries.Length,
                entries.Count(static entry =>
                    !entry.CatalogDrifted &&
                    !entry.Missing &&
                    !entry.AmbiguousOrDuplicate &&
                    !entry.LocalExportMissing &&
                    !entry.LocalHashMismatch),
                entries.Count(static entry => entry.CatalogDrifted),
                entries.Count(static entry => entry.Missing),
                entries.Count(static entry => entry.AmbiguousOrDuplicate),
                entries.Count(static entry => entry.LocalExportMissing),
                entries.Count(static entry => entry.LocalHashMismatch),
                entries,
                ContentBoundary);
        }

        /// <summary>
        /// Writes a metadata-only review receipt to the exact player-chosen JSON
        /// path and, when requested, a deterministic TSV beside it.
        /// </summary>
        public static ModProjectRevalidationExportResult Export(
            AssetCatalogSnapshot snapshot,
            string manifestPath,
            ModProjectRevalidationReview review,
            string outputPath,
            bool includeTsv)
        {
            return Export(snapshot, manifestPath, review, outputPath, includeTsv, hooks: null);
        }

        internal static ModProjectRevalidationExportResult Export(
            AssetCatalogSnapshot snapshot,
            string manifestPath,
            ModProjectRevalidationReview review,
            string outputPath,
            bool includeTsv,
            ModProjectRevalidationExportTestHooks? hooks)
        {
            ArgumentNullException.ThrowIfNull(snapshot);
            ArgumentNullException.ThrowIfNull(review);

            try
            {
                string normalizedManifest = FileMutationSafety.NormalizeLocalPath(
                    manifestPath,
                    "Mod project plan manifest");
                string normalizedOutput = FileMutationSafety.NormalizeLocalPath(
                    outputPath,
                    "Manifest revalidation receipt output");
                if (!string.Equals(Path.GetExtension(normalizedOutput), ".json", StringComparison.OrdinalIgnoreCase))
                {
                    return ModProjectRevalidationExportResult.Failed(
                        "Choose a .json path for the manifest revalidation receipt.");
                }

                if (FileMutationSafety.AreLexicallySamePath(normalizedManifest, normalizedOutput))
                {
                    return ModProjectRevalidationExportResult.Failed(
                        "The revalidation receipt cannot replace the original planner manifest.");
                }

                string? outputDirectory = Path.GetDirectoryName(normalizedOutput);
                if (string.IsNullOrWhiteSpace(outputDirectory) || !Directory.Exists(outputDirectory))
                {
                    return ModProjectRevalidationExportResult.Failed(
                        "The chosen manifest revalidation receipt folder could not be found. Nothing was written.");
                }

                string? tsvPath = includeTsv ? Path.ChangeExtension(normalizedOutput, ".tsv") : null;
                if (File.Exists(normalizedOutput) || (tsvPath is not null && File.Exists(tsvPath)))
                {
                    return ModProjectRevalidationExportResult.Failed(
                        "A manifest revalidation receipt already exists at the chosen JSON or TSV file. Choose a new file name; nothing was replaced.");
                }

                using GuardedFileMutation jsonTransaction =
                    FileMutationSafety.BeginGeneratedVacant(normalizedOutput, normalizedManifest);
                using GuardedFileMutation? tsvTransaction = tsvPath is not null
                    ? FileMutationSafety.BeginGeneratedVacant(tsvPath, normalizedManifest)
                    : null;

                ModProjectRevalidationReview beforeHold = ReviewForExport(
                    snapshot,
                    normalizedManifest);
                if (!ReviewsMatch(review, beforeHold))
                {
                    return ChangedAfterReview();
                }

                if (beforeHold.AmbiguousOrDuplicateCount > 0)
                {
                    return ModProjectRevalidationExportResult.Failed(
                        "The manifest revalidation review contains ambiguous or duplicate identities. Resolve them before exporting a receipt; nothing was written.");
                }

                using HeldRevalidationInputs heldInputs = HoldCurrentInputs(snapshot, beforeHold);
                ModProjectRevalidationReview current = ReviewForExport(
                    snapshot,
                    normalizedManifest);
                if (!ReviewsMatch(review, current))
                {
                    return ChangedAfterReview();
                }

                byte[] jsonBytes = JsonSerializer.SerializeToUtf8Bytes(current, s_writeOptions);
                byte[]? tsvBytes = includeTsv
                    ? Encoding.UTF8.GetBytes(BuildTsv(current))
                    : null;
                jsonTransaction.Commit(
                    jsonBytes,
                    beforePublish: path =>
                    {
                        hooks?.BeforeJsonPublish?.Invoke(path);
                        EnsureReviewUnchanged(snapshot, normalizedManifest, current);
                    });

                bool tsvWritten = false;
                if (tsvTransaction is not null)
                {
                    try
                    {
                        tsvTransaction.Commit(
                            tsvBytes!,
                            beforePublish: path =>
                            {
                                hooks?.BeforeTsvPublish?.Invoke(path);
                                EnsureReviewUnchanged(snapshot, normalizedManifest, current);
                            });
                        tsvWritten = true;
                    }
                    catch (Exception exception) when (
                        exception is ArgumentException or IOException or InvalidOperationException or NotSupportedException or UnauthorizedAccessException)
                    {
                        return new ModProjectRevalidationExportResult(
                            true,
                            $"Wrote the metadata-only manifest revalidation review receipt for {current.ReviewedCount} rows, but the optional TSV was not written because its destination changed or could not be secured. No game assets were copied or modified.",
                            normalizedOutput,
                            null,
                            current.ReviewedCount);
                    }
                }

                return new ModProjectRevalidationExportResult(
                    true,
                    tsvWritten
                        ? $"Wrote the metadata-only manifest revalidation review receipt and optional TSV for {current.ReviewedCount} rows. No game assets were copied or modified."
                        : $"Wrote the metadata-only manifest revalidation review receipt for {current.ReviewedCount} rows. No game assets were copied or modified.",
                    normalizedOutput,
                    tsvWritten ? tsvPath : null,
                    current.ReviewedCount);
            }
            catch (Exception exception) when (
                exception is ArgumentException or IOException or InvalidOperationException or NotSupportedException or UnauthorizedAccessException)
            {
                if (exception is InvalidOperationException &&
                    (exception.Message.Contains("changed after this review", StringComparison.OrdinalIgnoreCase) ||
                     exception.Message.Contains("changed at the receipt publication boundary", StringComparison.OrdinalIgnoreCase)))
                {
                    return ChangedAfterReview();
                }

                string message = FileMutationSafety.TryGetKnownRefusal(exception, out string? known) &&
                    !string.IsNullOrWhiteSpace(known)
                        ? known
                        : "The manifest revalidation receipt could not be written. Nothing was changed.";
                return ModProjectRevalidationExportResult.Failed(message);
            }
        }

        private static ModProjectRevalidationReview ReviewForExport(
            AssetCatalogSnapshot snapshot,
            string manifestPath)
        {
            try
            {
                return Review(snapshot, manifestPath);
            }
            catch (Exception exception) when (
                exception is ArgumentException or IOException or InvalidOperationException or NotSupportedException or UnauthorizedAccessException)
            {
                throw new InvalidOperationException(
                    "The planner manifest, catalog, or local export state changed after this review.",
                    exception);
            }
        }

        private static void EnsureReviewUnchanged(
            AssetCatalogSnapshot snapshot,
            string manifestPath,
            ModProjectRevalidationReview expected)
        {
            ModProjectRevalidationReview current = ReviewForExport(snapshot, manifestPath);
            if (!ReviewsMatch(expected, current))
            {
                throw new InvalidOperationException(
                    "The planner manifest, catalog, or local export state changed at the receipt publication boundary.");
            }
        }

        private static bool ReviewsMatch(
            ModProjectRevalidationReview left,
            ModProjectRevalidationReview right)
        {
            byte[] leftBytes = JsonSerializer.SerializeToUtf8Bytes(left, s_writeOptions);
            byte[] rightBytes = JsonSerializer.SerializeToUtf8Bytes(right, s_writeOptions);
            return leftBytes.AsSpan().SequenceEqual(rightBytes);
        }

        private static ModProjectRevalidationExportResult ChangedAfterReview() =>
            ModProjectRevalidationExportResult.Failed(
                "The planner manifest, catalog, or local export state changed after this review. Review again before exporting; nothing was written.");

        public static string BuildTsv(ModProjectRevalidationReview review)
        {
            ArgumentNullException.ThrowIfNull(review);
            var builder = new StringBuilder();
            builder.AppendLine(ReceiptTsvHeader);
            foreach (ModProjectRevalidationEntry entry in review.Entries)
            {
                builder.Append(EscapeTsv(entry.CatalogId)).Append('\t');
                builder.Append(EscapeTsv(entry.DisplayName)).Append('\t');
                builder.Append(EscapeTsv(entry.Kind)).Append('\t');
                builder.Append(ToStatusToken(entry.Status)).Append('\t');
                builder.Append(EscapeTsv(entry.Detail)).Append('\t');
                builder.Append(entry.CatalogDrifted ? "true" : "false").Append('\t');
                builder.Append(entry.Missing ? "true" : "false").Append('\t');
                builder.Append(entry.AmbiguousOrDuplicate ? "true" : "false").Append('\t');
                builder.Append(entry.LocalExportMissing ? "true" : "false").Append('\t');
                builder.Append(entry.LocalHashMismatch ? "true" : "false").Append('\t');
                builder.Append(EscapeTsv(entry.ManifestExpectedExportSha256 ?? string.Empty)).Append('\t');
                builder.Append(EscapeTsv(entry.CurrentExpectedExportSha256 ?? string.Empty)).Append('\t');
                builder.Append(entry.ManifestExportPresent ? "true" : "false").Append('\t');
                builder.Append(entry.CurrentExportPresent ? "true" : "false").Append('\t');
                builder.Append(EscapeTsv(entry.ManifestExportSha256 ?? string.Empty)).Append('\t');
                builder.Append(EscapeTsv(entry.CurrentExportSha256 ?? string.Empty)).AppendLine();
            }

            return builder.ToString();
        }

        private static string ToStatusToken(ModProjectRevalidationStatus status)
        {
            return status switch
            {
                ModProjectRevalidationStatus.CatalogDrifted => "catalog-drifted",
                ModProjectRevalidationStatus.AmbiguousOrDuplicate => "ambiguous-or-duplicate",
                ModProjectRevalidationStatus.LocalExportMissing => "local-export-missing",
                ModProjectRevalidationStatus.LocalHashMismatch => "local-hash-mismatch",
                ModProjectRevalidationStatus.Missing => "missing",
                _ => "unchanged",
            };
        }

        private static string EscapeTsv(string value) =>
            string.IsNullOrEmpty(value)
                ? string.Empty
                : value.Replace('\t', ' ').Replace('\r', ' ').Replace('\n', ' ');

        private static HeldRevalidationInputs HoldCurrentInputs(
            AssetCatalogSnapshot snapshot,
            ModProjectRevalidationReview review)
        {
            AssetCatalogSelection? selection = AssetCatalogFileSafety.ResolveSelection(
                snapshot.CatalogFilePath);
            if (selection is null)
            {
                throw new InvalidOperationException(
                    "The loaded catalog file or its generated export folder is missing or changed.");
            }

            AssetCatalogLoadSession? session = null;
            var sources = new List<AssetCatalogSourceRead>();
            try
            {
                session = AssetCatalogFileSafety.BeginLoad(selection);
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
                var seenPaths = new HashSet<string>(FileMutationSafety.PathComparer);
                foreach (ModProjectRevalidationEntry entry in review.Entries)
                {
                    if (entry.Missing || entry.AmbiguousOrDuplicate)
                    {
                        continue;
                    }

                    List<CurrentCatalogEntry> matches = FindCurrentMatches(
                        snapshot,
                        entry.Kind,
                        entry.CatalogId);
                    if (matches.Count != 1 ||
                        !matches[0].HasLocalExportContract ||
                        string.IsNullOrWhiteSpace(matches[0].ExportPath) ||
                        !seenPaths.Add(matches[0].ExportPath))
                    {
                        continue;
                    }

                    sources.Add(session.OpenSource(
                        matches[0].ExportPath,
                        "Manifest revalidation held local export",
                        expectedTrust: snapshot.TrustEvidence));
                }

                var held = new HeldRevalidationInputs(session, sources);
                session = null;
                sources = [];
                return held;
            }
            finally
            {
                foreach (AssetCatalogSourceRead source in sources)
                {
                    source.Dispose();
                }

                session?.Dispose();
            }
        }

        private static ModProjectRevalidationEntry ReviewEntry(
            AssetCatalogSnapshot snapshot,
            ModProjectPlannedAsset manifestAsset,
            IReadOnlySet<string> duplicateManifestIdentities)
        {
            string kind = NormalizeKind(manifestAsset.Kind);
            if (duplicateManifestIdentities.Contains(IdentityKey(kind, manifestAsset.CatalogId)))
            {
                return BuildEntry(
                    manifestAsset,
                    kind,
                    ModProjectRevalidationStatus.AmbiguousOrDuplicate,
                    "The manifest names this normalized catalog identity more than once; it was not matched.");
            }

            List<CurrentCatalogEntry> matches = FindCurrentMatches(snapshot, kind, manifestAsset.CatalogId);
            if (matches.Count == 0)
            {
                return BuildEntry(
                    manifestAsset,
                    kind,
                    ModProjectRevalidationStatus.Missing,
                    "No row with this normalized identity exists in the currently loaded catalog.");
            }

            if (matches.Count > 1)
            {
                return BuildEntry(
                    manifestAsset,
                    kind,
                    ModProjectRevalidationStatus.AmbiguousOrDuplicate,
                    "The currently loaded catalog has more than one row with this normalized identity; it was not matched.");
            }

            CurrentCatalogEntry current = matches[0];
            string? currentExpectedHash = NormalizeOptionalHash(
                current.ExpectedExportSha256,
                $"current expected export hash for '{manifestAsset.CatalogId}'");
            bool catalogDrifted =
                !string.Equals(manifestAsset.DisplayName, current.DisplayName, StringComparison.Ordinal) ||
                !string.Equals(manifestAsset.CanonicalRef, current.CanonicalRef, StringComparison.Ordinal) ||
                !string.Equals(manifestAsset.SourceArchive ?? string.Empty, current.SourceArchive ?? string.Empty, StringComparison.Ordinal) ||
                !string.Equals(manifestAsset.ExportFileName, current.ExportFileName, StringComparison.Ordinal) ||
                !string.Equals(
                    manifestAsset.ExpectedExportSha256 ?? string.Empty,
                    currentExpectedHash ?? string.Empty,
                    StringComparison.OrdinalIgnoreCase);

            if (!current.HasLocalExportContract)
            {
                return BuildEntry(
                    manifestAsset,
                    kind,
                    catalogDrifted
                        ? ModProjectRevalidationStatus.CatalogDrifted
                        : ModProjectRevalidationStatus.Unchanged,
                    catalogDrifted
                        ? "Catalog metadata or expected-hash metadata changed for this identity."
                        : "Catalog identity and metadata are unchanged; no local export applies to this row.",
                    currentExpectedHash,
                    currentExportPresent: false,
                    currentExportSha256: null);
            }

            ExportInspection export = InspectExport(snapshot, current.ExportPath);
            if (!export.Exists)
            {
                return BuildEntry(
                    manifestAsset,
                    kind,
                    ModProjectRevalidationStatus.LocalExportMissing,
                    "The currently loaded catalog row resolves to a local export that is missing.",
                    currentExpectedHash,
                    currentExportPresent: false,
                    currentExportSha256: null,
                    catalogDrifted: catalogDrifted);
            }

            bool violatesCurrentExpectedHash = currentExpectedHash is not null &&
                !string.Equals(currentExpectedHash, export.Sha256, StringComparison.OrdinalIgnoreCase);
            bool localStateDrifted = !manifestAsset.ExportPresent ||
                !string.Equals(
                    manifestAsset.ExportSha256 ?? string.Empty,
                    export.Sha256 ?? string.Empty,
                    StringComparison.OrdinalIgnoreCase);
            if (violatesCurrentExpectedHash || localStateDrifted)
            {
                return BuildEntry(
                    manifestAsset,
                    kind,
                    ModProjectRevalidationStatus.LocalHashMismatch,
                    violatesCurrentExpectedHash
                        ? "The local export SHA-256 does not match the expected SHA-256 in the currently loaded catalog."
                        : "The local export SHA-256 changed from the value recorded by the manifest.",
                    currentExpectedHash,
                    currentExportPresent: true,
                    currentExportSha256: export.Sha256,
                    catalogDrifted: catalogDrifted);
            }

            return BuildEntry(
                manifestAsset,
                kind,
                catalogDrifted
                    ? ModProjectRevalidationStatus.CatalogDrifted
                    : ModProjectRevalidationStatus.Unchanged,
                catalogDrifted
                    ? "Catalog metadata or expected-hash metadata changed for this identity."
                    : "Catalog metadata and local-export presence/hash are unchanged.",
                currentExpectedHash,
                currentExportPresent: true,
                currentExportSha256: export.Sha256);
        }

        private static ModProjectRevalidationEntry BuildEntry(
            ModProjectPlannedAsset manifestAsset,
            string kind,
            ModProjectRevalidationStatus status,
            string detail,
            string? currentExpectedExportSha256 = null,
            bool currentExportPresent = false,
            string? currentExportSha256 = null,
            bool catalogDrifted = false)
        {
            return new ModProjectRevalidationEntry(
                manifestAsset.CatalogId,
                manifestAsset.DisplayName,
                kind,
                status,
                detail,
                catalogDrifted || status == ModProjectRevalidationStatus.CatalogDrifted,
                status == ModProjectRevalidationStatus.Missing,
                status == ModProjectRevalidationStatus.AmbiguousOrDuplicate,
                status == ModProjectRevalidationStatus.LocalExportMissing,
                status == ModProjectRevalidationStatus.LocalHashMismatch,
                manifestAsset.ExpectedExportSha256,
                currentExpectedExportSha256,
                manifestAsset.ExportPresent,
                currentExportPresent,
                manifestAsset.ExportSha256,
                currentExportSha256);
        }

        private static List<CurrentCatalogEntry> FindCurrentMatches(
            AssetCatalogSnapshot snapshot,
            string kind,
            string catalogId)
        {
            return kind switch
            {
                "texture" => snapshot.Textures
                    .Where(row => SameIdentity(row.CatalogId, catalogId))
                    .Select(static row => new CurrentCatalogEntry(
                        row.CatalogId,
                        row.DisplayName,
                        row.CanonicalRef,
                        null,
                        row.ExportFileName,
                        row.ExportPath,
                        row.ExpectedExportSha256,
                        HasLocalExportContract: true))
                    .ToList(),
                "mesh" => snapshot.LooseMeshes
                    .Where(row => SameIdentity(row.CatalogId, catalogId))
                    .Select(static row => new CurrentCatalogEntry(
                        row.CatalogId,
                        row.DisplayName,
                        row.CanonicalRef,
                        null,
                        row.ExportFileName,
                        row.ExportPath,
                        row.ExpectedExportSha256,
                        HasLocalExportContract: true))
                    .ToList(),
                "embedded-mesh" => snapshot.EmbeddedMeshes
                    .Where(row => SameIdentity(row.CatalogId, catalogId))
                    .Select(static row => new CurrentCatalogEntry(
                        row.CatalogId,
                        row.DisplayName,
                        $"{row.SourceArchive}#{row.BodyName}",
                        row.SourceArchive,
                        row.ExportFileName,
                        row.ExportPath,
                        row.ExpectedExportSha256,
                        HasLocalExportContract: true))
                    .ToList(),
                "goodie" => snapshot.Goodies
                    .Where(row => SameIdentity(row.CatalogId, catalogId))
                    .Select(static row => new CurrentCatalogEntry(
                        row.CatalogId,
                        row.DisplayName,
                        BuildGoodieCanonicalRef(row),
                        string.IsNullOrWhiteSpace(row.SourceArchive) ? null : row.SourceArchive,
                        row.ExportFileName,
                        string.Empty,
                        string.Empty,
                        HasLocalExportContract: false))
                    .ToList(),
                _ => [],
            };
        }

        private static string BuildGoodieCanonicalRef(AssetGoodieItem row)
        {
            return !string.IsNullOrWhiteSpace(row.PrimaryMeshRef)
                ? row.PrimaryMeshRef
                : !string.IsNullOrWhiteSpace(row.PrimaryTextureRef)
                    ? row.PrimaryTextureRef
                    : !string.IsNullOrWhiteSpace(row.VideoCatalogId)
                        ? row.VideoCatalogId
                        : $"{row.SourceArchive}#{row.Index}";
        }

        private static LoadedManifest LoadManifest(string manifestPath)
        {
            string normalized = FileMutationSafety.NormalizeLocalPath(
                manifestPath,
                "Mod project plan manifest");
            if (!string.Equals(Path.GetExtension(normalized), ".json", StringComparison.OrdinalIgnoreCase))
            {
                throw new InvalidOperationException("Choose a .json mod project plan manifest to review.");
            }

            if (!File.Exists(normalized))
            {
                throw new InvalidOperationException("The mod project plan manifest could not be found.");
            }

            FileMutationSafety.RejectExistingReparseAncestors(normalized, "Mod project plan manifest");
            FileMutationSafety.RejectMultipleHardLinks(normalized, "Mod project plan manifest");
            var info = new FileInfo(normalized);
            if (info.Length <= 0 || info.Length > MaxManifestBytes)
            {
                throw new InvalidOperationException(
                    $"The mod project plan manifest must be between 1 byte and {MaxManifestBytes} bytes.");
            }

            byte[] bytes = File.ReadAllBytes(normalized);
            ModProjectPlan? plan;
            try
            {
                plan = JsonSerializer.Deserialize<ModProjectPlan>(bytes, s_readOptions);
            }
            catch (JsonException exception)
            {
                throw new InvalidOperationException(
                    "The mod project plan manifest is not valid planner JSON.",
                    exception);
            }

            if (plan is null)
            {
                throw new InvalidOperationException("The mod project plan manifest is empty or incomplete.");
            }

            ValidateManifest(plan);
            string sha256 = Convert.ToHexString(SHA256.HashData(bytes)).ToLowerInvariant();
            return new LoadedManifest(normalized, sha256, plan);
        }

        private static void ValidateManifest(ModProjectPlan plan)
        {
            if (!string.Equals(plan.ManifestVersion, ModProjectPlannerService.ManifestVersion, StringComparison.Ordinal))
            {
                throw new NotSupportedException(
                    $"Manifest version '{plan.ManifestVersion}' is not supported. Expected '{ModProjectPlannerService.ManifestVersion}'.");
            }

            if (string.IsNullOrWhiteSpace(plan.CatalogFileName) ||
                string.IsNullOrWhiteSpace(plan.CatalogPathContract) ||
                plan.CatalogSchemaVersion <= 0)
            {
                throw new InvalidOperationException("The manifest catalog provenance is missing or incomplete.");
            }

            ValidateRequiredHash(plan.CatalogSha256, "manifest catalog SHA-256");
            if (plan.Assets is null ||
                plan.SelectedCount <= 0 ||
                plan.SelectedCount > ModProjectPlannerService.MaxSelectedAssets ||
                plan.SelectedCount != plan.Assets.Count)
            {
                throw new InvalidOperationException(
                    $"The manifest must contain 1 to {ModProjectPlannerService.MaxSelectedAssets} rows and its selected count must match.");
            }

            if (plan.Assets.Any(static asset => asset is null))
            {
                throw new InvalidOperationException("Every manifest asset row must be an object.");
            }

            foreach (ModProjectPlannedAsset asset in plan.Assets)
            {
                string kind = NormalizeKind(asset.Kind);
                if (kind is not ("texture" or "mesh" or "embedded-mesh" or "goodie") ||
                    string.IsNullOrWhiteSpace(asset.CatalogId) ||
                    string.IsNullOrWhiteSpace(asset.DisplayName) ||
                    string.IsNullOrWhiteSpace(asset.CanonicalRef))
                {
                    throw new InvalidOperationException(
                        "Every manifest row must have a supported kind and non-empty catalog identity metadata.");
                }

                _ = NormalizeOptionalHash(
                    asset.ExpectedExportSha256,
                    $"expected export SHA-256 for '{asset.CatalogId}'");
                _ = NormalizeOptionalHash(
                    asset.ExportSha256,
                    $"local export SHA-256 for '{asset.CatalogId}'");
                if (asset.ExportPresent &&
                    (string.IsNullOrWhiteSpace(asset.ExportSha256) || asset.ExportLengthBytes is null or < 0))
                {
                    throw new InvalidOperationException(
                        $"Manifest row '{asset.CatalogId}' marks a local export present without a valid hash and length.");
                }

                if (!asset.ExportPresent &&
                    (asset.ExportSha256 is not null || asset.ExportLengthBytes is not null))
                {
                    throw new InvalidOperationException(
                        $"Manifest row '{asset.CatalogId}' records local export bytes while marking the export missing.");
                }
            }
        }

        private static string? NormalizeOptionalHash(string? value, string label)
        {
            if (string.IsNullOrWhiteSpace(value))
            {
                return null;
            }

            string normalized = value.Trim().ToLowerInvariant();
            ValidateRequiredHash(normalized, label);
            return normalized;
        }

        private static void ValidateRequiredHash(string? value, string label)
        {
            if (string.IsNullOrWhiteSpace(value) ||
                value.Length != 64 ||
                value.Any(static character => !Uri.IsHexDigit(character)))
            {
                throw new InvalidOperationException($"The {label} must be a 64-character SHA-256 hex digest.");
            }
        }

        private static ExportInspection InspectExport(AssetCatalogSnapshot snapshot, string exportPath)
        {
            using AssetCatalogSourceLease lease = AssetCatalogSourceAccessService.Open(
                snapshot,
                exportPath,
                "Manifest revalidation local export");
            if (!lease.Exists)
            {
                return new ExportInspection(false, null);
            }

            lease.Stream.Position = 0;
            string sha256 = Convert.ToHexString(SHA256.HashData(lease.Stream)).ToLowerInvariant();
            return new ExportInspection(true, sha256);
        }

        private static bool SameIdentity(string left, string right) =>
            string.Equals(left, right, StringComparison.OrdinalIgnoreCase);

        private static string IdentityKey(string kind, string catalogId) =>
            $"{NormalizeKind(kind)}\0{catalogId.Trim()}";

        private static string NormalizeKind(string kind)
        {
            string normalized = (kind ?? string.Empty).Trim().ToLowerInvariant();
            return normalized switch
            {
                "loose-mesh" => "mesh",
                _ => normalized,
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

        private sealed class HeldRevalidationInputs : IDisposable
        {
            private AssetCatalogLoadSession? _session;
            private IReadOnlyList<AssetCatalogSourceRead> _sources;

            internal HeldRevalidationInputs(
                AssetCatalogLoadSession session,
                IReadOnlyList<AssetCatalogSourceRead> sources)
            {
                _session = session;
                _sources = sources;
            }

            public void Dispose()
            {
                foreach (AssetCatalogSourceRead source in _sources)
                {
                    source.Dispose();
                }

                _sources = [];
                _session?.Dispose();
                _session = null;
            }
        }

        private sealed record LoadedManifest(string Path, string Sha256, ModProjectPlan Plan);

        private sealed record CurrentCatalogEntry(
            string CatalogId,
            string DisplayName,
            string CanonicalRef,
            string? SourceArchive,
            string ExportFileName,
            string ExportPath,
            string ExpectedExportSha256,
            bool HasLocalExportContract);

        private sealed record ExportInspection(bool Exists, string? Sha256);
    }
}
