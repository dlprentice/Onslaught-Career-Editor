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

public enum Level100OpeningPhase
{
    Briefing = 0,
    ReachTargetZone1 = 1,
    TargetZone1DispatchPending = 2,
    ReachFiringRange = 3,
    FiringRangeDispatchPending = 4,
    FiringRangeBriefing = 5,
    FiringRangeExercise = 6,
    FiringRangeVulcanBriefing = 7,
    FiringRangeVulcanExercise = 8,
}

public enum Level100TutorialMessage
{
    None = 0,
    HudIntroduction = 1,
    ThreatCircle = 2,
    Scanner = 3,
    MessageLog = 4,
    TechnicianStatus = 5,
    MovementControls = 6,
    ReachTargetZone1 = 7,
    ScannerObjective = 8,
    FiringRangeInstruction = 9,
    WeaponSystems = 10,
    WeaponIndicator = 11,
    PulseCannon = 12,
    OpenFire = 13,
    PulseCannonEnergy = 14,
    VulcanCannon = 15,
    OpenFireVulcan = 16,
    VulcanCannonAmmo = 17,
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

public sealed record TargetSnapshot(int Id, SimVector2 Position, int Hull, bool IsActive);

public sealed record ProjectileSnapshot(
    int Id,
    SimVector2 Position,
    SimVector2 Velocity,
    int ElevationMillimeters,
    int VerticalVelocityMillimetersPerTick,
    int RemainingTicks);

public sealed record WorldSnapshot(
    int Tick,
    uint Seed,
    VehicleMode Mode,
    VehicleTransition Transition,
    SimVector2 PlayerPosition,
    SimVector2 PlayerVelocity,
    int PlayerGroundElevationMillimeters,
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
    int Level100TimelineTick,
    Level100TutorialMessage Level100Message,
    int Level100EventMessageTicksRemaining,
    bool Level100PowerEnabled,
    bool Level100FlightEnabled,
    bool Level100PulseCannonEnabled,
    bool Level100VulcanCannonEnabled,
    Level100OpeningPhase Level100Phase,
    int Level100DispatchTicksRemaining,
    int Level100FiringRangeSequenceTick,
    int Level100FiringRangeHandoffTick,
    int NextProjectileId,
    int TargetsDestroyed,
    IReadOnlyList<TargetSnapshot> Targets,
    IReadOnlyList<ProjectileSnapshot> Projectiles)
{
    public bool Level100PlayerControlEnabled => Level100PowerEnabled;

    public bool Level100FiringRangeTargetsActive =>
        Level100FiringRangeSequenceTick >=
            SimulationConstants.Level100StaticTargetsActivationTick &&
        Targets.Any(target => target.Id is >= 1 and <= 4 && target.IsActive);

    public bool Level100CurrentWeaponHighlighted =>
        Level100FiringRangeSequenceTick >=
            SimulationConstants.Level100WeaponIndicatorStartTick &&
        Level100FiringRangeSequenceTick <
            SimulationConstants.Level100WeaponIndicatorEndTick;

    public bool Level100FireHelpVisible =>
        Level100FiringRangeSequenceTick >=
            SimulationConstants.Level100FireHelpActivationTick &&
        Level100Phase == Level100OpeningPhase.FiringRangeExercise &&
        Level100PulseCannonEnabled;
}
