using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Security.Cryptography;
using Xunit;

namespace OnslaughtCareerEditor.AppCore.Tests
{
    /// <summary>
    /// The Patch Lab census reader: exact TSV columns from the census lane, no
    /// format fork, honest miss when the file is absent, never writes.
    /// </summary>
    public sealed class PatchSurfaceCensusReaderTests : IDisposable
    {
        private readonly string _tempRoot;

        public PatchSurfaceCensusReaderTests()
        {
            _tempRoot = Path.Combine(Path.GetTempPath(), "oce-patch-census-tests", Guid.NewGuid().ToString("N"));
            Directory.CreateDirectory(_tempRoot);
        }

        public void Dispose()
        {
            try
            {
                Directory.Delete(_tempRoot, recursive: true);
            }
            catch (IOException)
            {
            }
        }

        private static string SamplePath()
        {
            return Path.GetFullPath(Path.Combine(
                AppContext.BaseDirectory, "..", "..", "..", "fixtures", "patch-surface-rows.sample.tsv"));
        }

        [Fact]
        public void LoadFrom_Sample_ParsesExactColumnsAndKeepsDuplicateVas()
        {
            Assert.True(File.Exists(SamplePath()), $"sample fixture missing: {SamplePath()}");

            PatchCensusCatalog catalog = PatchSurfaceCensusReader.LoadFrom(SamplePath());

            Assert.True(catalog.Found, catalog.Status);
            Assert.Equal(4, catalog.Rows.Count);
            Assert.Equal(2, catalog.MeasuredCount);
            Assert.Equal(2, catalog.StaticOnlyCount);
            Assert.Equal(0, catalog.SpeculativeCount);
            Assert.Contains("research experiments", catalog.Status, StringComparison.Ordinal);
            Assert.Contains("safe copy only", catalog.Status, StringComparison.Ordinal);

            PatchCensusRow first = catalog.Rows[0];
            Assert.Equal("0x0046F4A8", first.Va);
            Assert.Equal("0x0006F4A8", first.Offset);
            Assert.Equal("c7434800000040", first.OriginalBytes);
            Assert.Equal("c7434800000000", first.PatchedBytes);
            Assert.Equal("MEASURED", first.Confidence);
            Assert.Equal("low", first.Risk);
            Assert.Contains("C7 43 48", first.OriginalHexDisplay, StringComparison.Ordinal);
            Assert.Equal(2, first.EvidenceRefs.Count);
            Assert.Contains(first.EvidenceRefs, reference => reference.EndsWith("PARITY.md", StringComparison.Ordinal));

            // Two candidate patches share the same VA; both survive.
            Assert.Equal(2, catalog.Rows.Count(row => row.Va == "0x0046F4A8"));
        }

        [Fact]
        public void LoadFrom_MissingFile_IsAnHonestMiss()
        {
            PatchCensusCatalog catalog = PatchSurfaceCensusReader.LoadFrom(Path.Combine(_tempRoot, "no-such.tsv"));

            Assert.False(catalog.Found);
            Assert.Empty(catalog.Rows);
            Assert.Equal(PatchSurfaceCensusReader.MissingStatus, catalog.Status);
        }

        [Fact]
        public void LoadFrom_WrongHeader_RefusesInsteadOfForking()
        {
            string path = Path.Combine(_tempRoot, "forked.tsv");
            File.WriteAllText(path, "addr\tbytes\teffect\n0x1\taa\tnope\n");

            PatchCensusCatalog catalog = PatchSurfaceCensusReader.LoadFrom(path);

            Assert.False(catalog.Found);
            Assert.Empty(catalog.Rows);
            Assert.Equal(PatchSurfaceCensusReader.HeaderMismatchStatus, catalog.Status);
        }

        [Fact]
        public void FilterRows_MatchesEffectConfidenceAndEmptyQueries()
        {
            PatchCensusCatalog catalog = PatchSurfaceCensusReader.LoadFrom(SamplePath());

            Assert.Same(catalog.Rows, PatchSurfaceCensusReader.FilterRows(catalog.Rows, ""));
            Assert.Same(catalog.Rows, PatchSurfaceCensusReader.FilterRows(catalog.Rows, null));

            IReadOnlyList<PatchCensusRow> byEffect = PatchSurfaceCensusReader.FilterRows(catalog.Rows, "CLOCK_TICK");
            Assert.Single(byEffect);
            Assert.Equal("0x005D8578", byEffect[0].Va);

            IReadOnlyList<PatchCensusRow> byConfidence = PatchSurfaceCensusReader.FilterRows(catalog.Rows, "MEASURED");
            Assert.Equal(2, byConfidence.Count);

            Assert.Empty(PatchSurfaceCensusReader.FilterRows(catalog.Rows, "no-such-census-xyz"));
        }

        [Fact]
        public void LoadFrom_DoesNotMutateTheFile()
        {
            string copy = Path.Combine(_tempRoot, "patch-surface-rows.tsv");
            File.Copy(SamplePath(), copy);
            byte[] before = SHA256.HashData(File.ReadAllBytes(copy));

            PatchCensusCatalog first = PatchSurfaceCensusReader.LoadFrom(copy);
            PatchCensusCatalog second = PatchSurfaceCensusReader.LoadFrom(copy);

            Assert.Equal(first.Rows.Count, second.Rows.Count);
            Assert.Equal(before, SHA256.HashData(File.ReadAllBytes(copy)));
        }

        [Fact]
        public void RequiredColumns_MatchTheCensusLaneContract()
        {
            Assert.Equal(
                new[]
                {
                    "va",
                    "offset",
                    "original_bytes",
                    "patched_bytes",
                    "effect",
                    "confidence",
                    "evidence_path",
                    "risk",
                    "cheapest_verification",
                },
                PatchSurfaceCensusReader.RequiredColumns);
        }

        [Fact]
        public void Load_WhenSiblingCensusExists_ParsesWithoutWriting()
        {
            PatchCensusCatalog catalog = PatchSurfaceCensusReader.Load();
            if (!catalog.Found)
            {
                Assert.Equal(PatchSurfaceCensusReader.MissingStatus, catalog.Status);
                Assert.Empty(catalog.Rows);
                return;
            }

            Assert.True(catalog.Rows.Count > 0, catalog.Status);
            Assert.Contains("research experiments", catalog.Status, StringComparison.Ordinal);
            Assert.Contains("safe copy only", catalog.Status, StringComparison.Ordinal);
            Assert.All(catalog.Rows, row =>
            {
                Assert.StartsWith("0x", row.Va, StringComparison.OrdinalIgnoreCase);
                Assert.False(string.IsNullOrWhiteSpace(row.Effect));
                Assert.False(string.IsNullOrWhiteSpace(row.Confidence));
                Assert.False(string.IsNullOrWhiteSpace(row.Risk));
            });
        }
    }
}
