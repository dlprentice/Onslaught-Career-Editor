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

        public static string DescribeSearchStatus(string query, int matchCount)
        {
            if (matchCount <= 0)
            {
                return EmptySearchNextStep;
            }

            return $"Filtered results for \"{query}\".";
        }
    }
}
