using System.IO;
using NUnit.Framework;

namespace OnslaughtCareerEditor.UiTests;

/// <summary>
/// Census candidates in the Patch Lab are research experiments staged into a safe
/// copy only: the surface never writes an installed game, a miss or empty filter
/// says what to do next, and every row names what staging would change.
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
    public void CensusSurfaceNamesTheTsvAndStagesIntoSafeCopiesOnly()
    {
        string xaml = ReadWinUiFile(Path.Combine("Pages", "BinaryPatchesPage.xaml"));
        string page = ReadWinUiFile(Path.Combine("Pages", "BinaryPatchesPage.xaml.cs"));
        string model = ReadWinUiFile(Path.Combine("Models", "PatchCensusRowModel.cs"));

        Assert.That(xaml, Does.Contain("PatchLabCensusExpander"));
        Assert.That(xaml, Does.Contain("staged into a safe copy only"));
        Assert.That(xaml, Does.Contain("PatchLabCensusStageButton"));
        Assert.That(xaml, Does.Contain("PatchLabCensusUndoButton"));
        Assert.Multiple(() =>
        {
            Assert.That(xaml, Does.Not.Contain("PatchCensusStage_"));
            Assert.That(page, Does.Contain("PatchSurfaceCensusReader.Load()"));
            Assert.That(model, Does.Contain("not a product patch; stages into a safe copy only"));
            Assert.That(model, Does.Not.Contain("CanBeStaged"));
        });
    }

    [Test]
    public void StagingCopyNeverTargetsTheInstalledGame()
    {
        string page = ReadWinUiFile(Path.Combine("Pages", "BinaryPatchesPage.xaml.cs"));
        string xaml = ReadWinUiFile(Path.Combine("Pages", "BinaryPatchesPage.xaml"));

        Assert.That(xaml, Does.Contain("never the installed game"));
        Assert.That(page, Does.Contain("written into the safe copy only, never the installed game"));
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
        Assert.Multiple(() =>
        {
            Assert.That(reader, Does.Not.Contain("File.Write"));
            Assert.That(reader, Does.Not.Contain("File.Copy"));
            Assert.That(reader, Does.Not.Contain("BeginGenerated"));
        });
    }

    [Test]
    public void StagingServiceRefusesInstalledGameShapesStructurally()
    {
        string engine = File.ReadAllText(Path.Combine(
            TestFixturePaths.RepoRoot,
            "OnslaughtCareerEditor.AppCore",
            "BinaryPatchEngine.cs"));
        string service = File.ReadAllText(Path.Combine(
            TestFixturePaths.RepoRoot,
            "OnslaughtCareerEditor.AppCore",
            "PatchCensusStagingService.cs"));

        // The structural refusal is shared with the product apply path; the census
        // stager never obtains an InstalledGameWriteAuthorization at all.
        Assert.That(service, Does.Contain("CensusStagingTargetHasForbiddenInstallShape"));
        Assert.That(engine, Does.Contain("internal static bool CensusStagingTargetHasForbiddenInstallShape"));
        Assert.Multiple(() =>
        {
            Assert.That(service, Does.Contain("never written to an installed game"));
            Assert.That(service, Does.Not.Contain("AuthorizeInstalledGameWrite("));
        });
    }

    [Test]
    public void StagingWritesAreAtomicWithVerifiedBackupBeforeFirstWrite()
    {
        string service = File.ReadAllText(Path.Combine(
            TestFixturePaths.RepoRoot,
            "OnslaughtCareerEditor.AppCore",
            "PatchCensusStagingService.cs"));

        Assert.That(service, Does.Contain("PublishCensusStagingBytesAtomically"));
        Assert.That(service, Does.Contain("pre-experiment backup snapshot"));
        Assert.That(service, Does.Contain("on-disk verification"));
        Assert.That(service, Does.Contain("census-staged.v1"));
    }

    [Test]
    public void StagedExperimentsShowAsNamedReceiptsNotJustACount()
    {
        // The receipt surface: what the copy holds and what Undo will reverse is
        // visible per row ("VA: effect"), not summarized as a bare count.
        string xaml = ReadWinUiFile(Path.Combine("Pages", "BinaryPatchesPage.xaml"));
        string page = ReadWinUiFile(Path.Combine("Pages", "BinaryPatchesPage.xaml.cs"));

        Assert.Multiple(() =>
        {
            Assert.That(xaml, Does.Contain("PatchLabCensusStagedList"));
            Assert.That(
                xaml,
                Does.Contain("Census experiments currently staged in this safe copy"),
                "the list must be named for assistive technology, not just painted");
            Assert.That(page, Does.Contain("manifest.Entries.Select(entry => $\"{entry.Va}: {entry.Effect}\")"));
            Assert.That(page, Does.Contain("result.AppliedSummaries.Select(s => \"  • \" + s)"));
        });
    }
}
