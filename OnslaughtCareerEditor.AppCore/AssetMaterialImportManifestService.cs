using System;
using System.Collections.Generic;
using System.Linq;

namespace Onslaught___Career_Editor
{
    public sealed class AssetMaterialImportManifestService
    {
        public AssetMaterialImportManifest Build(AssetCatalogSnapshot snapshot)
        {
            AssetModelTextureLinkService textureLinkService = new();
            List<AssetMaterialImportManifestModelRow> rows = new();

            rows.AddRange(snapshot.LooseMeshes.Select(mesh => BuildRow(
                textureLinkService,
                snapshot.Textures,
                kind: "loose mesh",
                catalogId: mesh.CatalogId,
                label: mesh.DisplayName,
                sourceLabel: mesh.CanonicalRef,
                exportFileName: mesh.ExportFileName,
                exportExists: mesh.ExportExists,
                summary: mesh.ModelSummary,
                exportPath: mesh.ExportPath)));

            rows.AddRange(snapshot.EmbeddedMeshes.Select(mesh => BuildRow(
                textureLinkService,
                snapshot.Textures,
                kind: "embedded mesh",
                catalogId: mesh.CatalogId,
                label: mesh.DisplayName,
                sourceLabel: mesh.SourceArchive,
                exportFileName: mesh.ExportFileName,
                exportExists: mesh.ExportExists,
                summary: mesh.ModelSummary,
                exportPath: mesh.ExportPath)));

            int totalTextureBindings = rows.Sum(static row => row.TextureBindings.Count);
            int catalogResolved = rows.Sum(static row =>
                row.TextureBindings.Count(static binding => binding.ResolutionKind == "catalog"));
            int sidecarResolved = rows.Sum(static row =>
                row.TextureBindings.Count(static binding => binding.ResolutionKind == "sidecar"));
            int unresolved = rows.Sum(static row =>
                row.TextureBindings.Count(static binding => binding.ResolutionKind == "unresolved"));

            return new AssetMaterialImportManifest(
                TotalModelRows: rows.Count,
                MetadataAvailableRows: rows.Count(static row => row.MetadataAvailable),
                RowsWithTextureBindings: rows.Count(static row => row.TextureBindings.Count > 0),
                RowsReadyForImport: rows.Count(static row =>
                    row.TextureBindings.Count > 0 &&
                    row.TextureBindings.All(static binding => binding.ResolutionKind is "catalog" or "sidecar")),
                RowsWithUnresolvedTextureBindings: rows.Count(static row =>
                    row.TextureBindings.Any(static binding => binding.ResolutionKind == "unresolved")),
                TotalTextureBindingRows: totalTextureBindings,
                CatalogResolvedTextureBindingRows: catalogResolved,
                SidecarResolvedTextureBindingRows: sidecarResolved,
                UnresolvedTextureBindingRows: unresolved,
                Models: rows
                    .OrderByDescending(static row => row.TextureBindings.Count > 0)
                    .ThenBy(static row => row.Kind, StringComparer.OrdinalIgnoreCase)
                    .ThenBy(static row => row.Label, StringComparer.OrdinalIgnoreCase)
                    .ToList());
        }

        private static AssetMaterialImportManifestModelRow BuildRow(
            AssetModelTextureLinkService textureLinkService,
            IReadOnlyList<AssetTextureItem> textures,
            string kind,
            string catalogId,
            string label,
            string sourceLabel,
            string exportFileName,
            bool exportExists,
            AssetModelSummary summary,
            string exportPath)
        {
            IReadOnlyList<AssetModelTextureBindingResolution> textureBindings =
                textureLinkService.BuildBindingResolutions(textures, exportPath, summary);

            string readiness = textureBindings.Count switch
            {
                0 => "no-texture-bindings",
                _ when textureBindings.All(static binding => binding.ResolutionKind is "catalog" or "sidecar") => "ready",
                _ => "unresolved-texture-bindings"
            };

            return new AssetMaterialImportManifestModelRow(
                Kind: kind,
                CatalogId: catalogId,
                Label: string.IsNullOrWhiteSpace(label) ? "Model" : label,
                SourceLabel: string.IsNullOrWhiteSpace(sourceLabel) ? "Unknown source" : sourceLabel,
                ExportFileName: exportFileName,
                ExportExists: exportExists,
                MetadataAvailable: summary.MetadataAvailable,
                MaterialCount: summary.MaterialCount,
                TextureToMaterialConnectionCount: summary.TextureToMaterialConnectionCount,
                TextureBindings: textureBindings,
                ImportReadiness: readiness);
        }
    }

    public sealed record AssetMaterialImportManifest(
        int TotalModelRows,
        int MetadataAvailableRows,
        int RowsWithTextureBindings,
        int RowsReadyForImport,
        int RowsWithUnresolvedTextureBindings,
        int TotalTextureBindingRows,
        int CatalogResolvedTextureBindingRows,
        int SidecarResolvedTextureBindingRows,
        int UnresolvedTextureBindingRows,
        IReadOnlyList<AssetMaterialImportManifestModelRow> Models);

    public sealed record AssetMaterialImportManifestModelRow(
        string Kind,
        string CatalogId,
        string Label,
        string SourceLabel,
        string ExportFileName,
        bool ExportExists,
        bool MetadataAvailable,
        int MaterialCount,
        int TextureToMaterialConnectionCount,
        IReadOnlyList<AssetModelTextureBindingResolution> TextureBindings,
        string ImportReadiness);
}
