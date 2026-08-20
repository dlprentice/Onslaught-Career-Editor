using System.IO;
using NUnit.Framework;
using OnslaughtCareerEditor.AppCore;
using OnslaughtCareerEditor.WinUI.Helpers;

namespace OnslaughtCareerEditor.UiTests;

/// <summary>
/// Save Lab Mark goodies as NEW used to rewrite every listed Goodie
/// without saying what the opened save already has. The current-state
/// line paints that mix. The focused-Goodie line still owns one ID.
/// </summary>
public class SaveLabGoodiesCurrentHonestyTests
{
    [Test]
    public void UniformGoodiesPaintEveryListedNotAPath()
    {
        DisplayableGoodieCensus census = new(
            Locked: MissionScriptGoodieStateSaveCodec.DisplayableGoodieCount,
            LockedWithHint: 0,
            New: 0,
            Old: 0,
            Unrecognized: 0);

        string painted = SaveLabPageText.DescribeGoodiesCurrent(census);

        Assert.That(painted, Is.EqualTo("This save has every listed Goodie as Locked."));
        AssertHonesty(painted);
    }

    [Test]
    public void MixedGoodiesPaintCountsWithoutADump()
    {
        DisplayableGoodieCensus census = new(
            Locked: 1,
            LockedWithHint: 0,
            New: 3,
            Old: 229,
            Unrecognized: 0);

        string painted = SaveLabPageText.DescribeGoodiesCurrent(census);

        Assert.That(painted, Is.EqualTo("This save's Goodies are 1 Locked, 3 New and 229 Old."));
        AssertHonesty(painted);
    }

    [Test]
    public void UnrecognizedDwordsAreNamedWithoutAHexDump()
    {
        DisplayableGoodieCensus census = new(
            Locked: 230,
            LockedWithHint: 0,
            New: 0,
            Old: 0,
            Unrecognized: 3);

        string painted = SaveLabPageText.DescribeGoodiesCurrent(census);

        Assert.That(painted, Is.EqualTo("This save's Goodies are 230 Locked and 3 unrecognized."));
        Assert.That(painted, Does.Not.Contain("0x"));
        AssertHonesty(painted);
    }

    [Test]
    public void UnreadCensusPaintsTheUnreadableSentenceWithoutAPath()
    {
        Assert.That(
            SaveLabPageText.DescribeGoodiesCurrent(null),
            Is.EqualTo(SaveLabPageText.GoodiesCurrentUnreadable));
        Assert.That(
            SaveLabPageText.DescribeGoodiesCurrent(new DisplayableGoodieCensus(1, 0, 0, 0, 0)),
            Is.EqualTo(SaveLabPageText.GoodiesCurrentUnreadable));
        AssertHonesty(SaveLabPageText.GoodiesCurrentUnreadable);
    }

    [Test]
    public void GoldFixturePaintsTheMeasuredMixFromListedGoodies()
    {
        byte[] buffer = File.ReadAllBytes(TestFixturePaths.RequireGoldSavePath());
        Assert.That(
            MissionScriptGoodieStateSaveCodec.TryReadDisplayableCensus(buffer, out DisplayableGoodieCensus census),
            Is.True);

        string painted = SaveLabPageText.DescribeGoodiesCurrent(census);

        Assert.That(painted, Is.EqualTo("This save's Goodies are 1 Locked, 3 New and 229 Old."));
        AssertHonesty(painted);
        Assert.That(painted, Does.Not.Contain(TestFixturePaths.RequireGoldSavePath()));
    }

    [Test]
    public void SaveLabBindsTheCurrentGoodieMixNextToMarkAsNew()
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

        Assert.That(xaml, Does.Contain("AutomationProperties.AutomationId=\"SaveEditorGoodiesCurrent\""));
        Assert.That(xaml, Does.Contain("SaveEditorGoodiesAsNewToggle"));
        Assert.That(
            xaml.IndexOf("SaveEditorGoodiesCurrent", System.StringComparison.Ordinal),
            Is.GreaterThan(xaml.IndexOf("SaveEditorGoodiesAsNewToggle", System.StringComparison.Ordinal)));
        Assert.That(
            xaml.IndexOf("SaveEditorFocusedGoodieCurrent", System.StringComparison.Ordinal),
            Is.GreaterThan(xaml.IndexOf("SaveEditorGoodiesCurrent", System.StringComparison.Ordinal)),
            "Do not pile the bulk mix onto the focused-Goodie current-state line.");
        Assert.That(page, Does.Contain("PaintGoodiesCurrent"));
        Assert.That(page, Does.Contain("SaveLabPageText.DescribeGoodiesCurrent"));
        Assert.That(page, Does.Contain("TryReadDisplayableCensus"));
        Assert.That(page, Does.Not.Contain("EditorFocusedGoodieCurrentTextBlock.Text = SaveLabPageText.DescribeGoodiesCurrent"));
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
