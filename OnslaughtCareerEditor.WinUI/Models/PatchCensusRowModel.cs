using OnslaughtCareerEditor.AppCore;
using System;

namespace OnslaughtCareerEditor.WinUI.Models
{
    /// <summary>
    /// One census-candidate row in the Patch Lab. Census sites are not product
    /// patches; the model has no stage action.
    /// </summary>
    public sealed class PatchCensusRowModel
    {
        public PatchCensusRowModel(PatchCensusRow row, int index)
        {
            Row = row;
            Index = index;
            RowAutomationId = $"PatchCensusRow_{index:D3}";
            AccessibilityName =
                $"{row.Va} {row.Confidence} {row.Risk}: {row.Effect}. Census candidate, not a product patch.";
            ConfidenceLabel = $"Confidence: {row.Confidence}";
            RiskLabel = $"Risk: {row.Risk}";
            EvidenceSummary = row.EvidenceRefs.Count > 0
                ? $"Evidence ({row.EvidenceRefs.Count}): {string.Join("; ", row.EvidenceRefs)}"
                : "Evidence: none listed for this row.";
            Verification = string.IsNullOrWhiteSpace(row.CheapestVerification)
                ? "Cheapest verification: not recorded."
                : $"Cheapest verification: {row.CheapestVerification}";
        }

        public PatchCensusRow Row { get; }

        public int Index { get; }

        public string Va => Row.Va;

        public string Offset => Row.Offset;

        public string Effect => Row.Effect;

        public string OriginalHex => Row.OriginalHexDisplay;

        public string PatchedHex => Row.PatchedHexDisplay;

        public string ConfidenceLabel { get; }

        public string RiskLabel { get; }

        public string EvidenceSummary { get; }

        public string Verification { get; }

        public string RowAutomationId { get; }

        /// <summary>Distinct property name so the census binding is unique in XAML.</summary>
        public string CensusRowAutomationId => RowAutomationId;

        public string AccessibilityName { get; }
    }
}
