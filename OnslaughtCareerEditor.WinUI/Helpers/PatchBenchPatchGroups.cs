using System;
using System.Collections.Generic;
using System.Linq;
using OnslaughtCareerEditor.WinUI.Models;

namespace OnslaughtCareerEditor.WinUI.Helpers
{
    internal static class PatchBenchPatchGroups
    {
        public static List<BinaryPatchGroupModel> Build(IEnumerable<BinaryPatchItemModel> items)
        {
            List<BinaryPatchItemModel> itemList = items.ToList();
            var groups = new List<BinaryPatchGroupModel>();

            void AddGroup(string title, string description)
            {
                List<BinaryPatchItemModel> groupItems = itemList
                    .Where(item => string.Equals(item.FunctionalArea, title, StringComparison.OrdinalIgnoreCase))
                    .ToList();
                if (groupItems.Count > 0)
                {
                    groups.Add(new BinaryPatchGroupModel(title, description, BuildScanSummary(groupItems), groupItems));
                }
            }

            AddGroup(
                "Display & Startup",
                "Windowed startup, wider display-mode acceptance, and the optional fullscreen fallback all live together here.");
            AddGroup(
                "Graphics & Hardware Overrides",
                "Use these when you want the safe copy to use executable defaults instead of legacy GPU override rules.");
            AddGroup(
                "Frontend Color Mods",
                "Frontend margin color choices for the safe copy. Choose only one preset at a time; accepted checks cover bounded clear-screen margins, not every menu background, texture, font, or HUD color.");
            AddGroup(
                "Goodies Gallery Mods",
                "Opt-in Goodies gallery display changes for the safe copy. These do not edit saves or permanently award Goodies.");
            AddGroup(
                "Debug Camera Mods",
                "Experimental debug-camera changes for safe copies only. These may be unstable; open Details on a row for exactly what has been tested.");
            AddGroup(
                "Controls & Pause",
                "Experimental safe-copy control changes. Open Details on a row for tested behavior, remaining limits, and proof notes.");
            AddGroup(
                "UI & Diagnostics",
                "Small visible markers and diagnostics that make a modded safe copy easier to recognize.");

            string[] missingGroups = itemList
                .Select(item => item.FunctionalArea)
                .Distinct(StringComparer.OrdinalIgnoreCase)
                .Where(area => !groups.Any(group => string.Equals(group.Title, area, StringComparison.OrdinalIgnoreCase)))
                .ToArray();
            if (missingGroups.Length > 0)
            {
                throw new InvalidOperationException($"Patch Bench has visible patch rows without a rendered group: {string.Join(", ", missingGroups)}");
            }

            return groups;
        }

        private static string BuildScanSummary(IReadOnlyCollection<BinaryPatchItemModel> groupItems)
        {
            int experimentalCount = groupItems.Count(item =>
                string.Equals(item.Spec.Track, "Experimental", StringComparison.OrdinalIgnoreCase));
            int otherTrackCount = groupItems.Count(item =>
                !string.Equals(item.Spec.Track, "Stable", StringComparison.OrdinalIgnoreCase) &&
                !string.Equals(item.Spec.Track, "Experimental", StringComparison.OrdinalIgnoreCase));
            string optionLabel = groupItems.Count == 1 ? "option" : "options";
            var trackSummaries = new List<string>();
            if (experimentalCount == groupItems.Count)
            {
                trackSummaries.Add("all experimental");
            }
            else if (experimentalCount > 0)
            {
                trackSummaries.Add($"{experimentalCount} experimental");
            }

            if (otherTrackCount > 0)
            {
                string otherLabel = otherTrackCount == 1 ? "other track" : "other tracks";
                trackSummaries.Add($"{otherTrackCount} {otherLabel}");
            }

            string trackSummary = trackSummaries.Count == 0
                ? string.Empty
                : experimentalCount == groupItems.Count && otherTrackCount == 0
                    ? ", all experimental"
                    : $", including {string.Join(" and ", trackSummaries)}";

            return $"Visible rows: {groupItems.Count} {optionLabel}{trackSummary}. " +
                "Copied targets only; installed game stays read-only. " +
                "Open row details for checks and remaining limits.";
        }
    }
}
