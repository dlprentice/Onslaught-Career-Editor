using System.Buffers.Binary;
using System.Security.Cryptography;
using System.Text.Json;
using System.Text.Json.Serialization;
using Onslaught___Career_Editor;

namespace Onslaught___Career_Editor.Tools;

internal static class Program
{
    private const string SchemaVersion = "missionscript-goodie-state-save-appcore-copied-baseline-codec-harness-private-evidence.v1";
    private const string EvidenceRootRelative = "subagents/static-to-proof/missionscript-goodie-state-save-appcore-copied-baseline-codec-harness-proof";
    private const string SourceEvidenceRootRelative = "subagents/static-to-proof/save-options-controller-byte-preservation-copied-file-proof";
    private const string CareerSourceName = "career-baseline.bes";
    private const string DefaultOptionsSourceName = "defaultoptions-baseline.bea";
    private const string SummaryFileName = "evidence-summary.private.json";

    private const int KillsBase = 0x23F6;
    private const int TechSlotsBase = 0x240A;
    private const int TechSlotsEndExclusive = 0x248A;
    private const int OptionsEntriesStart = 0x24BE;
    private const int OptionsEntriesEnd = 0x26BE;
    private const int OptionsTailStart = 0x26BE;
    private const int OptionsTailEnd = 0x2714;

    private static readonly int[] ScriptIndices = [1, 51, 53, 68, 71, 233];
    private static readonly int[] LegacyTrapOffsets = [0x23A4, 0x22D4, 0x240C];

    private static readonly JsonSerializerOptions JsonOptions = new()
    {
        DefaultIgnoreCondition = JsonIgnoreCondition.WhenWritingNull,
        PropertyNamingPolicy = JsonNamingPolicy.CamelCase,
        WriteIndented = true
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
            string sourceRoot = Path.Combine(repoRoot, SourceEvidenceRootRelative);
            string careerSource = Path.GetFullPath(options.CareerSource ?? Path.Combine(sourceRoot, CareerSourceName));
            string defaultOptionsSource = Path.GetFullPath(options.DefaultOptionsSource ?? Path.Combine(sourceRoot, DefaultOptionsSourceName));
            string requiredOutRoot = Path.GetFullPath(Path.Combine(repoRoot, EvidenceRootRelative));
            string outRoot = Path.GetFullPath(options.OutRoot ?? requiredOutRoot);

            if (!PathsEqual(outRoot, requiredOutRoot))
            {
                throw new InvalidOperationException($"Output root must be the proof-private root: {requiredOutRoot}");
            }

            if (!IsWithinDirectory(outRoot, Path.Combine(repoRoot, "subagents", "static-to-proof")))
            {
                throw new InvalidOperationException("Output root must remain inside subagents/static-to-proof.");
            }

            if (!IsWithinDirectory(careerSource, sourceRoot) || !IsWithinDirectory(defaultOptionsSource, sourceRoot))
            {
                throw new InvalidOperationException("Sources must come from the prior copied-file proof-private evidence root.");
            }

            Evidence evidence = MaterializeEvidence(repoRoot, careerSource, defaultOptionsSource, outRoot);
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

    private static Evidence MaterializeEvidence(string repoRoot, string careerSource, string defaultOptionsSource, string outRoot)
    {
        byte[] careerSourceBefore = File.ReadAllBytes(careerSource);
        byte[] defaultOptionsSourceBefore = File.ReadAllBytes(defaultOptionsSource);
        ValidateContainer(careerSourceBefore, "career source");
        ValidateContainer(defaultOptionsSourceBefore, "defaultoptions source");

        if (Directory.Exists(outRoot))
        {
            Directory.Delete(outRoot, recursive: true);
        }
        Directory.CreateDirectory(outRoot);

        string careerBaselinePath = Path.Combine(outRoot, "career-goodie-codec-baseline.bes");
        string defaultOptionsBaselinePath = Path.Combine(outRoot, "defaultoptions-goodie-codec-baseline.bea");
        string careerNoopPath = Path.Combine(outRoot, "career-goodie-codec-noop.bes");
        string defaultOptionsNoopPath = Path.Combine(outRoot, "defaultoptions-goodie-codec-noop.bea");
        string patchedPath = Path.Combine(outRoot, "career-goodie-codec-script-boundary-set.bes");
        string idempotentPath = Path.Combine(outRoot, "career-goodie-codec-idempotent-set.bes");
        string roundtripPath = Path.Combine(outRoot, "career-goodie-codec-roundtrip-original-states.bes");

        foreach (string outputPath in new[]
                 {
                     careerBaselinePath, defaultOptionsBaselinePath, careerNoopPath, defaultOptionsNoopPath,
                     patchedPath, idempotentPath, roundtripPath
                 })
        {
            if (PathsEqual(careerSource, outputPath) || PathsEqual(defaultOptionsSource, outputPath))
            {
                throw new InvalidOperationException("Source and output paths must be distinct.");
            }
        }

        File.Copy(careerSource, careerBaselinePath, overwrite: true);
        File.Copy(defaultOptionsSource, defaultOptionsBaselinePath, overwrite: true);
        File.Copy(careerBaselinePath, careerNoopPath, overwrite: true);
        File.Copy(defaultOptionsBaselinePath, defaultOptionsNoopPath, overwrite: true);

        byte[] careerBaseline = File.ReadAllBytes(careerBaselinePath);
        byte[] defaultOptionsBaseline = File.ReadAllBytes(defaultOptionsBaselinePath);
        byte[] careerNoop = File.ReadAllBytes(careerNoopPath);
        byte[] defaultOptionsNoop = File.ReadAllBytes(defaultOptionsNoopPath);
        ValidateContainer(careerBaseline, "career baseline");
        ValidateContainer(defaultOptionsBaseline, "defaultoptions baseline");
        ValidateContainer(careerNoop, "career noop");
        ValidateContainer(defaultOptionsNoop, "defaultoptions noop");

        Dictionary<int, MissionScriptGoodieState> newStatesByScriptIndex = new();
        Dictionary<int, MissionScriptGoodieState> originalStatesByScriptIndex = new();
        List<GoodieTargetInfo> targets = new();
        foreach (int scriptIndex in ScriptIndices)
        {
            MissionScriptGoodieStateVector vector = MissionScriptGoodieStateSaveCodec.GetDisplayableVectorFromScriptIndex(scriptIndex);
            MissionScriptGoodieState original = MissionScriptGoodieStateSaveCodec.GetStateByScriptIndex(careerBaseline, scriptIndex);
            MissionScriptGoodieState next = ChooseDifferentState(original);
            newStatesByScriptIndex[scriptIndex] = next;
            originalStatesByScriptIndex[scriptIndex] = original;
            targets.Add(new GoodieTargetInfo
            {
                ScriptIndex = scriptIndex,
                SaveGoodieIndex = vector.SaveGoodieIndex,
                FileOffset = HexOffset(vector.TrueViewDwordOffset),
                BeforeState = (uint)original,
                AfterState = (uint)next,
                BeforeLabel = MissionScriptGoodieStateSaveCodec.GetStateLabel(original),
                AfterLabel = MissionScriptGoodieStateSaveCodec.GetStateLabel(next),
                Displayable = vector.IsDisplayable
            });
        }

        byte[] patched = careerBaseline.ToArray();
        MissionScriptGoodieStateVector[] writtenVectors = MissionScriptGoodieStateSaveCodec.SetDisplayableStatesByScriptIndex(patched, newStatesByScriptIndex);
        File.WriteAllBytes(patchedPath, patched);

        byte[] idempotent = patched.ToArray();
        MissionScriptGoodieStateSaveCodec.SetDisplayableStatesByScriptIndex(idempotent, newStatesByScriptIndex);
        File.WriteAllBytes(idempotentPath, idempotent);

        byte[] roundtrip = patched.ToArray();
        MissionScriptGoodieStateSaveCodec.SetDisplayableStatesByScriptIndex(roundtrip, originalStatesByScriptIndex);
        File.WriteAllBytes(roundtripPath, roundtrip);

        ValidateContainer(patched, "patched career");
        ValidateContainer(idempotent, "idempotent career");
        ValidateContainer(roundtrip, "roundtrip career");

        bool reservedIndexRejected = ThrowsArgumentOutOfRange(() =>
            MissionScriptGoodieStateSaveCodec.SetDisplayableStateByScriptIndex(careerBaseline.ToArray(), 234, MissionScriptGoodieState.Old));
        bool invalidStateRejected = ThrowsArgumentOutOfRange(() =>
            MissionScriptGoodieStateSaveCodec.SetDisplayableStateByScriptIndex(careerBaseline.ToArray(), 1, (MissionScriptGoodieState)4));
        bool emptyBatchRejected = ThrowsArgumentException(() =>
            MissionScriptGoodieStateSaveCodec.SetDisplayableStatesByScriptIndex(careerBaseline.ToArray(), new Dictionary<int, MissionScriptGoodieState>()));
        bool invalidMixedBatchLeavesBufferUnchanged = InvalidMixedBatchLeavesBufferUnchanged(careerBaseline);
        bool wrongSizeRejected = !MissionScriptGoodieStateSaveCodec.IsValidCareerSaveContainer(careerBaseline.AsSpan(0, MissionScriptGoodieStateSaveCodec.ExpectedFileSize - 1));
        bool wrongVersionRejected = WrongVersionRejected(careerBaseline);

        int[] targetOffsets = writtenVectors.SelectMany(row => Enumerable.Range(row.TrueViewDwordOffset, 4)).ToArray();
        int[] baselineToPatch = ChangedOffsets(careerBaseline, patched);
        int[] patchToIdempotent = ChangedOffsets(patched, idempotent);
        int[] roundtripToBaseline = ChangedOffsets(roundtrip, careerBaseline);
        int[] unexpectedOffsets = baselineToPatch.Where(offset => !targetOffsets.Contains(offset)).ToArray();
        int[] legacyTrapHits = baselineToPatch.Where(offset => LegacyTrapOffsets.Contains(offset)).ToArray();

        foreach (GoodieTargetInfo target in targets)
        {
            MissionScriptGoodieState readback = MissionScriptGoodieStateSaveCodec.GetStateByScriptIndex(patched, target.ScriptIndex);
            target.ReadbackState = (uint)readback;
            target.ReadbackMatches = target.ReadbackState == target.AfterState;
        }

        byte[] careerSourceAfter = File.ReadAllBytes(careerSource);
        byte[] defaultOptionsSourceAfter = File.ReadAllBytes(defaultOptionsSource);

        Evidence evidence = new()
        {
            SchemaVersion = SchemaVersion,
            Status = "PASS",
            EvidenceRoot = ToRepoRelative(repoRoot, outRoot),
            Source = new SourceInfo
            {
                Class = "validated copied real career .bes and defaultoptions.bea baselines from prior ignored evidence",
                SourcePathsPublic = false,
                SourceHashesPublic = false,
                ArtifactPathsPublic = false,
                ArtifactHashesPublic = false,
                RawBytesPublic = false
            },
            Harness = new HarnessInfo
            {
                ToolProjectPath = "tools/MissionScriptGoodieStateSaveCodecHarness/MissionScriptGoodieStateSaveCodecHarness.csproj",
                AppCoreCodecPath = "OnslaughtCareerEditor.AppCore/MissionScriptGoodieStateSaveCodec.cs",
                InterfaceKind = "AppCore Goodie codec applied by proof-only copied-baseline harness",
                AppCoreCodecUsed = true,
                AppCorePatcherUsed = false,
                ManualGoodieDwordWriteInHarness = false,
                AppCoreCodecFileIo = false,
                HarnessFileIo = true,
                ProductUiWired = false,
                SourceBaselineRead = true,
                PrivateArtifactMaterialized = true
            },
            Provenance = new ProvenanceInfo
            {
                CopyBeforeWrite = true,
                SourcesUnderPriorPrivateEvidenceRoot = true,
                OutputsUnderProofPrivateEvidenceRoot = true,
                SourceAndOutputPathsDistinct = !PathsEqual(careerSource, patchedPath) && !PathsEqual(defaultOptionsSource, defaultOptionsBaselinePath),
                CareerSourceToInputDiffCount = ChangedOffsets(careerSourceBefore, careerBaseline).Length,
                DefaultOptionsSourceToInputDiffCount = ChangedOffsets(defaultOptionsSourceBefore, defaultOptionsBaseline).Length,
                CareerSourceUnchanged = careerSourceBefore.SequenceEqual(careerSourceAfter),
                DefaultOptionsSourceUnchanged = defaultOptionsSourceBefore.SequenceEqual(defaultOptionsSourceAfter)
            },
            CopiedArtifacts =
            [
                FileRow(repoRoot, "career Goodie codec baseline", careerBaselinePath, careerBaseline),
                FileRow(repoRoot, "defaultoptions Goodie codec baseline", defaultOptionsBaselinePath, defaultOptionsBaseline),
                FileRow(repoRoot, "career Goodie codec no-op", careerNoopPath, careerNoop),
                FileRow(repoRoot, "defaultoptions Goodie codec no-op", defaultOptionsNoopPath, defaultOptionsNoop),
                FileRow(repoRoot, "career Goodie codec script-boundary set", patchedPath, patched),
                FileRow(repoRoot, "career Goodie codec idempotent set", idempotentPath, idempotent),
                FileRow(repoRoot, "career Goodie codec roundtrip original states", roundtripPath, roundtrip)
            ],
            Container = new ContainerInfo
            {
                ExpectedSize = MissionScriptGoodieStateSaveCodec.ExpectedFileSize,
                ExpectedSizeHex = Hex(MissionScriptGoodieStateSaveCodec.ExpectedFileSize, 4),
                VersionWord = Hex(MissionScriptGoodieStateSaveCodec.VersionWord, 4),
                TrueViewRule = "file_offset = 0x0002 + career_offset",
                TrueViewGoodieBase = HexOffset(MissionScriptGoodieStateSaveCodec.GoodieBaseOffset),
                GoodieStorageEntryCount = MissionScriptGoodieStateSaveCodec.GoodieStorageEntryCount,
                DisplayableGoodieCount = MissionScriptGoodieStateSaveCodec.DisplayableGoodieCount,
                ReservedPreserveEntryCount = MissionScriptGoodieStateSaveCodec.ReservedPreserveEntryCount,
                FileSizePreserved = new[] { careerBaseline, defaultOptionsBaseline, careerNoop, defaultOptionsNoop, patched, idempotent, roundtrip }
                    .All(row => row.Length == MissionScriptGoodieStateSaveCodec.ExpectedFileSize),
                VersionWordPreserved = new[] { careerBaseline, defaultOptionsBaseline, careerNoop, defaultOptionsNoop, patched, idempotent, roundtrip }
                    .All(row => ReadVersionWord(row) == MissionScriptGoodieStateSaveCodec.VersionWord)
            },
            Operation = new OperationInfo
            {
                ScriptIndexing = "1-based",
                MappingFormula = "save_goodie_index = script_index - 1",
                OffsetFormula = "0x1F46 + (script_index - 1) * 4",
                ReservedWritePolicy = "displayable-only-default-rejects-reserved",
                ScriptIndices = ScriptIndices,
                SaveGoodieIndices = targets.Select(row => row.SaveGoodieIndex).ToArray(),
                TargetDwordWriteCount = targets.Count,
                TargetOffsetRanges = targets.Select(row => $"{row.FileOffset}-{HexOffset(ParseHex(row.FileOffset) + 3)}").ToArray(),
                ChangedOffsets = baselineToPatch.Select(HexOffset).ToArray(),
                ChangedOffsetCount = baselineToPatch.Length,
                UnexpectedDiffCount = unexpectedOffsets.Length,
                LegacyTrapHitCount = legacyTrapHits.Length,
                AllTargetReadbacksMatch = targets.All(row => row.ReadbackMatches),
                Targets = targets.ToArray()
            },
            NoOpAndRoundTrip = new RoundTripInfo
            {
                CareerNoopDiffCount = ChangedOffsets(careerBaseline, careerNoop).Length,
                DefaultOptionsNoopDiffCount = ChangedOffsets(defaultOptionsBaseline, defaultOptionsNoop).Length,
                PatchToIdempotentDiffCount = patchToIdempotent.Length,
                RoundtripToBaselineDiffCount = roundtripToBaseline.Length
            },
            Preservation = new PreservationInfo
            {
                NonTargetGoodiesUnchanged = NonTargetGoodiesUnchanged(careerBaseline, patched, targets.Select(row => row.SaveGoodieIndex).ToHashSet()),
                ReservedGoodiesUnchanged = RangeUnchanged(careerBaseline, patched, MissionScriptGoodieStateSaveCodec.GoodieBaseOffset + MissionScriptGoodieStateSaveCodec.DisplayableGoodieCount * 4, MissionScriptGoodieStateSaveCodec.GoodieStorageEndExclusive),
                KillCountersUnchanged = RangeUnchanged(careerBaseline, patched, KillsBase, TechSlotsBase),
                TechSlotsUnchanged = RangeUnchanged(careerBaseline, patched, TechSlotsBase, TechSlotsEndExclusive),
                OptionsEntriesUnchanged = RangeUnchanged(careerBaseline, patched, OptionsEntriesStart, OptionsEntriesEnd),
                OptionsTailUnchanged = RangeUnchanged(careerBaseline, patched, OptionsTailStart, OptionsTailEnd)
            },
            Rejections = new RejectionInfo
            {
                ReservedIndex234Rejected = reservedIndexRejected,
                InvalidState4Rejected = invalidStateRejected,
                EmptyOverrideRejected = emptyBatchRejected,
                InvalidMixedBatchLeavesBufferUnchanged = invalidMixedBatchLeavesBufferUnchanged,
                WrongSizeRejected = wrongSizeRejected,
                WrongVersionRejected = wrongVersionRejected
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
                RebuildImplementation = false,
                RuntimeGoodieStateMutationProven = false,
                RuntimeSaveBehaviorProven = false,
                RuntimeGoodiesWallBehaviorProven = false,
                RuntimeScoreBehaviorProven = false,
                LegacyAlignedViewTrapOffsets = LegacyTrapOffsets.Select(HexOffset).ToArray(),
                LegacyTrapHitCount = legacyTrapHits.Length
            }
        };

        ValidateEvidence(evidence);
        return evidence;
    }

    private static MissionScriptGoodieState ChooseDifferentState(MissionScriptGoodieState current)
    {
        uint next = ((uint)current + 1) % (MissionScriptGoodieStateSaveCodec.MaxKnownStateValue + 1);
        return (MissionScriptGoodieState)next;
    }

    private static bool InvalidMixedBatchLeavesBufferUnchanged(byte[] baseline)
    {
        byte[] candidate = baseline.ToArray();
        try
        {
            MissionScriptGoodieStateSaveCodec.SetDisplayableStatesByScriptIndex(
                candidate,
                new Dictionary<int, MissionScriptGoodieState>
                {
                    [1] = MissionScriptGoodieState.Old,
                    [234] = MissionScriptGoodieState.New
                });
            return false;
        }
        catch (ArgumentOutOfRangeException)
        {
            return ChangedOffsets(baseline, candidate).Length == 0;
        }
    }

    private static bool WrongVersionRejected(byte[] baseline)
    {
        byte[] wrongVersion = baseline.ToArray();
        wrongVersion[0] ^= 0xff;
        return !MissionScriptGoodieStateSaveCodec.IsValidCareerSaveContainer(wrongVersion);
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

    private static bool NonTargetGoodiesUnchanged(byte[] before, byte[] after, HashSet<int> targetIndexes)
    {
        for (int index = 0; index < MissionScriptGoodieStateSaveCodec.GoodieStorageEntryCount; index++)
        {
            if (targetIndexes.Contains(index))
            {
                continue;
            }

            int offset = MissionScriptGoodieStateSaveCodec.GoodieBaseOffset + index * 4;
            if (!before.AsSpan(offset, 4).SequenceEqual(after.AsSpan(offset, 4)))
            {
                return false;
            }
        }

        return true;
    }

    private static void ValidateEvidence(Evidence evidence)
    {
        List<string> failures = [];
        if (evidence.Status != "PASS")
        {
            failures.Add("status mismatch");
        }

        if (!evidence.Harness.AppCoreCodecUsed ||
            evidence.Harness.AppCorePatcherUsed ||
            evidence.Harness.ManualGoodieDwordWriteInHarness ||
            evidence.Harness.AppCoreCodecFileIo ||
            evidence.Harness.ProductUiWired ||
            !evidence.Harness.HarnessFileIo ||
            !evidence.Harness.SourceBaselineRead ||
            !evidence.Harness.PrivateArtifactMaterialized)
        {
            failures.Add("harness guard mismatch");
        }

        if (!evidence.Provenance.CopyBeforeWrite ||
            !evidence.Provenance.SourcesUnderPriorPrivateEvidenceRoot ||
            !evidence.Provenance.OutputsUnderProofPrivateEvidenceRoot ||
            !evidence.Provenance.SourceAndOutputPathsDistinct ||
            evidence.Provenance.CareerSourceToInputDiffCount != 0 ||
            evidence.Provenance.DefaultOptionsSourceToInputDiffCount != 0 ||
            !evidence.Provenance.CareerSourceUnchanged ||
            !evidence.Provenance.DefaultOptionsSourceUnchanged)
        {
            failures.Add("provenance guard mismatch");
        }

        if (!evidence.Container.FileSizePreserved ||
            !evidence.Container.VersionWordPreserved ||
            evidence.Container.GoodieStorageEntryCount != MissionScriptGoodieStateSaveCodec.GoodieStorageEntryCount ||
            evidence.Container.DisplayableGoodieCount != MissionScriptGoodieStateSaveCodec.DisplayableGoodieCount ||
            evidence.Container.ReservedPreserveEntryCount != MissionScriptGoodieStateSaveCodec.ReservedPreserveEntryCount)
        {
            failures.Add("container guard mismatch");
        }

        if (evidence.Operation.TargetDwordWriteCount != ScriptIndices.Length ||
            evidence.Operation.UnexpectedDiffCount != 0 ||
            evidence.Operation.LegacyTrapHitCount != 0 ||
            !evidence.Operation.AllTargetReadbacksMatch ||
            !evidence.Operation.ChangedOffsets.SequenceEqual(ScriptIndices.Select(index => HexOffset(MissionScriptGoodieStateSaveCodec.GoodieBaseOffset + (index - 1) * 4))))
        {
            failures.Add("operation guard mismatch");
        }

        if (evidence.NoOpAndRoundTrip.CareerNoopDiffCount != 0 ||
            evidence.NoOpAndRoundTrip.DefaultOptionsNoopDiffCount != 0 ||
            evidence.NoOpAndRoundTrip.PatchToIdempotentDiffCount != 0 ||
            evidence.NoOpAndRoundTrip.RoundtripToBaselineDiffCount != 0)
        {
            failures.Add("roundtrip guard mismatch");
        }

        if (!evidence.Preservation.NonTargetGoodiesUnchanged ||
            !evidence.Preservation.ReservedGoodiesUnchanged ||
            !evidence.Preservation.KillCountersUnchanged ||
            !evidence.Preservation.TechSlotsUnchanged ||
            !evidence.Preservation.OptionsEntriesUnchanged ||
            !evidence.Preservation.OptionsTailUnchanged)
        {
            failures.Add("preservation guard mismatch");
        }

        if (!evidence.Rejections.ReservedIndex234Rejected ||
            !evidence.Rejections.InvalidState4Rejected ||
            !evidence.Rejections.EmptyOverrideRejected ||
            !evidence.Rejections.InvalidMixedBatchLeavesBufferUnchanged ||
            !evidence.Rejections.WrongSizeRejected ||
            !evidence.Rejections.WrongVersionRejected)
        {
            failures.Add("rejection guard mismatch");
        }

        if (evidence.NegativeGuards.RuntimeExecution ||
            evidence.NegativeGuards.BeLaunch ||
            evidence.NegativeGuards.GhidraMutation ||
            evidence.NegativeGuards.ExecutablePatching ||
            evidence.NegativeGuards.GodotWork ||
            evidence.NegativeGuards.ProductUiWired ||
            evidence.NegativeGuards.RebuildImplementation ||
            evidence.NegativeGuards.LegacyTrapHitCount != 0)
        {
            failures.Add("negative guard mismatch");
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
            switch (arg)
            {
                case "-h":
                case "--help":
                    options.ShowHelp = true;
                    break;
                case "--repo-root":
                    options.RepoRoot = RequireValue(args, ref index, arg);
                    break;
                case "--out-root":
                    options.OutRoot = RequireValue(args, ref index, arg);
                    break;
                case "--career-source":
                    options.CareerSource = RequireValue(args, ref index, arg);
                    break;
                case "--defaultoptions-source":
                    options.DefaultOptionsSource = RequireValue(args, ref index, arg);
                    break;
                default:
                    throw new ArgumentException($"Unknown argument: {arg}");
            }
        }

        return options;
    }

    private static string RequireValue(string[] args, ref int index, string name)
    {
        if (index + 1 >= args.Length)
        {
            throw new ArgumentException($"{name} requires a value.");
        }

        index++;
        return args[index];
    }

    private static void WriteUsage()
    {
        Console.WriteLine("MissionScriptGoodieStateSaveCodecHarness [--repo-root .] [--career-source <copied-baseline.bes>] [--defaultoptions-source <copied-defaultoptions.bea>]");
    }

    private static void ValidateContainer(byte[] data, string label)
    {
        if (!MissionScriptGoodieStateSaveCodec.IsValidCareerSaveContainer(data))
        {
            throw new InvalidOperationException($"{label} is not a valid 10004-byte 0x4BD1 career save container.");
        }
    }

    private static ushort ReadVersionWord(byte[] data) =>
        BinaryPrimitives.ReadUInt16LittleEndian(data.AsSpan(0, 2));

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

    private static bool RangeUnchanged(byte[] before, byte[] after, int start, int endExclusive) =>
        before.AsSpan(start, endExclusive - start).SequenceEqual(after.AsSpan(start, endExclusive - start));

    private static bool IsWithinDirectory(string path, string directory)
    {
        string fullPath = Path.GetFullPath(path).TrimEnd(Path.DirectorySeparatorChar, Path.AltDirectorySeparatorChar) + Path.DirectorySeparatorChar;
        string fullDirectory = Path.GetFullPath(directory).TrimEnd(Path.DirectorySeparatorChar, Path.AltDirectorySeparatorChar) + Path.DirectorySeparatorChar;
        return fullPath.StartsWith(fullDirectory, StringComparison.OrdinalIgnoreCase);
    }

    private static bool PathsEqual(string left, string right) =>
        string.Equals(Path.GetFullPath(left).TrimEnd(Path.DirectorySeparatorChar, Path.AltDirectorySeparatorChar),
            Path.GetFullPath(right).TrimEnd(Path.DirectorySeparatorChar, Path.AltDirectorySeparatorChar),
            StringComparison.OrdinalIgnoreCase);

    private static string ToRepoRelative(string repoRoot, string path) =>
        Path.GetRelativePath(repoRoot, path).Replace('\\', '/');

    private static string Sha256(byte[] data) =>
        Convert.ToHexString(SHA256.HashData(data)).ToLowerInvariant();

    private static string HexOffset(int value) => Hex(value, 4);

    private static string Hex(long value, int digits) => $"0x{value.ToString($"X{digits}")}";

    private static int ParseHex(string value) => Convert.ToInt32(value[2..], 16);

    private static ArtifactInfo FileRow(string repoRoot, string label, string path, byte[] data) => new()
    {
        Label = label,
        RelativePath = ToRepoRelative(repoRoot, path),
        Size = data.Length,
        VersionWord = Hex(ReadVersionWord(data), 4),
        Sha256 = Sha256(data)
    };

    private sealed class Options
    {
        public bool ShowHelp { get; set; }
        public string? RepoRoot { get; set; }
        public string? OutRoot { get; set; }
        public string? CareerSource { get; set; }
        public string? DefaultOptionsSource { get; set; }
    }

    private sealed class Evidence
    {
        public string SchemaVersion { get; set; } = "";
        public string Status { get; set; } = "";
        public string EvidenceRoot { get; set; } = "";
        public SourceInfo Source { get; set; } = new();
        public HarnessInfo Harness { get; set; } = new();
        public ProvenanceInfo Provenance { get; set; } = new();
        public ArtifactInfo[] CopiedArtifacts { get; set; } = [];
        public ContainerInfo Container { get; set; } = new();
        public OperationInfo Operation { get; set; } = new();
        public RoundTripInfo NoOpAndRoundTrip { get; set; } = new();
        public PreservationInfo Preservation { get; set; } = new();
        public RejectionInfo Rejections { get; set; } = new();
        public NegativeGuardInfo NegativeGuards { get; set; } = new();
    }

    private sealed class SourceInfo
    {
        public string Class { get; set; } = "";
        public bool SourcePathsPublic { get; set; }
        public bool SourceHashesPublic { get; set; }
        public bool ArtifactPathsPublic { get; set; }
        public bool ArtifactHashesPublic { get; set; }
        public bool RawBytesPublic { get; set; }
    }

    private sealed class HarnessInfo
    {
        public string ToolProjectPath { get; set; } = "";
        public string AppCoreCodecPath { get; set; } = "";
        public string InterfaceKind { get; set; } = "";
        public bool AppCoreCodecUsed { get; set; }
        public bool AppCorePatcherUsed { get; set; }
        public bool ManualGoodieDwordWriteInHarness { get; set; }
        public bool AppCoreCodecFileIo { get; set; }
        public bool HarnessFileIo { get; set; }
        public bool ProductUiWired { get; set; }
        public bool SourceBaselineRead { get; set; }
        public bool PrivateArtifactMaterialized { get; set; }
    }

    private sealed class ProvenanceInfo
    {
        public bool CopyBeforeWrite { get; set; }
        public bool SourcesUnderPriorPrivateEvidenceRoot { get; set; }
        public bool OutputsUnderProofPrivateEvidenceRoot { get; set; }
        public bool SourceAndOutputPathsDistinct { get; set; }
        public int CareerSourceToInputDiffCount { get; set; }
        public int DefaultOptionsSourceToInputDiffCount { get; set; }
        public bool CareerSourceUnchanged { get; set; }
        public bool DefaultOptionsSourceUnchanged { get; set; }
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
        public string TrueViewGoodieBase { get; set; } = "";
        public int GoodieStorageEntryCount { get; set; }
        public int DisplayableGoodieCount { get; set; }
        public int ReservedPreserveEntryCount { get; set; }
        public bool FileSizePreserved { get; set; }
        public bool VersionWordPreserved { get; set; }
    }

    private sealed class OperationInfo
    {
        public string ScriptIndexing { get; set; } = "";
        public string MappingFormula { get; set; } = "";
        public string OffsetFormula { get; set; } = "";
        public string ReservedWritePolicy { get; set; } = "";
        public int[] ScriptIndices { get; set; } = [];
        public int[] SaveGoodieIndices { get; set; } = [];
        public int TargetDwordWriteCount { get; set; }
        public string[] TargetOffsetRanges { get; set; } = [];
        public string[] ChangedOffsets { get; set; } = [];
        public int ChangedOffsetCount { get; set; }
        public int UnexpectedDiffCount { get; set; }
        public int LegacyTrapHitCount { get; set; }
        public bool AllTargetReadbacksMatch { get; set; }
        public GoodieTargetInfo[] Targets { get; set; } = [];
    }

    private sealed class GoodieTargetInfo
    {
        public int ScriptIndex { get; set; }
        public int SaveGoodieIndex { get; set; }
        public string FileOffset { get; set; } = "";
        public uint BeforeState { get; set; }
        public uint AfterState { get; set; }
        public uint ReadbackState { get; set; }
        public bool ReadbackMatches { get; set; }
        public string BeforeLabel { get; set; } = "";
        public string AfterLabel { get; set; } = "";
        public bool Displayable { get; set; }
    }

    private sealed class RoundTripInfo
    {
        public int CareerNoopDiffCount { get; set; }
        public int DefaultOptionsNoopDiffCount { get; set; }
        public int PatchToIdempotentDiffCount { get; set; }
        public int RoundtripToBaselineDiffCount { get; set; }
    }

    private sealed class PreservationInfo
    {
        public bool NonTargetGoodiesUnchanged { get; set; }
        public bool ReservedGoodiesUnchanged { get; set; }
        public bool KillCountersUnchanged { get; set; }
        public bool TechSlotsUnchanged { get; set; }
        public bool OptionsEntriesUnchanged { get; set; }
        public bool OptionsTailUnchanged { get; set; }
    }

    private sealed class RejectionInfo
    {
        public bool ReservedIndex234Rejected { get; set; }
        public bool InvalidState4Rejected { get; set; }
        public bool EmptyOverrideRejected { get; set; }
        public bool InvalidMixedBatchLeavesBufferUnchanged { get; set; }
        public bool WrongSizeRejected { get; set; }
        public bool WrongVersionRejected { get; set; }
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
        public bool RebuildImplementation { get; set; }
        public bool RuntimeGoodieStateMutationProven { get; set; }
        public bool RuntimeSaveBehaviorProven { get; set; }
        public bool RuntimeGoodiesWallBehaviorProven { get; set; }
        public bool RuntimeScoreBehaviorProven { get; set; }
        public string[] LegacyAlignedViewTrapOffsets { get; set; } = [];
        public int LegacyTrapHitCount { get; set; }
    }
}
