namespace Onslaught___Career_Editor
{
    public sealed class AssetCatalogReadabilityService
    {
        public const int DefaultSampleLimit = 12;

        public AssetCatalogReadability Build(AssetCatalogSnapshot snapshot, int sampleLimit = DefaultSampleLimit)
        {
            sampleLimit = Math.Clamp(sampleLimit, 0, 100);

            IReadOnlyList<AssetTextureReadabilityRow> textureRows = snapshot.Textures
                .Select(BuildTextureRow)
                .ToList();

            IReadOnlyList<AssetModelReadabilityRow> modelRows = snapshot.LooseMeshes
                .Select(mesh => BuildModelRow("loose mesh", mesh.DisplayName, mesh.CanonicalRef, mesh.ExportFileName, mesh.ExportExists, mesh.ModelSummary))
                .Concat(snapshot.EmbeddedMeshes.Select(mesh => BuildModelRow("embedded mesh", mesh.DisplayName, mesh.SourceArchive, mesh.ExportFileName, mesh.ExportExists, mesh.ModelSummary)))
                .ToList();

            return new AssetCatalogReadability(
                TextureRows: textureRows.Count,
                TextureExportRows: textureRows.Count(static row => row.ExportExists),
                TextureReadablePngRows: textureRows.Count(static row => row.ReadablePng),
                TextureMissingExportRows: textureRows.Count(static row => !row.ExportExists),
                TextureUnreadableExportRows: textureRows.Count(static row => row.ExportExists && !row.ReadablePng),
                TotalModelRows: modelRows.Count,
                ModelExportRows: modelRows.Count(static row => row.ExportExists),
                ModelMetadataAvailableRows: modelRows.Count(static row => row.MetadataAvailable),
                ModelWireframeAvailableRows: modelRows.Count(static row => row.WireframeAvailable),
                ModelMissingExportRows: modelRows.Count(static row => !row.ExportExists),
                ModelUnreadableExportRows: modelRows.Count(static row => row.ExportExists && !row.MetadataAvailable),
                TextureSamples: textureRows.Take(sampleLimit).ToList(),
                ModelSamples: modelRows.Take(sampleLimit).ToList());
        }

        private static AssetTextureReadabilityRow BuildTextureRow(AssetTextureItem item)
        {
            PngHeaderInfo header = PngHeaderReader.Read(item.ExportPath);
            return new AssetTextureReadabilityRow(
                Kind: "texture",
                Label: string.IsNullOrWhiteSpace(item.DisplayName) ? "Texture" : item.DisplayName,
                SourceLabel: string.IsNullOrWhiteSpace(item.SourceGroup) ? "Textures" : item.SourceGroup,
                ExportFileName: item.ExportFileName,
                ExportExists: item.ExportExists,
                ReadablePng: header.Readable,
                Width: header.Width,
                Height: header.Height,
                ByteSize: header.ByteSize,
                Status: header.Status);
        }

        private static AssetModelReadabilityRow BuildModelRow(
            string kind,
            string label,
            string sourceLabel,
            string exportFileName,
            bool exportExists,
            AssetModelSummary summary)
        {
            return new AssetModelReadabilityRow(
                Kind: kind,
                Label: string.IsNullOrWhiteSpace(label) ? "Model" : label,
                SourceLabel: string.IsNullOrWhiteSpace(sourceLabel) ? "Models" : sourceLabel,
                ExportFileName: exportFileName,
                ExportExists: exportExists,
                MetadataAvailable: summary.MetadataAvailable,
                WireframeAvailable: summary.GeometryPreview.Edges.Count > 0,
                ByteSize: summary.ByteSize,
                GeometryCount: summary.GeometryCount,
                ModelCount: summary.ModelCount,
                MaterialCount: summary.MaterialCount,
                TextureBindingCount: summary.TextureBindingCount,
                PreviewVertexCount: summary.GeometryPreview.Vertices.Count,
                PreviewEdgeCount: summary.GeometryPreview.Edges.Count,
                Status: summary.Status);
        }

    }

    public sealed record AssetCatalogReadability(
        int TextureRows,
        int TextureExportRows,
        int TextureReadablePngRows,
        int TextureMissingExportRows,
        int TextureUnreadableExportRows,
        int TotalModelRows,
        int ModelExportRows,
        int ModelMetadataAvailableRows,
        int ModelWireframeAvailableRows,
        int ModelMissingExportRows,
        int ModelUnreadableExportRows,
        IReadOnlyList<AssetTextureReadabilityRow> TextureSamples,
        IReadOnlyList<AssetModelReadabilityRow> ModelSamples);

    public sealed record AssetTextureReadabilityRow(
        string Kind,
        string Label,
        string SourceLabel,
        string ExportFileName,
        bool ExportExists,
        bool ReadablePng,
        int? Width,
        int? Height,
        long ByteSize,
        string Status);

    public sealed record AssetModelReadabilityRow(
        string Kind,
        string Label,
        string SourceLabel,
        string ExportFileName,
        bool ExportExists,
        bool MetadataAvailable,
        bool WireframeAvailable,
        long ByteSize,
        int GeometryCount,
        int ModelCount,
        int MaterialCount,
        int TextureBindingCount,
        int PreviewVertexCount,
        int PreviewEdgeCount,
        string Status);
}
