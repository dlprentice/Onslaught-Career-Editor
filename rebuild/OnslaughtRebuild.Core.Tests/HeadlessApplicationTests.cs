// SPDX-License-Identifier: GPL-3.0-or-later

using System.Text.Json;
using OnslaughtRebuild.Core;
using OnslaughtRebuild.Headless;

namespace OnslaughtRebuild.Core.Tests;

public sealed class HeadlessApplicationTests
{
    [Fact]
    public void TapeGolden_IsCheckedAndVerified()
    {
        using var output = new StringWriter();
        using var error = new StringWriter();

        int exitCode = HeadlessApplication.Run(
            ["--repeat", "1"],
            output,
            error);

        using JsonDocument result = JsonDocument.Parse(output.ToString());
        Assert.Equal(0, exitCode);
        Assert.True(result.RootElement.GetProperty("traceHashChecked").GetBoolean());
        Assert.True(result.RootElement.GetProperty("traceHashVerified").GetBoolean());
        Assert.True(result.RootElement.GetProperty("finalStateHashChecked").GetBoolean());
        Assert.True(result.RootElement.GetProperty("finalStateHashVerified").GetBoolean());
        Assert.Equal(
            result.RootElement.GetProperty("expectedTraceHash").GetString(),
            result.RootElement.GetProperty("traceHash").GetString());
        Assert.Equal(
            result.RootElement.GetProperty("expectedFinalStateHash").GetString(),
            result.RootElement.GetProperty("finalStateHash").GetString());
        Assert.Equal(
            "headless-built-in-golden",
            result.RootElement.GetProperty("verificationSource").GetString());
        Assert.Equal(string.Empty, error.ToString());
    }

    [Fact]
    public void NoVerify_ReportsThatNoGoldenWasChecked()
    {
        string tapePath = Path.Combine(AppContext.BaseDirectory, "scenarios", "first-flight.v1.json");
        using var output = new StringWriter();
        using var error = new StringWriter();

        int exitCode = HeadlessApplication.Run(
            ["--tape", tapePath, "--no-verify", "--repeat", "1"],
            output,
            error);

        using JsonDocument result = JsonDocument.Parse(output.ToString());
        Assert.Equal(0, exitCode);
        Assert.False(result.RootElement.GetProperty("traceHashChecked").GetBoolean());
        Assert.Equal(JsonValueKind.Null, result.RootElement.GetProperty("traceHashVerified").ValueKind);
        Assert.False(result.RootElement.GetProperty("finalStateHashChecked").GetBoolean());
        Assert.Equal(JsonValueKind.Null, result.RootElement.GetProperty("finalStateHashVerified").ValueKind);
        Assert.Equal(JsonValueKind.Null, result.RootElement.GetProperty("expectedTraceHash").ValueKind);
        Assert.Equal("none", result.RootElement.GetProperty("verificationSource").GetString());
        Assert.Equal(string.Empty, error.ToString());
    }

    [Fact]
    public void InvalidExpectedHash_IsRejectedAsUsageError()
    {
        string tapePath = Path.Combine(AppContext.BaseDirectory, "scenarios", "first-flight.v1.json");
        using var output = new StringWriter();
        using var error = new StringWriter();

        int exitCode = HeadlessApplication.Run(
            ["--tape", tapePath, "--expect", "not-a-sha256"],
            output,
            error);

        Assert.Equal(1, exitCode);
        Assert.Equal(string.Empty, output.ToString());
        Assert.Contains("64-character SHA-256", error.ToString(), StringComparison.Ordinal);
    }

    [Fact]
    public void MalformedTape_IsReportedWithoutEscapingTheApplicationBoundary()
    {
        string tapePath = WriteTemporaryTape("""
            {
              "schemaVersion": "onslaught-rebuild-command-tape.v1",
              "name": "missing-spans",
              "seed": 1,
              "durationTicks": 10,
              "expectedFinalStateHash": null
            }
            """);

        try
        {
            using var output = new StringWriter();
            using var error = new StringWriter();

            int exitCode = HeadlessApplication.Run(["--tape", tapePath], output, error);

            Assert.Equal(1, exitCode);
            Assert.Equal(string.Empty, output.ToString());
            Assert.Contains("spans are required", error.ToString(), StringComparison.Ordinal);
        }
        finally
        {
            File.Delete(tapePath);
        }
    }

    [Fact]
    public void ExplicitTape_RequiresIndependentExpectationUnlessVerificationIsDisabled()
    {
        string sourcePath = Path.Combine(AppContext.BaseDirectory, "scenarios", "first-flight.v1.json");
        using var output = new StringWriter();
        using var error = new StringWriter();

        int exitCode = HeadlessApplication.Run(["--tape", sourcePath], output, error);

        Assert.Equal(1, exitCode);
        Assert.Equal(string.Empty, output.ToString());
        Assert.Contains("requires --expect", error.ToString(), StringComparison.Ordinal);
    }

    [Fact]
    public void WrongExpectedHash_ReportsVerifiedFalseAndReturnsMismatchExitCode()
    {
        string tapePath = Path.Combine(AppContext.BaseDirectory, "scenarios", "first-flight.v1.json");
        using var output = new StringWriter();
        using var error = new StringWriter();

        int exitCode = HeadlessApplication.Run(
            ["--tape", tapePath, "--expect", new string('0', 64), "--repeat", "1"],
            output,
            error);

        using JsonDocument result = JsonDocument.Parse(output.ToString());
        Assert.Equal(2, exitCode);
        Assert.True(result.RootElement.GetProperty("traceHashChecked").GetBoolean());
        Assert.False(result.RootElement.GetProperty("traceHashVerified").GetBoolean());
        Assert.False(result.RootElement.GetProperty("finalStateHashChecked").GetBoolean());
        Assert.Contains("did not match", error.ToString(), StringComparison.Ordinal);
    }

    [Fact]
    public void DirectoryTapePath_IsReportedWithoutEscapingTheApplicationBoundary()
    {
        string directoryPath = Path.Combine(AppContext.BaseDirectory, "scenarios");
        using var output = new StringWriter();
        using var error = new StringWriter();

        int exitCode = HeadlessApplication.Run(["--tape", directoryPath], output, error);

        Assert.Equal(1, exitCode);
        Assert.Equal(string.Empty, output.ToString());
        Assert.NotEqual(string.Empty, error.ToString());
    }

    [Fact]
    public void OversizedTape_IsRejectedBeforeJsonParsing()
    {
        string tapePath = WriteTemporaryTape(string.Empty);
        try
        {
            using (var stream = new FileStream(tapePath, FileMode.Open, FileAccess.Write, FileShare.None))
            {
                stream.SetLength((8 * 1024 * 1024) + 1);
            }

            using var output = new StringWriter();
            using var error = new StringWriter();

            int exitCode = HeadlessApplication.Run(["--tape", tapePath], output, error);

            Assert.Equal(1, exitCode);
            Assert.Equal(string.Empty, output.ToString());
            Assert.Contains("8 MiB", error.ToString(), StringComparison.Ordinal);
        }
        finally
        {
            File.Delete(tapePath);
        }
    }

    [Fact]
    public void DefaultTape_IgnoresCurrentDirectoryShadowAndUsesBuiltInGolden()
    {
        string originalDirectory = Environment.CurrentDirectory;
        string shadowRoot = Path.Combine(
            Path.GetTempPath(),
            $"onslaught-rebuild-shadow-{Guid.NewGuid():N}");
        string shadowScenarioDirectory = Path.Combine(shadowRoot, "rebuild", "scenarios");
        Directory.CreateDirectory(shadowScenarioDirectory);

        try
        {
            var shadowTape = new CommandTape(
                CommandTape.CurrentSchemaVersion,
                "cwd-shadow",
                77,
                1,
                null,
                null,
                []);
            ReplayResult shadowResult = ReplayRunner.Run(shadowTape);
            shadowTape = shadowTape with
            {
                ExpectedFinalStateHash = shadowResult.FinalStateHash,
                ExpectedTraceHash = shadowResult.TraceHash,
            };
            File.WriteAllText(
                Path.Combine(shadowScenarioDirectory, "first-flight.v1.json"),
                CommandTapeCodec.Serialize(shadowTape));
            Environment.CurrentDirectory = shadowRoot;

            using var output = new StringWriter();
            using var error = new StringWriter();
            int exitCode = HeadlessApplication.Run([], output, error);

            using JsonDocument result = JsonDocument.Parse(output.ToString());
            Assert.Equal(0, exitCode);
            Assert.Equal("first-flight", result.RootElement.GetProperty("tape").GetString());
            Assert.Equal(
                "headless-built-in-golden",
                result.RootElement.GetProperty("verificationSource").GetString());
            Assert.Equal(string.Empty, error.ToString());
        }
        finally
        {
            Environment.CurrentDirectory = originalDirectory;
            Directory.Delete(shadowRoot, recursive: true);
        }
    }

    [Fact]
    public void CombinedReplayWorkOverLimit_IsRejectedBeforeSimulation()
    {
        var tape = new CommandTape(
            CommandTape.CurrentSchemaVersion,
            "work-limit",
            1,
            1_001,
            null,
            null,
            []);
        string tapePath = WriteTemporaryTape(CommandTapeCodec.Serialize(tape));

        try
        {
            using var output = new StringWriter();
            using var error = new StringWriter();

            int exitCode = HeadlessApplication.Run(
                ["--tape", tapePath, "--no-verify", "--repeat", "100"],
                output,
                error);

            Assert.Equal(1, exitCode);
            Assert.Equal(string.Empty, output.ToString());
            Assert.Contains("100,000", error.ToString(), StringComparison.Ordinal);
        }
        finally
        {
            File.Delete(tapePath);
        }
    }

    [Fact]
    public void BuiltInTapeDeclarationDrift_FailsClosedAgainstIndependentConstants()
    {
        string tapePath = Path.Combine(AppContext.BaseDirectory, "scenarios", "first-flight.v1.json");
        string original = File.ReadAllText(tapePath);
        CommandTape tape = CommandTapeCodec.Deserialize(original);

        try
        {
            File.WriteAllText(
                tapePath,
                CommandTapeCodec.Serialize(tape with { ExpectedTraceHash = new string('0', 64) }));
            using var output = new StringWriter();
            using var error = new StringWriter();

            int exitCode = HeadlessApplication.Run([], output, error);

            Assert.Equal(1, exitCode);
            Assert.Equal(string.Empty, output.ToString());
            Assert.Contains("independent headless golden", error.ToString(), StringComparison.Ordinal);
        }
        finally
        {
            File.WriteAllText(tapePath, original);
        }
    }

    private static string WriteTemporaryTape(string content)
    {
        string path = Path.Combine(
            Path.GetTempPath(),
            $"onslaught-rebuild-test-{Guid.NewGuid():N}.json");
        File.WriteAllText(path, content);
        return path;
    }
}
