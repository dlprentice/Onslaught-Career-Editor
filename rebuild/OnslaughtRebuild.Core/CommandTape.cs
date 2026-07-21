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
    short LookYAnalogPermille = 0)
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
    public const string CurrentSchemaVersion = "onslaught-rebuild-command-tape.v1";

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

            if ((span.ToggleMode || span.Reset) && span.DurationTicks != 1)
            {
                throw new InvalidDataException("ToggleMode and Reset are edge actions and require a one-tick span.");
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
