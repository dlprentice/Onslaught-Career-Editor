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
    Level100ActorCommandIntent Intent,
    Level100ActorId? TargetActorId,
    string? WaypointPath,
    int WaypointPointIndex,
    int WaypointCommandScalar,
    bool WaitForWaypointCompletion,
    int GroundFullGuideBaseTickPhase);

public sealed record Level100ActorMechanicsSnapshot(
    long LastConsumedCommandSequence,
    int RetailBaseTickAccumulatorThirtieths,
    IReadOnlyList<Level100ActorCommandIntentSnapshot> Actors);

public sealed record Level100ActorMechanicsWaitCompletion(
    Level100ActorId ActorId,
    Level100ActorScriptWaitKind WaitKind,
    string Argument);

/// <summary>
/// Canonical consumer for the released Level 100 actor-script mechanics
/// commands. It observes the released 20 Hz base frame in the 30 Hz Core and
/// implements only the evidenced CGroundVehicle guide cadence, normal speed,
/// heading bound, and terrain grounding. Actor identity and the full physical
/// pose remain exclusively in <see cref="Level100ActorRegistry"/>.
/// </summary>
public sealed class Level100ActorMechanics
{
    public const int RetailBaseTicksPerSecond = 20;

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
    private int _retailBaseTickAccumulatorThirtieths;

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
        if (snapshot.LastConsumedCommandSequence < 0 ||
            snapshot.RetailBaseTickAccumulatorThirtieths is < 0 or
                >= SimulationConstants.TicksPerSecond ||
            snapshot.Actors.Any(item => item is null))
        {
            throw new ArgumentException(
                "Level 100 actor mechanics snapshot is invalid.",
                nameof(snapshot));
        }

        _lastConsumedCommandSequence = snapshot.LastConsumedCommandSequence;
        _retailBaseTickAccumulatorThirtieths =
            snapshot.RetailBaseTickAccumulatorThirtieths;
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
    }

    public Level100ActorMechanicsSnapshot Snapshot => new(
        _lastConsumedCommandSequence,
        _retailBaseTickAccumulatorThirtieths,
        Array.AsReadOnly(_states.Values.Select(SnapshotState).ToArray()));

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

    public IReadOnlyList<Level100ActorMechanicsWaitCompletion> AdvanceTick()
    {
        _retailBaseTickAccumulatorThirtieths += RetailBaseTicksPerSecond;
        if (_retailBaseTickAccumulatorThirtieths <
            SimulationConstants.TicksPerSecond)
        {
            ClearSkippedCoreTickVelocities();
            return Array.Empty<Level100ActorMechanicsWaitCompletion>();
        }

        _retailBaseTickAccumulatorThirtieths -=
            SimulationConstants.TicksPerSecond;
        return AdvanceRetailBaseTick();
    }

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
                    RequireState(command).Allegiance = command.Scalar;
                    break;
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

        return Array.AsReadOnly(completions.ToArray());
    }

    private void ClearSkippedCoreTickVelocities()
    {
        foreach (ActorState state in _states.Values)
        {
            Level100ActorSnapshot actor =
                _actors.GetActor(state.ActorId);
            Level100ActorMotionDefinition? motion =
                _definitions.FindMotionDefinition(
                    actor.DefinitionName);
            if (motion?.MotionClass ==
                Level100ActorMotionClass.GroundVehicle)
            {
                ZeroActorVelocity(state.ActorId);
            }
        }
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
            path.Points[state.WaypointPointIndex];
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
            path.Points[state.WaypointPointIndex];
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
            path.Points[state.WaypointPointIndex];
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

        if (++state.WaypointPointIndex < path.Points.Count)
        {
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
            if (source.WaypointPointIndex >= path.Points.Count)
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
