using System;
using System.Buffers.Binary;
using System.Collections.Generic;
using System.ComponentModel;
using System.Globalization;
using System.IO;
using System.Linq;
using System.Runtime.CompilerServices;

namespace Onslaught___Career_Editor
{
    public sealed class SaveMissionRankRow : INotifyPropertyChanged
    {
        private string _currentRank = "-";
        private string _selectedRank = "Keep";

        public int NodeIndexZeroBased { get; init; }
        public string NodeLabel { get; init; } = string.Empty;
        public string MissionLabel { get; init; } = string.Empty;
        public IReadOnlyList<string> RankChoices => new[] { "Keep", "S", "A", "B", "C", "D", "E", "NONE" };

        public string CurrentRank
        {
            get => _currentRank;
            set => SetField(ref _currentRank, value);
        }

        public string SelectedRank
        {
            get => _selectedRank;
            set => SetField(ref _selectedRank, value);
        }

        public event PropertyChangedEventHandler? PropertyChanged;

        private void SetField(ref string field, string value, [CallerMemberName] string? propertyName = null)
        {
            if (string.Equals(field, value, StringComparison.Ordinal))
            {
                return;
            }

            field = value;
            PropertyChanged?.Invoke(this, new PropertyChangedEventArgs(propertyName));
        }
    }

    public sealed class SaveCategoryKillRow : INotifyPropertyChanged
    {
        private bool _overrideEnabled;
        private double _overrideValue;

        public int CategoryIndex { get; init; }
        public string CategoryName { get; init; } = string.Empty;
        public string ThresholdLabel { get; init; } = string.Empty;
        public int CurrentValue { get; init; }

        public bool OverrideEnabled
        {
            get => _overrideEnabled;
            set
            {
                if (_overrideEnabled == value)
                {
                    return;
                }

                _overrideEnabled = value;
                PropertyChanged?.Invoke(this, new PropertyChangedEventArgs(nameof(OverrideEnabled)));
            }
        }

        public double OverrideValue
        {
            get => _overrideValue;
            set
            {
                if (Math.Abs(_overrideValue - value) < double.Epsilon)
                {
                    return;
                }

                _overrideValue = value;
                PropertyChanged?.Invoke(this, new PropertyChangedEventArgs(nameof(OverrideValue)));
            }
        }

        public event PropertyChangedEventHandler? PropertyChanged;
    }

    public static class SaveEditorAdvancedService
    {
        private const int NodeBaseOffset = 0x0006;
        private const int NodeSize = 64;
        private const int NodeCount = 100;
        private const int NodeRankOffset = 0x3C;
        private static readonly int[] MissionWorldNumbers =
        {
            100,110,200,211,212,221,222,231,232,300,311,312,321,322,331,332,400,411,412,421,422,431,432,
            500,511,512,521,522,523,524,600,611,612,621,622,700,710,720,731,732,741,742,800
        };

        private static readonly (int CategoryIndex, string CategoryName, string ThresholdLabel, int DefaultSeed)[] CategoryDefinitions =
        {
            (BesFilePatcher.KILL_AIRCRAFT, "Aircraft", "25 / 50 / 75 / 100", 100),
            (BesFilePatcher.KILL_VEHICLES, "Vehicles", "100 / 200 / 300 / 400", 100),
            (BesFilePatcher.KILL_EMPLACEMENTS, "Emplacements", "25 / 50 / 75", 25),
            (BesFilePatcher.KILL_INFANTRY, "Infantry", "40 / 80 / 160", 40),
            (BesFilePatcher.KILL_MECHS, "Mechs", "20 / 40 / 80", 20)
        };

        private static readonly Dictionary<uint, string> RankBitsToName = new()
        {
            { 0x3F800000u, "S" },
            { 0x3F4CCCCDu, "A" },
            { 0x3F19999Au, "B" },
            { 0x3EB33333u, "C" },
            { 0x3E19999Au, "D" },
            { 0x00000000u, "E" },
            { 0xBF800000u, "NONE" }
        };

        public static IReadOnlyList<SaveMissionRankRow> LoadMissionRankRows(string? filePath)
        {
            List<SaveMissionRankRow> rows = new();
            for (int i = 0; i < MissionWorldNumbers.Length; i++)
            {
                int world = MissionWorldNumbers[i];
                string note = world switch
                {
                    100 => "Training",
                    110 => "Tutorial",
                    500 => "Branching",
                    800 => "Final",
                    _ => string.Empty
                };

                rows.Add(new SaveMissionRankRow
                {
                    NodeIndexZeroBased = i,
                    NodeLabel = $"{i + 1:00}",
                    MissionLabel = string.IsNullOrWhiteSpace(note) ? $"level{world}" : $"level{world} ({note})"
                });
            }

            if (string.IsNullOrWhiteSpace(filePath) || !File.Exists(filePath))
            {
                return rows;
            }

            try
            {
                byte[] buf = File.ReadAllBytes(filePath);
                if (buf.Length != BesFilePatcher.EXPECTED_FILE_SIZE)
                {
                    return rows;
                }

                for (int i = 0; i < rows.Count && i < NodeCount; i++)
                {
                    int nodeOff = NodeBaseOffset + (i * NodeSize);
                    if (nodeOff + NodeSize > buf.Length)
                    {
                        break;
                    }

                    uint rankBits = BinaryPrimitives.ReadUInt32LittleEndian(buf.AsSpan(nodeOff + NodeRankOffset, 4));
                    rows[i].CurrentRank = DecodeRankBits(rankBits);
                }
            }
            catch
            {
            }

            return rows;
        }

        public static IReadOnlyList<SaveCategoryKillRow> LoadCategoryKillRows(string? filePath)
        {
            int[] counts = CategoryDefinitions.Select(definition => definition.DefaultSeed).ToArray();
            if (!string.IsNullOrWhiteSpace(filePath) && File.Exists(filePath))
            {
                try
                {
                    SaveAnalysis analysis = BesFilePatcher.AnalyzeSave(filePath);
                    if (analysis.IsValid && analysis.KillCounts.Length >= CategoryDefinitions.Length)
                    {
                        for (int i = 0; i < CategoryDefinitions.Length; i++)
                        {
                            counts[i] = analysis.KillCounts[i];
                        }
                    }
                }
                catch
                {
                }
            }

            return CategoryDefinitions.Select((definition, index) => new SaveCategoryKillRow
            {
                CategoryIndex = definition.CategoryIndex,
                CategoryName = definition.CategoryName,
                ThresholdLabel = definition.ThresholdLabel,
                CurrentValue = counts[index],
                OverrideEnabled = false,
                OverrideValue = counts[index]
            }).ToArray();
        }

        public static int GetSuggestedGlobalKillSeed(IReadOnlyList<SaveCategoryKillRow> rows)
        {
            if (rows.Count == 0)
            {
                return 100;
            }

            int[] counts = rows.Select(row => row.CurrentValue).ToArray();
            return counts.Distinct().Count() > 1 ? counts.Max() : counts[0];
        }

        public static string BuildKillSeedSummary(IReadOnlyList<SaveCategoryKillRow> rows)
        {
            if (rows.Count == 0)
            {
                return "No save is loaded yet. This field is only the write value used for unchecked categories; it is not a cumulative score.";
            }

            int[] counts = rows.Select(row => row.CurrentValue).ToArray();
            int baselineSeed = GetSuggestedGlobalKillSeed(rows);
            return counts.Distinct().Count() > 1
                ? $"Loaded save uses mixed category counts. The default write value was seeded to the highest current count ({baselineSeed:N0}) so an unchecked-row patch does not silently lower a category."
                : $"Loaded save uses a shared kill value of {baselineSeed:N0} across all five categories.";
        }

        public static int CountMissionRankOverrides(IReadOnlyList<SaveMissionRankRow> rows)
        {
            return rows.Count(row => !string.Equals(row.SelectedRank, "Keep", StringComparison.OrdinalIgnoreCase));
        }

        public static int CountCategoryKillOverrides(IReadOnlyList<SaveCategoryKillRow> rows)
        {
            return rows.Count(row => row.OverrideEnabled);
        }

        public static bool TryBuildLevelRanks(
            IReadOnlyList<SaveMissionRankRow> rows,
            out Dictionary<int, string>? levelRanks,
            out string? error)
        {
            levelRanks = null;
            error = null;
            Dictionary<int, string> result = new();
            HashSet<string> valid = new(StringComparer.OrdinalIgnoreCase) { "S", "A", "B", "C", "D", "E", "NONE" };
            foreach (SaveMissionRankRow row in rows)
            {
                string selected = (row.SelectedRank ?? "Keep").Trim();
                if (selected.Equals("Keep", StringComparison.OrdinalIgnoreCase))
                {
                    continue;
                }

                string normalized = selected.ToUpperInvariant();
                if (!valid.Contains(normalized))
                {
                    error = $"Invalid rank override '{selected}' for mission node {row.NodeLabel}.";
                    return false;
                }

                result[row.NodeIndexZeroBased] = normalized;
            }

            levelRanks = result.Count == 0 ? null : result;
            return true;
        }

        public static bool TryBuildPerCategoryKills(
            IReadOnlyList<SaveCategoryKillRow> rows,
            out Dictionary<int, int>? perCategoryKills,
            out string? error)
        {
            perCategoryKills = null;
            error = null;
            Dictionary<int, int> result = new();
            foreach (SaveCategoryKillRow row in rows)
            {
                if (!row.OverrideEnabled)
                {
                    continue;
                }

                if (double.IsNaN(row.OverrideValue) || double.IsInfinity(row.OverrideValue))
                {
                    error = $"{row.CategoryName} override must be a finite non-negative whole number.";
                    return false;
                }

                int clamped = ClampKillValue((int)Math.Round(row.OverrideValue, MidpointRounding.AwayFromZero));
                result[row.CategoryIndex] = clamped;
            }

            perCategoryKills = result.Count == 0 ? null : result;
            return true;
        }

        private static string DecodeRankBits(uint rankBits)
        {
            if (RankBitsToName.TryGetValue(rankBits, out string? exact))
            {
                return exact;
            }

            float value = BitConverter.ToSingle(BitConverter.GetBytes(rankBits), 0);
            if (value >= 0.9f) return $"~S ({value:F2})";
            if (value >= 0.7f) return $"~A ({value:F2})";
            if (value >= 0.5f) return $"~B ({value:F2})";
            if (value >= 0.25f) return $"~C ({value:F2})";
            if (value >= 0.1f) return $"~D ({value:F2})";
            if (value > 0f) return $"~D ({value:F2})";
            if (value == 0f) return "E";
            if (value < 0f) return "NONE";
            return $"0x{rankBits:X8}";
        }

        private static int ClampKillValue(int value)
        {
            if (value < 0)
            {
                return 0;
            }

            if (value > 0x00FFFFFF)
            {
                return 0x00FFFFFF;
            }

            return value;
        }
    }
}
