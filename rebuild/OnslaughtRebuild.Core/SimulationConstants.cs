// SPDX-License-Identifier: GPL-3.0-or-later

namespace OnslaughtRebuild.Core;

public static class SimulationConstants
{
    public const int TicksPerSecond = 30;
    public const int ArenaHalfExtent = 30_000;
    // Milli-retail units/tick at 30 Hz ≈ 3.0 retail units/s (pair p27 envelope
    // [2.85, 3.15]). Policy:
    // reverse-engineering/game-mechanics/walker-forward-retail-to-core-translation-policy.md
    // Schema: battleengine-walker-forward-scalar-response.v2
    public const int WalkerSpeedPerTick = 100;
    // Milli-retail units/tick at 30 Hz ≈ 11.43 retail units/s (pair jet-p06
    // envelope [10.860, 12.003]). Policy:
    // reverse-engineering/game-mechanics/jet-forward-retail-to-core-translation-policy.md
    // Schema: battleengine-jet-forward-scalar-response.v1
    public const int JetSpeedPerTick = 381;
    // Milli-radians/tick at 30 Hz ≈ 0.0907 rad/s Look/Left hold (pair turn-p02
    // envelope [0.0816, 0.0997]). Policy:
    // reverse-engineering/game-mechanics/walker-turn-yaw-retail-to-core-translation-policy.md
    // Schema: battleengine-walker-turn-yaw-scalar-response.v1
    // Wired: LookX integrates continuous milli-rad yaw; FacingX/Z eight-way snap.
    public const int WalkerLookYawRateMilliRadPerTick = 3;
    // Milli-retail units/tick at 30 Hz ≈ 3.015 u/s Movement/Left path speed
    // (pair strafe-p02). Policy:
    // reverse-engineering/game-mechanics/walker-strafe-retail-to-core-translation-policy.md
    // Schema: battleengine-walker-strafe-lateral-scalar-response.v1
    // Not yet wired as a separate strafe axis in UpdateMovement (uses MoveX*speed).
    public const int WalkerStrafeSpeedPerTick = 101;
    public const int MaximumEnergy = 1_000;
    public const int MaximumShield = 1_000;
    public const int MaximumHull = 1_000;
    public const int TransformEnergyThreshold = 200;
    public const int TransformEnergyCost = 120;
    public const int TransformDurationTicks = 15;
    // Ticks @ 30 Hz for walker→jet settle after Transform (pair xform-p03,
    // mid ~4.92 s → 148). Policy:
    // reverse-engineering/game-mechanics/walker-transform-morph-retail-to-core-translation-policy.md
    // Distinct from TransformDurationTicks (short lock, not morph settle).
    public const int MorphToJetSettleTicks = 148;
    public const int WalkerEnergyRegenerationPerTick = 4;
    public const int WalkerShieldRegenerationPerTick = 2;
    public const int JetEnergyDrainPerTick = 3;
    public const int FireEnergyCost = 30;
    public const int FireCooldownTicks = 6;
    public const int ProjectileSpeedPerTick = 1_200;
    public const int ProjectileLifetimeTicks = 40;
    public const int ProjectileDamage = 250;
    public const int TargetHull = 1_000;
    public const int TargetHitRadius = 2_200;
}
