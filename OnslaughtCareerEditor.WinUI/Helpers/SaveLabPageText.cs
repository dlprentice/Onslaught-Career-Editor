namespace OnslaughtCareerEditor.WinUI.Helpers
{
    /// <summary>
    /// The sentences Save Lab and Game Options show when something fails. Kept
    /// out of the page so a raw exception cannot quietly become the explanation.
    /// </summary>
    internal static class SaveLabPageText
    {
        public const string ComparisonFailed =
            "Those files could not be compared. Nothing was changed.";

        public const string AnalysisFailed =
            "That file could not be analyzed. Nothing was changed.";

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
    }
}
