// SPDX-License-Identifier: GPL-3.0-or-later

namespace OnslaughtRebuild.Core;

public enum Level100ActorCommandIntent
{
    Stopped = 0,
    FollowingWaypoint = 1,
    Attacking = 2,
    Retreating = 3,
}

public sealed record Level100ActorCommandIntentSnapshot(
    Level100ActorId ActorId,
    int AiState,
    int Allegiance,
    bool HasAllegianceOverride,
    Level100ActorCommandIntent Intent,
    Level100ActorId? TargetActorId,
    string? WaypointPath,
    // How far along the path's AUTHORED TRAVERSAL CHAIN the follower is - an
    // index into Level100WaypointPathDefinition.TargetChainNodeIndices, NOT
    // into Points. The two orders differ on six of the eight Level 100 paths.
    // Resolve it with Level100WaypointPathDefinition.ChainPoint.
    int WaypointPointIndex,
    int WaypointCommandScalar,
    bool WaitForWaypointCompletion,
    int GroundFullGuideBaseTickPhase);

public sealed record Level100ActorMechanicsSnapshot(
    long LastConsumedCommandSequence,
    IReadOnlyList<Level100ActorCommandIntentSnapshot> Actors,
    int ReleasedRandomSeed,
    int NextActorRoundId,
    IReadOnlyList<Level100ActorWeaponSnapshot> ActorWeapons,
    IReadOnlyList<Level100ActorRoundSnapshot> ActorRounds);

public sealed record Level100ActorMechanicsWaitCompletion(
    Level100ActorId ActorId,
    Level100ActorScriptWaitKind WaitKind,
    string Argument);

/// <summary>
/// Canonical consumer for the released Level 100 actor-script mechanics
/// commands. It implements only the evidenced CGroundVehicle guide cadence,
/// normal speed, heading bound, and terrain grounding. Actor identity and the
/// full physical pose remain exclusively in
/// <see cref="Level100ActorRegistry"/>.
/// </summary>
/// <remarks>
/// This class used to carry a 20-of-every-30 accumulator, because the released
/// base frame is 20 Hz and Core ran at 30. Core now runs at 20 Hz, so every
/// Core tick IS a released base tick, the accumulator was the identity, and it
/// has been deleted along with its serialized-and-hashed snapshot field and the
/// <c>ClearSkippedCoreTickVelocities</c> pass that only existed to zero the
/// reported velocity on the Core ticks that were not base ticks. That pass made
/// a plane's reported <c>LinearVelocityMillimetersPerTick</c> alternate between
/// the base-tick step and zero, which any interpolating renderer saw as a
/// stutter; the stutter is gone with it.
/// </remarks>
public sealed partial class Level100ActorMechanics
{
    /// <summary>
    /// The released base-frame rate, <c>GAME_FR</c>
    /// (<c>references/Onslaught/thing.h:28</c>). Core runs at this rate, so it
    /// equals <see cref="SimulationConstants.TicksPerSecond"/> - but the two
    /// are not the same fact, and the divisions that turn authored
    /// per-second retail data into per-tick data are stated against this one.
    /// </summary>
    public const int RetailBaseTicksPerSecond =
        SimulationConstants.RetailTicksPerSecond;

    private const int FixedTrigScale = 1 << 30;
    private const int HalfPiMicroRad = 1_570_796;
    private const int PiMicroRad = 3_141_593;
    private const int TwoPiMicroRad = PiMicroRad * 2;
    private const int CordicGainQ30 = 652_032_874;

    private static ReadOnlySpan<int> CordicAnglesMicroRad =>
    [
        785_398, 463_648, 244_979, 124_355, 62_419, 31_240, 15_624,
        7_812, 3_906, 1_953, 977, 488, 244, 122, 61, 31, 15, 8, 4, 2, 1,
    ];

    private sealed class ActorState
    {
        internal required Level100ActorId ActorId { get; init; }
        internal int AiState { get; set; }
        internal int Allegiance { get; set; }
        internal bool HasAllegianceOverride { get; set; }
        internal Level100ActorCommandIntent Intent { get; set; }
        internal Level100ActorId? TargetActorId { get; set; }
        internal string? WaypointPath { get; set; }
        internal int WaypointPointIndex { get; set; }
        internal int WaypointCommandScalar { get; set; }
        internal bool WaitForWaypointCompletion { get; set; }
        internal int GroundFullGuideBaseTickPhase { get; set; }
    }

    private readonly Level100ActorRegistry _actors;
    private readonly Level100ActorDefinitionSet _definitions;
    private readonly SortedDictionary<int, ActorState> _states = [];
    private long _lastConsumedCommandSequence;

    public Level100ActorMechanics(
        Level100ActorRegistry actors,
        Level100ActorDefinitionSet definitions)
    {
        _actors = actors ?? throw new ArgumentNullException(nameof(actors));
        _definitions = definitions ?? throw new ArgumentNullException(nameof(definitions));
        ValidateDefinitionIdentity();
    }

    public Level100ActorMechanics(
        Level100ActorRegistry actors,
        Level100ActorDefinitionSet definitions,
        Level100ActorMechanicsSnapshot snapshot)
        : this(actors, definitions)
    {
        ArgumentNullException.ThrowIfNull(snapshot);
        ArgumentNullException.ThrowIfNull(snapshot.Actors);
        ArgumentNullException.ThrowIfNull(snapshot.ActorWeapons);
        ArgumentNullException.ThrowIfNull(snapshot.ActorRounds);
        if (snapshot.LastConsumedCommandSequence < 0 ||
            snapshot.Actors.Any(item => item is null))
        {
            throw new ArgumentException(
                "Level 100 actor mechanics snapshot is invalid.",
                nameof(snapshot));
        }

        _lastConsumedCommandSequence = snapshot.LastConsumedCommandSequence;
        foreach (Level100ActorCommandIntentSnapshot source in snapshot.Actors)
        {
            ValidateSnapshotState(source, snapshot);
            if (!_states.TryAdd(source.ActorId.Value, Restore(source)))
            {
                throw new ArgumentException(
                    "Level 100 actor mechanics snapshot has duplicate actors.",
                    nameof(snapshot));
            }
        }

        RestoreArmament(snapshot);
    }

    public Level100ActorMechanicsSnapshot Snapshot => new(
        _lastConsumedCommandSequence,
        Array.AsReadOnly(_states.Values.Select(SnapshotState).ToArray()),
        _releasedRandom.Seed,
        _nextActorRoundId,
        SnapshotActorWeapons(),
        SnapshotActorRounds());

    private static bool OwnsCommand(Level100ActorScriptCommandKind kind) =>
        kind is
            Level100ActorScriptCommandKind.FollowWaypoint or
            Level100ActorScriptCommandKind.FollowWaypointWait or
            Level100ActorScriptCommandKind.SetAIState or
            Level100ActorScriptCommandKind.SetAllegiance or
            Level100ActorScriptCommandKind.Attack or
            Level100ActorScriptCommandKind.Retreat or
            Level100ActorScriptCommandKind.Stop;

    public void ConsumeCommands(
        IReadOnlyList<Level100ActorScriptCommand> commands)
    {
        ArgumentNullException.ThrowIfNull(commands);
        foreach (Level100ActorScriptCommand command in commands)
        {
            ConsumeCommand(command, requireOwned: false);
        }
    }

    public void ApplyCommand(Level100ActorScriptCommand command) =>
        ConsumeCommand(command, requireOwned: true);

    /// <summary>
    /// One Core tick, which is one released base tick - see the class remarks
    /// for the accumulator this replaced.
    /// </summary>
    public IReadOnlyList<Level100ActorMechanicsWaitCompletion> AdvanceTick() =>
        AdvanceRetailBaseTick();

    private void ConsumeCommand(
        Level100ActorScriptCommand command,
        bool requireOwned)
    {
        ArgumentNullException.ThrowIfNull(command);
        if (command.Sequence <= _lastConsumedCommandSequence)
        {
            throw new InvalidOperationException(
                $"Level 100 actor command sequence {command.Sequence} follows " +
                $"{_lastConsumedCommandSequence}.");
        }

        bool owned = OwnsCommand(command.Kind);
        if (requireOwned && !owned)
        {
            throw new ArgumentOutOfRangeException(
                nameof(command),
                $"Level 100 actor mechanics does not own command {command.Kind}.");
        }

        if (owned)
        {
            switch (command.Kind)
            {
                case Level100ActorScriptCommandKind.FollowWaypoint:
                case Level100ActorScriptCommandKind.FollowWaypointWait:
                    BeginWaypoint(command);
                    break;
                case Level100ActorScriptCommandKind.SetAIState:
                    RequireState(command).AiState = command.Scalar;
                    break;
                case Level100ActorScriptCommandKind.SetAllegiance:
                {
                    ActorState state = RequireState(command);
                    state.Allegiance = command.Scalar;
                    state.HasAllegianceOverride = true;
                    break;
                }
                case Level100ActorScriptCommandKind.Attack:
                    BeginAttack(command);
                    break;
                case Level100ActorScriptCommandKind.Retreat:
                    SetSimpleIntent(command, Level100ActorCommandIntent.Retreating);
                    break;
                case Level100ActorScriptCommandKind.Stop:
                    Stop(command);
                    break;
            }
        }

        _lastConsumedCommandSequence = command.Sequence;
    }

    private IReadOnlyList<Level100ActorMechanicsWaitCompletion>
        AdvanceRetailBaseTick()
    {
        var completions = new List<Level100ActorMechanicsWaitCompletion>();
        foreach (ActorState state in _states.Values)
        {
            Level100ActorSnapshot actor = _actors.GetActor(state.ActorId);
            Level100ActorMotionDefinition? motion =
                _definitions.FindMotionDefinition(actor.DefinitionName);
            if (motion?.MotionClass == Level100ActorMotionClass.Plane)
            {
                if (actor.Active &&
                    actor.Lifecycle == Level100ActorLifecycle.Alive)
                {
                    AdvancePlane(state, motion);
                }
                else
                {
                    ZeroActorVelocity(state.ActorId);
                }
                actor = _actors.GetActor(state.ActorId);
            }

            if (motion?.MotionClass ==
                Level100ActorMotionClass.GroundVehicle)
            {
                if (actor.Active &&
                    actor.Lifecycle ==
                    Level100ActorLifecycle.Alive)
                {
                    bool fullGuideUpdate =
                        state.GroundFullGuideBaseTickPhase == 0;
                    state.GroundFullGuideBaseTickPhase =
                        (state.GroundFullGuideBaseTickPhase + 1) %
                        motion.FullGuideBaseTicks!.Value;
                    if (state.Intent ==
                        Level100ActorCommandIntent.FollowingWaypoint)
                    {
                        AdvanceGroundVehicle(
                            state,
                            motion,
                            fullGuideUpdate);
                    }
                    else
                    {
                        ZeroActorVelocity(state.ActorId);
                    }
                }
                else
                {
                    ZeroActorVelocity(state.ActorId);
                }
                actor = _actors.GetActor(state.ActorId);
            }

            if (state.Intent !=
                    Level100ActorCommandIntent.FollowingWaypoint ||
                motion is null ||
                !actor.Active ||
                actor.Lifecycle != Level100ActorLifecycle.Alive)
            {
                continue;
            }

            ObserveWaypointArrival(state, actor, motion, completions);
        }

        // Released ordering inside one base tick is: things move, then rounds
        // move (CRound vtable slot 66), then weapons that are due spawn new
        // rounds. Advancing live rounds before this tick's launches is what
        // stops a round from travelling on the tick it is created, which is
        // what retail's event-scheduled creation also produces.
        AdvanceActorRounds();
        AdvanceActorWeapons();

        return Array.AsReadOnly(completions.ToArray());
    }

    // ------------------------------------------------------------------
    // Plane (released behaviour class 9, CFighterBehaviourType -> CPlane,
    // vtable 0x005e1930).
    //
    // Decoded read-only from the pristine BEA.exe, sha256
    // 74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750, and
    // written up in local-lab/PLANE-MOTION-AND-ACTOR-WEAPONS-2026-07-26.md.
    // Three released functions own this between them:
    //
    //   CAirGuide::VFunc03            0x00402280  (CAirGuide vtable 0x005d8594
    //                                              slot 3) - produces the
    //                                              desired euler triple at
    //                                              unit+0x120 and writes
    //                                              mVelocity at unit+0x14c.
    //   CUnit__SmoothEulerTowardTargetAndBuildMatrix
    //                                 0x004fa4b0  - turns the current euler
    //                                              (unit+0x114) toward the
    //                                              desired by
    //                                              min(|error| * MM * 0.1,
    //                                                  MM * maxStep), where
    //                                              MM is vtable slot 24 and
    //                                              DAT_005d85c0 = 0.1.
    //   CUnit__UpdateMotionAndTrailEffects
    //                                 0x00402fa0  - sets the three max euler
    //                                              steps to
    //                                              record[+0xb8] * 0.333333
    //                                              (DAT_005d8608), accumulates
    //                                              mVelocity into the move
    //                                              buffer at unit+0x7c, and
    //                                              CLAMPS that buffer's
    //                                              magnitude to
    //                                              GetMaxVelocity() * 0.05
    //                                              (vtable slot 111 @0x1bc,
    //                                              which returns
    //                                              record[+0xb4]).
    //
    // Two consequences decide this reconstruction, and both were reached by
    // refuting an earlier reading of mine:
    //
    // 1. The guide's own `* 4.0` (DAT_005d85bc) is NOT the plane's move
    //    multiplier. CPlane's slot 24 (0x004de700) returns 1.0
    //    (DAT_005d8568); CGroundVehicle's (0x0050e940) returns 4.0. The 4.0 in
    //    the guide is a hardcoded constant that happens to match the ground
    //    class. The plane's actual speed comes from the slot-111 clamp, and
    //    because that clamp is `record[+0xb4] * (1/GAME_FR)` per base tick,
    //    the steady-state ground track is exactly CUnitAirVelocity units per
    //    second. `Level100ActorMechanics` therefore steps a plane at
    //    speed/RetailBaseTicksPerSecond and does not model the buffer.
    //
    // 2. MM = 1.0 means a plane takes a full move on EVERY released base tick,
    //    where a ground vehicle takes one every fourth. That is why a plane
    //    has no FullGuideBaseTicks phase here.
    //
    // Deliberately NOT modelled, because the bytes do not settle them:
    //  - the roll term the guide writes to unit+0x128;
    //  - the +/-60 degree (0x3F860A92) pitch bias the guide takes at
    //    0x004023ea from `guide+0x2c`, because `guide+0x2c` is a
    //    CGenericActiveReader wrapper and its +0x24 is not shown to be the
    //    target's world Z. Read as a world Z its sign contradicts the
    //    clearance branch three instructions later, so one of the two readings
    //    is wrong and nothing here picks between them;
    //  - the near-ground friction (DAT_005d8600 = 0.95) and gravity paths,
    //    which the clamp dominates in level flight.
    private void AdvancePlane(
        ActorState state,
        Level100ActorMotionDefinition motion)
    {
        Level100ActorPoseSnapshot pose = _actors.GetPose(state.ActorId);
        if (!TryGetPlaneGuideTarget(state, out SimVector2 guideTarget))
        {
            _actors.SetPose(
                state.ActorId,
                pose with
                {
                    LinearVelocityMillimetersPerTick = SimVector3.Zero,
                    AngularVelocityMicroRadiansPerTick = SimVector3.Zero,
                });
            return;
        }

        int forwardX = FloatBitsToQ30(pose.BasisFloatBits.Row0Z);
        int forwardY = FloatBitsToQ30(pose.BasisFloatBits.Row1Z);
        int forwardZ = FloatBitsToQ30(pose.BasisFloatBits.Row2Z);
        int horizontal = Q30Hypotenuse(forwardX, forwardZ);
        int currentYaw = FixedAtan2(-forwardX, forwardZ);
        int currentPitch = FixedAtan2(forwardY, horizontal);

        int desiredYaw = PlaneDesiredYaw(pose, guideTarget, currentYaw);
        int desiredPitch = PlaneDesiredPitch(pose);

        int maximumStep = DivideRoundNearest(
            (long)ScalePositiveFloatBits(
                SimulationConstants.Level100PlaneAirTurnRateFloatBits,
                1_000_000),
            3);
        int nextYaw = NormalizeMicroRad(
            currentYaw + PlaneEulerStep(currentYaw, desiredYaw, maximumStep));
        int nextPitch = NormalizeMicroRad(
            currentPitch +
            PlaneEulerStep(currentPitch, desiredPitch, maximumStep));

        int speedPerBaseTick = DivideRoundNearest(
            PlaneAirSpeedMillimetersPerSecond(motion.DefinitionName),
            RetailBaseTicksPerSecond);
        (int yawSin, int yawCos) = FixedSinCos(nextYaw);
        (int pitchSin, int pitchCos) = FixedSinCos(nextPitch);
        var velocity = new SimVector3(
            DivideRoundNearest(
                (long)-MultiplyFixed(yawSin, pitchCos) * speedPerBaseTick,
                FixedTrigScale),
            DivideRoundNearest(
                (long)pitchSin * speedPerBaseTick,
                FixedTrigScale),
            DivideRoundNearest(
                (long)MultiplyFixed(yawCos, pitchCos) * speedPerBaseTick,
                FixedTrigScale));
        var nextPosition = new SimVector3(
            checked(pose.PositionMillimeters.X + velocity.X),
            checked(pose.PositionMillimeters.Y + velocity.Y),
            checked(pose.PositionMillimeters.Z + velocity.Z));
        _actors.SetPose(
            state.ActorId,
            pose with
            {
                PositionMillimeters = nextPosition,
                BasisFloatBits = BuildPlaneBasis(nextYaw, nextPitch),
                LinearVelocityMillimetersPerTick = velocity,
                AngularVelocityMicroRadiansPerTick = new SimVector3(
                    NormalizeMicroRad(nextPitch - currentPitch),
                    NormalizeMicroRad(nextYaw - currentYaw),
                    0),
            });
    }

    /// <summary>
    /// The released air guide steers at whatever <c>guide+0x8..0x10</c> holds:
    /// the current waypoint point while following a path, and the attacked
    /// thing's position while attacking. Only those two are produced by the
    /// Level 100 scripts (<c>AirborneDrone1.msl</c> follows
    /// <c>Drone Path 1</c>; <c>AirborneDrone2.msl</c> and
    /// <c>AirTrainer.msl</c> call <c>Attack(player)</c>).
    /// </summary>
    private bool TryGetPlaneGuideTarget(
        ActorState state,
        out SimVector2 target)
    {
        switch (state.Intent)
        {
            case Level100ActorCommandIntent.FollowingWaypoint
                when state.WaypointPath is not null:
            {
                Level100WaypointPathDefinition path =
                    _definitions.GetWaypointPath(state.WaypointPath);
                Level100WaypointPointDefinition point =
                    path.ChainPoint(state.WaypointPointIndex);
                target = new SimVector2(
                    point.PositionMillimeters.X,
                    point.PositionMillimeters.Z);
                return true;
            }

            case Level100ActorCommandIntent.Attacking
                when state.TargetActorId.HasValue:
            {
                Level100ActorPoseSnapshot targetPose =
                    _actors.GetPose(state.TargetActorId.Value);
                target = new SimVector2(
                    targetPose.PositionMillimeters.X,
                    targetPose.PositionMillimeters.Z);
                return true;
            }

            default:
                target = default;
                return false;
        }
    }

    /// <summary>
    /// Desired yaw toward the guide target, with the released map-edge
    /// turn-back at <c>0x0040246a</c>: a 10.0-unit margin against the
    /// 512.0-unit map (<c>DAT_005d85cc</c> = 10.0, <c>DAT_005d85c4</c> =
    /// 502.0) overrides the target heading outright. The four commanded
    /// headings there are <c>-pi/2</c>, <c>+pi/2</c>, <c>0</c> and <c>pi</c>
    /// in the released retail X/Y frame; they are expressed here as "steer
    /// back toward the interior along the violated axis", which is the same
    /// four headings in Core's X/Z frame without importing the retail axis
    /// convention.
    /// </summary>
    private static int PlaneDesiredYaw(
        Level100ActorPoseSnapshot pose,
        SimVector2 target,
        int currentYaw)
    {
        int margin = SimulationConstants.Level100PlaneMapEdgeMarginMillimeters;
        if (pose.PositionMillimeters.X <
            Level100Terrain.MinimumRelativeXMillimeters + margin)
        {
            return FixedAtan2(-1 << 30, 0);
        }
        if (pose.PositionMillimeters.X >
            Level100Terrain.MaximumRelativeXMillimeters - margin)
        {
            return FixedAtan2(1 << 30, 0);
        }
        if (pose.PositionMillimeters.Z <
            Level100Terrain.MinimumRelativeZMillimeters + margin)
        {
            return 0;
        }
        if (pose.PositionMillimeters.Z >
            Level100Terrain.MaximumRelativeZMillimeters - margin)
        {
            return PiMicroRad;
        }

        long deltaX = (long)target.X - pose.PositionMillimeters.X;
        long deltaZ = (long)target.Z - pose.PositionMillimeters.Z;
        return deltaX == 0 && deltaZ == 0
            ? currentYaw
            : FixedAtan2(-deltaX, deltaZ);
    }

    /// <summary>
    /// The released clearance band at <c>0x0040240d</c>. Retail Z is down and
    /// its commands are <c>-pi/4</c> to climb and <c>+pi/4</c> to dive; Core Y
    /// is up, so the signs are inverted here and only here.
    /// </summary>
    private static int PlaneDesiredPitch(Level100ActorPoseSnapshot pose)
    {
        int clearance = PlaneMinimumGroundClearanceMillimeters(pose);
        int pitch = SimulationConstants.Level100PlaneClearancePitchMicroRadians;
        if (clearance <
            SimulationConstants.Level100PlaneClimbClearanceMillimeters)
        {
            return pitch;
        }
        if (clearance >
            SimulationConstants.Level100PlaneDiveClearanceMillimeters)
        {
            return -pitch;
        }
        return 0;
    }

    /// <summary>
    /// <c>CAirGuide__UpdateGroundClearanceCache</c> (<c>0x004028e0</c>) keeps
    /// the minimum height above terrain over the owner's rounded position
    /// +/-20 released units sampled in steps of 5 - a 41x41 unit box, 81
    /// samples. One released unit is 1000 Core millimetres.
    /// </summary>
    private static int PlaneMinimumGroundClearanceMillimeters(
        Level100ActorPoseSnapshot pose)
    {
        int radius =
            SimulationConstants.Level100PlaneClearanceSampleRadiusMillimeters;
        int step =
            SimulationConstants.Level100PlaneClearanceSampleStepMillimeters;
        int minimum = int.MaxValue;
        for (int offsetZ = -radius; offsetZ <= radius; offsetZ += step)
        {
            for (int offsetX = -radius; offsetX <= radius; offsetX += step)
            {
                int ground =
                    Level100Terrain.Instance.SampleGroundElevationMillimeters(
                        new SimVector2(
                            pose.PositionMillimeters.X + offsetX,
                            pose.PositionMillimeters.Z + offsetZ));
                int clearance = pose.PositionMillimeters.Y - ground;
                if (clearance < minimum)
                {
                    minimum = clearance;
                }
            }
        }
        return minimum;
    }

    /// <summary>
    /// One axis of <c>CUnit__SmoothEulerTowardTargetAndBuildMatrix</c>
    /// (<c>0x004fa4b0</c>): the step is
    /// <c>min(|error| * MM * 0.1, MM * maxStep)</c> where <c>MM</c> is vtable
    /// slot 24 - <b>1.0</b> for CPlane (<c>0x004de700</c>, <c>DAT_005d8568</c>)
    /// against 4.0 for CGroundVehicle - <c>0.1</c> is <c>DAT_005d85c0</c>, and
    /// <c>maxStep</c> is <c>record[+0xb8] * 0.3333333</c>
    /// (<c>DAT_005d8608</c>), written every tick by
    /// <c>CUnit__UpdateMotionAndTrailEffects</c> at <c>0x00402fbf</c>. With
    /// MM = 1 both factors are the identity, so this is exactly
    /// <c>min(|error| / 10, AirTurnRate / 3)</c>.
    /// </summary>
    private static int PlaneEulerStep(int current, int desired, int maximumStep)
    {
        int error = NormalizeMicroRad(desired - current);
        if (error == 0)
        {
            return 0;
        }
        int eased = DivideRoundNearest(Math.Abs((long)error), 10);
        return Math.Sign(error) * Math.Min(eased, maximumStep);
    }

    private static int PlaneAirSpeedMillimetersPerSecond(string definitionName) =>
        definitionName switch
        {
            "Target Drone" =>
                SimulationConstants
                    .Level100TargetDroneAirSpeedMillimetersPerSecond,
            "Air Trainer" =>
                SimulationConstants
                    .Level100AirTrainerAirSpeedMillimetersPerSecond,
            _ => throw new InvalidDataException(
                $"Level 100 plane '{definitionName}' has no released " +
                "CUnitAirVelocity in SimulationConstants."),
        };

    /// <summary>
    /// The rotation whose third column is the released facing axis the guide
    /// multiplies by speed. It matches the ground convention exactly at pitch
    /// zero, so <see cref="FixedAtan2"/> on
    /// <c>(-Row0Z, Row2Z)</c> still reads yaw.
    /// </summary>
    private static Level100FloatBasis3Bits BuildPlaneBasis(int yaw, int pitch)
    {
        (int sinYaw, int cosYaw) = FixedSinCos(yaw);
        (int sinPitch, int cosPitch) = FixedSinCos(pitch);
        return new Level100FloatBasis3Bits(
            Q30ToFloatBits(cosYaw),
            Q30ToFloatBits(MultiplyFixed(sinYaw, sinPitch)),
            Q30ToFloatBits(-MultiplyFixed(sinYaw, cosPitch)),
            0,
            Q30ToFloatBits(cosPitch),
            Q30ToFloatBits(sinPitch),
            Q30ToFloatBits(sinYaw),
            Q30ToFloatBits(-MultiplyFixed(cosYaw, sinPitch)),
            Q30ToFloatBits(MultiplyFixed(cosYaw, cosPitch)));
    }

    private static int Q30Hypotenuse(int left, int right)
    {
        ulong square =
            (ulong)((long)left * left) + (ulong)((long)right * right);
        if (square == 0)
        {
            return 0;
        }
        ulong root = 0;
        ulong bit = 1UL << 62;
        while (bit > square)
        {
            bit >>= 2;
        }
        while (bit != 0)
        {
            if (square >= root + bit)
            {
                square -= root + bit;
                root = (root >> 1) + bit;
            }
            else
            {
                root >>= 1;
            }
            bit >>= 2;
        }
        return checked((int)root);
    }

    private void AdvanceGroundVehicle(
        ActorState state,
        Level100ActorMotionDefinition motion,
        bool fullGuideUpdate)
    {
        Level100ActorPoseSnapshot pose = _actors.GetPose(state.ActorId);
        Level100ActorPoseSnapshot guidedPose = fullGuideUpdate
            ? UpdateGroundVehicleGuide(state, motion, pose)
            : pose with
            {
                AngularVelocityMicroRadiansPerTick = SimVector3.Zero,
            };
        SimVector3 velocity = GroundVehicleStep(
            state,
            motion,
            guidedPose);
        int nextX = checked(
            guidedPose.PositionMillimeters.X + velocity.X);
        int nextZ = checked(
            guidedPose.PositionMillimeters.Z + velocity.Z);
        int nextY = checked(
            Level100Terrain.Instance.SampleGroundElevationMillimeters(
                new SimVector2(nextX, nextZ)) +
            motion.CoreGroundOriginOffsetMillimeters!.Value);
        var nextPosition = new SimVector3(nextX, nextY, nextZ);
        _actors.SetPose(
            state.ActorId,
            guidedPose with
            {
                PositionMillimeters = nextPosition,
                LinearVelocityMillimetersPerTick = new SimVector3(
                    nextPosition.X - guidedPose.PositionMillimeters.X,
                    nextPosition.Y - guidedPose.PositionMillimeters.Y,
                    nextPosition.Z - guidedPose.PositionMillimeters.Z),
            });
    }

    private Level100ActorPoseSnapshot UpdateGroundVehicleGuide(
        ActorState state,
        Level100ActorMotionDefinition motion,
        Level100ActorPoseSnapshot pose)
    {
        Level100WaypointPathDefinition path =
            _definitions.GetWaypointPath(state.WaypointPath!);
        Level100WaypointPointDefinition point =
            path.ChainPoint(state.WaypointPointIndex);
        long deltaX =
            (long)point.PositionMillimeters.X -
            pose.PositionMillimeters.X;
        long deltaZ =
            (long)point.PositionMillimeters.Z -
            pose.PositionMillimeters.Z;
        if (deltaX == 0 && deltaZ == 0)
        {
            return pose with
            {
                AngularVelocityMicroRadiansPerTick = SimVector3.Zero,
            };
        }

        int forwardX = FloatBitsToQ30(
            pose.BasisFloatBits.Row0Z);
        int forwardZ = FloatBitsToQ30(
            pose.BasisFloatBits.Row2Z);
        int currentYaw = FixedAtan2(-forwardX, forwardZ);
        int desiredYaw = FixedAtan2(-deltaX, deltaZ);
        int error = NormalizeMicroRad(desiredYaw - currentYaw);
        int maximumTurnPerBaseTick = ScalePositiveFloatBits(
            motion.MaximumTurnRadiansPerBaseTickFloatBits!.Value,
            1_000_000);
        int fullUpdateMultiplier =
            motion.FullGuideBaseTicks!.Value;
        int easedTurn = DivideRoundNearest(
            (long)Math.Abs(error) * fullUpdateMultiplier,
            10);
        int maximumTurn =
            checked(maximumTurnPerBaseTick * fullUpdateMultiplier);
        int turn = Math.Sign(error) *
            Math.Min(easedTurn, maximumTurn);
        return pose with
        {
            BasisFloatBits = RotateBasisAroundCoreY(
                pose.BasisFloatBits,
                turn),
            AngularVelocityMicroRadiansPerTick =
                new SimVector3(0, turn, 0),
        };
    }

    private SimVector3 GroundVehicleStep(
        ActorState state,
        Level100ActorMotionDefinition motion,
        Level100ActorPoseSnapshot pose)
    {
        Level100WaypointPathDefinition path =
            _definitions.GetWaypointPath(state.WaypointPath!);
        Level100WaypointPointDefinition point =
            path.ChainPoint(state.WaypointPointIndex);
        long deltaX =
            (long)point.PositionMillimeters.X -
            pose.PositionMillimeters.X;
        long deltaZ =
            (long)point.PositionMillimeters.Z -
            pose.PositionMillimeters.Z;
        long radius = motion.ArrivalRadiusMillimeters;
        if ((deltaX * deltaX) + (deltaZ * deltaZ) <
            radius * radius)
        {
            return SimVector3.Zero;
        }

        int forwardX = FloatBitsToQ30(
            pose.BasisFloatBits.Row0Z);
        int forwardZ = FloatBitsToQ30(
            pose.BasisFloatBits.Row2Z);
        int yaw = FixedAtan2(-forwardX, forwardZ);
        int speedMillimetersPerSecond = ScalePositiveFloatBits(
            motion.MaximumSpeedFloatBits!.Value,
            1_000);
        int speedMillimetersPerBaseTick = DivideRoundNearest(
            speedMillimetersPerSecond,
            RetailBaseTicksPerSecond);
        (int sin, int cos) = FixedSinCos(yaw);
        return new SimVector3(
            DivideRoundNearest(
                -(long)sin * speedMillimetersPerBaseTick,
                FixedTrigScale),
            0,
            DivideRoundNearest(
                (long)cos * speedMillimetersPerBaseTick,
                FixedTrigScale));
    }

    private void ObserveWaypointArrival(
        ActorState state,
        Level100ActorSnapshot actor,
        Level100ActorMotionDefinition motion,
        List<Level100ActorMechanicsWaitCompletion> completions)
    {
        Level100WaypointPathDefinition path =
            _definitions.GetWaypointPath(state.WaypointPath!);
        Level100WaypointPointDefinition point =
            path.ChainPoint(state.WaypointPointIndex);
        long deltaX =
            (long)point.PositionMillimeters.X -
            actor.Pose.PositionMillimeters.X;
        long deltaZ =
            (long)point.PositionMillimeters.Z -
            actor.Pose.PositionMillimeters.Z;
        long radius = motion.ArrivalRadiusMillimeters;
        if ((deltaX * deltaX) + (deltaZ * deltaZ) >=
            radius * radius)
        {
            return;
        }

        if (++state.WaypointPointIndex < path.TargetChainNodeIndices.Count)
        {
            return;
        }

        // A closed chain has no end. Retail's cursor is a pointer that it
        // replaces with the current waypoint's own successor
        // (CScriptEventNB::UpdateWaypointFollowing 0x00538470,
        // `mov ecx,[eax+0x3c]` / `mov [esi+0x14],ecx`), and it stops only when
        // that successor is NULL. When the tail points back at the head there
        // is no NULL to reach, so the walk restarts at the head and the
        // FollowWaypointWait completion below never fires - which is the
        // shipped behaviour of the two Level 100 paths whose chains close.
        if (path.IsClosed)
        {
            state.WaypointPointIndex = 0;
            return;
        }

        bool waited = state.WaitForWaypointCompletion;
        string completedPath = state.WaypointPath!;
        SetStoppedIntent(state);
        ZeroActorVelocity(state.ActorId);
        if (waited)
        {
            completions.Add(new Level100ActorMechanicsWaitCompletion(
                actor.ActorId,
                Level100ActorScriptWaitKind.FollowWaypoint,
                completedPath));
        }
    }

    private void BeginWaypoint(Level100ActorScriptCommand command)
    {
        ActorState state = RequireState(command);
        string pathName = command.Argument ??
            throw new InvalidOperationException(
                "Released waypoint command has no path.");
        _ = _definitions.GetWaypointPath(pathName);
        Level100ActorSnapshot actor = _actors.GetActor(state.ActorId);
        _ = _definitions.FindMotionDefinition(actor.DefinitionName) ??
            throw new InvalidOperationException(
                $"Released waypoint actor {actor.ActorId} has no class motion definition.");
        state.Intent = Level100ActorCommandIntent.FollowingWaypoint;
        state.TargetActorId = null;
        state.WaypointPath = pathName;
        state.WaypointPointIndex = 0;
        // The released command scalar is canonical replay state, but its
        // actor-specific movement meaning is not established by this slice.
        state.WaypointCommandScalar = command.Scalar;
        state.WaitForWaypointCompletion =
            command.Kind ==
            Level100ActorScriptCommandKind.FollowWaypointWait;
    }

    private void BeginAttack(Level100ActorScriptCommand command)
    {
        ActorState state = RequireState(command);
        Level100ActorId target = command.TargetActorId ??
            throw new InvalidOperationException(
                "Released Attack command has no target.");
        _ = _actors.GetActor(target);
        ClearWaypoint(state);
        state.Intent = Level100ActorCommandIntent.Attacking;
        state.TargetActorId = target;
        ZeroActorVelocity(state.ActorId);
        ArmActorWeapons(state);
    }

    private void SetSimpleIntent(
        Level100ActorScriptCommand command,
        Level100ActorCommandIntent intent)
    {
        ActorState state = RequireState(command);
        ClearWaypoint(state);
        state.Intent = intent;
        state.TargetActorId = null;
        ZeroActorVelocity(state.ActorId);
    }

    private void Stop(Level100ActorScriptCommand command)
    {
        ActorState state = RequireState(command);
        SetStoppedIntent(state);
        ZeroActorVelocity(state.ActorId);
    }

    private ActorState RequireState(
        Level100ActorScriptCommand command)
    {
        Level100ActorId actorId = command.ActorId ??
            throw new InvalidOperationException(
                $"Released actor command {command.Kind} has no actor.");
        _ = _actors.GetActor(actorId);
        if (_states.TryGetValue(actorId.Value, out ActorState? state))
        {
            return state;
        }

        state = new ActorState
        {
            ActorId = actorId,
            Intent = Level100ActorCommandIntent.Stopped,
        };
        _states.Add(actorId.Value, state);
        return state;
    }

    private void ZeroActorVelocity(Level100ActorId actorId)
    {
        Level100ActorPoseSnapshot pose =
            _actors.GetPose(actorId);
        _actors.SetPose(
            actorId,
            pose with
            {
                LinearVelocityMillimetersPerTick =
                    SimVector3.Zero,
                AngularVelocityMicroRadiansPerTick =
                    SimVector3.Zero,
            });
    }

    private static void SetStoppedIntent(ActorState state)
    {
        ClearWaypoint(state);
        state.Intent = Level100ActorCommandIntent.Stopped;
        state.TargetActorId = null;
    }

    private static void ClearWaypoint(ActorState state)
    {
        state.WaypointPath = null;
        state.WaypointPointIndex = 0;
        state.WaypointCommandScalar = 0;
        state.WaitForWaypointCompletion = false;
    }

    private void ValidateDefinitionIdentity()
    {
        if (!StringComparer.Ordinal.Equals(
                _actors.Snapshot.DefinitionSetIdentitySha256,
                _definitions.IdentitySha256))
        {
            throw new ArgumentException(
                "Level 100 actor mechanics definitions do not own the registry.");
        }
    }

    private void ValidateSnapshotState(
        Level100ActorCommandIntentSnapshot source,
        Level100ActorMechanicsSnapshot snapshot)
    {
        Level100ActorSnapshot actor =
            _actors.GetActor(source.ActorId);
        Level100ActorMotionDefinition? motion =
            _definitions.FindMotionDefinition(actor.DefinitionName);
        bool validGroundPhase =
            motion?.MotionClass ==
                Level100ActorMotionClass.GroundVehicle
                ? source.GroundFullGuideBaseTickPhase >= 0 &&
                    source.GroundFullGuideBaseTickPhase <
                    motion.FullGuideBaseTicks!.Value
                : source.GroundFullGuideBaseTickPhase == 0;
        if (source.ActorId.Value <= 0 ||
            !Enum.IsDefined(source.Intent) ||
            source.WaypointPointIndex < 0 ||
            !validGroundPhase)
        {
            throw new ArgumentException(
                "Level 100 actor mechanics snapshot has invalid state.",
                nameof(snapshot));
        }

        if (source.Intent ==
            Level100ActorCommandIntent.FollowingWaypoint)
        {
            if (source.TargetActorId.HasValue ||
                source.WaypointPath is null ||
                motion is null)
            {
                throw new ArgumentException(
                    "Level 100 actor mechanics snapshot has invalid waypoint intent.",
                    nameof(snapshot));
            }
            Level100WaypointPathDefinition path =
                _definitions.GetWaypointPath(source.WaypointPath);
            if (source.WaypointPointIndex >= path.TargetChainNodeIndices.Count)
            {
                throw new ArgumentException(
                    "Level 100 actor mechanics snapshot has invalid waypoint progress.",
                    nameof(snapshot));
            }
            return;
        }

        if (source.WaypointPath is not null ||
            source.WaypointPointIndex != 0 ||
            source.WaypointCommandScalar != 0 ||
            source.WaitForWaypointCompletion)
        {
            throw new ArgumentException(
                "Level 100 actor mechanics snapshot retained an inactive waypoint.",
                nameof(snapshot));
        }

        if (source.Intent ==
            Level100ActorCommandIntent.Attacking)
        {
            if (!source.TargetActorId.HasValue)
            {
                throw new ArgumentException(
                    "Level 100 actor mechanics snapshot has no attack target.",
                    nameof(snapshot));
            }
            _ = _actors.GetActor(source.TargetActorId.Value);
        }
        else if (source.TargetActorId.HasValue)
        {
            throw new ArgumentException(
                "Level 100 actor mechanics snapshot has an unexpected target.",
                nameof(snapshot));
        }
    }

    private static Level100ActorCommandIntentSnapshot SnapshotState(
        ActorState state) => new(
            state.ActorId,
            state.AiState,
            state.Allegiance,
            state.HasAllegianceOverride,
            state.Intent,
            state.TargetActorId,
            state.WaypointPath,
            state.WaypointPointIndex,
            state.WaypointCommandScalar,
            state.WaitForWaypointCompletion,
            state.GroundFullGuideBaseTickPhase);

    private static ActorState Restore(
        Level100ActorCommandIntentSnapshot source) => new()
        {
            ActorId = source.ActorId,
            AiState = source.AiState,
            Allegiance = source.Allegiance,
            HasAllegianceOverride = source.HasAllegianceOverride,
            Intent = source.Intent,
            TargetActorId = source.TargetActorId,
            WaypointPath = source.WaypointPath,
            WaypointPointIndex = source.WaypointPointIndex,
            WaypointCommandScalar = source.WaypointCommandScalar,
            WaitForWaypointCompletion =
                source.WaitForWaypointCompletion,
            GroundFullGuideBaseTickPhase =
                source.GroundFullGuideBaseTickPhase,
        };

    private static Level100FloatBasis3Bits RotateBasisAroundCoreY(
        Level100FloatBasis3Bits basis,
        int angleMicroRad)
    {
        if (angleMicroRad == 0)
        {
            return basis;
        }

        (int sin, int cos) = FixedSinCos(angleMicroRad);
        int r0x = FloatBitsToQ30(basis.Row0X);
        int r0y = FloatBitsToQ30(basis.Row0Y);
        int r0z = FloatBitsToQ30(basis.Row0Z);
        int r2x = FloatBitsToQ30(basis.Row2X);
        int r2y = FloatBitsToQ30(basis.Row2Y);
        int r2z = FloatBitsToQ30(basis.Row2Z);
        return new Level100FloatBasis3Bits(
            Q30ToFloatBits(MultiplyFixed(cos, r0x) -
                MultiplyFixed(sin, r2x)),
            Q30ToFloatBits(MultiplyFixed(cos, r0y) -
                MultiplyFixed(sin, r2y)),
            Q30ToFloatBits(MultiplyFixed(cos, r0z) -
                MultiplyFixed(sin, r2z)),
            basis.Row1X,
            basis.Row1Y,
            basis.Row1Z,
            Q30ToFloatBits(MultiplyFixed(sin, r0x) +
                MultiplyFixed(cos, r2x)),
            Q30ToFloatBits(MultiplyFixed(sin, r0y) +
                MultiplyFixed(cos, r2y)),
            Q30ToFloatBits(MultiplyFixed(sin, r0z) +
                MultiplyFixed(cos, r2z)));
    }

    private static int MultiplyFixed(int left, int right) =>
        DivideRoundNearest(
            (long)left * right,
            FixedTrigScale);

    private static (int Sin, int Cos) FixedSinCos(
        int angleMicroRad)
    {
        int angle = NormalizeMicroRad(angleMicroRad);
        int resultSign = 1;
        if (angle > HalfPiMicroRad)
        {
            angle -= PiMicroRad;
            resultSign = -1;
        }
        else if (angle < -HalfPiMicroRad)
        {
            angle += PiMicroRad;
            resultSign = -1;
        }

        long x = CordicGainQ30;
        long y = 0;
        int remainder = angle;
        ReadOnlySpan<int> angles = CordicAnglesMicroRad;
        for (int index = 0; index < angles.Length; index++)
        {
            long previousX = x;
            if (remainder >= 0)
            {
                x -= y >> index;
                y += previousX >> index;
                remainder -= angles[index];
            }
            else
            {
                x += y >> index;
                y -= previousX >> index;
                remainder += angles[index];
            }
        }

        return ((int)y * resultSign, (int)x * resultSign);
    }

    private static int FixedAtan2(long y, long x)
    {
        if (x == 0)
        {
            return y switch
            {
                > 0 => HalfPiMicroRad,
                < 0 => -HalfPiMicroRad,
                _ => 0,
            };
        }

        int angle = 0;
        if (x < 0)
        {
            bool upperHalf = y >= 0;
            x = -x;
            y = -y;
            angle = upperHalf ? PiMicroRad : -PiMicroRad;
        }

        ReadOnlySpan<int> angles = CordicAnglesMicroRad;
        for (int index = 0; index < angles.Length; index++)
        {
            long previousX = x;
            if (y > 0)
            {
                x += y >> index;
                y -= previousX >> index;
                angle += angles[index];
            }
            else if (y < 0)
            {
                x -= y >> index;
                y += previousX >> index;
                angle -= angles[index];
            }
        }

        return NormalizeMicroRad(angle);
    }

    private static int NormalizeMicroRad(int angle)
    {
        while (angle > PiMicroRad)
        {
            angle -= TwoPiMicroRad;
        }
        while (angle < -PiMicroRad)
        {
            angle += TwoPiMicroRad;
        }
        return angle;
    }

    private static int ScalePositiveFloatBits(
        int bits,
        int scale)
    {
        uint raw = unchecked((uint)bits);
        int exponent = (int)((raw >> 23) & 0xFF);
        uint fraction = raw & 0x7FFFFF;
        if ((raw & 0x80000000) != 0 ||
            exponent == 0xFF ||
            (exponent == 0 && fraction == 0))
        {
            throw new InvalidDataException(
                "A Level 100 ground-motion scalar is not finite and positive.");
        }

        ulong significand = exponent == 0
            ? fraction
            : (1U << 23) | fraction;
        int binaryExponent = exponent == 0
            ? -149
            : exponent - 150;
        ulong scaled = checked(significand * (ulong)scale);
        ulong value = binaryExponent >= 0
            ? checked(scaled << binaryExponent)
            : RoundShiftRightToEven(scaled, -binaryExponent);
        return checked((int)value);
    }

    private static int FloatBitsToQ30(int bits)
    {
        uint raw = unchecked((uint)bits);
        bool negative = (raw & 0x80000000) != 0;
        int exponent = (int)((raw >> 23) & 0xFF);
        uint fraction = raw & 0x7FFFFF;
        if (exponent == 0xFF)
        {
            throw new InvalidDataException(
                "A Level 100 actor basis contains a non-finite component.");
        }

        ulong significand = exponent == 0
            ? fraction
            : (1U << 23) | fraction;
        int binaryExponent = exponent == 0
            ? -119
            : exponent - 120;
        ulong magnitude = binaryExponent >= 0
            ? checked(significand << binaryExponent)
            : RoundShiftRightToEven(significand, -binaryExponent);
        int value = checked((int)magnitude);
        return negative ? -value : value;
    }

    private static int Q30ToFloatBits(int value)
    {
        if (value == 0)
        {
            return 0;
        }

        bool negative = value < 0;
        uint magnitude = checked((uint)Math.Abs((long)value));
        int highestBit = 31 -
            System.Numerics.BitOperations.LeadingZeroCount(magnitude);
        int unbiasedExponent = highestBit - 30;
        ulong significand;
        if (highestBit <= 23)
        {
            significand = (ulong)magnitude << (23 - highestBit);
        }
        else
        {
            int shift = highestBit - 23;
            significand = RoundShiftRightToEven(magnitude, shift);
            if (significand == (1UL << 24))
            {
                significand >>= 1;
                unbiasedExponent++;
            }
        }

        int biasedExponent = unbiasedExponent + 127;
        if (biasedExponent is <= 0 or >= 0xFF)
        {
            throw new InvalidDataException(
                "A Level 100 actor basis left the supported finite range.");
        }

        uint result =
            (negative ? 0x80000000U : 0U) |
            ((uint)biasedExponent << 23) |
            ((uint)significand & 0x7FFFFF);
        return unchecked((int)result);
    }

    private static ulong RoundShiftRightToEven(
        ulong value,
        int shift)
    {
        if (shift <= 0)
        {
            return checked(value << -shift);
        }
        if (shift >= 64)
        {
            return 0;
        }

        ulong quotient = value >> shift;
        ulong mask = (1UL << shift) - 1;
        ulong remainder = value & mask;
        ulong halfway = 1UL << (shift - 1);
        return remainder > halfway ||
            (remainder == halfway && (quotient & 1) != 0)
                ? quotient + 1
                : quotient;
    }

    private static int DivideRoundNearest(
        long value,
        long denominator)
    {
        if (denominator <= 0)
        {
            throw new ArgumentOutOfRangeException(nameof(denominator));
        }
        return checked((int)(value >= 0
            ? (value + (denominator / 2)) / denominator
            : -((-value + (denominator / 2)) / denominator)));
    }
}
