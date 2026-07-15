using System.Drawing;

namespace OnslaughtCareerEditor.UiTests;

internal static class HomeVisualEvidenceAcceptance
{
    internal static bool HasMeaningfulFrameCoverage(Bitmap bitmap) =>
        ToolkitVisualEvidenceAcceptance.HasMeaningfulFrameCoverage(bitmap);

    internal static bool HasRenderedToolkitHeader(Bitmap bitmap) =>
        ToolkitVisualEvidenceAcceptance.HasRenderedToolkitHeader(bitmap);

    internal static bool HasRenderedActivity(Bitmap bitmap, Rectangle bounds) =>
        ToolkitVisualEvidenceAcceptance.HasRenderedActivity(bitmap, bounds);
}
