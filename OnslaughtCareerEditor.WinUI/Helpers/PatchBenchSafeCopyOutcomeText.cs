using OnslaughtCareerEditor.WinUI.Models;

namespace OnslaughtCareerEditor.WinUI.Helpers
{
    internal static class PatchBenchSafeCopyOutcomeText
    {
        public static string BuildPreparedSummary(PatchBenchSafeCopyOutcomeTextState state)
        {
            return
                "Safe game copy prepared. Required and selected patch verification passed on the copied BEA.exe. " +
                "The selected Steam/game install stays unchanged.\n" +
                BuildSavegamesSummary(state.CopiedSavegames) + "\n" +
                BuildControlOptionsSummary(state.ControlOptions) + "\n" +
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
                BuildMusicSwapSummary(state.MusicSwap) + "\n" +
                "Only the copied BEA.exe was patched; no game process was started.";
        }

        public static string BuildMusicReplacementStatus(PatchBenchSafeCopyMusicSwapTextState? musicSwap)
        {
            return musicSwap is null
                ? "Safe copy ready for music replacement staging. Staging only; in-game playback is still experimental and unproven."
                : $"Safe-copy track swap staged for {musicSwap.TargetMusicFileName}. Restore before staging another swap. In-game playback is still experimental and unproven.";
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
                : $"Control options: safe-copy mouse sensitivity {controlOptions.MouseSensitivity:0.###}; controller config P1={controlOptions.ControllerConfigP1}, P2={controlOptions.ControllerConfigP2}; invert walker Y P1/P2={FormatBool(controlOptions.InvertWalkerP1)}/{FormatBool(controlOptions.InvertWalkerP2)}; invert flight Y P1/P2={FormatBool(controlOptions.InvertFlightP1)}/{FormatBool(controlOptions.InvertFlightP2)}; runtime feel still needs live testing.";
        }

        private static string BuildMusicSwapSummary(PatchBenchSafeCopyMusicSwapTextState? musicSwap)
        {
            return musicSwap is null
                ? "Music swap: no copied-track swap staged during safe-copy creation."
                : $"Music swap: copied-track swap staged for {musicSwap.TargetMusicFileName}; backup {musicSwap.BackupRelativePath}; runtime playback still needs live testing.";
        }

        private static string FormatBool(bool value)
        {
            return value ? "on" : "off";
        }
    }
}
