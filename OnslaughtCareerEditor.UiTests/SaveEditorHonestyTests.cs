using System;
using System.IO;
using System.Linq;
using NUnit.Framework;
using Onslaught___Career_Editor;

namespace OnslaughtCareerEditor.UiTests;

/// <summary>
/// The smaller 2026-07-26 audit items: places where the Save Editor stated something untrue about the
/// file, the guard, or the effect of a click.
///
/// D9  — two bare catch {} presented hard-coded seeds as values read from the save.
/// D11 — the two write buttons share one output path and replace each other silently.
/// D12 — input rejection carried no diagnosis.
/// Plus the output-safety string, which claimed a guard wider than the one that exists.
/// </summary>
public class SaveEditorHonestyTests
{
    private static string GoldSavePath => TestFixturePaths.RequireGoldSavePath();

    // ----------------------------------------------------------------- D9

    [Test]
    public void D9_CategoryKillRowsFromAGenuineSave_AreMarkedAsRead()
    {
        // Non-vacuity control for the test below: a real save must come back known, or "unknown when
        // unread" would pass simply by never being known.
        var rows = SaveEditorAdvancedService
            .LoadCategoryKillRows(GoldSavePath, out var status)
            .ToArray();

        Assert.That(status.FileWasRead, Is.True, status.Reason);
        Assert.That(rows.All(row => row.CurrentValueKnown), Is.True);
        Assert.That(rows.Select(row => row.CurrentValueLabel), Has.None.EqualTo("-"));
    }

    [Test]
    public void D9_CategoryKillRowsWithNoReadableSave_DoNotPresentSeedsAsSaveValues()
    {
        string missing = Path.Combine(Path.GetTempPath(), $"absent-{Guid.NewGuid():N}.bes");

        var rows = SaveEditorAdvancedService
            .LoadCategoryKillRows(missing, out var status)
            .ToArray();

        Assert.That(status.FileWasRead, Is.False);
        Assert.That(status.Reason, Is.Not.Null.And.Not.Empty,
            "A read that did not happen must say why. This used to be a bare catch {}.");
        Assert.That(rows.All(row => !row.CurrentValueKnown), Is.True);
        Assert.That(
            rows.Select(row => row.CurrentValueLabel).Distinct().ToArray(),
            Is.EqualTo(new[] { "-" }),
            "The Current column rendered the hard-coded seeds 100/100/25/40/20 as though the save had " +
            "said so. It must render nothing instead.");

        Assert.That(
            SaveEditorAdvancedService.HasMixedKnownCategoryCounts(rows),
            Is.False,
            "Unread values must never drive the keep decision.");
        Assert.That(
            SaveEditorAdvancedService.BuildKillSeedSummary(rows),
            Does.Contain("not read"),
            "The summary must disclose that no save was read.");
    }

    [Test]
    public void D9_GoldFixtureHasMixedCounts_SoKeepIsTheDefaultTheUiOffers()
    {
        var rows = SaveEditorAdvancedService.LoadCategoryKillRows(GoldSavePath).ToArray();

        Assert.That(
            SaveEditorAdvancedService.HasMixedKnownCategoryCounts(rows),
            Is.True,
            "The tracked baseline has mixed per-category counts, which is the case where writing one " +
            "value over all five destroys real data.");
        Assert.That(
            SaveEditorAdvancedService.BuildKillSeedSummary(rows),
            Does.Contain("Keep the kill counts this save already has"),
            "The disclosure must name the control that is switched on for the user.");
    }

    [Test]
    public void D9_MissionRankRowsWithAWrongLengthFile_SayWhyInsteadOfLookingUnselected()
    {
        string tempDir = Path.Combine(Path.GetTempPath(), $"onslaught-shortsave-{Guid.NewGuid():N}");
        Directory.CreateDirectory(tempDir);
        try
        {
            // Start from the retail baseline and truncate a copy; never synthesise a save.
            string truncated = Path.Combine(tempDir, "truncated.bes");
            byte[] gold = File.ReadAllBytes(GoldSavePath);
            File.WriteAllBytes(truncated, gold.AsSpan(0, gold.Length - 32).ToArray());

            var rows = SaveEditorAdvancedService.LoadMissionRankRows(truncated, out var status).ToArray();

            Assert.That(status.FileWasRead, Is.False);
            Assert.That(status.Reason, Does.Contain("bytes"),
                "A wrong-length file must be distinguishable from 'no file selected'.");
            Assert.That(rows.All(row => row.CurrentRank == "-"), Is.True);
        }
        finally
        {
            Directory.Delete(tempDir, recursive: true);
        }
    }

    // ---------------------------------------------------------------- D11

    [Test]
    public void D11_TheOtherWriteActionOverwritingThisOne_IsDisclosed()
    {
        string path = Path.Combine(Path.GetTempPath(), "career_patched.bes");

        string? loss = SaveEditorService.DescribeWriteCompositionLoss(
            SaveEditorService.SaveEditorWriteKind.FocusedGoodieState,
            path,
            SaveEditorService.SaveEditorWriteKind.FullPatch,
            path);

        Assert.That(loss, Is.Not.Null,
            "Patching sections after writing a focused Goodie to the same output re-reads the input, " +
            "so the Goodie edit is lost. That must not happen behind a green success bar.");
        Assert.That(loss, Does.Contain("focused Goodie"));
    }

    [Test]
    public void D11_NothingIsClaimedWhenNothingWouldBeLost()
    {
        string path = Path.Combine(Path.GetTempPath(), "career_patched.bes");
        string other = Path.Combine(Path.GetTempPath(), "career_patched_2.bes");

        Assert.That(
            SaveEditorService.DescribeWriteCompositionLoss(
                null, null, SaveEditorService.SaveEditorWriteKind.FullPatch, path),
            Is.Null,
            "A first write has nothing to overwrite.");

        Assert.That(
            SaveEditorService.DescribeWriteCompositionLoss(
                SaveEditorService.SaveEditorWriteKind.FullPatch,
                path,
                SaveEditorService.SaveEditorWriteKind.FullPatch,
                path),
            Is.Null,
            "Re-running the same action genuinely just redoes itself from the same input.");

        Assert.That(
            SaveEditorService.DescribeWriteCompositionLoss(
                SaveEditorService.SaveEditorWriteKind.FocusedGoodieState,
                path,
                SaveEditorService.SaveEditorWriteKind.FullPatch,
                other),
            Is.Null,
            "A different destination loses nothing, and a warning there would be noise.");
    }

    // ---------------------------------------------------------------- D12

    [Test]
    public void D12_AValidCareerSaveIsNotRejected()
    {
        // The tracked fixture is stored as .bin; the editor requires the retail .bes extension, so copy
        // the real bytes rather than relaxing the check.
        string tempDir = Path.Combine(Path.GetTempPath(), $"onslaught-accept-{Guid.NewGuid():N}");
        Directory.CreateDirectory(tempDir);
        try
        {
            string valid = Path.Combine(tempDir, "career.bes");
            File.Copy(GoldSavePath, valid);
            Assert.That(SaveEditorService.DescribeCareerSaveInputRejection(valid), Is.Null);
        }
        finally
        {
            Directory.Delete(tempDir, recursive: true);
        }
    }

    [Test]
    public void D12_EachRejectionReasonIsDistinguishable()
    {
        string tempDir = Path.Combine(Path.GetTempPath(), $"onslaught-reject-{Guid.NewGuid():N}");
        Directory.CreateDirectory(tempDir);
        try
        {
            byte[] gold = File.ReadAllBytes(GoldSavePath);

            string missing = Path.Combine(tempDir, "absent.bes");
            string wrongLength = Path.Combine(tempDir, "short.bes");
            File.WriteAllBytes(wrongLength, gold.AsSpan(0, gold.Length - 4).ToArray());

            string wrongVersion = Path.Combine(tempDir, "badversion.bes");
            byte[] mutated = (byte[])gold.Clone();
            mutated[0] ^= 0xFF;
            File.WriteAllBytes(wrongVersion, mutated);

            string optionsLike = Path.Combine(tempDir, "defaultoptions.bea");
            File.WriteAllBytes(optionsLike, gold);

            string?[] reasons =
            {
                SaveEditorService.DescribeCareerSaveInputRejection(missing),
                SaveEditorService.DescribeCareerSaveInputRejection(wrongLength),
                SaveEditorService.DescribeCareerSaveInputRejection(wrongVersion),
                SaveEditorService.DescribeCareerSaveInputRejection(optionsLike),
                SaveEditorService.DescribeCareerSaveInputRejection("   ")
            };

            Assert.That(reasons, Has.None.Null, "Every rejected input must carry a reason.");
            Assert.That(
                reasons.Distinct().Count(),
                Is.EqualTo(reasons.Length),
                "The four failure modes were collapsed into one string, so the user was told the input " +
                "was invalid and never told which check failed. They must now differ.");

            Assert.That(reasons[1], Does.Contain(BesFilePatcher.EXPECTED_FILE_SIZE.ToString("N0")));
            Assert.That(reasons[2], Does.Contain("version word"));
            Assert.That(reasons[3], Does.Contain("options"));
        }
        finally
        {
            Directory.Delete(tempDir, recursive: true);
        }
    }

    // --------------------------------------------- output-safety claim

    [Test]
    public void OutputSafetyHint_DoesNotClaimAGuardWiderThanTheOneThatExists()
    {
        string hint = ReadSafetyHintLiteral();

        // RejectOutputInGameTree rejects a destination only when an ancestor directory holds BOTH
        // BEA.exe and data/. The user's Documents and LocalAppData save roots match neither, and the
        // app itself offers files from both, so a sentence promising "every game folder" was false.
        Assert.That(hint, Does.Not.Contain("every game folder"));
        Assert.That(hint, Does.Contain("BEA.exe"),
            "The hint must name what the guard actually keys on.");
        Assert.That(
            hint,
            Does.Contain("Documents").And.Contain("AppData"),
            "The hint must say which locations are NOT protected, because the app offers files from them.");
    }

    private static string ReadSafetyHintLiteral()
    {
        string source = Path.Combine(
            TestFixturePaths.RepoRoot,
            "OnslaughtCareerEditor.WinUI",
            "Pages",
            "SavesPage.xaml.cs");
        Assert.That(File.Exists(source), Is.True, $"Missing {source}");

        string text = File.ReadAllText(source);
        const string marker = "Output path must end in .bes";
        int start = text.IndexOf(marker, StringComparison.Ordinal);
        Assert.That(start, Is.GreaterThanOrEqualTo(0), "The output-safety hint literal was not found.");

        // The literal is a multi-part concatenation; take the enclosing statement.
        int end = text.IndexOf(';', start);
        return text.Substring(start, end - start);
    }
}
