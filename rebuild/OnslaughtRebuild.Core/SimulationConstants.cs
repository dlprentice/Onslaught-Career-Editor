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
    // Three fresh copied-retail runs read the exact four CThing pointers added
    // to Steam's objective set by "Activate Static Targets". Coordinates are
    // relative to the authored player start and rounded to integer millimetres.
    public static readonly SimVector2 Level100TargetTank1Position = new(-67_764, 78_283);
    public static readonly SimVector2 Level100TargetTank2Position = new(-78_750, 80_063);
    public static readonly SimVector2 Level100TargetTank3Position = new(-71_875, 84_688);
    public static readonly SimVector2 Level100TargetWarehousePosition = new(-86_313, 83_563);
    // Two uninterrupted repetitions per facility drove the released walker
    // into the same Level 100 structure with fixed body yaw. Steam removed the
    // inward velocity and retained tangent motion (ECR_SLIDE). These are the
    // observed centre-to-centre contact envelopes, including the 0.4-unit
    // single-player BattleEngine radius; they are not general building bounds.
    public static readonly SimVector2 Level100ControlTowerPosition = new(-13_290, 5_603);
    public const int Level100ControlTowerContactRadius = 2_574;
    public static readonly SimVector2 Level100TankFactoryPosition = new(10_125, 22_375);
    public const int Level100TankFactoryContactRadius = 8_434;
    public const int Level100PlayerStartYawMicroRad = 509_830;
    // Each authored trigger has radius 5.0. Steam CBattleEngine::GetRadius at
    // vtable slot 16 (0x0040DF80) returns 0.4 in single player, and two fresh
    // copied-runtime runs changed objective state only after those spheres
    // overlapped. Core stores the resulting 5.4-unit centre threshold.
    public const int Level100ObjectiveTriggerRadius = 5_400;
    // Two fresh app-owned Steam Level 100 runs repeated a six-second opening
    // pan. Retail remains in GAME_STATE_PANNING until the full interval ends,
    // so player actions are rejected for the first 180 Core ticks.
    public const int Level100OpeningPanTicks = 6 * TicksPerSecond;
    // Level 100 copied-retail runs repeated a 20 Hz walker response of
    // 0 -> 0.07 -> 0.119 -> 0.15 units/update, followed by exact 0.7 coast.
    // The 30 Hz Core retains the measured time constant and 3.0 units/s cap.
    public const int WalkerAccelerationPerTick = 33;
    public const int WalkerVelocityRetentionNumerator = 7_884;
    public const int WalkerVelocityRetentionDenominator = 10_000;
    public const int WalkerMaximumSpeedPerTick = 100;
    // Canonical Steam CMCMech state at the authored Level 100 start supplies
    // these four body-local Footbase offsets in the released controller order:
    // front-left, front-right, rear-left, rear-right. Two uninterrupted slope
    // traversals repeated the same planted endpoints. The controller advances
    // each swing at 400 phase units/second through phase 180, lifts the foot
    // 0.4 units, uses a 1.0-unit moving threshold (0.05 while stationary), and
    // permits at most two legs in the first half of a normal swing.
    public static IReadOnlyList<SimVector2> WalkerFootStanceOffsetsMillimeters { get; } =
        Array.AsReadOnly<SimVector2>(
        [
            new(-957, 1_078),
            new(937, 1_089),
            new(-882, -1_527),
            new(937, -1_505),
        ]);
    public const int WalkerFootMovingThresholdMillimeters = 1_000;
    public const int WalkerFootStationaryThresholdMillimeters = 50;
    public const int WalkerFootLiftMillimeters = 400;
    public const int WalkerFootPhaseEnd = 180;
    public const int WalkerFootPhaseUnitsPerSecond = 400;
    public const int WalkerFootMaximumEarlySwings = 2;
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
    // Steam injects 1/117 rad at 20 Hz and retains exactly 0.8 after each
    // update. This is the time-equivalent 30 Hz input; pitch uses the same
    // measured retention as yaw. Two uninterrupted Level 100 repetitions at
    // the authored start stabilized at these absolute opening-slope bounds.
    public const int WalkerPitchInputMicroRadPerTick = 3_938;
    public const int WalkerPitchRetentionNumerator = WalkerYawRetentionNumerator;
    public const int WalkerPitchRetentionDenominator = WalkerYawRetentionDenominator;
    public const int WalkerPitchUpLimitMicroRad = -1_091_250;
    public const int WalkerPitchDownLimitMicroRad = 532_123;
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
    // Fresh copied-Steam Level 100 runs independently repeated four
    // lowest-charge Pulse Cannon rounds against each of the three training
    // tanks. Every round carried definition speed 35 and moved exactly 1.75
    // units per released 20 Hz update. Core's nearest 30 Hz integer
    // translation is 1.167 units per tick.
    public const int ProjectileSpeedPerTick = 1_167;
    public const int ProjectileLifetimeTicks = 40;
    // A same-return capture of Steam CBattleEngine::GetLaunchPosition resolved
    // cockpit emitter "Gun" index 1 relative to the live BattleEngine basis.
    // Values are rounded to deterministic integer millimetres.
    public const int PulseCannonEmitterRightMillimeters = -6;
    public const int PulseCannonEmitterForwardMillimeters = 80;
    public const int PulseCannonEmitterUpMillimeters = 259;
    // Each authored training tank starts at retail life 6. Direct mesh impacts
    // repeatedly removed 1.8; one glancing mesh-part impact removed 1.0. Core
    // does not yet model the retail mesh-part multiplier, so this bounded
    // three-tank path represents full hits and retains milli-life precision.
    public const int Level100TargetTankLife = 6_000;
    // Two fresh uninterrupted copied-Steam repetitions removed the Warehouse
    // objective after exactly twelve lowest-charge shots along one fixed
    // center-aim attack line. This 12 * 1.8 envelope is not general Warehouse
    // health and does not reproduce the retail controller's 28 segments or its
    // other impact-point-dependent destruction paths.
    public const int Level100TargetWarehouseCenterAimDamageEnvelope = 21_600;
    public const int Level100PulseCannonFullHitDamage = 1_800;
    // Radius bounds the retained target-tank mesh in its horizontal plane
    // (maximum source-vertex radius 1.447 units, rounded outward).
    public const int Level100TargetTankHitRadius = 1_450;
    // Exact retained Warehouse OBJ horizontal vertex bound: 8.239447 units,
    // rounded outward. This bounds only the demonstrated direct-hit path.
    public const int Level100TargetWarehouseHorizontalBound = 8_240;
}
