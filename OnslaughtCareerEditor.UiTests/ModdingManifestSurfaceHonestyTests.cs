using System.IO;
using NUnit.Framework;

namespace OnslaughtCareerEditor.UiTests;

/// <summary>
/// The modding manifest export is a metadata-only, app-owned output: it must name
/// its own content boundary, refuse game-tree outputs through the shared guarded
/// write path, and stay hidden until a catalog actually loads.
/// </summary>
public class ModdingManifestSurfaceHonestyTests
{
    private static string ReadSource(string project, string relative)
    {
        return File.ReadAllText(Path.Combine(
            TestFixturePaths.RepoRoot,
            project,
            relative));
    }

    [Test]
    public void ExportButtonIsPresentWithAnHonestName()
    {
        string xaml = ReadSource("OnslaughtCareerEditor.WinUI", Path.Combine("Pages", "AssetLibraryPage.xaml"));

        Assert.That(xaml, Does.Contain("AssetExportModdingManifestButton"));
        Assert.That(xaml, Does.Contain("names, ids, and hashes only, no game assets"));
    }

    [Test]
    public void ManifestDocumentCarriesTheContentBoundary()
    {
        string service = ReadSource("OnslaughtCareerEditor.AppCore", "ModdingManifestService.cs");

        Assert.That(service, Does.Contain("Metadata only."));
        Assert.That(service, Does.Contain("do not pair it with anything"));
        Assert.That(service, Does.Contain("modding-manifest.v1"));
    }

    [Test]
    public void WritesGoThroughTheGuardedTransaction()
    {
        string service = ReadSource("OnslaughtCareerEditor.AppCore", "ModdingManifestService.cs");

        Assert.That(service, Does.Contain("BeginGenerated(outputPath)"));
        // The manifest never copies asset bytes: every write is the JSON document.
        Assert.That(service, Does.Not.Contain("CopyTo"));
        Assert.That(service, Does.Not.Contain("File.Copy"));
    }

    [Test]
    public void ButtonStaysHiddenUntilACatalogLoads()
    {
        string page = ReadSource("OnslaughtCareerEditor.WinUI", Path.Combine("Pages", "AssetLibraryPage.xaml.cs"));

        // Visible only on the catalog-loaded branch.
        Assert.That(page, Does.Contain("ExportModdingManifestButton.Visibility = Visibility.Visible;"));
        Assert.That(page, Does.Not.Contain("ExportModdingManifestButton.Visibility = Visibility.Visible;\r\n            CatalogFirstRunGuideBorder"));
    }

    [Test]
    public void FailureNamesWhatHappenedWithoutRawExceptions()
    {
        string service = ReadSource("OnslaughtCareerEditor.AppCore", "ModdingManifestService.cs");

        Assert.That(service, Does.Contain("The {outputName} could not be written. Nothing was changed."));
    }

    [Test]
    public void CatalogTsvExportIsPresentWithAnHonestName()
    {
        string xaml = ReadSource("OnslaughtCareerEditor.WinUI", Path.Combine("Pages", "AssetLibraryPage.xaml"));
        string service = ReadSource("OnslaughtCareerEditor.AppCore", "ModdingManifestService.cs");

        Assert.That(xaml, Does.Contain("AssetExportModdingCatalogTsvButton"));
        Assert.That(xaml, Does.Contain("Export catalog TSV"));
        Assert.That(service, Does.Contain("modding-catalog.tsv"));
        Assert.That(service, Does.Contain("catalog_id\\tdisplay_name\\tkind"));
        Assert.That(service, Does.Contain("ExportCatalogTsv"));
        Assert.That(service, Does.Contain("catalog TSV"));
        Assert.That(service, Does.Contain("could not be written. Nothing was changed."));
    }
}
