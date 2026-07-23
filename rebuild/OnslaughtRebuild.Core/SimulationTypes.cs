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
}

[Flags]
public enum SimActions : byte
{
    None = 0,
    ToggleMode = 1 << 0,
    Fire = 1 << 1,
    Reset = 1 << 2,
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
    // Fire may be held. UI adapters must edge-sample ToggleMode and Reset.
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

        const SimActions known = SimActions.ToggleMode | SimActions.Fire | SimActions.Reset;
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
    sbyte FacingX,
    sbyte FacingZ,
    int FacingYawMicroRad,
    int WalkerYawVelocityMicroRadPerTick,
    int FacingPitchMicroRad,
    int WalkerPitchVelocityMicroRadPerTick,
    int Energy,
    int Shield,
    int Hull,
    int TransformTicksRemaining,
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

    public bool Level100FiringRangeTargetsActive =>
        Level100StaticTargetsArmed &&
        Targets.Any(target => target.Id is >= 1 and <= 4 && target.IsActive);

    public bool Level100CurrentWeaponHighlighted =>
        (Level100HudEmphasisMask & (1 << 5)) != 0;
}
