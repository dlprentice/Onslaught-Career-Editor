using System.Buffers.Binary;
using System.Security.Cryptography;
using System.Text.Json;
using System.Text.Json.Serialization;
using Onslaught___Career_Editor;

namespace Onslaught___Career_Editor.Tools;

internal static class Program
{
    private const string SchemaVersion = "save-options-byte-preservation-appcore-implementation-contract-private-evidence.v1";
    private const string EvidenceRootRelative = "subagents/static-to-proof/save-options-byte-preservation-appcore-implementation-contract-proof";
    private const string SourceEvidenceRootRelative = "subagents/static-to-proof/save-options-controller-byte-preservation-copied-file-proof";
    private const string CareerSourceName = "career-baseline.bes";
    private const string DefaultOptionsSourceName = "defaultoptions-baseline.bea";
    private const string SummaryFileName = "evidence-summary.private.json";

    private const int CareerAircraftKillOffset = 0x23F6;
    private const int CareerAircraftKillMetadataOffset = 0x23F9;
    private const int SoundVolumeOffset = 0x248E;
    private const int MusicVolumeOffset = 0x2492;
    private const int OptionsEntriesStart = 0x24BE;
    private const int OptionsEntriesEnd = 0x26BE;
    private const int OptionsTailStart = 0x26BE;
    private const int OptionsTailEnd = 0x2714;

    private static readonly int[] LegacyTrapOffsets = [0x23A4, 0x22D4, 0x240C];
    private static readonly int[] AircraftLower24AllowedOffsets = [0x23F6, 0x23F7, 0x23F8];

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
            string requiredOutRoot = Path.Combine(repoRoot, EvidenceRootRelative);
            string outRoot = Path.GetFullPath(options.OutRoot ?? requiredOutRoot);
            if (!PathsEqual(outRoot, requiredOutRoot))
            {
                throw new InvalidOperationException($"Output root must be the proof-private root: {requiredOutRoot}");
            }

            string proofRoot = Path.Combine(repoRoot, "subagents", "static-to-proof");
            if (!IsWithinDirectory(outRoot, proofRoot))
            {
                throw new InvalidOperationException("Output root must stay under subagents/static-to-proof.");
            }

            string careerSource = Path.GetFullPath(options.CareerSource ?? Path.Combine(repoRoot, SourceEvidenceRootRelative, CareerSourceName));
            string defaultOptionsSource = Path.GetFullPath(options.DefaultOptionsSource ?? Path.Combine(repoRoot, SourceEvidenceRootRelative, DefaultOptionsSourceName));
            if (!IsWithinDirectory(careerSource, Path.Combine(repoRoot, SourceEvidenceRootRelative)) ||
                !IsWithinDirectory(defaultOptionsSource, Path.Combine(repoRoot, SourceEvidenceRootRelative)))
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

        string careerInput = Path.Combine(outRoot, "career-appcore-service-input.bes");
        string careerOutput = Path.Combine(outRoot, "career-appcore-aircraft-kill-service-output.bes");
        string defaultOptionsInput = Path.Combine(outRoot, "defaultoptions-appcore-service-input.bea");
        string soundOutput = Path.Combine(outRoot, "defaultoptions-appcore-sound-volume-output.bea");
        string optionsEntriesSource = Path.Combine(outRoot, "defaultoptions-appcore-options-entries-source.bea");
        string optionsEntriesOutput = Path.Combine(outRoot, "defaultoptions-appcore-options-entries-output.bea");
        string optionsTailSource = Path.Combine(outRoot, "defaultoptions-appcore-options-tail-source.bea");
        string optionsTailOutput = Path.Combine(outRoot, "defaultoptions-appcore-options-tail-output.bea");
        string inPlaceInput = Path.Combine(outRoot, "defaultoptions-appcore-inplace-copy.bea");

        File.Copy(careerSource, careerInput, overwrite: true);
        File.Copy(defaultOptionsSource, defaultOptionsInput, overwrite: true);
        File.Copy(defaultOptionsSource, inPlaceInput, overwrite: true);

        byte[] careerInputBytes = File.ReadAllBytes(careerInput);
        byte[] defaultOptionsInputBytes = File.ReadAllBytes(defaultOptionsInput);
        ValidateContainer(careerInputBytes, "career service input");
        ValidateContainer(defaultOptionsInputBytes, "defaultoptions service input");

        PatchResult careerInPlaceReject = SaveEditorService.PatchSave(new SavePatchRequest
        {
            InputPath = careerInput,
            OutputPath = careerInput,
            PatchNodes = false,
            PatchLinks = false,
            PatchGoodies = false,
            PatchKills = true
        });

        PatchResult optionsAsCareerReject = SaveEditorService.PatchSave(new SavePatchRequest
        {
            InputPath = defaultOptionsInput,
            OutputPath = Path.Combine(outRoot, "should-not-create-from-options.bes"),
            PatchNodes = false,
            PatchLinks = false,
            PatchGoodies = false,
            PatchKills = true
        });

        SaveAnalysis careerAnalysis = BesFilePatcher.AnalyzeSave(careerInput);
        if (!careerAnalysis.IsValid || careerAnalysis.KillCounts.Length < 5)
        {
            throw new InvalidOperationException("Career baseline did not analyze as a valid five-category save.");
        }

        Dictionary<int, int> perCategoryKills = new();
        for (int i = 0; i < 5; i++)
        {
            perCategoryKills[i] = careerAnalysis.KillCounts[i];
        }

        int nextAircraftKills = (careerAnalysis.KillCounts[BesFilePatcher.KILL_AIRCRAFT] + 1) & 0x00FFFFFF;
        if (nextAircraftKills == careerAnalysis.KillCounts[BesFilePatcher.KILL_AIRCRAFT])
        {
            nextAircraftKills = (careerAnalysis.KillCounts[BesFilePatcher.KILL_AIRCRAFT] + 2) & 0x00FFFFFF;
        }
        perCategoryKills[BesFilePatcher.KILL_AIRCRAFT] = nextAircraftKills;

        PatchResult careerPatch = SaveEditorService.PatchSave(new SavePatchRequest
        {
            InputPath = careerInput,
            OutputPath = careerOutput,
            PatchNodes = false,
            PatchLinks = false,
            PatchGoodies = false,
            PatchKills = true,
            PerCategoryKills = perCategoryKills
        });
        RequireSuccess(careerPatch, "career service patch");

        byte[] careerOutputBytes = File.ReadAllBytes(careerOutput);
        ValidateContainer(careerOutputBytes, "career service output");
        int[] careerDiffs = ChangedOffsets(careerInputBytes, careerOutputBytes);

        SaveAnalysis defaultOptionsAnalysis = BesFilePatcher.AnalyzeSave(defaultOptionsInput);
        if (!defaultOptionsAnalysis.IsValid)
        {
            throw new InvalidOperationException("defaultoptions baseline did not analyze as valid.");
        }

        float newSoundVolume = defaultOptionsAnalysis.SoundVolume > 0.49f ? 0.25f : 0.75f;
        PatchResult soundPatch = ConfigurationEditorService.PatchConfiguration(new ConfigurationPatchRequest
        {
            InputPath = defaultOptionsInput,
            OutputPath = soundOutput,
            SoundVolumeOverride = newSoundVolume
        });
        RequireSuccess(soundPatch, "configuration sound-volume patch");
        byte[] soundOutputBytes = File.ReadAllBytes(soundOutput);
        ValidateContainer(soundOutputBytes, "sound output");
        int[] soundDiffs = ChangedOffsets(defaultOptionsInputBytes, soundOutputBytes);

        byte[] entriesSourceBytes = defaultOptionsInputBytes.ToArray();
        entriesSourceBytes[OptionsEntriesStart] ^= 0x01;
        File.WriteAllBytes(optionsEntriesSource, entriesSourceBytes);
        PatchResult entriesPatch = ConfigurationEditorService.PatchConfiguration(new ConfigurationPatchRequest
        {
            InputPath = defaultOptionsInput,
            OutputPath = optionsEntriesOutput,
            CopyOptionsFromPath = optionsEntriesSource,
            CopyOptionsEntries = true,
            CopyOptionsTail = false
        });
        RequireSuccess(entriesPatch, "configuration options-entries copy");
        byte[] entriesOutputBytes = File.ReadAllBytes(optionsEntriesOutput);
        ValidateContainer(entriesOutputBytes, "entries output");
        int[] entriesDiffs = ChangedOffsets(defaultOptionsInputBytes, entriesOutputBytes);

        byte[] tailSourceBytes = defaultOptionsInputBytes.ToArray();
        tailSourceBytes[OptionsTailStart] ^= 0x01;
        File.WriteAllBytes(optionsTailSource, tailSourceBytes);
        PatchResult tailPatch = ConfigurationEditorService.PatchConfiguration(new ConfigurationPatchRequest
        {
            InputPath = defaultOptionsInput,
            OutputPath = optionsTailOutput,
            CopyOptionsFromPath = optionsTailSource,
            CopyOptionsEntries = false,
            CopyOptionsTail = true
        });
        RequireSuccess(tailPatch, "configuration options-tail copy");
        byte[] tailOutputBytes = File.ReadAllBytes(optionsTailOutput);
        ValidateContainer(tailOutputBytes, "tail output");
        int[] tailDiffs = ChangedOffsets(defaultOptionsInputBytes, tailOutputBytes);

        byte[] inPlaceBefore = File.ReadAllBytes(inPlaceInput);
        float newMusicVolume = defaultOptionsAnalysis.MusicVolume > 0.49f ? 0.25f : 0.75f;
        PatchResult inPlacePatch = ConfigurationEditorService.PatchConfiguration(new ConfigurationPatchRequest
        {
            InputPath = inPlaceInput,
            OutputPath = inPlaceInput,
            MusicVolumeOverride = newMusicVolume
        });
        RequireSuccess(inPlacePatch, "configuration copied in-place patch");
        byte[] inPlaceAfter = File.ReadAllBytes(inPlaceInput);
        string[] backupFiles = Directory.GetFiles(outRoot, "defaultoptions-appcore-inplace-copy.bea.*.bak");
        if (backupFiles.Length != 1)
        {
            throw new InvalidOperationException($"Expected exactly one copied in-place backup, found {backupFiles.Length}.");
        }
        byte[] inPlaceBackup = File.ReadAllBytes(backupFiles[0]);
        int[] inPlaceDiffs = ChangedOffsets(inPlaceBefore, inPlaceAfter);

        byte[] slotBuffer = careerInputBytes.ToArray();
        MissionScriptSlotBitsetSaveCodec.SetSlot(slotBuffer, 61, true);
        bool slotCodecToggled = MissionScriptSlotBitsetSaveCodec.GetSlot(slotBuffer, 61);
        int[] slotCodecDiffs = ChangedOffsets(careerInputBytes, slotBuffer);

        byte[] careerSourceAfter = File.ReadAllBytes(careerSource);
        byte[] defaultOptionsSourceAfter = File.ReadAllBytes(defaultOptionsSource);

        Evidence evidence = new()
        {
            SchemaVersion = SchemaVersion,
            Status = "PASS",
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
                ToolProjectPath = "tools/SaveOptionsAppCoreContractHarness/SaveOptionsAppCoreContractHarness.csproj",
                AppCoreSavePatchPath = "OnslaughtCareerEditor.AppCore/BesFilePatcher.cs",
                SaveEditorServicePath = "OnslaughtCareerEditor.AppCore/SaveEditorService.cs",
                ConfigurationEditorServicePath = "OnslaughtCareerEditor.AppCore/ConfigurationEditorService.cs",
                SlotCodecPath = "OnslaughtCareerEditor.AppCore/MissionScriptSlotBitsetSaveCodec.cs",
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
                SourceAndOutputPathsDistinct = !PathsEqual(careerSource, careerOutput) && !PathsEqual(defaultOptionsSource, soundOutput),
                CareerSourceUnchanged = careerSourceBefore.SequenceEqual(careerSourceAfter),
                DefaultOptionsSourceUnchanged = defaultOptionsSourceBefore.SequenceEqual(defaultOptionsSourceAfter),
                CareerSourceToInputDiffCount = ChangedOffsets(careerSourceBefore, careerInputBytes).Length,
                DefaultOptionsSourceToInputDiffCount = ChangedOffsets(defaultOptionsSourceBefore, defaultOptionsInputBytes).Length
            },
            Container = new ContainerInfo
            {
                ExpectedSize = BesFilePatcher.EXPECTED_FILE_SIZE,
                SlotCodecExpectedSize = MissionScriptSlotBitsetSaveCodec.ExpectedFileSize,
                VersionWord = Hex(BesFilePatcher.VERSION_WORD, 4),
                SlotCodecVersionWord = Hex(MissionScriptSlotBitsetSaveCodec.VersionWord, 4),
                TrueViewRule = "file_offset = 0x0002 + career_offset",
                CareerSlotsBase = Hex(MissionScriptSlotBitsetSaveCodec.CareerSlotsBaseOffset, 4),
                CareerSlotsEndExclusive = Hex(MissionScriptSlotBitsetSaveCodec.CareerSlotsEndExclusive, 4),
                AllOutputsFileSizePreserved = new[]
                {
                    careerOutputBytes, soundOutputBytes, entriesOutputBytes, tailOutputBytes, inPlaceAfter
                }.All(data => data.Length == BesFilePatcher.EXPECTED_FILE_SIZE),
                AllOutputsVersionWordPreserved = new[]
                {
                    careerOutputBytes, soundOutputBytes, entriesOutputBytes, tailOutputBytes, inPlaceAfter
                }.All(data => ReadVersionWord(data) == BesFilePatcher.VERSION_WORD)
            },
            CareerServicePatch = new CareerServicePatchInfo
            {
                Service = "SaveEditorService.PatchSave",
                PatchNodes = false,
                PatchLinks = false,
                PatchGoodies = false,
                PatchKills = true,
                OptionsLikeInputRejected = !optionsAsCareerReject.Success,
                InPlaceRejected = !careerInPlaceReject.Success,
                ChangedOffsets = careerDiffs.Select(HexOffset).ToArray(),
                ChangedOffsetCount = careerDiffs.Length,
                AllowedOffsets = AircraftLower24AllowedOffsets.Select(HexOffset).ToArray(),
                UnexpectedDiffCount = careerDiffs.Count(offset => !AircraftLower24AllowedOffsets.Contains(offset)),
                MetadataBytePreserved = careerInputBytes[CareerAircraftKillMetadataOffset] == careerOutputBytes[CareerAircraftKillMetadataOffset],
                Lower24Changed = (ReadU32(careerInputBytes, CareerAircraftKillOffset) & 0x00FFFFFF) !=
                                 (ReadU32(careerOutputBytes, CareerAircraftKillOffset) & 0x00FFFFFF),
                LegacyTrapHitCount = careerDiffs.Count(offset => LegacyTrapOffsets.Contains(offset)),
                TechSlotsRangeUnchanged = RangeUnchanged(careerInputBytes, careerOutputBytes, 0x240A, 0x248A),
                OptionsEntriesUnchanged = RangeUnchanged(careerInputBytes, careerOutputBytes, OptionsEntriesStart, OptionsEntriesEnd),
                OptionsTailUnchanged = RangeUnchanged(careerInputBytes, careerOutputBytes, OptionsTailStart, OptionsTailEnd)
            },
            ConfigurationServicePatch = new ConfigurationServicePatchInfo
            {
                Service = "ConfigurationEditorService.PatchConfiguration",
                OptionsLikePathRequired = true,
                SoundVolumeChangedOffsets = soundDiffs.Select(HexOffset).ToArray(),
                SoundVolumeUnexpectedDiffCount = soundDiffs.Count(offset => offset < SoundVolumeOffset || offset >= SoundVolumeOffset + 4),
                SoundVolumeOptionsEntriesUnchanged = RangeUnchanged(defaultOptionsInputBytes, soundOutputBytes, OptionsEntriesStart, OptionsEntriesEnd),
                SoundVolumeOptionsTailUnchanged = RangeUnchanged(defaultOptionsInputBytes, soundOutputBytes, OptionsTailStart, OptionsTailEnd),
                OptionsEntriesCopyChangedOffsets = entriesDiffs.Select(HexOffset).ToArray(),
                OptionsEntriesCopyUnexpectedDiffCount = entriesDiffs.Count(offset => offset < OptionsEntriesStart || offset >= OptionsEntriesEnd),
                OptionsEntriesCopyTailUnchanged = RangeUnchanged(defaultOptionsInputBytes, entriesOutputBytes, OptionsTailStart, OptionsTailEnd),
                OptionsTailCopyChangedOffsets = tailDiffs.Select(HexOffset).ToArray(),
                OptionsTailCopyUnexpectedDiffCount = tailDiffs.Count(offset => offset < OptionsTailStart || offset >= OptionsTailEnd),
                OptionsTailCopyEntriesUnchanged = RangeUnchanged(defaultOptionsInputBytes, tailOutputBytes, OptionsEntriesStart, OptionsEntriesEnd),
                CopiedInPlacePatchAllowedOnlyInProofRoot = IsWithinDirectory(inPlaceInput, outRoot),
                CopiedInPlaceBackupCreated = backupFiles.Length == 1,
                CopiedInPlaceBackupMatchesPrePatch = inPlaceBefore.SequenceEqual(inPlaceBackup),
                CopiedInPlaceChangedOffsets = inPlaceDiffs.Select(HexOffset).ToArray(),
                CopiedInPlaceUnexpectedDiffCount = inPlaceDiffs.Count(offset => offset < MusicVolumeOffset || offset >= MusicVolumeOffset + 4)
            },
            SlotCodecAlignment = new SlotCodecAlignmentInfo
            {
                Service = "MissionScriptSlotBitsetSaveCodec",
                CodecExpectedSizeMatchesSavePatcher = MissionScriptSlotBitsetSaveCodec.ExpectedFileSize == BesFilePatcher.EXPECTED_FILE_SIZE,
                CodecVersionWordMatchesSavePatcher = MissionScriptSlotBitsetSaveCodec.VersionWord == BesFilePatcher.VERSION_WORD,
                Slot61ToggleRoundTrip = slotCodecToggled,
                Slot61ChangedOffsets = slotCodecDiffs.Select(HexOffset).ToArray(),
                SlotCodecFileIo = false
            },
            CopiedArtifacts =
            [
                FileRow(repoRoot, "career service input", careerInput, careerInputBytes),
                FileRow(repoRoot, "career aircraft kill service output", careerOutput, careerOutputBytes),
                FileRow(repoRoot, "defaultoptions service input", defaultOptionsInput, defaultOptionsInputBytes),
                FileRow(repoRoot, "defaultoptions sound output", soundOutput, soundOutputBytes),
                FileRow(repoRoot, "defaultoptions options entries source", optionsEntriesSource, entriesSourceBytes),
                FileRow(repoRoot, "defaultoptions options entries output", optionsEntriesOutput, entriesOutputBytes),
                FileRow(repoRoot, "defaultoptions options tail source", optionsTailSource, tailSourceBytes),
                FileRow(repoRoot, "defaultoptions options tail output", optionsTailOutput, tailOutputBytes),
                FileRow(repoRoot, "defaultoptions copied in-place patched file", inPlaceInput, inPlaceAfter),
                FileRow(repoRoot, "defaultoptions copied in-place backup", backupFiles[0], inPlaceBackup)
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
                RuntimeSaveLoadProof = false,
                RuntimeDefaultOptionsProof = false
            }
        };

        ValidateEvidence(evidence);
        return evidence;
    }

    private static void ValidateEvidence(Evidence evidence)
    {
        if (evidence.CareerServicePatch.UnexpectedDiffCount != 0 ||
            evidence.CareerServicePatch.LegacyTrapHitCount != 0 ||
            !evidence.CareerServicePatch.MetadataBytePreserved ||
            !evidence.CareerServicePatch.Lower24Changed ||
            !evidence.CareerServicePatch.TechSlotsRangeUnchanged ||
            !evidence.CareerServicePatch.OptionsEntriesUnchanged ||
            !evidence.CareerServicePatch.OptionsTailUnchanged)
        {
            throw new InvalidOperationException("Career service patch preservation contract failed.");
        }

        if (evidence.ConfigurationServicePatch.SoundVolumeUnexpectedDiffCount != 0 ||
            evidence.ConfigurationServicePatch.OptionsEntriesCopyUnexpectedDiffCount != 0 ||
            evidence.ConfigurationServicePatch.OptionsTailCopyUnexpectedDiffCount != 0 ||
            evidence.ConfigurationServicePatch.CopiedInPlaceUnexpectedDiffCount != 0 ||
            !evidence.ConfigurationServicePatch.CopiedInPlaceBackupCreated ||
            !evidence.ConfigurationServicePatch.CopiedInPlaceBackupMatchesPrePatch)
        {
            throw new InvalidOperationException("Configuration service patch preservation contract failed.");
        }

        if (!evidence.SlotCodecAlignment.CodecExpectedSizeMatchesSavePatcher ||
            !evidence.SlotCodecAlignment.CodecVersionWordMatchesSavePatcher ||
            !evidence.SlotCodecAlignment.Slot61ToggleRoundTrip)
        {
            throw new InvalidOperationException("Slot codec alignment contract failed.");
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
        Console.WriteLine("Usage: dotnet run --project tools/SaveOptionsAppCoreContractHarness -- [--repo-root .]");
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
        if (data.Length != BesFilePatcher.EXPECTED_FILE_SIZE)
        {
            throw new InvalidOperationException($"{label}: expected {BesFilePatcher.EXPECTED_FILE_SIZE} bytes, got {data.Length}.");
        }

        ushort version = ReadVersionWord(data);
        if (version != BesFilePatcher.VERSION_WORD)
        {
            throw new InvalidOperationException($"{label}: expected version 0x{BesFilePatcher.VERSION_WORD:X4}, got 0x{version:X4}.");
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
            throw new InvalidOperationException("Cannot compare buffers with different lengths.");
        }

        List<int> diffs = new();
        for (int i = 0; i < before.Length; i++)
        {
            if (before[i] != after[i])
            {
                diffs.Add(i);
            }
        }

        return diffs.ToArray();
    }

    private static bool RangeUnchanged(byte[] before, byte[] after, int start, int endExclusive)
    {
        for (int offset = start; offset < endExclusive; offset++)
        {
            if (before[offset] != after[offset])
            {
                return false;
            }
        }

        return true;
    }

    private static bool IsWithinDirectory(string path, string directory)
    {
        string fullPath = Path.GetFullPath(path).TrimEnd(Path.DirectorySeparatorChar, Path.AltDirectorySeparatorChar);
        string fullDirectory = Path.GetFullPath(directory).TrimEnd(Path.DirectorySeparatorChar, Path.AltDirectorySeparatorChar);
        return fullPath.Equals(fullDirectory, StringComparison.OrdinalIgnoreCase) ||
               fullPath.StartsWith(fullDirectory + Path.DirectorySeparatorChar, StringComparison.OrdinalIgnoreCase) ||
               fullPath.StartsWith(fullDirectory + Path.AltDirectorySeparatorChar, StringComparison.OrdinalIgnoreCase);
    }

    private static bool PathsEqual(string left, string right) =>
        string.Equals(Path.GetFullPath(left), Path.GetFullPath(right), StringComparison.OrdinalIgnoreCase);

    private static ArtifactInfo FileRow(string repoRoot, string label, string path, byte[] data) => new()
    {
        Label = label,
        RelativePath = Path.GetRelativePath(repoRoot, path).Replace('\\', '/'),
        Size = data.Length,
        VersionWord = Hex(ReadVersionWord(data), 4),
        Sha256 = Convert.ToHexString(SHA256.HashData(data)).ToLowerInvariant()
    };

    private static string HexOffset(int value) => Hex(value, 4);

    private static string Hex(long value, int digits) => $"0x{value.ToString($"X{digits}")}";

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
        public SourceInfo Source { get; set; } = new();
        public ImplementationInfo Implementation { get; set; } = new();
        public ProvenanceInfo Provenance { get; set; } = new();
        public ContainerInfo Container { get; set; } = new();
        public CareerServicePatchInfo CareerServicePatch { get; set; } = new();
        public ConfigurationServicePatchInfo ConfigurationServicePatch { get; set; } = new();
        public SlotCodecAlignmentInfo SlotCodecAlignment { get; set; } = new();
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
        public string AppCoreSavePatchPath { get; set; } = "";
        public string SaveEditorServicePath { get; set; } = "";
        public string ConfigurationEditorServicePath { get; set; } = "";
        public string SlotCodecPath { get; set; } = "";
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
        public bool CareerSourceUnchanged { get; set; }
        public bool DefaultOptionsSourceUnchanged { get; set; }
        public int CareerSourceToInputDiffCount { get; set; }
        public int DefaultOptionsSourceToInputDiffCount { get; set; }
    }

    private sealed class ContainerInfo
    {
        public int ExpectedSize { get; set; }
        public int SlotCodecExpectedSize { get; set; }
        public string VersionWord { get; set; } = "";
        public string SlotCodecVersionWord { get; set; } = "";
        public string TrueViewRule { get; set; } = "";
        public string CareerSlotsBase { get; set; } = "";
        public string CareerSlotsEndExclusive { get; set; } = "";
        public bool AllOutputsFileSizePreserved { get; set; }
        public bool AllOutputsVersionWordPreserved { get; set; }
    }

    private sealed class CareerServicePatchInfo
    {
        public string Service { get; set; } = "";
        public bool PatchNodes { get; set; }
        public bool PatchLinks { get; set; }
        public bool PatchGoodies { get; set; }
        public bool PatchKills { get; set; }
        public bool OptionsLikeInputRejected { get; set; }
        public bool InPlaceRejected { get; set; }
        public string[] ChangedOffsets { get; set; } = [];
        public int ChangedOffsetCount { get; set; }
        public string[] AllowedOffsets { get; set; } = [];
        public int UnexpectedDiffCount { get; set; }
        public bool MetadataBytePreserved { get; set; }
        public bool Lower24Changed { get; set; }
        public int LegacyTrapHitCount { get; set; }
        public bool TechSlotsRangeUnchanged { get; set; }
        public bool OptionsEntriesUnchanged { get; set; }
        public bool OptionsTailUnchanged { get; set; }
    }

    private sealed class ConfigurationServicePatchInfo
    {
        public string Service { get; set; } = "";
        public bool OptionsLikePathRequired { get; set; }
        public string[] SoundVolumeChangedOffsets { get; set; } = [];
        public int SoundVolumeUnexpectedDiffCount { get; set; }
        public bool SoundVolumeOptionsEntriesUnchanged { get; set; }
        public bool SoundVolumeOptionsTailUnchanged { get; set; }
        public string[] OptionsEntriesCopyChangedOffsets { get; set; } = [];
        public int OptionsEntriesCopyUnexpectedDiffCount { get; set; }
        public bool OptionsEntriesCopyTailUnchanged { get; set; }
        public string[] OptionsTailCopyChangedOffsets { get; set; } = [];
        public int OptionsTailCopyUnexpectedDiffCount { get; set; }
        public bool OptionsTailCopyEntriesUnchanged { get; set; }
        public bool CopiedInPlacePatchAllowedOnlyInProofRoot { get; set; }
        public bool CopiedInPlaceBackupCreated { get; set; }
        public bool CopiedInPlaceBackupMatchesPrePatch { get; set; }
        public string[] CopiedInPlaceChangedOffsets { get; set; } = [];
        public int CopiedInPlaceUnexpectedDiffCount { get; set; }
    }

    private sealed class SlotCodecAlignmentInfo
    {
        public string Service { get; set; } = "";
        public bool CodecExpectedSizeMatchesSavePatcher { get; set; }
        public bool CodecVersionWordMatchesSavePatcher { get; set; }
        public bool Slot61ToggleRoundTrip { get; set; }
        public string[] Slot61ChangedOffsets { get; set; } = [];
        public bool SlotCodecFileIo { get; set; }
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
        public bool RuntimeSaveLoadProof { get; set; }
        public bool RuntimeDefaultOptionsProof { get; set; }
    }
}
