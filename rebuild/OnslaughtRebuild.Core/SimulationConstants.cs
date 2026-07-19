// SPDX-License-Identifier: GPL-3.0-or-later

namespace OnslaughtRebuild.Core;

public static class SimulationConstants
{
    public const int TicksPerSecond = 30;
    // 100_res_PC.aya WRES/WRLD placement data, translated so the released
    // player-one start (288.6875, 243.25) is Core origin. Half-milli values
    // use midpoint-away-from-zero rounding in the integer simulation.
    public static readonly SimVector2 Level100TargetZone1Position = new(-43_188, 33_500);
    public static readonly SimVector2 Level100FiringRangePosition = new(-69_688, 72_750);
    public const int Level100PlayerStartYawMicroRad = 509_830;
    public const int Level100ObjectiveTriggerRadius = 5_000;
    // Two fresh app-owned Steam Level 100 runs repeated a six-second opening
    // pan. Retail remains in GAME_STATE_PANNING until the full interval ends,
    // so player actions are rejected for the first 180 Core ticks.
    public const int Level100OpeningPanTicks = 6 * TicksPerSecond;
    // Three fresh uninterrupted copied-Steam runs observed the first Level 100
    // message sequence. Retail installs the pan at game time 3.0, so these are
    // 30 Hz ticks relative to that same opening-pan origin, rounded to the
    // nearest Core boundary. The explicit gaps are the retail message queue's
    // approximately 0.2-second handoffs.
    public const int Level100Hud01StartTick = 182;
    public const int Level100Hud01EndTick = 351;
    public const int Level100Hud02StartTick = 357;
    public const int Level100Hud02EndTick = 567;
    public const int Level100Hud06StartTick = 573;
    public const int Level100Hud06EndTick = 756;
    public const int Level100MessageLogStartTick = 762;
    public const int Level100MessageLogEndTick = 926;
    public const int Level100TechnicianStartTick = 932;
    public const int Level100TechnicianEndTick = 998;
    public const int Level100PowerActivationTick = 1_000;
    public const int Level100MovementInstructionStartTick = 1_004;
    public const int Level100MovementInstructionEndTick = 1_220;
    public const int Level100TargetZone1ActivationTick = 1_223;
    public const int Level100TargetZone1InstructionStartTick = 1_226;
    public const int Level100TargetZone1InstructionEndTick = 1_387;
    public const int Level100ScannerInstructionStartTick = 1_393;
    public const int Level100ScannerInstructionEndTick = 1_530;
    // TargetZone1.msl and FiringRange.msl each pause 0.5 seconds before
    // posting their event. Fifteen fixed Core ticks preserve that delay.
    public const int Level100ObjectiveDispatchTicks = 15;
    // Level 100 copied-retail runs repeated a 20 Hz walker response of
    // 0 -> 0.07 -> 0.119 -> 0.15 units/update, followed by exact 0.7 coast.
    // The 30 Hz Core retains the measured time constant and 3.0 units/s cap.
    public const int WalkerAccelerationPerTick = 33;
    public const int WalkerVelocityRetentionNumerator = 7_884;
    public const int WalkerVelocityRetentionDenominator = 10_000;
    public const int WalkerMaximumSpeedPerTick = 100;
    // Milli-retail units/tick at 30 Hz ≈ 11.43 retail units/s (pair jet-p06
    // envelope [10.860, 12.003]). Policy:
    // reverse-engineering/game-mechanics/jet-forward-retail-to-core-translation-policy.md
    // Schema: battleengine-jet-forward-scalar-response.v1
    public const int JetSpeedPerTick = 381;
    // Retail body yaw integrates its velocity and retains exactly 0.8 each
    // 50 ms update. These are the time-equivalent 30 Hz coefficients; the
    // velocity is kept in integer micro-radians to preserve the coast.
    public const int WalkerYawInputMicroRadPerTick = 10_444;
    public const int WalkerYawRetentionNumerator = 861_774;
    public const int WalkerYawRetentionDenominator = 1_000_000;
    public const int MaximumEnergy = 1_000;
    public const int MaximumShield = 1_000;
    public const int MaximumHull = 1_000;
    public const int TransformEnergyThreshold = 200;
    public const int TransformEnergyCost = 120;
    // Two fresh copied-retail Level 100 runs held raw BattleEngine state 1
    // for 535.359-537.249 ms before state 3. Sixteen 30 Hz Core intervals
    // are 533.333 ms and preserve those exact state-transition endpoints.
    public const int WalkerToJetTransitionTicks = 16;
    // Still synthetic for the unmeasured jet-to-walker/empty-energy paths.
    public const int TransformDurationTicks = 15;
    // Walker regen still provisional (no dual-accept yet).
    public const int WalkerEnergyRegenerationPerTick = 4;
    public const int WalkerShieldRegenerationPerTick = 2;
    // Milli-energy units/tick at 30 Hz ≈ 0.51 retail energy units/s drain
    // (pair energy-p02 envelope |r| ∈ [0.471, 0.562]). Policy:
    // reverse-engineering/game-mechanics/jet-energy-drain-retail-to-core-translation-policy.md
    // Schema: battleengine-jet-energy-drain-scalar-response.v1
    public const int JetEnergyDrainPerTick = 17;
    public const int FireEnergyCost = 30;
    public const int FireCooldownTicks = 6;
    public const int ProjectileSpeedPerTick = 1_200;
    public const int ProjectileLifetimeTicks = 40;
    public const int ProjectileDamage = 250;
    public const int TargetHull = 1_000;
    public const int TargetHitRadius = 2_200;
}
