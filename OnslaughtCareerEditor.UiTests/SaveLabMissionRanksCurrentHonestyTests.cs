using System.Collections.Generic;
using System.IO;
using System.Linq;
using NUnit.Framework;
using OnslaughtCareerEditor.AppCore;
using OnslaughtCareerEditor.WinUI.Helpers;

namespace OnslaughtCareerEditor.UiTests;

/// <summary>
/// Save Lab Mission rank baseline used to let you set every listed mission
/// to S without saying what the opened save already has. The current-state
/// line paints those grades. The per-mission Current column still owns the
/// row detail.
/// </summary>
public class SaveLabMissionRanksCurrentHonestyTests
{
    [Test]
    public void UniformGradesPaintEveryListedMissionNotAPath()
    {
        SaveMissionRankRow[] rows =
        {
            Rank("S"),
            Rank("S"),
            Rank("S"),
        };

        string painted = SaveLabPageText.DescribeMissionRanksCurrent(rows);

        Assert.That(painted, Is.EqualTo("This save has every listed mission at S."));
        AssertHonesty(painted);
    }

    [Test]
    public void MixedGradesPaintCountsAndSayNoGradeNotNone()
    {
        SaveMissionRankRow[] rows =
        {
            Rank("S"),
            Rank("S"),
            Rank("A"),
            Rank("NONE"),
            Rank("NONE"),
        };

        string painted = SaveLabPageText.DescribeMissionRanksCurrent(rows);

        Assert.That(painted, Is.EqualTo("This save's missions are 2 S, 1 A and 2 No Grade."));
        Assert.That(painted, Does.Not.Contain("NONE"));
        AssertHonesty(painted);
    }

    [Test]
    public void ApproximateBitsAreNamedWithoutADump()
    {
        SaveMissionRankRow[] rows =
        {
            Rank("~S (0.95)"),
            Rank("0xDEADBEEF"),
        };

        string painted = SaveLabPageText.DescribeMissionRanksCurrent(rows);

        Assert.That(painted, Is.EqualTo("This save's missions are 1 near S and 1 unrecognized."));
        Assert.That(painted, Does.Not.Contain("0.95"));
        Assert.That(painted, Does.Not.Contain("0x"));
        Assert.That(painted, Does.Not.Contain("DEAD"));
        AssertHonesty(painted);
    }

    [Test]
    public void UnreadRowsPaintTheUnreadableSentenceWithoutAPath()
    {
        SaveMissionRankRow[] rows = { Rank("-"), Rank(string.Empty) };

        Assert.That(
            SaveLabPageText.DescribeMissionRanksCurrent(rows),
            Is.EqualTo(SaveLabPageText.MissionRanksCurrentUnreadable));
        Assert.That(SaveLabPageText.DescribeMissionRanksCurrent(null),
            Is.EqualTo(SaveLabPageText.MissionRanksCurrentUnreadable));
        AssertHonesty(SaveLabPageText.MissionRanksCurrentUnreadable);
    }

    [Test]
    public void GoldFixturePaintsThisSaveFromTheListedMissions()
    {
        IReadOnlyList<SaveMissionRankRow> rows = SaveEditorAdvancedService.LoadMissionRankRows(
            TestFixturePaths.RequireGoldSavePath(),
            out SaveEditorAdvancedService.SaveEditorAdvancedReadStatus status);

        Assert.That(status.FileWasRead, Is.True, status.Reason);
        string painted = SaveLabPageText.DescribeMissionRanksCurrent(rows);

        Assert.That(painted, Does.StartWith("This save"));
        Assert.That(painted, Does.Contain("mission"));
        Assert.That(painted.Count(ch => ch == ' '), Is.GreaterThan(3));
        AssertHonesty(painted);
        Assert.That(painted, Does.Not.Contain(TestFixturePaths.RequireGoldSavePath()));
    }

    [Test]
    public void SaveLabBindsTheCurrentRankLineAndReadsTheOpenedSave()
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

        Assert.That(xaml, Does.Contain("AutomationProperties.AutomationId=\"SaveEditorMissionRanksCurrent\""));
        Assert.That(xaml, Does.Contain("SaveEditorRankComboBox"));
        Assert.That(xaml.IndexOf("SaveEditorMissionRanksCurrent", System.StringComparison.Ordinal),
            Is.GreaterThan(xaml.IndexOf("SaveEditorRankComboBox", System.StringComparison.Ordinal)));
        Assert.That(xaml.IndexOf("SaveEditorFocusedGoodieCurrent", System.StringComparison.Ordinal),
            Is.GreaterThan(xaml.IndexOf("SaveEditorMissionRanksCurrent", System.StringComparison.Ordinal)),
            "Do not pile the rank line onto the focused-Goodie current-state line.");
        Assert.That(page, Does.Contain("PaintMissionRanksCurrent"));
        Assert.That(page, Does.Contain("SaveLabPageText.DescribeMissionRanksCurrent"));
        Assert.That(page, Does.Contain("LoadMissionRankRows"));
        Assert.That(xaml, Does.Not.Contain("CDB"));
        Assert.That(xaml, Does.Not.Contain("sidecar"));
    }

    private static SaveMissionRankRow Rank(string current) =>
        new() { CurrentRank = current };

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
