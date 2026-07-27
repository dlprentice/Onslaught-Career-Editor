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
    /// One simulated tick on which the player released a weapon, paired with
    /// the number of player rounds that tick actually created.
    ///
    /// <para><see cref="Events"/> is the whole ordered stream for the tick, not
    /// a count, so a producer that emitted one cue per ROUND instead of one per
    /// RELEASE is visible here rather than having to be inferred.</para>
    /// </summary>
    internal readonly record struct ObservedPlayerWeaponRelease(
        int Tick,
        IReadOnlyList<Level100WeaponFireEvent> Events,
        int RoundsCreated);

    private readonly List<ObservedPlayerWeaponRelease> _playerWeaponReleases = [];
    private int _lastObservedTick = -1;
    private int _lastObservedNextProjectileId;

    /// <summary>Every player weapon release this run saw, in tick order.</summary>
    internal IReadOnlyList<ObservedPlayerWeaponRelease> PlayerWeaponReleases =>
        _playerWeaponReleases;

    /// <summary>
    /// Pairs each tick's <c>Level100WeaponFireEvents</c> with the advance of
    /// <c>NextProjectileId</c> over the same tick. The id watermark is used
    /// rather than the live projectile list because a round can be created and
    /// expire without ever being sampled.
    /// </summary>
    private void RecordPlayerWeaponFire(WorldSnapshot state)
    {
        if (state.Tick == _lastObservedTick)
        {
            return;
        }

        int roundsCreated = state.NextProjectileId - _lastObservedNextProjectileId;
        bool contiguous = state.Tick == _lastObservedTick + 1;
        _lastObservedTick = state.Tick;
        _lastObservedNextProjectileId = state.NextProjectileId;
        if (state.Level100WeaponFireEvents.Count == 0)
        {
            return;
        }

        _playerWeaponReleases.Add(new ObservedPlayerWeaponRelease(
            state.Tick,
            state.Level100WeaponFireEvents,
            contiguous ? roundsCreated : -1));
    }

    /// <summary>
    /// The first tick on which the LevelScript's <c>aborted</c> local was set,
    /// i.e. the tick <c>event("Abort Airborne Drones")</c> landed.
    /// </summary>
    internal int? AbortTick => _abortTick;

    /// <summary>Actor mechanics state as it stood on <see cref="AbortTick"/>.</summary>
    internal IReadOnlyList<Level100ActorCommandIntentSnapshot> MechanicsAtAbort =>
        _mechanicsAtAbort;

    private readonly Dictionary<int, int> _waveTwoPeakHealth = [];
    private readonly Dictionary<int, int> _waveTwoLowestHealth = [];

    /// <summary>
    /// Total hull removed from the six <c>AirborneDrone2</c> spawns across the
    /// whole run, in the released health units the registry reports.
    ///
    /// <para>Pure observation, like <see cref="Blasters"/>: it reads only
    /// snapshot fields the driver already consults and is never fed back into a
    /// decision. A destroyed drone contributes its full life; a damaged one
    /// contributes the deepest cut it ever took, so a spawn that is destroyed
    /// after being wounded is not double-counted and one that is wounded and
    /// then vanishes from the snapshot is not lost.</para>
    ///
    /// <para><b>Why this exists.</b> It replaces the wave-2 <b>kill count</b> as
    /// the evidence that the driver is still fighting beat 9. The kill count is
    /// chaotic at a resolution finer than the simulation's own input
    /// quantisation - see the remarks on
    /// <c>Level100FullChainTests.ChainAutopilot_ReachesWonByInputAlone</c> - and
    /// damage dealt is not, because it accumulates every hit instead of only
    /// the last one of six.</para>
    /// </summary>
    internal int WaveTwoDamageDealt => _waveTwoPeakHealth
        .Sum(pair => pair.Value - _waveTwoLowestHealth[pair.Key]);

    /// <summary>How many wave-2 spawns took any damage at all.</summary>
    internal int WaveTwoSpawnsDamaged => _waveTwoPeakHealth
        .Count(pair => _waveTwoLowestHealth[pair.Key] < pair.Value);

    private void RecordWaveTwoDamage(WorldSnapshot state)
    {
        foreach (Level100ActorSnapshot actor in state.Level100Actors.Actors)
        {
            if (actor.TargetGroup != Level100MissionTargetGroup.AirborneTargets2)
            {
                continue;
            }

            int id = actor.ActorId.Value;
            int health = actor.Lifecycle == Level100ActorLifecycle.Destroyed
                ? 0
                : actor.Health;
            if (!_waveTwoPeakHealth.TryGetValue(id, out int peak) || health > peak)
            {
                _waveTwoPeakHealth[id] = Math.Max(peak, health);
            }

            if (!_waveTwoLowestHealth.TryGetValue(id, out int lowest) || health < lowest)
            {
                _waveTwoLowestHealth[id] = health;
            }
        }
    }

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

    /// <summary>
    /// The same run with the trigger held shut for the whole of beat 9.
    ///
    /// <para><b>This is a control, and it is the only way two of this suite's
    /// measurements are still takeable.</b> Both
    /// <see cref="Level100FullChainTests.AbortAirborneDrones_SilencesTheDronesThatWereAttacking"/>
    /// and
    /// <see cref="Level100FullChainTests.BlasterMissLaw_SeparatesTheRunsOwnHitsFromItsMisses"/>
    /// observe things that only happen to a player who is losing beat 9: the
    /// released sub-40 % <c>Abort Airborne Drones</c> poll, and Blasters
    /// launched at a player whose crossing speed is below what the
    /// <c>18 / slant</c> law needs. The main run no longer supplies either,
    /// because it clears the wave. Neither assertion in either test was
    /// changed; they were given a run that still reaches the state they are
    /// about.</para>
    ///
    /// <para>The only difference is <see cref="SimActions.Fire"/> in beat 9.
    /// Firing does not steer this airframe - <c>Simulation.TryFire</c> runs
    /// after <c>UpdateMovement</c> and touches no motion state - so this is
    /// the same sortie, flown by the same controller, that simply never shoots
    /// anything down.</para>
    /// </summary>
    internal static Level100ChainAutopilot CreateWithWaveTwoTriggerHeldShut()
    {
        Level100ChainAutopilot driver = Create();
        driver._waveTwoTriggerHeldShut = true;
        return driver;
    }

    private bool _waveTwoTriggerHeldShut;

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

    /// <summary>
    /// The last place the player stood on dry land. A sortie that chases a
    /// drone out over the sea and then puts down - or simply runs its store
    /// dry - is <c>Level100MissionFailureReason.WaterLoss</c>, which is a lost
    /// level at full hull. Measured: an earlier revision of this driver
    /// followed the third wave-1 drone west and drowned at (-107362, 52796)
    /// with 17,500 of 20,000 hull intact.
    /// </summary>
    private SimVector2 _lastDryGround;

    // ------------------------------------------------------------------
    // Blaster ballistics measurement
    //
    // Pure observation of snapshots the driver already reads. It changes no
    // input and is not consulted by any decision: it exists to test the
    // `18 / slant` crossing-speed law against the run's own hits and misses.
    // ------------------------------------------------------------------

    /// <summary>One <c>Blaster</c> aimed at the player, from launch to expiry.</summary>
    internal readonly record struct ObservedBlaster(
        int LaunchTick,
        double LaunchSlantMeters,
        double PerpendicularSpeedMetersPerSecond,
        double ClosestApproachMillimeters,
        int LifeTicks,
        int FinalRemainingBaseTicks);

    private sealed class TrackedBlaster
    {
        public int LaunchTick;
        public double LaunchSlantMeters;
        public double PerpendicularSpeed;
        public double Closest = double.MaxValue;
        public SimVector3 Previous;
        public bool HasPrevious;
        public int LastSeenTick;
        public int FinalRemainingBaseTicks;
    }

    private readonly Dictionary<int, TrackedBlaster> _liveBlasters = [];
    private readonly List<ObservedBlaster> _blasters = [];
    private SimVector3 _previousPlayerPoint;
    private bool _hasPreviousPlayerPoint;

    internal IReadOnlyList<ObservedBlaster> Blasters => _blasters;

    private readonly List<(int Tick, int Delta)> _hullDrops = [];
    private int _previousHull = int.MinValue;

    /// <summary>Every hull decrease this run saw, with the tick it landed on.</summary>
    internal IReadOnlyList<(int Tick, int Delta)> HullDrops => _hullDrops;

    private void RecordBlasterBallistics(WorldSnapshot state)
    {
        if (_previousHull != int.MinValue && state.Hull < _previousHull)
        {
            _hullDrops.Add((state.Tick, _previousHull - state.Hull));
        }

        _previousHull = state.Hull;

        Level100ActorSnapshot? player = state.Level100Actors.Actors
            .FirstOrDefault(actor => actor.Name == "Player 1");
        if (player is null)
        {
            return;
        }

        var playerPoint = new SimVector3(
            state.PlayerPosition.X,
            state.PlayerElevationMillimeters,
            state.PlayerPosition.Z);
        double velocityX = 0;
        double velocityY = 0;
        double velocityZ = 0;
        if (_hasPreviousPlayerPoint)
        {
            velocityX = (double)playerPoint.X - _previousPlayerPoint.X;
            velocityY = (double)playerPoint.Y - _previousPlayerPoint.Y;
            velocityZ = (double)playerPoint.Z - _previousPlayerPoint.Z;
        }

        _previousPlayerPoint = playerPoint;
        _hasPreviousPlayerPoint = true;

        var seen = new HashSet<int>();
        foreach (Level100ActorRoundSnapshot round in
                 state.Level100ActorMechanics.ActorRounds)
        {
            if (round.Kind != Level100ActorRoundKind.Blaster ||
                round.TargetActorId != player.ActorId)
            {
                continue;
            }

            seen.Add(round.Id);
            double yaw = round.YawMicroRadians / 1_000_000d;
            double pitch = round.PitchMicroRadians / 1_000_000d;
            double directionX = -Math.Sin(yaw) * Math.Cos(pitch);
            double directionY = Math.Sin(pitch);
            double directionZ = Math.Cos(yaw) * Math.Cos(pitch);

            if (!_liveBlasters.TryGetValue(round.Id, out TrackedBlaster? tracked))
            {
                // The muzzle is the owning drone: the round has already taken
                // one base-tick step by the time this snapshot is published.
                Level100ActorSnapshot owner = state.Level100Actors.Actors
                    .First(actor => actor.ActorId == round.OwnerActorId);
                SimVector3 muzzle = owner.Pose.PositionMillimeters;
                double slantX = (double)playerPoint.X - muzzle.X;
                double slantY = (double)playerPoint.Y - muzzle.Y;
                double slantZ = (double)playerPoint.Z - muzzle.Z;

                double along = (velocityX * directionX) +
                    (velocityY * directionY) +
                    (velocityZ * directionZ);
                double perpX = velocityX - (along * directionX);
                double perpY = velocityY - (along * directionY);
                double perpZ = velocityZ - (along * directionZ);
                double perpendicular = Math.Sqrt(
                    (perpX * perpX) + (perpY * perpY) + (perpZ * perpZ));

                tracked = new TrackedBlaster
                {
                    LaunchTick = state.Tick,
                    LaunchSlantMeters = Math.Sqrt(
                        (slantX * slantX) + (slantY * slantY) + (slantZ * slantZ)) / 1_000d,
                    PerpendicularSpeed =
                        perpendicular * SimulationConstants.TicksPerSecond / 1_000d,
                };
                _liveBlasters[round.Id] = tracked;
            }

            tracked.LastSeenTick = state.Tick;
            tracked.FinalRemainingBaseTicks = round.RemainingBaseTicks;

            // The engine's own test, forward-looking. `AdvanceLevel100ActorMechanics`
            // runs BEFORE `UpdateMovement`, so the segment it sweeps next is
            // [this snapshot's round position, +one base-tick step] against THIS
            // snapshot's player pose. Reconstructing it backwards from
            // consecutive snapshots misses the fatal segment entirely, because a
            // round that impacts is removed inside the step that killed it.
            const double BlasterStepMillimeters =
                (double)SimulationConstants.Level100BlasterSpeedMillimetersPerSecond /
                Level100ActorMechanics.RetailBaseTicksPerSecond;
            var swept = new SimVector3(
                (int)(round.PositionMillimeters.X + (directionX * BlasterStepMillimeters)),
                (int)(round.PositionMillimeters.Y + (directionY * BlasterStepMillimeters)),
                (int)(round.PositionMillimeters.Z + (directionZ * BlasterStepMillimeters)));
            tracked.Closest = Math.Min(
                tracked.Closest,
                PointToSegmentMillimeters(
                    playerPoint, round.PositionMillimeters, swept));
            tracked.Previous = round.PositionMillimeters;
            tracked.HasPrevious = true;
        }

        foreach (int id in _liveBlasters.Keys.ToArray())
        {
            if (seen.Contains(id))
            {
                continue;
            }

            TrackedBlaster finished = _liveBlasters[id];
            _liveBlasters.Remove(id);
            _blasters.Add(new ObservedBlaster(
                finished.LaunchTick,
                finished.LaunchSlantMeters,
                finished.PerpendicularSpeed,
                finished.Closest,
                finished.LastSeenTick - finished.LaunchTick,
                finished.FinalRemainingBaseTicks));
        }
    }

    private static double Distance(SimVector3 a, SimVector3 b)
    {
        double deltaX = (double)a.X - b.X;
        double deltaY = (double)a.Y - b.Y;
        double deltaZ = (double)a.Z - b.Z;
        return Math.Sqrt((deltaX * deltaX) + (deltaY * deltaY) + (deltaZ * deltaZ));
    }

    private static double PointToSegmentMillimeters(
        SimVector3 point,
        SimVector3 start,
        SimVector3 end)
    {
        double segmentX = (double)end.X - start.X;
        double segmentY = (double)end.Y - start.Y;
        double segmentZ = (double)end.Z - start.Z;
        double lengthSquared =
            (segmentX * segmentX) + (segmentY * segmentY) + (segmentZ * segmentZ);
        if (lengthSquared < 1.0)
        {
            return Distance(point, start);
        }

        double toX = (double)point.X - start.X;
        double toY = (double)point.Y - start.Y;
        double toZ = (double)point.Z - start.Z;
        double projection = Math.Clamp(
            ((toX * segmentX) + (toY * segmentY) + (toZ * segmentZ)) / lengthSquared,
            0,
            1);
        double offsetX = toX - (projection * segmentX);
        double offsetY = toY - (projection * segmentY);
        double offsetZ = toZ - (projection * segmentZ);
        return Math.Sqrt(
            (offsetX * offsetX) + (offsetY * offsetY) + (offsetZ * offsetZ));
    }

    private void Observe(WorldSnapshot state)
    {
        RecordPlayerWeaponFire(state);
        RecordArmamentEvidence(state);
        RecordBlasterBallistics(state);
        RecordWaveTwoDamage(state);
        if (state.PlayerOnGround && !state.PlayerInWater)
        {
            _lastDryGround = state.PlayerPosition;
        }
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
            _log.Add(
                $"t{state.Tick} OUTCOME {state.Level100Mission.Outcome} " +
                $"reason={state.Level100Mission.FailureReason} " +
                $"hull={state.Hull} mode={state.Mode} " +
                $"pos=({state.PlayerPosition.X},{state.PlayerPosition.Z}) " +
                $"y={state.PlayerElevationMillimeters} water={state.PlayerInWater}");
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
        if (target.TargetGroup == Level100MissionTargetGroup.AirborneTargets2)
        {
            return EngageWaveTwo(state, target);
        }

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
        // ...but not when the watchdog above has just said the target's health
        // is not moving. Cancelling the reposition on `precise` alone made the
        // precision branch outrank the only check that can see a stance which
        // cannot work: measured, the driver stood at (23608, 69303) with a
        // clear ray, a converged yaw and a live Target Tank for 34,000 ticks
        // because every reposition the watchdog asked for was cancelled on the
        // same tick it was requested.
        if (precise && clear && horizontal <= GroundStandOffMillimeters && !notHurtingIt)
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
                // Standing on top of it is its own failure mode, and it is not
                // fixed by walking round. AimPoint's ladder is bounded in
                // ANGLE, so at the minimum stand-off it collapses to its 100 mm
                // floor and the whole ladder can sit below the terrain the ray
                // is sampled against: measured against Target Warehouse, whose
                // authored origin is 0.6 m below the ground the walker stands
                // on (buildings are not ground-seated - see the open list in
                // local-lab/INDEX.md), every rung of the ladder was under
                // ground + LineOfSightClearanceMillimeters, so `clear` was
                // false at every point on a 3.3 m orbit and the driver circled
                // for 34,000 ticks. Backing out restores the ladder's reach.
                if (horizontal <= MinimumGroundStandOffMillimeters)
                {
                    forward = -1;
                }

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

    /// <summary>How long one crab is held before it is reversed.</summary>
    private const int JetStrafeSegmentTicks = 150;

    /// <summary>
    /// The altitude band the crabbed jet is flown in. The floor keeps the nose
    /// out of the released ground effect; the ceiling exists because a crabbing
    /// jet sheds a vertical rate only through thrust.
    /// </summary>
    private const int WaveTwoFloorMillimeters = 9_000;

    private const int WaveTwoCeilingMillimeters = 26_000;

    /// <summary>
    /// Slant range beyond which reversing the crab is free. This is the shipped
    /// <c>Drone Vulcan Cannon</c> <c>CWeaponMaxRange</c> of 40.0 plus a margin
    /// for the closure that happens while the new crab builds.
    /// </summary>
    private const int WaveTwoSafeReversalMillimeters = 55_000;

    /// <summary>
    /// Clearance a landing site needs above the released water plane.
    /// <c>Simulation.UpdateWalkerGroundContact</c> declares the player in water
    /// when the sampled ground is at or below
    /// <c>Level100Terrain.WaterElevationMillimeters</c>, so this is a small
    /// margin on that test and not an invented shoreline. Measured: a 2 m
    /// margin classified the beat-9 charging position itself - sampled ground
    /// -598 mm against a -1160 mm water plane - as sea, and the driver spent
    /// the whole beat climbing "home" to where it already was.
    /// </summary>
    private const int DryGroundClearanceMillimeters = 300;

    /// <summary>Is the terrain under this point below the water plane?</summary>
    private bool OverWater(SimVector2 position) =>
        _terrain.SampleGroundElevationMillimeters(position) <
            Level100Terrain.WaterElevationMillimeters + DryGroundClearanceMillimeters;

    /// <summary>
    /// The released 3D centre distance, which is what every shipped range gate
    /// on this fight actually tests.
    /// </summary>
    private static double SlantRange(WorldSnapshot state, SimVector3 position)
    {
        double deltaX = (double)position.X - state.PlayerPosition.X;
        double deltaY = (double)position.Y - state.PlayerElevationMillimeters;
        double deltaZ = (double)position.Z - state.PlayerPosition.Z;
        return Math.Sqrt((deltaX * deltaX) + (deltaY * deltaY) + (deltaZ * deltaZ));
    }

    /// <summary>
    /// Beat 9's wave, which is a different fight from beat 7's and is driven
    /// separately for that reason.
    ///
    /// <para><b>Wave 1 does not shoot back.</b> <c>AirborneDrone1.msl</c> flies
    /// a route; <c>AirborneDrone2.msl</c>'s <c>init()</c> issues
    /// <c>Attack(player)</c> at line 26 and the six spawns carry a
    /// <c>Drone Vulcan Cannon</c> and a <c>Forseti Drone Missile Launcher</c>
    /// each. So beat 7 is a gunnery exercise and beat 9 is a dogfight, and the
    /// beat-7 driver above is deliberately left exactly as measured rather than
    /// generalised over both.</para>
    ///
    /// <para><b>What the shipped weapon records say the fight is.</b></para>
    /// <list type="bullet">
    ///   <item><description><c>Drone Vulcan Cannon</c>: <c>CWeaponMaxRange</c>
    ///   40.0, burst 8 at 0.15 s, reload 1.0 s, round <c>Blaster</c> at
    ///   <c>CRoundVelocity</c> 45.0 for <b>200 hull</b> a hit. Six drones is
    ///   48 rounds a second, or 9,600 hull a second if they all
    ///   land.</description></item>
    ///   <item><description><c>Forseti Drone Missile Launcher</c>:
    ///   <c>CWeaponMinRange</c> 20.0, <c>CWeaponMaxRange</c> 80.0, reload
    ///   <b>10.0 s</b>, round <c>Forseti Missile</c> at 15.0 for <b>2,500
    ///   hull</b>. Slow and rare, and it cannot fire inside 20 m at
    ///   all.</description></item>
    /// </list>
    ///
    /// <para><b>The Vulcan is the whole threat, and it is beaten by moving.</b>
    /// Neither drone weapon mode carries <c>CWeaponTrack</c> and neither
    /// carries a lead law, so <c>LaunchActorRound</c> aims every Blaster at the
    /// player's position on the tick it is fired. The impact envelope is the
    /// battle engine's own 0.4 m radius (<c>CBattleEngine::GetRadius</c>). A
    /// Blaster fired from 30 m is in flight for 0.67 s, so it needs the player
    /// to cross less than 0.4 m in that time: <b>a perpendicular speed above
    /// about 0.6 m/s makes it a clean miss</b>. Flying straight at a drone is
    /// the one manoeuvre that supplies less than that, and it is what the
    /// previous revision did - measured, it lost 8,800 hull in 2.4 released
    /// seconds between t9958 and t10030 and reached the sub-40 % abort with
    /// two of six drones down.</para>
    ///
    /// <para>So this driver holds <see cref="SimInput.MoveX"/> throughout.
    /// That is <c>TUTORIAL_STRAFE</c>, which the LevelScript plays at the head
    /// of <c>event("Reached Target Zone 3")</c> immediately before this wave,
    /// and it is worth more than the lateral acceleration alone:
    /// <c>Simulation.UpdateJetMovement</c> refreshes
    /// <c>_jetStrafeTicksRemaining</c> on every strafing tick and
    /// <c>Simulation.JetAlignmentPermille</c> returns <b>0</b> for as long as
    /// that window is open, so the released velocity-to-forward alignment stops
    /// pulling the flight path back onto the nose and the airframe holds a
    /// standing crab. The reticle does not move; the aeroplane does.</para>
    ///
    /// <para><b>Standing off was the obvious next move and it was measured and
    /// rejected.</b> The <c>18 / slant</c> requirement falls as range grows, so
    /// fighting at 15-20 m rather than 4-8 m should be nearly free - and on the
    /// Blaster axis it is. See
    /// <see cref="Level100FullChainTests.BlasterMissLaw_SeparatesTheRunsOwnHitsFromItsMisses"/>
    /// for the law itself. Two stand-off disciplines were flown, both holding a
    /// band by putting the nearest drone off the nose while inside the floor
    /// and re-attacking past the ceiling:</para>
    ///
    /// <list type="table">
    ///   <item><description>11-19 m band, 90 degrees off: Blaster damage fell
    ///   from 7,600 hull to <b>200</b> - one hit in the whole beat, exactly what
    ///   the law predicts - but <c>Forseti</c> hits rose from two to <b>seven</b>
    ///   and the run finished with <b>zero</b> kills at 2,500
    ///   hull.</description></item>
    ///   <item><description>10-16 m band, 60 degrees off, to stop the airframe
    ///   overshooting into missile range: 26 Blaster hits and three Forseti,
    ///   7,300 hull - the same total as this driver - and again <b>zero</b>
    ///   kills.</description></item>
    /// </list>
    ///
    /// <para>Both fail for the same two shipped reasons. First, the
    /// <c>Forseti Drone Missile Launcher</c> carries <c>CWeaponMinRange</c>
    /// 20.0 and <c>CanActorWeaponFire</c> rejects the shot below it, so knife
    /// range is the only place in the level where the 2,500-hull weapon cannot
    /// fire at all: hull saved from the 200-hull Blaster is handed back at
    /// 12.5 times the price. Second, and decisively, the Aquila cannot hover -
    /// the released speed correction floors the magnitude at
    /// <c>JetMinimumSpeedPerTick</c> even at <c>MoveZ</c> -1 - so a range band
    /// is held only by pointing the nose away from the target, and the time
    /// spent doing that is the same time the driver needs to hold a drone on
    /// the reticle. The stand-off does not resolve the track-or-dodge conflict;
    /// it renames it.</para>
    /// </summary>
    private SimInput EngageWaveTwo(WorldSnapshot state, Level100ActorSnapshot target)
    {
        if (state.Transition != VehicleTransition.None)
        {
            return SimInput.Idle;
        }

        SimVector3 aim = WaveTwoAimPoint(state, target);
        double horizontal = Horizontal(state, aim);
        double slant = SlantRange(state, aim);
        double yawError = YawErrorTo(state, aim.X, aim.Z);
        short lookX = LookAxis(yawError, 2_000);
        int altitude = state.PlayerAltitudeAboveGroundMillimeters;

        if (state.Mode != VehicleMode.Jet)
        {
            if (state.Energy < SortieLaunchEnergy)
            {
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

        // Never fight, and above all never come down, over the sea. The
        // released water path loses the level at full hull, and a drone that
        // has drifted out over the water is not worth following. The recovery
        // heading is the last place the player actually stood.
        bool overWater = OverWater(state.PlayerPosition);
        if (overWater)
        {
            yawError = YawErrorTo(state, _lastDryGround.X, _lastDryGround.Z);
            lookX = LookAxis(yawError, 2_000);
        }

        // Altitude, and this is the price of the crab. While MoveX is held
        // `JetAlignmentPermille` is 0, so the released alignment never pulls
        // the velocity back onto the nose - which is the point - but it also
        // means a vertical rate, once acquired, is not shed by anything except
        // thrust pointed the other way. Measured with the beat-7 driver's
        // "climb whenever below 9 m" rule and a held strafe: the jet wound
        // itself up to 57 m, ran the store dry there, dropped to walker and
        // fell out of the sky with all six drones untouched.
        //
        // So the crab is flown with an explicit altitude band and a rate term
        // instead.
        //
        // The correction is a BIAS ON THE AIM PITCH, not an alternative to it,
        // and the rate term is on whether or not the band is broken. The
        // earlier revision only corrected while outside the band and handed the
        // pitch axis back to the target inside it. That does not hold a band:
        // with the alignment at 0 the vertical velocity is a free integrator,
        // so the band was left at whatever rate the last tracking excursion had
        // built and the correction only ever fought the overshoot. Measured
        // with the constant applied and that controller: the jet climbed to
        // 31.1 m against a 26 m ceiling and spent the rest of the beat looking
        // down at drones from above, firing on 363 of 2,503 ticks.
        //
        // A rate term added to the aim pitch vanishes at steady state, so it
        // costs nothing once the vertical rate is dead - unlike an alternative
        // pitch command, which is off-target for as long as it is in charge.
        double aimPitch = -Math.Atan2(
            aim.Y - state.PlayerElevationMillimeters,
            Math.Max(1.0, horizontal));
        double bandBias = 0;
        if (altitude < WaveTwoFloorMillimeters)
        {
            bandBias = (altitude - WaveTwoFloorMillimeters) / 40_000d;
        }
        else if (altitude > WaveTwoCeilingMillimeters)
        {
            bandBias = (altitude - WaveTwoCeilingMillimeters) / 40_000d;
        }

        double verticalCorrection = Math.Clamp(
            bandBias + (state.PlayerVerticalVelocityMillimetersPerTick / 400d),
            -0.35,
            0.35);
        double commandedPitch = aimPitch + verticalCorrection;
        double altitudePitchError =
            commandedPitch - (state.FacingPitchMicroRad / 1_000_000d);

        // Both airborne axes are RATE commands from here down. See
        // `RateCommand`: on the ground the released input gain is speed
        // scheduled and the inversion below does not hold, which is why the
        // walker branch above still uses the proportional law.
        short lookYAltitude = RateCommand(
            WaveTwoPitchLambda * altitudePitchError * 1_000_000d,
            state.WalkerPitchVelocityMicroRadPerTick,
            SimulationConstants.JetPitchInputMicroRadPerTick);
        lookX = RateCommand(
            WaveTwoYawLambda * yawError * 1_000_000d,
            state.WalkerYawVelocityMicroRadPerTick,
            SimulationConstants.JetYawInputMicroRadPerTick);

        // Missile defence, and it is the larger half of this fight. Recorded
        // hull losses across the previous revision's beat 9 came in steps of
        // 2,500 and 2,900 - that is `Forseti Missile` (2.0 round + 0.5
        // explosion = 2,500 hull) with the odd 200-hull Blaster on top, not a
        // Blaster stream. Six launchers on a 10 s reload put roughly eighteen
        // of those in the air across the beat, and three landing is the whole
        // budget between 17,500 and the sub-40 % abort at 8,000.
        //
        // The released seeker is beatable and the shipped record says exactly
        // how. Round vtable slot 66 takes the direction to the target into the
        // round's own frame and, with `CRoundWeirdoSeek` 0, **clears the target
        // reader outright** when the forward component falls below
        // cos(`CRoundSeekAngle`) - 45 degrees. `CRoundSeek 3` never
        // re-acquires (`== 1` at
        // `CRound__SelectBestTargetReaderAndSyncAimState` is the only
        // self-acquire path in the image), so a dropped lock is dropped for
        // good. `CRoundTurnRate` is 0.04886922 rad per released tick, i.e.
        // 0.977 rad/s, while the jet's own yaw velocity accumulates to
        // `JetYawInputMicroRadPerTick / (1 - JetYawRetention)` = about
        // 1.47 rad/s. **The airframe out-turns the seeker**, so putting the
        // missile on the beam and holding full throttle opens the cone.
        Level100ActorRoundSnapshot? missile = InboundMissile(state);
        if (!overWater && missile is not null)
        {
            double bearing = BearingTo(state, missile.PositionMillimeters);
            double beam = bearing + (_crabDirection * Math.PI / 2);
            double beamError =
                NormalizeRadians(beam - (state.FacingYawMicroRad / 1_000_000d));
            short breakLookX = RateCommand(
                WaveTwoYawLambda * beamError * 1_000_000d,
                state.WalkerYawVelocityMicroRadPerTick,
                SimulationConstants.JetYawInputMicroRadPerTick);

            // The break does not stop the guns. The nose sweeps across the
            // wave while it turns, and a volley taken on the way past costs
            // nothing: SimActions.Fire is gated by FireCooldownTicks and no
            // energy, so a shot that is on the target is free whatever the
            // aeroplane is doing.
            return new SimInput(
                (sbyte)WaveTwoCrab(state),
                1,
                _waveTwoTriggerHeldShut
                    ? SimActions.None
                    : WaveTwoFireGate(
                        state, aim, slant, altitude, yawError, breakLookX, lookYAltitude),
                0,
                0,
                breakLookX,
                lookYAltitude);
        }

        if (!overWater && state.Energy < SortieRecoverEnergy)
        {
            return new SimInput(0, -1, SimActions.ToggleMode, 0, 0, lookX, 0);
        }

        short lookY = lookYAltitude;

        // Throttle. Backing off is what makes this airframe turn: the released
        // speed correction drives it to JetMinimumSpeedPerTick (6 m/s) at
        // MoveZ -1 while the yaw rate stays a fixed
        // JetYawInputMicroRadPerTick, so the turn radius collapses from about
        // 61 m to about 20 m. Measured: a revision that never backed off could
        // not stay on any drone and flew the fight 180 m off station with no
        // kills at all.
        sbyte throttle = horizontal > 60_000 || overWater ? (sbyte)1 : (sbyte)0;
        if (!overWater && (horizontal < 20_000 || Math.Abs(yawError) > 0.7))
        {
            throttle = -1;
        }

        SimActions actions = overWater || _waveTwoTriggerHeldShut
            ? SimActions.None
            : WaveTwoFireGate(state, aim, slant, altitude, yawError, lookX, lookY);
        return new SimInput(
            (sbyte)WaveTwoCrab(state),
            throttle,
            actions,
            0,
            0,
            lookX,
            lookY);
    }

    /// <summary>
    /// The held strafe.
    ///
    /// <para><b>It is never reversed while a drone is inside its Vulcan's
    /// 40 m envelope.</b> The crab takes about five released seconds to build
    /// through the released friction, so a reversal is a window in which the
    /// perpendicular speed passes through zero - and that window is exactly
    /// what the Blaster needs. Measured on a run that reversed every 150 ticks
    /// regardless: hull held flat at 14,200 for a hundred ticks while the crab
    /// was developed, then fell 14,200 to 7,500 across the reversal.</para>
    /// </summary>
    private int WaveTwoCrab(WorldSnapshot state)
    {
        if (state.Tick - _crabSinceTick >= JetStrafeSegmentTicks &&
            NearestWaveTwoSlant(state) > WaveTwoSafeReversalMillimeters)
        {
            _crabSinceTick = state.Tick;
            _crabDirection = -_crabDirection;
        }

        return _crabDirection;
    }

    private int _crabDirection = 1;
    private int _crabSinceTick;


    /// <summary>
    /// Pull the trigger whenever the reticle is genuinely on a drone, whatever
    /// the aeroplane is doing. The `Mech Air Bullet` costs no energy and the
    /// cadence is gated by <c>FireCooldownTicks</c>, so a shot taken while the
    /// nose sweeps past during a missile break is free.
    /// </summary>
    private static SimActions WaveTwoFireGate(
        WorldSnapshot state,
        SimVector3 aim,
        double slant,
        int altitude,
        double targetYawError,
        short lookX,
        short lookY)
    {
        double tolerance = FireTolerance(slant);

        // The gate is tested against the pose the round will ACTUALLY be
        // launched from and along, not the one in the snapshot the driver is
        // reading. `Simulation.Step` runs `UpdateMovement` - and inside it
        // `UpdateJetOrientation` - at line 188, and `TryFire` at line 192, so
        // by the time `LaunchWalkerRound` reads `_facingYawMicroRad` and
        // `PlayerPosition` both have already advanced by this tick's input.
        //
        // Measured on the baseline run: the nose moves up to 0.07 rad in that
        // one tick, which is half of the whole tolerance at 15 m, and the
        // muzzle moves up to 400 mm. Not one of the 76 wave-2 rounds the
        // baseline fired passed within 500 mm of a drone measured on the swept
        // segment, and the median miss was 1,198 mm - a systematic bias, not
        // scatter.
        double muzzleX = state.PlayerPosition.X + state.PlayerVelocity.X;
        double muzzleZ = state.PlayerPosition.Z + state.PlayerVelocity.Z;
        double muzzleY = state.PlayerElevationMillimeters +
            state.PlayerVerticalVelocityMillimetersPerTick +
            SimulationConstants.PulseCannonEmitterUpMillimeters;
        double deltaX = (double)aim.X - muzzleX;
        double deltaY = (double)aim.Y - muzzleY;
        double deltaZ = (double)aim.Z - muzzleZ;
        double horizontal = Math.Max(
            1.0, Math.Sqrt((deltaX * deltaX) + (deltaZ * deltaZ)));

        double yawError = NormalizeRadians(
            Math.Atan2(-deltaX, deltaZ) -
            PredictedAngle(
                state.FacingYawMicroRad,
                state.WalkerYawVelocityMicroRadPerTick,
                lookX,
                SimulationConstants.JetYawInputMicroRadPerTick));
        double pitchError = -Math.Atan2(deltaY, horizontal) -
            PredictedAngle(
                state.FacingPitchMicroRad,
                state.WalkerPitchVelocityMicroRadPerTick,
                lookY,
                SimulationConstants.JetPitchInputMicroRadPerTick);

        return altitude >= 6_000 &&
            slant is > 800 and < 55_000 &&
            Math.Abs(yawError) < tolerance &&
            Math.Abs(pitchError) < tolerance
                ? SimActions.Fire
                : SimActions.None;
    }

    /// <summary>
    /// The released jet attitude plant, written from the two constants that
    /// produce it in <c>Simulation.UpdateJetOrientation</c>:
    /// <c>velocity(t+1) = RETAIN * velocity(t) + fullScale * response</c>,
    /// then <c>angle(t+1) = angle(t) + velocity(t+1)</c>.
    /// </summary>
    private const double AttitudeRetain =
        (double)SimulationConstants.WalkerYawRetentionNumerator /
        SimulationConstants.WalkerYawRetentionDenominator;

    /// <summary>
    /// Fraction of the remaining yaw error the controller asks the airframe to
    /// remove per tick.
    ///
    /// <para>With <see cref="RateCommand"/> inverting the lag this is a
    /// first-order closed-loop pole rather than a gain: against a stationary
    /// reference the error decays as <c>(1 - lambda)</c> per tick for as long
    /// as the airframe has the authority, and saturates into a bang-bang slew
    /// when it does not. That is why it can be near unity at all - the old
    /// proportional law had to stay slow because it had no braking term.</para>
    ///
    /// <para>Swept against the whole chain at pitch lambda 0.30, wave-2 kills:
    /// 0.20 -&gt; 0, 0.30 -&gt; 1, 0.45 -&gt; 2, 0.60 -&gt; 2, 0.80 -&gt; 6,
    /// 0.85 -&gt; 6, 0.90 -&gt; 6, 0.95 -&gt; 3. A three-point plateau, not a
    /// spike.</para>
    /// </summary>
    private const double WaveTwoYawLambda = 0.90;

    /// <summary>
    /// The same pole on the pitch axis, and it is deliberately a third of the
    /// yaw one.
    ///
    /// <para>Two reasons, both measurable. The released pitch authority is
    /// <c>WalkerPitchInputMicroRadPerTick</c> 3,938 against
    /// <c>JetYawInputMicroRadPerTick</c> 9,805 - a ratio of 2.49 - so the same
    /// pole asks the pitch axis for a rate it more often cannot deliver.
    /// And the pitch REFERENCE is not a clean bearing: it is the aim pitch
    /// plus <c>verticalCorrection</c>, which already carries a derivative term
    /// in the airframe's own vertical velocity. Closing a fast loop around a
    /// reference that contains a rate term of the same loop is the classic
    /// destabilising case.</para>
    ///
    /// <para>Measured at yaw lambda 0.90, wave-2 kills by pitch lambda:
    /// 0.15 -&gt; 1, 0.20 -&gt; 6, 0.25 -&gt; 3, 0.30 -&gt; 6, 0.35 -&gt; 5,
    /// 0.40 -&gt; 0. Over twenty one-permille perturbations of beat 9, 0.20
    /// and 0.30 are indistinguishable (full clear on 10 and 11 of 20
    /// respectively, never fewer than three kills on either); 0.30 is kept
    /// because it also holds the higher floor on wave-2 spawns damaged.</para>
    /// </summary>
    private const double WaveTwoPitchLambda = 0.30;

    /// <summary>
    /// The stick position that makes the NEXT tick's angular velocity equal
    /// the requested one, given the velocity the airframe already carries.
    ///
    /// <para><b>This is the whole controller change, and it is a frame error
    /// in TIME rather than in space.</b> Core integrates a look axis into an
    /// angular VELOCITY behind a retention pole
    /// (<c>WalkerYawRetentionNumerator</c> 0.861774, so a steady stick reaches
    /// 7.23x its per-tick increment) and only then into an angle. A stick
    /// position is therefore a rate demand with a five-tick lag, not an angle
    /// demand, and a proportional controller on angle error carries no term
    /// that can take an accumulated rate back out again: it can only stop
    /// turning by waiting for the pole. Inverting the recurrence gives that
    /// term for nothing, and every quantity it needs is already in the
    /// snapshot.</para>
    ///
    /// <para><b>Measured, on the committed driver, over the 1,957 ticks of
    /// beat 9.</b> Median absolute yaw error 0.79 rad and upper-quartile
    /// 1.99 rad against a fire tolerance of 0.02-0.15, with roughly three
    /// times the required authority available; a firing solution existed on
    /// 7.3 % of ticks; bank angle reached 69 degrees because the yaw stick was
    /// saturated for most of the beat and <c>Simulation.cs:1255-1259</c> drives
    /// roll from the same axis. None of that is a gain problem - the airframe
    /// was being asked for the right thing in the wrong units.</para>
    ///
    /// <para><b>It is not a Core bypass and it is not privileged state.</b>
    /// <see cref="WorldSnapshot.WalkerYawVelocityMicroRadPerTick"/> and
    /// <see cref="WorldSnapshot.WalkerPitchVelocityMicroRadPerTick"/> are the
    /// same public snapshot fields this driver already reads for altitude, and
    /// the result still goes through <see cref="LookAxisCommand"/> and then
    /// through Core's own <c>LookAxisResponse</c>. What a player has that the
    /// old driver did not is the knowledge that the nose keeps swinging after
    /// the stick is centred.</para>
    ///
    /// <para><b>Airborne only.</b> <c>Simulation.UpdateJetOrientation</c>
    /// scales the axis by a <c>ratePermille</c> that is 1000 only in flight
    /// past the input ramp; on the ground it is speed-scheduled and this
    /// inversion does not hold. The walker branch of
    /// <see cref="EngageWaveTwo"/> is deliberately left on the proportional
    /// law.</para>
    /// </summary>
    private static short RateCommand(
        double desiredMicroRadPerTick,
        int measuredMicroRadPerTick,
        int fullScaleMicroRadPerTick)
    {
        double increment =
            desiredMicroRadPerTick - (AttitudeRetain * measuredMicroRadPerTick);
        int permille = (int)Math.Round(
            increment * 1_000d / fullScaleMicroRadPerTick);
        return LookAxisCommand.ForResponsePermille(
            Math.Clamp(permille, -1_000, 1_000));
    }

    /// <summary>
    /// The attitude the airframe will hold on the tick a look command is
    /// issued, for a command that has already been chosen. The forward half of
    /// the recurrence <see cref="RateCommand"/> inverts.
    /// </summary>
    private static double PredictedAngle(
        int angleMicroRad,
        int velocityMicroRadPerTick,
        short command,
        int fullScaleMicroRadPerTick)
    {
        double velocity = (AttitudeRetain * velocityMicroRadPerTick) +
            (fullScaleMicroRadPerTick * LookAxisResponse.Apply(command) / 1_000d);
        return (angleMicroRad + velocity) / 1_000_000d;
    }

    /// <summary>
    /// Where the reticle goes on a wave-2 drone.
    ///
    /// <para>Three corrections to the shared <see cref="AimPoint"/>, and the
    /// shared one is deliberately left alone because it is exact for the
    /// ground targets of beats 3-5 and moving it would move those beats.</para>
    ///
    /// <list type="number">
    ///   <item><description><b>The muzzle has already moved.</b>
    ///   <c>Simulation.Step</c> runs <c>UpdateMovement</c> before
    ///   <c>TryFire</c>, so the round leaves from the snapshot position plus
    ///   one tick of player velocity - up to 400 mm on this
    ///   airframe.</description></item>
    ///   <item><description><b>So has the drone.</b>
    ///   <c>AdvanceLevel100ActorMechanics</c> is the first thing the same step
    ///   does.</description></item>
    ///   <item><description><b>The lead has to be three-dimensional.</b>
    ///   <see cref="AimPoint"/> leads in the horizontal plane only, which is
    ///   exact for a tank and wrong for a drone that is climbing, and it takes
    ///   the flight time from the horizontal range rather than the slant
    ///   range.</description></item>
    /// </list>
    ///
    /// <para>The round is the jet's <c>Mech Air Bullet</c> at
    /// <c>CRoundVelocity</c> 60.0, not the walker Pulse round's 35.0; the
    /// intercept is solved by three fixed-point iterations because the flight
    /// time depends on the range to the lead point and the lead point depends
    /// on the flight time.</para>
    /// </summary>
    private static SimVector3 WaveTwoAimPoint(
        WorldSnapshot state,
        Level100ActorSnapshot target)
    {
        SimVector3 position = target.Pose.PositionMillimeters;
        SimVector3 velocity = target.Pose.LinearVelocityMillimetersPerTick;

        double muzzleX = state.PlayerPosition.X + state.PlayerVelocity.X;
        double muzzleY = state.PlayerElevationMillimeters +
            state.PlayerVerticalVelocityMillimetersPerTick;
        double muzzleZ = state.PlayerPosition.Z + state.PlayerVelocity.Z;

        double droneX = position.X + velocity.X;
        double droneY = position.Y + velocity.Y;
        double droneZ = position.Z + velocity.Z;

        double flightTicks = 0;
        for (int iteration = 0; iteration < 3; iteration++)
        {
            double deltaX = droneX + (velocity.X * flightTicks) - muzzleX;
            double deltaY = droneY + (velocity.Y * flightTicks) - muzzleY;
            double deltaZ = droneZ + (velocity.Z * flightTicks) - muzzleZ;
            flightTicks = Math.Sqrt(
                (deltaX * deltaX) + (deltaY * deltaY) + (deltaZ * deltaZ)) /
                SimulationConstants.MechAirBulletSpeedPerTick;
        }

        return new SimVector3(
            (int)(droneX + (velocity.X * flightTicks)),
            (int)(droneY + (velocity.Y * flightTicks)),
            (int)(droneZ + (velocity.Z * flightTicks)));
    }

    /// <summary>
    /// Slant range at which a still-locked <c>Forseti Missile</c> is answered.
    /// It is inside <c>CWeaponMaxRange</c> 80.0 on purpose: breaking at the
    /// launch range would leave the driver evading permanently against six
    /// launchers, and the cone only opens when the bearing rate beats
    /// <c>CRoundTurnRate</c>, which needs the missile close.
    /// </summary>
    private const int MissileBreakRangeMillimeters = 22_000;

    // ==================================================================
    // Beat 9: what was measured on the way to clearing it, including the
    // things that did not work. Kept here rather than in a note because the
    // note is not in this repository and these are expensive to re-derive.
    //
    // WHAT THE OLD DRIVER WAS ACTUALLY DOING, from 1,957 ticks of telemetry:
    //   - median |yaw error| 0.79 rad, upper quartile 1.99, against a fire
    //     tolerance of 0.02-0.15. A firing solution existed on 7.3 % of ticks.
    //   - nineteen target switches, ten of them steps of more than two radians
    //     taken at a slant of 4-15 m. At t13605 the driver held 0.046 rad on
    //     drone 40; one tick later it was asked for 2.692 rad on drone 41.
    //     EVERY hull-loss cluster in the trace is one of those slews.
    //   - bank reached 69 degrees, because the yaw stick was saturated for most
    //     of the beat and Simulation.cs:1255-1259 drives roll from that same
    //     axis.
    //   - of 76 rounds fired at wave 2, measured on the swept segment against
    //     the drone origin: closest approach median 1,198 mm, and NOT ONE
    //     inside 500 mm. Two hits in the whole beat.
    //
    // TRIED AND MEASURED WORSE. All of these are single changes against the
    // shipped controller, all confined to this method, all at the same
    // 36,000-tick budget:
    //   - target selection by bearing-weighted cost with a commitment window
    //     (the obvious fix for the slews): 2 kills, 4 spawns damaged, and 0-2
    //     under perturbation. Worse than doing nothing about it.
    //   - line-of-sight-frame crab: choosing MoveX by projecting the ROLLED
    //     body-right axis (the direction Simulation.UpdateJetMovement actually
    //     applies the strafe along) onto the evasion direction. 0-4 kills, and
    //     1 spawn damaged at the unperturbed point. The frame transform is
    //     real and the arithmetic is right; reversing a crab still costs the
    //     five released seconds it takes to rebuild one.
    //   - a two-phase manoeuvre - stop strafing to get the flight path back,
    //     fly a tangent to a 14 m circle, then re-strafe to freeze the path
    //     and track with the nose. This is the manoeuvre the released
    //     mechanism suggests: JetAlignmentPermille is ~0 for 120 ticks after
    //     ANY strafing tick, so a driver that holds MoveX every tick of beat 9
    //     has switched off AlignVelocityToForward - and with the mix at 1000
    //     that call puts the whole velocity on the nose in one tick, i.e. a
    //     3 m turn radius at minimum speed. Measured: 0 kills, 0 spawns
    //     damaged, and the beat ended 700 ticks EARLIER because the hull fell
    //     faster.
    //   - survive-first throttle (hold MoveZ +1 whenever the crossing speed is
    //     under what 18/slant needs): on its own, 2 kills and 5 spawns damaged
    //     and 2.2x the time alive - the best single change other than the
    //     controller - but it loses the level outright on two of five
    //     perturbations, and combined with the rate controller it is worse
    //     than the rate controller alone.
    //   - line-of-sight rate feed-forward added to the rate command: 4-6
    //     kills, never better than without it.
    //   - tightening the wave-2 fire tolerance from 1,100 mm of target to 800:
    //     six kills on five of five NARROW perturbations and three to four on
    //     the wider set. A spike, and not shipped for exactly the reason the
    //     previous 3-kill spike was not.
    //   - deferring the flight-leg landing while the descent path is over
    //     water: inert. The landing that drowns a six-kill run is not
    //     committed in FlyLeg at all - NavigateToZone toggles to walker as
    //     soon as the zone is inside 20 m, and on the Target Zone 4 approach
    //     that happens 28 m up. It is a real defect and it is NOT fixed here,
    //     because the fix is in a method shared with beats 1-8.
    // ==================================================================

    /// <summary>
    /// The nearest still-locked released seeker heading for the player, or
    /// null.
    ///
    /// <para>Reading the round list is the same class of observation this
    /// driver already makes of <c>actor.Health</c>: a player sees the missile
    /// and its smoke trail, not this record. It is input-equivalent, not
    /// perception-equivalent, and the class remarks say so.</para>
    /// </summary>
    private static Level100ActorRoundSnapshot? InboundMissile(WorldSnapshot state)
    {
        Level100ActorSnapshot? player = state.Level100Actors.Actors
            .FirstOrDefault(actor => actor.Name == "Player 1");
        if (player is null)
        {
            return null;
        }

        Level100ActorRoundSnapshot? nearest = null;
        double nearestRange = MissileBreakRangeMillimeters;
        foreach (Level100ActorRoundSnapshot round in
                 state.Level100ActorMechanics.ActorRounds)
        {
            if (round.Kind != Level100ActorRoundKind.ForsetiMissile ||
                !round.Locked ||
                round.TargetActorId != player.ActorId)
            {
                continue;
            }

            double range = SlantRange(state, round.PositionMillimeters);
            if (range < nearestRange)
            {
                nearestRange = range;
                nearest = round;
            }
        }

        return nearest;
    }

    private static double BearingTo(WorldSnapshot state, SimVector3 position) =>
        Math.Atan2(
            -((double)position.X - state.PlayerPosition.X),
            (double)position.Z - state.PlayerPosition.Z);

    /// <summary>
    /// Slant range to the nearest live wave-2 drone, which is the quantity
    /// <c>CUnit__ClassifyTargetRangeBand</c> tests against
    /// <c>CWeaponMaxRange</c> 40.0.
    /// </summary>
    private static double NearestWaveTwoSlant(WorldSnapshot state)
    {
        double nearest = double.MaxValue;
        foreach (Level100ActorSnapshot actor in state.Level100Actors.Actors)
        {
            if (actor.TargetGroup != Level100MissionTargetGroup.AirborneTargets2 ||
                !actor.Active ||
                actor.Lifecycle != Level100ActorLifecycle.Alive)
            {
                continue;
            }

            nearest = Math.Min(nearest, SlantRange(state, actor.Pose.PositionMillimeters));
        }

        return nearest;
    }

    // ------------------------------------------------------------------
    // Geometry a player can see
    // ------------------------------------------------------------------

    /// <summary>
    /// Where on the target the reticle goes. A player sweeps the body rather
    /// than shooting at the pivot; the sweep also covers the unmodelled
    /// difference between an actor's origin and its hull centre.
    /// </summary>
    private SimVector3 AimPoint(
        WorldSnapshot state,
        Level100ActorSnapshot target,
        bool sweep = true,
        int roundSpeedPerTick = SimulationConstants.ProjectileSpeedPerTick)
    {
        SimVector3 position = target.Pose.PositionMillimeters;
        double rawX = (double)position.X - state.PlayerPosition.X;
        double rawZ = (double)position.Z - state.PlayerPosition.Z;
        double range = Math.Sqrt((rawX * rawX) + (rawZ * rawZ));
        double flightTicks = range / roundSpeedPerTick;

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

        int aimX = (int)(position.X +
            (target.Pose.LinearVelocityMillimetersPerTick.X * flightTicks));
        int aimZ = (int)(position.Z +
            (target.Pose.LinearVelocityMillimetersPerTick.Z * flightTicks));

        // The reticle never goes into the dirt. Several released targets carry
        // an authored origin at or below the ground the walker stands on -
        // Target Warehouse's is 0.6 m below it, because buildings are still not
        // ground-seated (open list, local-lab/INDEX.md). The ladder is bounded
        // in ANGLE, so at short range it collapses to its 100 mm floor and
        // every rung of it can sit under
        // ground + LineOfSightClearanceMillimeters, which makes
        // HasLineOfSight false from every stance. Measured: the driver orbited
        // Target Warehouse at 3.3-4.4 m for 34,000 ticks and never fired.
        int groundUnderAim = _terrain.SampleGroundElevationMillimeters(
            new SimVector2(aimX, aimZ));
        int aimY = Math.Max(
            position.Y + aimHeight,
            groundUnderAim + (2 * LineOfSightClearanceMillimeters));

        return new SimVector3(aimX, aimY, aimZ);
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

    /// <summary>
    /// The stick position that turns the airframe at <c>error * gain</c> of its
    /// full rate.
    ///
    /// <para><b>The gain is a rate gain, not a stick gain, and the distinction
    /// became load-bearing when Core stopped being linear.</b> Every call site
    /// below chooses its gain by asking how fast the nose should sweep for a
    /// given aim error - 2,000 per radian in yaw, 4,000 in pitch, both tuned
    /// against measured convergence. Retail curves the axis
    /// (<c>references/Onslaught/Player.cpp:334-355</c>, ported to
    /// <see cref="LookAxisResponse"/>) and the curve is compressive, so handing
    /// that number straight to <see cref="SimInput"/> asks for a rate and gets
    /// 0.4665 of it near centre. <see cref="LookAxisCommand"/> converts the
    /// rate into the deflection that produces it, which is what a player's hand
    /// does; Core still applies the curve to the result.</para>
    ///
    /// <para>Measured without it, on the run this file exists to produce: the
    /// beat-3 precision shot at <c>Target Tank #23</c> stopped converging, a
    /// Pulse round destroyed the still-unactivated <c>Target Truck #25</c>
    /// 1.46 m behind it at t4240 - thirty ticks before the tank died rather
    /// than thirty-six after, which is the whole difference - and the run ended
    /// at t4281 when <c>event("Activate Static Targets 2")</c> ran
    /// <c>SetObjective()</c> on a destroyed actor.</para>
    /// </summary>
    private static short LookAxis(double error, double gain) =>
        LookAxisCommand.ForResponsePermille((int)(error * gain));

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
