using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using OnslaughtCareerEditor.WinUI.Models;
using Onslaught___Career_Editor;

namespace OnslaughtCareerEditor.WinUI.Helpers
{
    internal static class PatchBenchSelectedProfileText
    {
        public static string BuildStatus(PatchBenchSelectedProfileTextState state)
        {
            if (state.SelectedVisibleRowCount == 0)
            {
                return "Selected profile: Enhanced Copy only. No optional visible mod rows are selected; Create safe copy still applies the required 16:9 gameplay base.";
            }

            string? matchedProfileId = state.MatchedPreset?.Id;

            if (string.Equals(matchedProfileId, BinaryPatchPlanBuilder.CompatibilityProfileId, StringComparison.OrdinalIgnoreCase))
            {
                return "Selected profile: Enhanced Copy. Required base: aspect-correct 1600x900 gameplay, windowed startup, and minimum mouse sensitivity for modern mouse aiming.";
            }

            if (string.Equals(matchedProfileId, BinaryPatchPlanBuilder.RecommendedProfileId, StringComparison.OrdinalIgnoreCase))
            {
                return "Selected profile: Windowed + Graphics Defaults. Adds launch-smoked graphics-default rows; visible graphics difference is not proven.";
            }

            if (string.Equals(matchedProfileId, BinaryPatchPlanBuilder.EnhancedPreviewProfileId, StringComparison.OrdinalIgnoreCase))
            {
                return "Selected profile: Enhanced Profile Preview. Patch rows match visible safe-copy mods; copied-options controls come from the current controls below. Not a full overhaul, online mode, or control-feel fix.";
            }

            if (string.Equals(matchedProfileId, BinaryPatchPlanBuilder.DebugCameraPreviewProfileId, StringComparison.OrdinalIgnoreCase))
            {
                return "Selected profile: Debug Camera Preview. Experimental free-camera toggle and Q-forward path; not full camera controls, gameplay safety, or online play.";
            }

            if (state.MatchedPreset is not null)
            {
                return $"Selected profile: {state.MatchedPreset.DisplayName}. Selected rows match a catalog safe-copy preset; open preset details for included changes and limits.";
            }

            if (state.IsModernGraphicsOnly)
            {
                return "Selected profile: graphics flag rows only. Use this for byte/launch checks, not as a complete compatibility profile.";
            }

            return $"Selected profile: manual patch selection with {state.SelectedVisibleRowCount} visible row(s). Create safe copy will add the required Enhanced Copy base and these selected rows.";
        }

        public static string BuildPlayerModsStatus(bool hasPatchedMarker, bool hasGoodiesPreview, bool hasLevel100TextMod)
        {
            var selected = new List<string>();
            if (hasPatchedMarker)
                selected.Add("PATCHED identity marker");
            if (hasGoodiesPreview)
                selected.Add("Goodies wall preview");
            if (hasLevel100TextMod)
                selected.Add("Level 100 English subtitle marker");

            return selected.Count == 0
                ? "Player mods selected: none."
                : $"Player mods selected: {string.Join(", ", selected)}.";
        }

        public static string BuildDetails(PatchBenchSelectedProfileTextState state)
        {
            if (state.SelectedVisibleRowCount == 0)
            {
                return "Selected safe-copy preset details: Enhanced Copy only. Included changes: verified 16:9 aspect/FOV regions, tested -res 1600 900 launch, and copied 16:9 and mouse-aim options. Restore: recreate the safe copy, restore the copied BEA.exe.original.backup, or restore copied defaultoptions.bea backup. Limits: No Host/Join or online multiplayer. No all-machine guarantee. No installed-game mutation.";
            }

            if (state.MatchedPreset is null)
            {
                return $"Selected safe-copy preset details: Manual patch selection. Included changes: {state.SelectedVisibleRowCount} visible row(s). Checks and limits: open row details for what was checked and remaining limits. Restore: restore copied BEA.exe.original.backup, restore copied defaultoptions.bea backup when options were written, or recreate the safe copy. Limits: No Host/Join or online multiplayer. No installed-game mutation.";
            }

            SafeCopyProfilePreset preset = state.MatchedPreset;
            bool isEnhancedPreview = string.Equals(preset.Id, BinaryPatchPlanBuilder.EnhancedPreviewProfileId, StringComparison.OrdinalIgnoreCase);
            var builder = new StringBuilder();
            builder.AppendLine($"Selected safe-copy preset details: {preset.DisplayName}.");
            builder.AppendLine(FormatSafeCopyProfileModules(preset, isEnhancedPreview));
            builder.AppendLine(FormatSafeCopyProfileEvidence(preset));
            builder.AppendLine(FormatSafeCopyProfileRestore(preset));
            builder.Append(FormatSafeCopyProfileLimits(preset));
            return builder.ToString();
        }

        public static string BuildAdvancedCopySelectionSummary(PatchBenchSelectedProfileTextState state)
        {
            if (state.SelectedVisibleRowCount == 0)
            {
                return "No optional mod rows selected. Safe-copy creation still applies the required Enhanced Copy base. Advanced BEA.exe-only actions need a selected row.";
            }

            string? matchedProfileId = state.MatchedPreset?.Id;

            if (string.Equals(matchedProfileId, BinaryPatchPlanBuilder.CompatibilityProfileId, StringComparison.OrdinalIgnoreCase))
            {
                return BuildAdvancedCopyDestinationSummary("Enhanced Copy profile selected.");
            }

            if (string.Equals(matchedProfileId, BinaryPatchPlanBuilder.RecommendedProfileId, StringComparison.OrdinalIgnoreCase))
            {
                return BuildAdvancedCopyDestinationSummary("Windowed + Graphics Defaults profile selected.");
            }

            if (string.Equals(matchedProfileId, BinaryPatchPlanBuilder.EnhancedPreviewProfileId, StringComparison.OrdinalIgnoreCase))
            {
                return BuildAdvancedCopyDestinationSummary("Enhanced Profile Preview selected. Patch rows match visible safe-copy mods, not a full overhaul or online mode. It pre-fills copied-options controls for config 1, 16:9, and minimum mouse sensitivity; the control-options manifest records the applied values.");
            }

            if (string.Equals(matchedProfileId, BinaryPatchPlanBuilder.DebugCameraPreviewProfileId, StringComparison.OrdinalIgnoreCase))
            {
                return BuildAdvancedCopyDestinationSummary("Debug Camera Preview selected. It adds an experimental free-camera toggle and one Q-forward remap path, not full camera controls or gameplay safety.");
            }

            if (state.IsModernGraphicsOnly)
            {
                return BuildAdvancedCopyDestinationSummary("Extra graphics gate defaults preset selected.");
            }

            return BuildAdvancedCopyDestinationSummary($"{state.SelectedVisibleRowCount} visible patch(es) selected.");
        }

        private static string BuildAdvancedCopyDestinationSummary(string prefix)
        {
            return $"{prefix} Selected mods are applied when you create the safe game copy. The advanced buttons below patch a separate BEA.exe-only copy and do not create a launchable game folder.";
        }

        private static string FormatSafeCopyProfileModules(SafeCopyProfilePreset preset, bool isEnhancedPreview)
        {
            string[] names = preset.Modules
                .Select(module => FormatSafeCopyProfileModuleName(module))
                .Where(name => !string.IsNullOrWhiteSpace(name))
                .Distinct(StringComparer.OrdinalIgnoreCase)
                .ToArray();

            string prefix = isEnhancedPreview
                ? "Patch rows match Enhanced Profile Preview; copied-options controls come from the current controls below. Control defaults apply only while P1/P2 config 1, screen shape 1, minimum mouse sensitivity, and invert settings still match the preset. Modules: "
                : "Modules: ";
            return names.Length == 0
                ? $"{prefix}none listed; use row details for selected patch evidence."
                : $"{prefix}{string.Join("; ", names)}.";
        }

        private static string FormatSafeCopyProfileModuleName(SafeCopyProfileModule module)
        {
            return string.Equals(module.Id, "copied-options-control-defaults", StringComparison.OrdinalIgnoreCase)
                ? "Copied-options controls (current UI selections; preset defaults only if unchanged)"
                : module.DisplayName;
        }

        private static string FormatSafeCopyProfileEvidence(SafeCopyProfilePreset preset)
        {
            string[] refs = preset.Modules
                .SelectMany(module => module.EvidenceRefs)
                .Where(reference => !string.IsNullOrWhiteSpace(reference))
                .Distinct(StringComparer.OrdinalIgnoreCase)
                .Take(4)
                .ToArray();

            return refs.Length == 0
                ? "Evidence: no catalog refs listed; use row details before treating this preset as proven."
                : $"Evidence: {string.Join("; ", refs)}.";
        }

        private static string FormatSafeCopyProfileRestore(SafeCopyProfilePreset preset)
        {
            string[] restoreStrategies = preset.Modules
                .Select(module => module.RestoreStrategy)
                .Where(strategy => !string.IsNullOrWhiteSpace(strategy))
                .Distinct(StringComparer.OrdinalIgnoreCase)
                .Take(4)
                .ToArray();

            return restoreStrategies.Length == 0
                ? "Restore: restore copied BEA.exe.original.backup, restore copied defaultoptions.bea backup when options were written, or recreate the safe copy."
                : $"Restore: {string.Join("; ", restoreStrategies)}.";
        }

        private static string FormatSafeCopyProfileLimits(SafeCopyProfilePreset preset)
        {
            var limits = preset.Modules
                .SelectMany(module => module.NonClaims)
                .Where(nonClaim => !string.IsNullOrWhiteSpace(nonClaim))
                .Distinct(StringComparer.OrdinalIgnoreCase)
                .ToList();
            AddLimitIfMissing(limits, "No Host/Join or online multiplayer.");
            AddLimitIfMissing(limits, "No installed-game mutation.");

            return $"Limits: {string.Join(" ", limits.Take(8))}";
        }

        private static void AddLimitIfMissing(List<string> limits, string requiredLimit)
        {
            if (!limits.Any(limit => string.Equals(limit.Trim(), requiredLimit, StringComparison.OrdinalIgnoreCase)))
            {
                limits.Add(requiredLimit);
            }
        }
    }
}
