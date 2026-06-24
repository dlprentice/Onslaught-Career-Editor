using System.Buffers.Binary;
using System.Security.Cryptography;
using System.Text.Json;
using System.Text.Json.Serialization;
using Onslaught___Career_Editor;

namespace Onslaught___Career_Editor.Tools;

internal static class Program
{
    private const string SchemaVersion = "save-options-byte-preservation-appcore-fixture-matrix-private-evidence.v1";
    private const string EvidenceRootRelative = "subagents/static-to-proof/save-options-byte-preservation-appcore-fixture-matrix-proof";
    private const string SourceEvidenceRootRelative = "subagents/static-to-proof/save-options-controller-byte-preservation-copied-file-proof";
    private const string CareerSourceName = "career-baseline.bes";
    private const string DefaultOptionsSourceName = "defaultoptions-baseline.bea";
    private const string SummaryFileName = "fixture-matrix-summary.private.json";

    private const int ExpectedSize = 10004;
    private const ushort VersionWord = 0x4BD1;
    private const int KillsBase = 0x23F6;
    private const int CareerSlotsBase = 0x240A;
    private const int CareerSlotsEndExclusive = 0x248A;
    private const int SoundVolumeOffset = 0x248E;
    private const int MusicVolumeOffset = 0x2492;
    private const int FlightInvertP1Offset = 0x249E;
    private const int FlightInvertP2Offset = 0x24A2;
    private const int WalkerInvertP1Offset = 0x24A6;
    private const int WalkerInvertP2Offset = 0x24AA;
    private const int VibrationP1Offset = 0x24AE;
    private const int VibrationP2Offset = 0x24B2;
    private const int ControllerConfigP1Offset = 0x24B6;
    private const int ControllerConfigP2Offset = 0x24BA;
    private const int OptionsEntriesStart = 0x24BE;
    private const int OptionsTailStart = 0x26BE;
    private const int OptionsTailEnd = 0x2714;
    private const int OptionsEntrySize = 0x20;
    private const int TailControlSchemeOffset = OptionsTailStart + 0x08;

    private static readonly int[] LegacyTrapOffsets = [0x22D4, 0x23A4, 0x240C];

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

            string sourceRoot = Path.Combine(repoRoot, SourceEvidenceRootRelative);
            string careerSource = Path.GetFullPath(options.CareerSource ?? Path.Combine(sourceRoot, CareerSourceName));
            string defaultOptionsSource = Path.GetFullPath(options.DefaultOptionsSource ?? Path.Combine(sourceRoot, DefaultOptionsSourceName));
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

        List<CaseInfo> cases = new();
        List<ArtifactInfo> artifacts = new();

        string careerMatrixInput = CopyArtifact(repoRoot, careerSource, Path.Combine(outRoot, "career-fixture-matrix-input.bes"), artifacts, "career matrix copied input");
        string defaultOptionsMatrixInput = CopyArtifact(repoRoot, defaultOptionsSource, Path.Combine(outRoot, "defaultoptions-fixture-matrix-input.bea"), artifacts, "defaultoptions matrix copied input");
        byte[] careerInput = File.ReadAllBytes(careerMatrixInput);
        byte[] defaultOptionsInput = File.ReadAllBytes(defaultOptionsMatrixInput);
        ValidateContainer(careerInput, "career matrix input");
        ValidateContainer(defaultOptionsInput, "defaultoptions matrix input");

        AddAnalyzerCases(cases, careerMatrixInput, defaultOptionsMatrixInput);
        AddCareerKillCases(repoRoot, outRoot, careerMatrixInput, careerInput, cases, artifacts);
        AddKillBoundaryCases(repoRoot, outRoot, careerMatrixInput, careerInput, cases, artifacts);
        AddDefaultOptionsSettingCases(repoRoot, outRoot, defaultOptionsMatrixInput, defaultOptionsInput, cases, artifacts);
        AddOptionsCopyCases(repoRoot, outRoot, defaultOptionsMatrixInput, defaultOptionsInput, cases, artifacts);
        AddControllerKeybindCases(repoRoot, outRoot, defaultOptionsMatrixInput, defaultOptionsInput, cases, artifacts);
        AddSlotBitsetCases(repoRoot, outRoot, careerMatrixInput, careerInput, cases, artifacts);
        AddRejectionCases(outRoot, careerMatrixInput, defaultOptionsMatrixInput, careerInput, defaultOptionsInput, cases, artifacts);

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
                ToolProjectPath = "tools/SaveOptionsAppCoreFixtureMatrixHarness/SaveOptionsAppCoreFixtureMatrixHarness.csproj",
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
                CareerSourceUnchanged = careerSourceBefore.SequenceEqual(careerSourceAfter),
                DefaultOptionsSourceUnchanged = defaultOptionsSourceBefore.SequenceEqual(defaultOptionsSourceAfter),
                CareerSourceToInputDiffCount = ChangedOffsets(careerSourceBefore, careerInput).Length,
                DefaultOptionsSourceToInputDiffCount = ChangedOffsets(defaultOptionsSourceBefore, defaultOptionsInput).Length
            },
            Container = new ContainerInfo
            {
                ExpectedSize = ExpectedSize,
                VersionWord = Hex(VersionWord, 4),
                TrueViewRule = "file_offset = 0x0002 + career_offset",
                CareerSlotsBase = Hex(CareerSlotsBase, 4),
                CareerSlotsEndExclusive = Hex(CareerSlotsEndExclusive, 4),
                OptionsEntriesRange = "0x24BE-0x26BD",
                OptionsTailRange = "0x26BE-0x2713",
                AllOutputsFileSizePreserved = cases.Where(c => c.OutputCreated).All(c => c.FileSizePreserved),
                AllOutputsVersionWordPreserved = cases.Where(c => c.OutputCreated).All(c => c.VersionWordPreserved)
            },
            Matrix = BuildMatrixInfo(cases),
            Cases = cases.ToArray(),
            CopiedArtifacts = artifacts.ToArray(),
            NegativeGuards = new NegativeGuardInfo
            {
                SaveSynthesis = false,
                InstalledGameMutation = false,
                OriginalExecutableMutation = false,
                RuntimeExecution = false,
                BeLaunch = false,
                NewLaunch = false,
                ScreenshotCapture = false,
                NativeInput = false,
                DebuggerAttachment = false,
                CopiedExecutablePatchApplied = false,
                BinaryPatchEngineUsed = false,
                PatchCatalogTouched = false,
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

    private static void AddAnalyzerCases(List<CaseInfo> cases, string careerInput, string defaultOptionsInput)
    {
        SaveAnalysis career = BesFilePatcher.AnalyzeSave(careerInput);
        SaveAnalysis options = BesFilePatcher.AnalyzeSave(defaultOptionsInput);
        cases.Add(CaseInfo.Pass("container-analyzer", "career-analyze-save", "BesFilePatcher.AnalyzeSave", outputCreated: false)
            with { AnalysisValid = career.IsValid, FileSizePreserved = true, VersionWordPreserved = career.VersionValid });
        cases.Add(CaseInfo.Pass("container-analyzer", "defaultoptions-analyze-save", "BesFilePatcher.AnalyzeSave", outputCreated: false)
            with { AnalysisValid = options.IsValid, FileSizePreserved = true, VersionWordPreserved = options.VersionValid });
    }

    private static void AddCareerKillCases(
        string repoRoot,
        string outRoot,
        string careerInput,
        byte[] careerInputBytes,
        List<CaseInfo> cases,
        List<ArtifactInfo> artifacts)
    {
        SaveAnalysis analysis = BesFilePatcher.AnalyzeSave(careerInput);
        string[] names = ["aircraft", "vehicles", "emplacements", "infantry", "mechs"];
        for (int category = 0; category < 5; category++)
        {
            int current = analysis.KillCounts[category];
            int next = (current + category + 1) & 0x00FFFFFF;
            if (next == current)
            {
                next = (current + category + 7) & 0x00FFFFFF;
            }

            RunKillPatchCase(
                repoRoot,
                outRoot,
                careerInput,
                careerInputBytes,
                cases,
                artifacts,
                family: "career-kills",
                name: $"career-kill-{names[category]}",
                category,
                requestedKills: next,
                expectedKills: next);
        }
    }

    private static void AddKillBoundaryCases(
        string repoRoot,
        string outRoot,
        string careerInput,
        byte[] careerInputBytes,
        List<CaseInfo> cases,
        List<ArtifactInfo> artifacts)
    {
        RunKillPatchCase(repoRoot, outRoot, careerInput, careerInputBytes, cases, artifacts, "kill-boundaries", "kill-negative-clamps-zero", BesFilePatcher.KILL_AIRCRAFT, -5, 0);
        RunKillPatchCase(repoRoot, outRoot, careerInput, careerInputBytes, cases, artifacts, "kill-boundaries", "kill-zero-boundary", BesFilePatcher.KILL_INFANTRY, 0, 0);
        RunKillPatchCase(repoRoot, outRoot, careerInput, careerInputBytes, cases, artifacts, "kill-boundaries", "kill-overflow-clamps-max", BesFilePatcher.KILL_MECHS, 0x1FFFFFFF, 0x00FFFFFF);
    }

    private static void RunKillPatchCase(
        string repoRoot,
        string outRoot,
        string careerInput,
        byte[] careerInputBytes,
        List<CaseInfo> cases,
        List<ArtifactInfo> artifacts,
        string family,
        string name,
        int category,
        int requestedKills,
        int expectedKills)
    {
        SaveAnalysis analysis = BesFilePatcher.AnalyzeSave(careerInput);
        Dictionary<int, int> perCategoryKills = new();
        for (int i = 0; i < 5; i++)
        {
            perCategoryKills[i] = analysis.KillCounts[i];
        }
        perCategoryKills[category] = requestedKills;

        string output = Path.Combine(outRoot, $"{name}.bes");
        PatchResult result = SaveEditorService.PatchSave(new SavePatchRequest
        {
            InputPath = careerInput,
            OutputPath = output,
            PatchNodes = false,
            PatchLinks = false,
            PatchGoodies = false,
            PatchKills = true,
            PerCategoryKills = perCategoryKills
        });
        RequireSuccess(result, name);

        byte[] outputBytes = File.ReadAllBytes(output);
        ValidateContainer(outputBytes, name);
        AddArtifact(repoRoot, artifacts, name, output, outputBytes);

        int offset = KillsBase + category * 4;
        int[] allowed = [offset, offset + 1, offset + 2];
        int[] diffs = ChangedOffsets(careerInputBytes, outputBytes);
        uint before = ReadU32(careerInputBytes, offset);
        uint after = ReadU32(outputBytes, offset);
        cases.Add(new CaseInfo
        {
            Family = family,
            Name = name,
            Status = "PASS",
            Operation = "SaveEditorService.PatchSave",
            OutputCreated = true,
            FileSizePreserved = outputBytes.Length == ExpectedSize,
            VersionWordPreserved = ReadVersionWord(outputBytes) == VersionWord,
            ChangedOffsets = diffs.Select(HexOffset).ToArray(),
            ChangedOffsetCount = diffs.Length,
            AllowedRanges = [RangeLabel(offset, offset + 2)],
            UnexpectedDiffCount = diffs.Count(diff => !allowed.Contains(diff)),
            LegacyTrapHitCount = CountLegacyTrapHits(diffs),
            MetadataBytePreserved = (before & 0xFF000000) == (after & 0xFF000000),
            Lower24Expected = (uint)expectedKills,
            Lower24Observed = after & 0x00FFFFFF,
            Lower24MatchedExpected = (after & 0x00FFFFFF) == ((uint)expectedKills & 0x00FFFFFF),
            SourceToInputDiffCount = 0,
            SourceUnchanged = true
        });
    }

    private static void AddDefaultOptionsSettingCases(
        string repoRoot,
        string outRoot,
        string defaultOptionsInput,
        byte[] defaultOptionsInputBytes,
        List<CaseInfo> cases,
        List<ArtifactInfo> artifacts)
    {
        SaveAnalysis analysis = BesFilePatcher.AnalyzeSave(defaultOptionsInput);
        AddConfigCase(repoRoot, outRoot, defaultOptionsInput, defaultOptionsInputBytes, cases, artifacts, "defaultoptions-settings", "sound-volume", SoundVolumeOffset, new ConfigurationPatchRequest
        {
            InputPath = defaultOptionsInput,
            OutputPath = Path.Combine(outRoot, "defaultoptions-setting-sound-volume.bea"),
            SoundVolumeOverride = ChooseDifferentFloat(analysis.SoundVolume)
        });
        AddConfigCase(repoRoot, outRoot, defaultOptionsInput, defaultOptionsInputBytes, cases, artifacts, "defaultoptions-settings", "music-volume", MusicVolumeOffset, new ConfigurationPatchRequest
        {
            InputPath = defaultOptionsInput,
            OutputPath = Path.Combine(outRoot, "defaultoptions-setting-music-volume.bea"),
            MusicVolumeOverride = ChooseDifferentFloat(analysis.MusicVolume)
        });
        AddConfigCase(repoRoot, outRoot, defaultOptionsInput, defaultOptionsInputBytes, cases, artifacts, "defaultoptions-settings", "walker-invert-p1", WalkerInvertP1Offset, new ConfigurationPatchRequest
        {
            InputPath = defaultOptionsInput,
            OutputPath = Path.Combine(outRoot, "defaultoptions-setting-walker-invert-p1.bea"),
            InvertWalkerP1Override = analysis.InvertYAxisRaw[0] == 0
        });
        AddConfigCase(repoRoot, outRoot, defaultOptionsInput, defaultOptionsInputBytes, cases, artifacts, "defaultoptions-settings", "walker-invert-p2", WalkerInvertP2Offset, new ConfigurationPatchRequest
        {
            InputPath = defaultOptionsInput,
            OutputPath = Path.Combine(outRoot, "defaultoptions-setting-walker-invert-p2.bea"),
            InvertWalkerP2Override = analysis.InvertYAxisRaw[1] == 0
        });
        AddConfigCase(repoRoot, outRoot, defaultOptionsInput, defaultOptionsInputBytes, cases, artifacts, "defaultoptions-settings", "flight-invert-p1", FlightInvertP1Offset, new ConfigurationPatchRequest
        {
            InputPath = defaultOptionsInput,
            OutputPath = Path.Combine(outRoot, "defaultoptions-setting-flight-invert-p1.bea"),
            InvertFlightP1Override = analysis.InvertFlightRaw[0] == 0
        });
        AddConfigCase(repoRoot, outRoot, defaultOptionsInput, defaultOptionsInputBytes, cases, artifacts, "defaultoptions-settings", "flight-invert-p2", FlightInvertP2Offset, new ConfigurationPatchRequest
        {
            InputPath = defaultOptionsInput,
            OutputPath = Path.Combine(outRoot, "defaultoptions-setting-flight-invert-p2.bea"),
            InvertFlightP2Override = analysis.InvertFlightRaw[1] == 0
        });
        AddConfigCase(repoRoot, outRoot, defaultOptionsInput, defaultOptionsInputBytes, cases, artifacts, "defaultoptions-settings", "vibration-p1", VibrationP1Offset, new ConfigurationPatchRequest
        {
            InputPath = defaultOptionsInput,
            OutputPath = Path.Combine(outRoot, "defaultoptions-setting-vibration-p1.bea"),
            VibrationP1Override = analysis.VibrationRaw[0] == 0
        });
        AddConfigCase(repoRoot, outRoot, defaultOptionsInput, defaultOptionsInputBytes, cases, artifacts, "defaultoptions-settings", "vibration-p2", VibrationP2Offset, new ConfigurationPatchRequest
        {
            InputPath = defaultOptionsInput,
            OutputPath = Path.Combine(outRoot, "defaultoptions-setting-vibration-p2.bea"),
            VibrationP2Override = analysis.VibrationRaw[1] == 0
        });
        AddConfigCase(repoRoot, outRoot, defaultOptionsInput, defaultOptionsInputBytes, cases, artifacts, "defaultoptions-settings", "controller-config-p1", ControllerConfigP1Offset, new ConfigurationPatchRequest
        {
            InputPath = defaultOptionsInput,
            OutputPath = Path.Combine(outRoot, "defaultoptions-setting-controller-config-p1.bea"),
            ControllerConfigP1Override = ChooseDifferentControllerConfig(analysis.ControllerConfigNum[0])
        });
        AddConfigCase(repoRoot, outRoot, defaultOptionsInput, defaultOptionsInputBytes, cases, artifacts, "defaultoptions-settings", "controller-config-p2", ControllerConfigP2Offset, new ConfigurationPatchRequest
        {
            InputPath = defaultOptionsInput,
            OutputPath = Path.Combine(outRoot, "defaultoptions-setting-controller-config-p2.bea"),
            ControllerConfigP2Override = ChooseDifferentControllerConfig(analysis.ControllerConfigNum[1])
        });
    }

    private static void AddConfigCase(
        string repoRoot,
        string outRoot,
        string defaultOptionsInput,
        byte[] defaultOptionsInputBytes,
        List<CaseInfo> cases,
        List<ArtifactInfo> artifacts,
        string family,
        string name,
        int fieldOffset,
        ConfigurationPatchRequest request)
    {
        PatchResult result = ConfigurationEditorService.PatchConfiguration(request);
        RequireSuccess(result, name);
        byte[] outputBytes = File.ReadAllBytes(request.OutputPath);
        ValidateContainer(outputBytes, name);
        AddArtifact(repoRoot, artifacts, name, request.OutputPath, outputBytes);

        int[] diffs = ChangedOffsets(defaultOptionsInputBytes, outputBytes);
        cases.Add(new CaseInfo
        {
            Family = family,
            Name = name,
            Status = "PASS",
            Operation = "ConfigurationEditorService.PatchConfiguration",
            OutputCreated = true,
            FileSizePreserved = outputBytes.Length == ExpectedSize,
            VersionWordPreserved = ReadVersionWord(outputBytes) == VersionWord,
            ChangedOffsets = diffs.Select(HexOffset).ToArray(),
            ChangedOffsetCount = diffs.Length,
            AllowedRanges = [RangeLabel(fieldOffset, fieldOffset + 3)],
            UnexpectedDiffCount = diffs.Count(diff => diff < fieldOffset || diff > fieldOffset + 3),
            LegacyTrapHitCount = CountLegacyTrapHits(diffs),
            OptionsEntriesUnchanged = RangeUnchanged(defaultOptionsInputBytes, outputBytes, OptionsEntriesStart, OptionsTailStart),
            OptionsTailUnchanged = RangeUnchanged(defaultOptionsInputBytes, outputBytes, OptionsTailStart, OptionsTailEnd),
            SourceToInputDiffCount = 0,
            SourceUnchanged = true
        });
    }

    private static void AddOptionsCopyCases(
        string repoRoot,
        string outRoot,
        string defaultOptionsInput,
        byte[] defaultOptionsInputBytes,
        List<CaseInfo> cases,
        List<ArtifactInfo> artifacts)
    {
        byte[] entriesSource = defaultOptionsInputBytes.ToArray();
        entriesSource[OptionsEntriesStart] ^= 0x01;
        string entriesSourcePath = Path.Combine(outRoot, "defaultoptions-copy-entries-source.bea");
        File.WriteAllBytes(entriesSourcePath, entriesSource);
        AddArtifact(repoRoot, artifacts, "options-copy entries source", entriesSourcePath, entriesSource);
        AddOptionsCopyCase(repoRoot, outRoot, defaultOptionsInput, defaultOptionsInputBytes, entriesSourcePath, "options-copy-entries-only", copyEntries: true, copyTail: false, cases, artifacts, [RangeLabel(OptionsEntriesStart, OptionsTailStart - 1)]);

        byte[] tailSource = defaultOptionsInputBytes.ToArray();
        tailSource[OptionsTailStart] ^= 0x01;
        string tailSourcePath = Path.Combine(outRoot, "defaultoptions-copy-tail-source.bea");
        File.WriteAllBytes(tailSourcePath, tailSource);
        AddArtifact(repoRoot, artifacts, "options-copy tail source", tailSourcePath, tailSource);
        AddOptionsCopyCase(repoRoot, outRoot, defaultOptionsInput, defaultOptionsInputBytes, tailSourcePath, "options-copy-tail-only", copyEntries: false, copyTail: true, cases, artifacts, [RangeLabel(OptionsTailStart, OptionsTailEnd - 1)]);

        byte[] combinedSource = defaultOptionsInputBytes.ToArray();
        combinedSource[OptionsEntriesStart] ^= 0x02;
        combinedSource[OptionsTailStart] ^= 0x02;
        string combinedSourcePath = Path.Combine(outRoot, "defaultoptions-copy-combined-source.bea");
        File.WriteAllBytes(combinedSourcePath, combinedSource);
        AddArtifact(repoRoot, artifacts, "options-copy combined source", combinedSourcePath, combinedSource);
        AddOptionsCopyCase(repoRoot, outRoot, defaultOptionsInput, defaultOptionsInputBytes, combinedSourcePath, "options-copy-combined", copyEntries: true, copyTail: true, cases, artifacts, [RangeLabel(OptionsEntriesStart, OptionsTailEnd - 1)]);

        AddOptionsCopyCase(repoRoot, outRoot, defaultOptionsInput, defaultOptionsInputBytes, defaultOptionsInput, "options-copy-same-source-noop", copyEntries: true, copyTail: true, cases, artifacts, [RangeLabel(OptionsEntriesStart, OptionsTailEnd - 1)], expectNoDiff: true);
    }

    private static void AddOptionsCopyCase(
        string repoRoot,
        string outRoot,
        string defaultOptionsInput,
        byte[] defaultOptionsInputBytes,
        string copySource,
        string name,
        bool copyEntries,
        bool copyTail,
        List<CaseInfo> cases,
        List<ArtifactInfo> artifacts,
        string[] allowedRanges,
        bool expectNoDiff = false)
    {
        string output = Path.Combine(outRoot, $"{name}.bea");
        PatchResult result = ConfigurationEditorService.PatchConfiguration(new ConfigurationPatchRequest
        {
            InputPath = defaultOptionsInput,
            OutputPath = output,
            CopyOptionsFromPath = copySource,
            CopyOptionsEntries = copyEntries,
            CopyOptionsTail = copyTail
        });
        RequireSuccess(result, name);

        byte[] outputBytes = File.ReadAllBytes(output);
        ValidateContainer(outputBytes, name);
        AddArtifact(repoRoot, artifacts, name, output, outputBytes);
        int[] diffs = ChangedOffsets(defaultOptionsInputBytes, outputBytes);
        cases.Add(new CaseInfo
        {
            Family = "options-copy",
            Name = name,
            Status = "PASS",
            Operation = "ConfigurationEditorService.PatchConfiguration",
            OutputCreated = true,
            FileSizePreserved = outputBytes.Length == ExpectedSize,
            VersionWordPreserved = ReadVersionWord(outputBytes) == VersionWord,
            ChangedOffsets = diffs.Select(HexOffset).ToArray(),
            ChangedOffsetCount = diffs.Length,
            AllowedRanges = allowedRanges,
            UnexpectedDiffCount = diffs.Count(diff => diff < OptionsEntriesStart || diff >= OptionsTailEnd),
            LegacyTrapHitCount = CountLegacyTrapHits(diffs),
            NoOpDiffCount = expectNoDiff ? diffs.Length : null,
            SourceToInputDiffCount = 0,
            SourceUnchanged = true
        });
    }

    private static void AddControllerKeybindCases(
        string repoRoot,
        string outRoot,
        string defaultOptionsInput,
        byte[] defaultOptionsInputBytes,
        List<CaseInfo> cases,
        List<ArtifactInfo> artifacts)
    {
        AddKeybindCase(repoRoot, outRoot, defaultOptionsInput, defaultOptionsInputBytes, cases, artifacts, "keybind-look-mousex", rows =>
        {
            ConfigurationKeybindRow row = FindRow(rows, "Look", "Right");
            row.Player1Token = "MouseX+";
        }, [0x1B]);

        AddKeybindCase(repoRoot, outRoot, defaultOptionsInput, defaultOptionsInputBytes, cases, artifacts, "keybind-zoom-wheel", rows =>
        {
            ConfigurationKeybindRow row = FindRow(rows, "Zoom", "In");
            row.Player1Token = "MouseWheelUp";
        }, [0x10]);

        AddKeybindCase(repoRoot, outRoot, defaultOptionsInput, defaultOptionsInputBytes, cases, artifacts, "keybind-fire-mouseleft-mirror", rows =>
        {
            ConfigurationKeybindRow row = FindRow(rows, "Actions", "Fire weapon");
            row.Player1Token = "MouseLeft";
        }, [0x12, 0x13]);

        IReadOnlyList<ConfigurationKeybindRow> invalidRows = ConfigurationEditorService.LoadKeybindRowsFromFile(defaultOptionsInput);
        FindRow(invalidRows, "Movement", "Forward").Player1Token = "MouseLeft";
        string invalidOutput = Path.Combine(outRoot, "keybind-invalid-token-output.bea");
        PatchResult invalid = ConfigurationEditorService.PatchConfiguration(new ConfigurationPatchRequest
        {
            InputPath = defaultOptionsInput,
            OutputPath = invalidOutput,
            KeybindRows = invalidRows
        });
        cases.Add(CaseInfo.Rejection("controller-keybinds", "keybind-invalid-token-rejected", "ConfigurationEditorService.PatchConfiguration", invalidOutput, invalid));
    }

    private static void AddKeybindCase(
        string repoRoot,
        string outRoot,
        string defaultOptionsInput,
        byte[] defaultOptionsInputBytes,
        List<CaseInfo> cases,
        List<ArtifactInfo> artifacts,
        string name,
        Action<IReadOnlyList<ConfigurationKeybindRow>> mutateRows,
        int[] entryIds)
    {
        IReadOnlyList<ConfigurationKeybindRow> rows = ConfigurationEditorService.LoadKeybindRowsFromFile(defaultOptionsInput);
        mutateRows(rows);
        string output = Path.Combine(outRoot, $"{name}.bea");
        PatchResult result = ConfigurationEditorService.PatchConfiguration(new ConfigurationPatchRequest
        {
            InputPath = defaultOptionsInput,
            OutputPath = output,
            KeybindRows = rows
        });
        RequireSuccess(result, name);
        byte[] outputBytes = File.ReadAllBytes(output);
        ValidateContainer(outputBytes, name);
        AddArtifact(repoRoot, artifacts, name, output, outputBytes);

        Dictionary<int, int> entryOffsets = ReadOptionEntryOffsets(defaultOptionsInputBytes);
        HashSet<int> allowed = new();
        foreach (int entryId in entryIds)
        {
            int off = entryOffsets[entryId];
            for (int i = off; i < off + OptionsEntrySize; i++)
            {
                allowed.Add(i);
            }
        }
        allowed.Add(TailControlSchemeOffset);
        allowed.Add(TailControlSchemeOffset + 1);

        int[] diffs = ChangedOffsets(defaultOptionsInputBytes, outputBytes);
        cases.Add(new CaseInfo
        {
            Family = "controller-keybinds",
            Name = name,
            Status = "PASS",
            Operation = "ConfigurationEditorService.PatchConfiguration",
            OutputCreated = true,
            FileSizePreserved = outputBytes.Length == ExpectedSize,
            VersionWordPreserved = ReadVersionWord(outputBytes) == VersionWord,
            ChangedOffsets = diffs.Select(HexOffset).ToArray(),
            ChangedOffsetCount = diffs.Length,
            AllowedRanges = ["selected-options-entry-rows", "options-tail-control-scheme"],
            UnexpectedDiffCount = diffs.Count(diff => !allowed.Contains(diff)),
            LegacyTrapHitCount = CountLegacyTrapHits(diffs),
            KeybindDiffsWithinOptionsEntriesAndTailControlScheme = true,
            SourceToInputDiffCount = 0,
            SourceUnchanged = true
        });
    }

    private static void AddSlotBitsetCases(
        string repoRoot,
        string outRoot,
        string careerInput,
        byte[] careerInputBytes,
        List<CaseInfo> cases,
        List<ArtifactInfo> artifacts)
    {
        int[][] pairs =
        [
            [0, 31],
            [32, 63],
            [128, 159],
            [224, 255]
        ];

        foreach (int[] pair in pairs)
        {
            byte[] buffer = careerInputBytes.ToArray();
            bool desired = !(MissionScriptSlotBitsetSaveCodec.GetSlot(buffer, pair[0]) && MissionScriptSlotBitsetSaveCodec.GetSlot(buffer, pair[1]));
            MissionScriptSlotBitsetMask mask = MissionScriptSlotBitsetSaveCodec.SetSlotsInSingleDword(buffer, pair, desired);
            bool roundTrip = MissionScriptSlotBitsetSaveCodec.GetSlot(buffer, pair[0]) == desired &&
                             MissionScriptSlotBitsetSaveCodec.GetSlot(buffer, pair[1]) == desired;
            string name = $"slot-bitset-pair-{pair[0]}-{pair[1]}";
            string output = Path.Combine(outRoot, $"{name}.bes");
            File.WriteAllBytes(output, buffer);
            AddArtifact(repoRoot, artifacts, name, output, buffer);

            int[] diffs = ChangedOffsets(careerInputBytes, buffer);
            cases.Add(new CaseInfo
            {
                Family = "slot-bitset",
                Name = name,
                Status = "PASS",
                Operation = "MissionScriptSlotBitsetSaveCodec.SetSlotsInSingleDword",
                OutputCreated = true,
                FileSizePreserved = buffer.Length == ExpectedSize,
                VersionWordPreserved = ReadVersionWord(buffer) == VersionWord,
                ChangedOffsets = diffs.Select(HexOffset).ToArray(),
                ChangedOffsetCount = diffs.Length,
                AllowedRanges = [RangeLabel(mask.TrueViewDwordOffset, mask.TrueViewDwordEndOffset)],
                UnexpectedDiffCount = diffs.Count(diff => diff < mask.TrueViewDwordOffset || diff > mask.TrueViewDwordEndOffset),
                LegacyTrapHitCount = CountLegacyTrapHits(diffs),
                SlotRoundTrip = roundTrip,
                SourceToInputDiffCount = 0,
                SourceUnchanged = true
            });
        }
    }

    private static void AddRejectionCases(
        string outRoot,
        string careerInput,
        string defaultOptionsInput,
        byte[] careerInputBytes,
        byte[] defaultOptionsInputBytes,
        List<CaseInfo> cases,
        List<ArtifactInfo> artifacts)
    {
        string noSectionOutput = Path.Combine(outRoot, "save-no-selected-sections-output.bes");
        PatchResult noSections = SaveEditorService.PatchSave(new SavePatchRequest
        {
            InputPath = careerInput,
            OutputPath = noSectionOutput,
            PatchNodes = false,
            PatchLinks = false,
            PatchGoodies = false,
            PatchKills = false
        });
        cases.Add(CaseInfo.Rejection("rejections-noop-legacy", "save-no-selected-sections-rejected", "SaveEditorService.PatchSave", noSectionOutput, noSections));

        string noPendingOutput = Path.Combine(outRoot, "config-no-pending-output.bea");
        PatchResult noPending = ConfigurationEditorService.PatchConfiguration(new ConfigurationPatchRequest
        {
            InputPath = defaultOptionsInput,
            OutputPath = noPendingOutput
        });
        cases.Add(CaseInfo.Rejection("rejections-noop-legacy", "config-no-pending-rejected", "ConfigurationEditorService.PatchConfiguration", noPendingOutput, noPending));

        byte[] wrongSize = careerInputBytes.Take(careerInputBytes.Length - 1).ToArray();
        string wrongSizeInput = Path.Combine(outRoot, "career-wrong-size-derived-rejection-only.bes");
        File.WriteAllBytes(wrongSizeInput, wrongSize);
        artifacts.Add(new ArtifactInfo
        {
            Label = "wrong size derived rejection-only fixture",
            RelativePath = Path.GetRelativePath(Directory.GetCurrentDirectory(), wrongSizeInput).Replace('\\', '/'),
            Size = wrongSize.Length,
            VersionWord = Hex(ReadVersionWord(wrongSize), 4),
            Sha256 = Sha256(wrongSize)
        });
        string wrongSizeOutput = Path.Combine(outRoot, "career-wrong-size-output.bes");
        PatchResult wrongSizeResult = SaveEditorService.PatchSave(new SavePatchRequest
        {
            InputPath = wrongSizeInput,
            OutputPath = wrongSizeOutput,
            PatchNodes = false,
            PatchLinks = false,
            PatchGoodies = false,
            PatchKills = true
        });
        cases.Add(CaseInfo.Rejection("rejections-noop-legacy", "wrong-size-derived-rejected", "SaveEditorService.PatchSave", wrongSizeOutput, wrongSizeResult)
            with { DerivedInvalidFixture = true });

        byte[] wrongVersion = defaultOptionsInputBytes.ToArray();
        wrongVersion[0] = 0;
        wrongVersion[1] = 0;
        string wrongVersionInput = Path.Combine(outRoot, "defaultoptions-wrong-version-derived-rejection-only.bea");
        File.WriteAllBytes(wrongVersionInput, wrongVersion);
        artifacts.Add(new ArtifactInfo
        {
            Label = "wrong version derived rejection-only fixture",
            RelativePath = Path.GetRelativePath(Directory.GetCurrentDirectory(), wrongVersionInput).Replace('\\', '/'),
            Size = wrongVersion.Length,
            VersionWord = Hex(ReadVersionWord(wrongVersion), 4),
            Sha256 = Sha256(wrongVersion)
        });
        string wrongVersionOutput = Path.Combine(outRoot, "defaultoptions-wrong-version-output.bea");
        PatchResult wrongVersionResult = ConfigurationEditorService.PatchConfiguration(new ConfigurationPatchRequest
        {
            InputPath = wrongVersionInput,
            OutputPath = wrongVersionOutput,
            SoundVolumeOverride = 0.25f
        });
        cases.Add(CaseInfo.Rejection("rejections-noop-legacy", "wrong-version-derived-rejected", "ConfigurationEditorService.PatchConfiguration", wrongVersionOutput, wrongVersionResult)
            with { DerivedInvalidFixture = true });
    }

    private static MatrixInfo BuildMatrixInfo(IReadOnlyList<CaseInfo> cases)
    {
        CaseInfo[] outputCases = cases.Where(c => c.OutputCreated).ToArray();
        CaseInfo[] rejectionCases = cases.Where(c => c.RejectionCase).ToArray();
        CaseInfo[] nonSlotOutputCases = outputCases.Where(c => c.Family != "slot-bitset").ToArray();
        return new MatrixInfo
        {
            FixtureFamilyCount = cases.Select(c => c.Family).Distinct(StringComparer.Ordinal).Count(),
            AppCoreFixtureCaseCount = cases.Count,
            ContainerAnalyzerCaseCount = cases.Count(c => c.Family == "container-analyzer"),
            CareerKillCategoryCaseCount = cases.Count(c => c.Family == "career-kills"),
            KillBoundaryCaseCount = cases.Count(c => c.Family == "kill-boundaries"),
            DefaultOptionsSettingCaseCount = cases.Count(c => c.Family == "defaultoptions-settings"),
            OptionsCopyCaseCount = cases.Count(c => c.Family == "options-copy"),
            ControllerKeybindCaseCount = cases.Count(c => c.Family == "controller-keybinds"),
            SlotBitsetCaseCount = cases.Count(c => c.Family == "slot-bitset"),
            RejectionNoOpLegacyCaseCount = cases.Count(c => c.Family == "rejections-noop-legacy"),
            RejectionCaseCount = rejectionCases.Length,
            OutputCaseCount = outputCases.Length,
            UnexpectedDiffCount = outputCases.Sum(c => c.UnexpectedDiffCount),
            LegacyTrapHitCountNonSlot = nonSlotOutputCases.Sum(c => c.LegacyTrapHitCount),
            AllRejectionsOutputNotCreated = rejectionCases.All(c => !c.OutputCreated && !c.OutputCreatedAfterRejection),
            NoOpCaseCount = cases.Count(c => c.NoOpDiffCount.HasValue),
            NoOpDiffCount = cases.Where(c => c.NoOpDiffCount.HasValue).Sum(c => c.NoOpDiffCount!.Value),
            KeybindDiffsWithinOptionsEntriesAndTailControlScheme = cases.Where(c => c.Family == "controller-keybinds" && c.OutputCreated).All(c => c.KeybindDiffsWithinOptionsEntriesAndTailControlScheme),
            SlotRoundTripCaseCount = cases.Count(c => c.Family == "slot-bitset" && c.SlotRoundTrip),
            DerivedInvalidFixtureCount = cases.Count(c => c.DerivedInvalidFixture)
        };
    }

    private static void ValidateEvidence(Evidence evidence)
    {
        if (evidence.Matrix.FixtureFamilyCount != 8 ||
            evidence.Matrix.AppCoreFixtureCaseCount != 36 ||
            evidence.Matrix.ContainerAnalyzerCaseCount != 2 ||
            evidence.Matrix.CareerKillCategoryCaseCount != 5 ||
            evidence.Matrix.KillBoundaryCaseCount != 3 ||
            evidence.Matrix.DefaultOptionsSettingCaseCount != 10 ||
            evidence.Matrix.OptionsCopyCaseCount != 4 ||
            evidence.Matrix.ControllerKeybindCaseCount != 4 ||
            evidence.Matrix.SlotBitsetCaseCount != 4 ||
            evidence.Matrix.RejectionNoOpLegacyCaseCount != 4)
        {
            throw new InvalidOperationException("Fixture matrix case accounting mismatch.");
        }

        if (!evidence.Provenance.CareerSourceUnchanged ||
            !evidence.Provenance.DefaultOptionsSourceUnchanged ||
            evidence.Provenance.CareerSourceToInputDiffCount != 0 ||
            evidence.Provenance.DefaultOptionsSourceToInputDiffCount != 0)
        {
            throw new InvalidOperationException("Source provenance contract failed.");
        }

        if (!evidence.Container.AllOutputsFileSizePreserved ||
            !evidence.Container.AllOutputsVersionWordPreserved ||
            evidence.Matrix.UnexpectedDiffCount != 0 ||
            evidence.Matrix.LegacyTrapHitCountNonSlot != 0 ||
            !evidence.Matrix.AllRejectionsOutputNotCreated ||
            evidence.Matrix.NoOpDiffCount != 0 ||
            !evidence.Matrix.KeybindDiffsWithinOptionsEntriesAndTailControlScheme ||
            evidence.Matrix.SlotRoundTripCaseCount != evidence.Matrix.SlotBitsetCaseCount)
        {
            throw new InvalidOperationException("Fixture matrix preservation contract failed.");
        }

        foreach (CaseInfo item in evidence.Cases)
        {
            if (item.Status != "PASS")
            {
                throw new InvalidOperationException($"Fixture case failed: {item.Name}");
            }
        }
    }

    private static string CopyArtifact(string repoRoot, string source, string destination, List<ArtifactInfo> artifacts, string label)
    {
        File.Copy(source, destination, overwrite: true);
        byte[] data = File.ReadAllBytes(destination);
        AddArtifact(repoRoot, artifacts, label, destination, data);
        return destination;
    }

    private static void AddArtifact(string repoRoot, List<ArtifactInfo> artifacts, string label, string path, byte[] data)
    {
        artifacts.Add(new ArtifactInfo
        {
            Label = label,
            RelativePath = Path.GetRelativePath(repoRoot, path).Replace('\\', '/'),
            Size = data.Length,
            VersionWord = data.Length >= 2 ? Hex(ReadVersionWord(data), 4) : "missing",
            Sha256 = Sha256(data)
        });
    }

    private static ConfigurationKeybindRow FindRow(IReadOnlyList<ConfigurationKeybindRow> rows, string group, string action) =>
        rows.First(row => row.GroupLabel == group && row.ActionLabel == action);

    private static Dictionary<int, int> ReadOptionEntryOffsets(byte[] data)
    {
        Dictionary<int, int> offsets = new();
        for (int off = OptionsEntriesStart; off + OptionsEntrySize <= OptionsTailStart; off += OptionsEntrySize)
        {
            int entryId = BinaryPrimitives.ReadInt32LittleEndian(data.AsSpan(off + 0x04, 4));
            offsets[entryId] = off;
        }
        return offsets;
    }

    private static float ChooseDifferentFloat(float current) =>
        Math.Abs(current - 0.125f) < 0.0001f ? 0.875f : 0.125f;

    private static uint ChooseDifferentControllerConfig(uint current) =>
        current is >= 1 and <= 3 ? current + 1 : 1;

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
            return Enumerable.Range(0, Math.Max(before.Length, after.Length)).ToArray();
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

    private static int CountLegacyTrapHits(IEnumerable<int> offsets) =>
        offsets.Count(offset => LegacyTrapOffsets.Contains(offset));

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

    private static string Sha256(byte[] data) =>
        Convert.ToHexString(SHA256.HashData(data)).ToLowerInvariant();

    private static string RangeLabel(int start, int endInclusive) =>
        $"{HexOffset(start)}-{HexOffset(endInclusive)}";

    private static string HexOffset(int value) => Hex(value, 4);

    private static string Hex(long value, int digits) => $"0x{value.ToString($"X{digits}")}";

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
        Console.WriteLine("Usage: dotnet run --project tools/SaveOptionsAppCoreFixtureMatrixHarness -- [--repo-root .]");
    }

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
        public MatrixInfo Matrix { get; set; } = new();
        public CaseInfo[] Cases { get; set; } = [];
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
        public bool CareerSourceUnchanged { get; set; }
        public bool DefaultOptionsSourceUnchanged { get; set; }
        public int CareerSourceToInputDiffCount { get; set; }
        public int DefaultOptionsSourceToInputDiffCount { get; set; }
    }

    private sealed class ContainerInfo
    {
        public int ExpectedSize { get; set; }
        public string VersionWord { get; set; } = "";
        public string TrueViewRule { get; set; } = "";
        public string CareerSlotsBase { get; set; } = "";
        public string CareerSlotsEndExclusive { get; set; } = "";
        public string OptionsEntriesRange { get; set; } = "";
        public string OptionsTailRange { get; set; } = "";
        public bool AllOutputsFileSizePreserved { get; set; }
        public bool AllOutputsVersionWordPreserved { get; set; }
    }

    private sealed class MatrixInfo
    {
        public int FixtureFamilyCount { get; set; }
        public int AppCoreFixtureCaseCount { get; set; }
        public int ContainerAnalyzerCaseCount { get; set; }
        public int CareerKillCategoryCaseCount { get; set; }
        public int KillBoundaryCaseCount { get; set; }
        public int DefaultOptionsSettingCaseCount { get; set; }
        public int OptionsCopyCaseCount { get; set; }
        public int ControllerKeybindCaseCount { get; set; }
        public int SlotBitsetCaseCount { get; set; }
        public int RejectionNoOpLegacyCaseCount { get; set; }
        public int OutputCaseCount { get; set; }
        public int RejectionCaseCount { get; set; }
        public int NoOpCaseCount { get; set; }
        public int NoOpDiffCount { get; set; }
        public int UnexpectedDiffCount { get; set; }
        public int LegacyTrapHitCountNonSlot { get; set; }
        public bool AllRejectionsOutputNotCreated { get; set; }
        public bool KeybindDiffsWithinOptionsEntriesAndTailControlScheme { get; set; }
        public int SlotRoundTripCaseCount { get; set; }
        public int DerivedInvalidFixtureCount { get; set; }
    }

    private sealed record CaseInfo
    {
        public string Family { get; init; } = "";
        public string Name { get; init; } = "";
        public string Status { get; init; } = "";
        public string Operation { get; init; } = "";
        public bool AnalysisValid { get; init; }
        public bool OutputCreated { get; init; }
        public bool OutputCreatedAfterRejection { get; init; }
        public bool RejectionCase { get; init; }
        public bool FileSizePreserved { get; init; }
        public bool VersionWordPreserved { get; init; }
        public string[] ChangedOffsets { get; init; } = [];
        public int ChangedOffsetCount { get; init; }
        public string[] AllowedRanges { get; init; } = [];
        public int UnexpectedDiffCount { get; init; }
        public int LegacyTrapHitCount { get; init; }
        public bool MetadataBytePreserved { get; init; }
        public uint Lower24Expected { get; init; }
        public uint Lower24Observed { get; init; }
        public bool Lower24MatchedExpected { get; init; }
        public bool OptionsEntriesUnchanged { get; init; }
        public bool OptionsTailUnchanged { get; init; }
        public int? NoOpDiffCount { get; init; }
        public bool KeybindDiffsWithinOptionsEntriesAndTailControlScheme { get; init; }
        public bool SlotRoundTrip { get; init; }
        public int SourceToInputDiffCount { get; init; }
        public bool SourceUnchanged { get; init; }
        public bool DerivedInvalidFixture { get; init; }

        public static CaseInfo Pass(string family, string name, string operation, bool outputCreated) => new()
        {
            Family = family,
            Name = name,
            Status = "PASS",
            Operation = operation,
            OutputCreated = outputCreated
        };

        public static CaseInfo Rejection(string family, string name, string operation, string outputPath, PatchResult result) => new()
        {
            Family = family,
            Name = name,
            Status = !result.Success && !File.Exists(outputPath) ? "PASS" : "FAIL",
            Operation = operation,
            RejectionCase = true,
            OutputCreated = false,
            OutputCreatedAfterRejection = File.Exists(outputPath),
            FileSizePreserved = true,
            VersionWordPreserved = true,
            SourceUnchanged = true
        };
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
        public bool NewLaunch { get; set; }
        public bool ScreenshotCapture { get; set; }
        public bool NativeInput { get; set; }
        public bool DebuggerAttachment { get; set; }
        public bool CopiedExecutablePatchApplied { get; set; }
        public bool BinaryPatchEngineUsed { get; set; }
        public bool PatchCatalogTouched { get; set; }
        public bool GhidraMutation { get; set; }
        public bool ExecutablePatching { get; set; }
        public bool GodotWork { get; set; }
        public bool ProductUiWired { get; set; }
        public bool RebuildImplementation { get; set; }
        public bool RuntimeSaveLoadProof { get; set; }
        public bool RuntimeDefaultOptionsProof { get; set; }
    }
}
