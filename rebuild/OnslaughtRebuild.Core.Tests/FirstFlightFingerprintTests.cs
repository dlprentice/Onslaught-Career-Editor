// SPDX-License-Identifier: GPL-3.0-or-later

using OnslaughtRebuild.TestSupport;

namespace OnslaughtRebuild.Core.Tests;

public sealed class FirstFlightFingerprintTests
{
    [Fact]
    public void FirstFlightTape_TraceAndStateHashesMatchThePinnedFingerprint()
    {
        // Owns the first-flight.v1.json fingerprint (838 ticks, seed
        // 2836905711) for this revision, per rebuild/DETERMINISM.md: a
        // revision fingerprint includes accumulated changes since schema42,
        // including raw aircraft motion and ordered guide/events in schema47.
        // This old tape covers opening and a short Walker move/turn; its
        // name does not establish flight acceptance. Check that bounded state
        // before accepting a new fingerprint. The GDScript headless replayer
        // pins the same hashes (Tests/headless_replay_checks.gd), and native
        // Godot smoke pins the 2148-tick rendered path separately.
        // Includes the admitted Airfield exits and aircraft weapon model inputs.
        const string expectedTrace = "0872e009a2fb254927a3014d539ae1039332ad5eb8bd8af38a6e77cc86575ec9";
        const string expectedState = "69bd64ac4b2f344c1300d64e6619931f57dc06d768dbd70a5f1b816aedb1f59a";
        CommandTape tape = CommandTapeCodec.Deserialize(File.ReadAllText(
            Path.Combine(AppContext.BaseDirectory, "scenarios", "first-flight.v1.json")));
        var definitions = Level100TestActorDefinitions.LoadMaterialized();
        var initial = new Simulation(tape.Seed, definitions).Snapshot;
        ReplayResult replay = ReplayRunner.Run(tape, definitions);
        WorldSnapshot state = replay.FinalState;
        Assert.Equal(838, state.Tick);
        Assert.True(state.Level100PlayerActive);
        Assert.False(state.Level100FlightEnabled);
        Assert.NotEqual(initial.PlayerPosition, state.PlayerPosition);
        Assert.Equal(VehicleMode.Walker, state.Mode);
        Assert.Equal(initial.Hull, state.Hull);
        Assert.Empty(state.Projectiles);
        Assert.Equal(0, state.TargetsDestroyed);
        Assert.Equal(Level100MissionOutcome.Running, state.Level100Mission.Outcome);
        Level100ActorId trainer = state.Level100Actors.Actors.Single(actor => actor.Name == "Air Trainer").ActorId;
        Assert.NotNull(state.Level100Actors.BaseStates.Single(actor => actor.ActorId == trainer).State.RetailPlane);
        Assert.Contains(state.Level100ActorMechanics.Actors, actor => actor.ActorId == trainer && actor.PlaneGuide is not null);
        Assert.True(state.Level100ActorMechanics.PlaneEvents!.Float24Arithmetic);
        Assert.Equal(838u, state.Level100ActorMechanics.PlaneEvents.FrameCount);
        // Compare every tick with the pre-mount format-7 definitions, restoring
        // only the identity word. Keep format 6's older normalized trace too.
        // Neither the tape nor its behavioral checks move.
        var priorDefinitions = new Level100ActorDefinitionSet(definitions.Actors,
            definitions.Spawns, definitions.WaypointPaths,
            definitions.MotionDefinitions.Select(definition => definition with { WeaponMounts = null }));
        var legacyDefinitions = new Level100ActorDefinitionSet(definitions.Actors,
            definitions.Spawns.Select(spawn => spawn with { SpawnerExitWaypoints = null }),
            definitions.WaypointPaths, priorDefinitions.MotionDefinitions);
        var currentRun = new Simulation(tape.Seed, definitions);
        var priorRun = new Simulation(tape.Seed, priorDefinitions);
        var reader = new CommandTapeReader(tape);
        using var priorTrace = new ReplayTraceHasher();
        using var legacyTrace = new ReplayTraceHasher();
        for (int tick = 0; tick < tape.DurationTicks; tick++)
        {
            SimInput input = reader.ReadNext(tick);
            WorldSnapshot current = currentRun.Step(input), prior = priorRun.Step(input);
            byte[] normalized = StateHasher.GetCanonicalBytes(current with
            { Level100Actors = current.Level100Actors with
                { DefinitionSetIdentitySha256 = priorDefinitions.IdentitySha256 } });
            Assert.Equal(StateHasher.GetCanonicalBytes(prior), normalized);
            priorTrace.Append(tick, input, normalized);
            legacyTrace.Append(tick, input, StateHasher.GetCanonicalBytes(current with
            { Level100Actors = current.Level100Actors with
                { DefinitionSetIdentitySha256 = legacyDefinitions.IdentitySha256 } }));
        }
        Assert.Equal("6ec3dfbbfd2351f824e4bab7685503e8e014a57f9e6990ad2c13a78dfc44ad4d",
            StateHasher.ComputeHex(priorRun.Snapshot));
        Assert.Equal("2da46d641e2187ead860869dd25b5abdf54f59aa5bac8830f7e661babe000309", priorTrace.GetCurrentHash());
        Assert.Equal("5edc89006a783cfeef63369c20cb524e56014c96d314b36f34b11e0bcf1c9239",
            StateHasher.ComputeHex(state with { Level100Actors = state.Level100Actors with
                { DefinitionSetIdentitySha256 = legacyDefinitions.IdentitySha256 } }));
        Assert.Equal("0d835c29ff14cc6069cbf2dae7859bbf164ead0ca5112736cf8df0a597c91518", legacyTrace.GetCurrentHash());
        Assert.True(expectedState == replay.FinalStateHash,
            $"First-flight state {replay.FinalStateHash}; trace {replay.TraceHash}");
        Assert.Equal(expectedTrace, replay.TraceHash);
        ReplayComparison repeated = ReplayRunner.Compare(tape, tape, definitions);
        Assert.False(repeated.Diff.TraceHashMismatch || repeated.Diff.BehavioralEventMismatch || repeated.Diff.FinalStateMismatch);
        Assert.Equal(expectedTrace, repeated.After.TraceHash);
    }
}
