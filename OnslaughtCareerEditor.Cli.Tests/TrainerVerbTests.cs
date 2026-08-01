using System.Text.Json;
using Xunit;

namespace OnslaughtCareerEditor.Cli.Tests
{
    /// <summary>
    /// The live-trainer verbs.
    ///
    /// The gate itself - which process may be opened, and when a write is allowed - is pinned in
    /// AppCore against a fake address space, because pinning it here would need a running game.
    /// What these tests own is the half the CLI is responsible for: that the verbs exist, that the
    /// envelope and exit codes follow the same scheme as every other verb, and that "no copy is
    /// running" comes back as a verdict about the world rather than as a tool error.
    /// </summary>
    [Collection(CliCollection.Name)]
    public class TrainerVerbTests
    {
        [Fact]
        public void TheTrainerVerbIsRoutedAndDocumented()
        {
            CliRun help = Cli.Run("--help");

            Assert.Equal(0, help.ExitCode);
            Assert.Contains("trainer", help.StdOut);
        }

        [Theory]
        [InlineData("status")]
        [InlineData("read")]
        [InlineData("set")]
        public void EveryTrainerSubVerbExists(string subVerb)
        {
            CliRun listing = Cli.Run("trainer", "--help");
            Assert.Equal(0, listing.ExitCode);
            Assert.Contains(subVerb, listing.StdOut);

            CliRun subHelp = Cli.Run("trainer", subVerb, "--help");
            Assert.Equal(0, subHelp.ExitCode);
        }

        [Fact]
        public void TheVerbHelpSaysItOnlyAttachesToACopyThisAppLaunched()
        {
            CliRun help = Cli.Run("trainer", "--help");

            Assert.Equal(0, help.ExitCode);
            Assert.Contains("only to a process this app launched", help.StdOut);
        }

        [Fact]
        public void SetHelpSaysItReReadsBeforeItWrites()
        {
            CliRun help = Cli.Run("trainer", "set", "--help");

            Assert.Equal(0, help.ExitCode);
            Assert.Contains("re-reading", help.StdOut);
            Assert.Contains("believable", help.StdOut);
        }

        [Theory]
        [InlineData("status")]
        [InlineData("read")]
        public void NoRunningCopyIsAVerdictAboutTheWorld_NotAToolError(string subVerb)
        {
            using var scratch = new CliScratch();

            CliRun run = Cli.Run("trainer", subVerb, "--json");

            Assert.Equal(2, run.ExitCode);
            JsonElement envelope = run.Envelope();
            Assert.False(envelope.GetProperty("ok").GetBoolean());
            Assert.Equal($"trainer.{subVerb}", envelope.GetProperty("command").GetString());
            Assert.Equal(2, envelope.GetProperty("exitCode").GetInt32());
            Assert.Equal("data", envelope.GetProperty("error").GetProperty("kind").GetString());
            Assert.Contains("No safe copy", envelope.GetProperty("error").GetProperty("message").GetString());
        }

        [Fact]
        public void SettingNothingIsAUsageError_AndNamesTheFlags()
        {
            using var scratch = new CliScratch();

            CliRun run = Cli.Run("trainer", "set", "--json");

            Assert.Equal(1, run.ExitCode);
            JsonElement error = run.Envelope().GetProperty("error");
            Assert.Equal("usage", error.GetProperty("kind").GetString());
            Assert.Contains("--life", error.GetProperty("message").GetString());
        }

        [Fact]
        public void SettingAValueWithNothingRunningIsAVerdictAndWritesNothing()
        {
            using var scratch = new CliScratch();

            CliRun run = Cli.Run("trainer", "set", "--life", "100", "--json");

            Assert.Equal(2, run.ExitCode);
            JsonElement envelope = run.Envelope();
            Assert.Equal("trainer.set", envelope.GetProperty("command").GetString());
            Assert.Equal("data", envelope.GetProperty("error").GetProperty("kind").GetString());
        }

        [Fact]
        public void AnUnregisteredProcessIdIsRefusedWithoutBeingOpened()
        {
            using var scratch = new CliScratch();

            CliRun run = Cli.Run("trainer", "read", "--pid", "999999", "--json");

            Assert.Equal(2, run.ExitCode);
            JsonElement envelope = run.Envelope();
            Assert.Contains(
                "not a managed safe-copy process",
                envelope.GetProperty("error").GetProperty("message").GetString());
            Assert.False(envelope.GetProperty("data").GetProperty("attached").GetBoolean());
        }

        [Fact]
        public void ANonPositiveProcessIdIsAUsageError()
        {
            using var scratch = new CliScratch();

            CliRun run = Cli.Run("trainer", "status", "--pid", "0", "--json");

            Assert.Equal(1, run.ExitCode);
            Assert.Equal("usage", run.Envelope().GetProperty("error").GetProperty("kind").GetString());
        }

        [Fact]
        public void UnderJsonStdoutStaysASingleParseableDocument()
        {
            using var scratch = new CliScratch();

            // Every one of these takes a different route out of the verb, and all of them have to
            // leave stdout parseable so a caller can branch on the envelope rather than on text.
            foreach (string[] args in new[]
                     {
                         new[] { "trainer", "status", "--json" },
                         new[] { "trainer", "read", "--json" },
                         new[] { "trainer", "set", "--json" },
                         new[] { "trainer", "set", "--shields", "50", "--json" },
                     })
            {
                CliRun run = Cli.Run(args);
                _ = run.Envelope();
                Assert.NotEqual(0, run.ExitCode);
            }
        }
    }
}
