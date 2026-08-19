using System.IO;
using NUnit.Framework;
using OnslaughtCareerEditor.WinUI.Helpers;

namespace OnslaughtCareerEditor.UiTests;

/// <summary>
/// Asset Library search used to empty the list and say nothing. Lore and Media
/// already tell the player to try another word or clear the search. This page
/// has to do the same, without describing the emptiness.
/// </summary>
public class AssetLibraryHonestyTests
{
    [Test]
    public void AnEmptySearchSaysWhatToDoNext_RatherThanDescribingTheEmptiness()
    {
        string? sentence = AssetLibraryPageText.DescribeListNote(true, "no-such-texture", 0);

        Assert.That(sentence, Is.EqualTo(AssetLibraryPageText.EmptySearchNextStep));
        Assert.That(sentence, Does.Contain("another word"));
        Assert.That(sentence, Does.Contain("clear the search"));
        Assert.That(sentence, Does.Not.Contain("matches"));
        Assert.That(sentence, Does.Not.Contain("Filtered"));
        Assert.That(sentence, Does.Not.Contain("no-such-texture"));
    }

    [Test]
    public void AHitOrIdleListDoesNotInventAStatusLine()
    {
        Assert.That(AssetLibraryPageText.DescribeListNote(true, "crate", 3), Is.Null);
        Assert.That(AssetLibraryPageText.DescribeListNote(true, "", 0), Is.Null);
        Assert.That(AssetLibraryPageText.DescribeListNote(true, "   ", 0), Is.Null);
        Assert.That(AssetLibraryPageText.DescribeListNote(false, "crate", 0), Is.Null);
    }

    [Test]
    public void ThePageUsesTheSharedSearchSentence()
    {
        string code = File.ReadAllText(Path.Combine(
            TestFixturePaths.RepoRoot, "OnslaughtCareerEditor.WinUI", "Pages", "AssetLibraryPage.xaml.cs"));
        string xaml = File.ReadAllText(Path.Combine(
            TestFixturePaths.RepoRoot, "OnslaughtCareerEditor.WinUI", "Pages", "AssetLibraryPage.xaml"));

        Assert.That(code, Does.Contain("AssetLibraryPageText.DescribeListNote"));
        Assert.That(xaml, Does.Contain("AssetListNoteTextBlock"));
        Assert.That(code, Does.Not.Contain("matches the current search"));
        Assert.That(code, Does.Not.Contain("Filtered results"));
    }

    [Test]
    public void ACatalogPathIsNamedByItsLeafNotThePath()
    {
        string path = @"C:\Users\david\exports\catalog.json";
        string summary = AssetLibraryPageText.BuildPathSummary(path);

        Assert.That(summary, Is.EqualTo("catalog.json in exports"));
        Assert.That(summary, Does.Not.Contain(path));
        Assert.That(summary, Does.Not.Contain(@":\"));
        Assert.That(summary, Does.Not.Contain("Users"));
        Assert.That(
            AssetLibraryPageText.BuildPathSummary(@"D:\generated\textures\crate.png"),
            Is.EqualTo("crate.png in textures"));
    }

    [Test]
    public void AMissingAssetPathFallsBackWithoutPrintingAPath()
    {
        Assert.That(AssetLibraryPageText.BuildPathSummary("   "), Is.EqualTo("No file selected"));
        Assert.That(AssetLibraryPageText.BuildPathSummary(null), Is.EqualTo("No file selected"));
        Assert.That(AssetLibraryPageText.BuildPathSummary("   ").ToLowerInvariant(), Does.Not.Contain("path"));
        Assert.That(AssetLibraryPageText.BuildPathSummary(@"C:\").ToLowerInvariant(), Does.Not.Contain("path"));
    }

    [Test]
    public void ThePagePaintsThePathSummaryNotTheFullPath()
    {
        string code = File.ReadAllText(Path.Combine(
            TestFixturePaths.RepoRoot, "OnslaughtCareerEditor.WinUI", "Pages", "AssetLibraryPage.xaml.cs"));

        Assert.That(code, Does.Contain("AssetLibraryPageText.BuildPathSummary"));
        Assert.That(code, Does.Not.Contain("CatalogFullPathTextBlock.Text = _snapshot.CatalogFilePath"));
        Assert.That(code, Does.Not.Contain("CatalogFullPathTextBlock.Text = path"));
        Assert.That(code, Does.Not.Contain("SelectedExportPathTextBlock.Text = texture.ExportPath"));
        Assert.That(code, Does.Not.Contain("SelectedExportPathTextBlock.Text = mesh.ExportPath"));
    }
}
