namespace Onslaught___Career_Editor
{
    public sealed class GoodiePreviewCoverageService
    {
        private const int DefaultSampleLimit = 12;

        public GoodiePreviewCoverage Build(
            AssetCatalogSnapshot snapshot,
            int sampleLimit = DefaultSampleLimit)
        {
            if (sampleLimit < 0)
            {
                sampleLimit = 0;
            }

            List<GoodiePreviewCoverageRow> rows = snapshot.Goodies
                .Select(goodie => BuildRow(goodie, snapshot))
                .ToList();

            return new GoodiePreviewCoverage(
                TotalGoodieRows: rows.Count,
                SourceGridVisibleRows: rows.Count(static row => row.IsSourceGridVisible),
                SourceGridHiddenRows: rows.Count(static row => !row.IsSourceGridVisible),
                TextureBearingRows: rows.Count(static row => row.HasTexture),
                TextureMatchedRows: rows.Count(static row => row.TextureMatched),
                TexturePreviewReadyRows: rows.Count(static row => row.TexturePreviewReady),
                ModelBearingRows: rows.Count(static row => row.HasModel),
                ModelMatchedRows: rows.Count(static row => row.ModelMatched),
                ModelExportReadyRows: rows.Count(static row => row.ModelExportReady),
                ModelWireframeReadyRows: rows.Count(static row => row.ModelWireframeReady),
                VideoRows: rows.Count(static row => row.HasVideo),
                VideoCatalogLinkedRows: rows.Count(static row => row.VideoCatalogLinked),
                RowsWithoutLocalPreview: rows.Count(static row => !row.LocalPreviewReady),
                Samples: rows
                    .OrderBy(static row => row.LocalPreviewReady)
                    .ThenBy(static row => row.IsSourceGridVisible)
                    .ThenBy(static row => row.Index)
                    .Take(sampleLimit)
                    .ToList());
        }

        private static GoodiePreviewCoverageRow BuildRow(
            AssetGoodieItem goodie,
            AssetCatalogSnapshot snapshot)
        {
            AssetTextureItem? texture = FindTexture(snapshot, goodie.PrimaryTextureRef);
            AssetLooseMeshItem? mesh = FindLooseMesh(snapshot, goodie.PrimaryMeshRef);
            bool texturePreviewReady = texture?.ExportExists == true;
            bool modelExportReady = mesh?.ExportExists == true;
            bool modelWireframeReady = mesh?.ModelSummary.GeometryPreview.Available == true;
            bool videoLinked = goodie.HasVideo;
            bool localPreviewReady = texturePreviewReady || modelWireframeReady || videoLinked;
            string previewKind = modelWireframeReady
                ? "model wireframe"
                : texturePreviewReady
                    ? "texture"
                    : videoLinked
                        ? "media handoff"
                        : "none";

            return new GoodiePreviewCoverageRow(
                Index: goodie.Index,
                ContentKind: goodie.ContentKind,
                IsSourceGridVisible: goodie.IsSourceGridVisible,
                HasTexture: goodie.HasTexture,
                TextureMatched: texture != null,
                TexturePreviewReady: texturePreviewReady,
                HasModel: goodie.HasModel,
                ModelMatched: mesh != null,
                ModelExportReady: modelExportReady,
                ModelWireframeReady: modelWireframeReady,
                HasVideo: !string.IsNullOrWhiteSpace(goodie.VideoSequenceId),
                VideoCatalogLinked: videoLinked,
                LocalPreviewReady: localPreviewReady,
                PreviewKind: previewKind,
                Status: BuildStatus(goodie, texture, mesh, previewKind));
        }

        private static string BuildStatus(
            AssetGoodieItem goodie,
            AssetTextureItem? texture,
            AssetLooseMeshItem? mesh,
            string previewKind)
        {
            if (!goodie.IsSourceGridVisible)
            {
                return "Shipped resource is not exposed by the known Goodies wall mapping.";
            }

            if (previewKind != "none")
            {
                return $"Preview ready via {previewKind}.";
            }

            if (goodie.HasModel && mesh == null)
            {
                return "Model Goodie has no matching loose mesh catalog row.";
            }

            if (goodie.HasTexture && texture == null)
            {
                return "Texture Goodie has no matching texture catalog row.";
            }

            return "No local preview route is available from the current catalog.";
        }

        private static AssetTextureItem? FindTexture(AssetCatalogSnapshot snapshot, string canonicalRef)
        {
            string normalized = NormalizeAssetRef(canonicalRef);
            if (string.IsNullOrWhiteSpace(normalized))
            {
                return null;
            }

            return snapshot.Textures.FirstOrDefault(texture =>
                NormalizeAssetRef(texture.CanonicalRef) == normalized ||
                NormalizeAssetRef(texture.CanonicalRef).EndsWith(normalized, StringComparison.OrdinalIgnoreCase));
        }

        private static AssetLooseMeshItem? FindLooseMesh(AssetCatalogSnapshot snapshot, string canonicalRef)
        {
            string normalized = NormalizeAssetRef(canonicalRef);
            if (string.IsNullOrWhiteSpace(normalized))
            {
                return null;
            }

            return snapshot.LooseMeshes.FirstOrDefault(mesh =>
                NormalizeAssetRef(mesh.CanonicalRef) == normalized ||
                NormalizeAssetRef(mesh.CanonicalRef).EndsWith(normalized, StringComparison.OrdinalIgnoreCase));
        }

        private static string NormalizeAssetRef(string? value)
        {
            return string.IsNullOrWhiteSpace(value)
                ? string.Empty
                : value.Replace('\\', '/').Trim().ToLowerInvariant();
        }
    }

    public sealed record GoodiePreviewCoverage(
        int TotalGoodieRows,
        int SourceGridVisibleRows,
        int SourceGridHiddenRows,
        int TextureBearingRows,
        int TextureMatchedRows,
        int TexturePreviewReadyRows,
        int ModelBearingRows,
        int ModelMatchedRows,
        int ModelExportReadyRows,
        int ModelWireframeReadyRows,
        int VideoRows,
        int VideoCatalogLinkedRows,
        int RowsWithoutLocalPreview,
        IReadOnlyList<GoodiePreviewCoverageRow> Samples);

    public sealed record GoodiePreviewCoverageRow(
        int Index,
        string ContentKind,
        bool IsSourceGridVisible,
        bool HasTexture,
        bool TextureMatched,
        bool TexturePreviewReady,
        bool HasModel,
        bool ModelMatched,
        bool ModelExportReady,
        bool ModelWireframeReady,
        bool HasVideo,
        bool VideoCatalogLinked,
        bool LocalPreviewReady,
        string PreviewKind,
        string Status);
}
