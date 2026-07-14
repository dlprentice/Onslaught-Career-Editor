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
    public const int MaximumEnergy = 1_000;
    public const int MaximumShield = 1_000;
    public const int MaximumHull = 1_000;
    public const int TransformEnergyThreshold = 200;
    public const int TransformEnergyCost = 120;
    public const int TransformDurationTicks = 15;
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
