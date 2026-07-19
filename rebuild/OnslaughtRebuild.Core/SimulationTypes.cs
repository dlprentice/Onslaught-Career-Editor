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
    ReachTargetZone1 = 0,
    TargetZone1DispatchPending = 1,
    ReachFiringRange = 2,
    FiringRangeDispatchPending = 3,
    FiringRangeReached = 4,
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
    sbyte LookX = 0)
{
    // Fire may be held. UI adapters must edge-sample ToggleMode and Reset.
    // LookX is body look left/right (−1/0/+1); default 0 preserves prior tapes.
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
    int Energy,
    int Shield,
    int Hull,
    int TransformTicksRemaining,
    int FireCooldownTicksRemaining,
    Level100OpeningPhase Level100Phase,
    int Level100DispatchTicksRemaining,
    int NextProjectileId,
    int TargetsDestroyed,
    IReadOnlyList<TargetSnapshot> Targets,
    IReadOnlyList<ProjectileSnapshot> Projectiles);
