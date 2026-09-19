# SPDX-License-Identifier: GPL-3.0-or-later
extends RefCounted
## Faithful reconstruction constants, ported from SimulationConstants.cs.
## Original provenance and unresolved qualifications remain beside each value.
## These are immutable simulation definitions, not Inspector overrides.

# CLOCK_TICK 0.05 s / GAME_FR 20.0 (references/Onslaught/thing.h:28-29;
# eventmanager.cpp:296 advances mTime = mFrameCount * CLOCK_TICK), and
# eventmanager.cpp:210-212 FLOORS every scheduled delay onto a whole 20 Hz
# boundary (`delay *= GAME_FR; delay = floorf(delay)`). A Core running at
# any other rate cannot land those boundaries at all.
#
# This was 30 until the 20 Hz migration. Every constant below that carries
# a per-tick magnitude moved with it, under four distinct rules, and the
# conversion recovered the verbatim shipped value for most of them - see
# the individual comments. The single clearest example is the landing
# thruster: 983_263/1_000_000 was 0.975^(2/3), an artefact of running at a
# rate the game did not; at 20 Hz it is retail's 0.975 exactly.
const TICKS_PER_SECOND: int = 20
# Constants recovered from shipped bytes are naturally expressed per RETAIL
# tick; this pair is the single place that converts one to a Core tick.
# Core is now AT the retail rate, so the ratio is 1/1 and every
# "PerRetailTick" constant transfers unchanged. The pair is retained rather
# than deleted because it names the invariant: a constant read out of a
# shipped byte is per retail tick, and the day Core moves off 20 Hz again
# this is still the only place that has to change.
const RETAIL_TICKS_PER_SECOND: int = 20
const RETAIL_TICKS_PER_CORE_TICK_NUMERATOR: int = RETAIL_TICKS_PER_SECOND
const RETAIL_TICKS_PER_CORE_TICK_DENOMINATOR: int = TICKS_PER_SECOND
# 100_res_PC.aya WRES/WRLD placement data, translated so the released
# player-one start (288.6875, 243.25) is Core origin. Half-milli values
# use midpoint-away-from-zero rounding in the integer simulation.
const LEVEL100_TARGET_ZONE1_POSITION: Dictionary = {"x": -43_188, "z": 33_500}
const LEVEL100_FIRING_RANGE_POSITION: Dictionary = {"x": -69_688, "z": 72_750}
# Three fresh copied-retail runs read the exact four CThing pointers added
# to Steam's objective set by "Activate Static Targets". Coordinates are
# relative to the authored player start and rounded to integer millimetres.
const LEVEL100_TARGET_TANK1_POSITION: Dictionary = {"x": -67_764, "z": 78_283}
const LEVEL100_TARGET_TANK2_POSITION: Dictionary = {"x": -78_750, "z": 80_063}
const LEVEL100_TARGET_TANK3_POSITION: Dictionary = {"x": -71_875, "z": 84_688}
const LEVEL100_TARGET_WAREHOUSE_POSITION: Dictionary = {"x": -86_313, "z": 83_563}
# Two uninterrupted repetitions per facility drove the released walker
# into the same Level 100 structure with fixed body yaw. Steam removed the
# inward velocity and retained tangent motion (ECR_SLIDE). These are the
# observed centre-to-centre contact envelopes, including the 0.4-unit
# single-player BattleEngine radius; they are not general building bounds.
const LEVEL100_CONTROL_TOWER_POSITION: Dictionary = {"x": -13_290, "z": 5_603}
const LEVEL100_CONTROL_TOWER_CONTACT_RADIUS: int = 2_574
const LEVEL100_TANK_FACTORY_POSITION: Dictionary = {"x": 10_125, "z": 22_375}
const LEVEL100_TANK_FACTORY_CONTACT_RADIUS: int = 8_434
const LEVEL100_PLAYER_START_YAW_MICRO_RAD: int = 509_830
# Each authored trigger has radius 5.0. Steam CBattleEngine::GetRadius at
# vtable slot 16 (0x0040DF80) returns 0.4 in single player, and two fresh
# copied-runtime runs changed objective state only after those spheres
# overlapped. Core stores the resulting 5.4-unit centre threshold.
const LEVEL100_OBJECTIVE_TRIGGER_RADIUS: int = 5_400
# Two fresh app-owned Steam Level 100 runs repeated a six-second opening
# pan. Retail remains in GAME_STATE_PANNING until the full interval ends,
# so player actions are rejected for the first 120 Core ticks.
const LEVEL100_OPENING_PAN_TICKS: int = 6 * TICKS_PER_SECOND
# Level 100 copied-retail runs repeated a 20 Hz walker response of
# 0 -> 0.07 -> 0.119 -> 0.15 units/update, followed by exact 0.7 coast.
# Core is now at that same 20 Hz, so the measured sequence IS the
# recurrence: 70 mm added per tick into a store retained at
# mWalkFriction 0.7 (BattleEngineWalkerPart.cpp:412) gives
# 0 -> 70 -> 119 -> 153 -> ... -> 233 mm/tick, capped at
# mMaxWalkVelocity 0.15 = 150 mm/tick.
#
# CONVERSION RULE R3, not R1 or R4, and this row is why the distinction
# matters. 33 is an increment into a state that is damped by
# WalkerVelocityRetention on the same tick, so the factor is
# (1-r20)/(1-r30) * 1.5 = (0.3/0.2116) * 1.5 = 2.1264, giving 70.2.
# Scaling as a velocity (x1.5 -> 50) or as a free acceleration
# (x2.25 -> 74) would both give the wrong steady state.
const WALKER_ACCELERATION_PER_TICK: int = 70
# mWalkFriction 0.7 verbatim (BattleEngineWalkerPart.cpp:412,
# `SetVelocity(GetVelocity()*mWalkFriction)`). This was 7_884/10_000,
# i.e. 0.7^(2/3), the 30 Hz time-equivalent.
const WALKER_VELOCITY_RETENTION_NUMERATOR: int = 7_000
const WALKER_VELOCITY_RETENTION_DENOMINATOR: int = 10_000
# mMaxWalkVelocity 0.15 verbatim (BattleEngineWalkerPart.cpp:417).
const WALKER_MAXIMUM_SPEED_PER_TICK: int = 150
# BattleEngineWalkerPart.cpp:30-35,119-304,361-429. A hard input in one
# direction followed by its opposite within a strict 0.2-second window
# multiplies that opposite acceleration by 25 and locks movement input for
# 15 released updates. Core's current input seam is digital, so the exact
# 0.9/0.8 analog threshold behavior remains open while the shipped full-axis
# gesture and lifecycle are represented without floating-point state.
const WALKER_DASH_START_PERMILLE: int = 900
const WALKER_DASH_END_PERMILLE: int = 800
@warning_ignore("integer_division")
const WALKER_DASH_WINDOW_TICKS: int = TICKS_PER_SECOND / 5
const WALKER_DASH_LENGTH_TICKS: int = 15
const WALKER_DASH_FRICTION_THRESHOLD_TICKS: int = 5
const WALKER_DASH_ACCELERATION_MULTIPLIER: int = 25
const WALKER_DASH_ROLL_VELOCITY_MICRO_RAD_PER_TICK: int = 80_000
const WALKER_DASH_INITIAL_HISTORY_TICKS: int = 10 * TICKS_PER_SECOND
# BattleEngine.cpp:1871-1884. While grounded in Walker state, HandleSounds
# accumulates the full velocity magnitude, rolls once on strict >1.5,
# counts those rollovers, then plays `BE Hydraulics 02` on a later strict
# <0.01 stop only when the count is >5. Core velocity is millimetres per
# the same released 20 Hz tick, so this is a unit conversion only; there
# is no cadence scaling.
const WALKER_SOUND_TRAVEL_ROLLOVER_MILLIMETERS: int = 1_500
const WALKER_SOUND_STOPPED_SPEED_MILLIMETERS_PER_TICK: int = 10
const WALKER_SOUND_MINIMUM_ROLLOVER_COUNT: int = 5
# BattleEngine.cpp:3468-3498 and retail CBattleEngine::Damage at
# 0x0040A890. Damage(source) appends only while the list size is <15;
# ProcessDamageFlashes removes at most one entry per update after the
# strict start+2.0<now boundary. CDXCompass::Render at 0x00427210 uses the
# same 2.0-second age to drive the retained compass sprite to black.
const LEVEL100_DAMAGE_FLASH_CAPACITY: int = 15
const LEVEL100_DAMAGE_FLASH_LIFETIME_TICKS: int = 2 * TICKS_PER_SECOND
# Canonical Steam CMCMech state at the authored Level 100 start supplies
# these four body-local Footbase offsets in the released controller order:
# front-left, front-right, rear-left, rear-right. Two uninterrupted slope
# traversals repeated the same planted endpoints. The controller advances
# each swing at 400 phase units/second through phase 180, lifts the foot
# 0.4 units, uses a 1.0-unit moving threshold (0.05 while stationary), and
# permits at most two legs in the first half of a normal swing.
const WALKER_FOOT_STANCE_OFFSETS_MILLIMETERS: Array[Dictionary] = [
	{"x": -957, "z": 1_078},
	{"x": 937, "z": 1_089},
	{"x": -882, "z": -1_527},
	{"x": 937, "z": -1_505},
]
const WALKER_FOOT_MOVING_THRESHOLD_MILLIMETERS: int = 1_000
const WALKER_FOOT_STATIONARY_THRESHOLD_MILLIMETERS: int = 50
const WALKER_FOOT_LIFT_MILLIMETERS: int = 400
const WALKER_FOOT_PHASE_END: int = 180
const WALKER_FOOT_PHASE_UNITS_PER_SECOND: int = 400
const WALKER_FOOT_MAXIMUM_EARLY_SWINGS: int = 2
# RESOLVED 2026-07-26 in favour of "Aquila Prototype" -- see the byte
# decode and the Twin Vulcan walker-list argument recorded on
# JetMinimumEnergyDrainMicroPerRetailTick below. The jet speed envelope
# itself is unaffected by the resolution: mMinAirVelocity 0.3 and
# mMaxAirVelocity 0.9 are byte-identical in the Aquila Prototype and
# Blaster records (and in Standard, Sniper and Laser), so the two
# constants immediately below are correct either way. Only
# mMaxAirEnergyCost (0.012 vs 0.010), mLife (20.0 vs 25.0) and
# mGroundVelocity (5.0 vs 4.5) actually differ.
#
# Retained for the record, the original dispute note:
#
# DISPUTED 2026-07-25 - these values are derived from the Blaster record and
# the premise behind that choice does not survive checking. The comment here
# used to read: Level 100 names "Paladin Prototype", which is absent from the
# shipped table, so the GetConfiguration(0) fallback is the final shipped
# record, Blaster.
#
# Measured against the shipped data instead:
#   - "Paladin Prototype" does not occur anywhere in
#     data/battle engine configurations.dat (sha256 58722b12..., 1514 bytes,
#     6 records). The level never declares that name.
#   - The Level 100 LEVEL world (RLWD, id 100 - the one carrying the actors
#     and compiled scripts) declares "Aquila Prototype". This repo's own
#     materializer already asserts it and raises if absent
#     (rebuild/tools/materialize_retail_assets.py:1339). The BASE world
#     (BSWD, id 42) declares "Paladin Prototype" separately.
#   - "Aquila Prototype" IS present in the shipped table, so there is no
#     fallback to Blaster to make.
#
# If that holds, the maximum jet energy drain below is wrong: it comes
# from Blaster's 0.01, where Aquila Prototype's 0.012 is the right value.
# (That prediction was correct and has now been applied.)
# Aquila Prototype's walker weapon set is also exactly
# {Pulse Cannon Pod (primary), Mech Twin Vulcan Cannon}, which is what the
# Level 100 script enables at beat 3 and matches the only two weapon icons
# the level materializes. Under Blaster the walker has no Twin Vulcan at all.
#
# NOT changed here. The load-order step (UBattleEngineConfigurations::Load
# calling ShutDown first, so the later level table wins) is inferred from the
# reference source, not measured, and correcting these constants moves the
# pinned smoke stateHash. That needs one runtime confirmation first - see
# local-lab/LEVEL100-TUTORIAL-ASSESSMENT-2026-07-25.md.
#
# -- end of the retained 2026-07-25 note. The energy cost WAS corrected on
# 2026-07-26 and, measured, it does not move the smoke stateHash at all:
# that scenario never enters jet mode, so no air energy is ever spent.
#
# 0.3/0.9 retail-unit target velocities per retail tick, mapped to Core.
# These are the mMinAirVelocity / mMaxAirVelocity bytes and are identical
# in five of the six shipped records, Aquila Prototype included.
const JET_MINIMUM_SPEED_PER_TICK: int = 300
const JET_MAXIMUM_SPEED_PER_TICK: int = 900
# CBattleEngineJetPart::Move approaches the throttle's target speed by
# exactly one twenty-fifth of the shortfall per retail update
# (references/Onslaught/BattleEngineJetPart.cpp:379):
#
#     FVector move = mOrientation * FVector(0, (finalVel-velocity)/25.0f, 0);
#     mMainPart->AddVelocity(move);
#
# 1/25 = 0.04 exactly, so this is 40_000/1_000_000. The previous 27_031
# was NOT a conversion of that law - the exact 30 Hz form of 0.04 is
# 26_848, and 27_031 is 0.68 % away from it. It was fitted at 30 Hz. The
# shipped divisor wins.
const JET_TARGET_CORRECTION_NUMERATOR: int = 40_000
const JET_TARGET_CORRECTION_DENOMINATOR: int = 1_000_000
# CBattleEngineJetPart::YawLeft/YawRight add body-local vx / 300 once per
# released 20 Hz update, and a Core tick is now that update, so the
# milli-world-unit acceleration is 1000/300 = 10/3 per full-input tick.
const JET_STRAFE_ACCELERATION_NUMERATOR: int = 10
const JET_STRAFE_ACCELERATION_DENOMINATOR: int = 3
# CBattleEngineJetPart::Turn (BattleEngineJetPart.cpp:116) subtracts
#   yawRate = (vx * mAirTurnRate / 94.0f) * ZoomModifier(mZoom)
# from mYawvel once per retail update. `mAirTurnRate` is a shipped byte:
# record 3 "Aquila Prototype" @0x2F2 of data/battle engine
# configurations.dat (sha256
# 58722b12a04cae97ad2163acb2cc2c1699f95a0688318bd8a86696714d94454a,
# 1,514 bytes, decoded whole with CBattleEngineData::Load's field order,
# zero slack) reads 2.0 (0x40000000). ZoomModifier is the identity
# (BattleEngine.cpp:1913) and unzoomed mZoom is MAX_ZOOM_OUT 1.0.
# 2.0/94 = 0.0212766 rad = 21_277 micro-rad per retail tick.
#
# The previous 30 Hz value 9_805 converts (R3, x2.170337) to 21_280, three
# micro-radians from the byte - so this row was already correctly ported
# and only needed re-expressing. The shipped byte is used rather than the
# conversion.
const JET_YAW_INPUT_MICRO_RAD_PER_TICK: int = 21_277
const JET_PITCH_INPUT_MICRO_RAD_PER_TICK: int = WALKER_PITCH_INPUT_MICRO_RAD_PER_TICK
const JET_ROLL_INPUT_MICRO_RAD_PER_TICK: int = WALKER_PITCH_INPUT_MICRO_RAD_PER_TICK
# Written as seconds so the values are unchanged by a Core tick-rate move.
# CBattleEngineJetPart::Turn/Pitch ramp yaw, pitch and roll input over
# mTransformStartTime + 1.5 s; Move blends velocity onto the nose over
# mTransformStartTime + 2.5 s and over mStrafingStartTime + 4.0 s.
@warning_ignore("integer_division")
const JET_INPUT_RAMP_TICKS: int = 3 * TICKS_PER_SECOND / 2
@warning_ignore("integer_division")
const JET_TRANSFORM_ALIGNMENT_TICKS: int = 5 * TICKS_PER_SECOND / 2
const JET_STRAFE_ALIGNMENT_TICKS: int = 4 * TICKS_PER_SECOND
const JET_PITCH_SOFT_LIMIT_MICRO_RAD: int = 1_170_000
# Every retention below is now the SHIPPED FLOAT VERBATIM. Each was
# previously that float raised to the 2/3 power - the exact 30 Hz
# time-equivalent, and a pure tick-rate artefact. CONVERSION RULE R2
# (r20 = r30^1.5) recovers each one to six figures; the source value is
# used rather than the conversion.
#   BattleEngine.cpp:1219        mRoll *= 0.97f  (jet auto-level)
#   BattleEngineJetPart.cpp:622  return 0.99f    (altitude < 1)
#   BattleEngineJetPart.cpp:634  return 0.98f    (cruise)
#   BattleEngineJetPart.cpp:629  1.0f-(altitude*0.01f) floor, altitude < 3
const JET_ROLL_AUTO_LEVEL_NUMERATOR: int = 970_000
const JET_ROLL_AUTO_LEVEL_DENOMINATOR: int = 1_000_000
const JET_NEAR_SURFACE_FRICTION_NUMERATOR: int = 990_000
const JET_CRUISE_FRICTION_NUMERATOR: int = 980_000
const JET_LOW_ALTITUDE_FRICTION_NUMERATOR: int = 970_000
const JET_FRICTION_DENOMINATOR: int = 1_000_000
# The grounded jet, BattleEngineJetPart.cpp:413-419, is a COUPLED map and
# Core already implements it in the released order - retain, then add a
# fraction of the RETAINED magnitude along the nose:
#
#     FVector vel = mMainPart->GetVelocity()*0.95f;
#     mMainPart->SetVelocity(vel);
#     FVector new_vel_o = mOrientation * FVector(0, vel.Magnitude(), 0);
#     mMainPart->AddVelocity(new_vel_o*0.05f);
#
# At 20 Hz both halves are the shipped floats verbatim. Splitting a
# coupled map into two independently rate-converted factors was never
# exact, which is why the 30 Hz pair (966_382 / 31_951) was not simply
# 0.95^(2/3) and 0.05*(2/3). That approximation is now gone.
const JET_GROUNDED_RETENTION_NUMERATOR: int = 950_000
const JET_GROUNDED_FORWARD_COUPLING_NUMERATOR: int = 50_000
const JET_GROUNDED_RESPONSE_DENOMINATOR: int = 1_000_000
# BattleEngineJetPart.cpp:573 `mMainPart->mVelocity.Z *= 0.90f`.
const JET_DESCENDING_GROUND_EFFECT_RETENTION_NUMERATOR: int = 900_000
const JET_DESCENDING_GROUND_EFFECT_RETENTION_DENOMINATOR: int = 1_000_000
# BattleEngineJetPart.cpp:596,602 pitch/roll follow the ground normal by
# `(desired - current) * 0.02f * (1 - altitude/5)` per retail update. The
# 0.02 is verbatim; it was 9_215 at 30 Hz (R3, x2.170337 -> 20_000.0).
const JET_GROUND_FOLLOW_NUMERATOR: int = 20_000
const JET_GROUND_FOLLOW_DENOMINATOR: int = 1_000_000
const JET_SKIM_RETENTION_NUMERATOR: int = WALKER_YAW_RETENTION_NUMERATOR
const JET_SKIM_RETENTION_DENOMINATOR: int = WALKER_YAW_RETENTION_DENOMINATOR
const JET_GROUND_EFFECT_HEIGHT_MILLIMETERS: int = 5_000
# The divisor in BattleEngineJetPart.cpp:565's ground-effect lift,
# `(5-altitude)/400` per retail update. Named here because it used to be a
# bare 900 in a Simulation method body with nothing pointing at retail
# from the call site; 900 is 400 x 9/4, the 30 Hz free-acceleration factor.
const JET_GROUND_EFFECT_ACCELERATION_DIVISOR: int = 400

# The ground-effect sample point is HALF A SECOND of travel ahead, not half
# a tick. BattleEngineJetPart.cpp:548:
#
#     FVector pos = mMainPart->mPos + (mMainPart->mVelocity * GAME_FR * 0.5f);
#
# GAME_FR is 20.0f (thing.h:28) and mVelocity is per released UPDATE, not
# per second - actor.cpp computes its own limit as
# `GetMaxVelocity()/GAME_FR`, which only type-checks as a per-update
# quantity. So `mVelocity * GAME_FR` is units per SECOND and the 0.5f makes
# the lookahead half a second of travel.
#
# At 20 Hz that is 10 Core ticks of velocity - and, Core now being at the
# retail rate, those ARE the ten retail updates the 0.5 f buys. Core once
# used `velocity / 2` - half a Core tick - which was 30x too near.
# Measured consequence at cruise: retail samples 9,000 mm ahead and Core
# sampled 300 mm. Flying level at a rising slope, the released Aquila
# begins its lift and pitch-follow about fourteen ticks earlier; Core flew
# into the hill because it could not see it yet.
#
# This is a lookahead DISTANCE, so it scales with velocity and carries no
# tick-rate factor of its own beyond the half second.
@warning_ignore("integer_division")
const JET_GROUND_EFFECT_LOOKAHEAD_TICKS: int = TICKS_PER_SECOND / 2
const JET_SKIM_HEIGHT_MILLIMETERS: int = 500
const JET_SKIM_MINIMUM_HORIZONTAL_SPEED_PER_TICK: int = 300
# BattleEngineJetPart.cpp:536 `float damage=(0.5f-altitude)*20.0f`. The
# 20.0 is released life per released unit of depth below the 0.5 skim
# ceiling, applied once per released 20 Hz update.
const JET_WATER_SKIM_DAMAGE_PER_RELEASED_UNIT: int = 20
# BattleEngineJetPart.cpp:533 `mPitchvel -= 0.01f*magnitudeXY` per retail
# update, with magnitudeXY in retail units.
const JET_WATER_SKIM_PITCH_KICK_MICRO_RAD_PER_RETAIL_UNIT: int = 10_000

# Released AI states, from `data\MissionScripts\onsldef.msl` lines 2-6 -
# authored developer text, shipped with the game, and #included as a header
# by the developers' own source (Career.cpp:11, game.cpp:46). This is the
# strongest evidence class available for these values: it outranks anything
# recovered from disassembly.
#     AI_ON 0, AI_OFF 1, AI_NORMAL 2, AI_DEFENSIVE 3, AI_ONF 4
# Only AI_OFF is currently acted on; the rest are stored and carried but
# nothing distinguishes them yet.
const RELEASED_AI_STATE_ON: int = 0
const RELEASED_AI_STATE_OFF: int = 1
# One retail world unit in Core millimetres. Core once carried this as
# `RetailVelocityUnitPerUpdateAsCoreSpeed = 667` - one retail unit per
# released 20 Hz update expressed as a 30 Hz Core speed. Core is now AT
# the retail rate, so a retail unit per update is a Core millimetre count
# per tick with no rate factor at all, and the constant is just the length
# scale.
const MILLIMETERS_PER_RETAIL_UNIT: int = 1_000
# BattleEngineJetPart.cpp:423 `GetVelocity().MagnitudeSq() < 0.1f*0.1f`.
const JET_GROUNDED_SLOW_SPEED_PER_TICK: int = 100
# BattleEngineJetPart.cpp:432 `GetVelocity().MagnitudeSq() < 0.025f*0.025f`.
const JET_AUTO_LAND_SPEED_PER_TICK: int = 25
# CBattleEngineJetPart::Move arms the ground morph at
# mOnGround = time + 2.5 s, only considers it once
# mTransformStartTime + BATTLE_ENGINE_TRANSFORM_TIME * 2 has elapsed
# (BATTLE_ENGINE_TRANSFORM_TIME is 0.5 f, BattleEngine.h:43, so 1.0 s), and
# morphs a stalled jet 2.5 s after the stall begins. Seconds-derived so a
# Core tick-rate move leaves them meaning the same thing.
@warning_ignore("integer_division")
const JET_AUTO_LAND_DELAY_TICKS: int = 5 * TICKS_PER_SECOND / 2
const JET_AUTO_LAND_ELIGIBILITY_TICKS: int = 1 * TICKS_PER_SECOND
const JET_STALL_SPEED_PER_TICK: int = 150
@warning_ignore("integer_division")
const JET_STALL_DELAY_TICKS: int = 5 * TICKS_PER_SECOND / 2
# GRAVITY. Recovered 2026-07-31 for the 20 Hz migration; these three had no
# provenance at all before, having arrived without a comment at 18ddfc49.
# They are `CThing::Gravity()` and its two BattleEngine overrides, added to
# the vertical velocity once per retail update at
# references/Onslaught/BattleEngine.cpp:1577
# (`mVelocity.Z += Gravity();`) and integrated into position by
# actor.cpp:114 (`mPos += mVelocity;`):
#
#   thing.h:187                  virtual float Gravity() { return 0.01f; }
#   BattleEngine.cpp:1078-1084   WALKER              -> 0.01
#                                MORPHING_INTO_JET   -> 0.01
#                                MORPHING_INTO_WALKER-> 0.01 * 0.2 = 0.002
#                                JET                 -> mJetPart->Gravity()
#   BattleEngineJetPart.cpp:507  0.005f iff mEnergy == 0, else 0.0f
#
# Confirmed in the pristine specimen local-lab/safe-copy-bea-pristine/
# BEA.exe.original.backup, sha256 74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab
# 334ed7a753040eda1e1e7750: CThing__GravityDefault @0x004014b0 loads
# .rdata 0x005d8574 = 0.01f; CBattleEngine__Gravity @0x004074d0 loads
# 0x005d8bac = 0.002f for MORPHING_INTO_WALKER (the compiler folded
# 0.01*0.2 into its own literal, an independent confirmation);
# CBattleEngineJetPart__Gravity @0x004114d0 loads 0x005d8cb0 = 0.005f.
#
# Retail Z points down and adds; Core Y points up and subtracts.
#
# NOTE THAT THESE ARE NOT A RESCALE OF THE OLD 2/4/1. Gravity is a free
# acceleration (CONVERSION RULE R4, x2.25), and x2.25 on the rounded 30 Hz
# integers gives 4.5 / 9 / 2.25 - all three wrong, because 4 was standing
# in for 10/2.25 = 4.44 and 1 for 2/2.25 = 0.89. Deriving from the retail
# literal removes the compounded rounding: at 20 Hz a Core tick IS a retail
# update, so the constants are the shipped floats times 1000 exactly.
# The walker consequently falls 11 % faster than it did at 30 Hz. That is
# the migration removing an error, not introducing one.
const JET_GRAVITY_PER_TICK: int = 5
const WALKER_GRAVITY_PER_TICK: int = 10
const MORPH_INTO_WALKER_GRAVITY_PER_TICK: int = 2
# Grounded walk-to-fly injects 0.7 retail velocity once
# (BattleEngine.cpp:1511 `mVelocity.Z -= 0.7f`, retail Z down).
const WALKER_TO_JET_LIFT_IMPULSE_PER_TICK: int = 700
# The same mWalkFriction 0.7 as the horizontal store; was 788_374, i.e.
# 0.7^(2/3).
const WALKER_VERTICAL_RETENTION_NUMERATOR: int = 700_000
const WALKER_VERTICAL_RETENTION_DENOMINATOR: int = 1_000_000
# THE MIGRATION'S CLEAREST SINGLE PAYOFF. Held walker landing jets are
# references/Onslaught/BattleEngineWalkerPart.cpp:330-344:
#
#     vel.X = -vel.X*0.025f;   vel.Y = -vel.Y*0.025f;
#     if (vel.Z>0.01f) vel.Z = -vel.Z*0.075f; else vel.Z = 0;
#     mMainPart->AddVelocity(vel);
#
# i.e. retention 0.975 horizontal and 0.925 descending, per 20 Hz update.
# Core carried 983_263 and 949_353 because 0.983263^1.5 = 0.974999843 and
# 0.949353^1.5 = 0.924999697. The 843-nano and 303-nano residuals were not
# error in anyone's judgement - they were the price of running at a rate
# the game did not, and they are now gone. The action has no energy cost.
const WALKER_LANDING_JET_HORIZONTAL_RETENTION_NUMERATOR: int = 975_000
const WALKER_LANDING_JET_VERTICAL_RETENTION_NUMERATOR: int = 925_000
const WALKER_LANDING_JET_RETENTION_DENOMINATOR: int = 1_000_000
# `if (vel.Z>0.01f)` - the descent below which the vertical arm is not
# applied at all. 7 was round(10 * 2/3) and carried a 4.8 % error.
const WALKER_LANDING_JET_MINIMUM_DESCENT_PER_TICK: int = 10
# 0.015 rad per retail update (R3, x2.170337 on the old 6_911 -> 14_997.6).
const WALKER_TO_JET_PITCH_INPUT_MICRO_RAD_PER_TICK: int = 15_000
# Pristine CBattleEngine::Morph [0x0040A771,0x0040A7C7) schedules
# BECOME_JET (6000) at now + [0x005D85C0] = binary32 0.1f.
const WALKER_TO_JET_AIRBORNE_TRANSITION_TICKS: int = 2
# The same branch compares now - mLastTimeOnGround strictly below
# [0x005D8BB8] = binary32 0.6f; equality takes the stale-ground arm.
# Nearby 0.5f at 0x005D85EC and 0.3f at 0x005D8CB4 are separate predicates.
const RECENT_GROUND_CONTACT_TICKS: int = 12
const LEVEL100_MAXIMUM_ELEVATION_MILLIMETERS: int = 140_000
const LEVEL100_MAP_EDGE_SLOWDOWN_MILLIMETERS: int = 20_000
const LEVEL100_STEEP_SLOPE_GRADIENT_SQUARED_THRESHOLD: int = 704_088
# CBattleEngine::DeclareOnGround uses 0.2 outside pure walker state and
# 0.4 in walker state. Core is at the retail rate, so these are those two
# shipped floats verbatim.
const JET_GROUND_IMPACT_THRESHOLD_PER_TICK: int = 200
const WALKER_GROUND_IMPACT_THRESHOLD_PER_TICK: int = 400
# CBattleEngine::DeclareOnGround: damaging contact applies
# speed*16*cos(surface)^2 life with shield damage disabled, then retains
# the whole velocity by 1-cos(surface)^2. A non-damaging jet contact
# instead retains exactly 0.90; non-damaging walker and morph contacts are
# unchanged by this override.
const GROUND_IMPACT_DAMAGE_MULTIPLIER: int = 16
const GROUND_IMPACT_INCIDENCE_SCALE: int = 1_000_000
const JET_LOW_SPEED_GROUND_CONTACT_RETENTION_NUMERATOR: int = 900_000
const GROUND_CONTACT_RETENTION_DENOMINATOR: int = 1_000_000
# DeclareInWater starts the failure path once the centre is within 0.2
# retail units of the water plane.
const WATER_FAILURE_CLEARANCE_MILLIMETERS: int = 200
# BattleEngine.cpp:1149,1165 correct pitch toward the ground pitch by
# `* 0.03f` per retail update. Verbatim; was 13_823
# (R3, x2.170337 -> 29_999.9).
const WALKER_TERRAIN_PITCH_CORRECTION_NUMERATOR: int = 30_000
const WALKER_TERRAIN_PITCH_CORRECTION_DENOMINATOR: int = 1_000_000
# Retail body yaw integrates its velocity (BattleEngine.cpp:1196) and
# retains exactly 0.8 each 50 ms update (BattleEngine.cpp:1207). Core is
# at that rate, so the retention is the shipped 0.8 verbatim; it was
# 861_774, i.e. 0.8^(2/3).
#
# The earlier 22_667 was the behaviour-preserving R3 conversion of the
# previous 10_444 (x2.170337 = 22_666.9). It corresponded to
# `vx * mGroundTurnRate / 75.0f` (BattleEngineWalkerPart.cpp:349) with
# mGroundTurnRate = 1.7. MEASURED 2026-07-31, that byte is 1.0, not 1.7:
# record 3 "Aquila Prototype" @0x2F6 of data/battle engine
# configurations.dat (sha256 58722b12a04cae97ad2163acb2cc2c1699f95a068831
# 8bd8a86696714d94454a, 1,514 bytes, decoded whole, zero slack, alignment
# proven against the seven already-cited fields of the same record) reads
# 1.0 / 0x3F800000. The shipped input is therefore 1.0/75 = 13_333
# micro-rad per retail tick. Core now consumes that released record rather
# than the superseded fitted rate.
const WALKER_YAW_INPUT_MICRO_RAD_PER_TICK: int = 13_333
const WALKER_YAW_RETENTION_NUMERATOR: int = 800_000
const WALKER_YAW_RETENTION_DENOMINATOR: int = 1_000_000
# Steam injects 1/117 rad per 20 Hz update
# (BattleEngineWalkerPart.cpp:355 `mPitchvel -= (vy/117.0f) * ZoomModifier`,
# and BattleEngineJetPart.cpp:117,157 for jet roll and pitch) and retains
# exactly 0.8 after each update. 1/117 = 0.0085470 rad = 8_547 micro-rad,
# verbatim; it was 3_938 (R3, x2.170337 -> 8_546.7). Source/static
# terrain-relative soft limits replace the earlier start-slope-only
# absolute clamps.
const WALKER_PITCH_INPUT_MICRO_RAD_PER_TICK: int = 8_547
const WALKER_PITCH_RETENTION_NUMERATOR: int = WALKER_YAW_RETENTION_NUMERATOR
const WALKER_PITCH_RETENTION_DENOMINATOR: int = WALKER_YAW_RETENTION_DENOMINATOR
# Retail CBattleEngine starts current/old/desired zoom at 1.0. The two
# normal-weapon actions set desired zoom to 0.4 or 1.0, and Move approaches
# it by exactly 0.1 per 20 Hz update. ZoomModifier is the identity, so the
# same value scales both look input and the projection near-plane extent.
const ZOOM_SCALE: int = 1_000
const ZOOM_OUT_PERMILLE: int = ZOOM_SCALE
const ZOOM_IN_PERMILLE: int = 400
const ZOOM_STEP_PERMILLE_PER_TICK: int = 100
# Two uninterrupted copied-retail repetitions at the authored Level 100
# start stabilized at these absolute endpoints. They remain evidence
# anchors while the source-derived terrain-relative limiter is used; they
# are not reapplied as global clamps on every slope.
const OBSERVED_WALKER_PITCH_UP_LIMIT_AT_LEVEL100_START_MICRO_RAD: int = -1_091_250
const OBSERVED_WALKER_PITCH_DOWN_LIMIT_AT_LEVEL100_START_MICRO_RAD: int = 532_123
# Energy uses the accepted milli-retail policy: 1000 Core units equal one
# retail energy unit. Blaster stores eight energy units and requires one
# to begin walker-to-jet morphing.
const MAXIMUM_ENERGY: int = 8_000
# The released WalkerPart assigns shields from the same energy store on
# every non-jet update. This alias preserves the public snapshot field
# without inventing a second capacity or regeneration curve.
const MAXIMUM_SHIELD: int = MAXIMUM_ENERGY
const AQUILA_SHIELD_EFFICIENCY_PERCENT: int = 98
const MAXIMUM_AUGMENT_CHARGE: int = 10_000
const AUGMENT_DRAIN_PER_TICK: int = 10
# The Aquila Prototype's released mLife is 20.0, and the actor registry's
# Health field carries MILLI-LIFE - stated at Level100TargetTankLife above
# and obeyed by every actor there (Target Drone CUnitLife 1.0 -> 1_000,
# Air Trainer 3.0 -> 3_000, Target Tank 6.0 -> 6_000).
#
# The player is stored in THAT SAME FIELD: Simulation.cs writes
# `_level100Actors.SetHealth(_level100PlayerActorId, MaximumHull)`. So a
# MaximumHull of 1_000 declared the Aquila to be 1.0 released life while the
# shipped configuration says 20.0 - the registry contradicted itself, two
# hundred lines apart in this file.
#
# Released chain: BattleEngine.cpp:102 `mLife = mConfiguration->mLife`, and
# BattleEngine.cpp:2166 `mLife -= inAmount` subtracts damage in those same
# units. There is no separate player health unit in the released code; the
# player is on the identical scale as CUnitLife. Byte-confirmed in
# `battle engine configurations.dat`: record "Aquila Prototype", mLife at
# file offset 0x2D6, bits 0x41A00000 = 20.0f.
#
# NOT A LETHALITY BUG UNDER THE FORMER DIRECT-HULL SHORTCUT, and that is why
# it survived. Damage was converted through
# `MaximumHull / Level100PlayerReleasedLife`
# (Level100ActorWeapons.IncomingDamageMilliLifeFromFloatBits), so the
# constant cancelled out of hits-to-kill: Blaster stayed 100 hits and
# Forseti 8 at either value. That historical shortcut is now replaced by
# the released shield/augment split; this paragraph explains only why the
# earlier unit defect evaded the then-current tests.
#
# It also unblocks two things that could not be written correctly before:
# retail absorbs into shields first at mShieldEfficiency 98.0, and its
# low-hull warning gate is the ABSOLUTE `mLife < 7.0f`
# (BattleEngine.cpp:1769) - neither is expressible against a hull whose unit
# is wrong by 20x.
#
# Archaeology: introduced at 3cc382e8 where MaximumEnergy, MaximumShield and
# MaximumHull were all placeholder 1_000. The first two were later corrected
# with byte provenance. This one was never revisited.
const MAXIMUM_HULL: int = 20_000
# Morph itself does not spend energy, and jet-to-walker has no energy gate.
const TRANSFORM_ENERGY_THRESHOLD: int = 1_000
# DECIDED 2026-07-31, in the 20 Hz migration, and recorded as a DECISION
# rather than a conversion because it is one.
#
# Retail has a single macro for both directions:
# `BATTLE_ENGINE_TRANSFORM_TIME (0.5f)` (BattleEngine.h:43), scheduled
# through the event manager (BattleEngine.cpp:2058
# `AddEvent(BECOME_WALKER, this, GetTime() + BATTLE_ENGINE_TRANSFORM_TIME,
# START_OF_FRAME)`) which FLOORS every delay onto a whole GAME_FR 20
# boundary (eventmanager.cpp:210-212). 0.5 s x 20 Hz = exactly 10 ticks,
# both ways.
#
# Core's previous 16 / 15 came from two copied-retail runs that held raw
# BattleEngine state 1 for 535.359-537.249 ms. Those runs are not
# contradicted: a 500 ms transform whose start is not frame-aligned, polled
# on 50 ms boundaries, is observed as 500-550 ms, and 535-537 sits inside
# that window. The measurement resolves the shipped macro; it does not
# outrank it.
#
# JetToWalker converts to exactly 10 on its own (15 x 2/3), so only
# WalkerToJet is a real choice: the conversion gives 10.67 -> 11, the
# shipped macro gives 10. The macro wins, and the pair becomes symmetric
# as retail's single constant already implies.
const WALKER_TO_JET_TRANSITION_TICKS: int = 10
const JET_TO_WALKER_TRANSITION_TICKS: int = 10
# CBattleEngineWalkerPart::Move recharges the store after recent ground
# contact (references/Onslaught/BattleEngineWalkerPart.cpp:374-388):
#
#   if (EVENT_MANAGER.GetTime() - mMainPart->mLastTimeOnGround < 0.3f)
#     if ((!mInfinateEnergy) && (!mCloaked))
#       float recharge = mMainPart->mConfiguration->mGroundEnergyIncrease;
#       if (!mShieldsRecharging) recharge /= 2;
#       mMainPart->mEnergy += recharge;   // clamped to mConfiguration->mEnergy
#
# `mGroundEnergyIncrease` is a shipped byte. Record 3 "Aquila Prototype"
# @0x2d2 of data/battle engine configurations.dat (sha256
# 58722b12a04cae97ad2163acb2cc2c1699f95a0688318bd8a86696714d94454a,
# 1,514 bytes, decoded whole with CBattleEngineData::Load's field order,
# zero slack) carries mGroundEnergyIncrease 0.05 and mEnergy 8.0.
#
# MaximumEnergy is 8_000 Core against that released 8.0, so the store is
# milli-units: 0.05 released = 50 Core per RETAIL tick, and a Core tick is
# now that retail tick, so the shipped byte transfers verbatim. It was 33
# at 30 Hz (50 * 20/30). The value before that was 4, a placeholder eight
# times too slow, which cost the beat-9 sortie about 58 released seconds
# of standing still to recharge.
#
# The pristine 74154bfa… body 0x00413760..0x00413A63 performs the elapsed
# comparison at 0x004137D3 against 0x005D8CB4 = 9A 99 99 3E = 0.3f.
# This is distinct from the 0.5f InJetMode threshold at 0x005D85EC.
@warning_ignore("integer_division")
const WALKER_RECHARGE_GROUND_CONTACT_TICKS: int = TICKS_PER_SECOND * 3 / 10

# The `/2` arm is DELIBERATELY NOT MODELLED. The pristine body tests the
# WalkerPart flag at +0x14 and multiplies by 0.5 at 0x00413804 when false,
# then resets it true at 0x0041383B. Stuart's writes that clear the flag
# belong to charging/firing heat-backed weapons, not to shield damage.
# Core does not yet model those released heat/ammo-store transitions, so
# selecting the half-rate arm here would invent its trigger.
const WALKER_ENERGY_REGENERATION_PER_TICK: int = 50
# CBattleEngineJetPart::Move spends
#   cost = (mMaxAirEnergyCost - mMinAirEnergyCost) * mThrusterValue
#          + mMinAirEnergyCost
# once per retail tick while airborne with energy.
#
# The two costs are shipped bytes. data/battle engine configurations.dat
# (sha256 58722b12a04cae97ad2163acb2cc2c1699f95a0688318bd8a86696714d94454a,
# 1,514 bytes) decodes with CBattleEngineData::Load's exact field order
# (references/Onslaught/BattleEngineDataManager.cpp:148-430) consuming
# 1,514 of 1,514 bytes, 6 records, every record version 12 ==
# kCurrentBattleEngineDataFormat. Record 3, "Aquila Prototype" @0x2d2:
#   mMinAirEnergyCost 0.005  (0x3BA3D70A)   mMaxAirEnergyCost 0.012 (0x3C449BA6)
#   mMinAirVelocity   0.3    (0x3E99999A)   mMaxAirVelocity   0.9   (0x3F666666)
#   mEnergy           8.0                   mMinTransformEnergy 1.0
#
# These were previously taken from record 5, "Blaster", whose max air cost
# is 0.010 rather than 0.012. That reading is now settled against the
# bytes: the released Level 100 LevelScript does
# EnableWeapon("Mech Twin Vulcan Cannon") on the *walker*, and of the six
# shipped records only Aquila Prototype carries walker weapons
# ["Mech Twin Vulcan Cannon"] together with mPrimaryWeapon
# "Pulse Cannon Pod" -- exactly the two weapons the tutorial enables and
# the only two the level materializes. Blaster's walker list is
# ["Blaster Pod","Mech Grenade Launcher"] and contains no Twin Vulcan at
# all, so under Blaster beat 4 could not exist. The level's own RLWD
# declaration of "Aquila Prototype" is already asserted by
# rebuild/tools/materialize_retail_assets.py:1339.
#
# Stored in micro-retail-energy per RETAIL tick so the interpolation is
# exact at half throttle and the value survives the Core tick change.
const JET_MINIMUM_ENERGY_DRAIN_MICRO_PER_RETAIL_TICK: int = 5_000
const JET_MAXIMUM_ENERGY_DRAIN_MICRO_PER_RETAIL_TICK: int = 12_000
# Energy uses the accepted milli-retail policy (1000 Core units == one
# retail energy unit), so one Core energy unit is 1000 micro-retail.
const MICRO_RETAIL_ENERGY_PER_CORE_ENERGY_UNIT: int = 1_000
const FIRE_ENERGY_COST: int = 30
# Measured 2026-07-31:
# weapon `Pulse Cannon Pod` @0x17463 of data/default physics.dat (sha256
# e1fb3dedbeb29b4b4151da2c8cbbdc940b716b1a2321e1d6a9ba1542c74ada14,
# 175,603 bytes) resolves charge level 0 to weaponmode
# `Mech Pulse Cannon Charged` @0x134E3, whose CWeaponReloadTime is 0.1 s
# (0x3DCCCCCD @0x1351D), exactly two released 20 Hz updates.
const PULSE_CANNON_RELOAD_TICKS: int = 2
# The same charged mode carries CWeaponInaccuracy 0.008726646 rad
# (0x3C0EFA35), rounded here to deterministic integer microradians.
const PULSE_CANNON_INACCURACY_MICRO_RADIANS: int = 8_727
# Fresh copied-Steam Level 100 runs independently repeated four
# lowest-charge Pulse Cannon rounds against each of the three training
# tanks. Every round carried definition speed 35 and moved exactly 1.75
# units per released 20 Hz update. Core is now at that rate, so 1.75 units
# per tick is the shipped figure verbatim; it was 1_167 at 30 Hz.
const PROJECTILE_SPEED_PER_TICK: int = 1_750
# The round the above weaponmode fires is `Mech Pulse Bolt Medium`
# @0xAC16 of the same physics.dat. Its CRoundLifeSpan is exactly 6.0
# (0x40C00000 @0xAC5D), or 120 released 20 Hz updates. Charge level 1
# names `Mech Pulse Cannon Charged 2` @0x135b3, whose CWeaponRound is
# `Mech Pulse Bolt Large` @0xacda; Fire selects that identity when
# FullyCharged. Large's authored 20/7/0.20/8.0 scalars are not this arm.
const PROJECTILE_LIFETIME_TICKS: int = 6 * TICKS_PER_SECOND
# Same hash-pinned physics.dat, Round "Mech Pulse Bolt Large" @0xACDA:
# field 3 = 0x41A00000 (20 units/second), field 1 = 0x40E00000
# (7 seconds), field 12 = 0x3E4CCCCD (0.20 units). These project to
# Core's 20 Hz millimeter motion/contact units; they do not establish
# float motion, terminal event timing, or Large's presentation parity.
const LARGE_PULSE_SPEED_PER_TICK: int = 1_000
const LARGE_PULSE_LIFETIME_TICKS: int = 7 * TICKS_PER_SECOND
const LARGE_PULSE_CONTACT_RADIUS_MILLIMETERS: int = 200
# Mech Twin Vulcan Cannon, read out of data/default physics.dat
# (sha256 e1fb3ded...b1a2321e1d6a9ba1542c74ada14, 175,603 bytes, 777
# statements) with the value-id map established in
# reverse-engineering/binary-analysis/physics-round-value-ids-2026-07-25.md
# and independently re-parsed for this change:
#   weapon     Mech Twin Vulcan Cannon @0x171b4
#                CWeaponChargeLevel 0 -> mode "Mech Twin Vulcan Cannon"
#                CWeaponConsumption 2.0   (Pulse Cannon Pod is 4.0)
#   weaponmode Mech Twin Vulcan Cannon @0x13360
#                CWeaponInaccuracy 0.006981317 rad, CWeaponReloadTime 0.05 s,
#                CWeaponVolleySize 4, CWeaponRound "Mech Bullet",
#                CWeaponPredictive 1, four CWeaponLaunchSequence entries
#   round      Mech Bullet @0xa3f2
#                CRoundVelocity 60.0, CRoundDamage 0.08, CRoundLifeSpan 1.0,
#                CRoundExplosion "Mech Bullet Hit"; no CRoundRadius node
#   explosion  Mech Bullet Hit @0x4373
#                CExplosionRadius 0.2, CExplosionDamage 0.001
# CRoundVelocity is units per second on the measured 20 Hz released tick
# (the pulse's byte-read 35.0 divided by the measured 1.75 units per
# update is exactly 20), so 60.0 u/s is 3.0 units per released tick, which
# is now the Core tick, and the 1.0 s lifespan is 20 Core ticks.
const MECH_BULLET_SPEED_PER_TICK: int = 3_000
const MECH_BULLET_LIFETIME_TICKS: int = 1 * TICKS_PER_SECOND
const TWIN_VULCAN_VOLLEY_SIZE: int = 4
# Both player Vulcan modes carry the same CWeaponInaccuracy
# 0.006981317 rad (0x3BE4C388).
const PLAYER_VULCAN_INACCURACY_MICRO_RADIANS: int = 6_981
# CWeaponReloadTime 0.05 s. A 20 Hz Core tick IS 50 ms, so the reload is
# exactly one tick and the released 20 volleys per second fall out of the
# rate itself.
#
# This replaces a "thirds of a millisecond" counter that existed SOLELY
# because 1/30 s is not a whole number of milliseconds: at 30 Hz the
# reload was 150 thirds against 100 thirds per tick, firing on 2 ticks of
# every 3 to average the released 20 volleys per second rather than
# rounding it to 15 or 30. The unit has no reason to exist at 20 Hz.
const TWIN_VULCAN_RELOAD_TICKS: int = 1
# CWeaponConsumption is 2.0 for the Twin Vulcan against 4.0 for the Pulse
# Cannon Pod. The absolute Core cost of a pulse shot (FireEnergyCost) is
# not dual-accepted retail truth, so only the byte-read 2.0/4.0 ratio is
# carried across.
@warning_ignore("integer_division")
const TWIN_VULCAN_FIRE_ENERGY_COST: int = FIRE_ENERGY_COST / 2
# A same-return capture of Steam CBattleEngine::GetLaunchPosition resolved
# cockpit emitter "Gun" index 1 relative to the live BattleEngine basis.
# Values are rounded to deterministic integer millimetres.
const PULSE_CANNON_EMITTER_RIGHT_MILLIMETERS: int = -6
const PULSE_CANNON_EMITTER_FORWARD_MILLIMETERS: int = 80
const PULSE_CANNON_EMITTER_UP_MILLIMETERS: int = 259
# The released definitions retain life in float units. Registry health
# carries the same values in milli-life while the contact owner applies
# exact 1.8 medium-pulse damage to the contacted part.
const LEVEL100_TARGET_TANK_LIFE: int = 6_000
# Target Truck Unit field 3 is the released maximum-life owner. Its
# separate motion definition retains field 1 as ground maximum speed.
const LEVEL100_TRAINING_TRUCK_LIFE: int = 3_000
const LEVEL100_TARGET_WAREHOUSE_LIFE: int = 50_000
# Target Drone Unit field 3 CUnitLife 1.0 (0x3F800000).
const LEVEL100_TARGET_DRONE_LIFE: int = 1_000
# Air Trainer Unit field 3 CUnitLife 3.0 (0x40400000).
const LEVEL100_AIR_TRAINER_LIFE: int = 3_000

# ---------------------------------------------------------------------
# Plane (behaviour class 9) motion.
#
# Every value below is a shipped byte. `data/default physics.dat`
# (sha256 e1fb3ded...ada14, 175,603 bytes, 777 statements):
#
#   Unit  Target Drone @0x24e76 (name string @0x24e7e)
#           [39] CUnitBasedOn        "Base Air Unit"
#           [ 8] CUnitBehaviour      9
#           [ 2] CUnitAirVelocity    5.5   (0x40B00000)
#           [ 6] CUnitAirTurnRate    0.04363323 rad (0x3D32B8C2)
#           [ 3] CUnitLife           1.0   (0x3F800000)
#           [22] CUnitStrafeChange   0.01  (0x3C23D70A)
#           [23] CUnitMaxTargetRange 500.0 (0x43FA0000)
#   Unit  Air Trainer  @0x1e198 (name string @0x1e1a0)
#           [ 2] CUnitAirVelocity    9.2   (0x41133333)
#           [ 6] CUnitAirTurnRate    0.04363323 rad (0x3D32B8C2)
#           [ 3] CUnitLife           3.0   (0x40400000)
#           [23] CUnitMaxTargetRange 300.0 (0x43960000)
#
# The value-id -> class map is
# reverse-engineering/binary-analysis/physics-round-value-ids-2026-07-25.md;
# ids 2/6 write unit-record +0xb4/+0xb8. CAirUnit Init copies +0xb8 to
# all three Euler rate fields at 0x00402b0c..0x00402b32. The factor 1/3
# at 0x00402fc5 applies only while TF_DYING; living Plane motion uses
# the full rate. The air and ground guides have different move paths.
#
# The current Plane path reads these constants; its manifest motion
# scalars remain null. materialize_retail_assets.py validates these exact
# profile words in _level100_actor_motion_definitions.
#
# CAirGuide slot 3 writes drive using GetMaxVelocity() * 0.05 * 4.0.
# AirUnit motion subsequently clamps velocity to GetMaxVelocity() * 0.05
# before Unit moves the Actor. The current reconstruction uses that cap
# as constant speed; it does not yet reproduce the retained drive,
# friction, gravity and velocity transaction. Plane's multiplier is 1.0;
# the guide's factor 4 is not GroundVehicle's four-tick cadence.
const LEVEL100_TARGET_DRONE_AIR_SPEED_MILLIMETERS_PER_SECOND: int = 5_500
const LEVEL100_AIR_TRAINER_AIR_SPEED_MILLIMETERS_PER_SECOND: int = 9_200
const LEVEL100_PLANE_AIR_TURN_RATE_FLOAT_BITS: int = 0x3D32B8C2

# Air-guide altitude band, read out of the pristine BEA.exe
# (sha256 74154bfa...7750). CAirGuide__UpdateGroundClearanceCache
# (0x004028e0) caches the MINIMUM height above terrain over the owner's
# rounded x/y +/-20 units sampled in steps of 5 - a 41x41 unit box, 81
# samples - and 0x00402280 then commands pitch from it:
#   0x0040240d  clearance <  5.0  (DAT_005d85d8) -> pitch = -pi/4  (climb)
#   0x00402427  clearance < 15.0  (DAT_005d85d4) -> level out a descent
#   0x00402452  clearance > 50.0  (DAT_005d85d0) -> pitch = +pi/4  (dive)
# Retail Z is down, so the negative command is the climb; Core Y is up, so
# the sign is inverted at the point of use and the comment there says so.
const LEVEL100_PLANE_CLEARANCE_SAMPLE_RADIUS_MILLIMETERS: int = 20_000
const LEVEL100_PLANE_CLEARANCE_SAMPLE_STEP_MILLIMETERS: int = 5_000
const LEVEL100_PLANE_CLIMB_CLEARANCE_MILLIMETERS: int = 5_000
const LEVEL100_PLANE_LEVEL_CLEARANCE_MILLIMETERS: int = 15_000
const LEVEL100_PLANE_DIVE_CLEARANCE_MILLIMETERS: int = 50_000
# DAT_005d85dc/e4 = +/-pi/4 (0x3F490FDB), the clearance-band pitch command.
const LEVEL100_PLANE_CLEARANCE_PITCH_MICRO_RADIANS: int = 785_398
# 0x3F860A92 = 1.0471976 rad, the +/-60 degree pitch command taken toward
# an active attack target's altitude at 0x004023ea.
const LEVEL100_PLANE_TARGET_PITCH_MICRO_RADIANS: int = 1_047_198
# The map-edge turn-back at 0x0040246a: DAT_005d85cc = 10.0 and
# DAT_005d85c4 = 502.0 against the 512-unit map extent.
const LEVEL100_PLANE_MAP_EDGE_MARGIN_MILLIMETERS: int = 10_000

# ------------------------------------------------------------------
# Actor weapons. Every value below is a dword read out of
# `data/default physics.dat` (sha256 e1fb3ded...ada14, 175,603 bytes,
# 777 records) through the record walker in
# `rebuild/tools/materialize_retail_assets.py:563`, or a `.rdata` dword
# read out of the pristine BEA.exe (sha256 74154bfa...7750,
# .rdata VA 0x5d8000 -> file 0x1d8000), or a default written by the
# shipped record constructors. Field offsets come from
# `reverse-engineering/binary-analysis/physics-round-value-ids-2026-07-25.md`
# (weapon-mode lane `M`, round lane `R`, explosion lane `E`).
# ------------------------------------------------------------------

# The released gameplay pseudo-random stream.
#
# Random__NextLCGAbs @0x004de8d0 is a Schrage-decomposed Lehmer step over
#   a = DAT_006321f0 = 48271
#   m = DAT_006321f4 = 214783647
# Both dwords are read from the shipped file. `m` is NOT the textbook
# MINSTD modulus 2147483647 - the shipped constant is a digit short, and
# because m % a (25968) exceeds m / a (4449) the Schrage decomposition is
# not valid for it. The reconstruction reproduces the shipped constants
# rather than the textbook ones, because the shipped stream is the
# behaviour.
#
# CGame::InitRestartLoop @0x0046c430 allocates the 8-byte seed pair and
# seeds it with `push 0x1e240` at 0x0046c7e4 (RandomSeedPair__Set
# @0x004de8c0), then stores the pointer at `mov [ebp+0x304], eax`
# (0x0046c80d). The global read site everywhere else is
# `MOV ECX,[0x008a9d9c]`, and 0x008a9d9c - 0x304 = 0x008a9a98, which is
# the global CGame (149 `MOV ECX, 0x8a9a98` thiscall sites in .text).
# So the whole gameplay stream restarts from a fixed constant at every
# level start: it is deterministic by construction, not by our choice.
const LEVEL100_RELEASED_RANDOM_INITIAL_SEED: int = 123_456
const LEVEL100_RELEASED_RANDOM_MULTIPLIER: int = 48_271
const LEVEL100_RELEASED_RANDOM_MODULUS: int = 214_783_647
# The scatter sample. ProjectileBurst__SpawnFromCurrentPreset @0x005069f0
# and the round update @0x004d8e40 both compute
#   ((float)(NextLCGAbs() % 65536) * DAT_005d8de4 - DAT_005d8568) * scale
# with DAT_005d8de4 = 3.0517578125e-05 = 1/32768 and DAT_005d8568 = 1.0,
# i.e. a sample on [-1, 32767/32768] in steps of 1/32768. The exact
# finite grid is proved; the defective generator's residue frequencies
# are not claimed uniform.
const LEVEL100_RELEASED_RANDOM_UNIT_DIVISOR: int = 32_768
const LEVEL100_RELEASED_RANDOM_UNIT_MODULUS: int = 65_536

# Blaster (round record @ physics `Round / Blaster`).
#   CRoundVelocity  45.0  0x42340000     CRoundDamage   0.2  0x3e4ccccd
#   CRoundLifeSpan   3.0  0x40400000     CRoundExplosion 'Small Energy Hit'
# `Small Energy Hit` carries CExplosionRadius 0.0 and no CExplosionDamage,
# so the Blaster carries round damage only.
const LEVEL100_BLASTER_SPEED_MILLIMETERS_PER_SECOND: int = 45_000
const LEVEL100_BLASTER_LIFE_SPAN_MILLISECONDS: int = 3_000
const LEVEL100_BLASTER_DAMAGE_FLOAT_BITS: int = 0x3E4CCCCD

# Forseti Missile (round record @ physics `Round / Forseti Missile`).
#   CRoundVelocity 15.0 0x41700000      CRoundDamage    2.0 0x40000000
#   CRoundLifeSpan 10.0 0x41200000      CRoundTurnRate  0.04886922 0x3d482b17
#   CRoundSeek        3                 CRoundSeekDelay 0.1 0x3dcccccd
#   CRoundSeekAngle 0.7853982 0x3f490fdb CRoundWiggle 0.02094395 0x3cab92a6
#   CRoundExplode     1                 CRoundExplosion 'Micro Missile Hit'
# `Micro Missile Hit` has CExplosionBasedOn 'Small Explosion Base', which
# carries CExplosionRadius 1.0 and CExplosionDamage 0.5. The round+
# explosion sum is the same decomposition already used for the player's
# Mech Bullet (SimulationConstants / Level100DestructionState), and is
# recorded there as not independently proven.
#
# The round carries no CRoundSeekTerminationTime, so the shipped default
# from CRoundData__CreateAndRegisterByName @0x0042ffa0 applies:
# item[0x11] = 0x447a0000 = 1000.0 s, i.e. it never expires inside the
# 10 s lifespan. It also carries no CRoundRadius (default item[0x23] = 0).
const LEVEL100_FORSETI_MISSILE_SPEED_MILLIMETERS_PER_SECOND: int = 15_000
const LEVEL100_FORSETI_MISSILE_LIFE_SPAN_MILLISECONDS: int = 10_000
const LEVEL100_FORSETI_MISSILE_DAMAGE_FLOAT_BITS: int = 0x40000000
const LEVEL100_FORSETI_MISSILE_EXPLOSION_DAMAGE_FLOAT_BITS: int = 0x3F000000
const LEVEL100_FORSETI_MISSILE_TURN_RATE_MICRO_RADIANS: int = 48_869
const LEVEL100_FORSETI_MISSILE_SEEK_DELAY_MILLISECONDS: int = 100
const LEVEL100_FORSETI_MISSILE_SEEK_ANGLE_MICRO_RADIANS: int = 785_398
const LEVEL100_FORSETI_MISSILE_WIGGLE_MICRO_RADIANS: int = 20_944

# Drone Vulcan Cannon, weapon-mode record. Mesh slot `GunA` on
# `Target Drone` (`CUnitUse`), corroborated by the three drone mesh parts
# named GUNA/GUNA/GUNB.
#   CWeaponRound 'Blaster'            CWeaponReloadTime  1.0  0x3f800000
#   CWeaponBurstSize 8.0 0x41000000   CWeaponBurstDelay  0.15 0x3e19999a
#   CWeaponMaxRange 40.0 0x42200000   CWeaponInaccuracy  0.01745329 0x3c8efa35
#   CWeaponYawTolerance 0.17453292 0x3e32b8c2
#   CWeaponMinDeflection +0.7853982   CWeaponMaxDeflection -0.7853982
# No CWeaponMinRange (shipped default 0.0, item[0x1d]) and no
# CWeaponVolleySize (shipped default 1, item[0x12]).
const LEVEL100_DRONE_VULCAN_RELOAD_MILLISECONDS: int = 1_000
const LEVEL100_DRONE_VULCAN_BURST_SIZE: int = 8
const LEVEL100_DRONE_VULCAN_BURST_DELAY_MILLISECONDS: int = 150
const LEVEL100_DRONE_VULCAN_MINIMUM_RANGE_MILLIMETERS: int = 0
const LEVEL100_DRONE_VULCAN_MAXIMUM_RANGE_MILLIMETERS: int = 40_000
const LEVEL100_DRONE_VULCAN_INACCURACY_MICRO_RADIANS: int = 17_453
const LEVEL100_DRONE_VULCAN_YAW_TOLERANCE_MICRO_RADIANS: int = 174_533

# Forseti Drone Missile Launcher (slot `GunB` on `Target Drone`) and
# Forseti Missile Trainer Launcher (`Air Trainer`). Both fire the Forseti
# Missile with CWeaponInaccuracy 0.0 and CWeaponYawTolerance 0.34906584
# (0x3eb2b8c2); they differ only in reload time and maximum range.
const LEVEL100_FORSETI_DRONE_LAUNCHER_RELOAD_MILLISECONDS: int = 10_000
const LEVEL100_FORSETI_TRAINER_LAUNCHER_RELOAD_MILLISECONDS: int = 2_000
const LEVEL100_FORSETI_LAUNCHER_MINIMUM_RANGE_MILLIMETERS: int = 20_000
const LEVEL100_FORSETI_DRONE_LAUNCHER_MAXIMUM_RANGE_MILLIMETERS: int = 80_000
const LEVEL100_FORSETI_TRAINER_LAUNCHER_MAXIMUM_RANGE_MILLIMETERS: int = 60_000
const LEVEL100_FORSETI_LAUNCHER_YAW_TOLERANCE_MICRO_RADIANS: int = 349_066
const LEVEL100_FORSETI_LAUNCHER_INACCURACY_MICRO_RADIANS: int = 0

# Both drone weapon modes carry CWeaponMinDeflection +0.7853982 and
# CWeaponMaxDeflection -0.7853982 - the two names are shipped the wrong way
# round, which is exactly why the gate at OID__CanFireAtTarget_BallisticArcA
# @0x00507ab0 reads as inverted:
#   if (mode[+0x7c] <= pitchDelta) return 0;   // delta must be < +0.785
#   if (pitchDelta <= mode[+0x80]) return 0;   // delta must be > -0.785
# Under the shipped values that is a symmetric +/- pi/4 pitch window, and
# the Ghidra rendering is correct as written.
const LEVEL100_ACTOR_WEAPON_PITCH_WINDOW_MICRO_RADIANS: int = 785_398

# The released fire cadence, from ProjectileBurst__SpawnFromPercentBucketFallback
# @0x00506010 and CWeapon__HandleFireBurstEvent @0x00506930:
#   if (NOW <= weapon[+0x64]) return;            // reload gate
#   weapon[+0x64] = NOW + mode[+0x38];           // reload runs from burst START
#   weapon[+0x6c] = 0; spawn();                  // shot 0, immediately
#   if (mode[+0x44] > 0) { weapon[+0x6c] = 1;
#       schedule 0x1389 at NOW + mode[+0x3c]; }
#   ... handler: if (weapon[+0x6c] < mode[+0x44]) { spawn(); weapon[+0x6c]++;
#                    reschedule at NOW + mode[+0x3c]; }
# so CWeaponBurstSize N produces exactly N shots spaced CWeaponBurstDelay
# apart, and the reload interval is measured from the first shot.

# The target-height gate at CUnit__CanFireAtTarget_BallisticArcA
# @0x004fb500 compares terrain-relative target height against
# CWeaponMinTargetHeight / CWeaponMaxTargetHeight. Neither drone weapon
# mode carries either node, so the shipped defaults apply
# (item[0x1b] = -10.0, item[0x1c] = 10000.0) and the gate is
# unconditional for every Level 100 engagement. It is therefore not
# modelled, rather than modelled with invented numbers.

# The jet-mode Mech Vulcan Cannon. Aquila Prototype's jet weapon list is
# ["Mech Vulcan Cannon", "Missile Pod"] (battle engine configurations.dat
# @0x2d2), and the LevelScript enables the first of those for beats 7 and
# 9 while disabling both walker weapons - so this is the only weapon the
# player has for the two airborne-target beats.
#
#   weaponmode `Mech Vulcan Cannon`
#     CWeaponRound      'Mech Air Bullet'
#     CWeaponReloadTime 0.05  0x3d4ccccd     CWeaponVolleySize 2.0 0x40000000
#     CWeaponInaccuracy 0.006981317 0x3be4c388   CWeaponPredictive 1
#     CWeaponLaunchSequence with two muzzle entries
#   round `Mech Air Bullet`
#     CRoundVelocity 60.0 0x42700000  CRoundDamage 0.15 0x3e19999a
#     CRoundLifeSpan  1.0 0x3f800000  CRoundExplosion 'Mech Bullet Hit'
#   explosion `Mech Bullet Hit` CExplosionRadius 0.2, CExplosionDamage 0.001
#
# 60.0 units per second at the measured 20 Hz released tick is 3,000 mm
# per released tick, which is now the Core tick - the same figure
# MechBulletSpeedPerTick already carries, because both rounds ship
# CRoundVelocity 60.0. Damage is the same round+explosion sum the Mech
# Bullet uses and which is recorded there as not independently proven:
# 0.15 + 0.001 = 0.151, float bits 0x3E1A9FBE.
#
# Not modelled, and deliberately: the two CWeaponLaunchSequence muzzle
# offsets (same reason as the Twin Vulcan's four), and CWeaponPredictive,
# whose lead-computation law is unread.
const MECH_AIR_BULLET_SPEED_PER_TICK: int = MECH_BULLET_SPEED_PER_TICK
const MECH_AIR_BULLET_LIFETIME_TICKS: int = 1 * TICKS_PER_SECOND
const MECH_VULCAN_VOLLEY_SIZE: int = 2
const MECH_AIR_BULLET_DAMAGE_BITS: int = 0x3E1A9FBE
# CWeaponReloadTime 0.05 s, the same value and the same weapon-mode field
# as the walker Twin Vulcan, and now the same single Core tick.
const MECH_VULCAN_RELOAD_TICKS: int = TWIN_VULCAN_RELOAD_TICKS

# Player hull per released life point. `mLife` for Aquila Prototype is
# 20.0 (data/battle engine configurations.dat @0x2d2), and Core defines a
# full hull as MaximumHull. One released damage unit is therefore
# MaximumHull / 20 = 1,000 Core milli-life. Both operands are shipped or
# definitional; the ratio is not an independent measurement.
const LEVEL100_PLAYER_RELEASED_LIFE: int = 20

# The player's primary approximate-geometry cylinder. SetCollisionShape
# (0x004063B0) stores GetRadius() at +0x14, its square at +0x18, and
# COfGHeight()*0.5 at +0x1c. The collision centre is retail mPos.Z + 0.76;
# retail Z-down maps to Core Y-up, hence 760 mm below the Core pose origin.
const LEVEL100_PLAYER_CONTACT_RADIUS_MILLIMETERS: int = 400
const LEVEL100_PLAYER_COLLISION_CENTER_BELOW_ORIGIN_MILLIMETERS: int = 760
const LEVEL100_PLAYER_COLLISION_HALF_HEIGHT_MILLIMETERS: int = 950
