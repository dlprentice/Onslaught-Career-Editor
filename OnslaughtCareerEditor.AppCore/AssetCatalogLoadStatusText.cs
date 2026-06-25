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
                return $"{baseline}{attempted} That is the game install, not the generated export folder. Use the install as source for the external extractor, then load the separate generated export folder. The generated export folder should contain asset_catalog/catalog.json; the game install folder itself is not a catalog.";
            }

            if (string.IsNullOrWhiteSpace(detectedGameDirectory))
            {
                return $"{baseline}{attempted} Generate a catalog from your own game install outside the app, then choose the generated export folder that contains asset_catalog/catalog.json.";
            }

            return $"Battle Engine Aquila install detected, but no generated catalog is loaded.{attempted} Choose the generated export folder that contains asset_catalog/catalog.json; the game install folder itself is not a catalog.";
        }
    }
}
