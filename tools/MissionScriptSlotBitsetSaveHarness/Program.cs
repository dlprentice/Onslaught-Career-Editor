using System;
using System.Buffers.Binary;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Security.Cryptography;
using System.Text.Json;
using System.Text.Json.Serialization;
using Onslaught___Career_Editor;

namespace Onslaught___Career_Editor.Tools;

internal static class Program
{
    private const string SchemaVersion = "missionscript-slot-bitset-save-appcore-copied-baseline-codec-harness-private-evidence.v1";
    private const string EvidenceRootRelative = "subagents/static-to-proof/missionscript-slot-bitset-save-appcore-copied-baseline-codec-harness-proof";
    private const string BoundarySchemaVersion = "missionscript-slot-bitset-save-appcore-copied-baseline-boundary-corpus-private-evidence.v1";
    private const string BoundaryEvidenceRootRelative = "subagents/static-to-proof/missionscript-slot-bitset-save-appcore-copied-baseline-boundary-corpus-harness-proof";
    private const string BaselineFileName = "career-slot-appcore-baseline.bes";
    private const string NoopFileName = "career-slot-appcore-noop.bes";
    private const string SetFileName = "career-slot-appcore-61-62-set.bes";
    private const string IdempotentFileName = "career-slot-appcore-61-62-idempotent-set.bes";
    private const string ClearFileName = "career-slot-appcore-61-62-clear-roundtrip.bes";
    private const string BoundaryBaselineFileName = "career-slot-boundary-corpus-baseline.bes";
    private const string BoundaryNoopFileName = "career-slot-boundary-corpus-noop.bes";
    private const string BoundarySampleFileFormat = "career-slot-boundary-corpus-slot-{0:D3}-toggle.bes";
    private const string SummaryFileName = "evidence-summary.private.json";

    private static readonly JsonSerializerOptions JsonOptions = new()
    {
        DefaultIgnoreCondition = JsonIgnoreCondition.WhenWritingNull,
        PropertyNamingPolicy = JsonNamingPolicy.CamelCase,
        WriteIndented = true
    };

    private static readonly int[] TargetSlots = [61, 62];
    private static readonly int[] BoundaryVectorSlots = [63, 64, 224, 255];
    private static readonly int[] LegacyTrapOffsets = [0x23A4, 0x22D4, 0x240C];
    private static readonly Dictionary<string, (int Start, int End)> PreserveRanges = new()
    {
        ["killCountersAndPreSlotTail"] = (0x23F6, 0x240A),
        ["slotDword0"] = (0x240A, 0x240E),
        ["remainingSlotDwordsAfterTarget"] = (0x2412, 0x248A),
        ["postSlotFieldsThroughPreOptions"] = (0x248A, 0x24BE),
        ["optionsEntries"] = (0x24BE, 0x26BE),
        ["optionsTail"] = (0x26BE, 0x2714)
    };

    public static int Main(string[] args)
    {
        try
        {
            Options options = ParseArgs(args);
            if (options.ShowHelp)
            {
                WriteUsage();
                return 0;
            }

            string repoRoot = Path.GetFullPath(options.RepoRoot ?? Directory.GetCurrentDirectory());
            string sourcePath = RequirePath(options.SourcePath, "source");
            string evidenceRootRelative = options.Mode switch
            {
                HarnessMode.SeedSlots61And62 => EvidenceRootRelative,
                HarnessMode.BoundaryCorpus => BoundaryEvidenceRootRelative,
                _ => throw new InvalidOperationException($"Unsupported harness mode: {options.Mode}")
            };
            string outRoot = Path.GetFullPath(options.OutRoot ?? Path.Combine(repoRoot, evidenceRootRelative));
            string requiredOutRoot = Path.GetFullPath(Path.Combine(repoRoot, evidenceRootRelative));

            if (!PathsEqual(outRoot, requiredOutRoot))
            {
                throw new InvalidOperationException($"Output root must be the proof-private root: {requiredOutRoot}");
            }

            if (!IsWithinDirectory(outRoot, Path.Combine(repoRoot, "subagents", "static-to-proof")))
            {
                throw new InvalidOperationException("Output root must remain inside subagents/static-to-proof.");
            }

            if (!File.Exists(sourcePath))
            {
                throw new FileNotFoundException("Source copied baseline does not exist.", sourcePath);
            }

            Directory.CreateDirectory(outRoot);
            object evidence = options.Mode switch
            {
                HarnessMode.SeedSlots61And62 => MaterializeEvidence(repoRoot, sourcePath, outRoot),
                HarnessMode.BoundaryCorpus => MaterializeBoundaryCorpusEvidence(repoRoot, sourcePath, outRoot),
                _ => throw new InvalidOperationException($"Unsupported harness mode: {options.Mode}")
            };
            string summaryPath = Path.Combine(outRoot, SummaryFileName);
            File.WriteAllText(summaryPath, JsonSerializer.Serialize(evidence, JsonOptions) + Environment.NewLine);
            Console.WriteLine(summaryPath);
            return 0;
        }
        catch (Exception ex)
        {
            Console.Error.WriteLine(ex.Message);
            return 1;
        }
    }

    private static Evidence MaterializeEvidence(string repoRoot, string sourcePath, string outRoot)
    {
        byte[] source = File.ReadAllBytes(sourcePath);
        ValidateContainer(source, "source copied career baseline");

        string baselinePath = Path.Combine(outRoot, BaselineFileName);
        string noopPath = Path.Combine(outRoot, NoopFileName);
        string setPath = Path.Combine(outRoot, SetFileName);
        string idempotentPath = Path.Combine(outRoot, IdempotentFileName);
        string clearPath = Path.Combine(outRoot, ClearFileName);

        foreach (string outputPath in new[] { baselinePath, noopPath, setPath, idempotentPath, clearPath })
        {
            if (PathsEqual(sourcePath, outputPath))
            {
                throw new InvalidOperationException("Source and output paths must be distinct.");
            }
        }

        File.Copy(sourcePath, baselinePath, overwrite: true);
        File.Copy(baselinePath, noopPath, overwrite: true);

        byte[] baseline = File.ReadAllBytes(baselinePath);
        byte[] noop = File.ReadAllBytes(noopPath);
        ValidateContainer(baseline, "baseline copy");
        ValidateContainer(noop, "noop copy");

        MissionScriptSlotBitsetMask mask = MissionScriptSlotBitsetSaveCodec.BuildSingleDwordMask(TargetSlots);
        byte[] set = baseline.ToArray();
        uint baselineDword = ReadU32(set, mask.TrueViewDwordOffset);
        bool selectedBitsInitiallyClear = (baselineDword & mask.Mask) == 0;
        MissionScriptSlotBitsetSaveCodec.SetSlotsInSingleDword(set, TargetSlots, enabled: true);
        File.WriteAllBytes(setPath, set);

        byte[] idempotent = set.ToArray();
        MissionScriptSlotBitsetSaveCodec.SetSlotsInSingleDword(idempotent, TargetSlots, enabled: true);
        File.WriteAllBytes(idempotentPath, idempotent);

        byte[] clear = set.ToArray();
        MissionScriptSlotBitsetSaveCodec.SetSlotsInSingleDword(clear, TargetSlots, enabled: false);
        File.WriteAllBytes(clearPath, clear);

        byte[] sourceAfter = File.ReadAllBytes(sourcePath);
        foreach ((string Label, byte[] Data) row in new[]
                 {
                     ("set", set),
                     ("idempotent", idempotent),
                     ("clear", clear)
                 })
        {
            ValidateContainer(row.Data, row.Label);
        }

        int[] sourceToBaseline = ChangedOffsets(source, baseline);
        int[] baselineToNoop = ChangedOffsets(baseline, noop);
        int[] baselineToSet = ChangedOffsets(baseline, set);
        int[] setToIdempotent = ChangedOffsets(set, idempotent);
        int[] setToClear = ChangedOffsets(set, clear);
        int[] clearToBaseline = ChangedOffsets(clear, baseline);
        uint setDword = ReadU32(set, mask.TrueViewDwordOffset);
        uint clearDword = ReadU32(clear, mask.TrueViewDwordOffset);
        uint observedXor = baselineDword ^ setDword;
        uint clearXor = setDword ^ clearDword;
        int[] unexpectedOffsets = baselineToSet
            .Where(offset => offset < mask.TrueViewDwordOffset || offset > mask.TrueViewDwordEndOffset)
            .ToArray();
        int[] trapHits = baselineToSet
            .Where(offset => LegacyTrapOffsets.Contains(offset))
            .ToArray();
        Dictionary<string, bool> preservation = PreserveRanges.ToDictionary(
            row => row.Key,
            row => baseline.AsSpan(row.Value.Start, row.Value.End - row.Value.Start)
                .SequenceEqual(set.AsSpan(row.Value.Start, row.Value.End - row.Value.Start)));

        Evidence evidence = new()
        {
            SchemaVersion = SchemaVersion,
            Status = "PASS",
            EvidenceRoot = ToRepoRelative(repoRoot, outRoot),
            SourceCopiedBaseline = new SourceInfo
            {
                Class = "validated copied real career .bes baseline from prior ignored evidence",
                RelativePath = ToRepoRelative(repoRoot, sourcePath),
                Size = source.Length,
                VersionWord = Hex16(ReadVersionWord(source)),
                Sha256 = Sha256(source)
            },
            Harness = new HarnessInfo
            {
                ToolProjectPath = "tools/MissionScriptSlotBitsetSaveHarness/MissionScriptSlotBitsetSaveHarness.csproj",
                AppCoreCodecPath = "OnslaughtCareerEditor.AppCore/MissionScriptSlotBitsetSaveCodec.cs",
                InterfaceKind = "AppCore codec applied by proof-only copied-baseline harness",
                AppCoreCodecUsed = true,
                ManualSlotDwordWriteInHarness = false,
                ProductUiWired = false,
                AppCoreCodecFileIo = false,
                HarnessFileIo = true,
                SourceBaselineRead = true,
                PrivateArtifactMaterialized = true
            },
            Provenance = new ProvenanceInfo
            {
                CopyBeforeWrite = true,
                SourceAndOutputPathsDistinct = !PathsEqual(sourcePath, baselinePath),
                SourceToNewBaselineDiffCount = sourceToBaseline.Length,
                SourceUnchanged = source.SequenceEqual(sourceAfter)
            },
            CopiedArtifacts =
            [
                FileRow(repoRoot, "appcore slot baseline", baselinePath, baseline),
                FileRow(repoRoot, "appcore slot noop", noopPath, noop),
                FileRow(repoRoot, "appcore slot61/62 set", setPath, set),
                FileRow(repoRoot, "appcore slot61/62 idempotent set", idempotentPath, idempotent),
                FileRow(repoRoot, "appcore slot61/62 clear roundtrip", clearPath, clear)
            ],
            Container = new ContainerInfo
            {
                ExpectedSize = MissionScriptSlotBitsetSaveCodec.ExpectedFileSize,
                ExpectedSizeHex = Hex(MissionScriptSlotBitsetSaveCodec.ExpectedFileSize, 4),
                VersionWord = Hex16(MissionScriptSlotBitsetSaveCodec.VersionWord),
                TrueViewRule = "file_offset = 0x0002 + career_offset",
                FileSizePreserved = new[] { baseline, noop, set, idempotent, clear }
                    .All(data => data.Length == MissionScriptSlotBitsetSaveCodec.ExpectedFileSize),
                VersionWordPreserved = new[] { baseline, noop, set, idempotent, clear }
                    .All(data => ReadVersionWord(data) == MissionScriptSlotBitsetSaveCodec.VersionWord)
            },
            SlotWrite = new SlotWriteInfo
            {
                Slots = TargetSlots,
                DwordIndex = mask.DwordIndex,
                AllowedDwordRange = $"{Hex(mask.TrueViewDwordOffset, 4)}-{Hex(mask.TrueViewDwordEndOffset, 4)}",
                AllowedDwordXorMask = Hex(mask.Mask, 8),
                Slot61Mask = Hex(MissionScriptSlotBitsetSaveCodec.GetVector(61).BitMask, 8),
                Slot62Mask = Hex(MissionScriptSlotBitsetSaveCodec.GetVector(62).BitMask, 8),
                ComparisonMode = "little-endian dword XOR mask subset, not single-byte expectation",
                BaselineDword1Before = Hex(baselineDword, 8),
                BaselineSelectedMaskInitiallyClear = selectedBitsInitiallyClear,
                SetDword1After = Hex(setDword, 8),
                ObservedDwordXorMask = Hex(observedXor, 8),
                ClearDwordXorMask = Hex(clearXor, 8),
                BaselineToSetChangedOffsets = baselineToSet.Select(offset => Hex(offset, 4)).ToArray(),
                BaselineToSetChangedOffsetCount = baselineToSet.Length,
                ExpectedChangedOffsets = new[] { Hex(0x2411, 4) },
                UnexpectedOffsets = unexpectedOffsets.Select(offset => Hex(offset, 4)).ToArray(),
                UnexpectedDiffCount = unexpectedOffsets.Length,
                LegacyTrapHits = trapHits.Select(offset => Hex(offset, 4)).ToArray(),
                LegacyTrapHitCount = trapHits.Length,
                SetChangedTargetBits = observedXor == mask.Mask,
                PreservedNonTargetBitsInDword = (baselineDword & ~mask.Mask) == (setDword & ~mask.Mask),
                Slot61AfterSet = MissionScriptSlotBitsetSaveCodec.GetSlot(set, 61),
                Slot62AfterSet = MissionScriptSlotBitsetSaveCodec.GetSlot(set, 62),
                Slot61AfterClear = MissionScriptSlotBitsetSaveCodec.GetSlot(clear, 61),
                Slot62AfterClear = MissionScriptSlotBitsetSaveCodec.GetSlot(clear, 62)
            },
            NoOpAndRoundTrip = new RoundTripInfo
            {
                BaselineToNoopDiffCount = baselineToNoop.Length,
                SetToIdempotentDiffCount = setToIdempotent.Length,
                SetToClearChangedOffsets = setToClear.Select(offset => Hex(offset, 4)).ToArray(),
                SetToClearDiffCount = setToClear.Length,
                SetToClearDwordXorMask = Hex(clearXor, 8),
                ClearToBaselineDiffCount = clearToBaseline.Length
            },
            Preservation = preservation,
            NegativeGuards = new NegativeGuardInfo
            {
                SaveSynthesis = false,
                InstalledGameMutation = false,
                OriginalExecutableMutation = false,
                DefaultoptionsMutation = false,
                RuntimeExecution = false,
                BeLaunch = false,
                GhidraMutation = false,
                ExecutablePatching = false,
                GodotWork = false,
                ProductUiWired = false,
                LegacyAlignedViewTrapOffsets = LegacyTrapOffsets.Select(offset => Hex(offset, 4)).ToArray(),
                LegacyTrapHitCount = trapHits.Length
            }
        };

        ValidateEvidence(evidence);
        return evidence;
    }

    private static BoundaryEvidence MaterializeBoundaryCorpusEvidence(string repoRoot, string sourcePath, string outRoot)
    {
        byte[] source = File.ReadAllBytes(sourcePath);
        ValidateContainer(source, "source copied career baseline");

        string baselinePath = Path.Combine(outRoot, BoundaryBaselineFileName);
        string noopPath = Path.Combine(outRoot, BoundaryNoopFileName);
        string[] samplePaths = BoundaryVectorSlots
            .Select(slot => Path.Combine(outRoot, string.Format(BoundarySampleFileFormat, slot)))
            .ToArray();

        foreach (string outputPath in new[] { baselinePath, noopPath }.Concat(samplePaths))
        {
            if (PathsEqual(sourcePath, outputPath))
            {
                throw new InvalidOperationException("Source and output paths must be distinct.");
            }
        }

        File.Copy(sourcePath, baselinePath, overwrite: true);
        File.Copy(baselinePath, noopPath, overwrite: true);

        byte[] baseline = File.ReadAllBytes(baselinePath);
        byte[] noop = File.ReadAllBytes(noopPath);
        ValidateContainer(baseline, "boundary baseline copy");
        ValidateContainer(noop, "boundary noop copy");

        int[] sourceToBaseline = ChangedOffsets(source, baseline);
        int[] baselineToNoop = ChangedOffsets(baseline, noop);
        byte[] sourceAfter = File.ReadAllBytes(sourcePath);

        BoundaryPairInfo[] boundaryPairs = BuildBoundaryPairs(baseline);
        BoundarySlotRoundTripInfo slotRoundTrip = RunSingleSlotRoundTrips(repoRoot, baseline, samplePaths);
        ArtifactInfo[] artifacts = new[]
        {
            FileRow(repoRoot, "boundary corpus baseline", baselinePath, baseline),
            FileRow(repoRoot, "boundary corpus noop", noopPath, noop)
        }.Concat(samplePaths.Select((path, index) =>
        {
            byte[] data = File.ReadAllBytes(path);
            return FileRow(repoRoot, $"boundary corpus sample slot {BoundaryVectorSlots[index]}", path, data);
        })).ToArray();

        BoundaryEvidence evidence = new()
        {
            SchemaVersion = BoundarySchemaVersion,
            Status = "PASS",
            EvidenceRoot = ToRepoRelative(repoRoot, outRoot),
            SourceCopiedBaseline = new SourceInfo
            {
                Class = "validated copied real career .bes baseline from prior ignored evidence",
                RelativePath = ToRepoRelative(repoRoot, sourcePath),
                Size = source.Length,
                VersionWord = Hex16(ReadVersionWord(source)),
                Sha256 = Sha256(source)
            },
            Harness = new HarnessInfo
            {
                ToolProjectPath = "tools/MissionScriptSlotBitsetSaveHarness/MissionScriptSlotBitsetSaveHarness.csproj",
                AppCoreCodecPath = "OnslaughtCareerEditor.AppCore/MissionScriptSlotBitsetSaveCodec.cs",
                InterfaceKind = "AppCore codec boundary corpus applied by proof-only copied-baseline harness",
                AppCoreCodecUsed = true,
                ManualSlotDwordWriteInHarness = false,
                ProductUiWired = false,
                AppCoreCodecFileIo = false,
                HarnessFileIo = true,
                SourceBaselineRead = true,
                PrivateArtifactMaterialized = true
            },
            Provenance = new ProvenanceInfo
            {
                CopyBeforeWrite = true,
                SourceAndOutputPathsDistinct = new[] { baselinePath, noopPath }.Concat(samplePaths).All(path => !PathsEqual(sourcePath, path)),
                SourceToNewBaselineDiffCount = sourceToBaseline.Length,
                SourceUnchanged = source.SequenceEqual(sourceAfter)
            },
            CopiedArtifacts = artifacts,
            Container = new ContainerInfo
            {
                ExpectedSize = MissionScriptSlotBitsetSaveCodec.ExpectedFileSize,
                ExpectedSizeHex = Hex(MissionScriptSlotBitsetSaveCodec.ExpectedFileSize, 4),
                VersionWord = Hex16(MissionScriptSlotBitsetSaveCodec.VersionWord),
                TrueViewRule = "file_offset = 0x0002 + career_offset",
                FileSizePreserved = artifacts.All(row => row.Size == MissionScriptSlotBitsetSaveCodec.ExpectedFileSize),
                VersionWordPreserved = artifacts.All(row => row.VersionWord == Hex16(MissionScriptSlotBitsetSaveCodec.VersionWord))
            },
            Corpus = new BoundaryCorpusInfo
            {
                ExistingSeedVectorCaseCount = 5,
                BoundaryPairMaskCaseCount = boundaryPairs.Length,
                SingleSlotRoundTripCaseCount = MissionScriptSlotBitsetSaveCodec.SlotCount,
                BoundaryVectorSlots = BoundaryVectorSlots,
                BoundaryPairMask = "0x80000001",
                BoundaryPairExpectedSetXorMode = "(~baselineDword) & mask",
                BoundaryPairDwordOffsets = boundaryPairs.Select(row => row.TrueViewDwordOffset).ToArray(),
                BoundaryPairs = boundaryPairs,
                AllBoundaryPairMasksMatch = boundaryPairs.All(row => row.Mask == "0x80000001"),
                AllBoundaryPairSetXorMatchesBaselineState = boundaryPairs.All(row => row.ObservedSetXorMask == row.ExpectedSetXorMask),
                AllBoundaryPairRestoresToBaseline = boundaryPairs.All(row => row.RestoreToBaselineDiffCount == 0),
                AllValidSlotsRoundTrip = slotRoundTrip.AllValidSlotsRoundTrip,
                ToggleTouchesOnlyExpectedByteForAllValidSlots = slotRoundTrip.ToggleTouchesOnlyExpectedByteForAllValidSlots,
                ToggleIdempotentForAllValidSlots = slotRoundTrip.ToggleIdempotentForAllValidSlots,
                RestoreToBaselineForAllValidSlots = slotRoundTrip.RestoreToBaselineForAllValidSlots,
                SampleBoundaryArtifactCount = BoundaryVectorSlots.Length,
                CrossDwordMaskRejected = ThrowsArgumentException(() => MissionScriptSlotBitsetSaveCodec.BuildSingleDwordMask(stackalloc int[] { 63, 64 })),
                InvalidSlotLowerBoundRejected = ThrowsArgumentOutOfRange(() => MissionScriptSlotBitsetSaveCodec.GetVector(-1)),
                InvalidSlotUpperBoundRejected = ThrowsArgumentOutOfRange(() => MissionScriptSlotBitsetSaveCodec.GetVector(MissionScriptSlotBitsetSaveCodec.SlotCount)),
                Slot256Rejected = ThrowsArgumentOutOfRange(() => MissionScriptSlotBitsetSaveCodec.GetVector(256)),
                WrongSizeRejected = !MissionScriptSlotBitsetSaveCodec.IsValidCareerSaveContainer(baseline.AsSpan(0, baseline.Length - 1)),
                WrongVersionRejected = WrongVersionRejected(baseline)
            },
            NoOp = new BoundaryNoOpInfo
            {
                BaselineToNoopDiffCount = baselineToNoop.Length
            },
            Preservation = new BoundaryPreservationInfo
            {
                ReservedSlotTailAfterUsedDwordsUnchangedForAllValidSlots = slotRoundTrip.ReservedSlotTailAfterUsedDwordsUnchangedForAllValidSlots,
                PostSlotFieldsThroughPreOptionsUnchangedForAllValidSlots = slotRoundTrip.PostSlotFieldsThroughPreOptionsUnchangedForAllValidSlots,
                OptionsEntriesUnchangedForAllValidSlots = slotRoundTrip.OptionsEntriesUnchangedForAllValidSlots,
                OptionsTailUnchangedForAllValidSlots = slotRoundTrip.OptionsTailUnchangedForAllValidSlots,
                LegacyTrapHitCount = slotRoundTrip.LegacyTrapHitCount,
                UnexpectedDiffCount = slotRoundTrip.UnexpectedDiffCount
            },
            NegativeGuards = new NegativeGuardInfo
            {
                SaveSynthesis = false,
                InstalledGameMutation = false,
                OriginalExecutableMutation = false,
                DefaultoptionsMutation = false,
                RuntimeExecution = false,
                BeLaunch = false,
                GhidraMutation = false,
                ExecutablePatching = false,
                GodotWork = false,
                ProductUiWired = false,
                LegacyAlignedViewTrapOffsets = LegacyTrapOffsets.Select(offset => Hex(offset, 4)).ToArray(),
                LegacyTrapHitCount = slotRoundTrip.LegacyTrapHitCount
            }
        };

        ValidateBoundaryEvidence(evidence);
        return evidence;
    }

    private static BoundaryPairInfo[] BuildBoundaryPairs(byte[] baseline)
    {
        List<BoundaryPairInfo> rows = [];
        for (int dwordIndex = 0; dwordIndex < MissionScriptSlotBitsetSaveCodec.UsedSlotDwords; dwordIndex++)
        {
            int firstSlot = dwordIndex * 32;
            int lastSlot = firstSlot + 31;
            int[] pairSlots = [firstSlot, lastSlot];
            MissionScriptSlotBitsetMask mask = MissionScriptSlotBitsetSaveCodec.BuildSingleDwordMask(pairSlots);
            byte[] set = baseline.ToArray();
            uint baselineDword = ReadU32(baseline, mask.TrueViewDwordOffset);
            MissionScriptSlotBitsetSaveCodec.SetSlotsInSingleDword(set, pairSlots, enabled: true);
            uint setDword = ReadU32(set, mask.TrueViewDwordOffset);
            uint expectedSetXor = ~baselineDword & mask.Mask;
            uint observedSetXor = baselineDword ^ setDword;

            byte[] idempotent = set.ToArray();
            MissionScriptSlotBitsetSaveCodec.SetSlotsInSingleDword(idempotent, pairSlots, enabled: true);

            byte[] restore = set.ToArray();
            MissionScriptSlotBitsetSaveCodec.SetSlot(restore, firstSlot, MissionScriptSlotBitsetSaveCodec.GetSlot(baseline, firstSlot));
            MissionScriptSlotBitsetSaveCodec.SetSlot(restore, lastSlot, MissionScriptSlotBitsetSaveCodec.GetSlot(baseline, lastSlot));

            int[] setOffsets = ChangedOffsets(baseline, set);
            int[] unexpectedOffsets = setOffsets
                .Where(offset => offset < mask.TrueViewDwordOffset || offset > mask.TrueViewDwordEndOffset)
                .ToArray();

            rows.Add(new BoundaryPairInfo
            {
                Slots = [firstSlot, lastSlot],
                DwordIndex = mask.DwordIndex,
                TrueViewDwordOffset = Hex(mask.TrueViewDwordOffset, 4),
                TrueViewDwordEndOffset = Hex(mask.TrueViewDwordEndOffset, 4),
                Mask = Hex(mask.Mask, 8),
                ExpectedSetXorMask = Hex(expectedSetXor, 8),
                ObservedSetXorMask = Hex(observedSetXor, 8),
                SetDiffCount = setOffsets.Length,
                UnexpectedDiffCount = unexpectedOffsets.Length,
                IdempotentDiffCount = ChangedOffsets(set, idempotent).Length,
                RestoreToBaselineDiffCount = ChangedOffsets(baseline, restore).Length
            });
        }

        return rows.ToArray();
    }

    private static BoundarySlotRoundTripInfo RunSingleSlotRoundTrips(string repoRoot, byte[] baseline, string[] samplePaths)
    {
        int unexpectedDiffCount = 0;
        int legacyTrapHitCount = 0;
        int failedReadbackCount = 0;
        int idempotentDiffCount = 0;
        int restoreDiffCount = 0;
        int wrongByteDiffCount = 0;
        int reservedTailChangedCount = 0;
        int postSlotChangedCount = 0;
        int optionsEntriesChangedCount = 0;
        int optionsTailChangedCount = 0;

        Dictionary<int, string> samplePathBySlot = BoundaryVectorSlots
            .Select((slot, index) => (slot, path: samplePaths[index]))
            .ToDictionary(row => row.slot, row => row.path);

        for (int slot = 0; slot < MissionScriptSlotBitsetSaveCodec.SlotCount; slot++)
        {
            MissionScriptSlotBitsetVector vector = MissionScriptSlotBitsetSaveCodec.GetVector(slot);
            bool original = MissionScriptSlotBitsetSaveCodec.GetSlot(baseline, slot);
            byte[] toggled = baseline.ToArray();
            MissionScriptSlotBitsetSaveCodec.SetSlot(toggled, slot, !original);

            int[] changedOffsets = ChangedOffsets(baseline, toggled);
            bool expectedSingleByte = changedOffsets.Length == 1
                && changedOffsets[0] == vector.LittleEndianByteOffset
                && (byte)(baseline[vector.LittleEndianByteOffset] ^ toggled[vector.LittleEndianByteOffset]) == vector.LittleEndianByteMask;
            if (!expectedSingleByte)
            {
                wrongByteDiffCount++;
            }

            if (MissionScriptSlotBitsetSaveCodec.GetSlot(toggled, slot) != !original)
            {
                failedReadbackCount++;
            }

            unexpectedDiffCount += changedOffsets.Count(offset => offset != vector.LittleEndianByteOffset);
            legacyTrapHitCount += changedOffsets.Count(offset =>
                LegacyTrapOffsets.Contains(offset) && offset != vector.LittleEndianByteOffset);
            reservedTailChangedCount += CountChangedInRange(baseline, toggled, 0x242A, 0x248A);
            postSlotChangedCount += CountChangedInRange(baseline, toggled, 0x248A, 0x24BE);
            optionsEntriesChangedCount += CountChangedInRange(baseline, toggled, 0x24BE, 0x26BE);
            optionsTailChangedCount += CountChangedInRange(baseline, toggled, 0x26BE, 0x2714);

            byte[] idempotent = toggled.ToArray();
            MissionScriptSlotBitsetSaveCodec.SetSlot(idempotent, slot, !original);
            idempotentDiffCount += ChangedOffsets(toggled, idempotent).Length;

            byte[] restore = toggled.ToArray();
            MissionScriptSlotBitsetSaveCodec.SetSlot(restore, slot, original);
            restoreDiffCount += ChangedOffsets(baseline, restore).Length;

            if (samplePathBySlot.TryGetValue(slot, out string? samplePath))
            {
                File.WriteAllBytes(samplePath, toggled);
            }
        }

        return new BoundarySlotRoundTripInfo
        {
            AllValidSlotsRoundTrip = failedReadbackCount == 0,
            ToggleTouchesOnlyExpectedByteForAllValidSlots = wrongByteDiffCount == 0,
            ToggleIdempotentForAllValidSlots = idempotentDiffCount == 0,
            RestoreToBaselineForAllValidSlots = restoreDiffCount == 0,
            FailedReadbackCount = failedReadbackCount,
            WrongByteDiffCount = wrongByteDiffCount,
            IdempotentDiffCount = idempotentDiffCount,
            RestoreDiffCount = restoreDiffCount,
            UnexpectedDiffCount = unexpectedDiffCount,
            LegacyTrapHitCount = legacyTrapHitCount,
            ReservedSlotTailAfterUsedDwordsUnchangedForAllValidSlots = reservedTailChangedCount == 0,
            PostSlotFieldsThroughPreOptionsUnchangedForAllValidSlots = postSlotChangedCount == 0,
            OptionsEntriesUnchangedForAllValidSlots = optionsEntriesChangedCount == 0,
            OptionsTailUnchangedForAllValidSlots = optionsTailChangedCount == 0
        };
    }

    private static void ValidateBoundaryEvidence(BoundaryEvidence evidence)
    {
        List<string> failures = [];
        if (evidence.Status != "PASS")
        {
            failures.Add("status mismatch");
        }

        if (!evidence.Container.FileSizePreserved || !evidence.Container.VersionWordPreserved)
        {
            failures.Add("container preservation mismatch");
        }

        if (!evidence.Provenance.CopyBeforeWrite ||
            !evidence.Provenance.SourceAndOutputPathsDistinct ||
            evidence.Provenance.SourceToNewBaselineDiffCount != 0 ||
            !evidence.Provenance.SourceUnchanged)
        {
            failures.Add("provenance guard mismatch");
        }

        if (!evidence.Corpus.AllBoundaryPairMasksMatch ||
            !evidence.Corpus.AllBoundaryPairSetXorMatchesBaselineState ||
            !evidence.Corpus.AllBoundaryPairRestoresToBaseline ||
            !evidence.Corpus.AllValidSlotsRoundTrip ||
            !evidence.Corpus.ToggleTouchesOnlyExpectedByteForAllValidSlots ||
            !evidence.Corpus.ToggleIdempotentForAllValidSlots ||
            !evidence.Corpus.RestoreToBaselineForAllValidSlots ||
            !evidence.Corpus.CrossDwordMaskRejected ||
            !evidence.Corpus.InvalidSlotLowerBoundRejected ||
            !evidence.Corpus.InvalidSlotUpperBoundRejected ||
            !evidence.Corpus.Slot256Rejected ||
            !evidence.Corpus.WrongSizeRejected ||
            !evidence.Corpus.WrongVersionRejected)
        {
            failures.Add("corpus guard mismatch");
        }

        if (evidence.NoOp.BaselineToNoopDiffCount != 0 ||
            evidence.Preservation.LegacyTrapHitCount != 0 ||
            evidence.Preservation.UnexpectedDiffCount != 0 ||
            !evidence.Preservation.ReservedSlotTailAfterUsedDwordsUnchangedForAllValidSlots ||
            !evidence.Preservation.PostSlotFieldsThroughPreOptionsUnchangedForAllValidSlots ||
            !evidence.Preservation.OptionsEntriesUnchangedForAllValidSlots ||
            !evidence.Preservation.OptionsTailUnchangedForAllValidSlots)
        {
            failures.Add("preservation guard mismatch");
        }

        if (failures.Count > 0)
        {
            throw new InvalidOperationException(string.Join("; ", failures));
        }
    }

    private static void ValidateEvidence(Evidence evidence)
    {
        List<string> failures = [];
        if (evidence.Status != "PASS")
        {
            failures.Add("status mismatch");
        }

        if (!evidence.Container.FileSizePreserved || !evidence.Container.VersionWordPreserved)
        {
            failures.Add("container preservation mismatch");
        }

        if (!evidence.Provenance.CopyBeforeWrite ||
            !evidence.Provenance.SourceAndOutputPathsDistinct ||
            evidence.Provenance.SourceToNewBaselineDiffCount != 0 ||
            !evidence.Provenance.SourceUnchanged)
        {
            failures.Add("provenance guard mismatch");
        }

        if (!evidence.SlotWrite.BaselineSelectedMaskInitiallyClear ||
            evidence.SlotWrite.ObservedDwordXorMask != "0x60000000" ||
            evidence.SlotWrite.BaselineToSetChangedOffsets.Length != 1 ||
            evidence.SlotWrite.BaselineToSetChangedOffsets[0] != "0x2411" ||
            evidence.SlotWrite.UnexpectedDiffCount != 0 ||
            evidence.SlotWrite.LegacyTrapHitCount != 0 ||
            !evidence.SlotWrite.SetChangedTargetBits ||
            !evidence.SlotWrite.PreservedNonTargetBitsInDword ||
            !evidence.SlotWrite.Slot61AfterSet ||
            !evidence.SlotWrite.Slot62AfterSet ||
            evidence.SlotWrite.Slot61AfterClear ||
            evidence.SlotWrite.Slot62AfterClear)
        {
            failures.Add("slot write guard mismatch");
        }

        if (evidence.NoOpAndRoundTrip.BaselineToNoopDiffCount != 0 ||
            evidence.NoOpAndRoundTrip.SetToIdempotentDiffCount != 0 ||
            evidence.NoOpAndRoundTrip.ClearToBaselineDiffCount != 0)
        {
            failures.Add("roundtrip guard mismatch");
        }

        if (evidence.Preservation.Values.Any(value => !value))
        {
            failures.Add("preservation guard mismatch");
        }

        if (failures.Count > 0)
        {
            throw new InvalidOperationException(string.Join("; ", failures));
        }
    }

    private static Options ParseArgs(string[] args)
    {
        Options options = new();
        for (int index = 0; index < args.Length; index++)
        {
            string arg = args[index];
            if (arg is "-h" or "--help")
            {
                options.ShowHelp = true;
                continue;
            }

            if (arg == "--repo-root")
            {
                options.RepoRoot = RequireValue(args, ref index, arg);
                continue;
            }

            if (arg == "--source")
            {
                options.SourcePath = RequireValue(args, ref index, arg);
                continue;
            }

            if (arg == "--out-root")
            {
                options.OutRoot = RequireValue(args, ref index, arg);
                continue;
            }

            if (arg == "--mode")
            {
                options.Mode = ParseMode(RequireValue(args, ref index, arg));
                continue;
            }

            throw new ArgumentException($"Unsupported argument: {arg}");
        }

        return options;
    }

    private static HarnessMode ParseMode(string value)
    {
        return value switch
        {
            "seed-61-62" => HarnessMode.SeedSlots61And62,
            "boundary-corpus" => HarnessMode.BoundaryCorpus,
            _ => throw new ArgumentException($"Unsupported --mode value: {value}")
        };
    }

    private static string RequireValue(string[] args, ref int index, string option)
    {
        if (index + 1 >= args.Length)
        {
            throw new ArgumentException($"{option} requires a value.");
        }

        index++;
        return args[index];
    }

    private static string RequirePath(string? path, string label)
    {
        if (string.IsNullOrWhiteSpace(path))
        {
            throw new ArgumentException($"--{label} is required.");
        }

        return Path.GetFullPath(path);
    }

    private static void WriteUsage()
    {
        Console.WriteLine("MissionScriptSlotBitsetSaveHarness --source <copied-baseline.bes> [--mode seed-61-62|boundary-corpus] [--out-root <private-root>] [--repo-root <repo-root>]");
    }

    private static bool IsWithinDirectory(string path, string directory)
    {
        string fullPath = Path.GetFullPath(path).TrimEnd(Path.DirectorySeparatorChar, Path.AltDirectorySeparatorChar) + Path.DirectorySeparatorChar;
        string fullDirectory = Path.GetFullPath(directory).TrimEnd(Path.DirectorySeparatorChar, Path.AltDirectorySeparatorChar) + Path.DirectorySeparatorChar;
        return fullPath.StartsWith(fullDirectory, StringComparison.OrdinalIgnoreCase);
    }

    private static bool PathsEqual(string left, string right)
    {
        return string.Equals(Path.GetFullPath(left).TrimEnd(Path.DirectorySeparatorChar, Path.AltDirectorySeparatorChar),
            Path.GetFullPath(right).TrimEnd(Path.DirectorySeparatorChar, Path.AltDirectorySeparatorChar),
            StringComparison.OrdinalIgnoreCase);
    }

    private static string ToRepoRelative(string repoRoot, string path)
    {
        return Path.GetRelativePath(repoRoot, path).Replace('\\', '/');
    }

    private static void ValidateContainer(byte[] data, string label)
    {
        if (!MissionScriptSlotBitsetSaveCodec.IsValidCareerSaveContainer(data))
        {
            throw new InvalidOperationException($"{label} is not a valid 10004-byte 0x4BD1 career save container.");
        }
    }

    private static ushort ReadVersionWord(byte[] data)
    {
        return BinaryPrimitives.ReadUInt16LittleEndian(data.AsSpan(0, 2));
    }

    private static uint ReadU32(byte[] data, int offset)
    {
        return BinaryPrimitives.ReadUInt32LittleEndian(data.AsSpan(offset, 4));
    }

    private static int[] ChangedOffsets(byte[] before, byte[] after)
    {
        if (before.Length != after.Length)
        {
            throw new InvalidOperationException("Cannot diff buffers with different lengths.");
        }

        return before.Select((value, index) => value == after[index] ? -1 : index)
            .Where(index => index >= 0)
            .ToArray();
    }

    private static int CountChangedInRange(byte[] before, byte[] after, int start, int endExclusive)
    {
        int count = 0;
        for (int offset = start; offset < endExclusive; offset++)
        {
            if (before[offset] != after[offset])
            {
                count++;
            }
        }

        return count;
    }

    private static bool ThrowsArgumentException(Action action)
    {
        try
        {
            action();
            return false;
        }
        catch (ArgumentException)
        {
            return true;
        }
    }

    private static bool ThrowsArgumentOutOfRange(Action action)
    {
        try
        {
            action();
            return false;
        }
        catch (ArgumentOutOfRangeException)
        {
            return true;
        }
    }

    private static bool WrongVersionRejected(byte[] baseline)
    {
        byte[] wrongVersion = baseline.ToArray();
        wrongVersion[0] ^= 0xff;
        return !MissionScriptSlotBitsetSaveCodec.IsValidCareerSaveContainer(wrongVersion);
    }

    private static string Sha256(byte[] data)
    {
        return Convert.ToHexString(SHA256.HashData(data)).ToLowerInvariant();
    }

    private static string Hex(long value, int digits)
    {
        return $"0x{value.ToString($"X{digits}")}";
    }

    private static string Hex16(ushort value)
    {
        return Hex(value, 4);
    }

    private static ArtifactInfo FileRow(string repoRoot, string label, string path, byte[] data)
    {
        return new ArtifactInfo
        {
            Label = label,
            RelativePath = ToRepoRelative(repoRoot, path),
            Size = data.Length,
            VersionWord = Hex16(ReadVersionWord(data)),
            Sha256 = Sha256(data)
        };
    }

    private sealed class Options
    {
        public bool ShowHelp { get; set; }
        public string? RepoRoot { get; set; }
        public string? SourcePath { get; set; }
        public string? OutRoot { get; set; }
        public HarnessMode Mode { get; set; } = HarnessMode.SeedSlots61And62;
    }

    private enum HarnessMode
    {
        SeedSlots61And62,
        BoundaryCorpus
    }

    private sealed class Evidence
    {
        public string SchemaVersion { get; set; } = "";
        public string Status { get; set; } = "";
        public string EvidenceRoot { get; set; } = "";
        public SourceInfo SourceCopiedBaseline { get; set; } = new();
        public HarnessInfo Harness { get; set; } = new();
        public ProvenanceInfo Provenance { get; set; } = new();
        public ArtifactInfo[] CopiedArtifacts { get; set; } = [];
        public ContainerInfo Container { get; set; } = new();
        public SlotWriteInfo SlotWrite { get; set; } = new();
        public RoundTripInfo NoOpAndRoundTrip { get; set; } = new();
        public Dictionary<string, bool> Preservation { get; set; } = new();
        public NegativeGuardInfo NegativeGuards { get; set; } = new();
    }

    private sealed class BoundaryEvidence
    {
        public string SchemaVersion { get; set; } = "";
        public string Status { get; set; } = "";
        public string EvidenceRoot { get; set; } = "";
        public SourceInfo SourceCopiedBaseline { get; set; } = new();
        public HarnessInfo Harness { get; set; } = new();
        public ProvenanceInfo Provenance { get; set; } = new();
        public ArtifactInfo[] CopiedArtifacts { get; set; } = [];
        public ContainerInfo Container { get; set; } = new();
        public BoundaryCorpusInfo Corpus { get; set; } = new();
        public BoundaryNoOpInfo NoOp { get; set; } = new();
        public BoundaryPreservationInfo Preservation { get; set; } = new();
        public NegativeGuardInfo NegativeGuards { get; set; } = new();
    }

    private sealed class SourceInfo
    {
        public string Class { get; set; } = "";
        public string RelativePath { get; set; } = "";
        public int Size { get; set; }
        public string VersionWord { get; set; } = "";
        public string Sha256 { get; set; } = "";
    }

    private sealed class HarnessInfo
    {
        public string ToolProjectPath { get; set; } = "";
        public string AppCoreCodecPath { get; set; } = "";
        public string InterfaceKind { get; set; } = "";
        public bool AppCoreCodecUsed { get; set; }
        public bool ManualSlotDwordWriteInHarness { get; set; }
        public bool ProductUiWired { get; set; }
        public bool AppCoreCodecFileIo { get; set; }
        public bool HarnessFileIo { get; set; }
        public bool SourceBaselineRead { get; set; }
        public bool PrivateArtifactMaterialized { get; set; }
    }

    private sealed class ProvenanceInfo
    {
        public bool CopyBeforeWrite { get; set; }
        public bool SourceAndOutputPathsDistinct { get; set; }
        public int SourceToNewBaselineDiffCount { get; set; }
        public bool SourceUnchanged { get; set; }
    }

    private sealed class ArtifactInfo
    {
        public string Label { get; set; } = "";
        public string RelativePath { get; set; } = "";
        public int Size { get; set; }
        public string VersionWord { get; set; } = "";
        public string Sha256 { get; set; } = "";
    }

    private sealed class ContainerInfo
    {
        public int ExpectedSize { get; set; }
        public string ExpectedSizeHex { get; set; } = "";
        public string VersionWord { get; set; } = "";
        public string TrueViewRule { get; set; } = "";
        public bool FileSizePreserved { get; set; }
        public bool VersionWordPreserved { get; set; }
    }

    private sealed class SlotWriteInfo
    {
        public int[] Slots { get; set; } = [];
        public int DwordIndex { get; set; }
        public string AllowedDwordRange { get; set; } = "";
        public string AllowedDwordXorMask { get; set; } = "";
        public string Slot61Mask { get; set; } = "";
        public string Slot62Mask { get; set; } = "";
        public string ComparisonMode { get; set; } = "";
        public string BaselineDword1Before { get; set; } = "";
        public bool BaselineSelectedMaskInitiallyClear { get; set; }
        public string SetDword1After { get; set; } = "";
        public string ObservedDwordXorMask { get; set; } = "";
        public string ClearDwordXorMask { get; set; } = "";
        public string[] BaselineToSetChangedOffsets { get; set; } = [];
        public int BaselineToSetChangedOffsetCount { get; set; }
        public string[] ExpectedChangedOffsets { get; set; } = [];
        public string[] UnexpectedOffsets { get; set; } = [];
        public int UnexpectedDiffCount { get; set; }
        public string[] LegacyTrapHits { get; set; } = [];
        public int LegacyTrapHitCount { get; set; }
        public bool SetChangedTargetBits { get; set; }
        public bool PreservedNonTargetBitsInDword { get; set; }
        public bool Slot61AfterSet { get; set; }
        public bool Slot62AfterSet { get; set; }
        public bool Slot61AfterClear { get; set; }
        public bool Slot62AfterClear { get; set; }
    }

    private sealed class RoundTripInfo
    {
        public int BaselineToNoopDiffCount { get; set; }
        public int SetToIdempotentDiffCount { get; set; }
        public string[] SetToClearChangedOffsets { get; set; } = [];
        public int SetToClearDiffCount { get; set; }
        public string SetToClearDwordXorMask { get; set; } = "";
        public int ClearToBaselineDiffCount { get; set; }
    }

    private sealed class BoundaryCorpusInfo
    {
        public int ExistingSeedVectorCaseCount { get; set; }
        public int BoundaryPairMaskCaseCount { get; set; }
        public int SingleSlotRoundTripCaseCount { get; set; }
        public int[] BoundaryVectorSlots { get; set; } = [];
        public string BoundaryPairMask { get; set; } = "";
        public string BoundaryPairExpectedSetXorMode { get; set; } = "";
        public string[] BoundaryPairDwordOffsets { get; set; } = [];
        public BoundaryPairInfo[] BoundaryPairs { get; set; } = [];
        public bool AllBoundaryPairMasksMatch { get; set; }
        public bool AllBoundaryPairSetXorMatchesBaselineState { get; set; }
        public bool AllBoundaryPairRestoresToBaseline { get; set; }
        public bool AllValidSlotsRoundTrip { get; set; }
        public bool ToggleTouchesOnlyExpectedByteForAllValidSlots { get; set; }
        public bool ToggleIdempotentForAllValidSlots { get; set; }
        public bool RestoreToBaselineForAllValidSlots { get; set; }
        public int SampleBoundaryArtifactCount { get; set; }
        public bool CrossDwordMaskRejected { get; set; }
        public bool InvalidSlotLowerBoundRejected { get; set; }
        public bool InvalidSlotUpperBoundRejected { get; set; }
        public bool Slot256Rejected { get; set; }
        public bool WrongSizeRejected { get; set; }
        public bool WrongVersionRejected { get; set; }
    }

    private sealed class BoundaryPairInfo
    {
        public int[] Slots { get; set; } = [];
        public int DwordIndex { get; set; }
        public string TrueViewDwordOffset { get; set; } = "";
        public string TrueViewDwordEndOffset { get; set; } = "";
        public string Mask { get; set; } = "";
        public string ExpectedSetXorMask { get; set; } = "";
        public string ObservedSetXorMask { get; set; } = "";
        public int SetDiffCount { get; set; }
        public int UnexpectedDiffCount { get; set; }
        public int IdempotentDiffCount { get; set; }
        public int RestoreToBaselineDiffCount { get; set; }
    }

    private sealed class BoundarySlotRoundTripInfo
    {
        public bool AllValidSlotsRoundTrip { get; set; }
        public bool ToggleTouchesOnlyExpectedByteForAllValidSlots { get; set; }
        public bool ToggleIdempotentForAllValidSlots { get; set; }
        public bool RestoreToBaselineForAllValidSlots { get; set; }
        public int FailedReadbackCount { get; set; }
        public int WrongByteDiffCount { get; set; }
        public int IdempotentDiffCount { get; set; }
        public int RestoreDiffCount { get; set; }
        public int UnexpectedDiffCount { get; set; }
        public int LegacyTrapHitCount { get; set; }
        public bool ReservedSlotTailAfterUsedDwordsUnchangedForAllValidSlots { get; set; }
        public bool PostSlotFieldsThroughPreOptionsUnchangedForAllValidSlots { get; set; }
        public bool OptionsEntriesUnchangedForAllValidSlots { get; set; }
        public bool OptionsTailUnchangedForAllValidSlots { get; set; }
    }

    private sealed class BoundaryNoOpInfo
    {
        public int BaselineToNoopDiffCount { get; set; }
    }

    private sealed class BoundaryPreservationInfo
    {
        public bool ReservedSlotTailAfterUsedDwordsUnchangedForAllValidSlots { get; set; }
        public bool PostSlotFieldsThroughPreOptionsUnchangedForAllValidSlots { get; set; }
        public bool OptionsEntriesUnchangedForAllValidSlots { get; set; }
        public bool OptionsTailUnchangedForAllValidSlots { get; set; }
        public int LegacyTrapHitCount { get; set; }
        public int UnexpectedDiffCount { get; set; }
    }

    private sealed class NegativeGuardInfo
    {
        public bool SaveSynthesis { get; set; }
        public bool InstalledGameMutation { get; set; }
        public bool OriginalExecutableMutation { get; set; }
        public bool DefaultoptionsMutation { get; set; }
        public bool RuntimeExecution { get; set; }
        public bool BeLaunch { get; set; }
        public bool GhidraMutation { get; set; }
        public bool ExecutablePatching { get; set; }
        public bool GodotWork { get; set; }
        public bool ProductUiWired { get; set; }
        public string[] LegacyAlignedViewTrapOffsets { get; set; } = [];
        public int LegacyTrapHitCount { get; set; }
    }
}
