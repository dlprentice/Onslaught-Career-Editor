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
        /// <summary>
        /// The choice that means "this mission carries no override of its own".
        ///
        /// It used to read "Keep", which was a lie: a row on Keep is simply omitted from
        /// <see cref="SaveEditorAdvancedService.TryBuildLevelRanks"/>, and the patcher then wrote the
        /// mission rank baseline over it. On a real mixed-grade specimen that turned 42 missions'
        /// grades into a wall of S while the control the user had left alone said "Keep".
        /// The row defers to the baseline, so it now says so. The baseline itself is what can keep.
        /// </summary>
        public const string UseBaselineChoice = "Use baseline";

        /// <summary>
        /// The pre-2026-07-26 spelling of <see cref="UseBaselineChoice"/>. Still accepted so that a
        /// caller holding the old string gets "no override" rather than having "Keep" parsed as a
        /// grade name and rejected. It is deliberately not offered in <see cref="RankChoices"/>.
        /// </summary>
        public const string LegacyUseBaselineChoice = "Keep";

        private string _currentRank = "-";
        private string _selectedRank = UseBaselineChoice;

        public int NodeIndexZeroBased { get; init; }
        public string NodeLabel { get; init; } = string.Empty;
        public string MissionLabel { get; init; } = string.Empty;
        public IReadOnlyList<string> RankChoices => new[] { UseBaselineChoice, "S", "A", "B", "C", "D", "E", "NONE" };

        public static bool IsUseBaselineChoice(string? selection)
        {
            string trimmed = (selection ?? string.Empty).Trim();
            return trimmed.Length == 0
                || trimmed.Equals(UseBaselineChoice, StringComparison.OrdinalIgnoreCase)
                || trimmed.Equals(LegacyUseBaselineChoice, StringComparison.OrdinalIgnoreCase);
        }

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

        /// <summary>
        /// False when <see cref="CurrentValue"/> is a hard-coded seed rather than a number read from a
        /// save. Two bare <c>catch {}</c> blocks used to leave the seeds 100/100/25/40/20 in this
        /// property, and the UI rendered them in its "Current" column as though the file had said so.
        /// </summary>
        public bool CurrentValueKnown { get; init; }

        /// <summary>What the "Current" column should render. Never presents a seed as a reading.</summary>
        public string CurrentValueLabel => CurrentValueKnown
            ? CurrentValue.ToString("N0", CultureInfo.InvariantCulture)
            : "-";

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

        /// <summary>
        /// Why a read of the advanced rows produced the values it did. Before this existed, both
        /// readers swallowed every exception into <c>catch {}</c>, so "no file selected", "file
        /// unreadable" and "file read fine" were indistinguishable at the call site and the UI stated
        /// hard-coded seeds as if they had come from the save.
        /// </summary>
        public sealed class SaveEditorAdvancedReadStatus
        {
            public bool FileWasRead { get; init; }
            public string? Reason { get; init; }

            public static SaveEditorAdvancedReadStatus Read() => new() { FileWasRead = true };

            public static SaveEditorAdvancedReadStatus NotRead(string reason) =>
                new() { FileWasRead = false, Reason = reason };
        }

        public static IReadOnlyList<SaveMissionRankRow> LoadMissionRankRows(string? filePath)
        {
            return LoadMissionRankRows(filePath, out _);
        }

        public static IReadOnlyList<SaveMissionRankRow> LoadMissionRankRows(
            string? filePath,
            out SaveEditorAdvancedReadStatus status)
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

            if (string.IsNullOrWhiteSpace(filePath))
            {
                status = SaveEditorAdvancedReadStatus.NotRead("No save is selected.");
                return rows;
            }

            if (!File.Exists(filePath))
            {
                status = SaveEditorAdvancedReadStatus.NotRead("The selected save file was not found.");
                return rows;
            }

            try
            {
                byte[] buf = File.ReadAllBytes(filePath);
                if (buf.Length != BesFilePatcher.EXPECTED_FILE_SIZE)
                {
                    // The analyzer understands the 0x2514 + 0x20*N size law, but every write path and
                    // this reader require exactly 10004 bytes. All 41 real specimens are 10004, so no
                    // observed file lands here; failing closed stays correct, but it must say so
                    // instead of returning blank rows that look like "no file selected".
                    status = SaveEditorAdvancedReadStatus.NotRead(
                        $"Mission grades were not read: this file is {buf.Length:N0} bytes and a career save is " +
                        $"{BesFilePatcher.EXPECTED_FILE_SIZE:N0}.");
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
            catch (Exception ex) when (ex is IOException or UnauthorizedAccessException or ArgumentException
                                        or NotSupportedException or InvalidDataException)
            {
                // Was `catch {}`. The rows returned here still read "-" in every Current column, which
                // is honest only because the caller is now told why.
                status = SaveEditorAdvancedReadStatus.NotRead($"Mission grades could not be read: {ex.Message}");
                return rows;
            }

            status = SaveEditorAdvancedReadStatus.Read();
            return rows;
        }

        public static IReadOnlyList<SaveCategoryKillRow> LoadCategoryKillRows(string? filePath)
        {
            return LoadCategoryKillRows(filePath, out _);
        }

        public static IReadOnlyList<SaveCategoryKillRow> LoadCategoryKillRows(
            string? filePath,
            out SaveEditorAdvancedReadStatus status)
        {
            // These seeds are a starting point for the override boxes, never a claim about the file.
            int[] counts = CategoryDefinitions.Select(definition => definition.DefaultSeed).ToArray();
            status = SaveEditorAdvancedReadStatus.NotRead("No save is selected.");

            if (!string.IsNullOrWhiteSpace(filePath))
            {
                if (!File.Exists(filePath))
                {
                    status = SaveEditorAdvancedReadStatus.NotRead("The selected save file was not found.");
                }
                else
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

                            status = SaveEditorAdvancedReadStatus.Read();
                        }
                        else
                        {
                            status = SaveEditorAdvancedReadStatus.NotRead(
                                "Kill counts were not read: " +
                                (analysis.ErrorMessage ?? "this file is not a readable career save."));
                        }
                    }
                    catch (Exception ex) when (ex is IOException or UnauthorizedAccessException or ArgumentException
                                                or NotSupportedException or InvalidDataException)
                    {
                        // Was `catch {}`. Falling through here left 100/100/25/40/20 in CurrentValue and
                        // the UI printed them in its Current column as if the save had said so; worse,
                        // GetSuggestedGlobalKillSeed then turned that fiction into the number an
                        // unchecked-category patch wrote.
                        status = SaveEditorAdvancedReadStatus.NotRead($"Kill counts could not be read: {ex.Message}");
                    }
                }
            }

            bool known = status.FileWasRead;
            return CategoryDefinitions.Select((definition, index) => new SaveCategoryKillRow
            {
                CategoryIndex = definition.CategoryIndex,
                CategoryName = definition.CategoryName,
                ThresholdLabel = definition.ThresholdLabel,
                CurrentValue = counts[index],
                CurrentValueKnown = known,
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

        /// <summary>
        /// True when the save really was read and its five categories do not all hold the same count.
        /// This is the condition under which writing one baseline over all five destroys real data, so
        /// it is what the WinUI surface uses to default "keep the counts this save already has" on.
        /// Rows whose values were never read return false: an unread seed must not drive a write.
        /// </summary>
        public static bool HasMixedKnownCategoryCounts(IReadOnlyList<SaveCategoryKillRow> rows)
        {
            if (rows.Count == 0 || rows.Any(row => !row.CurrentValueKnown))
            {
                return false;
            }

            return rows.Select(row => row.CurrentValue).Distinct().Count() > 1;
        }

        public static string BuildKillSeedSummary(IReadOnlyList<SaveCategoryKillRow> rows)
        {
            if (rows.Count == 0)
            {
                return "No save is loaded yet. This field is only the write value used for unchecked categories; it is not a cumulative score.";
            }

            if (rows.Any(row => !row.CurrentValueKnown))
            {
                return "The current kill counts were not read from a save, so the Current column shows \"-\". The value below is only the write value that would be used for unchecked categories.";
            }

            int[] counts = rows.Select(row => row.CurrentValue).ToArray();
            int baselineSeed = GetSuggestedGlobalKillSeed(rows);
            return counts.Distinct().Count() > 1
                ? $"Loaded save uses mixed category counts. \"Keep the kill counts this save already has\" was switched on so that only the categories you check below are written; clearing it writes the value below to all five, which would replace the other counts (highest current count is {baselineSeed:N0})."
                : $"Loaded save uses a shared kill value of {baselineSeed:N0} across all five categories.";
        }

        public static int CountMissionRankOverrides(IReadOnlyList<SaveMissionRankRow> rows)
        {
            return rows.Count(row => !SaveMissionRankRow.IsUseBaselineChoice(row.SelectedRank));
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
                string selected = (row.SelectedRank ?? SaveMissionRankRow.UseBaselineChoice).Trim();
                if (SaveMissionRankRow.IsUseBaselineChoice(selected))
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
