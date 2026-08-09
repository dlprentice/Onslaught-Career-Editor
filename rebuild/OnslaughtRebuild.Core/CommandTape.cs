// SPDX-License-Identifier: GPL-3.0-or-later

using System.Text.Json;
using System.Text.Json.Serialization;

namespace OnslaughtRebuild.Core;

public sealed record CommandSpan(
    int StartTick,
    int DurationTicks,
    sbyte MoveX,
    sbyte MoveZ,
    bool ToggleMode = false,
    bool Fire = false,
    bool Reset = false,
    sbyte LookX = 0,
    sbyte LookY = 0,
    short LookXAnalogPermille = 0,
    short LookYAnalogPermille = 0,
    bool LandingJets = false,
    // BUTTON_SKIP_PANNING 0x3a, KEY_ONCE in every shipped row, so an edge.
    bool SkipPanning = false)
{
    [JsonIgnore]
    public int EndTickExclusive => checked(StartTick + DurationTicks);

    public SimInput ToInput()
    {
        SimActions actions = SimActions.None;
        if (ToggleMode)
        {
            actions |= SimActions.ToggleMode;
        }

        if (Fire)
        {
            actions |= SimActions.Fire;
        }

        if (Reset)
        {
            actions |= SimActions.Reset;
        }

        if (LandingJets)
        {
            actions |= SimActions.LandingJets;
        }

        if (SkipPanning)
        {
            actions |= SimActions.SkipPanning;
        }

        return new SimInput(
            MoveX,
            MoveZ,
            actions,
            LookX,
            LookY,
            LookXAnalogPermille,
            LookYAnalogPermille);
    }
}

public sealed record CommandTape
{
    /// <summary>
    /// The tape wire format. <b>Bump this whenever <see cref="CommandSpan"/>
    /// gains, loses or re-means a field</b>, and rely on
    /// <see cref="Validate"/> rejecting a mismatch rather than on a reader
    /// noticing.
    /// </summary>
    /// <remarks>
    /// <para>
    /// <c>v2 -&gt; v3</c>, 2026-08-09: <c>CommandSpan.Fire</c> changed from a
    /// held action to the shipped controller's <c>BUTTON_RELEASE</c> edge. A
    /// fire span must therefore be exactly one tick; otherwise an old held-fire
    /// tape would silently replay as several release edges.
    /// </para>
    /// <para>
    /// <c>v1 -&gt; v2</c>, 2026-07-27: <c>CommandSpan.SkipPanning</c>
    /// (<c>BUTTON_SKIP_PANNING</c> <c>0x3a</c>) was added. It is load-bearing —
    /// it ends the opening pan and, through
    /// <c>Level100Mission.NotifyPlayingStateStarted</c>, re-bases the whole
    /// tutorial message chain. A <c>v1</c> reader handed a tape written by this
    /// code would have deserialized it happily, because the property is simply
    /// absent from its <c>CommandSpan</c> and <c>System.Text.Json</c> supplies
    /// the default, and would then have replayed a DIFFERENT run under the same
    /// schema string. That is the silent-drop class <c>0ccf6e96</c> was written
    /// to make structurally impossible, so the string moves with the field.
    /// </para>
    /// <para>
    /// The one tracked tape, <c>rebuild/scenarios/first-flight.v1.json</c>,
    /// keeps its filename: that <c>v1</c> is the scenario's own name and has
    /// never tracked this constant (the file has not been renamed since
    /// <c>3cc382e8</c>). Its <c>schemaVersion</c> field is what moves.
    /// </para>
    /// </remarks>
    public const string CurrentSchemaVersion = "onslaught-rebuild-command-tape.v3";

    [JsonConstructor]
    public CommandTape(
        string schemaVersion,
        string name,
        uint seed,
        int durationTicks,
        string? expectedFinalStateHash,
        string? expectedTraceHash,
        IReadOnlyList<CommandSpan>? spans)
    {
        SchemaVersion = schemaVersion;
        Name = name;
        Seed = seed;
        DurationTicks = durationTicks;
        ExpectedFinalStateHash = expectedFinalStateHash;
        ExpectedTraceHash = expectedTraceHash;
        Spans = spans is null ? null! : Array.AsReadOnly(spans.ToArray());
    }

    public string SchemaVersion { get; init; }

    public string Name { get; init; }

    public uint Seed { get; init; }

    public int DurationTicks { get; init; }

    public string? ExpectedFinalStateHash { get; init; }

    public string? ExpectedTraceHash { get; init; }

    public IReadOnlyList<CommandSpan> Spans { get; }

    public void Validate()
    {
        if (!string.Equals(SchemaVersion, CurrentSchemaVersion, StringComparison.Ordinal))
        {
            throw new InvalidDataException($"Unsupported command tape schema: {SchemaVersion}");
        }

        if (string.IsNullOrWhiteSpace(Name))
        {
            throw new InvalidDataException("Command tape name is required.");
        }

        if (Seed == 0)
        {
            throw new InvalidDataException("Command tape seed must be nonzero.");
        }

        if (DurationTicks is < 1 or > 1_000_000)
        {
            throw new InvalidDataException("Command tape duration must be between 1 and 1,000,000 ticks.");
        }

        ValidateOptionalHash(ExpectedFinalStateHash, "Expected final state hash");
        ValidateOptionalHash(ExpectedTraceHash, "Expected trace hash");

        if (Spans is null)
        {
            throw new InvalidDataException("Command tape spans are required.");
        }

        int previousEnd = 0;
        foreach (CommandSpan span in Spans)
        {
            if (span is null)
            {
                throw new InvalidDataException("Command tape spans cannot contain null entries.");
            }

            if (span.StartTick < previousEnd || span.StartTick < 0)
            {
                throw new InvalidDataException("Command spans must be sorted and non-overlapping.");
            }

            int endTickExclusive;
            try
            {
                endTickExclusive = span.EndTickExclusive;
            }
            catch (OverflowException exception)
            {
                throw new InvalidDataException("Command span end tick exceeds the supported range.", exception);
            }

            if (span.DurationTicks <= 0 || endTickExclusive > DurationTicks)
            {
                throw new InvalidDataException("Command span is outside the tape duration.");
            }

            SimInput input = span.ToInput();
            try
            {
                input.Validate();
            }
            catch (ArgumentOutOfRangeException exception)
            {
                throw new InvalidDataException("Command span contains invalid input values.", exception);
            }

            if ((span.ToggleMode || span.Fire || span.Reset || span.SkipPanning) &&
                span.DurationTicks != 1)
            {
                throw new InvalidDataException(
                    "ToggleMode, Fire, Reset and SkipPanning are edge actions and require a one-tick span.");
            }

            previousEnd = endTickExclusive;
        }
    }

    private static void ValidateOptionalHash(string? hash, string label)
    {
        if (hash is not null &&
            (hash.Length != 64 || hash.Any(character => !Uri.IsHexDigit(character))))
        {
            throw new InvalidDataException($"{label} must be a 64-character SHA-256 hex value.");
        }
    }
}

public static class CommandTapeCodec
{
    private static readonly JsonSerializerOptions s_options = new()
    {
        PropertyNamingPolicy = JsonNamingPolicy.CamelCase,
        PropertyNameCaseInsensitive = false,
        UnmappedMemberHandling = JsonUnmappedMemberHandling.Disallow,
        WriteIndented = true,
    };

    public static CommandTape Deserialize(string json)
    {
        ArgumentException.ThrowIfNullOrWhiteSpace(json);
        CommandTape tape = JsonSerializer.Deserialize<CommandTape>(json, s_options)
            ?? throw new InvalidDataException("Command tape JSON did not contain a document.");
        tape.Validate();
        return tape;
    }

    public static string Serialize(CommandTape tape)
    {
        ArgumentNullException.ThrowIfNull(tape);
        tape.Validate();
        return JsonSerializer.Serialize(tape, s_options).ReplaceLineEndings("\n") + "\n";
    }
}
