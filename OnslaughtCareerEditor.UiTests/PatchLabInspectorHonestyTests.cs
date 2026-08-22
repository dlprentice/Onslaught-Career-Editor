using System.IO;
using NUnit.Framework;

namespace OnslaughtCareerEditor.UiTests;

/// <summary>
/// The Patch Lab inspector shows every catalog row with its bytes, evidence, and
/// risk; staging must route through the existing guarded selection model and the
/// page must never leak raw catalog keys into user-facing failure text.
/// </summary>
public class PatchLabInspectorHonestyTests
{
    private static string ReadWinUiFile(string name)
    {
        return File.ReadAllText(Path.Combine(
            TestFixturePaths.RepoRoot,
            "OnslaughtCareerEditor.WinUI",
            name));
    }

    [Test]
    public void InspectorNamesBytesEvidenceAndRisk()
    {
        string xaml = ReadWinUiFile(Path.Combine("Pages", "BinaryPatchesPage.xaml"));
        string model = ReadWinUiFile(Path.Combine("Models", "PatchLabRowModel.cs"));

        Assert.That(xaml, Does.Contain("PatchLabInspectorExpander"));
        Assert.That(xaml, Does.Contain("Original bytes"));
        Assert.That(xaml, Does.Contain("Patched bytes"));
        Assert.That(xaml, Does.Contain("{Binding RiskSummary}"));
        Assert.That(model, Does.Contain("\"Proof level: "));
        Assert.That(model, Does.Contain("Rollback: "));
    }

    [Test]
    public void StagingGoesThroughTheExistingSelectionModel()
    {
        string page = ReadWinUiFile(Path.Combine("Pages", "BinaryPatchesPage.xaml.cs"));

        // The inspector's stage handler routes through the shared selection helper
        // and nothing else; extract its body and pin what it may call.
        int start = page.IndexOf("private void PatchLabStageButton_Click", System.StringComparison.Ordinal);
        int end = page.IndexOf("private bool IsPatchRowSelected", System.StringComparison.Ordinal);
        Assert.That(start, Is.GreaterThan(0), "inspector stage handler missing");
        Assert.That(end, Is.GreaterThan(start), "inspector stage handler region missing");

        string handlerBody = page.Substring(start, end - start);
        Assert.That(handlerBody, Does.Contain("SetVisiblePatchRowSelected("));
        Assert.That(handlerBody, Does.Not.Contain("ApplyPatchesToFile"));
        Assert.That(handlerBody, Does.Not.Contain("File."));
        Assert.That(handlerBody, Does.Not.Contain("Process.Start"));
    }

    [Test]
    public void HiddenCompanionRowsCannotBeStagedDirectly()
    {
        string model = ReadWinUiFile(Path.Combine("Models", "PatchLabRowModel.cs"));

        Assert.That(model, Does.Contain("Hidden companion row - applied automatically with its visible row"));
        Assert.That(model, Does.Contain("CanBeStaged = !row.IsHiddenCompanion"));
    }

    [Test]
    public void AnEmptyFilterResultSaysWhatToDoNext()
    {
        string page = ReadWinUiFile(Path.Combine("Pages", "BinaryPatchesPage.xaml.cs"));

        Assert.That(page, Does.Contain("No patch row matches that filter. Try another word, or clear the filter."));
    }
}
