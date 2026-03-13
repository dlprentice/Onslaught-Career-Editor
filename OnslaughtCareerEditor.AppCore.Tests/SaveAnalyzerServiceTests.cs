using System.Collections.Generic;
using System.Linq;
using Onslaught___Career_Editor;
using Xunit;

namespace OnslaughtCareerEditor.AppCore.Tests
{
    public sealed class SaveAnalyzerServiceTests
    {
        [Fact]
        public void BuildDefaultSaveOutputPath_AppendsPatchedSuffix()
        {
            string output = SaveEditorService.BuildDefaultSaveOutputPath(@"C:\temp\career.bes");
            Assert.Equal(@"C:\temp\career_patched.bes", output);
        }

        [Fact]
        public void PatchSave_FailsWhenInputAndOutputPathsMatch()
        {
            PatchResult result = SaveEditorService.PatchSave(new SavePatchRequest
            {
                InputPath = @"C:\temp\career.bes",
                OutputPath = @"C:\temp\career.bes",
                PatchNodes = true
            });

            Assert.False(result.Success);
            Assert.Contains("Output file must be different from input file", result.Message);
        }

        [Fact]
        public void ConfigurationPendingSummary_IncludesSettingsCopyAndKeybinds()
        {
            ConfigurationPatchRequest request = new()
            {
                InputPath = @"C:\temp\defaultoptions.bea",
                OutputPath = @"C:\temp\defaultoptions.bea",
                SoundVolumeOverride = 0.8f,
                CopyOptionsTail = true,
                KeybindRows = new[]
                {
                    new ConfigurationKeybindRow
                    {
                        GroupLabel = "Movement",
                        ActionLabel = "Forward",
                        EntryId = 0x1F,
                        KeyboardDeviceCode = 9,
                        Player1Token = "Key W"
                    }
                }
            };

            string summary = ConfigurationEditorService.BuildPendingChangesSummary(request);

            Assert.Contains("settings overrides", summary);
            Assert.Contains("copied options tail", summary);
            Assert.Contains("1 keybind row", summary);
        }

        [Fact]
        public void ConfigurationValidation_FlagsUnsupportedMouseBinding()
        {
            IReadOnlyList<string> errors = ConfigurationEditorService.ValidateKeybindRows(new[]
            {
                new ConfigurationKeybindRow
                {
                    GroupLabel = "Actions",
                    ActionLabel = "Select weapon",
                    EntryId = 0x14,
                    KeyboardDeviceCode = 10,
                    AllowMouseButtons = true,
                    Player1Token = "MouseLeft"
                }
            });

            Assert.Single(errors);
            Assert.Contains("MouseLeft is only supported for Fire weapon", errors[0]);
        }

        [Fact]
        public void PatchConfiguration_FailsWhenPathIsNotOptionsLike()
        {
            PatchResult result = ConfigurationEditorService.PatchConfiguration(new ConfigurationPatchRequest
            {
                InputPath = @"C:\temp\career.bes",
                OutputPath = @"C:\temp\career_patched.bes",
                SoundVolumeOverride = 0.8f
            });

            Assert.False(result.Success);
            Assert.Contains("requires .bea/defaultoptions.bea", result.Message);
        }

        [Fact]
        public void SavePendingSummary_IncludesAdvancedOverrideCounts()
        {
            SavePatchRequest request = new()
            {
                InputPath = @"C:\temp\career.bes",
                OutputPath = @"C:\temp\career_patched.bes",
                PatchNodes = true,
                PatchKills = true,
                LevelRanks = new Dictionary<int, string> { [1] = "A", [4] = "S" },
                PerCategoryKills = new Dictionary<int, int> { [BesFilePatcher.KILL_INFANTRY] = 120 }
            };

            string summary = SaveEditorService.BuildPendingChangesSummary(request);

            Assert.Contains("2 mission rank overrides", summary);
            Assert.Contains("1 category kill override", summary);
        }

        [Fact]
        public void AdvancedSaveEditorBuildsMissionRankOverrides()
        {
            bool ok = SaveEditorAdvancedService.TryBuildLevelRanks(
                new[]
                {
                    new SaveMissionRankRow { NodeIndexZeroBased = 0, NodeLabel = "01", MissionLabel = "level100", SelectedRank = "Keep" },
                    new SaveMissionRankRow { NodeIndexZeroBased = 1, NodeLabel = "02", MissionLabel = "level110", SelectedRank = "A" }
                },
                out Dictionary<int, string>? levelRanks,
                out string? error);

            Assert.True(ok);
            Assert.Null(error);
            Assert.NotNull(levelRanks);
            Assert.Equal("A", levelRanks![1]);
        }

        [Fact]
        public void AdvancedSaveEditorRejectsInvalidMissionRank()
        {
            bool ok = SaveEditorAdvancedService.TryBuildLevelRanks(
                new[]
                {
                    new SaveMissionRankRow { NodeIndexZeroBased = 1, NodeLabel = "02", MissionLabel = "level110", SelectedRank = "Z" }
                },
                out Dictionary<int, string>? levelRanks,
                out string? error);

            Assert.False(ok);
            Assert.Null(levelRanks);
            Assert.Contains("Invalid rank override", error);
        }

        [Fact]
        public void AdvancedSaveEditorBuildsCategoryKillOverrides()
        {
            bool ok = SaveEditorAdvancedService.TryBuildPerCategoryKills(
                new[]
                {
                    new SaveCategoryKillRow
                    {
                        CategoryIndex = BesFilePatcher.KILL_AIRCRAFT,
                        CategoryName = "Aircraft",
                        ThresholdLabel = "25 / 50 / 75 / 100",
                        CurrentValue = 25,
                        OverrideEnabled = true,
                        OverrideValue = 123
                    }
                },
                out Dictionary<int, int>? perCategoryKills,
                out string? error);

            Assert.True(ok);
            Assert.Null(error);
            Assert.NotNull(perCategoryKills);
            Assert.Equal(123, perCategoryKills![BesFilePatcher.KILL_AIRCRAFT]);
        }

        [Fact]
        public void BuildAnalysisDocument_ForCareerSave_ProducesExpectedMetricsAndSummary()
        {
            SaveAnalysis analysis = new()
            {
                IsValid = true,
                FilePath = @"C:\temp\career.bes",
                IsOptionsFile = false,
                FileSize = BesFilePatcher.EXPECTED_FILE_SIZE,
                VersionWord = BesFilePatcher.VERSION_WORD,
                VersionValid = true,
                VersionStamp = BesFilePatcher.VERSION_STAMP_DWORD_VIEW,
                NewGoodieCountRaw = 12,
                CompletedNodes = 10,
                PartialNodes = 4,
                CompletedLinks = 25,
                TotalLinks = 40,
                GoodiesNew = 2,
                GoodiesOld = 18,
                GoodiesLocked = 5,
                GoodiesInstructions = 0,
                GoodiesOther = 1,
                KillCounts = new[] { 25, 100, 12, 8, 4 },
                NextUnlockThresholds = new int?[] { 50, 200, 25, 40, 20 },
                ActiveTechSlots = 5,
                TotalTechSlots = 32,
                SoundVolume = 0.75f,
                MusicVolume = 0.5f,
                RankDistribution = new Dictionary<string, int> { ["S"] = 6, ["A"] = 4 },
                MysteryRegions = new List<MysteryRegionData>
                {
                    new MysteryRegionData
                    {
                        Name = "ReservedTail",
                        StartOffset = 100,
                        EndOffset = 108,
                        NonZeroCount = 2,
                        Data = new byte[] { 1, 2 }
                    }
                }
            };

            SaveAnalyzerDocument document = SaveAnalyzerService.BuildAnalysisDocument(analysis, verbose: false, dumpMystery: false);

            Assert.False(document.IsComparisonMode);
            Assert.Equal("Analysis: career.bes", document.Title);
            Assert.Equal("Analysis Summary", document.SummaryTitle);
            Assert.Contains("career save", document.ModeText);
            Assert.Contains("10 missions, 25 links", document.StatusText);
            Assert.Equal("Career Save", document.Metrics.Single(metric => metric.Label == "File Kind").Value);
            Assert.Equal("10/14", document.Metrics.Single(metric => metric.Label == "Missions").Value);
            Assert.Equal("20/26", document.Metrics.Single(metric => metric.Label == "Goodies").Value);
            Assert.Equal("149", document.Metrics.Single(metric => metric.Label == "Kill Total").Value.Replace(",", string.Empty));
            Assert.Contains(document.SummaryNodes, node => node.Label.StartsWith("Missions (10/14 completed)"));
            Assert.Contains(document.SummaryNodes, node => node.Label.StartsWith("Unmapped/Reserved Regions (8 bytes)"));
            Assert.Contains("SAVE FILE ANALYSIS", document.ReportText);
        }

        [Fact]
        public void BuildAnalysisDocument_ForInvalidFile_SurfacesError()
        {
            SaveAnalysis analysis = new()
            {
                IsValid = false,
                FilePath = @"C:\temp\broken.bes",
                ErrorMessage = "Invalid file size"
            };

            SaveAnalyzerDocument document = SaveAnalyzerService.BuildAnalysisDocument(analysis, verbose: false, dumpMystery: false);

            Assert.Equal("Analysis: broken.bes", document.Title);
            Assert.Contains("Invalid file", document.StatusText);
            Assert.Single(document.SummaryNodes);
            Assert.Equal("Invalid file size", document.SummaryNodes[0].Label);
            Assert.Contains("ERROR: Invalid file size", document.ReportText);
        }

        [Fact]
        public void BuildCompareDocument_ProducesComparisonMetricsAndSummary()
        {
            BesFilePatcher.CompareResult result = new()
            {
                File1Name = "left.bes",
                File2Name = "right.bea",
                File1Size = BesFilePatcher.EXPECTED_FILE_SIZE,
                File2Size = BesFilePatcher.EXPECTED_FILE_SIZE,
                DifferingBytes = 32,
                RegionCounts = new Dictionary<string, int>
                {
                    ["Goodie[10]"] = 20,
                    ["VersionWord"] = 4
                },
                DiffRanges = new List<(int Start, int End)>
                {
                    (10, 20),
                    (100, 120)
                }
            };

            SaveAnalyzerDocument document = SaveAnalyzerService.BuildCompareDocument(@"C:\temp\left.bes", @"C:\temp\right.bea", result);

            Assert.True(document.IsComparisonMode);
            Assert.Equal("File Comparison", document.Title);
            Assert.Equal("Comparison Summary", document.SummaryTitle);
            Assert.Equal("32", document.Metrics.Single(metric => metric.Label == "Differing Bytes").Value);
            Assert.Equal("Yes", document.Metrics.Single(metric => metric.Label == "Options Involved").Value);
            Assert.Equal("Goodie[10]", document.Metrics.Single(metric => metric.Label == "Top Region").Value);
            Assert.Contains(document.SummaryNodes, node => node.Label == "Comparison");
            Assert.Contains("FILE COMPARISON", document.ReportText);
        }
    }
}
