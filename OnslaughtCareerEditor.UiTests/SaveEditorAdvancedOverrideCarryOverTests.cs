using System.Collections.Generic;
using System.IO;
using System.Linq;
using OnslaughtCareerEditor.WinUI.Helpers;
using OnslaughtCareerEditor.AppCore;

namespace OnslaughtCareerEditor.UiTests;

/// <summary>
/// The advanced Save Editor surface rebuilds its rows from the selected input save on every input path
/// change, which includes a single keystroke in the input path box. Before this contract existed, that
/// rebuild discarded every configured per-mission rank and per-category kill override with no warning
/// and reported nothing. These tests hold the carry-over that makes that loss impossible.
/// </summary>
public class SaveEditorAdvancedOverrideCarryOverTests
{
    private static string GoldSavePath => TestFixturePaths.RequireGoldSavePath();

    [Test]
    public void MissionRankOverrides_SurviveAReloadOfTheSameSave()
    {
        SaveMissionRankRow[] configured = SaveEditorAdvancedService.LoadMissionRankRows(GoldSavePath).ToArray();
        Assert.That(configured.Length, Is.GreaterThan(3), "The fixture must expose several mission rows.");
        configured[0].SelectedRank = "E";
        configured[2].SelectedRank = "NONE";
        Assert.That(SaveEditorAdvancedService.CountMissionRankOverrides(configured), Is.EqualTo(2));

        SaveMissionRankRow[] reloaded = SaveEditorAdvancedService.LoadMissionRankRows(GoldSavePath).ToArray();
        Assert.That(
            SaveEditorAdvancedService.CountMissionRankOverrides(reloaded),
            Is.Zero,
            "A freshly read row set must start with no overrides, or this test proves nothing.");

        int carried = SaveEditorAdvancedOverrideCarryOver.ApplyMissionRankOverrides(configured, reloaded);

        Assert.That(carried, Is.EqualTo(2));
        Assert.That(reloaded[0].SelectedRank, Is.EqualTo("E"));
        Assert.That(reloaded[2].SelectedRank, Is.EqualTo("NONE"));
        // The sentinel is deliberately no longer spelled "Keep": a row left on it is omitted from
        // LevelRanks and therefore takes the mission rank baseline, which is not "keeping" anything
        // unless the baseline itself is set to keep. The row now says what it does.
        Assert.That(
            reloaded[1].SelectedRank,
            Is.EqualTo(SaveMissionRankRow.UseBaselineChoice),
            "Untouched rows must stay on the use-baseline sentinel.");
        Assert.That(
            reloaded[1].RankChoices,
            Does.Not.Contain("Keep"),
            "The word Keep must not be offered on a per-mission row: only the baseline can keep.");
        Assert.That(
            SaveEditorAdvancedService.CountMissionRankOverrides(reloaded),
            Is.EqualTo(2),
            "Reloading the advanced surface must not drop the user's mission rank overrides.");
    }

    [Test]
    public void CategoryKillOverrides_SurviveAReloadAndKeepTheUserValue()
    {
        SaveCategoryKillRow[] configured = SaveEditorAdvancedService.LoadCategoryKillRows(GoldSavePath).ToArray();
        Assert.That(configured.Length, Is.EqualTo(5));
        configured[BesFilePatcher.KILL_MECHS].OverrideEnabled = true;
        configured[BesFilePatcher.KILL_MECHS].OverrideValue = 4242;

        SaveCategoryKillRow[] reloaded = SaveEditorAdvancedService.LoadCategoryKillRows(GoldSavePath).ToArray();
        Assert.That(
            SaveEditorAdvancedService.CountCategoryKillOverrides(reloaded),
            Is.Zero,
            "A freshly read row set must start with no overrides, or this test proves nothing.");

        int carried = SaveEditorAdvancedOverrideCarryOver.ApplyCategoryKillOverrides(configured, reloaded);

        Assert.That(carried, Is.EqualTo(1));
        SaveCategoryKillRow mechs = reloaded.Single(row => row.CategoryIndex == BesFilePatcher.KILL_MECHS);
        Assert.That(mechs.OverrideEnabled, Is.True);
        Assert.That(mechs.OverrideValue, Is.EqualTo(4242));
        Assert.That(
            reloaded.Count(row => row.OverrideEnabled),
            Is.EqualTo(1),
            "Carrying one override must not enable the categories the user left alone.");
    }

    [Test]
    public void CarryOver_RereadsCurrentValuesFromTheNewlySelectedSave()
    {
        // Switching input files must refresh what the file says while keeping what the user said.
        SaveCategoryKillRow[] configured = SaveEditorAdvancedService.LoadCategoryKillRows(GoldSavePath).ToArray();
        configured[BesFilePatcher.KILL_AIRCRAFT].OverrideEnabled = true;
        configured[BesFilePatcher.KILL_AIRCRAFT].OverrideValue = 7;

        string tempDir = Path.Combine(Path.GetTempPath(), $"onslaught-carryover-{System.Guid.NewGuid():N}");
        Directory.CreateDirectory(tempDir);
        try
        {
            string otherSave = Path.Combine(tempDir, "other.bes");
            byte[] buf = File.ReadAllBytes(GoldSavePath);
            System.Buffers.Binary.BinaryPrimitives.WriteUInt32LittleEndian(buf.AsSpan(0x23F6, 4), 55u);
            File.WriteAllBytes(otherSave, buf);

            SaveCategoryKillRow[] reloaded = SaveEditorAdvancedService.LoadCategoryKillRows(otherSave).ToArray();
            SaveEditorAdvancedOverrideCarryOver.ApplyCategoryKillOverrides(configured, reloaded);

            SaveCategoryKillRow aircraft = reloaded.Single(row => row.CategoryIndex == BesFilePatcher.KILL_AIRCRAFT);
            Assert.That(aircraft.CurrentValue, Is.EqualTo(55), "Current value must come from the newly selected save.");
            Assert.That(aircraft.OverrideValue, Is.EqualTo(7), "The user's override value must survive the file change.");
            Assert.That(aircraft.OverrideEnabled, Is.True);
        }
        finally
        {
            try { Directory.Delete(tempDir, recursive: true); } catch (IOException) { }
        }
    }

    [Test]
    public void GlobalKillValue_IsOnlyReseededWhileItIsStillAutoSeeded()
    {
        Assert.That(SaveEditorAdvancedOverrideCarryOver.ShouldReseedGlobalKillValue(true, true), Is.True);
        Assert.That(
            SaveEditorAdvancedOverrideCarryOver.ShouldReseedGlobalKillValue(true, false),
            Is.False,
            "A kill value the user typed must not be silently replaced by a value re-seeded from the file.");
        Assert.That(SaveEditorAdvancedOverrideCarryOver.ShouldReseedGlobalKillValue(false, true), Is.False);
    }

    [Test]
    public void CarryOver_IsReportedRatherThanPerformedSilently()
    {
        Assert.That(SaveEditorAdvancedOverrideCarryOver.DescribeCarryOver(0, 0), Is.Null);
        Assert.That(SaveEditorAdvancedOverrideCarryOver.DescribeCarryOver(1, 0), Does.Contain("1 mission rank override"));
        Assert.That(SaveEditorAdvancedOverrideCarryOver.DescribeCarryOver(0, 3), Does.Contain("3 category kill overrides"));
        string both = SaveEditorAdvancedOverrideCarryOver.DescribeCarryOver(2, 1)!;
        Assert.That(both, Does.Contain("2 mission rank overrides"));
        Assert.That(both, Does.Contain("1 category kill override"));
    }

    [Test]
    public void CarryOver_IgnoresRanksTheRowCannotOffer()
    {
        var previous = new List<SaveMissionRankRow>
        {
            new() { NodeIndexZeroBased = 0, NodeLabel = "01", MissionLabel = "level100", SelectedRank = "Z" },
            new() { NodeIndexZeroBased = 99, NodeLabel = "99", MissionLabel = "absent", SelectedRank = "S" }
        };
        SaveMissionRankRow[] reloaded = SaveEditorAdvancedService.LoadMissionRankRows(GoldSavePath).ToArray();

        int carried = SaveEditorAdvancedOverrideCarryOver.ApplyMissionRankOverrides(previous, reloaded);

        Assert.That(carried, Is.Zero, "An unknown rank and an absent node index must not be carried across.");
        Assert.That(SaveEditorAdvancedService.CountMissionRankOverrides(reloaded), Is.Zero);
    }
}
