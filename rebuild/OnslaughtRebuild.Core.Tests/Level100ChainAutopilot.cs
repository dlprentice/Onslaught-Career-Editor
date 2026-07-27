// SPDX-License-Identifier: GPL-3.0-or-later

using OnslaughtRebuild.Core;
using OnslaughtRebuild.TestSupport;

namespace OnslaughtRebuild.Core.Tests;

/// <summary>
/// A single deterministic autopilot for the whole released Level 100 chain.
///
/// <para><b>It drives <see cref="SimInput"/> only.</b> It posts no mission
/// event, writes no world state, and calls no measurement seam: the single Core
/// entry point it touches is <c>Simulation.Step(SimInput)</c>. Every beat it
/// reaches is produced by the released scripts running on the world state that
/// input creates.</para>
///
/// <para><b>It is input-equivalent to a player, not perception-equivalent.</b>
/// It reads <c>actor.Health</c> as an integer where a player reads a bar, and
/// it samples <see cref="Level100Terrain"/> directly where a player looks at a
/// hillside. That is stated here because the difference matters to anyone
/// citing this run as evidence of what a human can do.</para>
///
/// <para>The two things the earlier segment drivers lacked, and which are why
/// the chain stopped on beat 3's fourth target:</para>
/// <list type="number">
///   <item><description><b>A line-of-sight test before firing.</b> The old
///   driver walked to a fixed 18 m stand-off and fired regardless of what was
///   between it and the target. Against <c>Target Tank #23</c> that stand-off
///   is on a ridge 5.5 m above the parked tank, and the pitch that hits the
///   tank puts the round into the intervening crest: 3,578 consecutive rounds
///   landed on terrain. Adding target leading changed that by exactly zero
///   rounds, because leading moves the aim point and the problem was the
///   stance.</description></item>
///   <item><description><b>Repositioning when the stance does not work.</b> The
///   trigger is not a model of why - it is the fact a player uses, that the
///   target's health is not going down.</description></item>
///   <item><description><b>Fire discipline when a miss would hit something the
///   script has not armed yet.</b> See
///   <see cref="CollateralRiskBehind"/>.</description></item>
/// </list>
///
/// <para><b>This driver no longer works around the terrain-pitch sign
/// defect.</b> <c>Simulation.SampleTerrainPitchMicroRad</c> used to have the
/// opposite sign to the two released producers of that quantity, so a walker on
/// a bank could not aim downhill and an earlier revision of this driver walked
/// down the bank instead. With the sign corrected the walker aims downhill from
/// where it stands, and the bank-walking workaround has been removed: it now
/// stops closing and holds still for a precision shot instead.</para>
/// </summary>
internal sealed class Level100ChainAutopilot
{
    /// <summary>Terrain clearance a round needs along the whole ray.</summary>
    private const int LineOfSightClearanceMillimeters = 250;

    /// <summary>Samples taken along the firing ray.</summary>
    private const int LineOfSightSamples = 48;

    /// <summary>Preferred ground stand-off once the shot is clear.</summary>
    private const int GroundStandOffMillimeters = 14_000;

    /// <summary>
    /// Below this the autopilot stops closing and strafes instead: walking
    /// into the target does not clear a crest that is behind the target.
    /// </summary>
    private const int MinimumGroundStandOffMillimeters = 3_500;

    private const int StrafeSegmentTicks = 45;

    private readonly Simulation _simulation;
    private readonly List<string> _log = [];
    private readonly SortedDictionary<int, int> _impactsByActor = [];
    private readonly Level100Terrain _terrain = Level100Terrain.Instance;

    private string? _lastNavigation;
    private int _lastDestroyed = -1;
    private Level100MissionOutcome _lastOutcome = Level100MissionOutcome.Running;
    private readonly HashSet<string> _seenEvents = [];

    private int _strafeTicksRemaining;
    private int _strafeDirection = 1;
    private int _blockedTicks;
    private int _repositionTicksRemaining;
    private Level100ActorId _engagedActorId;
    private int _engagedHealth;
    private int _engagedSinceTick;
    private int _lastProgressKey = int.MinValue;
    private int _lastProgressTick;
    private bool _flightLegCommittedToLanding;
    private bool _flightLegLaunched;
    private Level100MissionTrigger? _flightLegTrigger;

    private Level100ChainAutopilot(Simulation simulation) => _simulation = simulation;

    internal IReadOnlyList<string> Report => _log;

    internal IReadOnlyDictionary<int, int> ImpactsByActor => _impactsByActor;

    internal WorldSnapshot Snapshot => _simulation.Snapshot;

    /// <summary>
    /// One released actor round, recorded on the first tick it is visible in
    /// <c>Level100ActorMechanics.ActorRounds</c>, together with the
    /// <c>AiState</c> its owner held on that tick.
    /// </summary>
    internal readonly record struct ObservedRoundLaunch(
        int Tick,
        int RoundId,
        int OwnerActorId,
        int OwnerAiState);

    private readonly List<ObservedRoundLaunch> _roundLaunches = [];
    private readonly HashSet<int> _seenRoundIds = [];
    private int? _abortTick;
    private IReadOnlyList<Level100ActorCommandIntentSnapshot> _mechanicsAtAbort =
        Array.Empty<Level100ActorCommandIntentSnapshot>();

    /// <summary>Every actor round this run ever saw, in first-seen order.</summary>
    internal IReadOnlyList<ObservedRoundLaunch> RoundLaunches => _roundLaunches;

    /// <summary>
    /// The first tick on which the LevelScript's <c>aborted</c> local was set,
    /// i.e. the tick <c>event("Abort Airborne Drones")</c> landed.
    /// </summary>
    internal int? AbortTick => _abortTick;

    /// <summary>Actor mechanics state as it stood on <see cref="AbortTick"/>.</summary>
    internal IReadOnlyList<Level100ActorCommandIntentSnapshot> MechanicsAtAbort =>
        _mechanicsAtAbort;

    /// <summary>
    /// Records the abort boundary and every round launch either side of it.
    ///
    /// <para>This is always on, and it is the only observable this run carries
    /// that is sensitive to anything happening <b>after</b> the abort. See
    /// <c>Level100FullChainTests.AbortAirborneDrones_SilencesTheDronesThatWereAttacking</c>
    /// for why that matters.</para>
    /// </summary>
    private void RecordArmamentEvidence(WorldSnapshot state)
    {
        if (_abortTick is null && state.Level100Mission.Aborted)
        {
            _abortTick = state.Tick;
            _mechanicsAtAbort = state.Level100ActorMechanics.Actors;
        }

        Dictionary<int, int> aiStateByActor = state.Level100ActorMechanics.Actors
            .ToDictionary(actor => actor.ActorId.Value, actor => actor.AiState);
        foreach (Level100ActorRoundSnapshot round in
                 state.Level100ActorMechanics.ActorRounds)
        {
            if (!_seenRoundIds.Add(round.Id))
            {
                continue;
            }

            _roundLaunches.Add(new ObservedRoundLaunch(
                state.Tick,
                round.Id,
                round.OwnerActorId.Value,
                aiStateByActor.TryGetValue(round.OwnerActorId.Value, out int ai)
                    ? ai
                    : SimulationConstants.ReleasedAiStateOn));
        }
    }

    /// <summary>
    /// A run with all four released tutorial slots already saved
    /// (<c>SLOT_TUTORIAL_1..4</c>). That is a returning player, not a cold
    /// first career: it skips the <c>GetSlot(...) == FALSE</c> arms, which are
    /// the HUD lectures and their <c>player.Deactivate()</c> /
    /// <c>player.Activate()</c> theatre. **It skips no kill gate and no
    /// trigger** - every `numTargets` countdown and every volume test is
    /// outside those arms. Stated because it changes what this run is evidence
    /// of.
    /// </summary>
    internal static Level100ChainAutopilot Create()
    {
        var simulation = new Simulation(
            1u,
            Level100TestActorDefinitions.Create(),
            new Level100TutorialProgress(true, true, true, true));
        for (int tick = 0; tick < SimulationConstants.Level100OpeningPanTicks; tick++)
        {
            simulation.Step(SimInput.Idle);
        }

        return new Level100ChainAutopilot(simulation);
    }

    /// <summary>Runs until the mission leaves <c>Running</c> or the budget ends.</summary>
    internal Level100MissionOutcome Run(int maximumTicks)
    {
        for (int tick = 0; tick < maximumTicks; tick++)
        {
            WorldSnapshot state = _simulation.Snapshot;
            Observe(state);
            if (state.Level100Mission.Outcome != Level100MissionOutcome.Running)
            {
                return state.Level100Mission.Outcome;
            }

            WorldSnapshot next = _simulation.Step(NextInput(state));
            foreach (Level100DestructionEvent destruction in next.Level100DestructionEvents)
            {
                if (destruction.Kind != Level100DestructionEventKind.PulseImpact)
                {
                    continue;
                }

                _impactsByActor.TryGetValue(destruction.ActorId, out int count);
                _impactsByActor[destruction.ActorId] = count + 1;
            }
        }

        WorldSnapshot final = _simulation.Snapshot;
        Observe(final);
        _log.Add(
            $"t{final.Tick} BUDGET EXHAUSTED outcome={final.Level100Mission.Outcome} " +
            $"nav={final.Level100Mission.NavigationObjective ?? "(none)"} " +
            $"mode={final.Mode} hull={final.Hull} pos=({final.PlayerPosition.X},{final.PlayerPosition.Z})");
        LogLiveObjectives(final);
        return final.Level100Mission.Outcome;
    }

    private void Observe(WorldSnapshot state)
    {
        RecordArmamentEvidence(state);
        string? navigation = state.Level100Mission.NavigationObjective;
        if (!string.Equals(navigation, _lastNavigation, StringComparison.Ordinal))
        {
            _log.Add(
                $"t{state.Tick} nav -> {navigation ?? "(none)"} " +
                $"mode={state.Mode} pos=({state.PlayerPosition.X},{state.PlayerPosition.Z}) hull={state.Hull}");
            _lastNavigation = navigation;
        }

        int destroyed = state.Level100Actors.Actors.Count(
            actor => actor.Lifecycle == Level100ActorLifecycle.Destroyed);
        if (destroyed != _lastDestroyed)
        {
            _log.Add(
                $"t{state.Tick} destroyed actors = {destroyed} hull={state.Hull} [" +
                string.Join(", ", state.Level100Actors.Actors
                    .Where(a => a.Lifecycle == Level100ActorLifecycle.Destroyed)
                    .Select(a => a.Name)) + "]");
            _lastDestroyed = destroyed;
        }

        foreach (Level100MissionEvent missionEvent in state.Level100MissionEvents)
        {
            if (missionEvent is Level100MissionEventPosted posted &&
                _seenEvents.Add(posted.EventName + "#" + state.Tick))
            {
                _log.Add($"t{state.Tick} EVENT {posted.EventName}");
            }
        }

        if (state.Level100Mission.Outcome != _lastOutcome)
        {
            _log.Add($"t{state.Tick} OUTCOME {state.Level100Mission.Outcome}");
            _lastOutcome = state.Level100Mission.Outcome;
        }

        // Progress is "a target died or the navigation objective moved". If
        // neither happens for half a released minute the run has stalled, and
        // the stall has to be reported with the numbers that caused it rather
        // than discovered later from a final position.
        int progressKey = destroyed + (_lastNavigation?.Length ?? 0);
        if (progressKey != _lastProgressKey)
        {
            _lastProgressKey = progressKey;
            _lastProgressTick = state.Tick;
        }
        else if (state.Tick - _lastProgressTick > 0 &&
            (state.Tick - _lastProgressTick) % (30 * SimulationConstants.TicksPerSecond) == 0)
        {
            _log.Add(
                $"t{state.Tick} STALLED {(state.Tick - _lastProgressTick) / SimulationConstants.TicksPerSecond}s " +
                Diagnose(state));
        }
    }

    /// <summary>What the autopilot can see right now, in one line.</summary>
    private string Diagnose(WorldSnapshot state)
    {
        string common =
            $"mode={state.Mode} tr={state.Transition} pos=({state.PlayerPosition.X},{state.PlayerPosition.Z}) " +
            $"elev={state.PlayerElevationMillimeters} ground={state.PlayerGroundElevationMillimeters} " +
            $"onGround={state.PlayerOnGround} energy={state.Energy} hull={state.Hull} " +
            $"yaw={state.FacingYawMicroRad} pitch={state.FacingPitchMicroRad} " +
            $"pulse={state.Level100PulseCannonEnabled} twin={state.Level100VulcanCannonEnabled} " +
            $"jetGun={state.Level100MechVulcanCannonEnabled} flight={state.Level100FlightEnabled} " +
            $"control={state.Level100PlayerControlEnabled}";

        Level100ActorSnapshot? zone = ActiveZone(state);
        if (zone is not null)
        {
            return $"{common} zone={zone.Name} d={Horizontal(state, zone.Pose.PositionMillimeters):F0}";
        }

        Level100ActorSnapshot? target = NearestTarget(state);
        if (target is null)
        {
            return $"{common} nothing to do";
        }

        SimVector3 aim = AimPoint(state, target);
        double horizontal = Horizontal(state, aim);
        return $"{common} target={target.Name} hp={target.Health} " +
            $"aim=({aim.X},{aim.Y},{aim.Z}) d={horizontal:F0} " +
            $"yawErr={YawErrorTo(state, aim.X, aim.Z):F4} " +
            $"pitchErr={PitchErrorTo(state, aim, horizontal):F4} " +
            $"los={HasLineOfSight(state, aim)} " +
            $"friendlyOnRay={FriendlyStructureOnTheRay(state, target, aim)} " +
            $"precise={CollateralRiskBehind(state, target)}";
    }

    private void LogLiveObjectives(WorldSnapshot state)
    {
        foreach (Level100ActorSnapshot actor in state.Level100Actors.Actors
            .Where(actor => actor.IsObjective && actor.Active &&
                actor.Lifecycle == Level100ActorLifecycle.Alive)
            .OrderBy(actor => actor.ActorId.Value))
        {
            SimVector3 position = actor.Pose.PositionMillimeters;
            _log.Add(
                $"  live objective {actor.ActorId.Value} {actor.Name} grp={actor.TargetGroup} " +
                $"hp={actor.Health} pos=({position.X},{position.Y},{position.Z}) " +
                $"d={Horizontal(state, position):F0} los={HasLineOfSight(state, AimPoint(state, actor))}");
        }
    }

    // ------------------------------------------------------------------
    // Decision
    // ------------------------------------------------------------------

    private SimInput NextInput(WorldSnapshot state)
    {
        if (!state.Level100PlayerControlEnabled)
        {
            return SimInput.Idle;
        }

        Level100ActorSnapshot? zone = ActiveZone(state);
        if (zone is not null)
        {
            return NavigateToZone(state, zone);
        }

        _flightLegTrigger = null;
        _flightLegLaunched = false;
        _flightLegCommittedToLanding = false;

        Level100ActorSnapshot? target = NearestTarget(state);
        if (target is not null)
        {
            return Engage(state, target);
        }

        return Hold(state);
    }

    /// <summary>The trigger volume the released script currently wants entered.</summary>
    private static Level100ActorSnapshot? ActiveZone(WorldSnapshot state) =>
        state.Level100Actors.Actors.FirstOrDefault(actor =>
            actor.Trigger.HasValue &&
            actor.Active &&
            actor.IsObjective &&
            !actor.TriggerEventDispatched &&
            !actor.TriggerEntered);

    /// <summary>The nearest live scored target the script has activated.</summary>
    private static Level100ActorSnapshot? NearestTarget(WorldSnapshot state) =>
        state.Level100Actors.Actors
            .Where(actor =>
                actor.IsObjective &&
                actor.Active &&
                actor.Lifecycle == Level100ActorLifecycle.Alive &&
                actor.TargetGroup != Level100MissionTargetGroup.None &&
                actor.TargetGroup != Level100MissionTargetGroup.AirTrainer)
            .OrderBy(actor => Horizontal(state, actor.Pose.PositionMillimeters))
            .FirstOrDefault();

    /// <summary>
    /// Nothing to shoot. Either the script is talking, or - and this is beat
    /// 5's whole lesson - the Air Trainer is making its thirty-second attack
    /// run with both walker weapons disabled. <c>TUTORIAL_DODGE</c> tells the
    /// player to move, and standing still costs hull for no reason: measured,
    /// an earlier revision that idled here arrived at beat 9 with 750 of 1000
    /// hull instead of 1000, which is most of the margin the six attacking
    /// drones then eat.
    /// </summary>
    private static SimInput Hold(WorldSnapshot state)
    {
        if (state.Transition != VehicleTransition.None)
        {
            return SimInput.Idle;
        }

        if (state.Mode != VehicleMode.Walker)
        {
            return new SimInput(0, 0, SimActions.ToggleMode);
        }

        return UnderAttack(state)
            ? new SimInput(EvasiveStrafe(state), 0)
            : SimInput.Idle;
    }

    /// <summary>Is something in the world currently shooting at the player?</summary>
    private static bool UnderAttack(WorldSnapshot state) =>
        state.Level100Actors.Actors.Any(actor =>
            actor.Active &&
            actor.Lifecycle == Level100ActorLifecycle.Alive &&
            actor.TargetGroup is Level100MissionTargetGroup.AirTrainer
                or Level100MissionTargetGroup.AirborneTargets2);

    /// <summary>
    /// A lateral weave. Strafe rather than run: it keeps the body pointed where
    /// the reticle needs to be, and it does not walk the autopilot off a bank
    /// or into the water while it is not looking where it is going.
    /// </summary>
    private static sbyte EvasiveStrafe(WorldSnapshot state) =>
        (state.Tick / (2 * SimulationConstants.TicksPerSecond)) % 2 == 0
            ? (sbyte)1
            : (sbyte)-1;

    // ------------------------------------------------------------------
    // Navigation
    // ------------------------------------------------------------------

    private SimInput NavigateToZone(WorldSnapshot state, Level100ActorSnapshot zone)
    {
        SimVector3 position = zone.Pose.PositionMillimeters;
        double horizontal = Horizontal(state, position);
        if (state.Level100FlightEnabled && horizontal > 20_000)
        {
            return FlyLeg(state, zone, horizontal);
        }

        // Walk the last metres in, or the whole way before flight is taught.
        if (state.Mode != VehicleMode.Walker)
        {
            return state.Transition == VehicleTransition.None
                ? new SimInput(0, 0, SimActions.ToggleMode)
                : SimInput.Idle;
        }

        if (state.Transition != VehicleTransition.None)
        {
            return SimInput.Idle;
        }

        double yawError = YawErrorTo(state, position.X, position.Z);
        short lookX = LookAxis(yawError, 2_000);
        double pitchError = -(state.FacingPitchMicroRad / 1_000_000d);
        short lookY = LookAxis(pitchError, 4_000);
        sbyte forward = horizontal > 1_500 ? (sbyte)1 : (sbyte)0;
        SimActions actions = state.PlayerOnGround ? SimActions.None : SimActions.LandingJets;
        return new SimInput(0, forward, actions, 0, 0, lookX, lookY);
    }

    /// <summary>
    /// One released flight leg. Identical in policy to the measured
    /// <c>Level100FlightLegDriver</c>: transform once, hold a shallow climb
    /// clear of the ground effect, fly the bearing, then drop out of jet mode
    /// and ride the landing thrusters down into the volume - because
    /// <c>TargetZoneN.msl</c> tests <c>InJetMode() == FALSE</c>.
    /// </summary>
    private SimInput FlyLeg(
        WorldSnapshot state,
        Level100ActorSnapshot zone,
        double horizontal)
    {
        if (_flightLegTrigger != zone.Trigger)
        {
            _flightLegTrigger = zone.Trigger;
            _flightLegLaunched = false;
            _flightLegCommittedToLanding = false;
        }

        SimVector3 position = zone.Pose.PositionMillimeters;
        double yawError = YawErrorTo(state, position.X, position.Z);
        short lookX = LookAxis(yawError, 2_000);

        if (!_flightLegLaunched)
        {
            if (state.Transition != VehicleTransition.None)
            {
                return SimInput.Idle;
            }

            if (state.Mode == VehicleMode.Jet)
            {
                _flightLegLaunched = true;
            }
            else
            {
                return new SimInput(0, 0, SimActions.ToggleMode);
            }
        }

        if (state.Mode == VehicleMode.Jet && state.Transition == VehicleTransition.None)
        {
            int altitude = state.PlayerAltitudeAboveGroundMillimeters;
            double targetPitch = altitude < 12_000 ? -0.20 : 0.0;
            double pitchError = targetPitch - (state.FacingPitchMicroRad / 1_000_000d);
            short lookY = LookAxis(pitchError, 4_000);
            if (horizontal < 12_000)
            {
                _flightLegCommittedToLanding = true;
                return new SimInput(0, -1, SimActions.ToggleMode, 0, 0, lookX, lookY);
            }

            sbyte throttle = horizontal > 40_000 ? (sbyte)1 : (sbyte)0;
            return new SimInput(0, throttle, SimActions.None, 0, 0, lookX, lookY);
        }

        if (state.Mode == VehicleMode.Walker && state.Transition == VehicleTransition.None)
        {
            SimActions actions = _flightLegCommittedToLanding && !state.PlayerOnGround
                ? SimActions.LandingJets
                : SimActions.None;
            sbyte forward = state.PlayerOnGround && horizontal > 1_500 ? (sbyte)1 : (sbyte)0;
            double pitchError = -(state.FacingPitchMicroRad / 1_000_000d);
            short lookY = LookAxis(pitchError, 4_000);
            return new SimInput(0, forward, actions, 0, 0, lookX, lookY);
        }

        return SimInput.Idle;
    }

    // ------------------------------------------------------------------
    // Engagement
    // ------------------------------------------------------------------

    private SimInput Engage(WorldSnapshot state, Level100ActorSnapshot target)
    {
        bool airborneTarget =
            target.TargetGroup is Level100MissionTargetGroup.AirborneTargets1
                or Level100MissionTargetGroup.AirborneTargets2;

        // Both drone waves are fought in the air.
        //
        // Beat 7 has no choice: the script disables both walker weapons at the
        // end of beat 5 and only re-enables them at beat 8, so the jet's Mech
        // Vulcan Cannon is the only weapon the player owns for the first wave.
        //
        // Beat 9 is a choice, and it is the one the level teaches - the
        // LevelScript plays TUTORIAL_STRAFE at the head of
        // event("Reached Target Zone 3"), immediately before the second wave.
        // The numbers say the same thing. The wave-2 drones carry the Forseti
        // Drone Missile Launcher at CWeaponMaxRange 80.0 while the player's
        // Pulse Cannon round expires at 46.7 m, so a walker cannot answer them
        // at the range they open fire, and closing on foot at
        // WalkerMaximumSpeedPerTick costs eleven seconds inside their envelope.
        // Measured with a walker: 750 -> 0 hull, no wave-2 drone destroyed.
        if (airborneTarget)
        {
            return EngageFromJet(state, target);
        }

        if (state.Mode != VehicleMode.Walker)
        {
            return state.Transition == VehicleTransition.None
                ? new SimInput(0, 0, SimActions.ToggleMode)
                : SimInput.Idle;
        }

        if (state.Transition != VehicleTransition.None)
        {
            return SimInput.Idle;
        }

        return EngageFromWalker(state, target);
    }

    /// <summary>
    /// A ground target, on foot. Every target that reaches this method is a
    /// ground target: <see cref="Engage"/> routes both drone waves to the jet.
    /// </summary>
    private SimInput EngageFromWalker(
        WorldSnapshot state,
        Level100ActorSnapshot target)
    {
        // Is there something the script has not armed yet in the volume a miss
        // would land in? If so this is a precision shot, not a brawl: the hull
        // sweep comes off, the feet stop, and the trigger tolerance tightens.
        // Measured cost of getting this wrong: two rounds.
        bool precise = CollateralRiskBehind(state, target);

        SimVector3 aim = AimPoint(state, target, sweep: !precise);
        double horizontal = Horizontal(state, aim);
        double yawError = YawErrorTo(state, aim.X, aim.Z);
        short lookX = LookAxis(yawError, 2_000);
        double pitchError = PitchErrorTo(state, aim, horizontal);
        short lookY = LookAxis(pitchError, 4_000);

        // The whole point of this driver: a parked vehicle on the far side of a
        // crest cannot be shot from the near side, and firing into that crest
        // is what stalled the chain for 3,578 rounds.
        bool clear = HasLineOfSight(state, aim) &&
            !FriendlyStructureOnTheRay(state, target, aim);

        // A stance can be unusable even with a perfectly clear ray. The
        // released walker pitch limiter (CBattleEngine,
        // references/Onslaught/BattleEngine.cpp:1125-1180, transcribed in
        // Simulation.ApplyWalkerTerrainPitchLimit) is terrain-relative, so
        // standing on the lip of a steep bank caps how far the nose will come
        // down: measured at (-94335, 31781), where the ground falls 1.12 m per
        // metre, the reachable pitch was 0.07-0.13 rad against the 0.27 rad the
        // shot needed, and an earlier revision of this driver stood there for
        // 180 released seconds with a clear line of sight and a converged yaw.
        //
        // Rather than model that limit - a driver that predicts the engine's
        // constraints is a second implementation of the engine, and will be
        // wrong somewhere else - the test is the one a player actually applies:
        // THE TARGET'S HEALTH IS NOT GOING DOWN. That covers the pitch limiter,
        // an aim point that misses the hull, an occluder the sampled ray
        // stepped over, and anything else not yet met.
        if (target.ActorId != _engagedActorId)
        {
            _engagedActorId = target.ActorId;
            _engagedHealth = target.Health;
            _engagedSinceTick = state.Tick;
            _repositionTicksRemaining = 0;
        }
        else if (target.Health < _engagedHealth)
        {
            _engagedHealth = target.Health;
            _engagedSinceTick = state.Tick;
        }

        bool notHurtingIt = clear &&
            horizontal <= GroundStandOffMillimeters &&
            state.Tick - _engagedSinceTick > 4 * SimulationConstants.TicksPerSecond;
        if (!clear || notHurtingIt)
        {
            _repositionTicksRemaining = Math.Max(
                _repositionTicksRemaining,
                2 * SimulationConstants.TicksPerSecond);
            if (notHurtingIt)
            {
                _engagedSinceTick = state.Tick;
            }
        }

        // A precision shot is taken standing still. Every metre walked while
        // aiming moves the terrain pitch the released limiter is holding the
        // nose against, and the misses that killed Target Truck #25 were 0.06
        // rad high while the walker was closing at speed.
        if (precise && clear && horizontal <= GroundStandOffMillimeters)
        {
            _repositionTicksRemaining = 0;
            _strafeTicksRemaining = 0;
        }

        sbyte forward = 0;
        sbyte strafe = 0;
        if (_repositionTicksRemaining > 0)
        {
            _repositionTicksRemaining--;
            _blockedTicks++;
            if (horizontal > MinimumGroundStandOffMillimeters && _strafeTicksRemaining == 0)
            {
                // Close in. Most crests stop occluding once the muzzle is past
                // them, and closing shortens the ray.
                forward = 1;
            }
            else
            {
                if (_strafeTicksRemaining == 0)
                {
                    _strafeTicksRemaining = StrafeSegmentTicks;
                    _strafeDirection = -_strafeDirection;
                }

                _strafeTicksRemaining--;
                strafe = (sbyte)_strafeDirection;
            }
        }
        else
        {
            _blockedTicks = 0;
            _strafeTicksRemaining = 0;
            if (horizontal > GroundStandOffMillimeters)
            {
                forward = 1;
            }

            // If something is shooting while this ground target is being
            // engaged, keep weaving: the strafe axis is independent of the aim
            // axis, so it costs nothing in accuracy.
            if (UnderAttack(state))
            {
                strafe = EvasiveStrafe(state);
            }
        }

        // Neither closing nor this strafe leg is working; try the other side.
        if (_blockedTicks > 15 * SimulationConstants.TicksPerSecond)
        {
            _blockedTicks = 0;
            _strafeDirection = -_strafeDirection;
            _strafeTicksRemaining = StrafeSegmentTicks * 2;
        }

        double tolerance = precise
            ? PrecisionTolerance(horizontal)
            : FireTolerance(horizontal);
        SimActions actions =
            clear && Math.Abs(yawError) < tolerance && Math.Abs(pitchError) < tolerance
                ? SimActions.Fire
                : SimActions.None;
        return new SimInput(strafe, forward, actions, 0, 0, lookX, lookY);
    }

    /// <summary>Energy at which a sortie is launched.</summary>
    private const int SortieLaunchEnergy = 7_000;

    /// <summary>Energy at which the jet comes home rather than stalling.</summary>
    private const int SortieRecoverEnergy = 900;

    /// <summary>
    /// Beat 7's drone wave, flown. The Aquila is not a helicopter: it cannot
    /// hold station on a target, and holding full throttle empties the store -
    /// the released Aquila Prototype costs are 0.005-0.012 energy per retail
    /// tick against a store of 8.0, which is 33-47 released seconds of flight,
    /// while `WalkerEnergyRegenerationPerTick` refills it only on the ground.
    /// So this flies discrete sorties: charge on the ground, launch, make firing
    /// passes, and come home before the store empties rather than stalling out
    /// of the sky, which is what an earlier revision did sixteen times.
    /// </summary>
    private SimInput EngageFromJet(WorldSnapshot state, Level100ActorSnapshot target)
    {
        if (state.Transition != VehicleTransition.None)
        {
            return SimInput.Idle;
        }

        SimVector3 aim = AimPoint(state, target);
        double horizontal = Horizontal(state, aim);
        double yawError = YawErrorTo(state, aim.X, aim.Z);
        short lookX = LookAxis(yawError, 2_000);
        int altitude = state.PlayerAltitudeAboveGroundMillimeters;

        if (state.Mode != VehicleMode.Jet)
        {
            // Launching on a part-full store was measured and is worse, not
            // better: with a third of the store the beat-9 sortie ran itself
            // dry 33 m further out than the abort's Target Zone 4 objective and
            // the run was lost on the way back. Charge fully, then commit.
            if (state.Energy < SortieLaunchEnergy)
            {
                // Charging. Face the wave and hold the landing thrusters if
                // still coming down; standing still is what refills the store.
                double groundPitchError = -(state.FacingPitchMicroRad / 1_000_000d);
                return new SimInput(
                    0,
                    0,
                    state.PlayerOnGround ? SimActions.None : SimActions.LandingJets,
                    0,
                    0,
                    lookX,
                    LookAxis(groundPitchError, 4_000));
            }

            return new SimInput(0, 0, SimActions.ToggleMode);
        }

        if (state.Energy < SortieRecoverEnergy)
        {
            // Out of store: put it down deliberately.
            return new SimInput(0, -1, SimActions.ToggleMode, 0, 0, lookX, 0);
        }

        // Climb clear of the ground-effect band first; it fights the nose and
        // the drones cruise five to fifty units above the terrain anyway.
        double pitchError = altitude < 9_000
            ? -0.25 - (state.FacingPitchMicroRad / 1_000_000d)
            : PitchErrorTo(state, aim, horizontal);
        short lookY = LookAxis(pitchError, 4_000);

        // Throttle: full only when there is ground to make up. Closing at
        // 18 m/s on a target 6 m away just produces another overshoot, and
        // every tick of full throttle is store that the next pass needs.
        sbyte throttle = horizontal > 60_000 ? (sbyte)1 : (sbyte)0;
        if (horizontal < 20_000 || Math.Abs(yawError) > 0.7)
        {
            throttle = -1;
        }

        double tolerance = FireTolerance(horizontal);
        SimActions actions =
            altitude >= 6_000 &&
            horizontal is > 3_000 and < 50_000 &&
            Math.Abs(yawError) < tolerance &&
            Math.Abs(pitchError) < tolerance
                ? SimActions.Fire
                : SimActions.None;
        return new SimInput(0, throttle, actions, 0, 0, lookX, lookY);
    }

    // ------------------------------------------------------------------
    // Geometry a player can see
    // ------------------------------------------------------------------

    /// <summary>
    /// Where on the target the reticle goes. A player sweeps the body rather
    /// than shooting at the pivot; the sweep also covers the unmodelled
    /// difference between an actor's origin and its hull centre.
    /// </summary>
    private static SimVector3 AimPoint(
        WorldSnapshot state,
        Level100ActorSnapshot target,
        bool sweep = true)
    {
        SimVector3 position = target.Pose.PositionMillimeters;
        double rawX = (double)position.X - state.PlayerPosition.X;
        double rawZ = (double)position.Z - state.PlayerPosition.Z;
        double range = Math.Sqrt((rawX * rawX) + (rawZ * rawZ));
        double flightTicks = range / SimulationConstants.ProjectileSpeedPerTick;

        // The sweep is bounded in *angle*, not in millimetres. A fixed 200 mm
        // ladder is a fifth of a radian at four metres, which fights the pitch
        // controller instead of searching the hull with it. A flying target
        // gets no sweep at all: it is already moving through the ladder faster
        // than the ladder moves, and the shot has to be taken now.
        //
        // The sweep also comes off entirely when a miss would land on an
        // unarmed tutorial target: searching the hull with a ladder means
        // deliberately putting rounds above and below it, and above it is where
        // Target Truck #25 is.
        int aimHeight = 0;
        if (!IsAirborneTarget(target))
        {
            aimHeight = 600;
            if (sweep)
            {
                int ladder = (int)Math.Clamp(range * 0.012, 100, 700);
                aimHeight += (((state.Tick / 11) % 5) - 2) * ladder / 2;
            }
        }

        return new SimVector3(
            (int)(position.X + (target.Pose.LinearVelocityMillimetersPerTick.X * flightTicks)),
            position.Y + aimHeight,
            (int)(position.Z + (target.Pose.LinearVelocityMillimetersPerTick.Z * flightTicks)));
    }

    private static bool IsAirborneTarget(Level100ActorSnapshot target) =>
        target.TargetGroup is Level100MissionTargetGroup.AirborneTargets1
            or Level100MissionTargetGroup.AirborneTargets2;

    /// <summary>
    /// How tight the aim has to be before firing. A fixed radian tolerance is
    /// wrong at both ends: at 4 m it lets the round miss the hull entirely, and
    /// at 40 m it refuses shots a player would take. This is the angle
    /// subtended by roughly a metre of target at the current range.
    /// </summary>
    private static double FireTolerance(double range) =>
        Math.Clamp(1_100.0 / Math.Max(range, 1.0), 0.02, 0.15);

    /// <summary>
    /// Does the ground let this shot through? Sampled along the ray from the
    /// evidenced muzzle to the aim point. This is the check the previous driver
    /// did not make.
    /// </summary>
    private bool HasLineOfSight(WorldSnapshot state, SimVector3 aim)
    {
        double startX = state.PlayerPosition.X;
        double startZ = state.PlayerPosition.Z;
        double startY = state.PlayerElevationMillimeters +
            SimulationConstants.PulseCannonEmitterUpMillimeters;
        double deltaX = aim.X - startX;
        double deltaY = aim.Y - startY;
        double deltaZ = aim.Z - startZ;

        for (int sample = 1; sample < LineOfSightSamples; sample++)
        {
            double fraction = (double)sample / LineOfSightSamples;
            int x = (int)(startX + (deltaX * fraction));
            int z = (int)(startZ + (deltaZ * fraction));
            double y = startY + (deltaY * fraction);
            int ground = _terrain.SampleGroundElevationMillimeters(new SimVector2(x, z));
            if (ground + LineOfSightClearanceMillimeters > y)
            {
                return false;
            }
        }

        return true;
    }

    /// <summary>
    /// Is a script-bearing friendly structure standing in the shot? Every
    /// <c>Facilities</c>, <c>TankFactory</c>, <c>Hangar</c> and <c>Turret</c>
    /// actor answers <c>hit(THING_TYPE_AMMUNITION)</c> with
    /// <c>PostEvent("Hit Friendly Building")</c>, and the released LevelScript
    /// turns the twenty-first of those into <c>Friendly Building Destroyed</c>
    /// and then <c>LevelLostString</c>. A player does not shoot through the
    /// tank factory to reach a target behind it, and an autopilot that does
    /// loses the level rather than stalling - which is a worse failure,
    /// because it looks like progress.
    /// </summary>
    private static bool FriendlyStructureOnTheRay(
        WorldSnapshot state,
        Level100ActorSnapshot target,
        SimVector3 aim)
    {
        const int StructureStandOffMillimeters = 9_000;
        double startX = state.PlayerPosition.X;
        double startZ = state.PlayerPosition.Z;
        double deltaX = aim.X - startX;
        double deltaZ = aim.Z - startZ;
        double lengthSquared = (deltaX * deltaX) + (deltaZ * deltaZ);
        if (lengthSquared < 1.0)
        {
            return false;
        }

        foreach (Level100ActorSnapshot actor in state.Level100Actors.Actors)
        {
            if (actor.ActorId == target.ActorId ||
                actor.TargetGroup != Level100MissionTargetGroup.None ||
                actor.Trigger.HasValue ||
                actor.ScriptName is not ("Facilities" or "TankFactory" or "Hangar" or "Turret"))
            {
                continue;
            }

            double toX = actor.Pose.PositionMillimeters.X - startX;
            double toZ = actor.Pose.PositionMillimeters.Z - startZ;
            double projection = ((toX * deltaX) + (toZ * deltaZ)) / lengthSquared;
            if (projection is <= 0 or >= 1)
            {
                continue;
            }

            double offsetX = toX - (projection * deltaX);
            double offsetZ = toZ - (projection * deltaZ);
            if ((offsetX * offsetX) + (offsetZ * offsetZ) <
                (double)StructureStandOffMillimeters * StructureStandOffMillimeters)
            {
                return true;
            }
        }

        return false;
    }

    /// <summary>
    /// Would a miss land on a tutorial target the script has <b>not armed
    /// yet</b>?
    ///
    /// <para>Killing one is the losing move that
    /// <see cref="Level100FullChainTests.NaiveWalkerAutopilot_BreaksTheTutorialAndLoses"/>
    /// exists to demonstrate, and it is a hazard for a competent driver too.
    /// Every <c>TargetTruckN.msl</c> answers <c>died()</c> with
    /// <c>switch (activated)</c>, and the <c>case FALSE</c> arm is
    /// <c>PostEvent("Broke Tutorial")</c> -&gt;
    /// <c>LevelLostString(LOSE_TUTORIAL_BROKE)</c>.</para>
    ///
    /// <para><c>IsObjective</c> is the observable that tracks those scripts'
    /// <c>activated</c> local: <c>event("Activate Static Targets 2")</c> is the
    /// one handler that both sets <c>activated = TRUE</c> and calls
    /// <c>SetObjective()</c>. A player reads the same thing off the HUD - the
    /// target is not marked yet, so it is not a target yet.</para>
    ///
    /// <para><b>Measured, and the numbers are why this switches the driver's
    /// behaviour instead of vetoing the shot.</b> <c>Target Truck #25</c> is
    /// parked at (31663, 68922) and beat 3's <c>Target Tank #23</c> at
    /// (31409, 70361) - <b>1.46 m apart</b>. The perpendicular distance from
    /// the shot line to the truck therefore never exceeds 1.46 m from any
    /// stance in the level, while the corridor a miss can wander into is 3.0 m
    /// of truck body plus the aim slop <see cref="FireTolerance"/> allows. No
    /// stance clears it, and a revision that treated this predicate as a veto
    /// was measured holding the trigger shut for 900 released seconds at 3.2 m
    /// with a clear ray and a converged reticle.</para>
    ///
    /// <para>What actually killed the truck was two rounds, not a spray: a
    /// pulse round takes 1,800 off a 3,000-hull truck, and the two that reached
    /// it were 0.06 rad high - inside the 0.15 rad
    /// <see cref="FireTolerance"/> ceiling - fired while closing at speed from
    /// 4.9 m above the tank, so they cleared the tank's hull and carried on
    /// down-range into the truck 1.46 m behind it. The answer is therefore the
    /// player's: stop, drop the hull-search ladder, and do not pull the trigger
    /// until the reticle is inside the hull rather than merely on the target.
    /// See <see cref="PrecisionTolerance"/>.</para>
    /// </summary>
    private static bool CollateralRiskBehind(
        WorldSnapshot state,
        Level100ActorSnapshot target)
    {
        // How far past the target a miss still matters. The round is not
        // stopped by the aim point - it flies for
        // ProjectileLifetimeTicks * ProjectileSpeedPerTick = 46.7 m - but a
        // miss that stays near the line of the shot is the one that reaches an
        // unarmed actor, and beyond this the terrain has taken it.
        const int OverShootMillimeters = 20_000;

        // Body half-width to allow around an unarmed actor's origin. The
        // released Target Truck is a vehicle, not a point.
        const int CollateralBodyMillimeters = 3_000;

        SimVector3 position = target.Pose.PositionMillimeters;
        double startX = state.PlayerPosition.X;
        double startZ = state.PlayerPosition.Z;
        double deltaX = position.X - startX;
        double deltaZ = position.Z - startZ;
        double lengthSquared = (deltaX * deltaX) + (deltaZ * deltaZ);
        if (lengthSquared < 1.0)
        {
            return false;
        }

        double length = Math.Sqrt(lengthSquared);
        double maximumProjection = 1.0 + (OverShootMillimeters / length);
        double corridor =
            CollateralBodyMillimeters + (length * FireTolerance(length));

        foreach (Level100ActorSnapshot actor in state.Level100Actors.Actors)
        {
            if (actor.ActorId == target.ActorId ||
                actor.TargetGroup == Level100MissionTargetGroup.None ||
                actor.Lifecycle != Level100ActorLifecycle.Alive ||
                actor.IsObjective)
            {
                continue;
            }

            double toX = actor.Pose.PositionMillimeters.X - startX;
            double toZ = actor.Pose.PositionMillimeters.Z - startZ;
            double projection = ((toX * deltaX) + (toZ * deltaZ)) / lengthSquared;
            if (projection <= 0 || projection > maximumProjection)
            {
                continue;
            }

            double offsetX = toX - (projection * deltaX);
            double offsetZ = toZ - (projection * deltaZ);
            if ((offsetX * offsetX) + (offsetZ * offsetZ) < corridor * corridor)
            {
                return true;
            }
        }

        return false;
    }

    /// <summary>
    /// The trigger tolerance when a miss would land on something the script has
    /// not armed. This is the angle subtended by half a metre at the target -
    /// well inside the hull - rather than the angle subtended by a metre, which
    /// is what <see cref="FireTolerance"/> allows and which is what put two
    /// rounds through <c>Target Truck #25</c>.
    /// </summary>
    private static double PrecisionTolerance(double range) =>
        Math.Clamp(500.0 / Math.Max(range, 1.0), 0.004, 0.030);

    private static double Horizontal(WorldSnapshot state, SimVector3 position)
    {
        double deltaX = (double)position.X - state.PlayerPosition.X;
        double deltaZ = (double)position.Z - state.PlayerPosition.Z;
        return Math.Sqrt((deltaX * deltaX) + (deltaZ * deltaZ));
    }

    private static double YawErrorTo(WorldSnapshot state, int x, int z)
    {
        double deltaX = (double)x - state.PlayerPosition.X;
        double deltaZ = (double)z - state.PlayerPosition.Z;
        return NormalizeRadians(
            Math.Atan2(-deltaX, deltaZ) - (state.FacingYawMicroRad / 1_000_000d));
    }

    private static double PitchErrorTo(WorldSnapshot state, SimVector3 aim, double horizontal) =>
        -Math.Atan2(
            aim.Y - state.PlayerElevationMillimeters,
            Math.Max(1.0, horizontal)) -
        (state.FacingPitchMicroRad / 1_000_000d);

    private static short LookAxis(double error, double gain) =>
        (short)Math.Clamp((int)(error * gain), -1_000, 1_000);

    private static double NormalizeRadians(double value)
    {
        while (value > Math.PI)
        {
            value -= 2 * Math.PI;
        }

        while (value < -Math.PI)
        {
            value += 2 * Math.PI;
        }

        return value;
    }
}
