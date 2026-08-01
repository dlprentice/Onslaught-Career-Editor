using Xunit;

namespace OnslaughtCareerEditor.Cli.Tests
{
    /// <summary>
    /// The three exit codes must stay distinguishable.
    ///
    /// The original CLI returned 1 both when it could not run and when it ran and the file turned out
    /// to be invalid. An agent cannot tell those apart, and they call for opposite responses: fix the
    /// invocation, or accept the answer. Every test here exists to keep that collapse from returning.
    /// </summary>
    [Collection(CliCollection.Name)]
    public class CliExitCodeTests
    {
        [Fact]
        public void AMissingFileIsAUsageErrorNotADataVerdict()
        {
            using var scratch = new CliScratch();

            CliRun run = Cli.Run("saves", "analyze", scratch.Path_("missing.bes"));

            Assert.Equal(1, run.ExitCode);
        }

        [Fact]
        public void AnInvalidFileIsADataVerdictNotAUsageError()
        {
            using var scratch = new CliScratch();
            string notASave = scratch.NonSaveFixture("bogus.bes");

            CliRun run = Cli.Run("saves", "analyze", notASave);

            Assert.Equal(2, run.ExitCode);
        }

        [Fact]
        public void TheSameSeparationHoldsForTheLegacyAnalyzeFlag()
        {
            using var scratch = new CliScratch();
            string notASave = scratch.NonSaveFixture("bogus.bes");

            Assert.Equal(1, Cli.Run(scratch.Path_("missing.bes"), "--analyze").ExitCode);
            Assert.Equal(2, Cli.Run(notASave, "--analyze").ExitCode);
        }

        [Fact]
        public void AValidSaveAnalyzesSuccessfully()
        {
            using var scratch = new CliScratch();
            string? baseline = scratch.TryCopyRealBaselineSave("baseline.bes");
            if (baseline is null)
            {
                // No retail installation on this machine, and saves are never synthesized.
                return;
            }

            Assert.Equal(0, Cli.Run("saves", "analyze", baseline).ExitCode);
        }

        [Fact]
        public void GoodieListingSeparatesAMissingFileFromAnUnreadableOne()
        {
            using var scratch = new CliScratch();
            string notASave = scratch.NonSaveFixture("bogus.bes");

            Assert.Equal(1, Cli.Run("goodies", "list", scratch.Path_("missing.bes")).ExitCode);
            Assert.Equal(2, Cli.Run("goodies", "list", notASave).ExitCode);
        }

        /// <summary>
        /// A patch target the CLI refuses to touch at all is a usage error. It must not be reported as a
        /// verdict, because nothing about the target's bytes was ever measured.
        /// </summary>
        [Fact]
        public void APatchTargetOutsideTheWorkspaceIsAUsageErrorNotAVerdict()
        {
            using var scratch = new CliScratch();
            string outsider = scratch.NonSaveFixture("elsewhere/BEA.exe");

            Assert.Equal(1, Cli.Run("patch", "verify", outsider).ExitCode);
            Assert.Equal(1, Cli.Run("patch", "apply", outsider).ExitCode);
            Assert.Equal(1, Cli.Run("patch", "restore", outsider).ExitCode);
        }

        [Fact]
        public void StoppingAnUnregisteredProcessIsAVerdictNotAUsageError()
        {
            using var scratch = new CliScratch();

            // The registry answered; it simply does not know this id.
            CliRun run = Cli.Run("process", "stop", "424242");

            Assert.Equal(2, run.ExitCode);
        }

        [Fact]
        public void AnInvalidProcessIdIsAUsageError()
        {
            using var scratch = new CliScratch();

            Assert.Equal(1, Cli.Run("process", "stop", "0").ExitCode);
        }

        [Fact]
        public void ListingVerbsSucceedOnAnEmptyWorkspaceRatherThanReportingNoData()
        {
            using var scratch = new CliScratch();

            // An empty list is a complete answer, not a negative verdict.
            Assert.Equal(0, Cli.Run("copy", "list").ExitCode);
            Assert.Equal(0, Cli.Run("process", "list").ExitCode);
        }
    }
}
