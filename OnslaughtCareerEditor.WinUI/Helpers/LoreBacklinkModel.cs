using System;

namespace OnslaughtCareerEditor.WinUI.Helpers
{
    /// <summary>
    /// One "what links here" row in the Lore reader: the document that links to the
    /// open one, with the anchors it uses in the tooltip and automation name.
    /// </summary>
    public sealed class LoreBacklinkModel
    {
        public LoreBacklinkModel(AppCore.LoreBacklink link)
        {
            Link = link;
            SourceDocumentTitle = string.IsNullOrWhiteSpace(link.SourceDocumentTitle)
                ? "Included document"
                : link.SourceDocumentTitle;

            string anchors = string.Join(", ", link.AnchorTargets
                .Where(anchor => !string.IsNullOrWhiteSpace(anchor))
                .Select(anchor => $"#{anchor}"));
            AnchorSummary = anchors;
            AccessibilityName = anchors.Length > 0
                ? $"Open {SourceDocumentTitle}, which links here at {anchors}"
                : $"Open {SourceDocumentTitle}, which links here";
        }

        public AppCore.LoreBacklink Link { get; }

        public string SourceDocumentTitle { get; }

        public string AnchorSummary { get; }

        public string AccessibilityName { get; }
    }
}
