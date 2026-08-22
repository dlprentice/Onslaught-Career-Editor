using System;

namespace OnslaughtCareerEditor.WinUI.Helpers
{
    /// <summary>
    /// One full-text search match row in the Lore library pane: the document it
    /// lives in, the snippet with the matched word bolded between two runs, and
    /// the automation strings the page binds to. When AppCore located the passage's
    /// section, the row names it and opens the reader scrolled there instead of at
    /// the top of the document.
    /// </summary>
    public sealed class LoreSearchHitModel
    {
        public LoreSearchHitModel(AppCore.LoreSearchHit hit)
        {
            Hit = hit;
            DocumentTitle = string.IsNullOrWhiteSpace(hit.DocumentTitle)
                ? "Included document"
                : hit.DocumentTitle;
            HasSectionTarget = !string.IsNullOrWhiteSpace(hit.SectionAnchor)
                && !string.IsNullOrWhiteSpace(hit.SectionHeading);

            string sectionSentence = HasSectionTarget
                ? $" Opens {DocumentTitle} in section {hit.SectionHeading}."
                : $" Open {DocumentTitle}.";
            AccessibilityName =
                $"Search match in {DocumentTitle}: {hit.SnippetBefore} {hit.MatchedText} {hit.SnippetAfter}."
                + sectionSentence;
        }

        public AppCore.LoreSearchHit Hit { get; }

        public string DocumentTitle { get; }

        public bool HasSectionTarget { get; }

        public string SectionHeading => Hit.SectionHeading;

        /// <summary>The row's visible section line, empty when there is no section target.</summary>
        public string SectionLine => HasSectionTarget ? $"in section: {SectionHeading}" : string.Empty;

        public string SnippetBefore => Hit.SnippetBefore;

        public string MatchedText => Hit.MatchedText;

        public string SnippetAfter => Hit.SnippetAfter;

        public string AccessibilityName { get; }
    }
}
