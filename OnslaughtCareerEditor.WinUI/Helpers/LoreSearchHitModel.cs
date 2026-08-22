using System;

namespace OnslaughtCareerEditor.WinUI.Helpers
{
    /// <summary>
    /// One full-text search match row in the Lore library pane: the document it
    /// lives in, the snippet with the matched word bolded between two runs, and
    /// the automation strings the page binds to.
    /// </summary>
    public sealed class LoreSearchHitModel
    {
        public LoreSearchHitModel(AppCore.LoreSearchHit hit)
        {
            Hit = hit;
            DocumentTitle = string.IsNullOrWhiteSpace(hit.DocumentTitle)
                ? "Included document"
                : hit.DocumentTitle;
            AccessibilityName =
                $"Search match in {DocumentTitle}: {hit.SnippetBefore} {hit.MatchedText} {hit.SnippetAfter}. "
                + $"Open {DocumentTitle}.";
        }

        public AppCore.LoreSearchHit Hit { get; }

        public string DocumentTitle { get; }

        public string SnippetBefore => Hit.SnippetBefore;

        public string MatchedText => Hit.MatchedText;

        public string SnippetAfter => Hit.SnippetAfter;

        public string AccessibilityName { get; }
    }
}
