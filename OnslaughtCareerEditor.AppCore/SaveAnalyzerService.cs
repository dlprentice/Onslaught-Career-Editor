using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;

namespace Onslaught___Career_Editor
{
    public sealed class SaveAnalyzerFileItem
    {
        public string Path { get; init; } = string.Empty;
        public string Name { get; init; } = string.Empty;
        public string DisplayName { get; init; } = string.Empty;
        public bool IsValid { get; init; }
        public DateTime Modified { get; init; }

        public override string ToString() => DisplayName;
    }

    public sealed class SaveAnalyzerMetric
    {
        public string Label { get; init; } = string.Empty;
        public string Value { get; init; } = string.Empty;
        public string? Detail { get; init; }
    }

    public sealed class SaveAnalyzerTreeNode
    {
        public string Label { get; init; } = string.Empty;
        public IReadOnlyList<SaveAnalyzerTreeNode> Children { get; init; } = Array.Empty<SaveAnalyzerTreeNode>();
    }

    public sealed class SaveAnalyzerDocument
    {
        public bool IsComparisonMode { get; init; }
        public string Title { get; init; } = string.Empty;
        public string ModeText { get; init; } = string.Empty;
        public string StatusText { get; init; } = string.Empty;
        public string SummaryTitle { get; init; } = string.Empty;
        public string ReportText { get; init; } = string.Empty;
        public IReadOnlyList<SaveAnalyzerMetric> Metrics { get; init; } = Array.Empty<SaveAnalyzerMetric>();
        public IReadOnlyList<SaveAnalyzerTreeNode> SummaryNodes { get; init; } = Array.Empty<SaveAnalyzerTreeNode>();
    }

    public static class SaveAnalyzerService
    {
        private static readonly string[] KillCategories = { "Aircraft", "Vehicles", "Emplacements", "Infantry", "Mechs" };

        public static IReadOnlyList<SaveAnalyzerFileItem> GetDetectedFiles(string? gameDir = null)
        {
            return AppConfig.FindSaveFiles(gameDir)
                .Select(save => new SaveAnalyzerFileItem
                {
                    Path = save.Path,
                    Name = save.Name,
                    IsValid = save.IsValid,
                    Modified = save.Modified,
                    DisplayName = BuildDisplayName(save)
                })
                .ToArray();
        }

        public static SaveAnalyzerDocument AnalyzeFile(string filePath, bool verbose, bool dumpMystery)
        {
            SaveAnalysis analysis = BesFilePatcher.AnalyzeSave(filePath);
            return BuildAnalysisDocument(analysis, verbose, dumpMystery);
        }

        public static SaveAnalyzerDocument CompareFiles(string leftPath, string rightPath)
        {
            BesFilePatcher.CompareResult result = BesFilePatcher.CompareFiles(leftPath, rightPath);
            return BuildCompareDocument(leftPath, rightPath, result);
        }

        public static SaveAnalyzerDocument BuildAnalysisDocument(SaveAnalysis analysis, bool verbose, bool dumpMystery)
        {
            string fileName = Path.GetFileName(analysis.FilePath) ?? "Unknown file";
            bool isValid = analysis.IsValid;
            int usedNodes = analysis.CompletedNodes + analysis.PartialNodes;
            int unlockedGoodies = analysis.GoodiesNew + analysis.GoodiesOld;
            int displayableGoodies = analysis.GoodiesNew
                                     + analysis.GoodiesOld
                                     + analysis.GoodiesLocked
                                     + analysis.GoodiesInstructions
                                     + analysis.GoodiesOther;
            int totalKills = analysis.KillCounts.Sum();

            List<SaveAnalyzerMetric> metrics = new()
            {
                new SaveAnalyzerMetric
                {
                    Label = "File Kind",
                    Value = analysis.IsOptionsFile ? "Global Options" : "Career Save",
                    Detail = analysis.IsOptionsFile ? ".bea boot snapshot" : ".bes mission progress"
                },
                new SaveAnalyzerMetric
                {
                    Label = "Missions",
                    Value = isValid ? $"{analysis.CompletedNodes}/{usedNodes}" : "Invalid",
                    Detail = isValid ? "completed / used nodes" : analysis.ErrorMessage
                },
                new SaveAnalyzerMetric
                {
                    Label = "Goodies",
                    Value = isValid ? $"{unlockedGoodies}/{displayableGoodies}" : "--",
                    Detail = isValid ? "unlocked / displayable" : null
                },
                new SaveAnalyzerMetric
                {
                    Label = "Kill Total",
                    Value = isValid ? totalKills.ToString("N0") : "--",
                    Detail = isValid ? "all tracked categories" : null
                },
                new SaveAnalyzerMetric
                {
                    Label = "Tech Slots",
                    Value = isValid ? $"{analysis.ActiveTechSlots}/{analysis.TotalTechSlots}" : "--",
                    Detail = isValid ? "active / total" : null
                }
            };

            return new SaveAnalyzerDocument
            {
                IsComparisonMode = false,
                Title = $"Analysis: {fileName}",
                SummaryTitle = "Analysis Summary",
                ModeText = analysis.IsOptionsFile
                    ? "Single-file analysis: defaultoptions.bea / .bea global settings view."
                    : "Single-file analysis: .bes career save view.",
                StatusText = isValid
                    ? $"Save Analyzer: {analysis.CompletedNodes} missions, {analysis.CompletedLinks} links"
                    : $"Save Analyzer: Invalid file - {analysis.ErrorMessage}",
                ReportText = BesFilePatcher.FormatAnalysisReport(analysis, verbose, dumpMystery),
                Metrics = metrics,
                SummaryNodes = BuildAnalysisSummaryNodes(analysis)
            };
        }

        public static SaveAnalyzerDocument BuildCompareDocument(string leftPath, string rightPath, BesFilePatcher.CompareResult result)
        {
            string? topRegion = result.RegionCounts
                .OrderByDescending(row => row.Value)
                .Select(row => row.Key)
                .FirstOrDefault();

            List<SaveAnalyzerMetric> metrics = new()
            {
                new SaveAnalyzerMetric
                {
                    Label = "Size Match",
                    Value = result.SameSize ? "Yes" : "No",
                    Detail = $"{result.File1Size:N0} vs {result.File2Size:N0} bytes"
                },
                new SaveAnalyzerMetric
                {
                    Label = "Differing Bytes",
                    Value = result.DifferingBytes.ToString("N0"),
                    Detail = "byte-level differences"
                },
                new SaveAnalyzerMetric
                {
                    Label = "Ranges",
                    Value = result.DiffRanges.Count.ToString("N0"),
                    Detail = "contiguous diff regions"
                },
                new SaveAnalyzerMetric
                {
                    Label = "Options Involved",
                    Value = IsOptionsPath(leftPath) || IsOptionsPath(rightPath) ? "Yes" : "No",
                    Detail = ".bea snapshot included"
                },
                new SaveAnalyzerMetric
                {
                    Label = "Top Region",
                    Value = topRegion ?? "None",
                    Detail = topRegion is null ? "files identical" : "highest differing byte count"
                }
            };

            return new SaveAnalyzerDocument
            {
                IsComparisonMode = true,
                Title = "File Comparison",
                SummaryTitle = "Comparison Summary",
                ModeText = "Comparison mode: summary counts and differing regions for the selected pair.",
                StatusText = result.DifferingBytes == 0
                    ? "Save Analyzer: Files are identical"
                    : $"Save Analyzer: Found {result.DifferingBytes} differing bytes in {result.DiffRanges.Count} regions",
                ReportText = BesFilePatcher.FormatCompareReport(result, leftPath, rightPath),
                Metrics = metrics,
                SummaryNodes = BuildCompareSummaryNodes(leftPath, rightPath, result)
            };
        }

        private static IReadOnlyList<SaveAnalyzerTreeNode> BuildAnalysisSummaryNodes(SaveAnalysis analysis)
        {
            if (!analysis.IsValid)
            {
                return new[]
                {
                    Node(analysis.ErrorMessage ?? "No analysis available")
                };
            }

            List<SaveAnalyzerTreeNode> nodes = new();

            nodes.Add(Node(
                "File Info",
                $"Size: {analysis.FileSize:N0} bytes",
                $"Version word: 0x{analysis.VersionWord:X4} {(analysis.VersionValid ? "(valid)" : "(INVALID)")}",
                $"Header dword view @0x0000: 0x{analysis.VersionStamp:X8}",
                $"NewGoodieCount: {analysis.NewGoodieCountRaw} (0x{analysis.NewGoodieCountRaw:X8})"));

            List<SaveAnalyzerTreeNode> optionsChildren = new()
            {
                Node($"File kind: {(analysis.IsOptionsFile ? "defaultoptions.bea (boot/global)" : ".bes (career save)")}", Array.Empty<string>()),
                Node(
                    analysis.IsOptionsFile
                        ? ".bea is the boot-time source for keybinds and most global settings."
                        : ".bes stores a snapshot; retail load/save flows may sync it into defaultoptions.bea for next boot.",
                    Array.Empty<string>()),
                Node($"Volumes: Sound={analysis.SoundVolume:0.###} Music={analysis.MusicVolume:0.###}", Array.Empty<string>()),
                Node($"InvertY Walker: P1={(analysis.InvertYAxisRaw[0] != 0 ? "ON" : "OFF")}, P2={(analysis.InvertYAxisRaw[1] != 0 ? "ON" : "OFF")}", Array.Empty<string>()),
                Node($"InvertY Flight: P1={(analysis.InvertFlightRaw[0] != 0 ? "ON" : "OFF")}, P2={(analysis.InvertFlightRaw[1] != 0 ? "ON" : "OFF")}", Array.Empty<string>()),
                Node($"Vibration: P1={(analysis.VibrationRaw[0] != 0 ? "ON" : "OFF")}, P2={(analysis.VibrationRaw[1] != 0 ? "ON" : "OFF")}", Array.Empty<string>())
            };
            if (analysis.OptionsEntryCount > 0)
            {
                optionsChildren.Add(Node($"Options entries: {analysis.OptionsEntryCount} (tail @ 0x{analysis.OptionsTailStart:X4})", Array.Empty<string>()));
                optionsChildren.Add(Node($"ControlSchemeIndex: {analysis.OptionsControlSchemeIndex}", Array.Empty<string>()));
                optionsChildren.Add(Node($"MouseSensitivity: {analysis.OptionsMouseSensitivity:0.###}", Array.Empty<string>()));
                optionsChildren.Add(Node($"ScreenShape: {analysis.OptionsScreenShape} (0=4:3,1=16:9,2=1:1)", Array.Empty<string>()));
            }

            nodes.Add(new SaveAnalyzerTreeNode
            {
                Label = analysis.IsOptionsFile ? "Boot-Time Global Options (.bea)" : "Stored Options Snapshot (.bes)",
                Children = optionsChildren
            });

            List<SaveAnalyzerTreeNode> missionChildren = new();
            foreach (string rank in new[] { "S", "A", "B", "C", "D", "E", "NONE" })
            {
                if (analysis.RankDistribution.TryGetValue(rank, out int count))
                {
                    missionChildren.Add(Node($"{rank}-rank: {count}", Array.Empty<string>()));
                }
            }

            if (analysis.PartialNodes > 0)
            {
                missionChildren.Add(Node($"Partial: {analysis.PartialNodes}", Array.Empty<string>()));
            }

            nodes.Add(new SaveAnalyzerTreeNode
            {
                Label = $"Missions ({analysis.CompletedNodes}/{analysis.CompletedNodes + analysis.PartialNodes} completed)",
                Children = missionChildren
            });

            nodes.Add(Node($"Links ({analysis.CompletedLinks}/{analysis.TotalLinks})", Array.Empty<string>()));

            List<SaveAnalyzerTreeNode> goodiesChildren = new();
            if (analysis.GoodiesNew > 0)
            {
                goodiesChildren.Add(Node($"NEW (gold): {analysis.GoodiesNew}", Array.Empty<string>()));
            }

            if (analysis.GoodiesOld > 0)
            {
                goodiesChildren.Add(Node($"OLD (blue): {analysis.GoodiesOld}", Array.Empty<string>()));
            }

            if (analysis.GoodiesLocked > 0)
            {
                goodiesChildren.Add(Node($"Locked: {analysis.GoodiesLocked}", Array.Empty<string>()));
            }

            if (analysis.GoodiesOther > 0)
            {
                goodiesChildren.Add(Node($"Other: {analysis.GoodiesOther}", Array.Empty<string>()));
            }

            int unlockedGoodies = analysis.GoodiesNew + analysis.GoodiesOld;
            int displayableGoodies = analysis.GoodiesNew + analysis.GoodiesOld + analysis.GoodiesLocked + analysis.GoodiesInstructions + analysis.GoodiesOther;
            nodes.Add(new SaveAnalyzerTreeNode
            {
                Label = $"Goodies ({unlockedGoodies}/{displayableGoodies} unlocked)",
                Children = goodiesChildren
            });

            List<SaveAnalyzerTreeNode> killChildren = new();
            for (int i = 0; i < KillCategories.Length; i++)
            {
                string threshold = analysis.NextUnlockThresholds[i].HasValue
                    ? $" (next: {analysis.NextUnlockThresholds[i]})"
                    : " (max)";
                killChildren.Add(Node($"{KillCategories[i]}: {analysis.KillCounts[i]:N0}{threshold}", Array.Empty<string>()));
            }

            nodes.Add(new SaveAnalyzerTreeNode
            {
                Label = $"Kill Counts ({analysis.KillCounts.Sum():N0} total)",
                Children = killChildren
            });

            nodes.Add(Node(
                "God Mode",
                $"Enabled (toggle): {(analysis.GodModeEnabledOn ? "ON" : "OFF")} (0x{analysis.GodModeEnabledRaw:X8})"));

            nodes.Add(Node($"Tech Slots ({analysis.ActiveTechSlots}/{analysis.TotalTechSlots} active)", Array.Empty<string>()));

            if (analysis.MysteryRegions.Count > 0)
            {
                List<SaveAnalyzerTreeNode> mysteryChildren = analysis.MysteryRegions
                    .Select(region =>
                    {
                        string status = region.AllZeros
                            ? "[zeros]"
                            : region.AllFF
                                ? "[0xFF]"
                                : $"{region.NonZeroCount} non-zero";
                        return Node($"{region.Name}: {status}", Array.Empty<string>());
                    })
                    .ToList();

                nodes.Add(new SaveAnalyzerTreeNode
                {
                    Label = $"Unmapped/Reserved Regions ({analysis.MysteryRegions.Sum(region => region.Size)} bytes)",
                    Children = mysteryChildren
                });
            }

            return nodes;
        }

        private static IReadOnlyList<SaveAnalyzerTreeNode> BuildCompareSummaryNodes(string leftPath, string rightPath, BesFilePatcher.CompareResult result)
        {
            List<SaveAnalyzerTreeNode> children = new()
            {
                Node($"Left file: {Path.GetFileName(leftPath)}", Array.Empty<string>()),
                Node($"Right file: {Path.GetFileName(rightPath)}", Array.Empty<string>()),
                Node($"Size match: {(result.SameSize ? "Yes" : "No")} ({result.File1Size:N0} vs {result.File2Size:N0} bytes)", Array.Empty<string>()),
                Node($"Differing bytes: {result.DifferingBytes:N0}", Array.Empty<string>()),
                Node($"Difference ranges: {result.DiffRanges.Count}", Array.Empty<string>()),
                Node($".bea / options involved: {(IsOptionsPath(leftPath) || IsOptionsPath(rightPath) ? "Yes" : "No")}", Array.Empty<string>())
            };

            if (result.RegionCounts.Count > 0)
            {
                children.Add(new SaveAnalyzerTreeNode
                {
                    Label = "Regions with differences",
                    Children = result.RegionCounts
                        .OrderByDescending(row => row.Value)
                        .Select(row => Node($"{row.Key}: {row.Value:N0}", Array.Empty<string>()))
                        .ToArray()
                });
            }

            return new[]
            {
                new SaveAnalyzerTreeNode
                {
                    Label = "Comparison",
                    Children = children
                }
            };
        }

        private static SaveAnalyzerTreeNode Node(string label, params string[] children)
        {
            return new SaveAnalyzerTreeNode
            {
                Label = label,
                Children = children.Select(child => new SaveAnalyzerTreeNode { Label = child }).ToArray()
            };
        }

        private static string BuildDisplayName(SaveFileInfo save)
        {
            string validity = save.IsValid ? string.Empty : " [invalid file]";
            return $"{Path.GetFileName(save.Path)} ({save.Modified:MMM dd, HH:mm}){validity}";
        }

        private static bool IsOptionsPath(string path)
        {
            string fileNameOnly = Path.GetFileName(path);
            return string.Equals(Path.GetExtension(path), ".bea", StringComparison.OrdinalIgnoreCase)
                || fileNameOnly.StartsWith("defaultoptions.bea", StringComparison.OrdinalIgnoreCase);
        }
    }
}
