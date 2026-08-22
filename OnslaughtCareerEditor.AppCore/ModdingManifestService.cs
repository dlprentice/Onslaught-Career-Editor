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
    /// <summary>One asset entry in an app-owned modding manifest.</summary>
    public sealed record ModdingManifestAsset(
        string CatalogId,
        string DisplayName,
        string Kind,
        string CanonicalRef,
        string? SourceArchive,
        string ExportFileName,
        bool ExportPresent,
        string? ExportSha256,
        long? ExportLengthBytes,
        IReadOnlyList<string> LinkedTextureRefs);

    /// <summary>The manifest document the app writes for third-party mod authors.</summary>
    public sealed record ModdingManifestDocument(
        string ManifestVersion,
        string GeneratedBy,
        string CatalogFilePath,
        string CatalogSha256,
        int AssetCount,
        IReadOnlyList<ModdingManifestAsset> Assets,
        string ContentBoundary);

    /// <summary>Outcome of one manifest export attempt.</summary>
    public sealed record ModdingManifestExportResult(
        bool Success,
        string Message,
        string? ManifestPath,
        int AssetCount)
    {
        public static ModdingManifestExportResult Failed(string message) =>
            new(false, message, null, 0);
    }

    /// <summary>How many catalog rows of each kind exist, and how many have a player-exported file beside them.</summary>
    public sealed record ModdingKindSummary(
        int TextureCount,
        int TextureExported,
        int MeshCount,
        int MeshExported,
        int EmbeddedMeshCount,
        int EmbeddedExported)
    {
        public int AssetCount => TextureCount + MeshCount + EmbeddedMeshCount;

        public int ExportedCount => TextureExported + MeshExported + EmbeddedExported;

        public string Describe() =>
            $"{TextureCount} textures ({TextureExported} exported), " +
            $"{MeshCount} meshes ({MeshExported} exported), " +
            $"{EmbeddedMeshCount} embedded meshes ({EmbeddedExported} exported)";
    }

    /// <summary>
    /// Writes an app-owned modding manifest beside a generated asset catalog the
    /// player has already exported with their own tools.
    ///
    /// The manifest is metadata only: catalog identity, per-asset catalog ids,
    /// display names, canonical references, export file names, and SHA-256 of the
    /// player's own exported files. It never copies, embeds, or repackages retail
    /// bytes, so sharing it cannot substitute for owning the game - the same
    /// boundary the Asset Library itself is held to. Output goes through
    /// <see cref="FileMutationSafety"/>'s guarded transaction, which stages beside
    /// the destination, refuses game-tree outputs, and verifies committed bytes.
    /// </summary>
    public static class ModdingManifestService
    {
        public const string ManifestVersion = "modding-manifest.v1";

        public const string ContentBoundary =
            "Metadata only. This manifest lists names, ids, references, and hashes of files " +
            "you exported yourself. It contains no game assets; do not pair it with anything " +
            "that redistributes retail content.";

        public const string CatalogTsvFileName = "modding-catalog.tsv";

        public const string CatalogTsvHeader =
            "catalog_id\tdisplay_name\tkind\tcanonical_ref\tsource_archive\texport_file_name\texport_present\texport_sha256\texport_length_bytes";

        private const string ManifestFileName = "modding-manifest.json";

        private static readonly JsonSerializerOptions s_writeOptions = new()
        {
            WriteIndented = true,
            DefaultIgnoreCondition = JsonIgnoreCondition.WhenWritingNull,
        };

        /// <summary>
        /// Builds the manifest document for a loaded snapshot without writing
        /// anything, so callers can show what an export would contain.
        /// </summary>
        public static ModdingManifestDocument BuildDocument(AssetCatalogSnapshot snapshot)
        {
            ArgumentNullException.ThrowIfNull(snapshot);

            var assets = new List<ModdingManifestAsset>();

            foreach (AssetTextureItem texture in snapshot.Textures)
            {
                string? hash = TryHashExport(texture.ExportPath, texture.ExportExists);
                assets.Add(new ModdingManifestAsset(
                    texture.CatalogId,
                    texture.DisplayName,
                    "texture",
                    texture.CanonicalRef,
                    null,
                    texture.ExportFileName,
                    texture.ExportExists,
                    hash,
                    TryLength(texture.ExportPath, texture.ExportExists),
                    Array.Empty<string>()));
            }

            foreach (AssetLooseMeshItem mesh in snapshot.LooseMeshes)
            {
                string? hash = TryHashExport(mesh.ExportPath, mesh.ExportExists);
                assets.Add(new ModdingManifestAsset(
                    mesh.CatalogId,
                    mesh.DisplayName,
                    "mesh",
                    mesh.CanonicalRef,
                    null,
                    mesh.ExportFileName,
                    mesh.ExportExists,
                    hash,
                    TryLength(mesh.ExportPath, mesh.ExportExists),
                    Array.Empty<string>()));
            }

            foreach (AssetEmbeddedMeshItem mesh in snapshot.EmbeddedMeshes)
            {
                string? hash = TryHashExport(mesh.ExportPath, mesh.ExportExists);
                assets.Add(new ModdingManifestAsset(
                    mesh.CatalogId,
                    mesh.DisplayName,
                    "embedded-mesh",
                    $"{mesh.SourceArchive}#{mesh.BodyName}",
                    mesh.SourceArchive,
                    mesh.ExportFileName,
                    mesh.ExportExists,
                    hash,
                    TryLength(mesh.ExportPath, mesh.ExportExists),
                    Array.Empty<string>()));
            }

            return new ModdingManifestDocument(
                ManifestVersion,
                "Onslaught Toolkit (WinUI)",
                Path.GetFileName(snapshot.CatalogFilePath),
                HashText(snapshot.CatalogFilePath) ?? string.Empty,
                assets.Count,
                assets,
                ContentBoundary);
        }

        /// <summary>
        /// Writes <c>modding-manifest.json</c> into the catalog's own export folder.
        /// The catalog file must still exist; the guarded transaction refuses an
        /// output inside a game tree on its own.
        /// </summary>
        public static ModdingManifestExportResult Export(AssetCatalogSnapshot snapshot)
        {
            ArgumentNullException.ThrowIfNull(snapshot);

            string catalogPath = snapshot.CatalogFilePath;
            if (string.IsNullOrWhiteSpace(catalogPath) || !File.Exists(catalogPath))
            {
                return ModdingManifestExportResult.Failed(
                    "Load a generated catalog first. The manifest is written beside its catalog.json.");
            }

            try
            {
                string outputDirectory = Path.GetDirectoryName(Path.GetFullPath(catalogPath))!;
                string outputPath = Path.Combine(outputDirectory, ManifestFileName);
                ModdingManifestDocument document = BuildDocument(snapshot);
                byte[] bytes = JsonSerializer.SerializeToUtf8Bytes(document, s_writeOptions);

                using var transaction = FileMutationSafety.BeginGenerated(outputPath);
                transaction.Commit(bytes);

                return new ModdingManifestExportResult(
                    true,
                    $"Wrote {ManifestFileName} beside the catalog with {document.AssetCount} asset entries.",
                    outputPath,
                    document.AssetCount);
            }
            catch (Exception exception) when (
                exception is IOException or UnauthorizedAccessException or InvalidOperationException)
            {
                return ModdingManifestExportResult.Failed(
                    DescribeCaughtWriteFailure(exception));
            }
        }

        /// <summary>
        /// Spreadsheet-shaped catalog for third-party authors: the same metadata
        /// as the JSON manifest, tab-separated, no retail bytes.
        /// </summary>
        public static string BuildTsv(AssetCatalogSnapshot snapshot)
        {
            ModdingManifestDocument document = BuildDocument(snapshot);
            var builder = new StringBuilder();
            builder.AppendLine(CatalogTsvHeader);
            foreach (ModdingManifestAsset asset in document.Assets)
            {
                builder.Append(EscapeTsv(asset.CatalogId)).Append('\t');
                builder.Append(EscapeTsv(asset.DisplayName)).Append('\t');
                builder.Append(EscapeTsv(asset.Kind)).Append('\t');
                builder.Append(EscapeTsv(asset.CanonicalRef)).Append('\t');
                builder.Append(EscapeTsv(asset.SourceArchive ?? string.Empty)).Append('\t');
                builder.Append(EscapeTsv(asset.ExportFileName)).Append('\t');
                builder.Append(asset.ExportPresent ? "true" : "false").Append('\t');
                builder.Append(EscapeTsv(asset.ExportSha256 ?? string.Empty)).Append('\t');
                builder.Append(asset.ExportLengthBytes.HasValue ? asset.ExportLengthBytes.Value.ToString() : string.Empty);
                builder.AppendLine();
            }

            return builder.ToString();
        }

        /// <summary>
        /// Writes <c>modding-catalog.tsv</c> beside the catalog through the same
        /// guarded transaction as the JSON manifest.
        /// </summary>
        public static ModdingManifestExportResult ExportCatalogTsv(AssetCatalogSnapshot snapshot)
        {
            ArgumentNullException.ThrowIfNull(snapshot);

            string catalogPath = snapshot.CatalogFilePath;
            if (string.IsNullOrWhiteSpace(catalogPath) || !File.Exists(catalogPath))
            {
                return ModdingManifestExportResult.Failed(
                    "Load a generated catalog first. The catalog TSV is written beside its catalog.json.");
            }

            try
            {
                string outputDirectory = Path.GetDirectoryName(Path.GetFullPath(catalogPath))!;
                string outputPath = Path.Combine(outputDirectory, CatalogTsvFileName);
                byte[] bytes = Encoding.UTF8.GetBytes(BuildTsv(snapshot));

                using var transaction = FileMutationSafety.BeginGenerated(outputPath);
                transaction.Commit(bytes);

                ModdingKindSummary summary = BuildKindSummary(snapshot);
                return new ModdingManifestExportResult(
                    true,
                    $"Wrote {CatalogTsvFileName} beside the catalog with {summary.AssetCount} asset rows ({summary.Describe()}).",
                    outputPath,
                    summary.AssetCount);
            }
            catch (Exception exception) when (
                exception is IOException or UnauthorizedAccessException or InvalidOperationException)
            {
                return ModdingManifestExportResult.Failed(
                    DescribeCaughtWriteFailure(exception, "catalog TSV"));
            }
        }

        /// <summary>Counts catalog rows by kind and whether the player's export file is present.</summary>
        public static ModdingKindSummary BuildKindSummary(AssetCatalogSnapshot snapshot)
        {
            ArgumentNullException.ThrowIfNull(snapshot);
            return new ModdingKindSummary(
                snapshot.Textures.Count,
                snapshot.Textures.Count(texture => texture.ExportExists),
                snapshot.LooseMeshes.Count,
                snapshot.LooseMeshes.Count(mesh => mesh.ExportExists),
                snapshot.EmbeddedMeshes.Count,
                snapshot.EmbeddedMeshes.Count(mesh => mesh.ExportExists));
        }

        private static string EscapeTsv(string value)
        {
            if (string.IsNullOrEmpty(value))
            {
                return string.Empty;
            }

            return value.Replace('\t', ' ').Replace('\r', ' ').Replace('\n', ' ');
        }

        /// <summary>
        /// Known AppCore refusals are already user-facing sentences and pass through;
        /// anything else (raw OS errors included) collapses to one honest sentence
        /// that says nothing was changed.
        /// </summary>
        private static string DescribeCaughtWriteFailure(Exception exception, string outputName = "manifest")
        {
            return FileMutationSafety.TryGetKnownRefusal(exception, out string? message) && !string.IsNullOrWhiteSpace(message)
                ? message
                : $"The {outputName} could not be written. Nothing was changed.";
        }

        private static string? TryHashExport(string exportPath, bool exportExists)
        {
            if (!exportExists || string.IsNullOrWhiteSpace(exportPath) || !File.Exists(exportPath))
            {
                return null;
            }

            try
            {
                using FileStream stream = File.OpenRead(exportPath);
                return Convert.ToHexString(SHA256.HashData(stream)).ToLowerInvariant();
            }
            catch (Exception exception) when (exception is IOException or UnauthorizedAccessException)
            {
                return null;
            }
        }

        private static long? TryLength(string exportPath, bool exportExists)
        {
            if (!exportExists || string.IsNullOrWhiteSpace(exportPath) || !File.Exists(exportPath))
            {
                return null;
            }

            try
            {
                return new FileInfo(exportPath).Length;
            }
            catch (Exception exception) when (exception is IOException or UnauthorizedAccessException)
            {
                return null;
            }
        }

        private static string? HashText(string catalogPath)
        {
            if (string.IsNullOrWhiteSpace(catalogPath) || !File.Exists(catalogPath))
            {
                return null;
            }

            try
            {
                using FileStream stream = File.OpenRead(catalogPath);
                return Convert.ToHexString(SHA256.HashData(stream)).ToLowerInvariant();
            }
            catch (Exception exception) when (exception is IOException or UnauthorizedAccessException)
            {
                return null;
            }
        }
    }
}
