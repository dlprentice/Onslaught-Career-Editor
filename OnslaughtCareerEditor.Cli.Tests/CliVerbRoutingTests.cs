using Xunit;

namespace OnslaughtCareerEditor.Cli.Tests
{
    /// <summary>
    /// Dispatch is by first token: a known verb reaches the verb tree, anything else reaches the legacy
    /// flag-style command. Both halves have to keep working, because scripts written against the old
    /// form are still expected to run.
    /// </summary>
    [Collection(CliCollection.Name)]
    public class CliVerbRoutingTests
    {
        [Theory]
        [InlineData("config")]
        [InlineData("saves")]
        [InlineData("goodies")]
        [InlineData("options")]
        [InlineData("copy")]
        [InlineData("patch")]
        [InlineData("process")]
        [InlineData("version")]
        [InlineData("lore")]
        [InlineData("media")]
        public void EveryTopLevelVerbIsRoutedAndDocumented(string verb)
        {
            CliRun help = Cli.Run("--help");
            Assert.Equal(0, help.ExitCode);
            Assert.Contains(verb, help.StdOut);

            // Reaching the verb's own help proves it is wired up, without running anything destructive.
            CliRun verbHelp = Cli.Run(verb, "--help");
            Assert.Equal(0, verbHelp.ExitCode);
        }

        [Theory]
        [InlineData("config", "show")]
        [InlineData("config", "set-game-dir")]
        [InlineData("config", "detect")]
        [InlineData("saves", "list")]
        [InlineData("saves", "analyze")]
        [InlineData("saves", "compare")]
        [InlineData("saves", "patch")]
        [InlineData("goodies", "list")]
        [InlineData("goodies", "set")]
        [InlineData("options", "show")]
        [InlineData("options", "edit")]
        [InlineData("copy", "list")]
        [InlineData("copy", "create")]
        [InlineData("copy", "launch")]
        [InlineData("copy", "stop")]
        [InlineData("copy", "delete")]
        [InlineData("patch", "list")]
        [InlineData("patch", "stage")]
        [InlineData("patch", "plan")]
        [InlineData("patch", "apply")]
        [InlineData("patch", "verify")]
        [InlineData("patch", "restore")]
        [InlineData("process", "list")]
        [InlineData("process", "stop")]
        [InlineData("lore", "search")]
        [InlineData("lore", "show")]
        [InlineData("media", "list")]
        public void EverySubVerbExists(string verb, string subVerb)
        {
            CliRun listing = Cli.Run(verb, "--help");
            Assert.Equal(0, listing.ExitCode);
            Assert.Contains(subVerb, listing.StdOut);

            CliRun subHelp = Cli.Run(verb, subVerb, "--help");
            Assert.Equal(0, subHelp.ExitCode);
        }

        [Fact]
        public void HelpDocumentsTheExitCodeScheme()
        {
            CliRun help = Cli.Run("--help");

            Assert.Equal(0, help.ExitCode);
            Assert.Contains("Exit codes:", help.StdOut);
            Assert.Contains("usage or tool error", help.StdOut);
            Assert.Contains("the data says no", help.StdOut);
        }

        [Fact]
        public void NoArgumentsPrintsHelpAndReportsAUsageError()
        {
            CliRun run = Cli.Run();

            Assert.Equal(1, run.ExitCode);
            Assert.Contains("Usage:", run.StdOut);
        }

        /// <summary>
        /// The legacy form is reached by any non-verb first token. This is the guarantee that existing
        /// invocations did not stop working the day verbs arrived.
        /// </summary>
        [Fact]
        public void ANonVerbFirstArgumentReachesTheLegacyCommand()
        {
            using var scratch = new CliScratch();
            string missing = scratch.Path_("no-such-file.bes");

            CliRun run = Cli.Run(missing, "--analyze");

            Assert.Equal(1, run.ExitCode);
            Assert.Contains("Input file not found", run.StdErr);
        }

        [Fact]
        public void TheLegacyFormStillAcceptsItsOriginalFlagSurface()
        {
            using var scratch = new CliScratch();
            string input = scratch.NonSaveFixture("legacy.bes");

            // --show-config is a legacy-only flag with no positional input; it must still be understood.
            CliRun config = Cli.Run("--show-config");
            Assert.Equal(0, config.ExitCode);
            Assert.Contains("Configuration", config.StdOut);

            // A legacy patch invocation parses its flags and reaches the patcher rather than erroring
            // out on unrecognised arguments.
            CliRun patch = Cli.Run(input, scratch.Path_("out.bes"), "--rank", "A", "--kills", "500");
            Assert.NotEqual(1, patch.ExitCode);
        }

        [Fact]
        public void VersionReportsTheCatalogIdentitiesAnAgentNeeds()
        {
            CliRun run = Cli.Run("version", "--json");

            Assert.Equal(0, run.ExitCode);
            var data = run.Envelope().GetProperty("data");
            Assert.False(string.IsNullOrWhiteSpace(data.GetProperty("version").GetString()));
            Assert.False(string.IsNullOrWhiteSpace(data.GetProperty("safeCopyRoot").GetString()));
            Assert.False(string.IsNullOrWhiteSpace(data.GetProperty("patchBenchRoot").GetString()));
        }
    }
}
