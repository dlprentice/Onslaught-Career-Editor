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
    // Level 100 names "Paladin Prototype", which is absent from the shipped
    // table. UBattleEngineDataManager::Load prepends each record, so the
    // GetConfiguration(0) fallback is the final shipped record, Blaster.
    // Its 0.3/0.9 retail-unit 20 Hz target velocities map to 30 Hz here.
    public const int JetMinimumSpeedPerTick = 200;
    public const int JetMaximumSpeedPerTick = 600;
    public const int JetTargetCorrectionNumerator = 27_031;
    public const int JetTargetCorrectionDenominator = 1_000_000;
    // CBattleEngineJetPart::YawLeft/YawRight add body-local vx / 300 once per
    // released 20 Hz update. Mapping that acceleration to the 30 Hz Core's
    // milli-world-unit velocity gives 40/27 per full-input tick.
    public const int JetStrafeAccelerationNumerator = 40;
    public const int JetStrafeAccelerationDenominator = 27;
    public const int JetYawInputMicroRadPerTick = 9_805;
    public const int JetPitchInputMicroRadPerTick = WalkerPitchInputMicroRadPerTick;
    public const int JetRollInputMicroRadPerTick = WalkerPitchInputMicroRadPerTick;
    public const int JetInputRampTicks = 45;
    public const int JetTransformAlignmentTicks = 75;
    public const int JetStrafeAlignmentTicks = 120;
    public const int JetPitchSoftLimitMicroRad = 1_170_000;
    public const int JetRollAutoLevelNumerator = 979_899;
    public const int JetRollAutoLevelDenominator = 1_000_000;
    public const int JetNearSurfaceFrictionNumerator = 993_322;
    public const int JetCruiseFrictionNumerator = 986_576;
    public const int JetLowAltitudeFrictionNumerator = 979_899;
    public const int JetFrictionDenominator = 1_000_000;
    public const int JetGroundedRetentionNumerator = 966_382;
    public const int JetGroundedForwardCouplingNumerator = 31_951;
    public const int JetGroundedResponseDenominator = 1_000_000;
    public const int JetDescendingGroundEffectRetentionNumerator = 932_170;
    public const int JetDescendingGroundEffectRetentionDenominator = 1_000_000;
    public const int JetGroundFollowNumerator = 9_215;
    public const int JetGroundFollowDenominator = 1_000_000;
    public const int JetSkimRetentionNumerator = WalkerYawRetentionNumerator;
    public const int JetSkimRetentionDenominator = WalkerYawRetentionDenominator;
    public const int JetGroundEffectHeightMillimeters = 5_000;
    public const int JetSkimHeightMillimeters = 500;
    public const int JetSkimMinimumHorizontalSpeedPerTick = 200;
    // One retail world-unit per released 20 Hz update expressed as a 30 Hz
    // Core speed. This conversion scale is independent of Blaster's 0.9 target.
    public const int RetailVelocityUnitPerUpdateAsCoreSpeed = 667;
    public const int JetGroundedSlowSpeedPerTick = 67;
    public const int JetAutoLandSpeedPerTick = 17;
    public const int JetAutoLandDelayTicks = 75;
    public const int JetAutoLandEligibilityTicks = 30;
    public const int JetStallSpeedPerTick = 100;
    public const int JetStallDelayTicks = 75;
    public const int JetGravityPerTick = 2;
    public const int WalkerGravityPerTick = 4;
    public const int MorphIntoWalkerGravityPerTick = 1;
    // Grounded walk-to-fly injects 0.7 retail velocity once. Converting its
    // released 20 Hz velocity unit to Core's 30 Hz step gives 467 mm/tick.
    public const int WalkerToJetLiftImpulsePerTick = 467;
    public const int WalkerVerticalRetentionNumerator = 788_374;
    public const int WalkerVerticalRetentionDenominator = 1_000_000;
    // Held walker landing jets add -2.5% horizontal velocity and -7.5%
    // downward velocity per released 20 Hz update. These are the equivalent
    // 30 Hz retention factors; the action has no energy cost.
    public const int WalkerLandingJetHorizontalRetentionNumerator = 983_263;
    public const int WalkerLandingJetVerticalRetentionNumerator = 949_353;
    public const int WalkerLandingJetRetentionDenominator = 1_000_000;
    public const int WalkerLandingJetMinimumDescentPerTick = 7;
    public const int WalkerToJetPitchInputMicroRadPerTick = 6_911;
    public const int WalkerToJetAirborneTransitionTicks = 3;
    public const int RecentGroundContactTicks = 18;
    public const int Level100MaximumElevationMillimeters = 140_000;
    public const int Level100MapEdgeSlowdownMillimeters = 20_000;
    public const int Level100SteepSlopeGradientSquaredThreshold = 704_088;
    // CBattleEngine::DeclareOnGround uses 0.2 outside pure walker state and
    // 0.4 in walker state. These are the corresponding 30 Hz velocities.
    public const int JetGroundImpactThresholdPerTick = 133;
    public const int WalkerGroundImpactThresholdPerTick = 267;
    // DeclareInWater starts the failure path once the centre is within 0.2
    // retail units of the water plane.
    public const int WaterFailureClearanceMillimeters = 200;
    public const int WalkerTerrainPitchCorrectionNumerator = 13_823;
    public const int WalkerTerrainPitchCorrectionDenominator = 1_000_000;
    // Retail body yaw integrates its velocity and retains exactly 0.8 each
    // 50 ms update. These are the time-equivalent 30 Hz coefficients; the
    // velocity is kept in integer micro-radians to preserve the coast.
    public const int WalkerYawInputMicroRadPerTick = 10_444;
    public const int WalkerYawRetentionNumerator = 861_774;
    public const int WalkerYawRetentionDenominator = 1_000_000;
    // Steam injects 1/117 rad at 20 Hz and retains exactly 0.8 after each
    // update. This is the time-equivalent 30 Hz input; pitch uses the same
    // measured retention as yaw. Source/static terrain-relative soft limits
    // replace the earlier start-slope-only absolute clamps.
    public const int WalkerPitchInputMicroRadPerTick = 3_938;
    public const int WalkerPitchRetentionNumerator = WalkerYawRetentionNumerator;
    public const int WalkerPitchRetentionDenominator = WalkerYawRetentionDenominator;
    // Two uninterrupted copied-retail repetitions at the authored Level 100
    // start stabilized at these absolute endpoints. They remain evidence
    // anchors while the source-derived terrain-relative limiter is used; they
    // are not reapplied as global clamps on every slope.
    public const int ObservedWalkerPitchUpLimitAtLevel100StartMicroRad = -1_091_250;
    public const int ObservedWalkerPitchDownLimitAtLevel100StartMicroRad = 532_123;
    // Energy uses the accepted milli-retail policy: 1000 Core units equal one
    // retail energy unit. Blaster stores eight energy units and requires one
    // to begin walker-to-jet morphing.
    public const int MaximumEnergy = 8_000;
    // The released WalkerPart assigns shields from the same energy store on
    // every non-jet update. This alias preserves the public snapshot field
    // without inventing a second capacity or regeneration curve.
    public const int MaximumShield = MaximumEnergy;
    public const int MaximumHull = 1_000;
    // Morph itself does not spend energy, and jet-to-walker has no energy gate.
    public const int TransformEnergyThreshold = 1_000;
    // Two fresh copied-retail Level 100 runs held raw BattleEngine state 1
    // for 535.359-537.249 ms before state 3. Sixteen 30 Hz Core intervals
    // are 533.333 ms and preserve those exact state-transition endpoints.
    public const int WalkerToJetTransitionTicks = 16;
    public const int JetToWalkerTransitionTicks = 15;
    // Walker regen still provisional (no dual-accept yet).
    public const int WalkerEnergyRegenerationPerTick = 4;
    // Level 100 falls back to Blaster, whose shipped minimum/maximum air costs
    // are .005/.01 retail energy per 20 Hz update. Under the accepted
    // milli-retail energy scale, their exact 30 Hz equivalents are 10/3 and
    // 20/3 Core units per tick. The accumulator interpolates between them by
    // throttle without discarding the fractional thirds.
    public const int JetMinimumEnergyDrainThirdsPerTick = 10;
    public const int JetMaximumEnergyDrainThirdsPerTick = 20;
    public const int JetEnergyDrainFractionDenominator = 3;
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
    // The released definitions retain life in float units. Registry health
    // carries the same values in milli-life while the contact owner applies
    // exact 1.8 medium-pulse damage to the contacted part.
    public const int Level100TargetTankLife = 6_000;
    // Target Truck Unit field 3 is the released maximum-life owner. Its
    // separate motion definition retains field 1 as ground maximum speed.
    public const int Level100TrainingTruckLife = 3_000;
    public const int Level100TargetWarehouseLife = 50_000;
}
