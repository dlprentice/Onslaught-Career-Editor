// SPDX-License-Identifier: GPL-3.0-or-later

using System.Text.Json;
using Godot;
using OnslaughtRebuild.Core;
using D = Godot.Collections.Dictionary;

namespace OnslaughtRebuild.GodotClient;

/// <summary>
/// Replay entry points for the GDScript headless replayer
/// (res://Tools/headless_replay.gd), which owns its options, work budget,
/// expectations, report and exit codes. Core's ReplayRunner replays and hashes;
/// these methods only decode, run and describe, and touch no bridge state.
/// A refusal also reports <c>input_error</c>: the exceptions a caller's tape,
/// manifest or path can cause, which the replayer reports as usage errors.
/// </summary>
public sealed partial class SimulationBridge
{
    /// <summary>Decodes and validates a tape without simulating it.</summary>
    public D DecodeTape(string json) => ReplayGuard(() => TapeFacts(CommandTapeCodec.Deserialize(json)));

    public D Replay(string tapeJson, byte[] manifestBytes) => ReplayGuard(() => ResultFacts(
        ReplayRunner.Run(CommandTapeCodec.Deserialize(tapeJson), Level100ActorDefinitionManifest.Decode(manifestBytes))));

    public D CompareReplays(string beforeJson, string afterJson, byte[] manifestBytes) => ReplayGuard(() =>
    {
        ReplayComparison comparison = ReplayRunner.Compare(CommandTapeCodec.Deserialize(beforeJson),
            CommandTapeCodec.Deserialize(afterJson), Level100ActorDefinitionManifest.Decode(manifestBytes));
        return new D
        {
            ["before"] = ResultFacts(comparison.Before),
            ["after"] = ResultFacts(comparison.After),
            ["diff"] = DiffFacts(comparison.Diff),
        };
    });

    private static D TapeFacts(CommandTape tape) => new()
    {
        ["name"] = tape.Name,
        ["seed"] = tape.Seed,
        ["duration_ticks"] = tape.DurationTicks,
        ["expected_trace_hash"] = Nullable(tape.ExpectedTraceHash),
        ["expected_final_state_hash"] = Nullable(tape.ExpectedFinalStateHash),
    };

    private static D ResultFacts(ReplayResult result) => new()
    {
        ["ticks"] = result.FinalState.Tick,
        ["trace_hash"] = result.TraceHash,
        ["final_state_hash"] = result.FinalStateHash,
        ["mode"] = result.FinalState.Mode.ToString(),
        ["energy"] = result.FinalState.Energy,
        ["shield"] = result.FinalState.Shield,
        ["hull"] = result.FinalState.Hull,
        ["targets_destroyed"] = result.FinalState.TargetsDestroyed,
        ["active_projectiles"] = result.FinalState.Projectiles.Count,
    };

    private static D DiffFacts(ReplayDiff diff) => new()
    {
        ["schema_version"] = diff.SchemaVersion,
        ["trace_hash_mismatch"] = diff.TraceHashMismatch,
        ["behavioral_event_mismatch"] = diff.BehavioralEventMismatch,
        ["final_state_mismatch"] = diff.FinalStateMismatch,
        ["first_divergence"] = diff.FirstDivergence is ReplayDivergence first
            ? new D
            {
                ["tick"] = first.Tick,
                ["category"] = first.Category,
                ["before_value"] = first.BeforeValue,
                ["after_value"] = first.AfterValue,
            }
            : default(Variant),
    };

    private static Variant Nullable(string? value) => value is { } text ? Variant.From(text) : default;

    private static D ReplayGuard(Func<Variant> action)
    {
        try
        {
            return new D { ["ok"] = true, ["value"] = action() };
        }
        catch (Exception error)
        {
            return new D
            {
                ["ok"] = false, ["error_type"] = error.GetType().Name, ["error"] = error.Message,
                ["input_error"] = error is ArgumentException or IOException or JsonException or
                    InvalidDataException or UnauthorizedAccessException,
            };
        }
    }
}
