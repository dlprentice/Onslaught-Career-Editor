using System;
using System.Linq;

namespace OnslaughtCareerEditor.WinUI.Helpers
{
    /// <summary>One included document this page links to.</summary>
    public sealed class LoreOutgoingLinkModel
    {
        public LoreOutgoingLinkModel(AppCore.LoreOutgoingLink link)
        {
            Link = link;
            TargetDocumentTitle = string.IsNullOrWhiteSpace(link.TargetDocumentTitle)
                ? "Included document"
                : link.TargetDocumentTitle;

            string anchors = string.Join(", ", link.AnchorTargets
                .Where(anchor => !string.IsNullOrWhiteSpace(anchor))
                .Select(anchor => $"#{anchor}"));
            AccessibilityName = anchors.Length > 0
                ? $"Open {TargetDocumentTitle}, linked from this page at {anchors}"
                : $"Open {TargetDocumentTitle}, linked from this page";
        }

        public AppCore.LoreOutgoingLink Link { get; }

        public string TargetDocumentTitle { get; }

        public string AccessibilityName { get; }
    }
}
