using System.IO;
using NUnit.Framework;
using OnslaughtCareerEditor.AppCore;

namespace OnslaughtCareerEditor.UiTests;

/// <summary>
/// Asset Library used to say a missing export was "not available at the
/// recorded local path." Name the file. The full path stays off the page.
/// </summary>
public class AssetExportHonestyTests
{
    [Test]
    public void AMissingModelExportNamesTheFileNotAPath()
    {
        string missing = Path.Combine(Path.GetTempPath(), Guid.NewGuid().ToString("N"), "gone.fbx");
        AssetModelSummary summary = FbxModelSummaryReader.Read(missing);

        Assert.That(summary.Status, Is.EqualTo(FbxModelSummaryReader.ExportMissing));
        Assert.That(summary.Status, Does.Contain("model export"));
        Assert.That(summary.Status.ToLowerInvariant(), Does.Not.Contain("path"));
        Assert.That(summary.Status, Does.Not.Contain(":\\"));
    }

    [Test]
    public void AMissingTextureExportNamesTheFileNotAPath()
    {
        string missing = Path.Combine(Path.GetTempPath(), Guid.NewGuid().ToString("N"), "gone.png");
        PngHeaderInfo header = PngHeaderReader.Read(missing);

        Assert.That(header.Status, Is.EqualTo(PngHeaderReader.ExportMissing));
        Assert.That(header.Status, Does.Contain("texture export"));
        Assert.That(header.Status.ToLowerInvariant(), Does.Not.Contain("path"));
        Assert.That(header.Status, Does.Not.Contain(":\\"));
    }

    [Test]
    public void ThePageAndReadersDropTheRecordedPathSentence()
    {
        string page = File.ReadAllText(Path.Combine(
            TestFixturePaths.RepoRoot, "OnslaughtCareerEditor.WinUI", "Pages", "AssetLibraryPage.xaml.cs"));
        string fbx = File.ReadAllText(Path.Combine(
            TestFixturePaths.RepoRoot, "OnslaughtCareerEditor.AppCore", "FbxModelSummaryReader.cs"));
        string png = File.ReadAllText(Path.Combine(
            TestFixturePaths.RepoRoot, "OnslaughtCareerEditor.AppCore", "PngHeaderReader.cs"));
        string catalog = File.ReadAllText(Path.Combine(
            TestFixturePaths.RepoRoot, "OnslaughtCareerEditor.AppCore", "AssetCatalogService.cs"));
        string readability = File.ReadAllText(Path.Combine(
            TestFixturePaths.RepoRoot, "OnslaughtCareerEditor.AppCore", "AssetCatalogReadabilityService.cs"));

        Assert.That(page, Does.Contain("PngHeaderReader.ExportMissing"));
        Assert.That(fbx, Does.Contain("ExportMissing"));
        Assert.That(png, Does.Contain("ExportMissing"));
        Assert.That(catalog, Does.Contain("FbxModelSummaryReader.ExportMissing"));
        Assert.That(readability, Does.Contain("PngHeaderReader.ExportMissing"));
        Assert.That(page + fbx + png + catalog + readability, Does.Not.Contain("recorded local path"));
    }

    [Test]
    public void ARefusedTextureExportNamesTheFileNotATrustedRoot()
    {
        string readability = File.ReadAllText(Path.Combine(
            TestFixturePaths.RepoRoot, "OnslaughtCareerEditor.AppCore", "AssetCatalogReadabilityService.cs"));
        string sentence = AssetCatalogReadabilityService.ExportCouldNotBeOpened;

        Assert.That(readability, Does.Contain("ExportCouldNotBeOpened"));
        Assert.That(readability, Does.Not.Contain("trusted-root"));
        Assert.That(readability, Does.Not.Contain("file-identity validation"));
        Assert.That(sentence, Is.EqualTo("That texture export could not be opened."));
        Assert.That(sentence, Does.Contain("texture export"));
        Assert.That(sentence.ToLowerInvariant(), Does.Not.Contain("trusted"));
        Assert.That(sentence.ToLowerInvariant(), Does.Not.Contain("root"));
        Assert.That(sentence.ToLowerInvariant(), Does.Not.Contain("path"));
        Assert.That(sentence.ToLowerInvariant(), Does.Not.Contain("validation"));
        Assert.That(sentence, Does.Not.Contain(":\\"));
        Assert.That(sentence, Does.Not.Contain("/"));
    }
}
