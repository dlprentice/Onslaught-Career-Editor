using System;
using System.Collections.Generic;
using System.Linq;
using OnslaughtCareerEditor.AppCore;

namespace OnslaughtCareerEditor.WinUI.Helpers
{
    /// <summary>
    /// The sentences Save Lab and Game Options show when something fails. Kept
    /// out of the page so a raw exception cannot quietly become the explanation.
    /// </summary>
    internal static class SaveLabPageText
    {
        public const string ComparisonFailed = SaveAnalyzerService.ComparisonFailed;

        public const string AnalysisFailed = SaveAnalyzerService.AnalysisFailed;

        public const string AnalysisNeedsAFile =
            "Choose a valid .bes or .bea file before running analysis.";

        public const string BrowseOptionsFailed =
            "Could not browse for an options file. Nothing was changed.";

        public const string ChooseOutputFailed =
            "Could not choose an output folder. Nothing was changed.";

        public const string BrowseCopySourceFailed =
            "Could not browse for a copy-source file. Nothing was changed.";

        public const string LoadKeybindsFailed =
            "Could not load keybinds from that file. Nothing was changed.";

        public const string InputNotReady =
            "That options file is not ready. Choose a valid defaultoptions.bea.";

        public const string PatchFailed =
            "Game options patch failed. Nothing was changed.";

        public const string SafeCopyInstallFailed =
            "Could not put that save in the safe copy. Nothing was changed.";

        public const string SaveEditorPatchFailed =
            "Could not write that career save. Nothing was changed.";

        /// <summary>
        /// A Save Editor write refusal. Named here so the page never paints a
        /// redacted <c>PatchResult.Message</c> that still carries a dump.
        /// </summary>
        public static string DescribeEditorPatchFailure(string? message)
        {
            if (string.IsNullOrWhiteSpace(message) || LooksLikeAPathOrDump(message))
                return SaveEditorPatchFailed;

            return message;
        }

        /// <summary>
        /// A Game Options write refusal. Named here so the page never paints a
        /// redacted <c>PatchResult.Message</c> that still carries a dump.
        /// </summary>
        public static string DescribeConfigurationPatchFailure(string? message)
        {
            if (string.IsNullOrWhiteSpace(message) || LooksLikeAPathOrDump(message))
                return PatchFailed;

            return message;
        }

        private static bool LooksLikeAPathOrDump(string message)
        {
            return message.Contains(":\\", StringComparison.Ordinal)
                || message.Contains(":/", StringComparison.Ordinal)
                || message.Contains("Win32", StringComparison.OrdinalIgnoreCase)
                || message.Contains("exception", StringComparison.OrdinalIgnoreCase);
        }

        /// <summary>
        /// Null when the write may proceed. Same classifier and sentence as Cheats
        /// and Save Rescue, so an output path cannot become a second walk.
        /// </summary>
        public static string? DescribeOutputRefusal(string? outputPath)
        {
            return CareerSaveLocation.ClassifyExisting(outputPath) == CareerSaveLocationKind.InstalledGame
                ? CareerSaveLocation.InstalledDestinationRefused
                : null;
        }

        public const string OverwriteCanceled =
            "That file was left as it is. Nothing was changed.";

        /// <summary>
        /// Same question Cheats already asks. The leaf name is enough; a full
        /// path does not belong in the confirmation.
        /// </summary>
        public static string BuildOverwriteQuestion(string? outputPath)
        {
            string fileName = Path.GetFileName((outputPath ?? string.Empty).Trim());
            if (string.IsNullOrWhiteSpace(fileName))
            {
                fileName = "That file";
            }

            return CheatsPageText.BuildOverwriteQuestion(fileName);
        }

        /// <summary>
        /// What this save already has for the focused Goodie. Shown next to the
        /// write controls so a player can see the dword they are about to replace.
        /// </summary>
        public static string DescribeFocusedGoodieCurrent(int goodieId, MissionScriptGoodieState state)
        {
            return $"This save has Goodie {goodieId:000} as {MissionScriptGoodieStateSaveCodec.GetStateLabel(state)}.";
        }

        public const string FocusedGoodieCurrentUnreadable =
            "This save's current Goodie state could not be read.";

        /// <summary>
        /// What this save already has for the listed missions. Shown next to
        /// the Mission rank baseline so setting S is replacing named grades
        /// rather than a blind wall. The per-mission Current column still
        /// owns the row detail.
        /// </summary>
        public static string DescribeMissionRanksCurrent(IReadOnlyList<SaveMissionRankRow>? rows)
        {
            if (rows is null || rows.Count == 0)
            {
                return MissionRanksCurrentUnreadable;
            }

            Dictionary<string, int> counts = new(StringComparer.Ordinal);
            foreach (SaveMissionRankRow row in rows)
            {
                string? label = ClassifyListedMissionRank(row.CurrentRank);
                if (label is null)
                {
                    continue;
                }

                counts[label] = counts.TryGetValue(label, out int n) ? n + 1 : 1;
            }

            if (counts.Count == 0)
            {
                return MissionRanksCurrentUnreadable;
            }

            if (counts.Count == 1)
            {
                (string label, int n) = counts.First();
                if (n == rows.Count && IsExactListedGrade(label))
                {
                    return $"This save has every listed mission at {label}.";
                }
            }

            string[] parts = ListedGradeOrder
                .Where(counts.ContainsKey)
                .Select(label => $"{counts[label]} {label}")
                .ToArray();
            if (parts.Length == 0)
            {
                return MissionRanksCurrentUnreadable;
            }

            return $"This save's missions are {JoinReadable(parts)}.";
        }

        public const string MissionRanksCurrentUnreadable =
            "This save's mission grades could not be read.";

        private static readonly string[] ListedGradeOrder =
        {
            "S", "A", "B", "C", "D", "E", "No Grade",
            "near S", "near A", "near B", "near C", "near D", "near E",
            "unrecognized"
        };

        private static bool IsExactListedGrade(string label) =>
            label is "S" or "A" or "B" or "C" or "D" or "E" or "No Grade";

        private static string? ClassifyListedMissionRank(string? current)
        {
            string trimmed = (current ?? string.Empty).Trim();
            if (trimmed.Length == 0 || trimmed == "-")
            {
                return null;
            }

            if (trimmed.Equals("NONE", StringComparison.OrdinalIgnoreCase))
            {
                return "No Grade";
            }

            foreach (string grade in new[] { "S", "A", "B", "C", "D", "E" })
            {
                if (trimmed.Equals(grade, StringComparison.OrdinalIgnoreCase))
                {
                    return grade;
                }
            }

            if (trimmed.StartsWith("~", StringComparison.Ordinal)
                && trimmed.Length >= 2
                && "SABCDE".Contains(char.ToUpperInvariant(trimmed[1])))
            {
                return $"near {char.ToUpperInvariant(trimmed[1])}";
            }

            return "unrecognized";
        }

        private static string JoinReadable(IReadOnlyList<string> values)
        {
            return values.Count switch
            {
                0 => string.Empty,
                1 => values[0],
                2 => $"{values[0]} and {values[1]}",
                _ => string.Join(", ", values.Take(values.Count - 1)) + " and " + values[^1],
            };
        }
    }
}
