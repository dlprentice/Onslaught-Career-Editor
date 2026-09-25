// SPDX-License-Identifier: GPL-3.0-or-later

using Godot;
using OnslaughtRebuild.Client;
using OnslaughtRebuild.Core;
using A = Godot.Collections.Array;
using D = Godot.Collections.Dictionary;

namespace OnslaughtRebuild.GodotClient;

// Detached Core facts for the GDScript host and its presentation owners. Each
// call reads the current snapshot and returns plain Godot values in the exact
// shapes the former C# host adapters sent; nothing here keeps presentation state.
public sealed partial class SimulationBridge
{
    /// <summary>
    /// One rendered frame's Core batch: the events accumulated since the last
    /// delivered frame (in Core order) and the audio frame facts. A paused frame
    /// passes <paramref name="deliver"/> false: it reports no events and keeps
    /// them pending, exactly like InteractiveSession's paused frame result.
    /// </summary>
    public D TakeFrameFacts(bool deliver) => Guard(() =>
    {
        WorldSnapshot snapshot = CurrentSnapshot;
        Level100MissionEvent[] mission = deliver ? [.. _missionEvents] : [];
        AquilaFlightEvent[] flight = deliver ? [.. _flightEvents] : [];
        Level100DestructionEvent[] destruction = deliver ? [.. _destructionEvents] : [];
        Level100WeaponFireEvent[] weapons = deliver ? [.. _weaponFireEvents] : [];
        if (deliver)
        {
            _missionEvents.Clear();
            _flightEvents.Clear();
            _destructionEvents.Clear();
            _weaponFireEvents.Clear();
        }

        var worldWeapons = new A();
        foreach (Level100WeaponFireEvent? item in weapons)
            worldWeapons.Add(item is null ? default(Variant) : (int)item.Weapon);
        var worldDestruction = new A();
        foreach (Level100DestructionEvent item in destruction)
            worldDestruction.Add(new D { ["effect_kind"] = (int)item.EffectKind, ["actor_id"] = item.ActorId,
                ["x"] = item.Position.X, ["y"] = item.Position.Y, ["z"] = item.Position.Z });
        return new D
        {
            ["tick"] = snapshot.Tick,
            ["mission_events"] = MissionEventFacts(mission),
            ["audio"] = AudioFrameFacts(snapshot, mission, flight, weapons, destruction),
            ["weapon_events"] = worldWeapons,
            ["destruction_events"] = worldDestruction,
        };
    });

    /// <summary>The HUD's per-snapshot facts and frame record.</summary>
    public D HudFrame() => Guard(() =>
    {
        WorldSnapshot snapshot = CurrentSnapshot;
        var frame = new D { ["tick"] = snapshot.Tick, ["energy"] = snapshot.Energy,
            ["shield"] = snapshot.Shield, ["hull"] = snapshot.Hull,
            ["facing_yaw_micro_rad"] = snapshot.FacingYawMicroRad,
            ["player_position"] = Position(snapshot.PlayerPosition), ["mission_tick"] = snapshot.Level100Mission.Tick };
        return new D { ["facts"] = HudFacts(snapshot), ["frame"] = frame };
    });

    /// <summary>The host's input, pause and frontend-handoff decisions.</summary>
    public D ControlFacts() => Guard(() =>
    {
        WorldSnapshot snapshot = CurrentSnapshot;
        Level100MissionSnapshot mission = snapshot.Level100Mission;
        return new D
        {
            ["tick"] = snapshot.Tick,
            ["transition_none"] = snapshot.Transition == VehicleTransition.None,
            ["mission_outcome"] = (int)mission.Outcome,
            ["mission_terminal_state"] = (int)mission.TerminalState,
            ["frontend_handoff_ready"] = mission.TerminalState == Level100MissionTerminalState.FrontEndHandoffReady,
            ["gameplay_paused"] = Level100MissionTiming.GameplayPaused(
                mission.Outcome, mission.FailureReason, mission.TerminalTicksRemaining),
        };
    });

    /// <summary>The simulation fields of the smoke report, enum names as C# spells them.</summary>
    public D SmokeFacts() => Guard(() =>
    {
        WorldSnapshot snapshot = CurrentSnapshot;
        Level100MissionSnapshot mission = snapshot.Level100Mission;
        return new D
        {
            ["tick"] = snapshot.Tick,
            ["state_hash"] = StateHasher.ComputeHex(snapshot),
            ["targets_destroyed"] = snapshot.TargetsDestroyed,
            ["mode"] = snapshot.Mode.ToString(),
            ["level100_opening_ticks_remaining"] = snapshot.Level100OpeningTicksRemaining,
            ["level100_mission_tick"] = mission.Tick,
            ["level100_mission_outcome"] = mission.Outcome.ToString(),
            ["level100_terminal_state"] = mission.TerminalState.ToString(),
            ["level100_player_control_enabled"] = snapshot.Level100PlayerControlEnabled,
            ["level100_flight_enabled"] = snapshot.Level100FlightEnabled,
            ["level100_pulse_cannon_enabled"] = snapshot.Level100PulseCannonEnabled,
            ["level100_vulcan_cannon_enabled"] = snapshot.Level100VulcanCannonEnabled,
            ["level100_firing_range_targets_active"] = snapshot.Level100FiringRangeTargetsActive,
            ["level100_current_weapon_highlighted"] = snapshot.Level100CurrentWeaponHighlighted,
        };
    });

    /// <summary>The single Player 1 Battle Engine and the actor positions for audio binding.</summary>
    public D AquilaBinding() => Guard(() =>
    {
        Level100ActorRegistrySnapshot actors = CurrentSnapshot.Level100Actors;
        Level100ActorId? playerActorId = null;
        foreach (Level100ActorSnapshot actor in actors.Actors)
        {
            if (!StringComparer.Ordinal.Equals(actor.Name, "Player 1") ||
                actor.ThingTypeMask != Level100ReleasedThingTypeMasks.BattleEngine)
            {
                continue;
            }
            if (playerActorId.HasValue)
                throw new InvalidDataException("Level 100 has multiple Player 1 Battle Engine actors.");
            playerActorId = actor.ActorId;
        }
        Level100ActorId id = playerActorId ??
            throw new InvalidDataException("Level 100 is missing its Player 1 Battle Engine actor.");
        return new D { ["actor_id"] = id.Value, ["actors"] = ActorFacts(actors) };
    });

    /// <summary>
    /// The authored WRES allegiance per base-world identity from the verified
    /// static-world manifest, for the HUD scanner. It never reaches Core.
    /// </summary>
    public D DecodeAuthoredAllegiance(byte[] manifestBytes) => Guard(() =>
    {
        ArgumentNullException.ThrowIfNull(manifestBytes);
        var allegiance = new D();
        foreach ((string definition, int value) in Level100ActorDefinitionManifest.DecodeAuthoredAllegiance(manifestBytes))
            allegiance[definition] = value;
        return allegiance;
    });

    private static A MissionEventFacts(IReadOnlyList<Level100MissionEvent> events)
    {
        var batch = new A();
        foreach (Level100MissionEvent item in events)
        {
            batch.Add(item switch
            {
                Level100MessageRequested message => new D { ["kind"] = "message", ["tick"] = message.Tick,
                    ["speaker_id"] = message.SpeakerId, ["message_id"] = message.MessageId,
                    ["script_waits_for_duration"] = message.ScriptWaitsForDuration,
                    ["expected_playback_ticks"] = message.ExpectedPlaybackTicks },
                Level100HelpRequested help => new D { ["kind"] = "help", ["tick"] = help.Tick,
                    ["help_message_id"] = help.HelpMessageId },
                _ => new D { ["kind"] = "other" },
            });
        }
        return batch;
    }

    private static D AudioFrameFacts(WorldSnapshot snapshot, IReadOnlyList<Level100MissionEvent> mission,
        IReadOnlyList<AquilaFlightEvent> flight, IReadOnlyList<Level100WeaponFireEvent> weapons,
        IReadOnlyList<Level100DestructionEvent> destruction)
    {
        Level100MissionSnapshot missionSnapshot = snapshot.Level100Mission;
        A messages = [];
        foreach (Level100MissionEvent value in mission)
            if (value is Level100MessageRequested message)
                messages.Add(new D { ["speaker_id"] = message.SpeakerId, ["message_id"] = message.MessageId });
        A flightFacts = [];
        foreach (AquilaFlightEvent value in flight)
            flightFacts.Add(new D { ["kind"] = (int)value.Kind, ["tick"] = value.Tick, ["mode"] = (int)value.Mode });
        A weaponFacts = [];
        foreach (Level100WeaponFireEvent value in weapons)
            weaponFacts.Add(new D { ["weapon"] = (int)value.Weapon });
        A destructionFacts = [];
        foreach (Level100DestructionEvent value in destruction)
            destructionFacts.Add(new D { ["effect_kind"] = (int)value.EffectKind,
                ["position"] = PositionFacts(value.Position.X, value.Position.Y, value.Position.Z) });
        return new D { ["actors"] = ActorFacts(snapshot.Level100Actors),
            // BattleEngine.cpp:1763-1815: strict absolute hull warning before energy.
            ["warning_state"] = snapshot.Hull < 7_000 ? 2 : snapshot.Energy < 2_000 ? 1 : 0,
            ["messages"] = messages, ["flight_events"] = flightFacts, ["weapon_events"] = weaponFacts,
            ["simulation_tick"] = snapshot.Tick, ["mission_tick"] = missionSnapshot.Tick,
            ["thruster_fraction"] = snapshot.JetThrusterPermille / 1_000f,
            ["destruction_events"] = destructionFacts,
            ["gameplay_mix"] = Level100MissionTiming.GameplayMix(missionSnapshot.Outcome,
                missionSnapshot.FailureReason, missionSnapshot.TerminalTicksRemaining),
            ["gameplay_paused"] = Level100MissionTiming.GameplayPaused(missionSnapshot.Outcome,
                missionSnapshot.FailureReason, missionSnapshot.TerminalTicksRemaining) };
    }

    private static A ActorFacts(Level100ActorRegistrySnapshot actors)
    {
        ArgumentNullException.ThrowIfNull(actors);
        A values = [];
        foreach (Level100ActorSnapshot actor in actors.Actors)
        {
            SimVector3 position = actor.Pose.PositionMillimeters;
            values.Add(new D { ["actor_id"] = actor.ActorId.Value, ["position_mm"] = PositionFacts(position.X, position.Y, position.Z) });
        }
        return values;
    }

    private static D HudFacts(WorldSnapshot value) => new()
    {
        ["tick"] = value.Tick, ["player_position"] = Position(value.PlayerPosition),
        ["facing_yaw_micro_rad"] = value.FacingYawMicroRad, ["mode"] = (int)value.Mode,
        ["walker_selected_weapon"] = (int)value.Level100WalkerSelectedWeapon,
        ["jet_selected_weapon"] = (int)value.Level100JetSelectedWeapon, ["hud_emphasis_mask"] = value.Level100HudEmphasisMask,
        ["mission"] = new D { ["tick"] = value.Level100Mission.Tick,
            ["pulse_cannon_availability"] = (int)value.Level100Mission.PulseCannonAvailability,
            ["twin_vulcan_availability"] = (int)value.Level100Mission.TwinVulcanAvailability,
            ["mech_vulcan_availability"] = (int)value.Level100Mission.MechVulcanAvailability,
            ["outcome"] = (int)value.Level100Mission.Outcome, ["failure_reason"] = (int)value.Level100Mission.FailureReason,
            ["terminal_ticks_remaining"] = value.Level100Mission.TerminalTicksRemaining },
        ["actors"] = Pack(value.Level100Actors.Actors, actor => new D { ["actor_id"] = actor.ActorId.Value,
            ["name"] = actor.Name, ["definition_identity"] = actor.DefinitionIdentity,
            ["active"] = actor.Active, ["is_objective"] = actor.IsObjective, ["lifecycle"] = (int)actor.Lifecycle,
            ["has_trigger"] = actor.Trigger.HasValue, ["position"] = Position(actor.Pose.PositionMillimeters),
            ["velocity"] = Position(actor.Pose.LinearVelocityMillimetersPerTick) }),
        ["commanded_allegiances"] = Pack(value.Level100ActorMechanics.Actors, actor => new D {
            ["actor_id"] = actor.ActorId.Value, ["allegiance"] = actor.Allegiance, ["has_override"] = actor.HasAllegianceOverride }),
        ["damage_flashes"] = Pack(value.Level100DamageFlashes, flash => new D {
            ["relative_yaw_micro_rad"] = flash.RelativeYawMicroRad, ["start_tick"] = flash.StartTick }),
    };

    private static D Position(SimVector2 value) => new() { ["x"] = value.X, ["z"] = value.Z };
    private static D Position(SimVector3 value) => new() { ["x"] = value.X, ["y"] = value.Y, ["z"] = value.Z };
    private static D PositionFacts(int x, int y, int z) => new() { ["x"] = x, ["y"] = y, ["z"] = z };
    private static A Pack<T>(IEnumerable<T> items, Func<T, D> convert)
    {
        var result = new A();
        foreach (T item in items) result.Add(convert(item));
        return result;
    }
}
