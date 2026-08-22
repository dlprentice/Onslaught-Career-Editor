using System.IO;
using NUnit.Framework;

namespace OnslaughtCareerEditor.UiTests;

/// <summary>
/// Census candidates in the Patch Lab consume the census lane's TSV shape only:
/// they cannot be staged, they never write, and a miss or empty filter says what
/// to do next.
/// </summary>
public class PatchLabCensusHonestyTests
{
    private static string ReadWinUiFile(string name)
    {
        return File.ReadAllText(Path.Combine(
            TestFixturePaths.RepoRoot,
            "OnslaughtCareerEditor.WinUI",
            name));
    }

    [Test]
    public void CensusSurfaceNamesTheTsvAndRefusesStaging()
    {
        string xaml = ReadWinUiFile(Path.Combine("Pages", "BinaryPatchesPage.xaml"));
        string page = ReadWinUiFile(Path.Combine("Pages", "BinaryPatchesPage.xaml.cs"));
        string model = ReadWinUiFile(Path.Combine("Models", "PatchCensusRowModel.cs"));

        Assert.That(xaml, Does.Contain("PatchLabCensusExpander"));
        Assert.That(xaml, Does.Contain("not product patches"));
        Assert.That(xaml, Does.Not.Contain("PatchCensusStage"));
        Assert.That(page, Does.Contain("PatchSurfaceCensusReader.Load()"));
        Assert.That(model, Does.Contain("Census candidate, not a product patch"));
        Assert.That(model, Does.Not.Contain("CanBeStaged"));
    }

    [Test]
    public void EmptyFilterAndMissingTsvSayWhatToDoNext()
    {
        string page = ReadWinUiFile(Path.Combine("Pages", "BinaryPatchesPage.xaml.cs"));

        Assert.That(page, Does.Contain("No census candidate matches that filter. Try another word, or clear the filter."));
        Assert.That(page, Does.Contain("Type a filter to list more."));
    }

    [Test]
    public void ReaderDoesNotWriteTheTsv()
    {
        string reader = File.ReadAllText(Path.Combine(
            TestFixturePaths.RepoRoot,
            "OnslaughtCareerEditor.AppCore",
            "PatchSurfaceCensusReader.cs"));

        Assert.That(reader, Does.Contain("RequiredColumns"));
        Assert.That(reader, Does.Contain("cheapest_verification"));
        Assert.That(reader, Does.Not.Contain("File.Write"));
        Assert.That(reader, Does.Not.Contain("File.Copy"));
        Assert.That(reader, Does.Not.Contain("BeginGenerated"));
    }
}
