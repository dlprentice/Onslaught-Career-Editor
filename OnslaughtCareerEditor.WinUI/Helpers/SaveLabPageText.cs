using System;
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
    }
}
