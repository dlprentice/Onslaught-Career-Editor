using System;
using System.IO;
using System.Linq;
using System.Security.Cryptography;
using Xunit;

namespace OnslaughtCareerEditor.AppCore.Tests
{
    /// <summary>
    /// The census staging service: candidate experiment bytes go into an app-owned
    /// BEA.exe-only safe copy only, with byte-exact prechecks, a verified backup
    /// before any write, atomic publication with readback, and a per-batch undo
    /// manifest. Installed-game shapes are refused structurally.
    /// </summary>
    public sealed class PatchCensusStagingTests : IDisposable
    {
        private readonly string _tempRoot;
        private readonly string _workspaceRoot;
        private readonly string _exePath;

        public PatchCensusStagingTests()
        {
            _tempRoot = Path.Combine(Path.GetTempPath(), "oce-census-staging-tests", Guid.NewGuid().ToString("N"));
            _workspaceRoot = Path.Combine(_tempRoot, "workspace", "PatchBench");
            Directory.CreateDirectory(Path.Combine(_workspaceRoot, "copy-1"));

            // A synthetic safe copy whose bytes at every catalog offset are the
            // originals; census rows in these tests use offsets far from catalog
            // regions so they cannot collide with them.
            _exePath = Path.Combine(_workspaceRoot, "copy-1", "BEA.exe");
            int maxCatalogEnd = BinaryPatchEngine.PatchSpecs
                .SelectMany(BinaryPatchEngine.GetPatchRegions)
                .Select(region => region.FileOffset + region.Original.Length)
                .Max();
            byte[] data = new byte[maxCatalogEnd + 0x1000];
            foreach (BinaryPatchSpec spec in BinaryPatchEngine.PatchSpecs)
            {
                foreach (BinaryPatchRegion region in BinaryPatchEngine.GetPatchRegions(spec))
                {
                    region.Original.CopyTo(data, region.FileOffset);
                }
            }

            FillNonCatalogBytes(data);
            File.WriteAllBytes(_exePath, data);
        }

        /// <summary>
        /// Fills the synthetic copy with a recognizable non-zero filler so tests can
        /// pick offsets whose current bytes are known.
        /// </summary>
        private static void FillNonCatalogBytes(byte[] data)
        {
            bool[] isCatalog = new bool[data.Length];
            foreach (BinaryPatchSpec spec in BinaryPatchEngine.PatchSpecs)
            {
                foreach (BinaryPatchRegion region in BinaryPatchEngine.GetPatchRegions(spec))
                {
                    for (int i = region.FileOffset; i < region.FileOffset + region.Original.Length; i++)
                    {
                        isCatalog[i] = true;
                    }
                }
            }

            for (int i = 0; i < data.Length; i++)
            {
                if (!isCatalog[i])
                {
                    data[i] = 0x75;
                }
            }
        }

        public void Dispose()
        {
            try
            {
                Directory.Delete(_tempRoot, recursive: true);
            }
            catch (IOException)
            {
            }
        }

        private static PatchCensusRow Row(
            string va,
            string offsetHex,
            string originalHex,
            string patchedHex,
            string effect = "test experiment",
            string confidence = "MEASURED",
            string risk = "low") =>
            new(va, offsetHex, originalHex, patchedHex, effect, confidence, "patches/PATCH-SURFACE-CATALOG.md#1-1", risk, "run the copied game and look");

        private byte[] ExeBytes() => File.ReadAllBytes(_exePath);

        private static int DistinctTestOffset(byte[] data) =>
            // An offset past every catalog region with recognizable filler bytes.
            data.Length - 0x800;

        [Fact]
        public void Stage_WritesPatchedBytes_CreatesBackup_AndReadsBack()
        {
            byte[] data = ExeBytes();
            int offset = DistinctTestOffset(data);
            var row = Row("0x00999999", $"0x{offset:X8}", "7575", "9090");

            PatchCensusStagingPlan plan = PatchCensusStagingService.BuildStagingPlan(
                new[] { row }, _exePath, _workspaceRoot);
            Assert.True(plan.Success, plan.Message);
            Assert.Single(plan.Candidates);

            PatchCensusStagingResult result = PatchCensusStagingService.StageBatch(plan, _exePath, _workspaceRoot);
            Assert.True(result.Success, result.Message);

            byte[] after = ExeBytes();
            Assert.Equal(data.Length, after.Length);
            Assert.Equal(0x90, after[offset]);
            Assert.Equal(0x90, after[offset + 1]);
            Assert.True(File.Exists(BinaryPatchEngine.BuildBackupPath(_exePath)), "backup snapshot must exist after staging");

            byte[] backup = File.ReadAllBytes(BinaryPatchEngine.BuildBackupPath(_exePath));
            Assert.Equal(data, backup);
            Assert.NotEqual(Convert.ToHexString(SHA256.HashData(data)), Convert.ToHexString(SHA256.HashData(after)));
        }

        [Fact]
        public void Stage_RefusesWhenOriginalBytesDoNotMatch_AndWritesNothing()
        {
            byte[] data = ExeBytes();
            int offset = DistinctTestOffset(data);
            var wrongOriginal = Row("0x00999999", $"0x{offset:X8}", "1e75", "9090");

            PatchCensusStagingPlan mismatchPlan = PatchCensusStagingService.BuildStagingPlan(
                new[] { wrongOriginal }, _exePath, _workspaceRoot);

            Assert.False(mismatchPlan.Success);
            Assert.Contains("expects different bytes", mismatchPlan.Message, StringComparison.Ordinal);
            Assert.Contains("Nothing was changed", mismatchPlan.Message, StringComparison.Ordinal);
            Assert.False(File.Exists(BinaryPatchEngine.BuildBackupPath(_exePath)));

            var hugeOffset = Row("0x00999999", "0x7FFFFFFF", "7575", "9090");
            PatchCensusStagingPlan rangePlan = PatchCensusStagingService.BuildStagingPlan(
                new[] { hugeOffset }, _exePath, _workspaceRoot);
            Assert.False(rangePlan.Success);
            Assert.Contains("sits outside this safe copy", rangePlan.Message, StringComparison.Ordinal);
        }

        [Fact]
        public void Stage_SecondBatchRequiresEitherUndoOrOriginalBytes()
        {
            byte[] data = ExeBytes();
            int offset = DistinctTestOffset(data);
            var first = Row("0x00999999", $"0x{offset:X8}", "7575", "9090", effect: "first batch");

            PatchCensusStagingPlan firstPlan = PatchCensusStagingService.BuildStagingPlan(new[] { first }, _exePath, _workspaceRoot);
            Assert.True(PatchCensusStagingService.StageBatch(firstPlan, _exePath, _workspaceRoot).Success);

            // Same offset, same original bytes but a different value: a legitimate
            // second candidate for this site. After the first batch the copy no
            // longer holds the original bytes, so planning must refuse until undo.
            var second = Row("0x00999999", $"0x{offset:X8}", "7575", "eb1e", effect: "second batch");
            PatchCensusStagingPlan secondPlan = PatchCensusStagingService.BuildStagingPlan(new[] { second }, _exePath, _workspaceRoot);
            Assert.False(secondPlan.Success);
            Assert.Contains("Undo any earlier experiment", secondPlan.Message, StringComparison.Ordinal);

            PatchCensusStagingResult undo = PatchCensusStagingService.UndoAll(_exePath, _workspaceRoot);
            Assert.True(undo.Success, undo.Message);
            Assert.Equal(data, ExeBytes());

            PatchCensusStagingPlan retry = PatchCensusStagingService.BuildStagingPlan(new[] { second }, _exePath, _workspaceRoot);
            Assert.True(retry.Success, retry.Message);
            Assert.True(PatchCensusStagingService.StageBatch(retry, _exePath, _workspaceRoot).Success);
            Assert.Equal(0xEB, ExeBytes()[offset]);
        }

        [Fact]
        public void Undo_ReversesRecordedBatchByteForByte()
        {
            byte[] data = ExeBytes();
            int offset = DistinctTestOffset(data);
            var row = Row("0x00999999", $"0x{offset:X8}", "75757575", "9a99193d");

            PatchCensusStagingPlan plan = PatchCensusStagingService.BuildStagingPlan(new[] { row }, _exePath, _workspaceRoot);
            Assert.True(PatchCensusStagingService.StageBatch(plan, _exePath, _workspaceRoot).Success);
            Assert.NotEqual(data, ExeBytes());

            PatchCensusStagingResult undo = PatchCensusStagingService.UndoAll(_exePath, _workspaceRoot);
            Assert.True(undo.Success, undo.Message);
            Assert.Equal(data, ExeBytes());

            PatchCensusStagingManifest cleared = PatchCensusStagingService.ReadManifest(_exePath);
            Assert.True(cleared.Present);
            Assert.Empty(cleared.Entries);
        }

        [Fact]
        public void Undo_NamesEveryExperimentItReversed_InItsSummaries()
        {
            byte[] data = ExeBytes();
            int firstOffset = DistinctTestOffset(data);
            int secondOffset = firstOffset - 0x400;
            var first = Row("0x00999999", $"0x{firstOffset:X8}", "7575", "9090", effect: "first experiment");
            var second = Row("0x00AAAAAA", $"0x{secondOffset:X8}", "7575", "eb1e", effect: "second experiment");

            PatchCensusStagingPlan plan = PatchCensusStagingService.BuildStagingPlan(
                new[] { first, second }, _exePath, _workspaceRoot);
            Assert.True(plan.Success, plan.Message);
            Assert.True(PatchCensusStagingService.StageBatch(plan, _exePath, _workspaceRoot).Success);

            PatchCensusStagingResult undo = PatchCensusStagingService.UndoAll(_exePath, _workspaceRoot);
            Assert.True(undo.Success, undo.Message);

            // The undo result names what it reversed, in the same VA: effect form
            // staging uses, so callers can show an honest per-row receipt.
            Assert.Equal(2, undo.AppliedSummaries.Count);
            Assert.Contains("0x00999999: first experiment", undo.AppliedSummaries);
            Assert.Contains("0x00AAAAAA: second experiment", undo.AppliedSummaries);
        }

        /// <summary>
        /// StageBatch re-runs the structural refusals itself instead of trusting
        /// plan.Success: a hand-built plan aimed at a known Steam install shape
        /// must be refused by the service even though the plan object says it is
        /// valid and the bytes on disk match.
        /// </summary>
        [Fact]
        public void StageBatch_RefusesAnInstallShapedTarget_EvenWithAHandbuiltValidPlan()
        {
            string steamDir = Path.Combine(
                _tempRoot, "fabricated", "steamapps", "common", "Battle Engine Aquila");
            Directory.CreateDirectory(steamDir);
            string steamExe = Path.Combine(steamDir, "BEA.exe");

            // The decoy carries the exact original bytes the candidate expects,
            // so only the structural walk stands between this call and a write.
            byte[] data = new byte[0x2000];
            Array.Fill(data, (byte)0x75);
            File.WriteAllBytes(steamExe, data);

            var row = Row("0x00999999", "0x00001000", "7575", "9090");
            var candidate = new PatchCensusStagingCandidate(row, 0x1000, new byte[] { 0x75, 0x75 }, new byte[] { 0x90, 0x90 });
            var forgedPlan = new PatchCensusStagingPlan(true, "hand-forged", new[] { candidate });

            PatchCensusStagingResult result = PatchCensusStagingService.StageBatch(forgedPlan, steamExe, _workspaceRoot);

            Assert.False(result.Success);
            Assert.Equal(PatchCensusStagingService.ForbiddenInstallShapeMessage, result.Message);
            Assert.False(File.Exists(BinaryPatchEngine.BuildBackupPath(steamExe)), "a refused batch must not leave a backup behind");
            Assert.Equal(data, File.ReadAllBytes(steamExe));
        }

        /// <summary>
        /// The same defense-in-depth for workspace containment: StageBatch refuses
        /// a hand-built plan aimed anywhere outside the app-owned patch workspace,
        /// without relying on the planner to have caught it.
        /// </summary>
        [Fact]
        public void StageBatch_RefusesATargetOutsideTheWorkspace_EvenWithAHandbuiltValidPlan()
        {
            string outsideDir = Path.Combine(_tempRoot, "outside");
            Directory.CreateDirectory(outsideDir);
            string outsideExe = Path.Combine(outsideDir, "BEA.exe");

            byte[] data = new byte[0x2000];
            Array.Fill(data, (byte)0x75);
            File.WriteAllBytes(outsideExe, data);

            var row = Row("0x00999999", "0x00001000", "7575", "9090");
            var candidate = new PatchCensusStagingCandidate(row, 0x1000, new byte[] { 0x75, 0x75 }, new byte[] { 0x90, 0x90 });
            var forgedPlan = new PatchCensusStagingPlan(true, "hand-forged", new[] { candidate });

            PatchCensusStagingResult result = PatchCensusStagingService.StageBatch(forgedPlan, outsideExe, _workspaceRoot);

            Assert.False(result.Success);
            Assert.Contains("not inside the app-owned patch workspace", result.Message, StringComparison.Ordinal);
            Assert.False(File.Exists(BinaryPatchEngine.BuildBackupPath(outsideExe)), "a refused batch must not leave a backup behind");
            Assert.Equal(data, File.ReadAllBytes(outsideExe));
        }

        [Fact]
        public void Undo_WithoutManifest_SaysSoAndChangesNothing()
        {
            byte[] before = ExeBytes();

            PatchCensusStagingResult result = PatchCensusStagingService.UndoAll(_exePath, _workspaceRoot);

            Assert.False(result.Success);
            Assert.Contains("no census experiment manifest", result.Message, StringComparison.OrdinalIgnoreCase);
            Assert.Equal(before, ExeBytes());
        }

        [Fact]
        public void Manifest_RecordsEveryColumnForTheUi()
        {
            int offset = DistinctTestOffset(ExeBytes());
            var row = new PatchCensusRow(
                "0x005D8578",
                $"0x{offset:X8}",
                "75757575",
                "9a99193d",
                "CLOCK_TICK 0.05f -> ~0.038f",
                "STATIC_ONLY",
                "patches/a.md#1;reverse-engineering/b.md",
                "high",
                "Scripted-event timer visibly changes pace");

            PatchCensusStagingPlan plan = PatchCensusStagingService.BuildStagingPlan(new[] { row }, _exePath, _workspaceRoot);
            Assert.True(PatchCensusStagingService.StageBatch(plan, _exePath, _workspaceRoot).Success);

            PatchCensusStagingManifest manifest = PatchCensusStagingService.ReadManifest(_exePath);
            Assert.True(manifest.Present);
            PatchCensusStagedEntry entry = Assert.Single(manifest.Entries);
            Assert.Equal("0x005D8578", entry.Va);
            Assert.Equal($"0x{offset:X8}", entry.Offset);
            Assert.Equal("CLOCK_TICK 0.05f -> ~0.038f", entry.Effect);
            Assert.Equal("STATIC_ONLY", entry.Confidence);
            Assert.Equal("high", entry.Risk);
            Assert.Equal("patches/a.md#1;reverse-engineering/b.md", entry.EvidencePath);
        }

        [Fact]
        public void Plan_RefusesTwoRowsDisagreeingAboutOriginalBytesAtOneOffset()
        {
            int offset = DistinctTestOffset(ExeBytes());
            var left = Row("0x00999999", $"0x{offset:X8}", "7575", "9090", effect: "left");
            var right = Row("0x00AAAAAA", $"0x{offset:X8}", "1e75", "eb1e", effect: "right");

            PatchCensusStagingPlan plan = PatchCensusStagingService.BuildStagingPlan(
                new[] { left, right }, _exePath, _workspaceRoot);

            Assert.False(plan.Success);
            Assert.Contains("disagree about the original bytes", plan.Message, StringComparison.Ordinal);
            Assert.Contains("Nothing was changed", plan.Message, StringComparison.Ordinal);
        }

        [Fact]
        public void Plan_SameVaAlternativeValues_OverlapRefusal()
        {
            int offset = DistinctTestOffset(ExeBytes());
            var zero = Row("0x0046F4A8", $"0x{offset:X8}", "75757575", "90909090", effect: "to 0.0f");
            var five = Row("0x0046F4A8", $"0x{offset:X8}", "75757575", "c7434800", effect: "to 5.0f");

            PatchCensusStagingPlan plan = PatchCensusStagingService.BuildStagingPlan(
                new[] { zero, five }, _exePath, _workspaceRoot);

            // Same VA, identical originals, but two different patched values at the
            // same range overlap by construction - the honest refusal is to stage
            // one alternative at a time.
            Assert.False(plan.Success);
            Assert.Contains("overlapping bytes", plan.Message, StringComparison.Ordinal);
        }

        [Fact]
        public void Plan_RefusesBadOffsetAndBadBytesHonesty()
        {
            var badOffset = Row("0x1", "nothex", "751e", "9090");
            PatchCensusStagingPlan offsetPlan = PatchCensusStagingService.BuildStagingPlan(
                new[] { badOffset }, _exePath, _workspaceRoot);
            Assert.False(offsetPlan.Success);
            Assert.Contains("file offset", offsetPlan.Message, StringComparison.Ordinal);

            var badBytes = Row("0x2", "0x1000", "751", "9090");
            PatchCensusStagingPlan bytesPlan = PatchCensusStagingService.BuildStagingPlan(
                new[] { badBytes }, _exePath, _workspaceRoot);
            Assert.False(bytesPlan.Success);
            Assert.Contains("could not parse", bytesPlan.Message, StringComparison.Ordinal);
        }

        [Fact]
        public void Plan_MissingOrNonExeTargetRefuses()
        {
            PatchCensusStagingPlan missing = PatchCensusStagingService.BuildStagingPlan(
                new[] { Row("0x1", "0x1000", "aa", "bb") },
                Path.Combine(_workspaceRoot, "copy-1", "missing.exe"),
                _workspaceRoot);
            Assert.False(missing.Success);
            Assert.Equal(PatchCensusStagingService.NoSafeCopyMessage, missing.Message);

            PatchCensusStagingPlan wrongName = PatchCensusStagingService.BuildStagingPlan(
                new[] { Row("0x1", "0x1000", "aa", "bb") },
                _tempRoot,
                _workspaceRoot);
            Assert.False(wrongName.Success);
        }

        [Fact]
        public void Stage_OutsideWorkspaceRoot_IsRefused()
        {
            string outsideDir = Path.Combine(_tempRoot, "outside");
            Directory.CreateDirectory(outsideDir);
            string outsideExe = Path.Combine(outsideDir, "BEA.exe");
            File.WriteAllBytes(outsideExe, new byte[0x2000]);

            PatchCensusStagingPlan plan = PatchCensusStagingService.BuildStagingPlan(
                new[] { Row("0x1", "0x1000", "aa", "bb") }, outsideExe, _workspaceRoot);

            Assert.False(plan.Success);
            Assert.Contains("not inside the app-owned patch workspace", plan.Message, StringComparison.Ordinal);
            Assert.False(File.Exists(BinaryPatchEngine.BuildBackupPath(outsideExe)));
        }

        [Fact]
        public void TryParseOffset_AcceptsOnlyBoundedHex()
        {
            Assert.True(PatchCensusStagingService.TryParseOffsetPublic("0x0006F4A8", out int parsed));
            Assert.Equal(0x6F4A8, parsed);

            Assert.True(PatchCensusStagingService.TryParseOffsetPublic("6F4A8", out parsed));
            Assert.Equal(0x6F4A8, parsed);

            Assert.False(PatchCensusStagingService.TryParseOffsetPublic("", out _));
            Assert.False(PatchCensusStagingService.TryParseOffsetPublic("xyz", out _));
            Assert.False(PatchCensusStagingService.TryParseOffsetPublic("000000001", out _));
        }
    }
}
