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

    // ------------------------------------------------------------------
    // P8 correction (task t_877b3e70): fail-closed destination boundary.
    // A fresh absolute .json is REFUSED before any directory creation or
    // file open when it lies inside a retail-install layout (an existing
    // ancestor holding BEA.exe beside a data directory) or behind an
    // existing reparse-point ancestor, and the refusals leave neither the
    // target nor any missing target parent behind. An ordinary fresh
    // destination outside protected storage stays allowed.
    // ------------------------------------------------------------------

    private static CommandTape BoundaryProbeTape() => new(
        CommandTape.CurrentSchemaVersion,
        "boundary-probe",
        3,
        1,
        null,
        null,
        []);

    [Fact]
    public void TapeFileWriteNew_RejectsFreshJsonUnderSyntheticRetailInstallShape()
    {
        string retailRoot = Path.Combine(
            Path.GetTempPath(),
            $"onslaught-rebuild-retail-{Guid.NewGuid():N}");
        Directory.CreateDirectory(Path.Combine(retailRoot, "data"));
        // Synthetic markers only: the boundary keys on the retail-install
        // SHAPE (BEA.exe beside a data directory), never on retail bytes.
        File.WriteAllText(Path.Combine(retailRoot, "BEA.exe"), "synthetic");

        try
        {
            // Inside the existing fake retail data directory...
            string dataDestination = Path.Combine(retailRoot, "data", "recording.json");
            Assert.Throws<ArgumentException>(
                () => TapeFile.WriteNew(dataDestination, BoundaryProbeTape()));
            Assert.False(File.Exists(dataDestination));

            // ...and under a career-save-style directory whose parents do not
            // exist yet: the refusal must fire before Directory.CreateDirectory.
            string saveDestination = Path.Combine(retailRoot, "savegames", "nested", "tape.json");
            Assert.Throws<ArgumentException>(
                () => TapeFile.WriteNew(saveDestination, BoundaryProbeTape()));
            Assert.False(File.Exists(saveDestination));
            Assert.False(Directory.Exists(Path.Combine(retailRoot, "savegames")));
        }
        finally
        {
            Directory.Delete(retailRoot, recursive: true);
        }
    }

    [Fact]
    public void TapeFileWriteNew_RejectsExistingReparsePointAncestors_WhereSupported()
    {
        string baseRoot = Path.Combine(
            Path.GetTempPath(),
            $"onslaught-rebuild-link-{Guid.NewGuid():N}");
        string plainTarget = Path.Combine(baseRoot, "plain-target");
        Directory.CreateDirectory(plainTarget);
        string link = Path.Combine(baseRoot, "link");
        if (!TryCreateReparseDirectoryLink(link, plainTarget))
        {
            // This host cannot mint junctions or symlinks for the test user.
            // The card scopes the reparse control to "where supported"; the
            // ordinary-destination control still pins the safe path.
            Directory.Delete(baseRoot, recursive: true);
            return;
        }

        try
        {
            string destination = Path.Combine(link, "recording.json");

            ArgumentException refused = Assert.Throws<ArgumentException>(
                () => TapeFile.WriteNew(destination, BoundaryProbeTape()));

            Assert.Contains("reparse", refused.Message, StringComparison.Ordinal);
            // Nothing may land through the link either.
            Assert.False(File.Exists(Path.Combine(plainTarget, "recording.json")));
        }
        finally
        {
            // Remove the junction itself before the recursive sweep; on some
            // hosts .NET's recursive delete denies the reparse point directly.
            if (Directory.Exists(link))
            {
                Directory.Delete(link, recursive: false);
            }

            Directory.Delete(baseRoot, recursive: true);
        }
    }

    [Fact]
    public void TapeFileWriteNew_AllowsOrdinaryFreshDestinationOutsideProtectedStorage()
    {
        string ordinaryRoot = Path.Combine(
            Path.GetTempPath(),
            $"onslaught-rebuild-ordinary-{Guid.NewGuid():N}");
        string unrelatedProtectedRoot = Path.Combine(
            Path.GetTempPath(),
            $"onslaught-rebuild-unrelated-{Guid.NewGuid():N}");
        Directory.CreateDirectory(unrelatedProtectedRoot);
        string destination = Path.Combine(ordinaryRoot, "sessions", "ordinary.tape.json");

        try
        {
            // Supplying a protected root that the destination has nothing to
            // do with must not disturb the ordinary safe write.
            TapeFile.WriteNew(destination, BoundaryProbeTape(), [unrelatedProtectedRoot]);

            Assert.True(File.Exists(destination));
            Assert.Equal(
                CommandTape.IdentityOf(BoundaryProbeTape()),
                CommandTape.IdentityOf(CommandTapeCodec.Deserialize(File.ReadAllText(destination))));
        }
        finally
        {
            Directory.Delete(ordinaryRoot, recursive: true);
            Directory.Delete(unrelatedProtectedRoot, recursive: true);
        }
    }

    // ------------------------------------------------------------------
    // P8 correction v2 (task t_aa8698d0): Windows DOS/extended namespace
    // identity. A destination written as \\?\C:\...\known\extended.json is
    // THE SAME FILE as C:\...\known\extended.json, so the boundary must
    // evaluate one canonical identity: refusal fires for the alias exactly
    // when it fires for the ordinary form, and no write may proceed through
    // a namespace form the boundary did not evaluate.
    // ------------------------------------------------------------------

    [Fact]
    public void TapeFileWriteNew_RejectsExtendedNamespaceAliasInsideSuppliedKnownRoot()
    {
        string knownRoot = Path.Combine(
            Path.GetTempPath(),
            $"onslaught-rebuild-known-{Guid.NewGuid():N}");
        Directory.CreateDirectory(knownRoot);

        try
        {
            // The destination lives under a MISSING parent inside the known
            // root, so a refusal that fires late would leave creation debris
            // behind and the test can see it.
            string ordinary = Path.Combine(knownRoot, "missing", "ordinary.json");
            string extended = @"\\?\" + ordinary;

            Assert.Throws<ArgumentException>(
                () => TapeFile.WriteNew(ordinary, BoundaryProbeTape(), [knownRoot]));
            Assert.False(File.Exists(ordinary));
            Assert.False(Directory.Exists(Path.Combine(knownRoot, "missing")));

            ArgumentException refused = Assert.Throws<ArgumentException>(
                () => TapeFile.WriteNew(extended, BoundaryProbeTape(), [knownRoot]));
            Assert.Contains("game or save root", refused.Message, StringComparison.Ordinal);

            // The alias must not have created the file at its ordinary
            // identity either: both spellings name ONE destination, and the
            // refusal must precede any parent-directory creation.
            Assert.False(File.Exists(ordinary));
            Assert.False(Directory.Exists(Path.Combine(knownRoot, "missing")));
        }
        finally
        {
            Directory.Delete(knownRoot, recursive: true);
        }
    }

    [Fact]
    public void TapeFileWriteNew_RefusesUnsupportedDeviceNamespaceDestinations()
    {
        // \\?\GLOBALROOT\... is NOT an alias of an ordinary file-system path:
        // the boundary must refuse it before any parent directory creation or
        // open, because no evaluated identity exists to compare against.
        string deviceDestination = @"\\?\GLOBALROOT\onslaught-probe\extended.json";

        ArgumentException refused = Assert.Throws<ArgumentException>(
            () => TapeFile.WriteNew(deviceDestination, BoundaryProbeTape()));

        Assert.Contains("device namespace", refused.Message, StringComparison.Ordinal);

        // A volume-GUID body is equally unevaluated: refuse rather than
        // compare a fabricated identity.
        ArgumentException volumeRefused = Assert.Throws<ArgumentException>(
            () => TapeFile.WriteNew(
                @"\\?\Volume{9c5f8a3e-0000-0000-0000-000000000000}\probe.json",
                BoundaryProbeTape()));
        Assert.Contains("device namespace", volumeRefused.Message, StringComparison.Ordinal);
    }

    [Fact]
    public void TapeFileWriteNew_EvaluatesResolvedIdentityOfExtendedAliasWithDotSegments()
    {
        // The extended prefix suppresses GetFullPath normalization, so the
        // folded identity of \\?\C:\...\sibling\..\known\missing\x.json still
        // carries dot segments the later create-new open WOULD resolve. The
        // boundary must therefore evaluate the RESOLVED identity, not the
        // literal dotted spelling: this destination resolves INSIDE the
        // supplied known root and is refused on that basis, leaving no
        // creation debris under either lexical spelling.
        string knownRoot = Path.Combine(
            Path.GetTempPath(),
            $"onslaught-rebuild-known-{Guid.NewGuid():N}");
        Directory.CreateDirectory(knownRoot);

        try
        {
            string sibling = Path.Combine(Path.GetDirectoryName(knownRoot)!, Path.GetFileName(knownRoot) + "-sibling");
            Directory.CreateDirectory(sibling);
            try
            {
                string dotDot = $@"\\?\{sibling}\..\{Path.GetFileName(knownRoot)}\missing\extended.json";

                ArgumentException refused = Assert.Throws<ArgumentException>(
                    () => TapeFile.WriteNew(dotDot, BoundaryProbeTape(), [knownRoot]));

                Assert.Contains("game or save root", refused.Message, StringComparison.Ordinal);

                // Refusal precedes every parent creation: neither spelling of
                // the destination exists, and the missing directory segment
                // was never materialized under any ancestor.
                Assert.False(File.Exists(Path.Combine(knownRoot, "missing", "extended.json")));
                Assert.False(Directory.Exists(Path.Combine(knownRoot, "missing")));
                Assert.False(Directory.Exists(Path.Combine(sibling, "missing")));
            }
            finally
            {
                Directory.Delete(sibling, recursive: true);
            }
        }
        finally
        {
            Directory.Delete(knownRoot, recursive: true);
        }
    }

    private static bool TryCreateReparseDirectoryLink(string linkPath, string targetPath)
    {
        if (OperatingSystem.IsWindows())
        {
            // A junction needs neither elevation nor developer mode; cmd's
            // mklink /J mints one deterministically.
            using var process = System.Diagnostics.Process.Start(
                new System.Diagnostics.ProcessStartInfo(
                    "cmd.exe",
                    $"/c mklink /J \"{linkPath}\" \"{targetPath}\"")
                {
                    CreateNoWindow = true,
                    UseShellExecute = false,
                    RedirectStandardOutput = true,
                    RedirectStandardError = true,
                });
            if (process is null)
            {
                return false;
            }

            process.WaitForExit(15_000);
            return process.ExitCode == 0 && Directory.Exists(linkPath);
        }

        try
        {
            Directory.CreateSymbolicLink(linkPath, targetPath);
            return Directory.Exists(linkPath);
        }
        catch (Exception exception) when (
            exception is IOException or UnauthorizedAccessException or NotSupportedException)
        {
            return false;
        }
    }
}
