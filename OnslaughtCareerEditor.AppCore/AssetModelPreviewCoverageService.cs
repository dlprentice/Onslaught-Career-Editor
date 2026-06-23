namespace Onslaught___Career_Editor
{
    public sealed class AssetModelPreviewCoverageService
    {
        private const int DefaultSampleLimit = 12;

        public AssetModelPreviewCoverage Build(AssetCatalogSnapshot snapshot, int sampleLimit = DefaultSampleLimit)
        {
            if (sampleLimit < 0)
            {
                sampleLimit = 0;
            }

            AssetModelTextureLinkService textureLinkService = new();
            List<AssetModelPreviewCoverageRow> rows = new();
            rows.AddRange(snapshot.LooseMeshes.Select(mesh => BuildRow(
                "loose mesh",
                mesh.DisplayName,
                mesh.CanonicalRef,
                mesh.ExportFileName,
                mesh.ExportExists,
                mesh.ModelSummary,
                textureLinkService.Build(snapshot.Textures, mesh.ModelSummary))));
            rows.AddRange(snapshot.EmbeddedMeshes.Select(mesh => BuildRow(
                "embedded mesh",
                mesh.DisplayName,
                mesh.SourceArchive,
                mesh.ExportFileName,
                mesh.ExportExists,
                mesh.ModelSummary,
                textureLinkService.Build(snapshot.Textures, mesh.ModelSummary))));

            int existingExports = rows.Count(static row => row.ExportExists);
            int metadataAvailable = rows.Count(static row => row.MetadataAvailable);
            int wireframeAvailable = rows.Count(static row => row.WireframeAvailable);
            int rowsWithMaterials = rows.Count(static row => row.MaterialCount > 0);
            int rowsWithTextureBindings = rows.Count(static row => row.TextureBindingCount > 0);
            int totalMaterialNodes = rows.Sum(static row => row.MaterialCount);
            int totalTextureBindingNodes = rows.Sum(static row => row.TextureBindingCount);
            int rowsWithMaterialLayers = rows.Count(static row => row.MaterialLayerCount > 0);
            int rowsWithMaterialAssignmentIndices = rows.Count(static row => row.MaterialAssignmentIndexCount > 0);
            int totalMaterialLayerNodes = rows.Sum(static row => row.MaterialLayerCount);
            int totalMaterialAssignmentIndices = rows.Sum(static row => row.MaterialAssignmentIndexCount);
            int rowsWithMaterialMappingModes = rows.Count(static row => row.MaterialMappingModes.Count > 0);
            int rowsWithMaterialReferenceModes = rows.Count(static row => row.MaterialReferenceModes.Count > 0);
            IReadOnlyList<string> materialMappingModes = rows
                .SelectMany(static row => row.MaterialMappingModes)
                .Distinct(StringComparer.OrdinalIgnoreCase)
                .OrderBy(static name => name, StringComparer.OrdinalIgnoreCase)
                .ToList();
            IReadOnlyList<string> materialReferenceModes = rows
                .SelectMany(static row => row.MaterialReferenceModes)
                .Distinct(StringComparer.OrdinalIgnoreCase)
                .OrderBy(static name => name, StringComparer.OrdinalIgnoreCase)
                .ToList();
            int rowsWithObjectConnections = rows.Count(static row => row.ObjectConnectionCount > 0);
            int rowsWithPropertyConnections = rows.Count(static row => row.PropertyConnectionCount > 0);
            int rowsWithTextureToMaterialConnections = rows.Count(static row => row.TextureToMaterialConnectionCount > 0);
            int rowsWithTextureToMaterialSlotNames = rows.Count(static row => row.TextureToMaterialSlotNames.Count > 0);
            int totalObjectConnections = rows.Sum(static row => row.ObjectConnectionCount);
            int totalPropertyConnections = rows.Sum(static row => row.PropertyConnectionCount);
            int totalTextureToMaterialConnections = rows.Sum(static row => row.TextureToMaterialConnectionCount);
            IReadOnlyList<string> textureToMaterialSlotNames = rows
                .SelectMany(static row => row.TextureToMaterialSlotNames)
                .Distinct(StringComparer.OrdinalIgnoreCase)
                .OrderBy(static name => name, StringComparer.OrdinalIgnoreCase)
                .ToList();
            int rowsWithCatalogMatchedTextureBindingFiles =
                rows.Count(static row => row.CatalogMatchedTextureNames.Count > 0);
            int rowsWithoutCatalogMatchedTextureBindingFiles =
                rows.Count(static row => row.CatalogMatchedTextureNames.Count == 0);
            int rowsWithAllTextureBindingFilesCatalogMatched =
                rows.Count(static row => row.TextureBindingCount > 0 && row.CatalogMissingTextureFileNames.Count == 0);
            int rowsWithAnyMissingCatalogTextureBindingFiles =
                rows.Count(static row => row.CatalogMissingTextureFileNames.Count > 0);
            int totalCatalogMatchedTextureBindingFiles =
                rows.Sum(static row => row.CatalogMatchedTextureNames.Count);
            int missingExports = rows.Count(static row => !row.ExportExists);
            int unreadableExports = rows.Count(static row => row.ExportExists && !row.MetadataAvailable);
            int metadataWithoutWireframe = rows.Count(static row => row.MetadataAvailable && !row.WireframeAvailable);
            int rowsWithTextureCoordinates = rows.Count(static row => row.TextureCoordinateCount > 0);
            int rowsWithTextureCoordinateIndices = rows.Count(static row => row.TextureCoordinateIndexCount > 0);
            int totalTextureCoordinates = rows.Sum(static row => row.TextureCoordinateCount);
            int totalTextureCoordinateIndices = rows.Sum(static row => row.TextureCoordinateIndexCount);
            int rowsWithNormals = rows.Count(static row => row.NormalCount > 0);
            int rowsWithNormalIndices = rows.Count(static row => row.NormalIndexCount > 0);
            int totalNormals = rows.Sum(static row => row.NormalCount);
            int totalNormalIndices = rows.Sum(static row => row.NormalIndexCount);
            int rowsWithNormalMappingModes =
                rows.Count(static row => row.NormalMappingModes.Count > 0);
            int rowsWithNormalReferenceModes =
                rows.Count(static row => row.NormalReferenceModes.Count > 0);
            IReadOnlyList<string> normalMappingModes = rows
                .SelectMany(static row => row.NormalMappingModes)
                .Distinct(StringComparer.OrdinalIgnoreCase)
                .OrderBy(static name => name, StringComparer.OrdinalIgnoreCase)
                .ToList();
            IReadOnlyList<string> normalReferenceModes = rows
                .SelectMany(static row => row.NormalReferenceModes)
                .Distinct(StringComparer.OrdinalIgnoreCase)
                .OrderBy(static name => name, StringComparer.OrdinalIgnoreCase)
                .ToList();
            int rowsWithVertexColors = rows.Count(static row => row.VertexColorCount > 0);
            int rowsWithVertexColorIndices = rows.Count(static row => row.VertexColorIndexCount > 0);
            int totalVertexColors = rows.Sum(static row => row.VertexColorCount);
            int totalVertexColorIndices = rows.Sum(static row => row.VertexColorIndexCount);
            int rowsWithVertexColorMappingModes =
                rows.Count(static row => row.VertexColorMappingModes.Count > 0);
            int rowsWithVertexColorReferenceModes =
                rows.Count(static row => row.VertexColorReferenceModes.Count > 0);
            IReadOnlyList<string> vertexColorMappingModes = rows
                .SelectMany(static row => row.VertexColorMappingModes)
                .Distinct(StringComparer.OrdinalIgnoreCase)
                .OrderBy(static name => name, StringComparer.OrdinalIgnoreCase)
                .ToList();
            IReadOnlyList<string> vertexColorReferenceModes = rows
                .SelectMany(static row => row.VertexColorReferenceModes)
                .Distinct(StringComparer.OrdinalIgnoreCase)
                .OrderBy(static name => name, StringComparer.OrdinalIgnoreCase)
                .ToList();
            int rowsWithTextureCoordinateMappingModes =
                rows.Count(static row => row.TextureCoordinateMappingModes.Count > 0);
            int rowsWithTextureCoordinateReferenceModes =
                rows.Count(static row => row.TextureCoordinateReferenceModes.Count > 0);
            IReadOnlyList<string> textureCoordinateMappingModes = rows
                .SelectMany(static row => row.TextureCoordinateMappingModes)
                .Distinct(StringComparer.OrdinalIgnoreCase)
                .OrderBy(static name => name, StringComparer.OrdinalIgnoreCase)
                .ToList();
            IReadOnlyList<string> textureCoordinateReferenceModes = rows
                .SelectMany(static row => row.TextureCoordinateReferenceModes)
                .Distinct(StringComparer.OrdinalIgnoreCase)
                .OrderBy(static name => name, StringComparer.OrdinalIgnoreCase)
                .ToList();

            return new AssetModelPreviewCoverage(
                TotalModelRows: rows.Count,
                LooseMeshRows: snapshot.LooseMeshes.Count,
                EmbeddedMeshRows: snapshot.EmbeddedMeshes.Count,
                ExistingExportRows: existingExports,
                MissingExportRows: missingExports,
                MetadataAvailableRows: metadataAvailable,
                WireframeAvailableRows: wireframeAvailable,
                RowsWithTextureCoordinates: rowsWithTextureCoordinates,
                RowsWithTextureCoordinateIndices: rowsWithTextureCoordinateIndices,
                TotalTextureCoordinates: totalTextureCoordinates,
                TotalTextureCoordinateIndices: totalTextureCoordinateIndices,
                RowsWithNormals: rowsWithNormals,
                RowsWithNormalIndices: rowsWithNormalIndices,
                TotalNormals: totalNormals,
                TotalNormalIndices: totalNormalIndices,
                RowsWithNormalMappingModes: rowsWithNormalMappingModes,
                RowsWithNormalReferenceModes: rowsWithNormalReferenceModes,
                NormalMappingModes: normalMappingModes,
                NormalReferenceModes: normalReferenceModes,
                RowsWithVertexColors: rowsWithVertexColors,
                RowsWithVertexColorIndices: rowsWithVertexColorIndices,
                TotalVertexColors: totalVertexColors,
                TotalVertexColorIndices: totalVertexColorIndices,
                RowsWithVertexColorMappingModes: rowsWithVertexColorMappingModes,
                RowsWithVertexColorReferenceModes: rowsWithVertexColorReferenceModes,
                VertexColorMappingModes: vertexColorMappingModes,
                VertexColorReferenceModes: vertexColorReferenceModes,
                RowsWithTextureCoordinateMappingModes: rowsWithTextureCoordinateMappingModes,
                RowsWithTextureCoordinateReferenceModes: rowsWithTextureCoordinateReferenceModes,
                TextureCoordinateMappingModes: textureCoordinateMappingModes,
                TextureCoordinateReferenceModes: textureCoordinateReferenceModes,
                RowsWithMaterials: rowsWithMaterials,
                RowsWithTextureBindings: rowsWithTextureBindings,
                TotalMaterialNodes: totalMaterialNodes,
                TotalTextureBindingNodes: totalTextureBindingNodes,
                RowsWithMaterialLayers: rowsWithMaterialLayers,
                RowsWithMaterialAssignmentIndices: rowsWithMaterialAssignmentIndices,
                TotalMaterialLayerNodes: totalMaterialLayerNodes,
                TotalMaterialAssignmentIndices: totalMaterialAssignmentIndices,
                RowsWithMaterialMappingModes: rowsWithMaterialMappingModes,
                RowsWithMaterialReferenceModes: rowsWithMaterialReferenceModes,
                MaterialMappingModes: materialMappingModes,
                MaterialReferenceModes: materialReferenceModes,
                RowsWithObjectConnections: rowsWithObjectConnections,
                RowsWithPropertyConnections: rowsWithPropertyConnections,
                RowsWithTextureToMaterialConnections: rowsWithTextureToMaterialConnections,
                RowsWithTextureToMaterialSlotNames: rowsWithTextureToMaterialSlotNames,
                TotalObjectConnections: totalObjectConnections,
                TotalPropertyConnections: totalPropertyConnections,
                TotalTextureToMaterialConnections: totalTextureToMaterialConnections,
                TextureToMaterialSlotNames: textureToMaterialSlotNames,
                RowsWithCatalogMatchedTextureBindingFiles: rowsWithCatalogMatchedTextureBindingFiles,
                RowsWithoutCatalogMatchedTextureBindingFiles: rowsWithoutCatalogMatchedTextureBindingFiles,
                RowsWithAllTextureBindingFilesCatalogMatched: rowsWithAllTextureBindingFilesCatalogMatched,
                RowsWithAnyMissingCatalogTextureBindingFiles: rowsWithAnyMissingCatalogTextureBindingFiles,
                TotalCatalogMatchedTextureBindingFiles: totalCatalogMatchedTextureBindingFiles,
                MetadataWithoutWireframeRows: metadataWithoutWireframe,
                UnreadableExportRows: unreadableExports,
                Samples: rows
                    .OrderByDescending(static row => row.WireframeAvailable)
                    .ThenByDescending(static row => row.MetadataAvailable)
                    .ThenBy(static row => row.Kind, StringComparer.OrdinalIgnoreCase)
                    .ThenBy(static row => row.Label, StringComparer.OrdinalIgnoreCase)
                    .Take(sampleLimit)
                    .ToList(),
                UnmatchedSamples: rows
                    .Where(static row => row.CatalogMatchedTextureNames.Count == 0)
                    .OrderBy(static row => row.Kind, StringComparer.OrdinalIgnoreCase)
                    .ThenBy(static row => row.Label, StringComparer.OrdinalIgnoreCase)
                    .Take(sampleLimit)
                    .ToList());
        }

        private static AssetModelPreviewCoverageRow BuildRow(
            string kind,
            string label,
            string sourceLabel,
            string exportFileName,
            bool exportExists,
            AssetModelSummary summary,
            AssetModelTextureLinks textureLinks)
        {
            bool wireframeAvailable = summary.GeometryPreview.Available;
            return new AssetModelPreviewCoverageRow(
                Kind: kind,
                Label: string.IsNullOrWhiteSpace(label) ? "Model" : label,
                SourceLabel: string.IsNullOrWhiteSpace(sourceLabel) ? "Unknown source" : sourceLabel,
                ExportFileName: exportFileName,
                ExportExists: exportExists,
                MetadataAvailable: summary.MetadataAvailable,
                WireframeAvailable: wireframeAvailable,
                VertexCount: summary.VertexCount,
                PolygonIndexCount: summary.PolygonIndexCount,
                NormalCount: summary.NormalCount,
                NormalIndexCount: summary.NormalIndexCount,
                NormalMappingModes: summary.NormalMappingModes,
                NormalReferenceModes: summary.NormalReferenceModes,
                VertexColorCount: summary.VertexColorCount,
                VertexColorIndexCount: summary.VertexColorIndexCount,
                VertexColorMappingModes: summary.VertexColorMappingModes,
                VertexColorReferenceModes: summary.VertexColorReferenceModes,
                TextureCoordinateCount: summary.TextureCoordinateCount,
                TextureCoordinateIndexCount: summary.TextureCoordinateIndexCount,
                TextureCoordinateMappingModes: summary.TextureCoordinateMappingModes,
                TextureCoordinateReferenceModes: summary.TextureCoordinateReferenceModes,
                MaterialCount: summary.MaterialCount,
                TextureBindingCount: summary.TextureBindingCount,
                MaterialLayerCount: summary.MaterialLayerCount,
                MaterialAssignmentIndexCount: summary.MaterialAssignmentIndexCount,
                MaterialMappingModes: summary.MaterialMappingModes,
                MaterialReferenceModes: summary.MaterialReferenceModes,
                ObjectConnectionCount: summary.ObjectConnectionCount,
                PropertyConnectionCount: summary.PropertyConnectionCount,
                TextureToMaterialConnectionCount: summary.TextureToMaterialConnectionCount,
                TextureToMaterialSlotNames: summary.TextureToMaterialSlotNames,
                TextureBindingFileNames: textureLinks.TextureBindingFileNames,
                CatalogMatchedTextureNames: textureLinks.CatalogMatchedTextureNames,
                CatalogMissingTextureFileNames: textureLinks.CatalogMissingTextureFileNames,
                PreviewVertexCount: summary.GeometryPreview.Vertices.Count,
                PreviewEdgeCount: summary.GeometryPreview.Edges.Count,
                Status: summary.Status);
        }
    }

    public sealed record AssetModelPreviewCoverage(
        int TotalModelRows,
        int LooseMeshRows,
        int EmbeddedMeshRows,
        int ExistingExportRows,
        int MissingExportRows,
        int MetadataAvailableRows,
        int WireframeAvailableRows,
        int RowsWithTextureCoordinates,
        int RowsWithTextureCoordinateIndices,
        int TotalTextureCoordinates,
        int TotalTextureCoordinateIndices,
        int RowsWithNormals,
        int RowsWithNormalIndices,
        int TotalNormals,
        int TotalNormalIndices,
        int RowsWithNormalMappingModes,
        int RowsWithNormalReferenceModes,
        IReadOnlyList<string> NormalMappingModes,
        IReadOnlyList<string> NormalReferenceModes,
        int RowsWithVertexColors,
        int RowsWithVertexColorIndices,
        int TotalVertexColors,
        int TotalVertexColorIndices,
        int RowsWithVertexColorMappingModes,
        int RowsWithVertexColorReferenceModes,
        IReadOnlyList<string> VertexColorMappingModes,
        IReadOnlyList<string> VertexColorReferenceModes,
        int RowsWithTextureCoordinateMappingModes,
        int RowsWithTextureCoordinateReferenceModes,
        IReadOnlyList<string> TextureCoordinateMappingModes,
        IReadOnlyList<string> TextureCoordinateReferenceModes,
        int RowsWithMaterials,
        int RowsWithTextureBindings,
        int TotalMaterialNodes,
        int TotalTextureBindingNodes,
        int RowsWithMaterialLayers,
        int RowsWithMaterialAssignmentIndices,
        int TotalMaterialLayerNodes,
        int TotalMaterialAssignmentIndices,
        int RowsWithMaterialMappingModes,
        int RowsWithMaterialReferenceModes,
        IReadOnlyList<string> MaterialMappingModes,
        IReadOnlyList<string> MaterialReferenceModes,
        int RowsWithObjectConnections,
        int RowsWithPropertyConnections,
        int RowsWithTextureToMaterialConnections,
        int RowsWithTextureToMaterialSlotNames,
        int TotalObjectConnections,
        int TotalPropertyConnections,
        int TotalTextureToMaterialConnections,
        IReadOnlyList<string> TextureToMaterialSlotNames,
        int RowsWithCatalogMatchedTextureBindingFiles,
        int RowsWithoutCatalogMatchedTextureBindingFiles,
        int RowsWithAllTextureBindingFilesCatalogMatched,
        int RowsWithAnyMissingCatalogTextureBindingFiles,
        int TotalCatalogMatchedTextureBindingFiles,
        int MetadataWithoutWireframeRows,
        int UnreadableExportRows,
        IReadOnlyList<AssetModelPreviewCoverageRow> Samples,
        IReadOnlyList<AssetModelPreviewCoverageRow> UnmatchedSamples);

    public sealed record AssetModelPreviewCoverageRow(
        string Kind,
        string Label,
        string SourceLabel,
        string ExportFileName,
        bool ExportExists,
        bool MetadataAvailable,
        bool WireframeAvailable,
        int VertexCount,
        int PolygonIndexCount,
        int NormalCount,
        int NormalIndexCount,
        IReadOnlyList<string> NormalMappingModes,
        IReadOnlyList<string> NormalReferenceModes,
        int VertexColorCount,
        int VertexColorIndexCount,
        IReadOnlyList<string> VertexColorMappingModes,
        IReadOnlyList<string> VertexColorReferenceModes,
        int TextureCoordinateCount,
        int TextureCoordinateIndexCount,
        IReadOnlyList<string> TextureCoordinateMappingModes,
        IReadOnlyList<string> TextureCoordinateReferenceModes,
        int MaterialCount,
        int TextureBindingCount,
        int MaterialLayerCount,
        int MaterialAssignmentIndexCount,
        IReadOnlyList<string> MaterialMappingModes,
        IReadOnlyList<string> MaterialReferenceModes,
        int ObjectConnectionCount,
        int PropertyConnectionCount,
        int TextureToMaterialConnectionCount,
        IReadOnlyList<string> TextureToMaterialSlotNames,
        IReadOnlyList<string> TextureBindingFileNames,
        IReadOnlyList<string> CatalogMatchedTextureNames,
        IReadOnlyList<string> CatalogMissingTextureFileNames,
        int PreviewVertexCount,
        int PreviewEdgeCount,
        string Status);
}
