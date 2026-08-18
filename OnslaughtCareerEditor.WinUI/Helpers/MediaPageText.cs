namespace OnslaughtCareerEditor.WinUI.Helpers
{
    /// <summary>
    /// The sentences Media shows when something fails. Kept out of the page so a
    /// raw exception cannot quietly become the player-facing explanation again.
    /// </summary>
    internal static class MediaPageText
    {
        public const string LoadFailureMessage =
            "Nothing was changed. Check the game folder is reachable, then try again.";

        public const string InlineVideoUnavailableBody =
            "The inline player could not start. Try another video, or check that the media files are intact.";

        public const string AudioPlaybackFailedStatus =
            "Media: this audio track could not be played";

        public const string VideoPlaybackFailedStatus =
            "Media: this video could not be played";

        public const string StoryStartFailedStatus =
            "Media: the story could not start";

        public const string StoryContinueFailedStatus =
            "Media: the next cutscene could not be played";
    }
}
