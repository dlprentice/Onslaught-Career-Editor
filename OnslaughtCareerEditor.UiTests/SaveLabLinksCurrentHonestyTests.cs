using System.IO;
using NUnit.Framework;
using OnslaughtCareerEditor.AppCore;
using OnslaughtCareerEditor.WinUI.Helpers;

namespace OnslaughtCareerEditor.UiTests;

/// <summary>
/// Save Lab Patch links used to rewrite every still-locked used link
/// without saying what the opened save already has. The current-state
/// line paints that mix. Unused slots are not counted.
/// </summary>
public class SaveLabLinksCurrentHonestyTests
{
    [Test]
    public void UniformLinksPaintEveryListedNotAPath()
    {
        DisplayableLinkCensus census = new(
            StillLocked: 12,
            Complete: 0,
            Broken: 0,
            Unrecognized: 0);

        string painted = SaveLabPageText.DescribeLinksCurrent(census);

        Assert.That(painted, Is.EqualTo("This save has every listed link still locked."));
        AssertHonesty(painted);
    }

    [Test]
    public void MixedLinksPaintCountsWithoutADump()
    {
        DisplayableLinkCensus census = new(
            StillLocked: 0,
            Complete: 42,
            Broken: 21,
            Unrecognized: 0);

        string painted = SaveLabPageText.DescribeLinksCurrent(census);

        Assert.That(painted, Is.EqualTo("This save's links are 42 complete and 21 broken."));
        AssertHonesty(painted);
    }

    [Test]
    public void UnrecognizedDwordsAreNamedWithoutAHexDump()
    {
        DisplayableLinkCensus census = new(
            StillLocked: 10,
            Complete: 0,
            Broken: 0,
            Unrecognized: 3);

        string painted = SaveLabPageText.DescribeLinksCurrent(census);

        Assert.That(painted, Is.EqualTo("This save's links are 10 still locked and 3 unrecognized."));
        Assert.That(painted, Does.Not.Contain("0x"));
        AssertHonesty(painted);
    }

    [Test]
    public void UnreadCensusPaintsTheUnreadableSentenceWithoutAPath()
    {
        Assert.That(
            SaveLabPageText.DescribeLinksCurrent(null),
            Is.EqualTo(SaveLabPageText.LinksCurrentUnreadable));
        Assert.That(
            SaveLabPageText.DescribeLinksCurrent(new DisplayableLinkCensus(0, 0, 0, 0)),
            Is.EqualTo("This save has no listed links."));
        AssertHonesty(SaveLabPageText.LinksCurrentUnreadable);
        AssertHonesty("This save has no listed links.");
    }

    [Test]
    public void GoldFixturePaintsTheMeasuredMixFromUsedLinks()
    {
        byte[] buffer = File.ReadAllBytes(TestFixturePaths.RequireGoldSavePath());
        Assert.That(
            BesFilePatcher.TryReadDisplayableLinkCensus(buffer, out DisplayableLinkCensus census),
            Is.True);

        string painted = SaveLabPageText.DescribeLinksCurrent(census);

        Assert.That(painted, Is.EqualTo("This save's links are 42 complete and 21 broken."));
        AssertHonesty(painted);
        Assert.That(painted, Does.Not.Contain(TestFixturePaths.RequireGoldSavePath()));
    }

    [Test]
    public void SaveLabBindsTheCurrentLinkMixNextToPatchLinks()
    {
        string xaml = File.ReadAllText(Path.Combine(
            TestFixturePaths.RepoRoot,
            "OnslaughtCareerEditor.WinUI",
            "Pages",
            "SavesPage.xaml"));
        string page = File.ReadAllText(Path.Combine(
            TestFixturePaths.RepoRoot,
            "OnslaughtCareerEditor.WinUI",
            "Pages",
            "SavesPage.SaveEditorAdvanced.cs"));

        Assert.That(xaml, Does.Contain("AutomationProperties.AutomationId=\"SaveEditorLinksCurrent\""));
        Assert.That(xaml, Does.Contain("SaveEditorPatchLinksCheckBox"));
        Assert.That(
            xaml.IndexOf("SaveEditorLinksCurrent", System.StringComparison.Ordinal),
            Is.GreaterThan(xaml.IndexOf("SaveEditorPatchLinksCheckBox", System.StringComparison.Ordinal)));
        Assert.That(
            xaml.IndexOf("SaveEditorLinksCurrent", System.StringComparison.Ordinal),
            Is.GreaterThan(xaml.IndexOf("SaveEditorGoodiesCurrent", System.StringComparison.Ordinal)),
            "Do not pile the link mix onto the current Goodie mix line.");
        Assert.That(
            xaml.IndexOf("SaveEditorLinksCurrent", System.StringComparison.Ordinal),
            Is.GreaterThan(xaml.IndexOf("SaveEditorMissionRanksCurrent", System.StringComparison.Ordinal)),
            "Do not pile the link mix onto the current mission-grade line.");
        Assert.That(
            xaml.IndexOf("SaveEditorFocusedGoodieCurrent", System.StringComparison.Ordinal),
            Is.LessThan(xaml.IndexOf("SaveEditorLinksCurrent", System.StringComparison.Ordinal)),
            "Do not pile the link mix onto the focused-Goodie current-state line.");
        Assert.That(page, Does.Contain("PaintLinksCurrent"));
        Assert.That(page, Does.Contain("SaveLabPageText.DescribeLinksCurrent"));
        Assert.That(page, Does.Contain("TryReadDisplayableLinkCensus"));
        Assert.That(page, Does.Not.Contain("EditorGoodiesCurrentTextBlock.Text = SaveLabPageText.DescribeLinksCurrent"));
        Assert.That(page, Does.Not.Contain("EditorMissionRanksCurrentTextBlock.Text = SaveLabPageText.DescribeLinksCurrent"));
        Assert.That(page, Does.Not.Contain("EditorFocusedGoodieCurrentTextBlock.Text = SaveLabPageText.DescribeLinksCurrent"));
        Assert.That(xaml, Does.Not.Contain("CDB"));
        Assert.That(xaml, Does.Not.Contain("sidecar"));
    }

    private static void AssertHonesty(string painted)
    {
        Assert.That(painted, Does.Not.Contain(@":\"));
        Assert.That(painted, Does.Not.Contain("verified"));
        Assert.That(painted, Does.Not.Contain("app-owned"));
        Assert.That(painted, Does.Not.Contain("exception"));
        Assert.That(painted, Does.Not.Contain("sidecar"));
        Assert.That(painted, Does.Not.Contain("CDB"));
    }
}
