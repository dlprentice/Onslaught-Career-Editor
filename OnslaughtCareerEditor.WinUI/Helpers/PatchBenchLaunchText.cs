using System.Collections.Generic;
using System.IO;
using OnslaughtCareerEditor.WinUI.Models;

namespace OnslaughtCareerEditor.WinUI.Helpers
{
    internal static class PatchBenchLaunchText
    {
        private const string StaleSafeCopySummary = "Prepared safe game copy is stale. Create a new safe copy to apply the current optional patch/savegame/control choices.";
        private const string StaleSafeCopyLaunchPlan = "Prepared safe copy does not match the current optional patch/savegame/control choices. Create a new safe copy before Play.";
        private const string StaleSafeCopyLaunchStatus = "Selections changed after this safe copy was created. Create a new safe copy to apply the current optional mods/savegame/control choice.";
        private const string LaunchPlanNextStep = "Create a new safe copy before Play.";

        public const string NoActiveCopiedGame = "Launch a safe copy first.";

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
                LaunchPlanText: state.LaunchError ?? LaunchPlanNextStep,
                LaunchStatusText: LaunchPlanNextStep);
        }

        public static string BuildModifierSummary(IReadOnlyList<string> arguments)
        {
            return arguments.Count == 0
                ? "Launch modifiers: none."
                : $"Launch modifiers: {string.Join(" ", arguments)}.";
        }

        /// <summary>
        /// The launch question names the copy folder. The working-directory
        /// path does not belong in the confirmation.
        /// </summary>
        public static string BuildLaunchConfirmation(string? workingDirectory, string modifierSummary)
        {
            string name = FolderLeaf(workingDirectory, "this safe copy");
            return
                "The app will launch BEA.exe from the safe game copy only." +
                Environment.NewLine + Environment.NewLine +
                "Safe copy: " + name +
                Environment.NewLine +
                modifierSummary +
                Environment.NewLine + Environment.NewLine +
                "The Steam/game install stays unchanged. The game may take focus, switch display modes, fail to start, or exit. Any manual input after launch is not counted as automated proof.";
        }

        private static string FolderLeaf(string? path, string fallback)
        {
            if (string.IsNullOrWhiteSpace(path))
            {
                return fallback;
            }

            string name = Path.GetFileName(Path.TrimEndingDirectorySeparator(path.Trim()));
            return string.IsNullOrWhiteSpace(name) ? fallback : name;
        }
    }
}
