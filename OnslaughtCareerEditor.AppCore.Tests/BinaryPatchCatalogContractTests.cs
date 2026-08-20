using System;
using System.IO;
using System.Linq;
using OnslaughtCareerEditor.AppCore;
using Xunit;

namespace OnslaughtCareerEditor.AppCore.Tests
{
    public sealed class BinaryPatchCatalogContractTests
    {
        [Fact]
        public void MutationPolicyParityAcceptsAnExactSpec()
        {
            BinaryPatchSpec expected = MakeSpec();
            BinaryPatchSpec actual = MakeSpec();

            Assert.False(
                ReferenceEquals(expected, actual),
                "the two operands must be distinct instances or this test proves nothing");
            Assert.True(BinaryPatchEngine.MutationPolicyEquals(expected, actual));
        }

        [Fact]
        public void MutationPolicyParityRejectsEveryPlanningFieldDrift()
        {
            BinaryPatchSpec expected = MakeSpec();
            BinaryPatchSpec[] drifted =
            {
                expected with { Dependencies = new[] { "other-dependency" } },
                expected with { Conflicts = new[] { "other-conflict" } },
                expected with { ExclusiveGroup = "other-group" },
                expected with { ProofLevel = "other-proof" },
                expected with { Selectability = "hidden_companion" },
                expected with { PresetEligibility = new[] { "other-profile" } },
                expected with { RequiresWindowedPair = false },
                expected with { Key = "other-key" },
                expected with { Track = "other-track" },
                expected with { DisplayName = "Other patch" },
                expected with { FileOffset = 0x121 },
                expected with { Original = new byte[] { 0x01, 0x03 } },
                expected with { Patched = new byte[] { 0x90, 0x91 } },
                expected with { Optional = false },
                expected with { TargetBinaryHashes = new[] { "other-hash" } },
                expected with { TargetBinarySize = 4097 },
                expected with
                {
                    AdditionalRegions = new[]
                    {
                        new BinaryPatchRegion(0x220, new byte[] { 0x03 }, new byte[] { 0x91 }),
                    },
                },
            };

            foreach (BinaryPatchSpec actual in drifted)
            {
                Assert.False(BinaryPatchEngine.MutationPolicyEquals(expected, actual));
            }
        }

        [Fact]
        public void MutationPolicyParityTreatsSetsAsOrderIndependent()
        {
            BinaryPatchSpec expected = MakeSpec();
            BinaryPatchSpec reordered = expected with
            {
                Dependencies = new[] { "dependency-b", "dependency-a" },
                Conflicts = new[] { "conflict-b", "conflict-a" },
                TargetBinaryHashes = new[] { "b", "a" },
                PresetEligibility = new[] { "profile-b", "profile-a" },
            };

            Assert.True(BinaryPatchEngine.MutationPolicyEquals(expected, reordered));
        }

        [Fact]
        public void SelectionPolicyRejectsNoOpPatchBytes()
        {
            BinaryPatchSpec expected = MakeSpec();
            BinaryPatchSpec noOp = expected with
            {
                Patched = expected.Original.ToArray(),
                Dependencies = Array.Empty<string>(),
                Conflicts = Array.Empty<string>(),
                ExclusiveGroup = string.Empty,
                RequiresWindowedPair = false,
            };

            var result = BinaryPatchEngine.ValidatePatchSelectionPolicy(new[] { noOp });

            Assert.False(result.success);
            Assert.Contains("no-op", result.message, StringComparison.OrdinalIgnoreCase);
        }

        [Fact]
        public void SelectionPolicyRejectsShiftedOverlapEvenWhenPatchedArraysMatch()
        {
            BinaryPatchSpec first = MakeSpec() with
            {
                FileOffset = 0x120,
                Dependencies = Array.Empty<string>(),
                Conflicts = Array.Empty<string>(),
                ExclusiveGroup = string.Empty,
                RequiresWindowedPair = false,
            };
            BinaryPatchSpec second = first with
            {
                Key = "second",
                FileOffset = 0x121,
            };

            var result = BinaryPatchEngine.ValidatePatchSelectionPolicy(new[] { first, second });

            Assert.False(result.success);
            Assert.Contains("overlapping", result.message, StringComparison.OrdinalIgnoreCase);
        }

        [Fact]
        public void SelectionPolicyRejectsMutationDriftFromPinnedCatalog()
        {
            BinaryPatchSpec canonical = BinaryPatchEngine.PatchSpecs.First(spec => spec.Key == "resolution_gate");
            Assert.Equal(28, BinaryPatchEngine.GetPatchRegions(canonical).Count);
            BinaryPatchSpec drifted = canonical with { Patched = new byte[] { 0x01 } };

            var result = BinaryPatchEngine.ValidatePatchSelectionPolicy(new[] { drifted });

            Assert.False(result.success);
            Assert.Contains("pinned patch catalog", result.message, StringComparison.OrdinalIgnoreCase);
        }

        [Fact]
        public void CatalogTransitionAttestationAllowsOnlyCompleteKnownRows()
        {
            BinaryPatchSpec spec = MakeSpec() with
            {
                FileOffset = 0x10,
                AdditionalRegions = new[]
                {
                    new BinaryPatchRegion(0x20, new byte[] { 0x03 }, new byte[] { 0x91 }),
                },
                Dependencies = Array.Empty<string>(),
                Conflicts = Array.Empty<string>(),
                ExclusiveGroup = string.Empty,
                RequiresWindowedPair = false,
            };
            byte[] backup = new byte[0x40];
            spec.Original.CopyTo(backup, spec.FileOffset);
            spec.AdditionalRegions![0].Original.CopyTo(backup, spec.AdditionalRegions[0].FileOffset);

            byte[] patched = backup.ToArray();
            spec.Patched.CopyTo(patched, spec.FileOffset);
            spec.AdditionalRegions[0].Patched.CopyTo(patched, spec.AdditionalRegions[0].FileOffset);
            Assert.Equal(BinaryPatchState.Patched, BinaryPatchEngine.GetPatchState(patched, spec));
            Assert.True(BinaryPatchEngine.CurrentBytesContainOnlyKnownCatalogTransitions(patched, backup, new[] { spec }));

            byte[] unrelatedDrift = patched.ToArray();
            unrelatedDrift[0x30] = 0x42;
            Assert.False(BinaryPatchEngine.CurrentBytesContainOnlyKnownCatalogTransitions(unrelatedDrift, backup, new[] { spec }));

            byte[] partialPatch = backup.ToArray();
            partialPatch[spec.FileOffset] = spec.Patched[0];
            Assert.Equal(BinaryPatchState.Mismatch, BinaryPatchEngine.GetPatchState(partialPatch, spec));
            Assert.False(BinaryPatchEngine.CurrentBytesContainOnlyKnownCatalogTransitions(partialPatch, backup, new[] { spec }));
        }

        [Fact]
        public void InspectCopyExecutableRefusesAMissingFileWithoutGuessingOriginal()
        {
            BinaryPatchCopyInspectResult result = BinaryPatchEngine.InspectCopyExecutable(
                Path.Combine(Path.GetTempPath(), "no-such-copy", "BEA.exe"),
                new[] { MakeSpec() });

            Assert.Equal(BinaryPatchCopyInspectRefusal.NoExecutable, result.Refusal);
            Assert.False(result.Success);
            Assert.Empty(result.Rows);
        }

        [Fact]
        public void InspectCopyExecutableRefusesAnInstalledGamePathWithoutReadingIt()
        {
            string root = Path.Combine(Path.GetTempPath(), "inspect-installed-" + Guid.NewGuid().ToString("N"));
            string exePath = Path.Combine(root, "steamapps", "common", "Battle Engine Aquila", "BEA.exe");
            Directory.CreateDirectory(Path.GetDirectoryName(exePath)!);
            File.WriteAllBytes(exePath, new byte[] { 0x4D, 0x5A });

            try
            {
                BinaryPatchCopyInspectResult result = BinaryPatchEngine.InspectCopyExecutable(
                    exePath,
                    new[] { MakeSpec() });

                Assert.Equal(BinaryPatchCopyInspectRefusal.InstalledGame, result.Refusal);
                Assert.False(result.Success);
                Assert.Empty(result.Rows);
            }
            finally
            {
                Directory.Delete(root, recursive: true);
            }
        }

        [Fact]
        public void InspectCopyExecutableReadsOriginalAndPatchedStatesFromACopyFile()
        {
            BinaryPatchSpec spec = MakeSpec() with
            {
                Dependencies = Array.Empty<string>(),
                Conflicts = Array.Empty<string>(),
                ExclusiveGroup = string.Empty,
                RequiresWindowedPair = false,
                AdditionalRegions = Array.Empty<BinaryPatchRegion>(),
            };
            string path = Path.Combine(Path.GetTempPath(), "inspect-copy-" + Guid.NewGuid().ToString("N") + ".bin");
            byte[] original = new byte[spec.FileOffset + spec.Original.Length + 8];
            spec.Original.CopyTo(original, spec.FileOffset);
            File.WriteAllBytes(path, original);

            try
            {
                BinaryPatchCopyInspectResult originalResult = BinaryPatchEngine.InspectCopyExecutable(path, new[] { spec });
                Assert.True(originalResult.Success);
                Assert.Equal(BinaryPatchCopyInspectRefusal.None, originalResult.Refusal);
                Assert.Equal(BinaryPatchState.Original, Assert.Single(originalResult.Rows).State);

                byte[] patched = original.ToArray();
                spec.Patched.CopyTo(patched, spec.FileOffset);
                File.WriteAllBytes(path, patched);

                BinaryPatchCopyInspectResult patchedResult = BinaryPatchEngine.InspectCopyExecutable(path, new[] { spec });
                Assert.True(patchedResult.Success);
                Assert.Equal(BinaryPatchState.Patched, Assert.Single(patchedResult.Rows).State);
            }
            finally
            {
                File.Delete(path);
            }
        }

        private static BinaryPatchSpec MakeSpec()
        {
            return new BinaryPatchSpec(
                Key: "example",
                Track: "Experimental",
                DisplayName: "Example patch",
                FileOffset: 0x120,
                Original: new byte[] { 0x01, 0x02 },
                Patched: new byte[] { 0x90, 0x90 },
                Optional: true,
                TargetBinaryHashes: new[] { "a", "b" },
                TargetBinarySize: 4096,
                Dependencies: new[] { "dependency-a", "dependency-b" },
                Conflicts: new[] { "conflict-a", "conflict-b" },
                ExclusiveGroup: "example-group",
                ProofLevel: "example-proof",
                Selectability: "experimental_visible",
                PresetEligibility: new[] { "profile-a", "profile-b" },
                RequiresWindowedPair: true);
        }
    }
}
