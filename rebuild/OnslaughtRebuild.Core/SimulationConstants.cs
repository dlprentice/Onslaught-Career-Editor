// SPDX-License-Identifier: GPL-3.0-or-later

namespace OnslaughtRebuild.Core;

public static class SimulationConstants
{
    public const int TicksPerSecond = 30;
    public const int ArenaHalfExtent = 30_000;
    public const int WalkerSpeedPerTick = 350;
    public const int JetSpeedPerTick = 650;
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
