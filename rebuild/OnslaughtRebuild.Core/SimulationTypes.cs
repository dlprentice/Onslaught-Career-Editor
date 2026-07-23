// SPDX-License-Identifier: GPL-3.0-or-later

namespace OnslaughtRebuild.Core;

public enum VehicleMode
{
    Walker = 0,
    Jet = 1,
}

public enum VehicleTransition
{
    None = 0,
    WalkerToJet = 1,
    JetToWalker = 2,
}

public enum AquilaJetWeapon : byte
{
    None = 0,
    MechVulcanCannon = 1,
    SpreadPod = 2,
}

[Flags]
public enum AquilaFlightEvents : ushort
{
    None = 0,
    TransformRejected = 1 << 0,
    WalkerToJetStarted = 1 << 1,
    JetToWalkerStarted = 1 << 2,
    TransformCompleted = 1 << 3,
    Touchdown = 1 << 4,
    EnteredWater = 1 << 5,
    WaterSkim = 1 << 6,
    StallStarted = 1 << 7,
    GroundImpactDamageThresholdCrossed = 1 << 8,
    WaterFailureStarted = 1 << 9,
    JetWeaponFireRequested = 1 << 10,
}

public sealed record AquilaFlightEvent(
    int Tick,
    AquilaFlightEvents Kind,
    VehicleMode Mode,
    VehicleTransition Transition,
    AquilaJetWeapon Weapon = AquilaJetWeapon.None);

[Flags]
public enum SimActions : byte
{
    None = 0,
    ToggleMode = 1 << 0,
    Fire = 1 << 1,
    Reset = 1 << 2,
    LandingJets = 1 << 3,
}

public readonly record struct SimVector2(int X, int Z)
{
    public static SimVector2 Zero => new(0, 0);
}

public readonly record struct SimInput(
    sbyte MoveX,
    sbyte MoveZ,
    SimActions Actions = SimActions.None,
    sbyte LookX = 0,
    sbyte LookY = 0,
    short LookXAnalogPermille = 0,
    short LookYAnalogPermille = 0)
{
    // Fire and LandingJets may be held. UI adapters must edge-sample
    // ToggleMode and Reset.
    // LookX is body look left/right and LookY is screen up/down (-1/0/+1).
    // Analog look is the deterministic -1000..1000 axis produced by an input adapter.
    public static SimInput Idle => new(0, 0);

    public bool HasAction(SimActions action) => (Actions & action) != 0;

    public void Validate()
    {
        if (MoveX is < -1 or > 1)
        {
            throw new ArgumentOutOfRangeException(nameof(MoveX), "MoveX must be -1, 0, or 1.");
        }

        if (MoveZ is < -1 or > 1)
        {
            throw new ArgumentOutOfRangeException(nameof(MoveZ), "MoveZ must be -1, 0, or 1.");
        }

        if (LookX is < -1 or > 1)
        {
            throw new ArgumentOutOfRangeException(nameof(LookX), "LookX must be -1, 0, or 1.");
        }

        if (LookY is < -1 or > 1)
        {
            throw new ArgumentOutOfRangeException(nameof(LookY), "LookY must be -1, 0, or 1.");
        }

        if (LookXAnalogPermille is < -1_000 or > 1_000)
        {
            throw new ArgumentOutOfRangeException(
                nameof(LookXAnalogPermille),
                "LookXAnalogPermille must be between -1000 and 1000.");
        }

        if (LookYAnalogPermille is < -1_000 or > 1_000)
        {
            throw new ArgumentOutOfRangeException(
                nameof(LookYAnalogPermille),
                "LookYAnalogPermille must be between -1000 and 1000.");
        }

        const SimActions known = SimActions.ToggleMode |
            SimActions.Fire |
            SimActions.Reset |
            SimActions.LandingJets;
        if ((Actions & ~known) != 0)
        {
            throw new ArgumentOutOfRangeException(nameof(Actions), "Input contains an unknown action bit.");
        }
    }
}

public sealed record TargetSnapshot(
    Level100ActorId ActorId,
    int Id,
    SimVector2 Position,
    int Hull,
    bool IsActive);

public sealed record ProjectileSnapshot(
    int Id,
    SimVector2 Position,
    SimVector2 Velocity,
    int ElevationMillimeters,
    int VerticalVelocityMillimetersPerTick,
    int RemainingTicks);

public sealed record WalkerFootContactSnapshot(
    int Id,
    SimVector2 Position,
    int GroundElevationMillimeters,
    int PhaseThirds,
    int LiftMillimeters)
{
    public int StepPhase => PhaseThirds == 0
        ? 0
        : Math.Min(
            SimulationConstants.WalkerFootPhaseEnd,
            (PhaseThirds + 1) / 3);
}

public abstract record Level100SimulationFact;

public sealed record Level100ActorHitFact(
    Level100ActorId ActorId,
    Level100ActorId? OtherActorId = null,
    uint OtherThingTypeMask = 0)
    : Level100SimulationFact;

public sealed record Level100ActorStartedDyingFact(Level100ActorId ActorId)
    : Level100SimulationFact;

public sealed record Level100ActorDiedFact(Level100ActorId ActorId)
    : Level100SimulationFact;

public sealed record Level100ActorPoseFact(
    Level100ActorId ActorId,
    Level100ActorPoseSnapshot Pose)
    : Level100SimulationFact;

public sealed record Level100ActorActivationFact(
    Level100ActorId ActorId,
    bool Active)
    : Level100SimulationFact;

public sealed record Level100ActorObjectiveFact(
    Level100ActorId ActorId,
    bool IsObjective)
    : Level100SimulationFact;

public sealed record Level100ActorHealthFact(
    Level100ActorId ActorId,
    int Health)
    : Level100SimulationFact;

public sealed record Level100SpawnThingFact(
    Level100ActorId OwnerActorId,
    string DefinitionName,
    string SpawnerName,
    int Count,
    string ScriptName)
    : Level100SimulationFact;

public sealed record Level100MissionInputFact(Level100MissionInput Input)
    : Level100SimulationFact;

public sealed record Level100PlayerDamageFact(int Damage) : Level100SimulationFact;

public sealed record Level100PlayerDeathFact : Level100SimulationFact;

public sealed record Level100WaterLossFact : Level100SimulationFact;

public sealed record Level100ActorScriptWaitCompletedFact(
    Level100ActorId ActorId,
    Level100ActorScriptWaitKind WaitKind,
    string? Argument = null)
    : Level100SimulationFact;

public sealed record Level100TriggerActorSnapshot(
    Level100MissionTrigger Trigger,
    SimVector2 Position,
    bool Active,
    bool IsObjective,
    bool Reached);

public sealed record WorldSnapshot(
    int Tick,
    uint Seed,
    Level100TutorialProgress InitialLevel100TutorialProgress,
    VehicleMode Mode,
    VehicleTransition Transition,
    SimVector2 PlayerPosition,
    SimVector2 PlayerVelocity,
    int PlayerGroundElevationMillimeters,
    int PlayerGroundDeltaMillimeters,
    int PlayerElevationMillimeters,
    int PlayerVerticalVelocityMillimetersPerTick,
    bool PlayerOnGround,
    bool PlayerInWater,
    bool PlayerWaterFailure,
    bool PlayerOnSteepSlope,
    bool LandingJetsActive,
    int GroundImpactSpeedMillimetersPerTick,
    IReadOnlyList<AquilaFlightEvent> AquilaFlightEventLog,
    sbyte FacingX,
    sbyte FacingZ,
    int FacingYawMicroRad,
    int WalkerYawVelocityMicroRadPerTick,
    int FacingPitchMicroRad,
    int WalkerPitchVelocityMicroRadPerTick,
    int BodyRollMicroRad,
    int RollVelocityMicroRadPerTick,
    int Energy,
    int Shield,
    int Hull,
    int TransformTicksRemaining,
    bool WalkerToJetUsesTakeoffLift,
    bool WalkerToJetLiftApplied,
    int TicksSinceGroundContact,
    int JetTicksSinceTransform,
    int JetStrafeTicksRemaining,
    int JetStrafeAccelerationRemainder,
    int JetEnergyDrainRemainderThirds,
    int JetThrusterPermille,
    int JetGroundedSlowTicks,
    int JetStallTicks,
    int FireCooldownTicksRemaining,
    int Level100OpeningTicksRemaining,
    bool Level100PlayerActive,
    bool Level100FlightEnabled,
    bool Level100PulseCannonEnabled,
    bool Level100VulcanCannonEnabled,
    bool Level100MechVulcanCannonEnabled,
    bool Level100MissilePodEnabled,
    int Level100HudEmphasisMask,
    Level100MissionSnapshot Level100Mission,
    IReadOnlyList<Level100MissionEvent> Level100MissionEvents,
    Level100ActorRegistrySnapshot Level100Actors,
    Level100DestructionRuntimeSnapshot Level100Destruction,
    IReadOnlyList<Level100DestructionEvent> Level100DestructionEvents,
    Level100ActorScriptRuntimeSnapshot Level100ActorScripts,
    IReadOnlyList<Level100ActorScriptCommand> Level100ActorScriptCommands,
    int NextProjectileId,
    IReadOnlyList<ProjectileSnapshot> Projectiles,
    IReadOnlyList<WalkerFootContactSnapshot> WalkerFeet)
{
    public bool Level100PlayerControlEnabled =>
        Level100PlayerActive && Level100OpeningTicksRemaining == 0;

    public bool Level100StaticTargetsArmed => Level100Actors.Actors.Any(actor =>
        actor.TargetGroup == Level100MissionTargetGroup.StaticTargets &&
        actor.IsObjective &&
        actor.Lifecycle != Level100ActorLifecycle.Destroyed);

    public IReadOnlyList<Level100TriggerActorSnapshot> Level100TriggerActors =>
        Array.AsReadOnly(Level100Actors.Actors
            .Where(actor => actor.Trigger.HasValue && actor.Pose is not null)
            .OrderBy(actor => actor.Trigger)
            .Select(actor => new Level100TriggerActorSnapshot(
                actor.Trigger!.Value,
                new SimVector2(
                    actor.Pose!.PositionMillimeters.X,
                    actor.Pose.PositionMillimeters.Z),
                actor.Active,
                actor.IsObjective,
                actor.TriggerEventDispatched))
            .ToArray());

    public int TargetsDestroyed => Level100Actors.Actors.Count(actor =>
        actor.TargetGroup == Level100MissionTargetGroup.StaticTargets &&
        actor.Lifecycle == Level100ActorLifecycle.Destroyed);

    public IReadOnlyList<TargetSnapshot> Targets =>
        Array.AsReadOnly(Level100Actors.Actors
            .Where(actor =>
                actor.TargetGroup == Level100MissionTargetGroup.StaticTargets &&
                actor.Pose is not null)
            .OrderBy(actor => actor.TargetOrdinal)
            .Select(actor => new TargetSnapshot(
                actor.ActorId,
                actor.TargetOrdinal,
                new SimVector2(
                    actor.Pose!.PositionMillimeters.X,
                    actor.Pose.PositionMillimeters.Z),
                actor.Health,
                actor.Active && actor.Lifecycle != Level100ActorLifecycle.Destroyed))
            .ToArray());

    public int PlayerAltitudeAboveGroundMillimeters =>
        PlayerElevationMillimeters - PlayerGroundElevationMillimeters;

    public int PlayerAltitudeAboveSurfaceMillimeters =>
        PlayerElevationMillimeters - Math.Max(
            PlayerGroundElevationMillimeters,
            Level100Terrain.WaterElevationMillimeters);

    public bool Level100FiringRangeTargetsActive =>
        Level100StaticTargetsArmed &&
        Targets.Any(target => target.Id is >= 1 and <= 4 && target.IsActive);

    public bool Level100CurrentWeaponHighlighted =>
        (Level100HudEmphasisMask & (1 << 5)) != 0;
}
