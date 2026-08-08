using System;
using System.Collections.Generic;
using System.Linq;
using OnslaughtCareerEditor.AppCore;

namespace OnslaughtCareerEditor.WinUI.Helpers
{
    /// <summary>
    /// Carries the user's advanced Save Editor overrides across an input reload.
    ///
    /// The advanced surface reloads its rows from the selected input save whenever the input path
    /// changes, which includes every keystroke in the input path box. Rebuilding the rows from the
    /// file discards every per-mission rank and per-category kill override the user had configured,
    /// with no warning, no undo, and a success-shaped UI. These helpers re-apply the user's own
    /// choices onto the freshly-read rows so a reload refreshes what the file says without ever
    /// throwing away what the user said.
    ///
    /// The returned counts let the page report a carry-over instead of performing it silently.
    /// </summary>
    internal static class SaveEditorAdvancedOverrideCarryOver
    {
        /// <summary>
        /// Re-apply every mission rank selection that is an actual override (i.e. not the
        /// "use baseline" sentinel) from <paramref name="previousRows"/> onto the
        /// matching node index in <paramref name="reloadedRows"/>. Returns the number carried over.
        /// </summary>
        internal static int ApplyMissionRankOverrides(
            IReadOnlyList<SaveMissionRankRow>? previousRows,
            IReadOnlyList<SaveMissionRankRow>? reloadedRows)
        {
            if (previousRows is null || reloadedRows is null || previousRows.Count == 0 || reloadedRows.Count == 0)
            {
                return 0;
            }

            Dictionary<int, SaveMissionRankRow> byNodeIndex = new();
            foreach (SaveMissionRankRow row in reloadedRows)
            {
                byNodeIndex[row.NodeIndexZeroBased] = row;
            }

            int carried = 0;
            foreach (SaveMissionRankRow previous in previousRows)
            {
                string selected = (previous.SelectedRank ?? SaveMissionRankRow.UseBaselineChoice).Trim();
                if (SaveMissionRankRow.IsUseBaselineChoice(selected))
                {
                    continue;
                }

                if (!byNodeIndex.TryGetValue(previous.NodeIndexZeroBased, out SaveMissionRankRow? target))
                {
                    continue;
                }

                if (!target.RankChoices.Contains(selected, StringComparer.OrdinalIgnoreCase))
                {
                    continue;
                }

                target.SelectedRank = selected;
                carried++;
            }

            return carried;
        }

        /// <summary>
        /// Re-apply every enabled per-category kill override from <paramref name="previousRows"/> onto the
        /// matching category in <paramref name="reloadedRows"/>. Returns the number carried over.
        /// </summary>
        internal static int ApplyCategoryKillOverrides(
            IReadOnlyList<SaveCategoryKillRow>? previousRows,
            IReadOnlyList<SaveCategoryKillRow>? reloadedRows)
        {
            if (previousRows is null || reloadedRows is null || previousRows.Count == 0 || reloadedRows.Count == 0)
            {
                return 0;
            }

            Dictionary<int, SaveCategoryKillRow> byCategory = new();
            foreach (SaveCategoryKillRow row in reloadedRows)
            {
                byCategory[row.CategoryIndex] = row;
            }

            int carried = 0;
            foreach (SaveCategoryKillRow previous in previousRows)
            {
                if (!previous.OverrideEnabled)
                {
                    continue;
                }

                if (!byCategory.TryGetValue(previous.CategoryIndex, out SaveCategoryKillRow? target))
                {
                    continue;
                }

                target.OverrideValue = previous.OverrideValue;
                target.OverrideEnabled = true;
                carried++;
            }

            return carried;
        }

        /// <summary>
        /// The global kill value box is re-seeded from the loaded save. Re-seeding a value the user typed
        /// themselves silently replaces their write value, so only an untouched auto-seeded box may be
        /// re-seeded. This mirrors the output-path provenance rule already used by the editor.
        /// </summary>
        internal static bool ShouldReseedGlobalKillValue(bool hasValidInput, bool currentValueWasAutoSeeded)
        {
            return hasValidInput && currentValueWasAutoSeeded;
        }

        /// <summary>
        /// One-line status describing what a reload carried across, so the carry-over is visible rather
        /// than assumed. Returns null when there was nothing to carry.
        /// </summary>
        internal static string? DescribeCarryOver(int missionRankOverrides, int categoryKillOverrides)
        {
            if (missionRankOverrides <= 0 && categoryKillOverrides <= 0)
            {
                return null;
            }

            List<string> parts = new();
            if (missionRankOverrides > 0)
            {
                parts.Add(missionRankOverrides == 1
                    ? "1 mission rank override"
                    : $"{missionRankOverrides} mission rank overrides");
            }

            if (categoryKillOverrides > 0)
            {
                parts.Add(categoryKillOverrides == 1
                    ? "1 category kill override"
                    : $"{categoryKillOverrides} category kill overrides");
            }

            return "Kept " + string.Join(" and ", parts) +
                   " from the previous selection. Current values below were re-read from the selected save.";
        }
    }
}
