using System.IO;
using NUnit.Framework;

namespace OnslaughtCareerEditor.UiTests;

public class ModProjectManifestRevalidationSurfaceTests
{
    private static string ReadWinUiFile(params string[] parts)
    {
        return File.ReadAllText(Path.Combine(
            TestFixturePaths.RepoRoot,
            "OnslaughtCareerEditor.WinUI",
            Path.Combine(parts)));
    }

    [Test]
    public void AssetLibraryExposesARealManifestRevalidationReviewAndReceiptSurface()
    {
        string xaml = ReadWinUiFile("Pages", "AssetLibraryPage.xaml");

        Assert.Multiple(() =>
        {
            Assert.That(xaml, Does.Contain("Manifest revalidation / drift review"));
            Assert.That(xaml, Does.Contain("AutomationProperties.AutomationId=\"AssetManifestReviewInputFileTextBox\""));
            Assert.That(xaml, Does.Contain("AutomationProperties.AutomationId=\"AssetReviewManifestButton\""));
            Assert.That(xaml, Does.Contain("AutomationProperties.AutomationId=\"AssetManifestReviewSummary\""));
            Assert.That(xaml, Does.Contain("AutomationProperties.AutomationId=\"AssetManifestReviewProvenance\""));
            Assert.That(xaml, Does.Contain("AutomationProperties.AutomationId=\"AssetManifestReviewItemsList\""));
            Assert.That(xaml, Does.Contain("AutomationProperties.AutomationId=\"AssetManifestReviewOutputFileTextBox\""));
            Assert.That(xaml, Does.Contain("AutomationProperties.AutomationId=\"AssetManifestReviewIncludeTsvCheckBox\""));
            Assert.That(xaml, Does.Contain("AutomationProperties.AutomationId=\"AssetExportManifestReviewReceiptButton\""));
            Assert.That(xaml, Does.Contain("AutomationProperties.AutomationId=\"AssetManifestReviewStatus\""));
            Assert.That(xaml, Does.Contain("metadata-only review receipt"));
            Assert.That(xaml, Does.Contain("copies no game, catalog, or asset bytes"));
        });
    }

    [Test]
    public void AssetLibraryUsesAppCoreReviewAndGuardedReceiptExport()
    {
        string code = ReadWinUiFile("Pages", "AssetLibraryPage.xaml.cs");

        Assert.Multiple(() =>
        {
            Assert.That(code, Does.Contain("ModProjectManifestRevalidationService.Review"));
            Assert.That(code, Does.Contain("ModProjectManifestRevalidationService.Export"));
            Assert.That(code, Does.Contain("UnchangedCount"));
            Assert.That(code, Does.Contain("CatalogDriftedCount"));
            Assert.That(code, Does.Contain("MissingCount"));
            Assert.That(code, Does.Contain("AmbiguousOrDuplicateCount"));
            Assert.That(code, Does.Contain("LocalExportMissingCount"));
            Assert.That(code, Does.Contain("LocalHashMismatchCount"));
            Assert.That(code, Does.Not.Contain("File.Copy("));
        });
    }
}
