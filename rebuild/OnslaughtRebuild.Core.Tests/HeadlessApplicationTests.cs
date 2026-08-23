// SPDX-License-Identifier: GPL-3.0-or-later

using System.Text.Json;
using OnslaughtRebuild.Client;
using OnslaughtRebuild.Core;
using OnslaughtRebuild.Headless;
using OnslaughtRebuild.TestSupport;

namespace OnslaughtRebuild.Core.Tests;

public sealed class HeadlessApplicationTests
{
    [Fact]
    public void DefaultTape_ReplaysDeterministicallyWithoutEmbeddedExpectation()
    {
        using var output = new StringWriter();
        using var error = new StringWriter();

        int exitCode = HeadlessApplication.Run(
            ["--repeat", "2"],
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
    public void DefaultTape_TraceAndStateHashesMatchThePinnedFirstFlightFingerprint()
    {
        // Owns the first-flight.v1.json fingerprint (838 ticks, seed
        // 2836905711) for this revision, per rebuild/DETERMINISM.md: a
        // behavior change that legitimately moves Core's trace must re-pin
        // these two values in the same commit as the behavior change. The
        // native Godot smoke pins the 2148-tick rendered path separately.
        using var output = new StringWriter();
        using var error = new StringWriter();

        int exitCode = HeadlessApplication.Run(
            ["--expect", "efc818f7708bea67ecaffb5e6acc6807c90f29e7499a69f1891ff407f8388014", "--repeat", "2"],
            output,
            error);

        using JsonDocument result = JsonDocument.Parse(output.ToString());
        Assert.Equal(0, exitCode);
        Assert.Equal(838, result.RootElement.GetProperty("ticks").GetInt32());
        Assert.True(result.RootElement.GetProperty("traceHashChecked").GetBoolean());
        Assert.True(result.RootElement.GetProperty("traceHashVerified").GetBoolean());
        Assert.Equal(
            "efc818f7708bea67ecaffb5e6acc6807c90f29e7499a69f1891ff407f8388014",
            result.RootElement.GetProperty("traceHash").GetString());
        Assert.Equal(
            "0c034978c006049e57833564aba0b10cad00c87e61d5658737e13cc6a389f6ce",
            result.RootElement.GetProperty("finalStateHash").GetString());
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
              "schemaVersion": "onslaught-rebuild-command-tape.v4",
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
    public void DefaultTape_IgnoresCurrentDirectoryShadow()
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
            Assert.Equal("none", result.RootElement.GetProperty("verificationSource").GetString());
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
                ["--tape", tapePath, "--repeat", "100"],
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

    private static string WriteTemporaryTape(string content)
    {
        string path = Path.Combine(
            Path.GetTempPath(),
            $"onslaught-rebuild-test-{Guid.NewGuid():N}.json");
        File.WriteAllText(path, content);
        return path;
    }

    private static Level100ActorDefinitionSet LoadMaterializedActorDefinitions()
    {
        string path = Path.Combine(
            AppContext.BaseDirectory,
            "Assets",
            "Level100",
            "StaticWorld",
            "level100-static-world.json");
        return Level100ActorDefinitionManifest.Decode(File.ReadAllBytes(path));
    }

    // ------------------------------------------------------------------
    // P8 stage 1: a recorded v5 tape replays under --expect, and the
    // create-new / no-overwrite persistence control refuses an existing
    // destination before any bytes are touched.
    // ------------------------------------------------------------------

    [Fact]
    public void RecordedTape_RoundTripsThroughHeadlessExpectGate()
    {
        const uint seed = 23;
        const long oneCoreStepTicks = 500_000;
        // The REAL materialized Level 100 manifest, exactly what
        // HeadlessApplication.LoadActorDefinitions resolves — a recorded tape
        // only replays under the same actor set it was captured with.
        var definitions = LoadMaterializedActorDefinitions();
        var recorder = new CommandTapeRecorder();
        var session = new InteractiveSession(seed, definitions);
        session.EnableRecording(recorder);

        const int firstRunControlTick = 665;
        for (int tick = 0; tick < firstRunControlTick; tick++)
        {
            session.AdvanceFrameTicks(oneCoreStepTicks);
        }
        Assert.True(session.CurrentSnapshot.Level100PlayerControlEnabled);

        // Tick 665: pointer motion becomes the deterministic post-quantise
        // analogue permille axis; movement and the physical fire-button level
        // are sampled, and one zoom edge is consumed.
        session.QueuePointerMotionMilliPixels(9_000, -4_000);
        session.QueueZoomIn();
        session.ObserveInput(new InteractiveInput(0, 1, true, false, false));
        session.AdvanceFrameTicks(oneCoreStepTicks);
        SimInput firstConsumed = Assert.NotNull(session.LastConsumedInput);
        Assert.True(firstConsumed.HasAction(SimActions.ChargeWeapon));
        Assert.True(firstConsumed.HasAction(SimActions.ZoomIn));
        Assert.NotEqual(0, firstConsumed.LookXAnalogPermille);
        Assert.NotEqual(0, firstConsumed.LookYAnalogPermille);

        // Tick 666 stays held: ChargeWeapon is a level and can coalesce with
        // otherwise-identical input; the zoom edge does not repeat.
        session.AdvanceFrameTicks(oneCoreStepTicks);
        SimInput heldConsumed = Assert.NotNull(session.LastConsumedInput);
        Assert.True(heldConsumed.HasAction(SimActions.ChargeWeapon));
        Assert.False(heldConsumed.HasAction(SimActions.ZoomIn));

        // Tick 667 releases the same physical button (one Fire edge), consumes
        // a movement pulse and the opposite zoom edge. These exact edge bits
        // must survive the tape round trip as one-tick spans.
        session.ObserveInput(InteractiveInput.Idle);
        session.QueueMovementPulse(1, 0);
        session.QueueZoomOut();
        session.AdvanceFrameTicks(oneCoreStepTicks);
        SimInput releasedConsumed = Assert.NotNull(session.LastConsumedInput);
        Assert.True(releasedConsumed.HasAction(SimActions.Fire));
        Assert.True(releasedConsumed.HasAction(SimActions.ZoomOut));
        Assert.Equal(1, releasedConsumed.MoveX);

        WorldSnapshot final = session.CurrentSnapshot;
        CommandTape probe = CommandTapeCodec.Deserialize(
            CommandTapeCodec.Serialize(recorder.Build("probe", seed)));
        string traceHash = ReplayRunner.Run(probe, definitions).TraceHash;
        CommandTape tape = CommandTapeCodec.Deserialize(
            CommandTapeCodec.Serialize(recorder.Build(
                "recorded-headless",
                seed,
                final.Tick,
                StateHasher.ComputeHex(final),
                traceHash)));
        string tapePath = WriteTemporaryTape(CommandTapeCodec.Serialize(tape));

        // Capture-side equivalence before the file-level gate: serializing and
        // deserializing preserves the session's final and trace hashes.
        ReplayResult replayed = ReplayRunner.Run(tape, definitions);
        Assert.Equal(traceHash, replayed.TraceHash);
        Assert.Equal(StateHasher.ComputeHex(final), replayed.FinalStateHash);

        try
        {
            using var output = new StringWriter();
            using var error = new StringWriter();

            int exitCode = HeadlessApplication.Run(
                ["--tape", tapePath, "--expect", traceHash, "--repeat", "2"],
                output,
                error);

            Assert.Equal(0, exitCode);
            Assert.Equal(string.Empty, error.ToString());
            using JsonDocument result = JsonDocument.Parse(output.ToString());
            Assert.True(result.RootElement.GetProperty("traceHashVerified").GetBoolean());
        }
        finally
        {
            File.Delete(tapePath);
        }
    }

    [Fact]
    public void TapeFileWriteNew_RefusesToOverwriteAnExistingTape()
    {
        var first = new CommandTape(
            CommandTape.CurrentSchemaVersion,
            "first-write",
            5,
            1,
            null,
            null,
            [new CommandSpan(0, 1, 0, 1)]);
        var second = new CommandTape(
            CommandTape.CurrentSchemaVersion,
            "second-write",
            7,
            2,
            null,
            null,
            []);

        string directory = Path.Combine(
            Path.GetTempPath(),
            $"onslaught-rebuild-record-{Guid.NewGuid():N}");
        Directory.CreateDirectory(directory);
        try
        {
            string path = Path.Combine(directory, "recorded.tape.json");

            TapeFile.WriteNew(path, first);
            long lengthBefore = new FileInfo(path).Length;

            IOException refused = Assert.Throws<IOException>(
                () => TapeFile.WriteNew(path, second));

            Assert.Contains("refuses to overwrite", refused.Message, StringComparison.Ordinal);
            Assert.Equal(lengthBefore, new FileInfo(path).Length);
            Assert.Equal(
                "first-write",
                CommandTapeCodec.Deserialize(File.ReadAllText(path)).Name);
        }
        finally
        {
            Directory.Delete(directory, recursive: true);
        }
    }

    [Fact]
    public void TapeFileWriteNew_RejectsCareerSaveAndRetailFileDestinations()
    {
        var tape = new CommandTape(
            CommandTape.CurrentSchemaVersion,
            "path-boundary",
            3,
            1,
            null,
            null,
            []);
        string root = Path.Combine(
            Path.GetTempPath(),
            $"onslaught-rebuild-record-boundary-{Guid.NewGuid():N}");
        Directory.CreateDirectory(root);
        try
        {
            string careerSave = Path.Combine(root, "career.bes");
            string retailExecutable = Path.Combine(root, "BEA.exe");

            Assert.Throws<ArgumentException>(() => TapeFile.WriteNew(careerSave, tape));
            Assert.Throws<ArgumentException>(() => TapeFile.WriteNew(retailExecutable, tape));
            Assert.False(File.Exists(careerSave));
            Assert.False(File.Exists(retailExecutable));
        }
        finally
        {
            Directory.Delete(root, recursive: true);
        }
    }

    [Fact]
    public void TapeFileWriteNew_CreatesMissingDirectoriesAndPersistsLfCanonicalJson()
    {
        var tape = new CommandTape(
            CommandTape.CurrentSchemaVersion,
            "nested",
            3,
            1,
            null,
            null,
            []);
        string root = Path.Combine(
            Path.GetTempPath(),
            $"onslaught-rebuild-record-{Guid.NewGuid():N}");
        string path = Path.Combine(root, "deep", "recorded.tape.json");
        try
        {
            TapeFile.WriteNew(path, tape);

            string json = File.ReadAllText(path);
            Assert.DoesNotContain("\r", json, StringComparison.Ordinal);
            Assert.EndsWith("\n", json, StringComparison.Ordinal);
            Assert.Equal(
                CommandTape.IdentityOf(tape),
                CommandTape.IdentityOf(CommandTapeCodec.Deserialize(json)));
        }
        finally
        {
            if (Directory.Exists(root))
            {
                Directory.Delete(root, recursive: true);
            }
        }
    }
}
