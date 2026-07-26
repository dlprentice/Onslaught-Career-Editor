// SPDX-License-Identifier: GPL-3.0-or-later

namespace OnslaughtRebuild.Core;

public static class SimulationConstants
{
    public const int TicksPerSecond = 30;
    // Retail's simulation tick is CLOCK_TICK 0.05 s
    // (references/Onslaught/thing.h:29; eventmanager.cpp:296 advances
    // mTime = mFrameCount * CLOCK_TICK). Constants recovered from shipped bytes
    // are naturally expressed per RETAIL tick; this pair is the single place
    // that converts one to a Core tick. When Core moves to 20 Hz the ratio
    // becomes 1/1 and every "PerRetailTick" constant transfers unchanged, with
    // no other edit. Do not reintroduce bare 30s anywhere.
    public const int RetailTicksPerSecond = 20;
    public const int RetailTicksPerCoreTickNumerator = RetailTicksPerSecond;
    public const int RetailTicksPerCoreTickDenominator = TicksPerSecond;
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
    // RESOLVED 2026-07-26 in favour of "Aquila Prototype" -- see the byte
    // decode and the Twin Vulcan walker-list argument recorded on
    // JetMinimumEnergyDrainMicroPerRetailTick below. The jet speed envelope
    // itself is unaffected by the resolution: mMinAirVelocity 0.3 and
    // mMaxAirVelocity 0.9 are byte-identical in the Aquila Prototype and
    // Blaster records (and in Standard, Sniper and Laser), so the two
    // constants immediately below are correct either way. Only
    // mMaxAirEnergyCost (0.012 vs 0.010), mLife (20.0 vs 25.0) and
    // mGroundVelocity (5.0 vs 4.5) actually differ.
    //
    // Retained for the record, the original dispute note:
    //
    // DISPUTED 2026-07-25 - these values are derived from the Blaster record and
    // the premise behind that choice does not survive checking. The comment here
    // used to read: Level 100 names "Paladin Prototype", which is absent from the
    // shipped table, so the GetConfiguration(0) fallback is the final shipped
    // record, Blaster.
    //
    // Measured against the shipped data instead:
    //   - "Paladin Prototype" does not occur anywhere in
    //     data/battle engine configurations.dat (sha256 58722b12..., 1514 bytes,
    //     6 records). The level never declares that name.
    //   - The Level 100 LEVEL world (RLWD, id 100 - the one carrying the actors
    //     and compiled scripts) declares "Aquila Prototype". This repo's own
    //     materializer already asserts it and raises if absent
    //     (rebuild/tools/materialize_retail_assets.py:1339). The BASE world
    //     (BSWD, id 42) declares "Paladin Prototype" separately.
    //   - "Aquila Prototype" IS present in the shipped table, so there is no
    //     fallback to Blaster to make.
    //
    // If that holds, the maximum jet energy drain below is wrong: it comes
    // from Blaster's 0.01, where Aquila Prototype's 0.012 is the right value.
    // (That prediction was correct and has now been applied.)
    // Aquila Prototype's walker weapon set is also exactly
    // {Pulse Cannon Pod (primary), Mech Twin Vulcan Cannon}, which is what the
    // Level 100 script enables at beat 3 and matches the only two weapon icons
    // the level materializes. Under Blaster the walker has no Twin Vulcan at all.
    //
    // NOT changed here. The load-order step (UBattleEngineConfigurations::Load
    // calling ShutDown first, so the later level table wins) is inferred from the
    // reference source, not measured, and correcting these constants moves the
    // pinned smoke stateHash. That needs one runtime confirmation first - see
    // local-lab/LEVEL100-TUTORIAL-ASSESSMENT-2026-07-25.md.
    //
    // -- end of the retained 2026-07-25 note. The energy cost WAS corrected on
    // 2026-07-26 and, measured, it does not move the smoke stateHash at all:
    // that scenario never enters jet mode, so no air energy is ever spent.
    //
    // 0.3/0.9 retail-unit target velocities per retail tick, mapped to Core.
    // These are the mMinAirVelocity / mMaxAirVelocity bytes and are identical
    // in five of the six shipped records, Aquila Prototype included.
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
    // Written as seconds so the values are unchanged by a Core tick-rate move.
    // CBattleEngineJetPart::Turn/Pitch ramp yaw, pitch and roll input over
    // mTransformStartTime + 1.5 s; Move blends velocity onto the nose over
    // mTransformStartTime + 2.5 s and over mStrafingStartTime + 4.0 s.
    public const int JetInputRampTicks = 3 * TicksPerSecond / 2;
    public const int JetTransformAlignmentTicks = 5 * TicksPerSecond / 2;
    public const int JetStrafeAlignmentTicks = 4 * TicksPerSecond;
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
    // CBattleEngineJetPart::Move arms the ground morph at
    // mOnGround = time + 2.5 s, only considers it once
    // mTransformStartTime + BATTLE_ENGINE_TRANSFORM_TIME * 2 has elapsed
    // (BATTLE_ENGINE_TRANSFORM_TIME is 0.5 f, BattleEngine.h:43, so 1.0 s), and
    // morphs a stalled jet 2.5 s after the stall begins. Seconds-derived so a
    // Core tick-rate move leaves them meaning the same thing.
    public const int JetAutoLandDelayTicks = 5 * TicksPerSecond / 2;
    public const int JetAutoLandEligibilityTicks = 1 * TicksPerSecond;
    public const int JetStallSpeedPerTick = 100;
    public const int JetStallDelayTicks = 5 * TicksPerSecond / 2;
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
    // CBattleEngineJetPart::Move spends
    //   cost = (mMaxAirEnergyCost - mMinAirEnergyCost) * mThrusterValue
    //          + mMinAirEnergyCost
    // once per retail tick while airborne with energy.
    //
    // The two costs are shipped bytes. data/battle engine configurations.dat
    // (sha256 58722b12a04cae97ad2163acb2cc2c1699f95a0688318bd8a86696714d94454a,
    // 1,514 bytes) decodes with CBattleEngineData::Load's exact field order
    // (references/Onslaught/BattleEngineDataManager.cpp:148-430) consuming
    // 1,514 of 1,514 bytes, 6 records, every record version 12 ==
    // kCurrentBattleEngineDataFormat. Record 3, "Aquila Prototype" @0x2d2:
    //   mMinAirEnergyCost 0.005  (0x3BA3D70A)   mMaxAirEnergyCost 0.012 (0x3C449BA6)
    //   mMinAirVelocity   0.3    (0x3E99999A)   mMaxAirVelocity   0.9   (0x3F666666)
    //   mEnergy           8.0                   mMinTransformEnergy 1.0
    //
    // These were previously taken from record 5, "Blaster", whose max air cost
    // is 0.010 rather than 0.012. That reading is now settled against the
    // bytes: the released Level 100 LevelScript does
    // EnableWeapon("Mech Twin Vulcan Cannon") on the *walker*, and of the six
    // shipped records only Aquila Prototype carries walker weapons
    // ["Mech Twin Vulcan Cannon"] together with mPrimaryWeapon
    // "Pulse Cannon Pod" -- exactly the two weapons the tutorial enables and
    // the only two the level materializes. Blaster's walker list is
    // ["Blaster Pod","Mech Grenade Launcher"] and contains no Twin Vulcan at
    // all, so under Blaster beat 4 could not exist. The level's own RLWD
    // declaration of "Aquila Prototype" is already asserted by
    // rebuild/tools/materialize_retail_assets.py:1339.
    //
    // Stored in micro-retail-energy per RETAIL tick so the interpolation is
    // exact at half throttle and the value survives the Core tick change.
    public const int JetMinimumEnergyDrainMicroPerRetailTick = 5_000;
    public const int JetMaximumEnergyDrainMicroPerRetailTick = 12_000;
    // Energy uses the accepted milli-retail policy (1000 Core units == one
    // retail energy unit), so one Core energy unit is 1000 micro-retail.
    public const int MicroRetailEnergyPerCoreEnergyUnit = 1_000;
    public const int FireEnergyCost = 30;
    public const int FireCooldownTicks = 6;
    // Fresh copied-Steam Level 100 runs independently repeated four
    // lowest-charge Pulse Cannon rounds against each of the three training
    // tanks. Every round carried definition speed 35 and moved exactly 1.75
    // units per released 20 Hz update. Core's nearest 30 Hz integer
    // translation is 1.167 units per tick.
    public const int ProjectileSpeedPerTick = 1_167;
    public const int ProjectileLifetimeTicks = 40;
    // Mech Twin Vulcan Cannon, read out of data/default physics.dat
    // (sha256 e1fb3ded...b1a2321e1d6a9ba1542c74ada14, 175,603 bytes, 777
    // statements) with the value-id map established in
    // reverse-engineering/binary-analysis/physics-round-value-ids-2026-07-25.md
    // and independently re-parsed for this change:
    //   weapon     Mech Twin Vulcan Cannon @0x171b4
    //                CWeaponChargeLevel 0 -> mode "Mech Twin Vulcan Cannon"
    //                CWeaponConsumption 2.0   (Pulse Cannon Pod is 4.0)
    //   weaponmode Mech Twin Vulcan Cannon @0x13360
    //                CWeaponInaccuracy 0.006981317 rad, CWeaponReloadTime 0.05 s,
    //                CWeaponVolleySize 4, CWeaponRound "Mech Bullet",
    //                CWeaponPredictive 1, four CWeaponLaunchSequence entries
    //   round      Mech Bullet @0xa3f2
    //                CRoundVelocity 60.0, CRoundDamage 0.08, CRoundLifeSpan 1.0,
    //                CRoundExplosion "Mech Bullet Hit"; no CRoundRadius node
    //   explosion  Mech Bullet Hit @0x4373
    //                CExplosionRadius 0.2, CExplosionDamage 0.001
    // CRoundVelocity is units per second on the measured 20 Hz released tick
    // (the pulse's byte-read 35.0 divided by the measured 1.75 units per
    // update is exactly 20), so 60.0 u/s is 2.0 units per 30 Hz Core tick and
    // the 1.0 s lifespan is 30 Core ticks.
    public const int MechBulletSpeedPerTick = 2_000;
    public const int MechBulletLifetimeTicks = 1 * TicksPerSecond;
    public const int TwinVulcanVolleySize = 4;
    // 0.05 s reload expressed exactly. One 30 Hz Core tick is 100/3 ms, so
    // counting in thirds of a millisecond makes both the tick and the reload
    // integral and keeps the released 20 volleys per second exact rather than
    // rounding it to 15 or 30.
    public const int FireCooldownThirdMillisecondsPerTick = 100;
    public const int TwinVulcanReloadThirdMilliseconds = 150;
    // CWeaponConsumption is 2.0 for the Twin Vulcan against 4.0 for the Pulse
    // Cannon Pod. The absolute Core cost of a pulse shot (FireEnergyCost) is
    // not dual-accepted retail truth, so only the byte-read 2.0/4.0 ratio is
    // carried across.
    public const int TwinVulcanFireEnergyCost = FireEnergyCost / 2;
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
    // Target Drone Unit field 3 CUnitLife 1.0 (0x3F800000).
    public const int Level100TargetDroneLife = 1_000;
    // Air Trainer Unit field 3 CUnitLife 3.0 (0x40400000).
    public const int Level100AirTrainerLife = 3_000;

    // ---------------------------------------------------------------------
    // Plane (behaviour class 9) motion.
    //
    // Every value below is a shipped byte. `data/default physics.dat`
    // (sha256 e1fb3ded...ada14, 175,603 bytes, 777 statements):
    //
    //   Unit  Target Drone @0x24e76 (name string @0x24e7e)
    //           [39] CUnitBasedOn        "Base Air Unit"
    //           [ 8] CUnitBehaviour      9
    //           [ 2] CUnitAirVelocity    5.5   (0x40B00000)
    //           [ 6] CUnitAirTurnRate    0.04363323 rad (0x3D32B8C2)
    //           [ 3] CUnitLife           1.0   (0x3F800000)
    //           [22] CUnitStrafeChange   0.01  (0x3C23D70A)
    //           [23] CUnitMaxTargetRange 500.0 (0x43FA0000)
    //   Unit  Air Trainer  @0x1e198 (name string @0x1e1a0)
    //           [ 2] CUnitAirVelocity    9.2   (0x41133333)
    //           [ 6] CUnitAirTurnRate    0.04363323 rad (0x3D32B8C2)
    //           [ 3] CUnitLife           3.0   (0x40400000)
    //           [23] CUnitMaxTargetRange 300.0 (0x43960000)
    //
    // The value-id -> class map is
    // reverse-engineering/binary-analysis/physics-round-value-ids-2026-07-25.md;
    // ids 2/6 write unit-record +0xb4/+0xb8, exactly the slots the ground ids
    // 1/5 write, which is why the air unit reuses the ground guide's turn law
    // with its own field.
    //
    // These are NOT carried on `Level100ActorMotionDefinition` because that
    // record reaches Core through
    // rebuild/OnslaughtRebuild.Client/Level100ActorDefinitionManifest.cs:142,
    // an eleven-argument positional construction in a tree this work does not
    // own, and InteractiveSessionTests.cs:730-741 pins every non-GroundVehicle
    // motion scalar to null. `materialize_retail_assets.py`
    // `_level100_actor_motion_definitions` asserts these exact bits on every
    // run, so the two cannot drift apart silently.
    //
    // Speed unit: the air guide (CAirGuide vtable 0x005d8594 slot 3 =
    // 0x00402280) sets mVelocity (unit +0x14c) to
    // `GetMaxVelocity() * 0.05 * 4.0` along the facing axis, where 0.05 is
    // 1/GAME_FR at the measured 20 Hz released tick (DAT_005d8584) and 4.0 is
    // DAT_005d85bc. The already-tested ground reconstruction moves at
    // CUnitGroundVelocity units per second, and the ground guide
    // (CGroundVehicleGuide__VFunc03 @0x0047d750) is the same virtual with the
    // same two factors, so the net rate is the record value in units per
    // second and the 4.0 is the full-move cadence, not a speed multiplier.
    public const int Level100TargetDroneAirSpeedMillimetersPerSecond = 5_500;
    public const int Level100AirTrainerAirSpeedMillimetersPerSecond = 9_200;
    public const int Level100PlaneAirTurnRateFloatBits = 0x3D32B8C2;

    // Air-guide altitude band, read out of the pristine BEA.exe
    // (sha256 74154bfa...7750). CAirGuide__UpdateGroundClearanceCache
    // (0x004028e0) caches the MINIMUM height above terrain over the owner's
    // rounded x/y +/-20 units sampled in steps of 5 - a 41x41 unit box, 81
    // samples - and 0x00402280 then commands pitch from it:
    //   0x0040240d  clearance <  5.0  (DAT_005d85d8) -> pitch = -pi/4  (climb)
    //   0x00402427  clearance < 15.0  (DAT_005d85d4) -> level out a descent
    //   0x00402452  clearance > 50.0  (DAT_005d85d0) -> pitch = +pi/4  (dive)
    // Retail Z is down, so the negative command is the climb; Core Y is up, so
    // the sign is inverted at the point of use and the comment there says so.
    public const int Level100PlaneClearanceSampleRadiusMillimeters = 20_000;
    public const int Level100PlaneClearanceSampleStepMillimeters = 5_000;
    public const int Level100PlaneClimbClearanceMillimeters = 5_000;
    public const int Level100PlaneLevelClearanceMillimeters = 15_000;
    public const int Level100PlaneDiveClearanceMillimeters = 50_000;
    // DAT_005d85dc/e4 = +/-pi/4 (0x3F490FDB), the clearance-band pitch command.
    public const int Level100PlaneClearancePitchMicroRadians = 785_398;
    // 0x3F860A92 = 1.0471976 rad, the +/-60 degree pitch command taken toward
    // an active attack target's altitude at 0x004023ea.
    public const int Level100PlaneTargetPitchMicroRadians = 1_047_198;
    // The map-edge turn-back at 0x0040246a: DAT_005d85cc = 10.0 and
    // DAT_005d85c4 = 502.0 against the 512-unit map extent.
    public const int Level100PlaneMapEdgeMarginMillimeters = 10_000;
}
