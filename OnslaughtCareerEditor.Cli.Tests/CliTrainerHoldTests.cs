using Xunit;

namespace OnslaughtCareerEditor.Cli.Tests
{
    /// <summary>
    /// The verb that closes the trainer's CLI gap.
    ///
    /// The GUI has had per-vital hold toggles since the trainer shipped; the CLI had status, read
    /// and set, and <c>set</c> ended by telling people to go and use the app instead. A single
    /// write is nearly a no-op - the game rewrites these fields about twenty times a second - so
    /// without hold the headless twin could not do the one thing a trainer is for.
    ///
    /// Nothing here attaches to a running game. Every case below is a refusal that must fire before
    /// any process is opened, which is exactly the part worth pinning: the ones that need a live
    /// mission are covered by driving the app.
    /// </summary>
    [Collection(CliCollection.Name)]
    public sealed class CliTrainerHoldTests
    {
        [Fact]
        public void TheVerbIsReachableAndDocumentsWhyItExists()
        {
            CliRun run = Cli.Run("trainer", "hold", "--help");

            Assert.Equal(0, run.ExitCode);
            Assert.Contains("--life", run.StdOut);
            Assert.Contains("--energy", run.StdOut);
            Assert.Contains("--shields", run.StdOut);
            Assert.Contains("--for", run.StdOut);
            Assert.Contains("overwrites a single write", run.StdOut);
        }

        [Fact]
        public void RefusesWithNothingToHold()
        {
            using var scratch = new CliScratch();

            CliRun run = Cli.Run("trainer", "hold");

            Assert.Equal(1, run.ExitCode);
            Assert.Contains("Nothing to hold", run.StdErr);
            Assert.Contains("trainer read", run.StdErr);
        }

        [Theory]
        [InlineData("0")]
        [InlineData("-5")]
        [InlineData("3601")]
        public void RefusesADurationItWillNotHonour(string seconds)
        {
            using var scratch = new CliScratch();

            CliRun run = Cli.Run("trainer", "hold", "--life", "100", "--for", seconds);

            Assert.Equal(1, run.ExitCode);
            Assert.Contains("between 1 and 3600", run.StdErr);
        }

        /// <summary>
        /// It is a verb that finishes, not a daemon. Saying so in the refusal matters because the
        /// obvious next thought on seeing a hold verb is to leave it running forever, and a process
        /// that exits while still holding would leave the game being written to by nothing.
        /// </summary>
        [Fact]
        public void SaysPlainlyThatItIsNotADaemon()
        {
            using var scratch = new CliScratch();

            CliRun run = Cli.Run("trainer", "hold", "--life", "100", "--for", "99999");

            Assert.Contains("not a daemon", run.StdErr);
        }

        [Fact]
        public void WithNoRunningCopyItSaysSoRatherThanHanging()
        {
            using var scratch = new CliScratch();

            CliRun run = Cli.Run("trainer", "hold", "--life", "100", "--for", "1");

            // No managed copy has ever been launched under this scratch config root, so the target
            // cannot resolve. What matters is that it is a clean refusal, not a wait.
            Assert.NotEqual(0, run.ExitCode);
            Assert.False(string.IsNullOrWhiteSpace(run.StdErr));
        }

        /// <summary>
        /// The advice <c>set</c> gives had to change the moment this verb existed - it used to send
        /// people to the GUI, which was the gap admitting itself in the product's own words.
        /// </summary>
        [Fact]
        public void SetNowPointsAtHoldRatherThanAtTheApp()
        {
            using var scratch = new CliScratch();

            CliRun run = Cli.Run("trainer", "set", "--life", "100");

            Assert.DoesNotContain("Cheats page", run.StdOut + run.StdErr);
        }
    }
}
