using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Security.Cryptography;
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
        /// Known AppCore refusals are already user-facing sentences and pass through;
        /// anything else (raw OS errors included) collapses to one honest sentence
        /// that says nothing was changed.
        /// </summary>
        private static string DescribeCaughtWriteFailure(Exception exception)
        {
            return FileMutationSafety.TryGetKnownRefusal(exception, out string? message) && !string.IsNullOrWhiteSpace(message)
                ? message
                : "The manifest could not be written. Nothing was changed.";
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
