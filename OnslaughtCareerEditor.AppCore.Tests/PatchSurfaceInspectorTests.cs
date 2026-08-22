using System;
using System.IO;
using System.Linq;
using Xunit;

namespace OnslaughtCareerEditor.AppCore.Tests
{
    /// <summary>
    /// The Patch Lab inspection surface: rows join compiled specs with catalog
    /// prose, stay read-only, and grade risk from the catalog's own evidence class.
    /// </summary>
    public sealed class PatchSurfaceInspectorTests
    {
        [Fact]
        public void Load_ReturnsEveryCompiledSpecWithRegions()
        {
            PatchLabCatalog catalog = PatchSurfaceInspector.Load();

            Assert.Equal(BinaryPatchEngine.PatchSpecs.Count, catalog.Rows.Count);
            Assert.True(catalog.Rows.Count > 0);
            Assert.True(catalog.TotalRegions > 0);

            PatchLabRow widescreen = Assert.Single(catalog.Rows, row => row.Key == "resolution_gate");
            Assert.Equal(28, widescreen.Regions.Count);
            Assert.All(widescreen.Regions, region =>
            {
                Assert.NotEmpty(region.OriginalHex);
                Assert.NotEmpty(region.PatchedHex);
            });
        }

        [Fact]
        public void Load_JoinsCatalogProseOntoCompiledRows()
        {
            PatchLabCatalog catalog = PatchSurfaceInspector.Load();

            PatchLabRow widescreen = Assert.Single(catalog.Rows, row => row.Key == "resolution_gate");
            // From patches.v2.json; the compiled record carries no purpose text.
            Assert.Contains("28-region widescreen hook set", widescreen.Purpose, StringComparison.Ordinal);
            Assert.Equal("high", widescreen.Confidence, ignoreCase: true);
            Assert.Equal("copied_gameplay_runtime_16_9", widescreen.ProofLevel, ignoreCase: true);
            Assert.Contains(widescreen.EvidenceRefs, reference =>
                reference.EndsWith(".tsv", StringComparison.OrdinalIgnoreCase) ||
                reference.EndsWith(".md", StringComparison.OrdinalIgnoreCase));

            // Every compiled spec must find its prose row; a key mismatch would show
            // up as the fallback purpose text.
            Assert.All(catalog.Rows, row =>
                Assert.DoesNotContain("could not be read", row.Purpose, StringComparison.Ordinal));
        }

        [Fact]
        public void Load_GradesRiskFromTheCatalogsOwnEvidenceClass()
        {
            PatchLabCatalog catalog = PatchSurfaceInspector.Load();

            PatchLabRow resolutionGate = Assert.Single(catalog.Rows, row => row.Key == "resolution_gate");
            Assert.Equal(PatchLabRisk.Low, resolutionGate.Risk);

            PatchLabRow? anyExperimental = catalog.Rows.FirstOrDefault(row => row.Risk == PatchLabRisk.Experimental);
            Assert.NotNull(anyExperimental);
            Assert.Contains("experimental", anyExperimental!.Track, StringComparison.OrdinalIgnoreCase);

            Assert.All(catalog.Rows, row => Assert.DoesNotContain("\n", row.RiskSummary, StringComparison.Ordinal));
        }

        [Fact]
        public void HiddenCompanionRowsAreFlaggedAndVisibleRowsAreNot()
        {
            PatchLabCatalog catalog = PatchSurfaceInspector.Load();

            var visibleKeys = BinaryPatchPlanBuilder.GetVisibleSpecs().Select(spec => spec.Key).ToHashSet(StringComparer.OrdinalIgnoreCase);
            foreach (PatchLabRow row in catalog.Rows)
            {
                Assert.Equal(!visibleKeys.Contains(row.Key), row.IsHiddenCompanion);
            }

            // The version-overlay companion is the canonical hidden row.
            PatchLabRow cave = Assert.Single(catalog.Rows, row =>
                row.Key == "version_overlay_patched_format_cave_string");
            Assert.True(cave.IsHiddenCompanion);
            Assert.Empty(cave.Dependencies);
        }

        [Fact]
        public void FilterRows_MatchesKeyTitlePurposeAndIgnoresEmptyQueries()
        {
            PatchLabCatalog catalog = PatchSurfaceInspector.Load();

            Assert.Same(catalog.Rows, PatchSurfaceInspector.FilterRows(catalog.Rows, ""));
            Assert.Same(catalog.Rows, PatchSurfaceInspector.FilterRows(catalog.Rows, null));

            IReadOnlyList<PatchLabRow> byKey = PatchSurfaceInspector.FilterRows(catalog.Rows, "goodies");
            Assert.Contains(byKey, row => row.Key == "goodies_gallery_display_unlock");

            IReadOnlyList<PatchLabRow> byPurpose = PatchSurfaceInspector.FilterRows(catalog.Rows, "widescreen");
            Assert.Contains(byPurpose, row => row.Key == "resolution_gate");

            Assert.Empty(PatchSurfaceInspector.FilterRows(catalog.Rows, "no-such-row-xyz"));
        }

        [Fact]
        public void Load_DoesNotMutateAnything()
        {
            // The inspector is static and read-only; this test pins the contract that
            // loading twice returns equivalent content rather than accumulating state.
            PatchLabCatalog first = PatchSurfaceInspector.Load();
            PatchLabCatalog second = PatchSurfaceInspector.Load();

            Assert.Equal(first.Rows.Count, second.Rows.Count);
            Assert.Equal(first.TotalRegions, second.TotalRegions);
            Assert.Equal(first.CatalogVersion, second.CatalogVersion);
        }
    }
}
