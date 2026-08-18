namespace OnslaughtCareerEditor.WinUI.Helpers
{
    /// <summary>
    /// The sentence Asset Library shows when a search matches nothing. Kept out
    /// of the page so an empty list cannot quietly become "no matches" again.
    /// </summary>
    internal static class AssetLibraryPageText
    {
        public const string EmptySearchNextStep =
            "Try another word, or clear the search.";

        public static string? DescribeListNote(bool hasCatalog, string? search, int matchCount)
        {
            if (!hasCatalog || matchCount > 0 || string.IsNullOrWhiteSpace(search))
            {
                return null;
            }

            return EmptySearchNextStep;
        }
    }
}
