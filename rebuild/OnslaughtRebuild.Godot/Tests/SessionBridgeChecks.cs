// SPDX-License-Identifier: GPL-3.0-or-later

using Godot;
using OnslaughtRebuild.Client;
using OnslaughtRebuild.Core;
using D = Godot.Collections.Dictionary;

namespace OnslaughtRebuild.GodotClient;

/// <summary>
/// Migration oracle: drives the retained C# InteractiveSession and the native
/// Client/interactive_session.gd over Bridge/SimulationBridge.cs through one
/// seeded operation sequence (the smoke scenario, then randomized held levels,
/// edges, pulses, pointer motion, pause/suspend and frame lengths) and compares
/// every observable after each operation and frame, including full state hashes.
/// </summary>
public sealed partial class SessionBridgeChecks : Node
{
    private const uint Seed = 0x4F4E534Cu;
    private const string ManifestPath = "res://Assets/Level100/StaticWorld/level100-static-world.json";
    private readonly List<string> _failures = [];
    private int _checks;
    private int _frames;
    private int _steps;
    private InteractiveSession _reference = null!;
    private GodotObject _native = null!;
    private GodotObject _bridge = null!;
    // --write-golden=PATH records every operation with the retained C#
    // session's results for the GDScript replay (Tests/interactive_session_checks.gd).
    private readonly Godot.Collections.Array _trace = [];

    public override void _Ready()
    {
        try
        {
            Require(DisplayServer.GetName() == "headless", "Session bridge checks require a headless runtime.");
            byte[] manifest = Godot.FileAccess.GetFileAsBytes(ManifestPath);
            Require(manifest.Length > 0, "The static-world manifest is missing.");
            _reference = new InteractiveSession(Seed, Level100ActorDefinitionManifest.Decode(manifest), new PlatformInputEdgeState());
            _bridge = new SimulationBridge();
            GodotObject platform = GD.Load<GDScript>("res://Client/platform_input_edges.gd").New().AsGodotObject();
            _native = GD.Load<GDScript>("res://Client/interactive_session.gd").New(_bridge, platform).AsGodotObject();
            Ok(_native.Call("start", Seed, manifest), "start");
            Compare("initial");

            for (int tick = 0; tick < FirstFlightSmokeScenario.DurationTicks; tick++)
            {
                Observe(FirstFlightSmokeScenario.GetInputForTick(_reference.CurrentSnapshot.Tick));
                Advance(500_000);
            }
            var random = new Random(0x5E5510);
            for (int operation = 0; operation < 6_000; operation++)
                Randomized(random, operation);
            RefusalParity();
        }
        catch (Exception error)
        {
            _failures.Add("Harness aborted: " + error);
        }
        string? golden = OS.GetCmdlineUserArgs().Where(arg => arg.StartsWith("--write-golden=", StringComparison.Ordinal))
            .Select(arg => arg["--write-golden=".Length..]).SingleOrDefault();
        if (golden is not null && _failures.Count == 0) System.IO.File.WriteAllBytes(golden, GD.VarToBytes(_trace));
        GD.Print($"SESSION_BRIDGE_CHECKS: {_checks} checks; {_frames} frames; {_steps} steps; failures={_failures.Count}");
        foreach (string failure in _failures.Take(20)) GD.Print("SESSION_BRIDGE_FAILURE " + failure);
        GetTree().Quit(_failures.Count == 0 ? 0 : 1);
    }

    private void Randomized(Random random, int operation)
    {
        int choice = random.Next(100);
        if (choice < 35) Advance(random.Next(4) == 0 ? random.Next(0, 3_200_000) : 500_000);
        else if (choice < 55)
            Observe(new InteractiveInput((sbyte)random.Next(-1, 2), (sbyte)random.Next(-1, 2), random.Next(3) == 0,
                random.Next(9) == 0, random.Next(400) == 0, (sbyte)random.Next(-1, 2), (sbyte)random.Next(-1, 2), random.Next(5) == 0));
        else if (choice < 60) Both(s => s.QueueToggleMode(), "queue_toggle_mode");
        else if (choice < 62) Both(s => s.QueueSkipPanning(), "queue_skip_panning");
        else if (choice < 67) Both(s => s.QueueFirePulse(), "queue_fire_pulse");
        else if (choice < 69) Both(s => s.QueueChangeWeapon(), "queue_change_weapon");
        else if (choice < 71) Both(s => s.QueueZoomIn(), "queue_zoom_in");
        else if (choice < 73) Both(s => s.QueueZoomOut(), "queue_zoom_out");
        else if (choice < 77)
        {
            sbyte x = (sbyte)random.Next(-1, 2), z = x == 0 ? (sbyte)(random.Next(2) * 2 - 1) : (sbyte)random.Next(-1, 2);
            _reference.QueueMovementPulse(x, z);
            Record("queue_movement_pulse", new Godot.Collections.Array { x, z });
            Ok(_native.Call("queue_movement_pulse", x, z), "movement pulse");
        }
        else if (choice < 80)
        {
            sbyte x = (sbyte)random.Next(-1, 2), y = x == 0 ? (sbyte)(random.Next(2) * 2 - 1) : (sbyte)random.Next(-1, 2);
            _reference.QueueLookPulse(x, y);
            Record("queue_look_pulse", new Godot.Collections.Array { x, y });
            Ok(_native.Call("queue_look_pulse", x, y), "look pulse");
        }
        else if (choice < 90)
        {
            int x = random.Next(-60_000, 60_001), y = random.Next(-60_000, 60_001);
            if (random.Next(20) == 0) x = random.Next(2) == 0 ? 2_000_000 : -2_000_000;
            if (x == 0 && y == 0) y = 1;
            _reference.QueuePointerMotionMilliPixels(x, y);
            Record("queue_pointer_motion_milli_pixels", new Godot.Collections.Array { x, y });
            Ok(_native.Call("queue_pointer_motion_milli_pixels", x, y), "pointer motion");
        }
        else if (choice < 93)
        {
            bool paused = random.Next(2) == 0;
            _reference.SetAuthenticMenuPaused(paused);
            Record("set_authentic_menu_paused", new Godot.Collections.Array { paused });
            _native.Call("set_authentic_menu_paused", paused);
        }
        else if (choice < 95) Both(s => s.SuspendInputUntilReleased(), "suspend_input_until_released");
        else if (choice < 97) Both(s => s.ReleaseAllInput(), "release_all_input");
        else if (choice < 99)
        {
            float sensitivity = random.Next(4) == 0 ? 7f : (random.Next(21) + 1) * 3f;
            _reference.SetMouseSensitivity(sensitivity);
            Record("set_mouse_sensitivity", new Godot.Collections.Array { (double)sensitivity });
            Ok(_native.Call("set_mouse_sensitivity", sensitivity), "sensitivity");
        }
        else Both(s => s.QueueReset(), "queue_reset");
        Compare($"operation {operation}");
    }

    private void Observe(InteractiveInput input)
    {
        _reference.ObserveInput(input);
        Record("observe_input", new Godot.Collections.Array { new D
        {
            ["move_x"] = input.MoveX, ["move_z"] = input.MoveZ, ["fire_held"] = input.FireHeld,
            ["toggle_mode_held"] = input.ToggleModeHeld, ["reset_held"] = input.ResetHeld,
            ["look_x"] = input.LookX, ["look_y"] = input.LookY, ["landing_jets_held"] = input.LandingJetsHeld,
        } });
        Ok(_native.Call("observe_input", new D
        {
            ["move_x"] = input.MoveX, ["move_z"] = input.MoveZ, ["fire_held"] = input.FireHeld,
            ["toggle_mode_held"] = input.ToggleModeHeld, ["reset_held"] = input.ResetHeld,
            ["look_x"] = input.LookX, ["look_y"] = input.LookY, ["landing_jets_held"] = input.LandingJetsHeld,
        }), "observe_input");
    }

    private void Both(Action<InteractiveSession> reference, string native)
    {
        reference(_reference);
        Record(native, new Godot.Collections.Array());
        _native.Call(native);
    }

    private void Record(string method, Godot.Collections.Array arguments, D? expected = null)
    {
        var entry = new D { ["method"] = method, ["arguments"] = arguments };
        if (expected is not null) entry["expected"] = expected;
        _trace.Add(entry);
    }

    private void Advance(long elapsedTicks)
    {
        FrameAdvanceResult expected = _reference.AdvanceFrameTicks(elapsedTicks);
        var frame = new D
        {
            ["steps_advanced"] = expected.StepsAdvanced, ["frame_time_capped"] = expected.FrameTimeCapped,
            ["interpolation_phase"] = expected.InterpolationPhase,
            ["interpolation_alpha_bits"] = BitConverter.DoubleToInt64Bits(expected.InterpolationAlpha),
        };
        if (expected.StepsAdvanced > 0)
        {
            SimInput last = _reference.LastConsumedInput!.Value;
            frame["state_hash"] = StateHasher.ComputeHex(expected.CurrentSnapshot);
            frame["consumed"] = new D
            {
                ["move_x"] = last.MoveX, ["move_z"] = last.MoveZ, ["actions"] = (int)last.Actions,
                ["look_x"] = last.LookX, ["look_y"] = last.LookY,
                ["look_x_analog_permille"] = last.LookXAnalogPermille, ["look_y_analog_permille"] = last.LookYAnalogPermille,
            };
        }
        Record("advance_frame_ticks", new Godot.Collections.Array { elapsedTicks }, frame);
        D actual = Ok(_native.Call("advance_frame_ticks", elapsedTicks), "advance").AsGodotDictionary();
        _frames++;
        _steps += expected.StepsAdvanced;
        Check(actual["steps_advanced"].AsInt32() == expected.StepsAdvanced, $"frame {_frames}: steps differ");
        Check(actual["frame_time_capped"].AsBool() == expected.FrameTimeCapped, $"frame {_frames}: cap differs");
        Check(actual["interpolation_phase"].AsInt64() == expected.InterpolationPhase, $"frame {_frames}: phase differs");
        Check(actual["interpolation_alpha"].AsDouble() == expected.InterpolationAlpha, $"frame {_frames}: alpha differs");
        if (expected.StepsAdvanced > 0)
        {
            string expectedHash = StateHasher.ComputeHex(expected.CurrentSnapshot);
            Check(Ok(_bridge.Call("GetStateHash"), "hash").AsString() == expectedHash, $"frame {_frames} tick {expected.CurrentSnapshot.Tick}: state hash differs");
            SimInput consumed = _reference.LastConsumedInput!.Value;
            D input = Ok(_bridge.Call("GetLastConsumedInput"), "input").AsGodotDictionary();
            Check(input["move_x"].AsInt32() == consumed.MoveX && input["move_z"].AsInt32() == consumed.MoveZ &&
                input["actions"].AsInt32() == (int)consumed.Actions && input["look_x"].AsInt32() == consumed.LookX &&
                input["look_y"].AsInt32() == consumed.LookY &&
                input["look_x_analog_permille"].AsInt32() == consumed.LookXAnalogPermille &&
                input["look_y_analog_permille"].AsInt32() == consumed.LookYAnalogPermille,
                $"frame {_frames}: consumed input differs");
        }
        _bridge.Call("GetTick");
    }

    private void Compare(string where)
    {
        InteractiveSessionMetrics metrics = _reference.Metrics;
        _trace.Add(new D
        {
            ["compare"] = where,
            ["metrics"] = new D
            {
                ["total_steps"] = metrics.TotalSteps, ["toggle_edges_consumed"] = metrics.ToggleEdgesConsumed,
                ["reset_edges_consumed"] = metrics.ResetEdgesConsumed, ["reset_generation"] = metrics.ResetGeneration,
                ["fire_held_ticks_sampled"] = metrics.FireHeldTicksSampled, ["fire_pulse_edges_consumed"] = metrics.FirePulseEdgesConsumed,
                ["change_weapon_edges_consumed"] = metrics.ChangeWeaponEdgesConsumed,
                ["movement_pulse_edges_consumed"] = metrics.MovementPulseEdgesConsumed,
                ["capped_frame_count"] = metrics.CappedFrameCount, ["dropped_elapsed_ticks"] = metrics.DroppedElapsedTicks,
            },
            ["flags"] = new Godot.Collections.Array { _reference.IsPaused, _reference.IsAuthenticMenuPaused,
                _reference.InputSuspendedUntilReleased, _reference.HasHeldOrPendingInput, _reference.InterpolationPhase },
        });
        D actual = _native.Call("metrics").AsGodotDictionary();
        Check(actual["total_steps"].AsInt64() == metrics.TotalSteps &&
            actual["toggle_edges_consumed"].AsInt64() == metrics.ToggleEdgesConsumed &&
            actual["reset_edges_consumed"].AsInt64() == metrics.ResetEdgesConsumed &&
            actual["reset_generation"].AsInt64() == metrics.ResetGeneration &&
            actual["fire_held_ticks_sampled"].AsInt64() == metrics.FireHeldTicksSampled &&
            actual["fire_pulse_edges_consumed"].AsInt64() == metrics.FirePulseEdgesConsumed &&
            actual["change_weapon_edges_consumed"].AsInt64() == metrics.ChangeWeaponEdgesConsumed &&
            actual["movement_pulse_edges_consumed"].AsInt64() == metrics.MovementPulseEdgesConsumed &&
            actual["capped_frame_count"].AsInt64() == metrics.CappedFrameCount &&
            actual["dropped_elapsed_ticks"].AsInt64() == metrics.DroppedElapsedTicks, where + ": metrics differ");
        Check(_native.Call("is_paused").AsBool() == _reference.IsPaused &&
            _native.Call("is_authentic_menu_paused").AsBool() == _reference.IsAuthenticMenuPaused &&
            _native.Call("input_suspended_until_released").AsBool() == _reference.InputSuspendedUntilReleased &&
            _native.Call("has_held_or_pending_input").AsBool() == _reference.HasHeldOrPendingInput &&
            _native.Call("interpolation_phase").AsInt64() == _reference.InterpolationPhase, where + ": session flags differ");
    }

    private void RefusalParity()
    {
        Refuses(() => _reference.QueueMovementPulse(0, 0), _native.Call("queue_movement_pulse", 0, 0), "zero movement pulse");
        Refuses(() => _reference.QueueLookPulse(0, 0), _native.Call("queue_look_pulse", 0, 0), "zero look pulse");
        Refuses(() => _reference.QueueMovementPulse(2, 0), _native.Call("queue_movement_pulse", 2, 0), "out-of-range movement pulse");
        Refuses(() => _reference.QueuePointerMotionMilliPixels(0, 0), _native.Call("queue_pointer_motion_milli_pixels", 0, 0), "zero pointer motion");
        Refuses(() => _reference.AdvanceFrameTicks(-1), _native.Call("advance_frame_ticks", -1), "negative frame");
        Refuses(() => _reference.SetMouseSensitivity(0f), _native.Call("set_mouse_sensitivity", 0.0), "zero sensitivity");
        Refuses(() => _reference.ObserveInput(new InteractiveInput(2, 0, false, false, false)),
            _native.Call("observe_input", new D { ["move_x"] = 2, ["move_z"] = 0, ["fire_held"] = false, ["toggle_mode_held"] = false,
                ["reset_held"] = false, ["look_x"] = 0, ["look_y"] = 0, ["landing_jets_held"] = false }), "out-of-range held input");
        Compare("after refusals");
    }

    private void Refuses(Action reference, Variant native, string name)
    {
        string? expected = null;
        try { reference(); }
        catch (Exception error) { expected = error.GetType().Name; }
        _trace.Add(new D { ["refusal"] = name, ["expected_type"] = expected ?? "" });
        D result = native.AsGodotDictionary();
        Check(expected is not null, name + ": reference accepted a refused operation");
        Check(!result["ok"].AsBool() && result["error_type"].AsString() == expected, $"{name}: native refusal type {Get(result, "error_type")} vs {expected}");
    }

    private Variant Ok(Variant returned, string name)
    {
        D result = returned.AsGodotDictionary();
        if (!result["ok"].AsBool()) throw new InvalidOperationException($"{name} failed: {Get(result, "error")}");
        return Get(result, "value");
    }

    private static Variant Get(D result, string key) => result.TryGetValue(key, out Variant value) ? value : default;

    private void Check(bool condition, string message)
    {
        _checks++;
        if (!condition) _failures.Add(message);
    }

    private static void Require(bool condition, string message)
    {
        if (!condition) throw new InvalidOperationException(message);
    }
}
