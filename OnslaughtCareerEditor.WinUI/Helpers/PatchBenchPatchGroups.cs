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
                    groups.Add(new BinaryPatchGroupModel(title, description, groupItems));
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
                "Menu background color choices for the safe copy. Choose only one color preset at a time; these affect frontend clear-screen backgrounds, not textures, fonts, or HUD colors.");
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
    }
}
