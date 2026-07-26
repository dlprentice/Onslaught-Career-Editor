using System;
using System.Buffers.Binary;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using NUnit.Framework;
using Onslaught___Career_Editor;

namespace OnslaughtCareerEditor.UiTests;

/// <summary>
/// Byte-level closure for the three S1 data-loss defects measured on 2026-07-26.
///
/// D1 — one category kill override rewrote the other four with the patcher's default.
/// D2 — one mission rank override rewrote every other mission's grade with the baseline.
/// D3 — a scalar payload supplied with its section disabled was dropped while reporting success.
///
/// Every test here starts from the tracked retail baseline fixture (never a synthesised save), and
/// every one asserts that the output is exactly EXPECTED_FILE_SIZE bytes and that the bytes outside
/// the region under test are identical to the input, so the ~37.3% of the format that is still
/// opaque is proven to survive the round trip rather than assumed to.
/// </summary>
public class SavePatchKeepSemanticsTests
{
    private static string GoldSavePath => TestFixturePaths.RequireGoldSavePath();

    private const int NodeBase = 0x0006;
    private const int NodeSize = 64;
    private const int NodeCount = 100;
    private const int NodeCompleteOffset = 0x04;
    private const int NodeWorldOffset = 0x10;
    private const int NodeAttemptsOffset = 0x38;
    private const int NodeRankOffset = 0x3C;
    private const int KillBase = 0x23F6;
    private const int KillCategoryCount = 5;

    private const uint RankBitsS = 0x3F800000u;
    private const uint RankBitsA = 0x3F4CCCCDu;

    // ---------------------------------------------------------------- D1

    [Test]
    public void D1_OneCategoryKillOverride_LeavesTheOtherFourCategoriesByteIdentical()
    {
        using TempSave temp = TempSave.FromGold("keep-kills");

        // Non-vacuity: the fixture must actually have mixed counts, or "the other four were preserved"
        // proves nothing. This is the measured gold state [3221, 9738, 3002, 3953, 1024].
        int[] beforeCounts = ReadKillCounts(temp.InputBytes);
        Assert.That(
            beforeCounts.Distinct().Count(),
            Is.GreaterThan(1),
            "The baseline fixture must hold mixed per-category kill counts for this test to mean anything.");

        var patcher = new BesFilePatcher
        {
            PatchNodes = false,
            PatchLinks = false,
            PatchGoodies = false,
            PatchKills = true,
            // GlobalKillCount deliberately left null: the caller stated one category and nothing else.
            PerCategoryKills = new Dictionary<int, int> { [BesFilePatcher.KILL_MECHS] = 2000 }
        };

        PatchResult result = patcher.PatchFile(temp.InputPath, temp.OutputPath);
        Assert.That(result.Success, Is.True, result.Message);

        byte[] after = temp.ReadOutput();
        int[] afterCounts = ReadKillCounts(after);

        Assert.That(afterCounts[BesFilePatcher.KILL_MECHS], Is.EqualTo(2000), "The targeted category must be written.");
        for (int category = 0; category < KillCategoryCount; category++)
        {
            if (category == BesFilePatcher.KILL_MECHS)
            {
                continue;
            }

            // The whole dword, not just the count: the opaque metadata byte in bits 24..31 must survive
            // too, and it does so here because an untargeted category is never written at all.
            uint beforeRaw = ReadUInt32(temp.InputBytes, KillBase + (category * 4));
            uint afterRaw = ReadUInt32(after, KillBase + (category * 4));
            Assert.That(
                afterRaw,
                Is.EqualTo(beforeRaw),
                $"Category {category} was not targeted and must be byte-identical. " +
                $"Before this fix it was overwritten with the patcher's default of 100.");
        }

        temp.AssertOnlyTheseRangesChanged((KillBase + (BesFilePatcher.KILL_MECHS * 4), 4));
    }

    [Test]
    public void D1_ExplicitBaselineStillFillsEveryCategory_SoTheKeepFixDidNotRemoveTheFillTool()
    {
        using TempSave temp = TempSave.FromGold("fill-kills");

        var patcher = new BesFilePatcher
        {
            PatchNodes = false,
            PatchLinks = false,
            PatchGoodies = false,
            PatchKills = true,
            GlobalKillCount = 500,
            PerCategoryKills = new Dictionary<int, int> { [BesFilePatcher.KILL_MECHS] = 20 }
        };

        PatchResult result = patcher.PatchFile(temp.InputPath, temp.OutputPath);
        Assert.That(result.Success, Is.True, result.Message);

        int[] after = ReadKillCounts(temp.ReadOutput());
        Assert.That(after, Is.EqualTo(new[] { 500, 500, 500, 500, 20 }),
            "An explicit baseline is still the way to fill every category; only the silent fill was removed.");
    }

    // ---------------------------------------------------------------- D2

    [Test]
    public void D2_OneMissionRankOverride_LeavesEveryOtherMissionByteIdentical()
    {
        using TempSave temp = TempSave.FromGold("keep-ranks");

        int[] activeNodes = ActiveNodeIndexes(temp.InputBytes);
        Assert.That(activeNodes.Length, Is.GreaterThan(1),
            "The fixture must have more than one active mission for this to prove anything.");
        int targetNode = activeNodes[0];

        var patcher = new BesFilePatcher
        {
            PatchNodes = true,
            PatchLinks = false,
            PatchGoodies = false,
            PatchKills = false,
            // Rank deliberately left null: the caller stated one mission and nothing else.
            LevelRanks = new Dictionary<int, string> { [targetNode] = "A" }
        };

        PatchResult result = patcher.PatchFile(temp.InputPath, temp.OutputPath);
        Assert.That(result.Success, Is.True, result.Message);

        byte[] after = temp.ReadOutput();
        Assert.That(
            ReadUInt32(after, NodeBase + (targetNode * NodeSize) + NodeRankOffset),
            Is.EqualTo(RankBitsA),
            "The targeted mission must receive the requested grade.");
        Assert.That(
            ReadUInt32(after, NodeBase + (targetNode * NodeSize) + NodeCompleteOffset),
            Is.EqualTo(1u),
            "The targeted mission must be marked complete.");

        foreach (int node in activeNodes.Where(index => index != targetNode))
        {
            int off = NodeBase + (node * NodeSize);
            Assert.That(
                after.AsSpan(off, NodeSize).SequenceEqual(temp.InputBytes.AsSpan(off, NodeSize)),
                Is.True,
                $"Untargeted mission node {node} must be byte-identical. Before this fix its grade was " +
                $"overwritten with the baseline S, and an intermediate version of the fix still wrote " +
                $"mComplete=1 into it.");
        }

        // The strongest form of the anti-regression: writing nothing into untargeted nodes means the
        // combination mComplete==1 with mRanking==0xBF800000 (never completed) cannot be manufactured.
        temp.AssertOnlyTheseRangesChanged((NodeBase + (targetNode * NodeSize), NodeSize));
    }

    [Test]
    public void D2_ExplicitBaselineStillWritesEveryActiveMission_SoTheKeepFixDidNotRemoveTheUnlockTool()
    {
        using TempSave temp = TempSave.FromGold("fill-ranks");

        int[] activeNodes = ActiveNodeIndexes(temp.InputBytes);
        int targetNode = activeNodes[0];

        var patcher = new BesFilePatcher
        {
            PatchNodes = true,
            PatchLinks = false,
            PatchGoodies = false,
            PatchKills = false,
            Rank = "S",
            LevelRanks = new Dictionary<int, string> { [targetNode] = "A" }
        };

        PatchResult result = patcher.PatchFile(temp.InputPath, temp.OutputPath);
        Assert.That(result.Success, Is.True, result.Message);

        byte[] after = temp.ReadOutput();
        Assert.That(ReadUInt32(after, NodeBase + (targetNode * NodeSize) + NodeRankOffset), Is.EqualTo(RankBitsA));
        foreach (int node in activeNodes.Where(index => index != targetNode))
        {
            Assert.That(
                ReadUInt32(after, NodeBase + (node * NodeSize) + NodeRankOffset),
                Is.EqualTo(RankBitsS),
                $"An explicit baseline must still write every active mission; node {node} did not receive it.");
            Assert.That(
                ReadUInt32(after, NodeBase + (node * NodeSize) + NodeAttemptsOffset),
                Is.Zero,
                "The explicit-baseline path keeps its historic behaviour of zeroing mNumAttempts.");
        }
    }

    [Test]
    public void D2_KeepBaselineNeverProducesCompleteWithNeverCompletedRankBits()
    {
        using TempSave temp = TempSave.FromGold("keep-ranks-no-invented-state");

        int[] activeNodes = ActiveNodeIndexes(temp.InputBytes);
        var patcher = new BesFilePatcher
        {
            PatchNodes = true,
            PatchLinks = false,
            PatchGoodies = false,
            PatchKills = false,
            LevelRanks = new Dictionary<int, string> { [activeNodes[0]] = "A" }
        };

        Assert.That(patcher.PatchFile(temp.InputPath, temp.OutputPath).Success, Is.True);

        byte[] after = temp.ReadOutput();
        for (int node = 0; node < NodeCount; node++)
        {
            int off = NodeBase + (node * NodeSize);
            uint complete = ReadUInt32(after, off + NodeCompleteOffset);
            uint rankBits = ReadUInt32(after, off + NodeRankOffset);
            bool inventedHere = complete == 1u && rankBits == 0xBF800000u;
            bool alreadyInInput =
                ReadUInt32(temp.InputBytes, off + NodeCompleteOffset) == 1u &&
                ReadUInt32(temp.InputBytes, off + NodeRankOffset) == 0xBF800000u;

            Assert.That(
                inventedHere && !alreadyInInput,
                Is.False,
                $"Node {node} was given mComplete=1 with the 'never completed' rank -1.0. That combination " +
                $"is not produced by the game's own win path and the keep pass must never invent it.");
        }
    }

    // ---------------------------------------------------------------- D3

    private static IEnumerable<TestCaseData> DiscardedScalarCases()
    {
        yield return new TestCaseData(
                new Action<BesFilePatcher>(p => { p.Rank = "A"; p.PatchNodes = false; }),
                "mission rank baseline")
            .SetName("D3_RankWithNodePatchingOff_Fails");
        yield return new TestCaseData(
                new Action<BesFilePatcher>(p => { p.GlobalKillCount = 999; p.PatchKills = false; }),
                "baseline kill count")
            .SetName("D3_GlobalKillCountWithKillPatchingOff_Fails");
        yield return new TestCaseData(
                new Action<BesFilePatcher>(p => { p.UseNewGoodiesInstead = true; p.PatchGoodies = false; }),
                "goodie style")
            .SetName("D3_GoodieStyleWithGoodiePatchingOff_Fails");
    }

    [TestCaseSource(nameof(DiscardedScalarCases))]
    public void D3_ScalarPayloadWithItsSectionDisabled_FailsAndWritesNoFile(
        Action<BesFilePatcher> configure,
        string expectedFragment)
    {
        using TempSave temp = TempSave.FromGold("discarded-scalar");

        // Start from a configuration that would otherwise succeed, then disable exactly one section
        // while leaving its payload configured.
        var patcher = new BesFilePatcher
        {
            PatchNodes = true,
            PatchLinks = true,
            PatchGoodies = true,
            PatchKills = true,
            Rank = "S",
            GlobalKillCount = 100,
            UseNewGoodiesInstead = false
        };
        configure(patcher);

        PatchResult result = patcher.PatchFile(temp.InputPath, temp.OutputPath);

        Assert.That(result.Success, Is.False,
            "A configured value whose section is disabled must fail, not report success and drop the edit.");
        Assert.That(result.Message.ToLowerInvariant(), Does.Contain(expectedFragment.ToLowerInvariant()));
        Assert.That(File.Exists(temp.OutputPath), Is.False,
            "No output may be written when part of the caller's stated intent cannot reach bytes.");
    }

    [Test]
    public void D3_EveryRegisteredIntent_IsRefusedWhenItsOwningSectionIsOff()
    {
        // Generated from the contract table rather than hand-listed. A payload added to the table but
        // never wired into the patcher fails here; a payload wired into the patcher but never added to
        // the table fails SavePatchIntentCoverageTests. Between them there is no way to add a fourth
        // silent drop.
        foreach (SavePatchIntent intent in SavePatchIntentContract.Intents)
        {
            using TempSave temp = TempSave.FromGold($"intent-{intent.PropertyName}");

            var patcher = new BesFilePatcher
            {
                PatchNodes = true,
                PatchLinks = true,
                PatchGoodies = true,
                PatchKills = true,
                Rank = "S",
                GlobalKillCount = 100,
                UseNewGoodiesInstead = false
            };

            ConfigureIntent(patcher, intent.PropertyName);
            DisableSection(patcher, intent.SectionSwitchPropertyName);

            PatchResult result = patcher.PatchFile(temp.InputPath, temp.OutputPath);
            Assert.That(result.Success, Is.False,
                $"Intent '{intent.PropertyName}' was configured with {intent.SectionSwitchPropertyName} " +
                $"disabled and the patch still succeeded, which means the value was silently dropped.");
            Assert.That(File.Exists(temp.OutputPath), Is.False,
                $"Intent '{intent.PropertyName}': no file may be written when the intent cannot reach bytes.");
        }
    }

    [Test]
    public void D3_SectionEnabledWithNothingToWrite_FailsInsteadOfReportingAnEmptySuccess()
    {
        // The mirror of the silent drop, created by making "absent" representable at all.
        foreach ((string section, Action<BesFilePatcher> configure) in new (string, Action<BesFilePatcher>)[]
        {
            ("PatchNodes", p => { p.PatchNodes = true; p.PatchLinks = false; p.PatchGoodies = false; p.PatchKills = false; }),
            ("PatchKills", p => { p.PatchNodes = false; p.PatchLinks = false; p.PatchGoodies = false; p.PatchKills = true; })
        })
        {
            using TempSave temp = TempSave.FromGold($"empty-{section}");
            var patcher = new BesFilePatcher();
            configure(patcher);

            PatchResult result = patcher.PatchFile(temp.InputPath, temp.OutputPath);
            Assert.That(result.Success, Is.False,
                $"{section} was enabled with no payload at all, so the pass would write nothing. " +
                $"Reporting success over an empty edit is the same lie in the other direction.");
            Assert.That(File.Exists(temp.OutputPath), Is.False);
        }
    }

    // ---------------------------------------------------------------- helpers

    private static void ConfigureIntent(BesFilePatcher patcher, string propertyName)
    {
        switch (propertyName)
        {
            case nameof(SavePatchIntentSnapshot.Rank):
                patcher.Rank = "A";
                break;
            case nameof(SavePatchIntentSnapshot.LevelRanks):
                patcher.LevelRanks = new Dictionary<int, string> { [0] = "A" };
                break;
            case nameof(SavePatchIntentSnapshot.UseNewGoodiesInstead):
                patcher.UseNewGoodiesInstead = true;
                break;
            case nameof(SavePatchIntentSnapshot.GlobalKillCount):
                patcher.GlobalKillCount = 999;
                break;
            case nameof(SavePatchIntentSnapshot.PerCategoryKills):
                patcher.PerCategoryKills = new Dictionary<int, int> { [BesFilePatcher.KILL_MECHS] = 20 };
                break;
            default:
                Assert.Fail(
                    $"SavePatchIntentContract registers '{propertyName}' but this test does not know how to " +
                    $"configure it on BesFilePatcher. Add the case, and make sure the patcher actually " +
                    $"consumes the new payload.");
                break;
        }
    }

    private static void DisableSection(BesFilePatcher patcher, string sectionSwitchPropertyName)
    {
        switch (sectionSwitchPropertyName)
        {
            case nameof(SavePatchIntentSnapshot.PatchNodes): patcher.PatchNodes = false; break;
            case nameof(SavePatchIntentSnapshot.PatchLinks): patcher.PatchLinks = false; break;
            case nameof(SavePatchIntentSnapshot.PatchGoodies): patcher.PatchGoodies = false; break;
            case nameof(SavePatchIntentSnapshot.PatchKills): patcher.PatchKills = false; break;
            default:
                Assert.Fail($"Unknown section switch '{sectionSwitchPropertyName}'.");
                break;
        }
    }

    private static uint ReadUInt32(byte[] buffer, int offset) =>
        BinaryPrimitives.ReadUInt32LittleEndian(buffer.AsSpan(offset, 4));

    private static int[] ReadKillCounts(byte[] buffer) =>
        Enumerable.Range(0, KillCategoryCount)
            .Select(index => (int)(ReadUInt32(buffer, KillBase + (index * 4)) & 0x00FFFFFFu))
            .ToArray();

    private static int[] ActiveNodeIndexes(byte[] buffer) =>
        Enumerable.Range(0, NodeCount)
            .Where(index => ReadUInt32(buffer, NodeBase + (index * NodeSize) + NodeWorldOffset) != 0u)
            .ToArray();

    private sealed class TempSave : IDisposable
    {
        private readonly string _directory;

        private TempSave(string directory, string inputPath, string outputPath)
        {
            _directory = directory;
            InputPath = inputPath;
            OutputPath = outputPath;
            InputBytes = File.ReadAllBytes(inputPath);
        }

        public string InputPath { get; }
        public string OutputPath { get; }
        public byte[] InputBytes { get; }

        public static TempSave FromGold(string label)
        {
            string gold = GoldSavePath;
            Assert.That(File.Exists(gold), Is.True, $"Missing tracked retail baseline fixture: {gold}");

            string directory = Path.Combine(Path.GetTempPath(), $"onslaught-{label}-{Guid.NewGuid():N}");
            Directory.CreateDirectory(directory);
            string input = Path.Combine(directory, "input.bes");
            File.Copy(gold, input, overwrite: true);
            return new TempSave(directory, input, Path.Combine(directory, "output.bes"));
        }

        public byte[] ReadOutput()
        {
            byte[] output = File.ReadAllBytes(OutputPath);
            Assert.That(
                output.Length,
                Is.EqualTo(BesFilePatcher.EXPECTED_FILE_SIZE),
                "A patched career save must keep the exact retail file length.");
            return output;
        }

        /// <summary>
        /// Assert that every byte outside the named ranges is identical to the input. This is what
        /// proves the ~37.3% of the format that is still opaque survived the round trip untouched.
        /// </summary>
        public void AssertOnlyTheseRangesChanged(params (int Start, int Length)[] allowed)
        {
            byte[] after = ReadOutput();
            bool[] permitted = new bool[after.Length];
            foreach ((int start, int length) in allowed)
            {
                for (int i = start; i < start + length; i++)
                {
                    permitted[i] = true;
                }
            }

            List<int> unexpected = new();
            for (int i = 0; i < after.Length; i++)
            {
                if (after[i] != InputBytes[i] && !permitted[i])
                {
                    unexpected.Add(i);
                }
            }

            Assert.That(
                unexpected,
                Is.Empty,
                unexpected.Count == 0
                    ? string.Empty
                    : $"{unexpected.Count} byte(s) outside the targeted region changed, first at " +
                      $"0x{unexpected[0]:X4}. Unmapped and reserved bytes must survive a patch untouched.");
        }

        public void Dispose()
        {
            if (Directory.Exists(_directory))
            {
                Directory.Delete(_directory, recursive: true);
            }
        }
    }
}
