using System;
using Onslaught___Career_Editor;
using Xunit;

namespace OnslaughtCareerEditor.AppCore.Tests
{
    public sealed class SafeCopyProfileCatalogContractTests
    {
        [Fact]
        public void ProfileParityRejectsModuleNarrativeAndRestoreDrift()
        {
            SafeCopyProfilePreset expected = MakePreset();
            SafeCopyProfileModule module = expected.Modules[0];
            SafeCopyProfilePreset[] drifted =
            {
                expected with { Modules = new[] { module with { ProofStatus = "different proof" } } },
                expected with { Modules = new[] { module with { ClaimBoundary = "different boundary" } } },
                expected with { Modules = new[] { module with { RestoreStrategy = "different restore" } } },
                expected with { Modules = new[] { module with { EvidenceRefs = new[] { "different.md" } } } },
                expected with { Modules = new[] { module with { NonClaims = new[] { "different non-claim" } } } },
                expected with { Modules = new[] { module with { PatchKeys = new[] { "different-row" } } } },
                expected with { Modules = new[] { module with { LaunchArguments = new[] { "-different" } } } },
                expected with { Modules = new[] { module with { CopiedOptionsEdits = new[] { "different=1" } } } },
            };

            foreach (SafeCopyProfilePreset actual in drifted)
            {
                Assert.False(BinaryPatchPlanBuilder.ProfilePresetEquals(expected, actual));
            }
        }

        /// <summary>
        /// Two SEPARATELY BUILT presets with identical content must compare equal.
        ///
        /// <para>Corrected 2026-07-29. This asserted
        /// <c>ProfilePresetEquals(expected, expected)</c> — the same instance twice —
        /// which any implementation satisfies by reference identity alone. It could
        /// not fail, and it is in the default <c>npm test</c> gate, so it read as
        /// coverage of the parity contract while proving nothing about it.</para>
        ///
        /// <para><c>MakePreset()</c> allocates fresh arrays on every call, so the two
        /// operands here are reference-distinct all the way down. That forces the
        /// comparison through structural equality, including sequence equality on
        /// <c>PatchKeys</c>, <c>LaunchArguments</c>, <c>CopiedOptionsEdits</c>,
        /// <c>EvidenceRefs</c> and <c>NonClaims</c> — the part that actually
        /// carries risk, and the part the old form skipped entirely.</para>
        /// </summary>
        [Fact]
        public void ProfileParityAcceptsAnExactPreset()
        {
            SafeCopyProfilePreset expected = MakePreset();
            SafeCopyProfilePreset builtSeparately = MakePreset();

            Assert.False(
                ReferenceEquals(expected, builtSeparately),
                "the two operands must be distinct instances or this test proves nothing");
            Assert.True(BinaryPatchPlanBuilder.ProfilePresetEquals(expected, builtSeparately));
        }

        private static SafeCopyProfilePreset MakePreset()
        {
            var module = new SafeCopyProfileModule(
                Id: "module",
                DisplayName: "Module",
                Category: "Executable patch rows",
                ProofStatus: "Bounded proof.",
                ClaimBoundary: "Bounded claim.",
                PatchKeys: new[] { "row" },
                LaunchArguments: new[] { "-skipfmv" },
                CopiedOptionsEdits: new[] { "example=1" },
                RestoreStrategy: "Restore the copied backup.",
                EvidenceRefs: new[] { "patches/README.md" },
                NonClaims: new[] { "No broader claim." });
            return new SafeCopyProfilePreset(
                Id: "profile",
                DisplayName: "Profile",
                Description: "Description",
                PatchKeys: new[] { "row" },
                IsSelectable: true,
                ProofStatus: "Bounded proof.",
                DefaultControllerConfiguration: 1,
                DefaultPersistControllerConfigInOptions: true,
                DefaultMouseLookSensitivity: GameProfileControlOptionsService.MinimumMouseLookSensitivity,
                DefaultScreenShape: 1,
                Modules: new[] { module });
        }
    }
}
