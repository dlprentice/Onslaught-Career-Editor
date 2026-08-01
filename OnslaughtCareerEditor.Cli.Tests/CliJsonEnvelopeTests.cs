using System.Text.Json;
using Xunit;

namespace OnslaughtCareerEditor.Cli.Tests
{
    /// <summary>
    /// The envelope is the contract an agent parses. Its shape has to be identical on success and on
    /// failure, or every caller needs a special case for the failure path - which is exactly when
    /// parsing matters most.
    /// </summary>
    [Collection(CliCollection.Name)]
    public class CliJsonEnvelopeTests
    {
        private static void AssertEnvelopeShape(JsonElement envelope, string expectedCommand, bool expectedOk)
        {
            Assert.Equal(JsonValueKind.Object, envelope.ValueKind);
            Assert.Equal(expectedOk, envelope.GetProperty("ok").GetBoolean());
            Assert.Equal(expectedCommand, envelope.GetProperty("command").GetString());
            Assert.True(envelope.TryGetProperty("exitCode", out JsonElement exitCode));
            Assert.Equal(JsonValueKind.Number, exitCode.ValueKind);
            Assert.Equal(JsonValueKind.Array, envelope.GetProperty("warnings").ValueKind);
        }

        [Theory]
        [InlineData(new[] { "version" }, "version")]
        [InlineData(new[] { "config", "show" }, "config.show")]
        [InlineData(new[] { "copy", "list" }, "copy.list")]
        [InlineData(new[] { "process", "list" }, "process.list")]
        [InlineData(new[] { "patch", "list" }, "patch.list")]
        public void SuccessfulVerbsEmitTheEnvelopeWithTheirDottedCommandName(string[] args, string expectedCommand)
        {
            using var scratch = new CliScratch();

            CliRun run = Cli.Run(args.Append("--json").ToArray());

            Assert.Equal(0, run.ExitCode);
            JsonElement envelope = run.Envelope();
            AssertEnvelopeShape(envelope, expectedCommand, expectedOk: true);
            Assert.Equal(JsonValueKind.Null, envelope.TryGetProperty("error", out JsonElement error)
                ? error.ValueKind
                : JsonValueKind.Null);
        }

        [Fact]
        public void AUsageFailureEmitsTheSameEnvelopeWithAUsageError()
        {
            using var scratch = new CliScratch();

            CliRun run = Cli.Run("saves", "analyze", scratch.Path_("missing.bes"), "--json");

            Assert.Equal(1, run.ExitCode);
            JsonElement envelope = run.Envelope();
            AssertEnvelopeShape(envelope, "saves.analyze", expectedOk: false);
            Assert.Equal(1, envelope.GetProperty("exitCode").GetInt32());

            JsonElement error = envelope.GetProperty("error");
            Assert.Equal("usage", error.GetProperty("kind").GetString());
            Assert.Contains("not found", error.GetProperty("message").GetString());
        }

        [Fact]
        public void ADataVerdictEmitsTheSameEnvelopeWithADataError()
        {
            using var scratch = new CliScratch();
            string notASave = scratch.NonSaveFixture("bogus.bes");

            CliRun run = Cli.Run("saves", "analyze", notASave, "--json");

            Assert.Equal(2, run.ExitCode);
            JsonElement envelope = run.Envelope();
            AssertEnvelopeShape(envelope, "saves.analyze", expectedOk: false);
            Assert.Equal(2, envelope.GetProperty("exitCode").GetInt32());
            Assert.Equal("data", envelope.GetProperty("error").GetProperty("kind").GetString());
        }

        /// <summary>
        /// Under --json, stdout carries the document and nothing else. A banner line printed alongside it
        /// would break every caller that pipes stdout into a parser.
        /// </summary>
        [Fact]
        public void JsonModeKeepsStdOutPureEvenWhenTheVerbAlsoHasHumanOutput()
        {
            using var scratch = new CliScratch();

            CliRun run = Cli.Run("copy", "list", "--json");

            Assert.Equal(0, run.ExitCode);
            _ = run.Envelope();
            Assert.DoesNotContain("Safe copies under:", run.StdOut);
        }

        /// <summary>
        /// Warnings must ride inside the document. In text mode they go to stderr, but a JSON caller
        /// reading only stdout would otherwise never see them.
        /// </summary>
        [Fact]
        public void WarningsAreCarriedInsideTheEnvelopeRatherThanPrintedBesideIt()
        {
            using var scratch = new CliScratch();

            // Stage a workspace so the verb gets past target resolution and actually reaches selection
            // defaulting. The staged bytes are not a real executable, which is fine: the warning is
            // emitted before the engine ever inspects the file's identity.
            string source = scratch.NonSaveFixture("source/BEA.exe");
            CliRun staged = Cli.Run("patch", "stage", source, "--json");
            Assert.Equal(0, staged.ExitCode);
            string workspaceId = staged.Envelope().GetProperty("data").GetProperty("workspaceId").GetString()!;

            // No selection given, so the verb reports the default it fell back to.
            CliRun run = Cli.Run("patch", "verify", workspaceId, "--json");

            JsonElement warnings = run.Envelope().GetProperty("warnings");
            Assert.Equal(JsonValueKind.Array, warnings.ValueKind);
            Assert.Contains(
                warnings.EnumerateArray().Select(w => w.GetString() ?? string.Empty),
                text => text.Contains("defaulting to the", StringComparison.OrdinalIgnoreCase));
            Assert.DoesNotContain("Warning:", run.StdOut);
        }

        /// <summary>
        /// An unrecognised executable is a verdict about the target, not a broken invocation: the engine
        /// ran, read the bytes, and refused to treat them as a known clean retail BEA.exe.
        /// </summary>
        [Fact]
        public void AnUnknownPatchTargetIdentityIsReportedAsAVerdict()
        {
            using var scratch = new CliScratch();
            string source = scratch.NonSaveFixture("source/BEA.exe");
            CliRun staged = Cli.Run("patch", "stage", source, "--json");
            string workspaceId = staged.Envelope().GetProperty("data").GetProperty("workspaceId").GetString()!;

            CliRun run = Cli.Run("patch", "verify", workspaceId);

            Assert.Equal(2, run.ExitCode);
        }

        [Fact]
        public void AnalysisIsEmittedAsStructuredDataNotOnlyAsRenderedText()
        {
            using var scratch = new CliScratch();
            string? baseline = scratch.TryCopyRealBaselineSave("baseline.bes");
            if (baseline is null)
            {
                // No retail installation on this machine, and saves are never synthesized.
                return;
            }

            CliRun run = Cli.Run("saves", "analyze", baseline, "--json");

            Assert.Equal(0, run.ExitCode);
            JsonElement data = run.Envelope().GetProperty("data");
            Assert.True(data.GetProperty("isValid").GetBoolean());

            // The structured document, not just the pre-rendered report string.
            JsonElement metrics = data.GetProperty("document").GetProperty("metrics");
            Assert.Equal(JsonValueKind.Array, metrics.ValueKind);
            Assert.NotEmpty(metrics.EnumerateArray());

            JsonElement analysis = data.GetProperty("analysis");
            Assert.Equal(JsonValueKind.Array, analysis.GetProperty("killCounts").ValueKind);
            Assert.True(analysis.GetProperty("goodies").TryGetProperty("new", out _));
        }
    }
}
