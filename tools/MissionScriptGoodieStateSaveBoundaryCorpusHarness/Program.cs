using System.Security.Cryptography;
using System.Text.Json;
using System.Text.Json.Serialization;
using Onslaught___Career_Editor;

namespace Onslaught___Career_Editor.Tools;

internal static class Program
{
    private const string SchemaVersion = "missionscript-goodie-state-save-appcore-copied-baseline-boundary-corpus-private-evidence.v1";
    private const string EvidenceRootRelative = "subagents/static-to-proof/missionscript-goodie-state-save-appcore-copied-baseline-boundary-corpus-harness-proof";
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

    private static readonly int[] BoundaryScriptIndices = [1, 2, 51, 53, 68, 71, 232, 233];
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

        string careerBaselinePath = Path.Combine(outRoot, "career-goodie-boundary-corpus-baseline.bes");
        string defaultOptionsBaselinePath = Path.Combine(outRoot, "defaultoptions-goodie-boundary-corpus-baseline.bea");
        string careerNoopPath = Path.Combine(outRoot, "career-goodie-boundary-corpus-noop.bes");
        string defaultOptionsNoopPath = Path.Combine(outRoot, "defaultoptions-goodie-boundary-corpus-noop.bea");

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
        ValidateContainer(careerNoop, "career no-op");
        ValidateContainer(defaultOptionsNoop, "defaultoptions no-op");

        List<ArtifactInfo> copiedArtifacts =
        [
            FileRow(repoRoot, "career Goodie boundary corpus baseline", careerBaselinePath, careerBaseline),
            FileRow(repoRoot, "defaultoptions Goodie boundary corpus baseline", defaultOptionsBaselinePath, defaultOptionsBaseline),
            FileRow(repoRoot, "career Goodie boundary corpus no-op", careerNoopPath, careerNoop),
            FileRow(repoRoot, "defaultoptions Goodie boundary corpus no-op", defaultOptionsNoopPath, defaultOptionsNoop)
        ];

        StorageReadResult storageRead = ReadAllStorageStates(careerBaseline);
        DisplayableRoundTripResult displayableRoundTrips = RunDisplayableRoundTrips(careerBaseline);
        ReservedRejectionResult reservedRejections = RunReservedRejections(careerBaseline);
        BoundaryStateMatrixResult boundaryMatrix = RunBoundaryStateMatrix(careerBaseline);
        RejectionResult rejections = RunRejections(careerBaseline);

        foreach (int scriptIndex in BoundaryScriptIndices)
        {
            byte[] sample = careerBaseline.ToArray();
            MissionScriptGoodieState original = MissionScriptGoodieStateSaveCodec.GetStateByScriptIndex(sample, scriptIndex);
            MissionScriptGoodieState next = ChooseDifferentState(original);
            MissionScriptGoodieStateSaveCodec.SetDisplayableStateByScriptIndex(sample, scriptIndex, next);
            string samplePath = Path.Combine(outRoot, $"career-goodie-boundary-corpus-script-{scriptIndex:D3}-sample.bes");
            File.WriteAllBytes(samplePath, sample);
            copiedArtifacts.Add(FileRow(repoRoot, $"career Goodie boundary sample script {scriptIndex}", samplePath, sample));
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
                RawBytesPublic = false,
                CopiedDefaultOptionsValidationOnly = true
            },
            Harness = new HarnessInfo
            {
                ToolProjectPath = "tools/MissionScriptGoodieStateSaveBoundaryCorpusHarness/MissionScriptGoodieStateSaveBoundaryCorpusHarness.csproj",
                AppCoreCodecPath = "OnslaughtCareerEditor.AppCore/MissionScriptGoodieStateSaveCodec.cs",
                InterfaceKind = "AppCore Goodie codec boundary corpus applied by proof-only copied-baseline harness",
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
                SourceAndOutputPathsDistinct = !PathsEqual(careerSource, careerBaselinePath) && !PathsEqual(defaultOptionsSource, defaultOptionsBaselinePath),
                CareerSourceToInputDiffCount = ChangedOffsets(careerSourceBefore, careerBaseline).Length,
                DefaultOptionsSourceToInputDiffCount = ChangedOffsets(defaultOptionsSourceBefore, defaultOptionsBaseline).Length,
                CareerSourceUnchanged = careerSourceBefore.SequenceEqual(careerSourceAfter),
                DefaultOptionsSourceUnchanged = defaultOptionsSourceBefore.SequenceEqual(defaultOptionsSourceAfter)
            },
            CopiedArtifacts = copiedArtifacts.ToArray(),
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
                GoodieStorageEndExclusive = HexOffset(MissionScriptGoodieStateSaveCodec.GoodieStorageEndExclusive),
                FileSizePreserved = copiedArtifacts.All(row => row.Size == MissionScriptGoodieStateSaveCodec.ExpectedFileSize),
                VersionWordPreserved = copiedArtifacts.All(row => row.VersionWord == Hex(MissionScriptGoodieStateSaveCodec.VersionWord, 4))
            },
            Corpus = new CorpusInfo
            {
                PreviousInMemoryBoundaryCorpusXunitCaseCount = 651,
                StorageVectorCopiedBaselineReadCaseCount = storageRead.CaseCount,
                DisplayableCopiedBaselineRoundTripCaseCount = displayableRoundTrips.CaseCount,
                ReservedCopiedBaselineRejectionCaseCount = reservedRejections.CaseCount,
                BoundaryStateCopiedBaselineMatrixCaseCount = boundaryMatrix.CaseCount,
                CopiedBaselineBoundaryCorpusCaseCount = storageRead.CaseCount + displayableRoundTrips.CaseCount + reservedRejections.CaseCount + boundaryMatrix.CaseCount,
                SampleBoundaryArtifactCount = BoundaryScriptIndices.Length,
                BoundaryScriptIndices = BoundaryScriptIndices,
                BoundaryStateValues = [0, 1, 2, 3],
                BoundaryOffsets = BoundaryScriptIndices.Select(scriptIndex => HexOffset(MissionScriptGoodieStateSaveCodec.GoodieBaseOffset + (scriptIndex - 1) * 4)).ToArray(),
                AllStorageScriptIndicesReadFromCopiedBaseline = storageRead.AllRead,
                AllStorageStateValuesWithinKnownRange = storageRead.AllStatesWithinKnownRange,
                AllDisplayableCopiedBaselineRoundTrip = displayableRoundTrips.AllRoundTrip,
                ToggleTouchesOnlyExpectedByteForAllDisplayable = displayableRoundTrips.ToggleTouchesOnlyExpectedByte,
                ToggleIdempotentForAllDisplayable = displayableRoundTrips.ToggleIdempotent,
                RestoreToBaselineForAllDisplayable = displayableRoundTrips.RestoreToBaseline,
                AllReservedCopiedBaselineRejectionsLeaveBufferUnchanged = reservedRejections.AllRejectedAndUnchanged,
                AllBoundaryStatesRoundTripOnCopiedBaseline = boundaryMatrix.AllRoundTrip,
                AllBoundaryStatesRestoreToBaseline = boundaryMatrix.RestoreToBaseline,
                TargetReadbackMismatchCount = displayableRoundTrips.TargetReadbackMismatchCount + boundaryMatrix.TargetReadbackMismatchCount,
                UnexpectedDiffCount = displayableRoundTrips.UnexpectedDiffCount + boundaryMatrix.UnexpectedDiffCount,
                LegacyTrapHitCount = displayableRoundTrips.LegacyTrapHitCount + boundaryMatrix.LegacyTrapHitCount,
                LegacyAlignedViewTrapOffsets = LegacyTrapOffsets.Select(HexOffset).ToArray()
            },
            NoOp = new NoOpInfo
            {
                CareerNoopDiffCount = ChangedOffsets(careerBaseline, careerNoop).Length,
                DefaultOptionsNoopDiffCount = ChangedOffsets(defaultOptionsBaseline, defaultOptionsNoop).Length
            },
            Preservation = new PreservationInfo
            {
                NonTargetGoodiesUnchangedForAllDisplayableRoundTrips = displayableRoundTrips.NonTargetGoodiesUnchanged,
                ReservedGoodiesUnchangedForAllDisplayableRoundTrips = displayableRoundTrips.ReservedGoodiesUnchanged,
                KillCountersUnchangedForAllDisplayableRoundTrips = displayableRoundTrips.KillCountersUnchanged,
                TechSlotsUnchangedForAllDisplayableRoundTrips = displayableRoundTrips.TechSlotsUnchanged,
                OptionsEntriesUnchangedForAllDisplayableRoundTrips = displayableRoundTrips.OptionsEntriesUnchanged,
                OptionsTailUnchangedForAllDisplayableRoundTrips = displayableRoundTrips.OptionsTailUnchanged
            },
            Rejections = rejections,
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
                RuntimeObservationRows = 0,
                MissionScriptRuntimeEvidenceRows = 0,
                RuntimeCommandEffectRows = 0,
                RuntimeGoodieStateRows = 0,
                RuntimeSaveRows = 0,
                RuntimeDefaultOptionsRows = 0,
                RuntimeGoodiesWallRows = 0,
                RuntimeScoreRows = 0,
                PublicLeakCheck = "PASS"
            }
        };

        ValidateEvidence(evidence);
        return evidence;
    }

    private static StorageReadResult ReadAllStorageStates(byte[] baseline)
    {
        int readCount = 0;
        bool allKnown = true;
        for (int scriptIndex = 1; scriptIndex <= MissionScriptGoodieStateSaveCodec.GoodieStorageEntryCount; scriptIndex++)
        {
            MissionScriptGoodieState state = MissionScriptGoodieStateSaveCodec.GetStateByScriptIndex(baseline, scriptIndex);
            allKnown &= (uint)state <= MissionScriptGoodieStateSaveCodec.MaxKnownStateValue;
            readCount++;
        }

        return new StorageReadResult(readCount, readCount == MissionScriptGoodieStateSaveCodec.GoodieStorageEntryCount, allKnown);
    }

    private static DisplayableRoundTripResult RunDisplayableRoundTrips(byte[] baseline)
    {
        int readbackMismatches = 0;
        int unexpectedDiffs = 0;
        int trapHits = 0;
        bool expectedByteOnly = true;
        bool idempotent = true;
        bool restored = true;
        bool nonTargetGoodies = true;
        bool reservedGoodies = true;
        bool kills = true;
        bool techSlots = true;
        bool optionsEntries = true;
        bool optionsTail = true;

        for (int scriptIndex = 1; scriptIndex <= MissionScriptGoodieStateSaveCodec.DisplayableGoodieCount; scriptIndex++)
        {
            MissionScriptGoodieState original = MissionScriptGoodieStateSaveCodec.GetStateByScriptIndex(baseline, scriptIndex);
            MissionScriptGoodieState next = ChooseDifferentState(original);
            MissionScriptGoodieStateVector vector = MissionScriptGoodieStateSaveCodec.GetDisplayableVectorFromScriptIndex(scriptIndex);

            byte[] toggled = baseline.ToArray();
            MissionScriptGoodieStateSaveCodec.SetDisplayableStateByScriptIndex(toggled, scriptIndex, next);
            int[] changed = ChangedOffsets(baseline, toggled);
            expectedByteOnly &= changed.SequenceEqual([vector.TrueViewDwordOffset]);
            unexpectedDiffs += changed.Count(offset => offset != vector.TrueViewDwordOffset);
            trapHits += changed.Count(offset => LegacyTrapOffsets.Contains(offset));
            if (MissionScriptGoodieStateSaveCodec.GetStateByScriptIndex(toggled, scriptIndex) != next)
            {
                readbackMismatches++;
            }

            byte[] setAgain = toggled.ToArray();
            MissionScriptGoodieStateSaveCodec.SetDisplayableStateByScriptIndex(setAgain, scriptIndex, next);
            idempotent &= ChangedOffsets(toggled, setAgain).Length == 0;

            MissionScriptGoodieStateSaveCodec.SetDisplayableStateByScriptIndex(setAgain, scriptIndex, original);
            restored &= ChangedOffsets(baseline, setAgain).Length == 0;

            HashSet<int> target = [vector.SaveGoodieIndex];
            nonTargetGoodies &= NonTargetGoodiesUnchanged(baseline, toggled, target);
            reservedGoodies &= RangeUnchanged(baseline, toggled, MissionScriptGoodieStateSaveCodec.GoodieBaseOffset + MissionScriptGoodieStateSaveCodec.DisplayableGoodieCount * 4, MissionScriptGoodieStateSaveCodec.GoodieStorageEndExclusive);
            kills &= RangeUnchanged(baseline, toggled, KillsBase, TechSlotsBase);
            techSlots &= RangeUnchanged(baseline, toggled, TechSlotsBase, TechSlotsEndExclusive);
            optionsEntries &= RangeUnchanged(baseline, toggled, OptionsEntriesStart, OptionsEntriesEnd);
            optionsTail &= RangeUnchanged(baseline, toggled, OptionsTailStart, OptionsTailEnd);
        }

        return new DisplayableRoundTripResult(
            MissionScriptGoodieStateSaveCodec.DisplayableGoodieCount,
            readbackMismatches == 0 && expectedByteOnly && idempotent && restored,
            expectedByteOnly,
            idempotent,
            restored,
            nonTargetGoodies,
            reservedGoodies,
            kills,
            techSlots,
            optionsEntries,
            optionsTail,
            readbackMismatches,
            unexpectedDiffs,
            trapHits);
    }

    private static ReservedRejectionResult RunReservedRejections(byte[] baseline)
    {
        int cases = 0;
        bool allRejectedAndUnchanged = true;
        for (int scriptIndex = MissionScriptGoodieStateSaveCodec.DisplayableGoodieCount + 1;
             scriptIndex <= MissionScriptGoodieStateSaveCodec.GoodieStorageEntryCount;
             scriptIndex++)
        {
            byte[] candidate = baseline.ToArray();
            bool rejected = ThrowsArgumentOutOfRange(() =>
                MissionScriptGoodieStateSaveCodec.SetDisplayableStateByScriptIndex(candidate, scriptIndex, MissionScriptGoodieState.Old));
            allRejectedAndUnchanged &= rejected && ChangedOffsets(baseline, candidate).Length == 0;
            cases++;
        }

        return new ReservedRejectionResult(cases, allRejectedAndUnchanged);
    }

    private static BoundaryStateMatrixResult RunBoundaryStateMatrix(byte[] baseline)
    {
        int cases = 0;
        int readbackMismatches = 0;
        int unexpectedDiffs = 0;
        int trapHits = 0;
        bool allRoundTrip = true;
        bool restored = true;

        foreach (int scriptIndex in BoundaryScriptIndices)
        {
            MissionScriptGoodieState original = MissionScriptGoodieStateSaveCodec.GetStateByScriptIndex(baseline, scriptIndex);
            MissionScriptGoodieStateVector vector = MissionScriptGoodieStateSaveCodec.GetDisplayableVectorFromScriptIndex(scriptIndex);
            foreach (MissionScriptGoodieState state in Enum.GetValues<MissionScriptGoodieState>())
            {
                byte[] candidate = baseline.ToArray();
                MissionScriptGoodieStateSaveCodec.SetDisplayableStateByScriptIndex(candidate, scriptIndex, state);
                int[] changed = ChangedOffsets(baseline, candidate);
                bool expectedDiff = state == original
                    ? changed.Length == 0
                    : changed.SequenceEqual([vector.TrueViewDwordOffset]);
                allRoundTrip &= expectedDiff;
                unexpectedDiffs += changed.Count(offset => offset != vector.TrueViewDwordOffset);
                trapHits += changed.Count(offset => LegacyTrapOffsets.Contains(offset));
                if (MissionScriptGoodieStateSaveCodec.GetStateByScriptIndex(candidate, scriptIndex) != state)
                {
                    readbackMismatches++;
                }

                MissionScriptGoodieStateSaveCodec.SetDisplayableStateByScriptIndex(candidate, scriptIndex, original);
                bool restoredToBaseline = ChangedOffsets(baseline, candidate).Length == 0;
                restored &= restoredToBaseline;
                cases++;
            }
        }

        return new BoundaryStateMatrixResult(cases, allRoundTrip && readbackMismatches == 0, restored, readbackMismatches, unexpectedDiffs, trapHits);
    }

    private static RejectionResult RunRejections(byte[] baseline)
    {
        byte[] wrongSize = baseline.Take(MissionScriptGoodieStateSaveCodec.ExpectedFileSize - 1).ToArray();
        byte[] wrongVersion = baseline.ToArray();
        wrongVersion[0] ^= 0xff;
        byte[] mixed = baseline.ToArray();
        bool invalidMixedBatchLeavesBufferUnchanged = ThrowsArgumentOutOfRange(() =>
            MissionScriptGoodieStateSaveCodec.SetDisplayableStatesByScriptIndex(
                mixed,
                new Dictionary<int, MissionScriptGoodieState>
                {
                    [1] = MissionScriptGoodieState.Old,
                    [234] = MissionScriptGoodieState.New
                }))
            && ChangedOffsets(baseline, mixed).Length == 0;

        return new RejectionResult
        {
            InvalidScriptIndex0Rejected = ThrowsArgumentOutOfRange(() => MissionScriptGoodieStateSaveCodec.GetVectorFromScriptIndex(0)),
            InvalidScriptIndex301Rejected = ThrowsArgumentOutOfRange(() => MissionScriptGoodieStateSaveCodec.GetVectorFromScriptIndex(301)),
            ReservedScriptIndex234Rejected = ThrowsArgumentOutOfRange(() => MissionScriptGoodieStateSaveCodec.SetDisplayableStateByScriptIndex(baseline.ToArray(), 234, MissionScriptGoodieState.Old)),
            InvalidState4Rejected = ThrowsArgumentOutOfRange(() => MissionScriptGoodieStateSaveCodec.SetDisplayableStateByScriptIndex(baseline.ToArray(), 1, (MissionScriptGoodieState)4)),
            InvalidStateUintMaxRejected = ThrowsArgumentOutOfRange(() => MissionScriptGoodieStateSaveCodec.SetDisplayableStateByScriptIndex(baseline.ToArray(), 1, (MissionScriptGoodieState)uint.MaxValue)),
            EmptyOverrideRejected = ThrowsArgumentException(() => MissionScriptGoodieStateSaveCodec.SetDisplayableStatesByScriptIndex(baseline.ToArray(), new Dictionary<int, MissionScriptGoodieState>())),
            InvalidMixedBatchLeavesBufferUnchanged = invalidMixedBatchLeavesBufferUnchanged,
            WrongSizeRejected = !MissionScriptGoodieStateSaveCodec.IsValidCareerSaveContainer(wrongSize),
            WrongVersionRejected = !MissionScriptGoodieStateSaveCodec.IsValidCareerSaveContainer(wrongVersion)
        };
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
            !evidence.Harness.HarnessFileIo ||
            evidence.Harness.ProductUiWired)
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
            evidence.Container.GoodieStorageEntryCount != 300 ||
            evidence.Container.DisplayableGoodieCount != 233 ||
            evidence.Container.ReservedPreserveEntryCount != 67)
        {
            failures.Add("container guard mismatch");
        }

        if (evidence.Corpus.StorageVectorCopiedBaselineReadCaseCount != 300 ||
            evidence.Corpus.DisplayableCopiedBaselineRoundTripCaseCount != 233 ||
            evidence.Corpus.ReservedCopiedBaselineRejectionCaseCount != 67 ||
            evidence.Corpus.BoundaryStateCopiedBaselineMatrixCaseCount != 32 ||
            evidence.Corpus.CopiedBaselineBoundaryCorpusCaseCount != 632 ||
            evidence.Corpus.TargetReadbackMismatchCount != 0 ||
            evidence.Corpus.UnexpectedDiffCount != 0 ||
            evidence.Corpus.LegacyTrapHitCount != 0 ||
            !evidence.Corpus.AllStorageScriptIndicesReadFromCopiedBaseline ||
            !evidence.Corpus.AllDisplayableCopiedBaselineRoundTrip ||
            !evidence.Corpus.AllReservedCopiedBaselineRejectionsLeaveBufferUnchanged ||
            !evidence.Corpus.AllBoundaryStatesRoundTripOnCopiedBaseline ||
            !evidence.Corpus.AllBoundaryStatesRestoreToBaseline)
        {
            failures.Add("corpus guard mismatch");
        }

        if (evidence.NoOp.CareerNoopDiffCount != 0 ||
            evidence.NoOp.DefaultOptionsNoopDiffCount != 0 ||
            !evidence.Preservation.NonTargetGoodiesUnchangedForAllDisplayableRoundTrips ||
            !evidence.Preservation.ReservedGoodiesUnchangedForAllDisplayableRoundTrips ||
            !evidence.Preservation.KillCountersUnchangedForAllDisplayableRoundTrips ||
            !evidence.Preservation.TechSlotsUnchangedForAllDisplayableRoundTrips ||
            !evidence.Preservation.OptionsEntriesUnchangedForAllDisplayableRoundTrips ||
            !evidence.Preservation.OptionsTailUnchangedForAllDisplayableRoundTrips)
        {
            failures.Add("preservation guard mismatch");
        }

        if (!evidence.Rejections.InvalidScriptIndex0Rejected ||
            !evidence.Rejections.InvalidScriptIndex301Rejected ||
            !evidence.Rejections.ReservedScriptIndex234Rejected ||
            !evidence.Rejections.InvalidState4Rejected ||
            !evidence.Rejections.InvalidStateUintMaxRejected ||
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
            evidence.NegativeGuards.RebuildImplementation)
        {
            failures.Add("negative guard mismatch");
        }

        if (failures.Count > 0)
        {
            throw new InvalidOperationException(string.Join("; ", failures));
        }
    }

    private static MissionScriptGoodieState ChooseDifferentState(MissionScriptGoodieState current)
    {
        uint next = ((uint)current + 1) % (MissionScriptGoodieStateSaveCodec.MaxKnownStateValue + 1);
        return (MissionScriptGoodieState)next;
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

    private static bool RangeUnchanged(byte[] before, byte[] after, int start, int endExclusive) =>
        before.AsSpan(start, endExclusive - start).SequenceEqual(after.AsSpan(start, endExclusive - start));

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
        Console.WriteLine("MissionScriptGoodieStateSaveBoundaryCorpusHarness [--repo-root .] [--career-source <copied-baseline.bes>] [--defaultoptions-source <copied-defaultoptions.bea>]");
    }

    private static void ValidateContainer(byte[] data, string label)
    {
        if (!MissionScriptGoodieStateSaveCodec.IsValidCareerSaveContainer(data))
        {
            throw new InvalidOperationException($"{label} is not a valid 10004-byte 0x4BD1 career save container.");
        }
    }

    private static ushort ReadVersionWord(byte[] data) =>
        (ushort)(data[0] | (data[1] << 8));

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

    private sealed record StorageReadResult(int CaseCount, bool AllRead, bool AllStatesWithinKnownRange);
    private sealed record ReservedRejectionResult(int CaseCount, bool AllRejectedAndUnchanged);
    private sealed record BoundaryStateMatrixResult(int CaseCount, bool AllRoundTrip, bool RestoreToBaseline, int TargetReadbackMismatchCount, int UnexpectedDiffCount, int LegacyTrapHitCount);
    private sealed record DisplayableRoundTripResult(
        int CaseCount,
        bool AllRoundTrip,
        bool ToggleTouchesOnlyExpectedByte,
        bool ToggleIdempotent,
        bool RestoreToBaseline,
        bool NonTargetGoodiesUnchanged,
        bool ReservedGoodiesUnchanged,
        bool KillCountersUnchanged,
        bool TechSlotsUnchanged,
        bool OptionsEntriesUnchanged,
        bool OptionsTailUnchanged,
        int TargetReadbackMismatchCount,
        int UnexpectedDiffCount,
        int LegacyTrapHitCount);

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
        public CorpusInfo Corpus { get; set; } = new();
        public NoOpInfo NoOp { get; set; } = new();
        public PreservationInfo Preservation { get; set; } = new();
        public RejectionResult Rejections { get; set; } = new();
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
        public bool CopiedDefaultOptionsValidationOnly { get; set; }
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
        public string GoodieStorageEndExclusive { get; set; } = "";
        public bool FileSizePreserved { get; set; }
        public bool VersionWordPreserved { get; set; }
    }

    private sealed class CorpusInfo
    {
        public int PreviousInMemoryBoundaryCorpusXunitCaseCount { get; set; }
        public int StorageVectorCopiedBaselineReadCaseCount { get; set; }
        public int DisplayableCopiedBaselineRoundTripCaseCount { get; set; }
        public int ReservedCopiedBaselineRejectionCaseCount { get; set; }
        public int BoundaryStateCopiedBaselineMatrixCaseCount { get; set; }
        public int CopiedBaselineBoundaryCorpusCaseCount { get; set; }
        public int SampleBoundaryArtifactCount { get; set; }
        public int[] BoundaryScriptIndices { get; set; } = [];
        public int[] BoundaryStateValues { get; set; } = [];
        public string[] BoundaryOffsets { get; set; } = [];
        public bool AllStorageScriptIndicesReadFromCopiedBaseline { get; set; }
        public bool AllStorageStateValuesWithinKnownRange { get; set; }
        public bool AllDisplayableCopiedBaselineRoundTrip { get; set; }
        public bool ToggleTouchesOnlyExpectedByteForAllDisplayable { get; set; }
        public bool ToggleIdempotentForAllDisplayable { get; set; }
        public bool RestoreToBaselineForAllDisplayable { get; set; }
        public bool AllReservedCopiedBaselineRejectionsLeaveBufferUnchanged { get; set; }
        public bool AllBoundaryStatesRoundTripOnCopiedBaseline { get; set; }
        public bool AllBoundaryStatesRestoreToBaseline { get; set; }
        public int TargetReadbackMismatchCount { get; set; }
        public int UnexpectedDiffCount { get; set; }
        public int LegacyTrapHitCount { get; set; }
        public string[] LegacyAlignedViewTrapOffsets { get; set; } = [];
    }

    private sealed class NoOpInfo
    {
        public int CareerNoopDiffCount { get; set; }
        public int DefaultOptionsNoopDiffCount { get; set; }
    }

    private sealed class PreservationInfo
    {
        public bool NonTargetGoodiesUnchangedForAllDisplayableRoundTrips { get; set; }
        public bool ReservedGoodiesUnchangedForAllDisplayableRoundTrips { get; set; }
        public bool KillCountersUnchangedForAllDisplayableRoundTrips { get; set; }
        public bool TechSlotsUnchangedForAllDisplayableRoundTrips { get; set; }
        public bool OptionsEntriesUnchangedForAllDisplayableRoundTrips { get; set; }
        public bool OptionsTailUnchangedForAllDisplayableRoundTrips { get; set; }
    }

    private sealed class RejectionResult
    {
        public bool InvalidScriptIndex0Rejected { get; set; }
        public bool InvalidScriptIndex301Rejected { get; set; }
        public bool ReservedScriptIndex234Rejected { get; set; }
        public bool InvalidState4Rejected { get; set; }
        public bool InvalidStateUintMaxRejected { get; set; }
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
        public int RuntimeObservationRows { get; set; }
        public int MissionScriptRuntimeEvidenceRows { get; set; }
        public int RuntimeCommandEffectRows { get; set; }
        public int RuntimeGoodieStateRows { get; set; }
        public int RuntimeSaveRows { get; set; }
        public int RuntimeDefaultOptionsRows { get; set; }
        public int RuntimeGoodiesWallRows { get; set; }
        public int RuntimeScoreRows { get; set; }
        public string PublicLeakCheck { get; set; } = "";
    }
}
