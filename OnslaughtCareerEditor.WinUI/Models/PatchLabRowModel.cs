using OnslaughtCareerEditor.AppCore;
using System;
using System.Collections.Generic;
using System.Linq;

namespace OnslaughtCareerEditor.WinUI.Models
{
    /// <summary>
    /// One read-only patch row shown by the Lab's patch inspector: catalog identity,
    /// byte regions, evidence, and risk joined from <see cref="PatchLabRow"/>, plus
    /// the presentation strings and automation ids the page binds to.
    /// </summary>
    public sealed class PatchLabRowModel
    {
        public PatchLabRowModel(PatchLabRow row)
        {
            Row = row;

            TrackLabel = row.Track.ToUpperInvariant() + (row.IsHiddenCompanion ? " - HIDDEN COMPANION ROW" : string.Empty);
            EvidenceSummary = row.EvidenceRefs.Count > 0
                ? $"Evidence ({row.EvidenceRefs.Count}): {string.Join("; ", row.EvidenceRefs)}"
                : "Evidence: none listed for this row.";
            GraphSummary = BuildGraphSummary(row);
            RegionsHeader = $"Bytes ({row.Regions.Count} region{(row.Regions.Count == 1 ? "" : "s")})";
            RegionLines = row.Regions
                .Select(region => new PatchLabRegionLine(
                    $"0x{region.FileOffset:X6}",
                    region.OriginalHex,
                    region.PatchedHex))
                .ToArray();
            CanBeStaged = !row.IsHiddenCompanion;
            StageLabel = row.IsHiddenCompanion
                ? "Hidden companion row - applied automatically with its visible row"
                : "Stage this row in the selection above";
            StageAccessibilityName = row.IsHiddenCompanion
                ? $"{row.Title}: hidden companion row cannot be staged directly"
                : $"Stage {row.Title} in the safe-copy patch selection";
            RowAutomationId = $"PatchInspectorRow_{row.Key}";
            InspectorRowAutomationId = RowAutomationId;
            StageButtonAutomationId = $"PatchInspectorStage_{row.Key}";
        }

        public PatchLabRow Row { get; }

        public string Key => Row.Key;
        public string Title => Row.Title;
        public string Purpose => Row.Purpose;
        public string TrackLabel { get; }
        public string ProofLevel => string.IsNullOrWhiteSpace(Row.ProofLevel)
            ? "Proof level: not recorded"
            : $"Proof level: {Row.ProofLevel}";
        public string Confidence => string.IsNullOrWhiteSpace(Row.Confidence)
            ? "Confidence: not recorded"
            : $"Confidence: {Row.Confidence}";
        public string RiskSummary => Row.RiskSummary;
        public string RollbackStrategy => $"Rollback: {Row.RollbackStrategy}";
        public string EvidenceSummary { get; }
        public string GraphSummary { get; }
        public string RegionsHeader { get; }
        public IReadOnlyList<PatchLabRegionLine> RegionLines { get; }

        public bool CanBeStaged { get; }
        public string StageLabel { get; }
        public string StageAccessibilityName { get; }
        public string RowAutomationId { get; }
        /// <summary>Same id exposed under a distinct property name for the inspector row binding.</summary>
        public string InspectorRowAutomationId { get; }
        public string StageButtonAutomationId { get; }

        private static string BuildGraphSummary(PatchLabRow row)
        {
            var parts = new List<string>();
            if (row.RequiresWindowedPair)
            {
                parts.Add("tested together with the required windowed pair");
            }

            if (row.Dependencies.Count > 0)
            {
                parts.Add($"needs: {string.Join(", ", row.Dependencies)}");
            }

            if (row.Conflicts.Count > 0)
            {
                parts.Add($"conflicts with: {string.Join(", ", row.Conflicts)}");
            }

            if (!string.IsNullOrWhiteSpace(row.ExclusiveGroup))
            {
                parts.Add($"exclusive group '{row.ExclusiveGroup}': only one can be chosen");
            }

            return parts.Count > 0
                ? string.Join(" | ", parts)
                : "No dependencies, conflicts, or exclusive group.";
        }
    }

    /// <summary>One formatted byte region line in the inspector.</summary>
    public sealed record PatchLabRegionLine(string Offset, string OriginalHex, string PatchedHex);
}
