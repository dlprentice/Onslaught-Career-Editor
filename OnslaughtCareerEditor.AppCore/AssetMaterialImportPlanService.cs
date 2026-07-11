using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;

namespace Onslaught___Career_Editor
{
    public sealed class AssetMaterialImportPlanService
    {
        public const int DefaultSampleLimit = 12;

        public AssetMaterialImportPlan Build(AssetCatalogSnapshot snapshot, int sampleLimit = DefaultSampleLimit)
        {
            sampleLimit = Math.Clamp(sampleLimit, 0, 100);
            AssetModelTextureLinkService textureLinkService = new();
            List<AssetMaterialImportPlanRow> rows = new();

            rows.AddRange(snapshot.LooseMeshes.Select(mesh => BuildRow(
                textureLinkService,
                snapshot,
                "loose mesh",
                mesh.DisplayName,
                mesh.CanonicalRef,
                mesh.ExportFileName,
                mesh.ExportPath,
                mesh.ExportExists,
                mesh.ModelSummary)));
            rows.AddRange(snapshot.EmbeddedMeshes.Select(mesh => BuildRow(
                textureLinkService,
                snapshot,
                "embedded mesh",
                mesh.DisplayName,
                mesh.SourceArchive,
                mesh.ExportFileName,
                mesh.ExportPath,
                mesh.ExportExists,
                mesh.ModelSummary)));

            int totalTextureBindings = rows.Sum(static row => row.TextureBindingFileNames.Count);
            int totalCatalogMatched = rows.Sum(static row => row.CatalogMatchedTextureNames.Count);
            int totalCatalogMissing = rows.Sum(static row => row.CatalogMissingTextureFileNames.Count);
            int totalSidecars = rows.Sum(static row => row.SidecarTextureFileNames.Count);
            int totalMissingSidecars = rows.Sum(static row => row.CatalogMissingSidecarTextureFileNames.Count);
            int totalUnresolved = rows.Sum(static row => row.UnresolvedTextureBindingFileNames.Count);

            return new AssetMaterialImportPlan(
                TotalModelRows: rows.Count,
                MetadataAvailableRows: rows.Count(static row => row.MetadataAvailable),
                RowsWithTextureBindings: rows.Count(static row => row.TextureBindingFileNames.Count > 0),
                RowsWithAllTextureBindingsCatalogMatched: rows.Count(static row =>
                    row.TextureBindingFileNames.Count > 0 && row.CatalogMissingTextureFileNames.Count == 0),
                RowsWithCatalogMissingTextureBindings: rows.Count(static row => row.CatalogMissingTextureFileNames.Count > 0),
                RowsWithSidecarTexturePreviews: rows.Count(static row => row.SidecarTextureFileNames.Count > 0),
                RowsWithCatalogMissingSidecarTexturePreviews: rows.Count(static row =>
                    row.CatalogMissingSidecarTextureFileNames.Count > 0),
                RowsWithUnresolvedTextureBindings: rows.Count(static row => row.UnresolvedTextureBindingFileNames.Count > 0),
                TotalTextureBindingFiles: totalTextureBindings,
                TotalCatalogMatchedTextureBindingFiles: totalCatalogMatched,
                TotalCatalogMissingTextureBindingFiles: totalCatalogMissing,
                TotalSidecarTextureFiles: totalSidecars,
                TotalCatalogMissingSidecarTextureFiles: totalMissingSidecars,
                TotalUnresolvedTextureBindingFiles: totalUnresolved,
                Samples: rows
                    .OrderByDescending(static row => row.TextureBindingFileNames.Count > 0)
                    .ThenBy(static row => row.Kind, StringComparer.OrdinalIgnoreCase)
                    .ThenBy(static row => row.Label, StringComparer.OrdinalIgnoreCase)
                    .Take(sampleLimit)
                    .ToList(),
                UnresolvedSamples: rows
                    .Where(static row => row.UnresolvedTextureBindingFileNames.Count > 0)
                    .OrderBy(static row => row.Kind, StringComparer.OrdinalIgnoreCase)
                    .ThenBy(static row => row.Label, StringComparer.OrdinalIgnoreCase)
                    .Take(sampleLimit)
                    .ToList());
        }

        private static AssetMaterialImportPlanRow BuildRow(
            AssetModelTextureLinkService textureLinkService,
            AssetCatalogSnapshot snapshot,
            string kind,
            string label,
            string sourceLabel,
            string exportFileName,
            string exportPath,
            bool exportExists,
            AssetModelSummary summary)
        {
            AssetModelTextureLinks links = textureLinkService.Build(snapshot.Textures, summary);
            IReadOnlyList<AssetModelSidecarTexture> allSidecars =
                textureLinkService.ResolveSidecarTextures(snapshot, exportPath, links.TextureBindingFileNames);
            IReadOnlyList<AssetModelSidecarTexture> missingSidecars =
                textureLinkService.ResolveSidecarTextures(snapshot, exportPath, links.CatalogMissingTextureFileNames);
            HashSet<string> missingSidecarKeys = missingSidecars
                .Select(static texture => NormalizeTextureKey(texture.FileName))
                .Where(static key => !string.IsNullOrWhiteSpace(key))
                .ToHashSet(StringComparer.OrdinalIgnoreCase);
            IReadOnlyList<string> unresolved = links.CatalogMissingTextureFileNames
                .Where(binding => !missingSidecarKeys.Contains(NormalizeTextureKey(binding)))
                .OrderBy(static value => value, StringComparer.OrdinalIgnoreCase)
                .ToList();

            return new AssetMaterialImportPlanRow(
                Kind: kind,
                Label: string.IsNullOrWhiteSpace(label) ? "Model" : label,
                SourceLabel: string.IsNullOrWhiteSpace(sourceLabel) ? "Unknown source" : sourceLabel,
                ExportFileName: exportFileName,
                ExportExists: exportExists,
                MetadataAvailable: summary.MetadataAvailable,
                MaterialCount: summary.MaterialCount,
                TextureToMaterialConnectionCount: summary.TextureToMaterialConnectionCount,
                TextureBindingFileNames: links.TextureBindingFileNames,
                CatalogMatchedTextureNames: links.CatalogMatchedTextureNames,
                CatalogMissingTextureFileNames: links.CatalogMissingTextureFileNames,
                SidecarTextureFileNames: allSidecars
                    .Select(static texture => texture.FileName)
                    .OrderBy(static value => value, StringComparer.OrdinalIgnoreCase)
                    .ToList(),
                CatalogMissingSidecarTextureFileNames: missingSidecars
                    .Select(static texture => texture.FileName)
                    .OrderBy(static value => value, StringComparer.OrdinalIgnoreCase)
                    .ToList(),
                UnresolvedTextureBindingFileNames: unresolved,
                Status: BuildStatus(links, missingSidecars.Count, unresolved.Count));
        }

        private static string BuildStatus(
            AssetModelTextureLinks links,
            int catalogMissingSidecarCount,
            int unresolvedCount)
        {
            if (links.TextureBindingFileNames.Count == 0)
            {
                return "No readable FBX texture binding files were recorded for this model export.";
            }

            if (links.CatalogMissingTextureFileNames.Count == 0)
            {
                return "All readable FBX texture binding files resolve through catalog texture rows.";
            }

            if (unresolvedCount == 0)
            {
                return "All catalog-missing FBX texture binding files have local sidecar texture previews.";
            }

            if (catalogMissingSidecarCount > 0)
            {
                return "Some catalog-missing FBX texture binding files have sidecar previews; some remain unresolved.";
            }

            return "Some FBX texture binding files are not resolved through the catalog or local sidecar previews.";
        }

        private static string NormalizeTextureKey(string value)
        {
            if (string.IsNullOrWhiteSpace(value))
            {
                return string.Empty;
            }

            string fileName = Path.GetFileName(value.Replace('\\', Path.DirectorySeparatorChar).Replace('/', Path.DirectorySeparatorChar));
            if (string.IsNullOrWhiteSpace(fileName))
            {
                return string.Empty;
            }

            string withoutExtension = Path.GetFileNameWithoutExtension(fileName);
            int tgaIndex = withoutExtension.IndexOf(".tga", StringComparison.OrdinalIgnoreCase);
            if (tgaIndex >= 0)
            {
                withoutExtension = withoutExtension[..tgaIndex];
            }

            int ddsIndex = withoutExtension.IndexOf(".dds", StringComparison.OrdinalIgnoreCase);
            if (ddsIndex >= 0)
            {
                withoutExtension = withoutExtension[..ddsIndex];
            }

            int variantIndex = withoutExtension.IndexOf('(');
            if (variantIndex >= 0)
            {
                withoutExtension = withoutExtension[..variantIndex];
            }

            return withoutExtension.Trim().ToLowerInvariant();
        }
    }

    public sealed record AssetMaterialImportPlan(
        int TotalModelRows,
        int MetadataAvailableRows,
        int RowsWithTextureBindings,
        int RowsWithAllTextureBindingsCatalogMatched,
        int RowsWithCatalogMissingTextureBindings,
        int RowsWithSidecarTexturePreviews,
        int RowsWithCatalogMissingSidecarTexturePreviews,
        int RowsWithUnresolvedTextureBindings,
        int TotalTextureBindingFiles,
        int TotalCatalogMatchedTextureBindingFiles,
        int TotalCatalogMissingTextureBindingFiles,
        int TotalSidecarTextureFiles,
        int TotalCatalogMissingSidecarTextureFiles,
        int TotalUnresolvedTextureBindingFiles,
        IReadOnlyList<AssetMaterialImportPlanRow> Samples,
        IReadOnlyList<AssetMaterialImportPlanRow> UnresolvedSamples);

    public sealed record AssetMaterialImportPlanRow(
        string Kind,
        string Label,
        string SourceLabel,
        string ExportFileName,
        bool ExportExists,
        bool MetadataAvailable,
        int MaterialCount,
        int TextureToMaterialConnectionCount,
        IReadOnlyList<string> TextureBindingFileNames,
        IReadOnlyList<string> CatalogMatchedTextureNames,
        IReadOnlyList<string> CatalogMissingTextureFileNames,
        IReadOnlyList<string> SidecarTextureFileNames,
        IReadOnlyList<string> CatalogMissingSidecarTextureFileNames,
        IReadOnlyList<string> UnresolvedTextureBindingFileNames,
        string Status);
}
