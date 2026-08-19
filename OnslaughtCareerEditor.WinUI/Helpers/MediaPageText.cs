using System.IO;

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

        public const string AudioPlaybackFailedBody =
            "This audio track could not be played. Try another one, or check that the media files are intact.";

        public const string VideoPlaybackFailedStatus =
            "Media: this video could not be played";

        public const string VideoPlaybackFailedBody =
            "This video could not be played. Try another one, or check that the media files are intact.";

        public const string DedicatedPlayerInitFailed =
            "The video player could not start. Nothing was changed.";

        public const string StoryStartFailedStatus =
            "Media: the story could not start";

        public const string StoryContinueFailedStatus =
            "Media: the next cutscene could not be played";

        public const string EmptySearchNextStep =
            "Try another word, or clear the search.";

        public const string EmptyLibraryNextStep =
            "Check the game folder still has its media files, or choose another folder.";

        public const string GameFolderNotConfigured =
            "Game install not configured. Choose Settings or Browse Game Folder.";

        public static string DescribeAudioEmptyState(bool hasGameDirectory, string? search)
        {
            if (!hasGameDirectory)
            {
                return GameFolderNotConfigured;
            }

            return string.IsNullOrWhiteSpace(search)
                ? EmptyLibraryNextStep
                : EmptySearchNextStep;
        }

        public static string DescribeVideoEmptyState(bool hasGameDirectory, string? search)
        {
            if (!hasGameDirectory)
            {
                return GameFolderNotConfigured;
            }

            return string.IsNullOrWhiteSpace(search)
                ? EmptyLibraryNextStep
                : EmptySearchNextStep;
        }

        /// <summary>
        /// Folder cards name the last path segment. The full path stays off the page.
        /// </summary>
        public static string BuildFolderSummary(string? path, string fallback)
        {
            if (string.IsNullOrWhiteSpace(path))
            {
                return fallback;
            }

            string trimmed = path.TrimEnd(Path.DirectorySeparatorChar, Path.AltDirectorySeparatorChar);
            string name = Path.GetFileName(trimmed);
            return string.IsNullOrWhiteSpace(name) ? fallback : name;
        }

        /// <summary>
        /// Selected audio and video name the file, not the folder it sits in.
        /// </summary>
        public static string BuildFileName(string? path, string fallback)
        {
            if (string.IsNullOrWhiteSpace(path))
            {
                return fallback;
            }

            string name = Path.GetFileName(path.Trim());
            return string.IsNullOrWhiteSpace(name) ? fallback : name;
        }

        public static string DescribeDirectoryDetail(string? path)
        {
            return string.IsNullOrWhiteSpace(path)
                ? "No install folder selected."
                : BuildFolderSummary(path, "Configured install");
        }
    }
}
