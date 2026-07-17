namespace Onslaught___Career_Editor
{
    public static class AssetCatalogLoadStatusText
    {
        public static string BuildMissingCatalogStatus(string? attemptedPath, string? detectedGameDirectory)
        {
            string attempted = string.IsNullOrWhiteSpace(attemptedPath)
                ? string.Empty
                : " The selected path does not contain catalog.json.";
            const string baseline = "No generated catalog is loaded. This app reads an existing generated local asset catalog only.";

            if (!string.IsNullOrWhiteSpace(attemptedPath) &&
                AppConfig.InspectGameDirectory(attemptedPath).Status == GameDirectoryStatus.FullInstall)
            {
                return $"{baseline}{attempted} That is the game install, not an export catalog. Asset Library is a catalog viewer, not an extractor. Choose an existing export folder containing asset_catalog/catalog.json. PNG/FBX export is separate tooling and currently requires the legacy extractor's local runtime dependencies.";
            }

            if (string.IsNullOrWhiteSpace(detectedGameDirectory))
            {
                return $"{baseline}{attempted} Asset Library is a viewer, not an extractor. Choose an existing export folder containing asset_catalog/catalog.json; PNG/FBX export currently requires the legacy extractor's local runtime dependencies.";
            }

            return $"Battle Engine Aquila install detected, but no export catalog is loaded.{attempted} Asset Library is a viewer, not an extractor. Choose an existing export folder containing asset_catalog/catalog.json; the game install itself is not a catalog.";
        }
    }
}
