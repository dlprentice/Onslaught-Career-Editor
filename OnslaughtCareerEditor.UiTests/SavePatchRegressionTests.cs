using System;
using System.Buffers.Binary;
using System.Diagnostics;
using System.IO;
using System.Threading.Tasks;
using NUnit.Framework;
using OnslaughtCareerEditor.AppCore;

namespace OnslaughtCareerEditor.UiTests;

public class SavePatchRegressionTests
{
    private static string RepoRoot => TestFixturePaths.RepoRoot;
    private static string GoldSavePath => TestFixturePaths.RequireGoldSavePath();

    [Test]
    public void PatchFile_WritesTailSettingsAtCorrectOffsets_WithNormalBooleanPolarity()
    {
        Assert.That(File.Exists(GoldSavePath), Is.True, $"Missing baseline save: {GoldSavePath}");

        string tempDir = Path.Combine(Path.GetTempPath(), $"onslaught-regression-{Guid.NewGuid():N}");
        Directory.CreateDirectory(tempDir);
        string input = Path.Combine(tempDir, "input.bes");
        string output = Path.Combine(tempDir, "output.bes");

        try
        {
            File.Copy(GoldSavePath, input, true);

            var patcher = new BesFilePatcher
            {
                PatchNodes = false,
                PatchLinks = false,
                PatchGoodies = false,
                PatchKills = false,

                InvertYAxisP1Override = true,
                InvertYAxisP2Override = false,
                InvertFlightP1Override = false,
                InvertFlightP2Override = true,
                VibrationP1Override = true,
                VibrationP2Override = false,
                ControllerConfigP1Override = 123u,
                ControllerConfigP2Override = 456u,
            };

            var result = patcher.PatchFile(input, output);
            Assert.That(result.Success, Is.True, result.Message);

            byte[] buf = File.ReadAllBytes(output);
            AssertUInt(buf, 0x249E, 0u, "Invert Y (Flight) P1 should write OFF as 0");
            AssertUInt(buf, 0x24A2, 1u, "Invert Y (Flight) P2 should write ON as 1");

            AssertUInt(buf, 0x24A6, 1u, "Invert Y (Walker) P1 should write ON as 1");
            AssertUInt(buf, 0x24AA, 0u, "Invert Y (Walker) P2 should write OFF as 0");

            AssertUInt(buf, 0x24AE, 1u, "Controller vibration P1 should write ON as 1");
            AssertUInt(buf, 0x24B2, 0u, "Controller vibration P2 should write OFF as 0");

            AssertUInt(buf, 0x24B6, 123u, "Controller config P1 should be written at 0x24B6");
            AssertUInt(buf, 0x24BA, 456u, "Controller config P2 should be written at 0x24BA");
        }
        finally
        {
            if (Directory.Exists(tempDir))
            {
                Directory.Delete(tempDir, recursive: true);
            }
        }
    }

    [Test]
    public void Cli_LevelRank_OneTargetsFirstNode_NotSecondNode()
    {
        Assert.That(File.Exists(GoldSavePath), Is.True, $"Missing baseline save: {GoldSavePath}");

        string tempDir = Path.Combine(Path.GetTempPath(), $"onslaught-levelrank-{Guid.NewGuid():N}");
        Directory.CreateDirectory(tempDir);
        string input = Path.Combine(tempDir, "input.bes");
        string output = Path.Combine(tempDir, "output.bes");

        try
        {
            File.Copy(GoldSavePath, input, true);
            EnsureNodeIsActive(input, 0);
            EnsureNodeIsActive(input, 1);

            string baselineOutput = Path.Combine(tempDir, "baseline_patch.bes");
            int baselineExitCode = RunCliSuccess(input, baselineOutput, "--rank", "E", "--no-links", "--no-goodies", "--no-kills");
            Assert.That(baselineExitCode, Is.EqualTo(0), "CLI baseline patch run failed");

            int exitCode = RunCliSuccess(input, output, "--rank", "E", "--level-rank", "1:S", "--no-links", "--no-goodies", "--no-kills");

            Assert.That(exitCode, Is.EqualTo(0), "CLI patch run failed");
            Assert.That(File.Exists(output), Is.True, "Output file was not written");

            byte[] baselineBuf = File.ReadAllBytes(baselineOutput);
            byte[] buf = File.ReadAllBytes(output);

            // True-view node base starts at file 0x0006.
            // Node 0 ranking offset: 0x0006 + (0 * 64) + 0x3C = 0x0042
            // Node 1 ranking offset: 0x0006 + (1 * 64) + 0x3C = 0x0082
            uint baselineNode1 = ReadUInt32(baselineBuf, 0x0082);
            uint node0 = ReadUInt32(buf, 0x0042);
            uint node1 = ReadUInt32(buf, 0x0082);

            Assert.That(node0, Is.EqualTo(0x3F800000u), "--level-rank 1:S must target node index 0");
            Assert.That(node1, Is.EqualTo(baselineNode1), "Node index 1 should not be touched by --level-rank 1:S");
        }
        finally
        {
            if (Directory.Exists(tempDir))
            {
                Directory.Delete(tempDir, recursive: true);
            }
        }
    }

    [Test]
    public void Cli_InvalidLevelRankEntry_FailsAndDoesNotWriteOutput()
    {
        Assert.That(File.Exists(GoldSavePath), Is.True, $"Missing baseline save: {GoldSavePath}");

        string tempDir = Path.Combine(Path.GetTempPath(), $"onslaught-levelrank-invalid-{Guid.NewGuid():N}");
        Directory.CreateDirectory(tempDir);
        string input = Path.Combine(tempDir, "input.bes");
        string output = Path.Combine(tempDir, "output_invalid_rank.bes");

        try
        {
            File.Copy(GoldSavePath, input, true);
            var result = RunCliRaw(input, output, "--level-rank", "bad", "--no-links", "--no-goodies", "--no-kills");
            Assert.That(result.ExitCode, Is.Not.EqualTo(0), "CLI should fail for invalid --level-rank input.");
            Assert.That(result.Stderr, Does.Contain("Invalid --level-rank entry").IgnoreCase);
            Assert.That(File.Exists(output), Is.False, "Output file must not be written when CLI validation fails.");
        }
        finally
        {
            if (Directory.Exists(tempDir))
                Directory.Delete(tempDir, recursive: true);
        }
    }

    [Test]
    public void Cli_CopyOptionsFromWithBothNoCopyFlags_FailsAndDoesNotWriteOutput()
    {
        Assert.That(File.Exists(GoldSavePath), Is.True, $"Missing baseline save: {GoldSavePath}");

        string tempDir = Path.Combine(Path.GetTempPath(), $"onslaught-copy-options-invalid-{Guid.NewGuid():N}");
        Directory.CreateDirectory(tempDir);
        string input = Path.Combine(tempDir, "input.bes");
        string output = Path.Combine(tempDir, "output_invalid_copy_options.bes");

        try
        {
            File.Copy(GoldSavePath, input, true);
            var result = RunCliRaw(
                input,
                output,
                "--copy-options-from", input,
                "--no-copy-options-entries",
                "--no-copy-options-tail");
            Assert.That(result.ExitCode, Is.Not.EqualTo(0), "CLI should fail when both no-copy options are set.");
            Assert.That(result.Stderr, Does.Contain("both --no-copy-options-entries and --no-copy-options-tail").IgnoreCase);
            Assert.That(File.Exists(output), Is.False, "Output file must not be written when copy-options validation fails.");
        }
        finally
        {
            if (Directory.Exists(tempDir))
                Directory.Delete(tempDir, recursive: true);
        }
    }

    [Test]
    public void PatchFile_RejectsInPlaceOutputPath()
    {
        Assert.That(File.Exists(GoldSavePath), Is.True, $"Missing baseline save: {GoldSavePath}");

        string tempDir = Path.Combine(Path.GetTempPath(), $"onslaught-inplace-guard-{Guid.NewGuid():N}");
        Directory.CreateDirectory(tempDir);
        string input = Path.Combine(tempDir, "input.bes");

        try
        {
            File.Copy(GoldSavePath, input, true);
            var patcher = new BesFilePatcher
            {
                PatchNodes = false,
                PatchLinks = false,
                PatchGoodies = false,
                PatchKills = false,
            };

            var result = patcher.PatchFile(input, input);
            Assert.That(result.Success, Is.False, "Patcher must reject in-place writes.");
            Assert.That(result.Message, Does.Contain("Refusing to patch in place").IgnoreCase);
        }
        finally
        {
            if (Directory.Exists(tempDir))
                Directory.Delete(tempDir, recursive: true);
        }
    }

    [Test]
    public void TryParseKeyboardPackedKey_AcceptsRawFallbackToken()
    {
        bool ok = BesFilePatcher.TryParseKeyboardPackedKey(
            "vk=0x0000 scan=0x0027",
            out uint packed,
            out string? error);

        Assert.That(ok, Is.True, error ?? "Expected parser success.");
        Assert.That(packed, Is.EqualTo(0x00000027u));
    }

    [Test]
    public void FormatBinding_FallbackToken_RoundTripsThroughParser()
    {
        const uint originalPacked = 0xABCD1234u;
        string token = BesFilePatcher.FormatBinding(deviceCode: 9u, packedKey: originalPacked, entryId: 0x1F);

        Assert.That(token, Is.EqualTo("vk=0xABCD scan=0x1234"));

        bool ok = BesFilePatcher.TryParseKeyboardPackedKey(token, out uint parsedPacked, out string? error);
        Assert.That(ok, Is.True, error ?? "Expected parser success.");
        Assert.That(parsedPacked, Is.EqualTo(originalPacked));
    }

    [Test]
    public void PatchFile_GoodiesBoundary_PatchesSlot232_AndPreservesReservedSlots()
    {
        Assert.That(File.Exists(GoldSavePath), Is.True, $"Missing baseline save: {GoldSavePath}");

        string tempDir = Path.Combine(Path.GetTempPath(), $"onslaught-goodies-boundary-{Guid.NewGuid():N}");
        Directory.CreateDirectory(tempDir);
        string input = Path.Combine(tempDir, "input.bes");
        string output = Path.Combine(tempDir, "output.bes");

        try
        {
            File.Copy(GoldSavePath, input, true);
            byte[] before = File.ReadAllBytes(input);

            var patcher = new BesFilePatcher
            {
                PatchNodes = false,
                PatchLinks = false,
                PatchGoodies = true,
                PatchKills = false,
                UseNewGoodiesInstead = false,
            };

            var result = patcher.PatchFile(input, output);
            Assert.That(result.Success, Is.True, result.Message);

            byte[] after = File.ReadAllBytes(output);
            int slot232Off = 0x1F46 + (232 * 4);
            AssertUInt(after, slot232Off, 3u, "Displayable goodie slot 232 should be unlocked as OLD");

            for (int idx = 233; idx < 300; idx++)
            {
                int off = 0x1F46 + (idx * 4);
                uint oldRaw = ReadUInt32(before, off);
                uint newRaw = ReadUInt32(after, off);
                Assert.That(newRaw, Is.EqualTo(oldRaw), $"Reserved goodie slot {idx} changed unexpectedly.");
            }
        }
        finally
        {
            if (Directory.Exists(tempDir))
                Directory.Delete(tempDir, recursive: true);
        }
    }

    [Test]
    public void PatchFile_KillPatch_PreservesMetaHighByte()
    {
        Assert.That(File.Exists(GoldSavePath), Is.True, $"Missing baseline save: {GoldSavePath}");

        string tempDir = Path.Combine(Path.GetTempPath(), $"onslaught-killmeta-{Guid.NewGuid():N}");
        Directory.CreateDirectory(tempDir);
        string input = Path.Combine(tempDir, "input.bes");
        string output = Path.Combine(tempDir, "output.bes");

        try
        {
            byte[] buf = File.ReadAllBytes(GoldSavePath);
            byte[] seededMeta = new byte[] { 0xA1, 0xB2, 0xC3, 0xD4, 0xE5 };
            for (int i = 0; i < seededMeta.Length; i++)
            {
                int off = 0x23F6 + (i * 4);
                uint seeded = ((uint)seededMeta[i] << 24) | 7u;
                BinaryPrimitives.WriteUInt32LittleEndian(buf.AsSpan(off, 4), seeded);
            }
            File.WriteAllBytes(input, buf);

            var patcher = new BesFilePatcher
            {
                PatchNodes = false,
                PatchLinks = false,
                PatchGoodies = false,
                PatchKills = true,
                GlobalKillCount = 123,
            };

            var result = patcher.PatchFile(input, output);
            Assert.That(result.Success, Is.True, result.Message);

            byte[] after = File.ReadAllBytes(output);
            for (int i = 0; i < seededMeta.Length; i++)
            {
                int off = 0x23F6 + (i * 4);
                uint raw = ReadUInt32(after, off);
                Assert.That((raw >> 24) & 0xFFu, Is.EqualTo((uint)seededMeta[i]), $"Meta byte changed for kill slot {i}.");
                Assert.That(raw & 0x00FFFFFFu, Is.EqualTo(123u), $"Kill payload mismatch for slot {i}.");
            }
        }
        finally
        {
            if (Directory.Exists(tempDir))
                Directory.Delete(tempDir, recursive: true);
        }
    }

    // ---- True-view layout owned by the four Save Editor section passes ----
    private const int NodeBase = 0x0006;
    private const int NodeSize = 64;
    private const int NodeCount = 100;
    private const int LinkBase = 0x1906;
    private const int LinkSize = 8;
    private const int LinkCount = 200;
    private const int GoodieBase = 0x1F46;
    private const int GoodieDisplayableCount = 233;
    private const int KillBase = 0x23F6;
    private const int KillCategoryCount = 5;

    [Test]
    public void PatchSave_UnmodifiedRoundTripThroughAppService_IsByteIdentical()
    {
        string tempDir = NewTempDir("roundtrip");
        try
        {
            string input = Path.Combine(tempDir, "input.bes");
            File.Copy(GoldSavePath, input, true);
            byte[] before = File.ReadAllBytes(input);

            SaveAnalysis analysis = BesFilePatcher.AnalyzeSave(input);
            Assert.That(analysis.IsValid, Is.True, "Baseline fixture must analyze as a valid career save.");
            Dictionary<int, int> currentKills = new()
            {
                [BesFilePatcher.KILL_AIRCRAFT] = analysis.KillCounts[0],
                [BesFilePatcher.KILL_VEHICLES] = analysis.KillCounts[1],
                [BesFilePatcher.KILL_EMPLACEMENTS] = analysis.KillCounts[2],
                [BesFilePatcher.KILL_INFANTRY] = analysis.KillCounts[3],
                [BesFilePatcher.KILL_MECHS] = analysis.KillCounts[4],
            };

            string output = Path.Combine(tempDir, "roundtrip.bes");
            PatchResult result = SaveEditorService.PatchSave(new SavePatchRequest
            {
                InputPath = input,
                OutputPath = output,
                Rank = "S",
                PatchNodes = true,
                PatchLinks = true,
                PatchGoodies = false,
                PatchKills = true,
                PerCategoryKills = currentKills
            });

            Assert.That(result.Success, Is.True, result.Message);
            byte[] after = File.ReadAllBytes(output);
            Assert.That(after.Length, Is.EqualTo(BesFilePatcher.EXPECTED_FILE_SIZE));
            Assert.That(
                DescribeDifferences(before, after),
                Is.EqualTo("IDENTICAL"),
                "Re-writing the fixture's own node/link/kill values through the app service must reproduce the input byte-for-byte.");
            Assert.That(File.ReadAllBytes(input), Is.EqualTo(before), "The source save must never be modified.");

            // Non-vacuity control: the same request with one changed kill value must differ.
            currentKills[BesFilePatcher.KILL_MECHS] = analysis.KillCounts[4] + 1;
            string changedOutput = Path.Combine(tempDir, "changed.bes");
            PatchResult changedResult = SaveEditorService.PatchSave(new SavePatchRequest
            {
                InputPath = input,
                OutputPath = changedOutput,
                Rank = "S",
                PatchNodes = true,
                PatchLinks = true,
                PatchGoodies = false,
                PatchKills = true,
                PerCategoryKills = currentKills
            });
            Assert.That(changedResult.Success, Is.True, changedResult.Message);
            Assert.That(
                DescribeDifferences(before, File.ReadAllBytes(changedOutput)),
                Is.Not.EqualTo("IDENTICAL"),
                "The identity assertion must be able to detect a one-value change.");
        }
        finally
        {
            DeleteTempDir(tempDir);
        }
    }

    [Test]
    public void PatchSave_AllSections_ChangesOnlyBytesOwnedBySelectedSections()
    {
        string tempDir = NewTempDir("owned-regions");
        try
        {
            string input = Path.Combine(tempDir, "input.bes");
            File.Copy(GoldSavePath, input, true);
            byte[] before = File.ReadAllBytes(input);

            string output = Path.Combine(tempDir, "all-sections.bes");
            PatchResult result = SaveEditorService.PatchSave(new SavePatchRequest
            {
                InputPath = input,
                OutputPath = output,
                Rank = "C",
                UseNewGoodiesInstead = true,
                GlobalKillCount = 4242,
                PatchNodes = true,
                PatchLinks = true,
                PatchGoodies = true,
                PatchKills = true
            });
            Assert.That(result.Success, Is.True, result.Message);

            byte[] after = File.ReadAllBytes(output);
            Assert.That(after.Length, Is.EqualTo(before.Length), "File length must be preserved.");

            bool[] owned = BuildOwnedByteMap();
            List<int> strays = new();
            for (int offset = 0; offset < before.Length; offset++)
            {
                if (before[offset] != after[offset] && !owned[offset])
                {
                    strays.Add(offset);
                }
            }

            Assert.That(
                strays,
                Is.Empty,
                "Bytes changed outside the node/link/goodie/kill regions: " +
                string.Join(", ", strays.Take(24).Select(o => $"0x{o:X4}")));

            // Non-vacuity control: the map must not simply cover the whole file.
            int ownedCount = owned.Count(flag => flag);
            Assert.That(ownedCount, Is.LessThan(before.Length / 2),
                $"Owned-region map must be a strict minority of the file; covered {ownedCount} of {before.Length} bytes.");
            Assert.That(
                DescribeDifferences(before, after),
                Is.Not.EqualTo("IDENTICAL"),
                "This patch must actually change bytes for the containment check to mean anything.");
        }
        finally
        {
            DeleteTempDir(tempDir);
        }
    }

    [Test]
    public void PatchSave_MissionRankOverrideWithoutNodePatching_FailsAndWritesNothing()
    {
        string tempDir = NewTempDir("rank-drop");
        try
        {
            string input = Path.Combine(tempDir, "input.bes");
            File.Copy(GoldSavePath, input, true);
            byte[] before = File.ReadAllBytes(input);
            var overrides = new Dictionary<int, string> { [0] = "E" };

            string blockedOutput = Path.Combine(tempDir, "blocked.bes");
            PatchResult blocked = SaveEditorService.PatchSave(new SavePatchRequest
            {
                InputPath = input,
                OutputPath = blockedOutput,
                PatchNodes = false,
                PatchLinks = false,
                PatchGoodies = false,
                PatchKills = true,
                GlobalKillCount = 100,
                LevelRanks = overrides
            });

            Assert.That(blocked.Success, Is.False,
                "A mission rank override with node patching disabled must not report success.");
            Assert.That(blocked.Message, Does.Contain("Mission rank overrides"));
            Assert.That(File.Exists(blockedOutput), Is.False,
                "No output may be written when the requested overrides would be discarded.");

            // Positive control: with node patching enabled the same override reaches the file.
            string allowedOutput = Path.Combine(tempDir, "allowed.bes");
            PatchResult allowed = SaveEditorService.PatchSave(new SavePatchRequest
            {
                InputPath = input,
                OutputPath = allowedOutput,
                Rank = "S",
                PatchNodes = true,
                PatchLinks = false,
                PatchGoodies = false,
                PatchKills = false,
                LevelRanks = overrides
            });
            Assert.That(allowed.Success, Is.True, allowed.Message);
            byte[] after = File.ReadAllBytes(allowedOutput);
            AssertUInt(after, NodeBase + 0x3C, 0x00000000u, "Node 0 must receive the requested E rank");
            Assert.That(File.ReadAllBytes(input), Is.EqualTo(before), "The source save must never be modified.");
        }
        finally
        {
            DeleteTempDir(tempDir);
        }
    }

    [Test]
    public void PatchSave_CategoryKillOverrideWithoutKillPatching_FailsAndWritesNothing()
    {
        string tempDir = NewTempDir("kill-drop");
        try
        {
            string input = Path.Combine(tempDir, "input.bes");
            File.Copy(GoldSavePath, input, true);
            var overrides = new Dictionary<int, int> { [BesFilePatcher.KILL_AIRCRAFT] = 777 };

            string blockedOutput = Path.Combine(tempDir, "blocked.bes");
            PatchResult blocked = SaveEditorService.PatchSave(new SavePatchRequest
            {
                InputPath = input,
                OutputPath = blockedOutput,
                PatchNodes = false,
                PatchLinks = false,
                PatchGoodies = true,
                PatchKills = false,
                PerCategoryKills = overrides
            });

            Assert.That(blocked.Success, Is.False,
                "A per-category kill override with kill patching disabled must not report success.");
            Assert.That(blocked.Message, Does.Contain("Per-category kill overrides"));
            Assert.That(File.Exists(blockedOutput), Is.False,
                "No output may be written when the requested overrides would be discarded.");

            // Positive control: with kill patching enabled the same override reaches the file.
            string allowedOutput = Path.Combine(tempDir, "allowed.bes");
            PatchResult allowed = SaveEditorService.PatchSave(new SavePatchRequest
            {
                InputPath = input,
                OutputPath = allowedOutput,
                PatchNodes = false,
                PatchLinks = false,
                PatchGoodies = false,
                PatchKills = true,
                GlobalKillCount = 100,
                PerCategoryKills = overrides
            });
            Assert.That(allowed.Success, Is.True, allowed.Message);
            byte[] after = File.ReadAllBytes(allowedOutput);
            uint aircraftRaw = ReadUInt32(after, KillBase + (BesFilePatcher.KILL_AIRCRAFT * 4));
            Assert.That(aircraftRaw & 0x00FFFFFFu, Is.EqualTo(777u), "Aircraft kill override must reach the file.");
        }
        finally
        {
            DeleteTempDir(tempDir);
        }
    }

    [Test]
    public void Cli_LevelRankWithNoNodes_FailsAndDoesNotWriteOutput()
    {
        Assert.That(File.Exists(GoldSavePath), Is.True, $"Missing baseline save: {GoldSavePath}");

        string tempDir = NewTempDir("cli-rank-drop");
        try
        {
            string input = Path.Combine(tempDir, "input.bes");
            File.Copy(GoldSavePath, input, true);
            string output = Path.Combine(tempDir, "output.bes");

            var result = RunCliRaw(input, output, "--rank", "E", "--level-rank", "1:S", "--no-nodes");
            Assert.That(result.ExitCode, Is.Not.EqualTo(0),
                $"CLI must reject --level-rank with --no-nodes.\nSTDOUT:\n{result.Stdout}\nSTDERR:\n{result.Stderr}");
            Assert.That(result.Stderr, Does.Contain("--level-rank").IgnoreCase);
            Assert.That(File.Exists(output), Is.False,
                "The CLI must not write an output file when the rank override would be discarded.");

            // Positive control: the same override without --no-nodes still succeeds.
            string allowed = Path.Combine(tempDir, "allowed.bes");
            var okResult = RunCliRaw(input, allowed, "--rank", "E", "--level-rank", "1:S", "--no-links", "--no-goodies", "--no-kills");
            Assert.That(okResult.ExitCode, Is.EqualTo(0), okResult.Stderr);
            AssertUInt(File.ReadAllBytes(allowed), NodeBase + 0x3C, 0x3F800000u, "Node 0 must receive the requested S rank");
        }
        finally
        {
            DeleteTempDir(tempDir);
        }
    }

    [Test]
    public void Cli_PerCategoryKillsWithNoKills_FailsAndDoesNotWriteOutput()
    {
        Assert.That(File.Exists(GoldSavePath), Is.True, $"Missing baseline save: {GoldSavePath}");

        string tempDir = NewTempDir("cli-kill-drop");
        try
        {
            string input = Path.Combine(tempDir, "input.bes");
            File.Copy(GoldSavePath, input, true);
            string output = Path.Combine(tempDir, "output.bes");

            var result = RunCliRaw(input, output, "--aircraft-kills", "777", "--no-kills");
            Assert.That(result.ExitCode, Is.Not.EqualTo(0),
                $"CLI must reject per-category kills with --no-kills.\nSTDOUT:\n{result.Stdout}\nSTDERR:\n{result.Stderr}");
            Assert.That(result.Stderr, Does.Contain("per-category kill").IgnoreCase);
            Assert.That(File.Exists(output), Is.False,
                "The CLI must not write an output file when per-category kills would be discarded.");
        }
        finally
        {
            DeleteTempDir(tempDir);
        }
    }

    [Test]
    public void PatchSave_UnknownRankBaseline_FailsInsteadOfSilentlyWritingTopGrade()
    {
        string tempDir = NewTempDir("unknown-rank");
        try
        {
            string input = Path.Combine(tempDir, "input.bes");
            File.Copy(GoldSavePath, input, true);
            string output = Path.Combine(tempDir, "blocked.bes");

            PatchResult result = SaveEditorService.PatchSave(new SavePatchRequest
            {
                InputPath = input,
                OutputPath = output,
                Rank = "Z",
                PatchNodes = true,
                PatchLinks = false,
                PatchGoodies = false,
                PatchKills = false
            });

            Assert.That(result.Success, Is.False,
                "An unrecognised rank baseline used to fall back to S and write the highest grade over every mission.");
            Assert.That(result.Message, Does.Contain("Z"));
            Assert.That(File.Exists(output), Is.False, "No output may be written for an unencodable rank.");

            // Positive control: every rank the format encodes still writes.
            foreach (string rank in new[] { "S", "A", "B", "C", "D", "E", "NONE" })
            {
                string accepted = Path.Combine(tempDir, $"ok_{rank}.bes");
                PatchResult ok = SaveEditorService.PatchSave(new SavePatchRequest
                {
                    InputPath = input,
                    OutputPath = accepted,
                    Rank = rank,
                    PatchNodes = true,
                    PatchLinks = false,
                    PatchGoodies = false,
                    PatchKills = false
                });
                Assert.That(ok.Success, Is.True, $"Rank {rank} must remain writable. {ok.Message}");
            }
        }
        finally
        {
            DeleteTempDir(tempDir);
        }
    }

    [Test]
    public void PatchSave_UnknownMissionRankOverride_FailsInsteadOfSilentlyWritingTopGrade()
    {
        string tempDir = NewTempDir("unknown-override-rank");
        try
        {
            string input = Path.Combine(tempDir, "input.bes");
            File.Copy(GoldSavePath, input, true);
            string output = Path.Combine(tempDir, "blocked.bes");

            PatchResult result = SaveEditorService.PatchSave(new SavePatchRequest
            {
                InputPath = input,
                OutputPath = output,
                Rank = "E",
                PatchNodes = true,
                PatchLinks = false,
                PatchGoodies = false,
                PatchKills = false,
                LevelRanks = new Dictionary<int, string> { [0] = "PLATINUM" }
            });

            Assert.That(result.Success, Is.False);
            Assert.That(result.Message, Does.Contain("PLATINUM"));
            Assert.That(File.Exists(output), Is.False);
        }
        finally
        {
            DeleteTempDir(tempDir);
        }
    }

    [Test]
    public void PatchSave_OverrideKeysOutsideTheirArrays_FailInsteadOfBeingDiscarded()
    {
        string tempDir = NewTempDir("oob-override-keys");
        try
        {
            string input = Path.Combine(tempDir, "input.bes");
            File.Copy(GoldSavePath, input, true);

            string rankOut = Path.Combine(tempDir, "rank.bes");
            PatchResult rankResult = SaveEditorService.PatchSave(new SavePatchRequest
            {
                InputPath = input,
                OutputPath = rankOut,
                Rank = "S",
                PatchNodes = true,
                PatchLinks = false,
                PatchGoodies = false,
                PatchKills = false,
                LevelRanks = new Dictionary<int, string> { [NodeCount] = "A" }
            });
            Assert.That(rankResult.Success, Is.False,
                "A mission rank override outside the node array can never reach the file.");
            Assert.That(File.Exists(rankOut), Is.False);

            string killOut = Path.Combine(tempDir, "kill.bes");
            PatchResult killResult = SaveEditorService.PatchSave(new SavePatchRequest
            {
                InputPath = input,
                OutputPath = killOut,
                PatchNodes = false,
                PatchLinks = false,
                PatchGoodies = false,
                PatchKills = true,
                GlobalKillCount = 100,
                PerCategoryKills = new Dictionary<int, int> { [KillCategoryCount] = 5 }
            });
            Assert.That(killResult.Success, Is.False,
                "A kill override outside the five categories can never reach the file.");
            Assert.That(File.Exists(killOut), Is.False);
        }
        finally
        {
            DeleteTempDir(tempDir);
        }
    }

    [Test]
    public void PatchSave_MissionRankOverrideOnAnUnusedNodeSlot_FailsInsteadOfBeingDiscarded()
    {
        string tempDir = NewTempDir("unused-node-override");
        try
        {
            string input = Path.Combine(tempDir, "input.bes");
            File.Copy(GoldSavePath, input, true);

            // Node slots beyond the retail career map carry world id 0; the node pass skips them.
            byte[] buf = File.ReadAllBytes(input);
            const int unusedNode = 90;
            Assert.That(
                ReadUInt32(buf, NodeBase + (unusedNode * NodeSize) + 0x10),
                Is.Zero,
                "The fixture must actually leave this node slot unused for this test to mean anything.");

            string output = Path.Combine(tempDir, "blocked.bes");
            PatchResult result = SaveEditorService.PatchSave(new SavePatchRequest
            {
                InputPath = input,
                OutputPath = output,
                Rank = "S",
                PatchNodes = true,
                PatchLinks = false,
                PatchGoodies = false,
                PatchKills = false,
                LevelRanks = new Dictionary<int, string> { [unusedNode] = "A" }
            });

            Assert.That(result.Success, Is.False,
                "A rank override aimed at an unused node slot used to be dropped while reporting success.");
            Assert.That(result.Message, Does.Contain(unusedNode.ToString()));
            Assert.That(File.Exists(output), Is.False);

            // Positive control: the same override on a used slot still succeeds and reaches the file.
            string allowed = Path.Combine(tempDir, "allowed.bes");
            PatchResult ok = SaveEditorService.PatchSave(new SavePatchRequest
            {
                InputPath = input,
                OutputPath = allowed,
                Rank = "S",
                PatchNodes = true,
                PatchLinks = false,
                PatchGoodies = false,
                PatchKills = false,
                LevelRanks = new Dictionary<int, string> { [0] = "A" }
            });
            Assert.That(ok.Success, Is.True, ok.Message);
            AssertUInt(File.ReadAllBytes(allowed), NodeBase + 0x3C, 0x3F4CCCCDu, "Node 0 must receive the requested A rank");
        }
        finally
        {
            DeleteTempDir(tempDir);
        }
    }

    private static bool[] BuildOwnedByteMap()
    {
        bool[] owned = new bool[BesFilePatcher.EXPECTED_FILE_SIZE];

        void Mark(int offset, int length)
        {
            for (int i = offset; i < offset + length && i < owned.Length; i++)
            {
                owned[i] = true;
            }
        }

        for (int n = 0; n < NodeCount; n++)
        {
            int off = NodeBase + (n * NodeSize);
            Mark(off + 0x04, 4);  // complete
            Mark(off + 0x38, 4);  // attempts
            Mark(off + 0x3C, 4);  // rank float bits
        }

        for (int l = 0; l < LinkCount; l++)
        {
            Mark(LinkBase + (l * LinkSize), 4);  // link state
        }

        Mark(GoodieBase, GoodieDisplayableCount * 4);
        Mark(KillBase, KillCategoryCount * 4);
        return owned;
    }

    private static string DescribeDifferences(byte[] left, byte[] right)
    {
        if (left.Length != right.Length)
        {
            return $"LENGTH {left.Length} vs {right.Length}";
        }

        List<string> runs = new();
        int total = 0;
        int i = 0;
        while (i < left.Length)
        {
            if (left[i] != right[i])
            {
                int start = i;
                while (i < left.Length && left[i] != right[i])
                {
                    i++;
                    total++;
                }

                if (runs.Count < 16)
                {
                    runs.Add($"0x{start:X4}..0x{i - 1:X4}");
                }
            }
            else
            {
                i++;
            }
        }

        return total == 0 ? "IDENTICAL" : $"{total} bytes differ at {string.Join(", ", runs)}";
    }

    private static string NewTempDir(string label)
    {
        string tempDir = Path.Combine(Path.GetTempPath(), $"onslaught-{label}-{Guid.NewGuid():N}");
        Directory.CreateDirectory(tempDir);
        return tempDir;
    }

    private static void DeleteTempDir(string tempDir)
    {
        try
        {
            if (Directory.Exists(tempDir))
            {
                Directory.Delete(tempDir, recursive: true);
            }
        }
        catch (IOException)
        {
            // Leaving an OS-temp scratch directory behind must not fail the regression assertion.
        }
    }

    private static void AssertUInt(byte[] buf, int offset, uint expected, string message)
    {
        uint actual = ReadUInt32(buf, offset);
        Assert.That(actual, Is.EqualTo(expected),
            $"{message}. offset=0x{offset:X4}, expected=0x{expected:X8}, actual=0x{actual:X8}");
    }

    private static uint ReadUInt32(byte[] buf, int offset)
    {
        return BinaryPrimitives.ReadUInt32LittleEndian(buf.AsSpan(offset, 4));
    }

    private static int RunCliSuccess(params string[] args)
    {
        var result = RunCliRaw(args);
        if (result.ExitCode != 0)
        {
            Assert.Fail($"CLI failed with exit code {result.ExitCode}\\nSTDOUT:\\n{result.Stdout}\\nSTDERR:\\n{result.Stderr}");
        }

        return result.ExitCode;
    }

    private static CliRunResult RunCliRaw(params string[] args)
    {
        string repoRoot = RepoRoot;
        string projectPath = Path.Combine(repoRoot, "OnslaughtCareerEditor.Cli", "OnslaughtCareerEditor.Cli.csproj");
        string? dotnetExe = ResolveDotnetExe();
        if (dotnetExe == null)
            Assert.Ignore("dotnet runtime not found for CLI regression test.");

        var psi = new ProcessStartInfo
        {
            FileName = dotnetExe,
            WorkingDirectory = repoRoot,
            RedirectStandardOutput = true,
            RedirectStandardError = true,
            UseShellExecute = false,
            CreateNoWindow = true
        };

        psi.ArgumentList.Add("run");
        psi.ArgumentList.Add("--project");
        psi.ArgumentList.Add(projectPath);
        psi.ArgumentList.Add("--");
        foreach (var arg in args)
            psi.ArgumentList.Add(arg);

        using var process = Process.Start(psi);
        Assert.That(process, Is.Not.Null, "Failed to start dotnet process.");
        var stdoutTask = process!.StandardOutput.ReadToEndAsync();
        var stderrTask = process.StandardError.ReadToEndAsync();

        if (!process.WaitForExit(120_000))
        {
            try { process.Kill(entireProcessTree: true); } catch { }
            Assert.Fail("CLI process timed out after 120s.");
        }

        Task.WaitAll(stdoutTask, stderrTask);
        return new CliRunResult(process.ExitCode, stdoutTask.Result, stderrTask.Result);
    }

    private readonly struct CliRunResult(int exitCode, string stdout, string stderr)
    {
        public int ExitCode { get; } = exitCode;
        public string Stdout { get; } = stdout;
        public string Stderr { get; } = stderr;
    }

    private static void EnsureNodeIsActive(string filePath, int nodeIndex)
    {
        byte[] buf = File.ReadAllBytes(filePath);
        int nodeBase = 0x0006 + (nodeIndex * 64);
        int worldOffset = nodeBase + 0x10;
        WriteUInt32(buf, worldOffset, 1u);
        File.WriteAllBytes(filePath, buf);
    }

    private static void WriteUInt32(byte[] buf, int offset, uint value)
    {
        BinaryPrimitives.WriteUInt32LittleEndian(buf.AsSpan(offset, 4), value);
    }

    private static string? ResolveDotnetExe()
    {
        var env = Environment.GetEnvironmentVariable("DOTNET_EXE");
        if (!string.IsNullOrWhiteSpace(env) && File.Exists(env))
            return env;

        var candidates = new[]
        {
            @"C:\\Program Files\\dotnet\\dotnet.exe",
            @"/mnt/c/Program Files/dotnet/dotnet.exe",
            "/usr/bin/dotnet",
            "/usr/local/bin/dotnet"
        };

        foreach (var candidate in candidates)
        {
            if (File.Exists(candidate))
                return candidate;
        }

        return null;
    }
}
