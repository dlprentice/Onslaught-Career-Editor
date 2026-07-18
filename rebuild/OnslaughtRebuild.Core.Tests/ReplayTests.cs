// SPDX-License-Identifier: GPL-3.0-or-later

using OnslaughtRebuild.Core;

namespace OnslaughtRebuild.Core.Tests;

public sealed class ReplayTests
{
    [Fact]
    public void FirstFlightReplay_IsDeterministic()
    {
        CommandTape tape = LoadFirstFlightTape();

        ReplayResult first = ReplayRunner.Run(tape);
        ReplayResult second = ReplayRunner.Run(tape);

        Assert.Equal(first.FinalStateHash, second.FinalStateHash);
        Assert.Equal(first.TraceHash, second.TraceHash);
        Assert.Equal(tape.DurationTicks, first.FinalState.Tick);
    }

    [Fact]
    public void CommandTape_RoundTripsWithoutChangingReplayState()
    {
        CommandTape tape = LoadFirstFlightTape();
        string serialized = CommandTapeCodec.Serialize(tape);
        CommandTape roundTripped = CommandTapeCodec.Deserialize(serialized);

        Assert.EndsWith("\n", serialized, StringComparison.Ordinal);
        Assert.DoesNotContain("\r", serialized, StringComparison.Ordinal);
        ReplayResult original = ReplayRunner.Run(tape);
        ReplayResult replayed = ReplayRunner.Run(roundTripped);
        Assert.Equal(original.FinalStateHash, replayed.FinalStateHash);
        Assert.Equal(original.TraceHash, replayed.TraceHash);
        Assert.Equal(tape.Spans.Count, roundTripped.Spans.Count);
    }

    [Fact]
    public void CommandTape_RejectsOverlappingSpans()
    {
        var tape = new CommandTape(
            CommandTape.CurrentSchemaVersion,
            "overlap",
            1,
            10,
            null,
            null,
            [
                new CommandSpan(0, 5, 0, 1),
                new CommandSpan(4, 2, 1, 0),
            ]);

        Assert.Throws<InvalidDataException>(tape.Validate);
    }

    [Fact]
    public void CommandTape_RejectsMissingSpanCollectionAsInvalidData()
    {
        const string json = """
            {
              "schemaVersion": "onslaught-rebuild-command-tape.v1",
              "name": "missing-spans",
              "seed": 1,
              "durationTicks": 10,
              "expectedFinalStateHash": null
            }
            """;

        Assert.Throws<InvalidDataException>(() => CommandTapeCodec.Deserialize(json));
    }

    [Fact]
    public void CommandTape_RejectsOverflowingSpanAsInvalidData()
    {
        var tape = new CommandTape(
            CommandTape.CurrentSchemaVersion,
            "overflow",
            1,
            10,
            null,
            null,
            [new CommandSpan(int.MaxValue, 2, 0, 0)]);

        Assert.Throws<InvalidDataException>(tape.Validate);
    }

    [Fact]
    public void CommandTape_RejectsUnknownJsonProperties()
    {
        const string json = """
            {
              "schemaVersion": "onslaught-rebuild-command-tape.v1",
              "name": "unknown-property",
              "seed": 1,
              "durationTicks": 1,
              "expectedFinalStateHash": null,
              "spans": [],
              "firing": true
            }
            """;

        Assert.Throws<System.Text.Json.JsonException>(() => CommandTapeCodec.Deserialize(json));
    }

    [Fact]
    public void CommandTape_RejectsInvalidAxisAsInvalidData()
    {
        var tape = new CommandTape(
            CommandTape.CurrentSchemaVersion,
            "invalid-axis",
            1,
            1,
            null,
            null,
            [new CommandSpan(0, 1, 2, 0)]);

        Assert.Throws<InvalidDataException>(tape.Validate);
    }

    [Fact]
    public void CommandTape_RejectsZeroSeed()
    {
        var tape = new CommandTape(
            CommandTape.CurrentSchemaVersion,
            "zero-seed",
            0,
            1,
            null,
            null,
            []);

        Assert.Throws<InvalidDataException>(tape.Validate);
    }

    [Fact]
    public void CommandTape_RejectsMultiTickEdgeActions()
    {
        var tape = new CommandTape(
            CommandTape.CurrentSchemaVersion,
            "held-edge",
            1,
            2,
            null,
            null,
            [new CommandSpan(0, 2, 0, 0, ToggleMode: true)]);

        Assert.Throws<InvalidDataException>(tape.Validate);
    }

    [Fact]
    public void CommandTape_DefensivelyCopiesSpanCollections()
    {
        var source = new List<CommandSpan> { new(0, 1, 0, 1) };
        var tape = new CommandTape(
            CommandTape.CurrentSchemaVersion,
            "immutable-spans",
            1,
            1,
            null,
            null,
            source);

        source.Clear();

        Assert.Single(tape.Spans);
        var spans = Assert.IsAssignableFrom<IList<CommandSpan>>(tape.Spans);
        Assert.True(spans.IsReadOnly);
        Assert.Throws<NotSupportedException>(() => spans.Clear());
    }

    [Fact]
    public void CommandSpan_LookX_RoundsTripsInJsonAndAffectsFacing()
    {
        const string json = """
              {
                "schemaVersion": "onslaught-rebuild-command-tape.v1",
                "name": "look-hold",
                "seed": 1,
                "durationTicks": 20,
                "spans": [
                  { "startTick": 0, "durationTicks": 20, "moveX": 0, "moveZ": 0, "lookX": 1 }
                ]
              }
              """;
        CommandTape tape = CommandTapeCodec.Deserialize(json);
        Assert.Equal(1, tape.Spans[0].LookX);
        ReplayResult result = ReplayRunner.Run(tape);
        Assert.Equal(1, result.FinalState.FacingX);
        Assert.Equal(1, result.FinalState.FacingZ);
    }

    [Fact]
    public void CommandSpan_MissingLookX_DefaultsToZero()
    {
        const string json = """
              {
                "schemaVersion": "onslaught-rebuild-command-tape.v1",
                "name": "no-look",
                "seed": 1,
                "durationTicks": 1,
                "spans": [
                  { "startTick": 0, "durationTicks": 1, "moveX": 0, "moveZ": 1 }
                ]
              }
              """;
        CommandTape tape = CommandTapeCodec.Deserialize(json);
        Assert.Equal(0, tape.Spans[0].LookX);
    }

    [Fact]
    public void ReplayHashesIncludeContinuousYawBeforeFacingSectorChanges()
    {
        var looked = new CommandTape(
            CommandTape.CurrentSchemaVersion,
            "looked",
            1,
            1,
            null,
            null,
            [new CommandSpan(0, 1, 0, 0, LookX: 1)]);
        var idled = new CommandTape(
            CommandTape.CurrentSchemaVersion,
            "idled",
            1,
            1,
            null,
            null,
            []);

        ReplayResult lookedResult = ReplayRunner.Run(looked);
        ReplayResult idledResult = ReplayRunner.Run(idled);

        Assert.Equal(idledResult.FinalState.FacingX, lookedResult.FinalState.FacingX);
        Assert.Equal(idledResult.FinalState.FacingZ, lookedResult.FinalState.FacingZ);
        Assert.Equal(10_444, lookedResult.FinalState.FacingYawMicroRad);
        Assert.Equal(10_444, lookedResult.FinalState.WalkerYawVelocityMicroRadPerTick);
        Assert.NotEqual(idledResult.FinalStateHash, lookedResult.FinalStateHash);
        Assert.NotEqual(idledResult.TraceHash, lookedResult.TraceHash);
    }

    [Fact]
    public void ReplayTraceHash_DistinguishesHistoriesErasedByReset()
    {
        var movedThenReset = new CommandTape(
            CommandTape.CurrentSchemaVersion,
            "moved-reset",
            1,
            2,
            null,
            null,
            [
                new CommandSpan(0, 1, 1, 0),
                new CommandSpan(1, 1, 0, 0, Reset: true),
            ]);
        var idledThenReset = new CommandTape(
            CommandTape.CurrentSchemaVersion,
            "idle-reset",
            1,
            2,
            null,
            null,
            [new CommandSpan(1, 1, 0, 0, Reset: true)]);

        ReplayResult moved = ReplayRunner.Run(movedThenReset);
        ReplayResult idled = ReplayRunner.Run(idledThenReset);
        Assert.Equal(moved.FinalStateHash, idled.FinalStateHash);

        Assert.NotEqual(moved.TraceHash, idled.TraceHash);
    }

    [Fact]
    public void CoreAssembly_HasNoPresentationOrReferenceSourceDependency()
    {
        string[] references = typeof(Simulation).Assembly
            .GetReferencedAssemblies()
            .Select(reference => reference.Name ?? string.Empty)
            .ToArray();

        Assert.DoesNotContain(references, name => name.StartsWith("Godot", StringComparison.OrdinalIgnoreCase));
        Assert.DoesNotContain(references, name => name.Contains("WinUI", StringComparison.OrdinalIgnoreCase));
        Assert.DoesNotContain(references, name => name.Contains("OnslaughtCareerEditor", StringComparison.OrdinalIgnoreCase));
    }

    [Fact]
    public void CoreCodec_DoesNotExposeFilesystemLoading()
    {
        Assert.Null(typeof(CommandTapeCodec).GetMethod("Load"));
    }

    [Fact]
    public void CoreSource_HasNoFilesystemProcessClockOrNetworkApiUsage()
    {
        string sourceRoot = Path.Combine(AppContext.BaseDirectory, "core-source");
        string[] forbiddenTokens =
        [
            "File.",
            "Directory.",
            "Path.",
            "FileStream",
            "FileInfo",
            "DirectoryInfo",
            "DriveInfo",
            "FileSystemWatcher",
            "StreamReader",
            "StreamWriter",
            "MemoryMappedFile",
            "Environment.",
            "Process.",
            "Console.",
            "AppContext.",
            "OperatingSystem.",
            "RuntimeInformation.",
            "DateTime.",
            "DateTimeOffset.",
            "Stopwatch.",
            "TimeProvider",
            "Task.Delay",
            "Task.Run",
            "Thread.",
            "Parallel.",
            "Guid.NewGuid",
            "new Random(",
            "Random.Shared",
            "RandomNumberGenerator",
            "HttpClient",
            "HttpMessageInvoker",
            "WebRequest",
            "WebClient",
            "TcpClient",
            "TcpListener",
            "UdpClient",
            "Socket",
            "NetworkStream",
            "Dns.",
        ];

        foreach (string path in Directory.GetFiles(sourceRoot, "*.cs", SearchOption.AllDirectories))
        {
            string source = File.ReadAllText(path);
            foreach (string token in forbiddenTokens)
            {
                Assert.DoesNotContain(token, source, StringComparison.Ordinal);
            }
        }
    }

    [Fact]
    public void CoreProject_HasNoExternalOrCustomBuildInputs()
    {
        string projectPath = Path.Combine(
            AppContext.BaseDirectory,
            "core-project",
            "OnslaughtRebuild.Core.csproj");
        string projectText = File.ReadAllText(projectPath);
        var project = System.Xml.Linq.XDocument.Parse(projectText);

        string[] forbiddenElements =
        [
            "ProjectReference",
            "Reference",
            "PackageReference",
            "FrameworkReference",
            "PackageDownload",
            "NativeReference",
            "COMReference",
            "AdditionalFiles",
            "Analyzer",
            "Import",
            "UsingTask",
            "Target",
        ];
        string[] linkedInputElements = ["Compile", "Content", "EmbeddedResource", "None"];

        Assert.DoesNotContain(
            project.Descendants(),
            element => forbiddenElements.Contains(element.Name.LocalName, StringComparer.Ordinal));
        Assert.DoesNotContain(
            project.Descendants(),
            element => linkedInputElements.Contains(element.Name.LocalName, StringComparer.Ordinal) &&
                element.Attribute("Include") is not null);
        Assert.DoesNotContain("references/Onslaught", projectText, StringComparison.OrdinalIgnoreCase);
        Assert.DoesNotContain("references\\Onslaught", projectText, StringComparison.OrdinalIgnoreCase);
    }

    private static CommandTape LoadFirstFlightTape()
    {
        string path = Path.Combine(AppContext.BaseDirectory, "scenarios", "first-flight.v1.json");
        return CommandTapeCodec.Deserialize(File.ReadAllText(path));
    }
}
