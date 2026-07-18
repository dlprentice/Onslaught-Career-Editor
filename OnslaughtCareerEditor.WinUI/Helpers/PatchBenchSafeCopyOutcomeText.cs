using OnslaughtCareerEditor.WinUI.Models;

namespace OnslaughtCareerEditor.WinUI.Helpers
{
    internal static class PatchBenchSafeCopyOutcomeText
    {
        public const string HostJoinReceiptBoundary = "No Host/Join or online multiplayer";
        private const string MusicPlaybackBoundary = "in-game playback is still experimental and unproven";
        private const string MusicPlaybackBoundaryClause = MusicPlaybackBoundary + ".";
        private static string MusicPlaybackBoundarySentence => char.ToUpperInvariant(MusicPlaybackBoundary[0]) + MusicPlaybackBoundary[1..] + ".";

        public static string BuildDefaultMusicReplacementStatus()
        {
            return $"No music swap staged. Staging only; {MusicPlaybackBoundaryClause}";
        }

        public static string BuildCanceledSummary()
        {
            return "Safe copy creation canceled.";
        }

        public static string BuildCanceledOperationLog()
        {
            return "Safe copy creation canceled before any copy or patch operation started.";
        }

        public static string BuildFailedSummary()
        {
            return "Safe game copy preparation failed.";
        }

        public static string BuildFailedReceipt()
        {
            return "Safe copy preparation failed before a receipt could be written. The installed game was not changed.";
        }

        public static string BuildRestoredTrackedLaunchSummary()
        {
            return "A safe copy process from this app launch record is still tracked.";
        }

        public static string BuildRestoredTrackedLaunchReceipt()
        {
            return "Tracked safe-copy process restored from the app launch record. Create a new safe copy to write a fresh receipt for the current selections.";
        }

        public static string BuildRestoredTrackedLaunchStatus()
        {
            return "A safe-copy BEA.exe process launched by this app is still tracked from a saved app launch record. Stop it before preparing or launching another safe copy.";
        }

        public static string BuildSourceChangedSummary(bool hasTrackedSafeCopyLaunch)
        {
            return hasTrackedSafeCopyLaunch
                ? "Source changed while a safe copy process is still tracked."
                : "No safe game copy prepared in this session.";
        }

        public static string BuildSourceChangedReceipt(bool hasTrackedSafeCopyLaunch)
        {
            return hasTrackedSafeCopyLaunch
                ? "Source changed while a safe copy process is still tracked. Stop it and create a new safe copy to write a fresh receipt."
                : "Create a safe copy to see the exact profile, included changes, launch modifiers, savegame/music/control choices, and limits.";
        }

        public static string BuildSourceChangedLaunchStatus(bool hasTrackedSafeCopyLaunch)
        {
            return hasTrackedSafeCopyLaunch
                ? "A safe copy process is still tracked. Stop it before preparing another safe copy."
                : PatchBenchLaunchText.BuildBoundary("No safe copy launch attempted.");
        }

        public static string BuildPreparedSummary(PatchBenchSafeCopyOutcomeTextState state)
        {
            return
                "Safe game copy prepared. Required and selected patch verification passed on the copied BEA.exe. " +
                "The selected Steam/game install stays unchanged.\n" +
                BuildSavegamesSummary(state.CopiedSavegames) + "\n" +
                BuildControlOptionsSummary(state.ControlOptions) + "\n" +
                BuildLevel100TextModSummary(state.Level100TextModApplied) + "\n" +
                BuildLevel100EarlyFlightModSummary(state.Level100EarlyFlightModApplied) + "\n" +
                BuildMusicSwapSummary(state.MusicSwap) + "\n" +
                $"Play will run BEA.exe from safe copy folder: {state.SafeCopyFolderName}";
        }

        public static string BuildPreparedOperationLog(PatchBenchSafeCopyOutcomeTextState state)
        {
            return
                "Safe game copy preparation complete.\n" +
                $"Files copied: {state.FilesCopied}\n" +
                $"Patches applied: {state.PatchDisplayList}\n" +
                state.LaunchModifierSummary + "\n" +
                BuildSavegamesSummary(state.CopiedSavegames) + "\n" +
                BuildControlOptionsSummary(state.ControlOptions) + "\n" +
                BuildLevel100TextModSummary(state.Level100TextModApplied) + "\n" +
                BuildLevel100EarlyFlightModSummary(state.Level100EarlyFlightModApplied) + "\n" +
                BuildMusicSwapSummary(state.MusicSwap) + "\n" +
                "Only files inside the safe copy were changed; no game process was started.";
        }

        public static string BuildMusicReplacementStatus(PatchBenchSafeCopyMusicSwapTextState? musicSwap)
        {
            return musicSwap is null
                ? $"Safe copy ready for music replacement staging. Staging only; {MusicPlaybackBoundaryClause}"
                : $"Safe-copy track swap staged for {musicSwap.TargetMusicFileName}. Restore before staging another swap. {MusicPlaybackBoundarySentence}";
        }

        public static string BuildMusicSwapInputsMissingStatus()
        {
            return "Prepare a safe game copy and select two safe-copy tracks before staging a swap.";
        }

        public static string BuildMusicPresetMissingSafeCopyStatus()
        {
            return "Prepare a safe game copy before staging a music preset.";
        }

        public static string BuildMusicPresetFailedStatus()
        {
            return "Safe-copy music preset staging failed.";
        }

        public static string BuildMusicStagingBlockedStatus()
        {
            return "Stop the managed safe copy before staging copied music bytes.";
        }

        public static string BuildMusicStagingMissingSafeCopyStatus()
        {
            return "Prepare a safe game copy before staging copied music bytes.";
        }

        public static string BuildMusicStagingProgressStatus(bool copiedTrackSwap)
        {
            return copiedTrackSwap
                ? "Staging safe-copy music swap..."
                : "Staging copied music bytes...";
        }

        public static string BuildMusicStagedStatus(string targetMusicFileName, bool copiedTrackSwap)
        {
            return copiedTrackSwap
                ? $"Safe-copy track swap staged for {targetMusicFileName}. Staging only; {MusicPlaybackBoundaryClause}"
                : $"Copied music bytes staged for {targetMusicFileName}. Staging only; {MusicPlaybackBoundaryClause}";
        }

        public static string BuildMusicStagingFailedStatus()
        {
            return "Copied music byte staging failed.";
        }

        public static string BuildMusicRestoreBlockedStatus()
        {
            return "Stop the managed safe copy before restoring music backup.";
        }

        public static string BuildMusicRestoreMissingSafeCopyStatus()
        {
            return "Prepare a safe game copy before restoring music backup.";
        }

        public static string BuildMusicRestoreProgressStatus()
        {
            return "Restoring safe-copy music backup...";
        }

        public static string BuildMusicRestoreResultStatus(string targetMusicFileName, bool success)
        {
            return success
                ? $"Music backup restored for {targetMusicFileName}. Staging only; {MusicPlaybackBoundaryClause}"
                : "Safe-copy music backup was not restored.";
        }

        public static string BuildMusicRestoreFailedStatus()
        {
            return "Safe-copy music backup restore failed.";
        }

        private static string BuildSavegamesSummary(bool copiedSavegames)
        {
            return copiedSavegames
                ? "Savegames: copied into the safe game copy only; source savegames remain read-only."
                : "Savegames: not copied into this safe copy.";
        }

        private static string BuildControlOptionsSummary(PatchBenchSafeCopyControlOptionsTextState? controlOptions)
        {
            return controlOptions is null
                ? "Control options: no safe-copy defaultoptions.bea control preset applied."
                : $"Control options: safe-copy screen shape {controlOptions.ScreenShape} (1=16:9); mouse sensitivity {controlOptions.MouseSensitivity:0.###}; controller config P1={controlOptions.ControllerConfigP1}, P2={controlOptions.ControllerConfigP2}; invert walker Y P1/P2={FormatBool(controlOptions.InvertWalkerP1)}/{FormatBool(controlOptions.InvertWalkerP2)}; invert flight Y P1/P2={FormatBool(controlOptions.InvertFlightP1)}/{FormatBool(controlOptions.InvertFlightP2)}; runtime behavior still needs this copy's Play check.";
        }

        private static string BuildMusicSwapSummary(PatchBenchSafeCopyMusicSwapTextState? musicSwap)
        {
            return musicSwap is null
                ? "Music swap: no copied-track swap staged during safe-copy creation."
                : $"Music swap: copied-track swap staged for {musicSwap.TargetMusicFileName}; backup {musicSwap.BackupRelativePath}; runtime playback still needs live testing.";
        }

        private static string BuildLevel100TextModSummary(bool applied)
        {
            return applied
                ? "Level 100 text: one fixed-size English TUTORIAL_01 marker staged and hash-verified in the safe copy."
                : "Level 100 text: original English subtitle retained.";
        }

        private static string BuildLevel100EarlyFlightModSummary(bool applied)
        {
            return applied
                ? "Level 100 gameplay: early transformation staged from one verified compiled-script command in the safe copy."
                : "Level 100 gameplay: original tutorial transformation gate retained.";
        }

        private static string FormatBool(bool value)
        {
            return value ? "on" : "off";
        }
    }
}
