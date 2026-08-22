using OnslaughtCareerEditor.AppCore;
using System;
using System.ComponentModel;

namespace OnslaughtCareerEditor.WinUI.Models
{
    /// <summary>
    /// One census-candidate row in the Patch Lab. Census rows are research
    /// experiments, not product patches: they can be selected for staging into a
    /// safe copy, but never present themselves as catalog features.
    /// </summary>
    public sealed class PatchCensusRowModel : INotifyPropertyChanged
    {
        private bool _isSelectedForStaging;

        public PatchCensusRowModel(PatchCensusRow row, int index)
        {
            Row = row;
            Index = index;
            RowAutomationId = $"PatchCensusRow_{index:D3}";
            AccessibilityName =
                $"Select census experiment {row.Va} {row.Confidence} {row.Risk}: {row.Effect}. Census experiment, not a product patch; stages into a safe copy only.";
            ConfidenceLabel = $"Confidence: {row.Confidence}";
            RiskLabel = $"Risk: {row.Risk}";
            EvidenceSummary = row.EvidenceRefs.Count > 0
                ? $"Evidence ({row.EvidenceRefs.Count}): {string.Join("; ", row.EvidenceRefs)}"
                : "Evidence: none listed for this row.";
            Verification = string.IsNullOrWhiteSpace(row.CheapestVerification)
                ? "Cheapest verification: not recorded."
                : $"Cheapest verification: {row.CheapestVerification}";
            PlayerEffectSummary = BuildPlayerEffectSummary(row);
        }

        public event PropertyChangedEventHandler? PropertyChanged;

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

        /// <summary>
        /// What staging this row changes, in player terms, with the honest boundary:
        /// what to look for after the copied game runs, and that nothing is proven
        /// until it is observed.
        /// </summary>
        public string PlayerEffectSummary { get; }

        public bool IsSelectedForStaging
        {
            get => _isSelectedForStaging;
            set
            {
                if (_isSelectedForStaging == value)
                {
                    return;
                }

                _isSelectedForStaging = value;
                PropertyChanged?.Invoke(this, new PropertyChangedEventArgs(nameof(IsSelectedForStaging)));
            }
        }

        public string RowAutomationId { get; }

        /// <summary>Distinct property name so the census binding is unique in XAML.</summary>
        public string CensusRowAutomationId => RowAutomationId;

        public string CensusRowCheckBoxAutomationId => $"PatchCensusCheck_{Index:D3}";

        public string AccessibilityName { get; }

        private static string BuildPlayerEffectSummary(PatchCensusRow row)
        {
            string effect = row.Effect?.Trim() ?? string.Empty;
            if (effect.Length == 0)
            {
                return "Staging this row changes bytes in the safe copy; no player-visible effect is recorded.";
            }

            return "If staged: " + effect +
                ". This is an unproven experiment - run the cheapest check on your copied game before believing any benefit.";
        }
    }
}
