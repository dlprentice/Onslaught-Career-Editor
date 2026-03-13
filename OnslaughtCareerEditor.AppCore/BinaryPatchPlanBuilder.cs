using System;
using System.Collections.Generic;
using System.Linq;

namespace Onslaught___Career_Editor
{
    /// <summary>
    /// Shared binary patch selection policy for both WPF and WinUI hosts.
    /// Keeps UI-specific dialogs/status separate from the actual patch-selection rules.
    /// </summary>
    public static class BinaryPatchPlanBuilder
    {
        private static readonly string[] CompanionPatchKeys =
        {
            "version_overlay_use_patched_format_pointer",
            "version_overlay_patched_format_cave_string",
        };

        private static readonly HashSet<string> s_hiddenCompanionKeys =
            new(CompanionPatchKeys, StringComparer.OrdinalIgnoreCase);

        public static IReadOnlyList<BinaryPatchSpec> GetVisibleSpecs()
        {
            return BinaryPatchEngine.PatchSpecs
                .Where(spec => !s_hiddenCompanionKeys.Contains(spec.Key))
                .ToArray();
        }

        public static IReadOnlyList<BinaryPatchSpec> BuildSelectedSpecs(IEnumerable<string> visibleSelectedKeys)
        {
            var keySet = new HashSet<string>(visibleSelectedKeys ?? Array.Empty<string>(), StringComparer.OrdinalIgnoreCase);
            var selected = BinaryPatchEngine.PatchSpecs
                .Where(spec => keySet.Contains(spec.Key))
                .ToList();

            if (selected.Count == 0)
            {
                return selected;
            }

            foreach (string companionKey in CompanionPatchKeys)
            {
                BinaryPatchSpec? spec = BinaryPatchEngine.PatchSpecs.FirstOrDefault(x =>
                    string.Equals(x.Key, companionKey, StringComparison.OrdinalIgnoreCase));
                if (spec is not null && !selected.Any(x => string.Equals(x.Key, companionKey, StringComparison.OrdinalIgnoreCase)))
                {
                    selected.Add(spec);
                }
            }

            return selected;
        }

        public static string? ValidateVisibleSelection(IEnumerable<string> visibleSelectedKeys)
        {
            var selected = GetVisibleSpecs()
                .Where(spec => (visibleSelectedKeys ?? Array.Empty<string>()).Contains(spec.Key, StringComparer.OrdinalIgnoreCase))
                .ToList();

            if (selected.Count == 0)
            {
                return "Select at least one patch first.";
            }

            bool hasExperimental = selected.Any(x => string.Equals(x.Track, "Experimental", StringComparison.OrdinalIgnoreCase));
            bool hasStable = selected.Any(x => string.Equals(x.Track, "Stable", StringComparison.OrdinalIgnoreCase));
            if (hasExperimental && !hasStable)
            {
                return "Experimental startup patch should be layered on top of the stable patch set, not applied by itself.";
            }

            return null;
        }

        public static string? BuildSelectionSignature(string? exePath, IEnumerable<string> visibleSelectedKeys)
        {
            if (string.IsNullOrWhiteSpace(exePath))
            {
                return null;
            }

            string[] keys = (visibleSelectedKeys ?? Array.Empty<string>())
                .Where(key => !string.IsNullOrWhiteSpace(key))
                .Distinct(StringComparer.OrdinalIgnoreCase)
                .OrderBy(key => key, StringComparer.OrdinalIgnoreCase)
                .ToArray();

            if (keys.Length == 0)
            {
                return null;
            }

            return exePath.Trim() + "|" + string.Join(",", keys);
        }
    }
}
