using System.Buffers.Binary;
using System.Security.Cryptography;
using System.Text.Json;
using System.Text.Json.Serialization;
using Onslaught___Career_Editor;

namespace Onslaught___Career_Editor.Tools;

internal static class Program
{
    private const string SchemaVersion = "missionscript-goodie-state-save-copied-baseline-byte-diff-private-evidence.v1";
    private const string EvidenceRootRelative = "subagents/static-to-proof/missionscript-goodie-state-save-copied-baseline-byte-diff-fixture-proof";
    private const string SourceEvidenceRootRelative = "subagents/static-to-proof/save-options-controller-byte-preservation-copied-file-proof";
    private const string CareerSourceName = "career-baseline.bes";
    private const string DefaultOptionsSourceName = "defaultoptions-baseline.bea";
    private const string SummaryFileName = "evidence-summary.private.json";

    private const int ExpectedSize = 10004;
    private const ushort VersionWord = 0x4BD1;
    private const int GoodieBase = 0x1F46;
    private const int GoodieCount = 300;
    private const int DisplayableGoodieCount = 233;
    private const int GoodieEndExclusive = GoodieBase + GoodieCount * 4;
    private const int ReservedGoodiesStart = GoodieBase + DisplayableGoodieCount * 4;
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

        string careerBaselinePath = Path.Combine(outRoot, "career-goodie-baseline.bes");
        string defaultOptionsBaselinePath = Path.Combine(outRoot, "defaultoptions-goodie-baseline.bea");
        string careerNoopPath = Path.Combine(outRoot, "career-goodie-noop.bes");
        string defaultOptionsNoopPath = Path.Combine(outRoot, "defaultoptions-goodie-noop.bea");
        string patchedPath = Path.Combine(outRoot, "career-goodie-script-boundary-patch.bes");
        string idempotentPath = Path.Combine(outRoot, "career-goodie-idempotent-patch.bes");
        string roundtripPath = Path.Combine(outRoot, "career-goodie-roundtrip-original-states.bes");

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

        SaveAnalysis analysis = BesFilePatcher.AnalyzeSave(careerBaselinePath);
        if (!analysis.IsValid || analysis.GoodieStates.Count != GoodieCount || analysis.GoodiesReserved != GoodieCount - DisplayableGoodieCount)
        {
            throw new InvalidOperationException("Career baseline did not analyze as a 300-row Goodie save.");
        }

        Dictionary<int, uint> newStatesByIndex = new();
        Dictionary<int, uint> originalStatesByIndex = new();
        List<GoodieTargetInfo> targets = new();
        foreach (int scriptIndex in ScriptIndices)
        {
            int saveIndex = scriptIndex - 1;
            GoodieStateDetail detail = analysis.GoodieStates.Single(row => row.Index == saveIndex);
            uint next = ChooseDifferentState(detail.RawState);
            newStatesByIndex[saveIndex] = next;
            originalStatesByIndex[saveIndex] = detail.RawState;
            targets.Add(new GoodieTargetInfo
            {
                ScriptIndex = scriptIndex,
                SaveGoodieIndex = saveIndex,
                FileOffset = HexOffset(GoodieBase + saveIndex * 4),
                BeforeState = detail.RawState,
                AfterState = next,
                BeforeLabel = detail.StateLabel,
                Displayable = detail.IsDisplayable
            });
        }

        PatchResult patch = BesFilePatcher.PatchGoodieStates(careerBaselinePath, patchedPath, newStatesByIndex);
        RequireSuccess(patch, "Goodie patch");
        PatchResult idempotent = BesFilePatcher.PatchGoodieStates(patchedPath, idempotentPath, newStatesByIndex);
        RequireSuccess(idempotent, "Goodie idempotent patch");
        PatchResult roundtrip = BesFilePatcher.PatchGoodieStates(patchedPath, roundtripPath, originalStatesByIndex);
        RequireSuccess(roundtrip, "Goodie roundtrip patch");

        string rejectedReservedPath = Path.Combine(outRoot, "should-not-create-reserved-goodie.bes");
        string rejectedInvalidStatePath = Path.Combine(outRoot, "should-not-create-invalid-state.bes");
        string rejectedInPlacePath = careerBaselinePath;
        string rejectedEmptyPath = Path.Combine(outRoot, "should-not-create-empty-goodie.bes");
        PatchResult reservedReject = BesFilePatcher.PatchGoodieStates(careerBaselinePath, rejectedReservedPath, new Dictionary<int, uint> { [233] = 3 });
        PatchResult invalidStateReject = BesFilePatcher.PatchGoodieStates(careerBaselinePath, rejectedInvalidStatePath, new Dictionary<int, uint> { [0] = 4 });
        PatchResult inPlaceReject = BesFilePatcher.PatchGoodieStates(careerBaselinePath, rejectedInPlacePath, new Dictionary<int, uint> { [0] = 1 });
        PatchResult emptyReject = BesFilePatcher.PatchGoodieStates(careerBaselinePath, rejectedEmptyPath, new Dictionary<int, uint>());

        byte[] patched = File.ReadAllBytes(patchedPath);
        byte[] idempotentBytes = File.ReadAllBytes(idempotentPath);
        byte[] roundtripBytes = File.ReadAllBytes(roundtripPath);
        ValidateContainer(patched, "patched career");
        ValidateContainer(idempotentBytes, "idempotent career");
        ValidateContainer(roundtripBytes, "roundtrip career");

        int[] targetOffsets = targets.SelectMany(row => Enumerable.Range(ParseHex(row.FileOffset), 4)).ToArray();
        int[] baselineToPatch = ChangedOffsets(careerBaseline, patched);
        int[] patchToIdempotent = ChangedOffsets(patched, idempotentBytes);
        int[] roundtripToBaseline = ChangedOffsets(roundtripBytes, careerBaseline);
        int[] unexpectedOffsets = baselineToPatch.Where(offset => !targetOffsets.Contains(offset)).ToArray();
        int[] legacyTrapHits = baselineToPatch.Where(offset => LegacyTrapOffsets.Contains(offset)).ToArray();

        foreach (GoodieTargetInfo target in targets)
        {
            uint readback = ReadU32(patched, ParseHex(target.FileOffset));
            target.ReadbackState = readback;
            target.ReadbackMatches = readback == target.AfterState;
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
                PriorEvidenceClass = "validated copied real career .bes and defaultoptions.bea baselines from prior ignored evidence",
                SourcePathsPublic = false,
                SourceHashesPublic = false,
                ArtifactPathsPublic = false,
                ArtifactHashesPublic = false,
                RawBytesPublic = false
            },
            Implementation = new ImplementationInfo
            {
                ToolProjectPath = "tools/MissionScriptGoodieStateSaveHarness/MissionScriptGoodieStateSaveHarness.csproj",
                AppCorePatcherPath = "OnslaughtCareerEditor.AppCore/BesFilePatcher.cs",
                AppCoreMethod = "BesFilePatcher.PatchGoodieStates",
                AppCoreServicesUsed = true,
                ProductUiWired = false,
                HarnessFileIo = true,
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
            Container = new ContainerInfo
            {
                ExpectedSize = ExpectedSize,
                ExpectedSizeHex = "0x2714",
                VersionWord = Hex(VersionWord, 4),
                TrueViewRule = "file_offset = 0x0002 + career_offset",
                GoodieBase = HexOffset(GoodieBase),
                GoodieStorageEntryCount = GoodieCount,
                DisplayableGoodieCount = DisplayableGoodieCount,
                ReservedPreserveEntryCount = GoodieCount - DisplayableGoodieCount,
                AllOutputsFileSizePreserved = new[] { careerBaseline, defaultOptionsBaseline, careerNoop, defaultOptionsNoop, patched, idempotentBytes, roundtripBytes }.All(row => row.Length == ExpectedSize),
                AllOutputsVersionWordPreserved = new[] { careerBaseline, defaultOptionsBaseline, careerNoop, defaultOptionsNoop, patched, idempotentBytes, roundtripBytes }.All(row => ReadVersionWord(row) == VersionWord)
            },
            Analysis = new AnalysisInfo
            {
                CareerAnalysisValid = analysis.IsValid,
                GoodieStateRowCount = analysis.GoodieStates.Count,
                DisplayableGoodieCount = analysis.GoodieStates.Count(row => row.IsDisplayable),
                ReservedGoodieCount = analysis.GoodiesReserved
            },
            Operation = new OperationInfo
            {
                Service = "BesFilePatcher.PatchGoodieStates",
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
                ReservedGoodiesUnchanged = RangeUnchanged(careerBaseline, patched, ReservedGoodiesStart, GoodieEndExclusive),
                KillCountersUnchanged = RangeUnchanged(careerBaseline, patched, KillsBase, TechSlotsBase),
                TechSlotsUnchanged = RangeUnchanged(careerBaseline, patched, TechSlotsBase, TechSlotsEndExclusive),
                OptionsEntriesUnchanged = RangeUnchanged(careerBaseline, patched, OptionsEntriesStart, OptionsEntriesEnd),
                OptionsTailUnchanged = RangeUnchanged(careerBaseline, patched, OptionsTailStart, OptionsTailEnd)
            },
            Rejections = new RejectionInfo
            {
                ReservedIndex233Rejected = !reservedReject.Success && !File.Exists(rejectedReservedPath),
                InvalidState4Rejected = !invalidStateReject.Success && !File.Exists(rejectedInvalidStatePath),
                InPlaceRejected = !inPlaceReject.Success,
                EmptyOverrideRejected = !emptyReject.Success && !File.Exists(rejectedEmptyPath)
            },
            CopiedArtifacts =
            [
                FileRow(repoRoot, "career Goodie baseline", careerBaselinePath, careerBaseline),
                FileRow(repoRoot, "defaultoptions Goodie baseline", defaultOptionsBaselinePath, defaultOptionsBaseline),
                FileRow(repoRoot, "career Goodie no-op", careerNoopPath, careerNoop),
                FileRow(repoRoot, "defaultoptions Goodie no-op", defaultOptionsNoopPath, defaultOptionsNoop),
                FileRow(repoRoot, "career Goodie script-boundary patch", patchedPath, patched),
                FileRow(repoRoot, "career Goodie idempotent patch", idempotentPath, idempotentBytes),
                FileRow(repoRoot, "career Goodie roundtrip original states", roundtripPath, roundtripBytes)
            ],
            NegativeGuards = new NegativeGuardInfo
            {
                SaveSynthesis = false,
                InstalledGameMutation = false,
                OriginalExecutableMutation = false,
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
                RuntimeScoreBehaviorProven = false
            }
        };

        ValidateEvidence(evidence);
        return evidence;
    }

    private static uint ChooseDifferentState(uint current)
    {
        uint normalized = current <= 3 ? current : 0;
        return (normalized + 1) % 4;
    }

    private static bool NonTargetGoodiesUnchanged(byte[] before, byte[] after, HashSet<int> targetIndexes)
    {
        for (int index = 0; index < GoodieCount; index++)
        {
            if (targetIndexes.Contains(index))
            {
                continue;
            }

            int offset = GoodieBase + index * 4;
            if (!before.AsSpan(offset, 4).SequenceEqual(after.AsSpan(offset, 4)))
            {
                return false;
            }
        }

        return true;
    }

    private static void ValidateEvidence(Evidence evidence)
    {
        if (evidence.Status != "PASS" ||
            !evidence.Provenance.CopyBeforeWrite ||
            !evidence.Provenance.SourcesUnderPriorPrivateEvidenceRoot ||
            !evidence.Provenance.OutputsUnderProofPrivateEvidenceRoot ||
            !evidence.Provenance.SourceAndOutputPathsDistinct ||
            evidence.Provenance.CareerSourceToInputDiffCount != 0 ||
            evidence.Provenance.DefaultOptionsSourceToInputDiffCount != 0 ||
            !evidence.Provenance.CareerSourceUnchanged ||
            !evidence.Provenance.DefaultOptionsSourceUnchanged)
        {
            throw new InvalidOperationException("Provenance contract failed.");
        }

        if (!evidence.Container.AllOutputsFileSizePreserved ||
            !evidence.Container.AllOutputsVersionWordPreserved ||
            !evidence.Analysis.CareerAnalysisValid ||
            evidence.Analysis.GoodieStateRowCount != GoodieCount ||
            evidence.Analysis.DisplayableGoodieCount != DisplayableGoodieCount ||
            evidence.Analysis.ReservedGoodieCount != GoodieCount - DisplayableGoodieCount)
        {
            throw new InvalidOperationException("Container or analysis contract failed.");
        }

        if (evidence.Operation.TargetDwordWriteCount != ScriptIndices.Length ||
            evidence.Operation.UnexpectedDiffCount != 0 ||
            evidence.Operation.LegacyTrapHitCount != 0 ||
            !evidence.Operation.AllTargetReadbacksMatch)
        {
            throw new InvalidOperationException("Goodie operation contract failed.");
        }

        if (evidence.NoOpAndRoundTrip.CareerNoopDiffCount != 0 ||
            evidence.NoOpAndRoundTrip.DefaultOptionsNoopDiffCount != 0 ||
            evidence.NoOpAndRoundTrip.PatchToIdempotentDiffCount != 0 ||
            evidence.NoOpAndRoundTrip.RoundtripToBaselineDiffCount != 0)
        {
            throw new InvalidOperationException("No-op/idempotent/roundtrip contract failed.");
        }

        if (!evidence.Preservation.NonTargetGoodiesUnchanged ||
            !evidence.Preservation.ReservedGoodiesUnchanged ||
            !evidence.Preservation.KillCountersUnchanged ||
            !evidence.Preservation.TechSlotsUnchanged ||
            !evidence.Preservation.OptionsEntriesUnchanged ||
            !evidence.Preservation.OptionsTailUnchanged)
        {
            throw new InvalidOperationException("Preservation contract failed.");
        }

        if (!evidence.Rejections.ReservedIndex233Rejected ||
            !evidence.Rejections.InvalidState4Rejected ||
            !evidence.Rejections.InPlaceRejected ||
            !evidence.Rejections.EmptyOverrideRejected)
        {
            throw new InvalidOperationException("Rejection contract failed.");
        }
    }

    private static Options ParseArgs(string[] args)
    {
        Options options = new();
        for (int i = 0; i < args.Length; i++)
        {
            string arg = args[i];
            switch (arg)
            {
                case "-h":
                case "--help":
                    options.ShowHelp = true;
                    break;
                case "--repo-root":
                    options.RepoRoot = RequireValue(args, ref i, arg);
                    break;
                case "--out-root":
                    options.OutRoot = RequireValue(args, ref i, arg);
                    break;
                case "--career-source":
                    options.CareerSource = RequireValue(args, ref i, arg);
                    break;
                case "--defaultoptions-source":
                    options.DefaultOptionsSource = RequireValue(args, ref i, arg);
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
        Console.WriteLine("Usage: dotnet run --project tools/MissionScriptGoodieStateSaveHarness -- [--repo-root .]");
    }

    private static void RequireSuccess(PatchResult result, string label)
    {
        if (!result.Success)
        {
            throw new InvalidOperationException($"{label} failed: {result.Message}");
        }
    }

    private static void ValidateContainer(byte[] data, string label)
    {
        if (data.Length != ExpectedSize)
        {
            throw new InvalidOperationException($"{label}: expected {ExpectedSize} bytes, got {data.Length}.");
        }

        ushort version = ReadVersionWord(data);
        if (version != VersionWord)
        {
            throw new InvalidOperationException($"{label}: expected version 0x{VersionWord:X4}, got 0x{version:X4}.");
        }
    }

    private static ushort ReadVersionWord(byte[] data) =>
        BinaryPrimitives.ReadUInt16LittleEndian(data.AsSpan(0, 2));

    private static uint ReadU32(byte[] data, int offset) =>
        BinaryPrimitives.ReadUInt32LittleEndian(data.AsSpan(offset, 4));

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
        public ImplementationInfo Implementation { get; set; } = new();
        public ProvenanceInfo Provenance { get; set; } = new();
        public ContainerInfo Container { get; set; } = new();
        public AnalysisInfo Analysis { get; set; } = new();
        public OperationInfo Operation { get; set; } = new();
        public RoundTripInfo NoOpAndRoundTrip { get; set; } = new();
        public PreservationInfo Preservation { get; set; } = new();
        public RejectionInfo Rejections { get; set; } = new();
        public ArtifactInfo[] CopiedArtifacts { get; set; } = [];
        public NegativeGuardInfo NegativeGuards { get; set; } = new();
    }

    private sealed class SourceInfo
    {
        public string PriorEvidenceClass { get; set; } = "";
        public bool SourcePathsPublic { get; set; }
        public bool SourceHashesPublic { get; set; }
        public bool ArtifactPathsPublic { get; set; }
        public bool ArtifactHashesPublic { get; set; }
        public bool RawBytesPublic { get; set; }
    }

    private sealed class ImplementationInfo
    {
        public string ToolProjectPath { get; set; } = "";
        public string AppCorePatcherPath { get; set; } = "";
        public string AppCoreMethod { get; set; } = "";
        public bool AppCoreServicesUsed { get; set; }
        public bool ProductUiWired { get; set; }
        public bool HarnessFileIo { get; set; }
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

    private sealed class ContainerInfo
    {
        public int ExpectedSize { get; set; }
        public string ExpectedSizeHex { get; set; } = "";
        public string VersionWord { get; set; } = "";
        public string TrueViewRule { get; set; } = "";
        public string GoodieBase { get; set; } = "";
        public int GoodieStorageEntryCount { get; set; }
        public int DisplayableGoodieCount { get; set; }
        public int ReservedPreserveEntryCount { get; set; }
        public bool AllOutputsFileSizePreserved { get; set; }
        public bool AllOutputsVersionWordPreserved { get; set; }
    }

    private sealed class AnalysisInfo
    {
        public bool CareerAnalysisValid { get; set; }
        public int GoodieStateRowCount { get; set; }
        public int DisplayableGoodieCount { get; set; }
        public int ReservedGoodieCount { get; set; }
    }

    private sealed class OperationInfo
    {
        public string Service { get; set; } = "";
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
        public bool ReservedIndex233Rejected { get; set; }
        public bool InvalidState4Rejected { get; set; }
        public bool InPlaceRejected { get; set; }
        public bool EmptyOverrideRejected { get; set; }
    }

    private sealed class ArtifactInfo
    {
        public string Label { get; set; } = "";
        public string RelativePath { get; set; } = "";
        public int Size { get; set; }
        public string VersionWord { get; set; } = "";
        public string Sha256 { get; set; } = "";
    }

    private sealed class NegativeGuardInfo
    {
        public bool SaveSynthesis { get; set; }
        public bool InstalledGameMutation { get; set; }
        public bool OriginalExecutableMutation { get; set; }
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
    }
}
