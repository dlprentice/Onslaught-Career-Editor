using System.IO;

namespace OnslaughtCareerEditor.WinUI.Helpers
{
    /// <summary>
    /// The sentences the Lore library pane shows while a search is active. Kept out of the
    /// page so an empty result cannot quietly become "filtered results" again.
    /// </summary>
    internal static class LorePageText
    {
        public const string EmptySearchNextStep =
            "Try another word, or clear the search.";

        public const string EmptyLibraryNextStep =
            "Refresh the library, or reinstall the app if this keeps happening.";

        public const string DocumentLoadFailed =
            "That Lore document could not be opened. Refresh the library and try again.";

        public const string LinkOpenFailed =
            "That Lore link could not be opened. Refresh the library and try again.";

        public const string DocumentTooltipFallback = "Offline Lore document";

        public static string DescribeSearchStatus(string query, int matchCount)
        {
            if (matchCount <= 0)
            {
                return EmptySearchNextStep;
            }

            return $"Filtered results for \"{query}\".";
        }

        /// <summary>
        /// The current-document tooltip names the file, not the lore-book folder
        /// or a full path. The summary line already says which article this is.
        /// </summary>
        public static string BuildDocumentTooltip(string? title, string? relativePath, string? sourcePath = null)
        {
            string relativeLeaf = LeafName(relativePath);
            if (!string.IsNullOrWhiteSpace(relativeLeaf))
            {
                return relativeLeaf;
            }

            if (!string.IsNullOrWhiteSpace(title))
            {
                return title.Trim();
            }

            string sourceLeaf = LeafName(sourcePath);
            return string.IsNullOrWhiteSpace(sourceLeaf) ? DocumentTooltipFallback : sourceLeaf;
        }

        private static string LeafName(string? path)
        {
            if (string.IsNullOrWhiteSpace(path))
            {
                return string.Empty;
            }

            return Path.GetFileName(path.Trim().Replace('/', Path.DirectorySeparatorChar));
        }
    }
}
