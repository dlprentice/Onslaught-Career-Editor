using System.IO;

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

        /// <summary>
        /// Path cards name the file and its parent folder. The full path stays off the page.
        /// </summary>
        public static string BuildPathSummary(string? path)
        {
            if (string.IsNullOrWhiteSpace(path))
            {
                return "No file selected";
            }

            string trimmed = path.TrimEnd(Path.DirectorySeparatorChar, Path.AltDirectorySeparatorChar);
            string name = Path.GetFileName(trimmed);
            string? parent = Path.GetFileName(Path.GetDirectoryName(trimmed) ?? string.Empty);
            if (string.IsNullOrWhiteSpace(parent))
            {
                return string.IsNullOrWhiteSpace(name) ? "That file" : name;
            }

            return $"{name} in {parent}";
        }
    }
}
