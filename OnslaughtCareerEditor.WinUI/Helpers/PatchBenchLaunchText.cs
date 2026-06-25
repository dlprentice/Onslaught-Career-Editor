using System.Collections.Generic;
using OnslaughtCareerEditor.WinUI.Models;

namespace OnslaughtCareerEditor.WinUI.Helpers
{
    internal static class PatchBenchLaunchText
    {
        private const string StaleSafeCopySummary = "Prepared safe game copy is stale. Create a new safe copy to apply the current optional patch/savegame/control choices.";
        private const string StaleSafeCopyLaunchPlan = "Prepared safe copy does not match the current optional patch/savegame/control choices. Create a new safe copy before Play.";
        private const string StaleSafeCopyLaunchStatus = "Selections changed after this safe copy was created. Create a new safe copy to apply the current optional mods/savegame/control choice.";

        public static string BuildBoundary(string prefix)
        {
            return $"{prefix} This does not confirm it reached the menu, stayed windowed, rendered correctly, or played replacement music.";
        }

        public static PatchBenchLaunchReadinessTextResult BuildReadiness(PatchBenchLaunchReadinessTextState state)
        {
            if (!state.ContentMatchesCurrent)
            {
                return new PatchBenchLaunchReadinessTextResult(
                    StaleSafeCopySummary,
                    StaleSafeCopyLaunchPlan,
                    BuildBoundary(StaleSafeCopyLaunchStatus));
            }

            if (state.HasLaunchPlan && state.CommandPreview is not null)
            {
                return new PatchBenchLaunchReadinessTextResult(
                    SummaryText: null,
                    LaunchPlanText: state.CommandPreview,
                    LaunchStatusText: BuildBoundary("Safe copy ready for a guarded launch attempt."));
            }

            return new PatchBenchLaunchReadinessTextResult(
                SummaryText: null,
                LaunchPlanText: state.LaunchError ?? "Launch plan is not ready.",
                LaunchStatusText: "Safe copy launch option needs review.");
        }

        public static string BuildModifierSummary(IReadOnlyList<string> arguments)
        {
            return arguments.Count == 0
                ? "Launch modifiers: none."
                : $"Launch modifiers: {string.Join(" ", arguments)}.";
        }
    }
}
