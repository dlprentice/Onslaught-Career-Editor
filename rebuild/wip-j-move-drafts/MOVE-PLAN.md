# Level 100 movement (M4d) port plan (Peer J, 2026-10-15, written from bea-decomp while Archive B is read-only)

Source: bea-decomp src/ (internal disk), read only. Addresses are retail functions (pristine specimen 74154bfa…;
the Steam BEA.exe measured 74154bfa… on 2026-10-15, so instruction checks can objdump it from the internal disk).

## The chain, per level-100 class

Every actor: CActor::HandleEvent (004019e0) -> Move() or LowFidelityMove(), then AddMoveEvent (rescued edit 1).

| Class | Move chain (each calls the next) | Notes |
|---|---|---|
| CBuilding | CBuilding::Move 004178a0 only | NEVER calls CUnit/CActor::Move: buildings do not move. Needs UpdateTimer, AnySpawnerUnknown4e4420, anim modes "closing"/"unshutting", Unknown115 (spawners). |
| CSimpleBuilding | 004dfaa0: returns at once unless dying | dying: gravity 0.002, explosions, then CUnit::Move. ClipToGround = !dying (004dfcb0). |
| CCannon | 0041b370 (anim "Activate"/"Deactivate" by the AI target) -> CGroundUnit 0047c970 -> CUnit 004fa8d0 -> CActor 004015e0 | Gravity 0 (inline, 004bfc60). Turret slew in CUnit::Move (mUnknownE0/E8 with Azimuth, AngleDifference; GetTargetablePos). |
| CGroundVehicle | 0047d1c0 (tilt from MAP.Normal: two cross products, Normalise; FVector ^ operand order = oracle) -> CGroundUnit -> CUnit -> CActor | COfGHeight 0.1. Guide CGroundVehicleGuide::Unknown3 0047d750 NEEDS the occupancy grid (see below). |
| CPlane | 004d1cd0 (thrusters, wing state; after: velocity = speed * forward column) -> CAirUnit 00402fa0 -> CUnit -> CActor | Guide CAirGuide::Unknown3 00402280 (atan2, Azimuth, Elevation, map-who nearest, clearance). Gravity dying-only (inline 0.025 / CAirUnit 00403b60). |
| CDropship | 00447120 (door states 0..7, landing tree-flattening, top-speed straightening) -> CAirUnit -> CUnit -> CActor | Guide is CDropshipGuide::Unknown3 00448930 (Guide.h:40), NOT a basic guide: CHECK Units.cs after recovery. Unknown73 0.99; Gravity 00448360 dying-only; ClipToGround folded to 004dfcb0. Door-state 6 reads GetEmitter(27) = needs CMCDropship pose. |
| CBattleEngine | 004081c0 (stealth, safe positions, aug, zoom, locks, walker part Move 00413760 / jet part 00410c50, gravity, map-edge clamps) -> CActor::Move directly -> standing-on-object, forced movement into CMCBattleEngine, step-up via WORLD.FindFirstThingToHitLine (ECL_MESH) | The POS probe. Held during PreRun: walker part with no input. Needs CMCBattleEngine/CMCMech (1,303 lines) for AddMovement and the legs; the line test needs mesh collision volumes. |
| CFeature | 0044cc10: CActor::Move, dying sink (asin, Azimuth) | Trees/features rarely move; dying only. |

Shared pieces (CUnit::Move 004fa8d0, in order): guide Unknown3 or Stop; UpdateTimer 004fa800; CActor::Move;
Unknown76 (inline 00405de0) -> Unknown77 004fa4b0 (orientation slew; FMatrix(yaw,pitch,roll) = FromYawPitchRoll);
shields; dying Unknown95; mUnknown170 ramp; vents GetEmitter(21); firing effect; dust GetEmitter(22) (particles:
count, do not draw); spawners DoSpawn; turret/barrel slew; deploy states 1/2/4 (GoToPoint 300 ahead; Unknown116;
StartUndeploying); spawner sound; UpdatePosition (004f39b0 -> CRTMesh::UpdatePosition is EMPTY: no port needed).

CGroundUnit::Move 0047c970: multiplier SINT(4.0) steps of (v += accel; v *= friction), friction Unknown73 (CUnit
0.98) or Unknown72 (0.25) on ground/water with Unknown76; accel = mUnknown14C * 0.4 + gravity; parachute thrusters
(MAP.GetHeight(SINT x, SINT y) -> X87.Fist); top speed Unknown111()/20 in XY; then CUnit::Move; then the bob
(sin, kept as (float)sin -> X87.Sin then round).

CActor::Move 004015e0: mLastMoveTime; old pos/orientation; map-who sector; pos += velocity (the decomp's FVector
&position alias: X, Y, Z order); ClipToGround: alt = MAP.Collide(pos) - COfGHeight; at/below: Z = alt, TF_SLIDE
slide or DeclareOnGround + bounce (|vZ| > Gravity()+0.05 -> -vZ*BounceFactor (unit data) else 0); water;
UpdateEntry(old pos) -> collision-seeking MovedSector (CS things are counted as not ported).
LowFidelityMove (actor.cpp:54, no address: inlined into HandleEvent): old pos; pos += v; clip; mLastTimeOnGround.

## Dependencies to port, in order

1. CActor::Move/LowFidelityMove + CUnit::Move + UpdateTimer + Unknown77 + CGroundUnit/CCannon/CBuilding/
   CSimpleBuilding moves (J). Gravity/ClipToGround/COfGHeight/BounceFactor/ObeyGravity/Unknown72/73/76/109 per class
   as tabulated above (unit.h: CUnit 44-261, CAirUnit 262, CPlane 302, CGroundUnit 353, CGroundVehicle 372, CCannon
   447, CBuilding 507, CDropship 543, CSimpleBuilding 836).
2. COccupancyGrid + COccupancy (NavigationMap.cpp, 971 lines; mostly integer: Load 004be050, BuildStatic 004bcd60,
   ClearSteep, ApplyStatic, AddUnit/RemoveUnit, IsBlocked, FindNearest, BuildPath 0047? (NavigationMap.cpp:587),
   Flood 004be420, StepDown, Simplify 004beea0, Unknown4bc2e0 004bc2e0, UnknownCell). Proposed owner: Peer B (squads
   already use the path type CNormalSquadUnknownD4 through Unknown4bc2e0/Simplify) or a forked helper. Self-contained;
   test against the world's grids loaded from level 100 and the native port's path traces if Peer I can log them.
3. Guides' steering: CGroundVehicleGuide 0047d750 (grid), CTerrainGuide 004f1ee0 (cannons: Unknown111()/5),
   CAirGuide 00402280, CDropshipGuide 00448930 (J).
4. CAirUnit/CPlane/CDropship moves (J); the dropship's door states need CMCDropship's pose (GetEmitter 26/27).
5. Motion controllers: CMCCannon (88 lines), CMCGroundVehicle (86), CMCDropship (99), MotionController.cpp (191):
   they change part poses, hence GetEmitter positions (muzzles, thrusters) and collision volumes. Port with
   MeshPose's controller branch (now NotSupported).
6. The player: CBattleEngineWalkerPart::Move 00413760, CMCBattleEngine/CMCMech, WORLD.FindFirstThingToHitLine with
   mesh collision volumes (MeshCollisionVolume.cpp), standing on objects. Largest single block; gates POS/LIFE.

## D's oracle queue from this chain (float sites)
Unknown77 004fa4b0; CGroundUnit::Move's step loop and top-speed clamp 0047c970; CGroundVehicle::Move's tilt 0047d1c0
(cross products: operand order); CUnit::Move's turret slew 004fa8d0; CTerrainGuide 004f1ee0 (Normalise reuse noted in
the decomp's comment); CAirGuide 00402280; CAirUnit::Move 00402fa0 (Magnitude clamp); CPlane::Move's velocity
re-aim 004d1cd0; CActor::Move 004015e0 (pos += v alias order; bounce).

## Open questions (cheapest falsifier)
- Which level-100 ground vehicles have a "WheelMotion" anim mode? Those get CMCBuggy (MCBuggy.cpp, 559 lines) and do
  not tilt; the rest get CMCGroundVehicle and tilt (CGroundVehicle::Init 0047cfd0). Falsifier: list the anim modes of
  the level's vehicle meshes with MeshData once the checkout is back.
- ANSWERED (world.cpp 845-875, Unit.cpp 2056): CUnit::GetOccupancyGrid 004fd380 picks WORLD.mOccupancy by unit data
  mUnknownFC (0 none, 1 -> [0] max slope 35, 2 -> [1] 45, 3/4 -> [2] 60; world.cpp 946-948). A level with a base world
  (level 100: base 1) SKIPS its own grids (SkipLegacy x3, plus SkipHeader before version 50); the base world's load
  (base = TRUE) Loads all three. So level 100's vehicles steer on base world 1's grids. The guides read mGrid at
  construction (GroundVehicleGuide.cpp:18), i.e. at unit Init, after the base world has loaded. Still open: which
  level-100 unit types have mUnknownFC != 0 (read with PhysicsRegistry once the checkout is back).
- Does any level-100 actor take TF_SLIDE? (grep flags set at Init; falsifier: port log of mFlags at load end.)

## Instruction findings (Steam BEA.exe, SHA-256 74154bfa… = the pristine specimen; read 2026-10-15)
- DIVISION BY A CONSTANT IS A RECIPROCAL MULTIPLY: CGroundUnit::Move's `Unknown111() / 20.0f` is `fmul 0.05f`
  (0x3d4ccccd, 0047cd45); its `friction /= 1.15f` is `fmul 0.8695652f` (0x3f5e9bd4, 0047cb1c). Rounding differs from
  a true divide. Every `x / k` in decomp source needs its site checked; port as `x * (float reciprocal)` where so.
- CGroundUnit::Move's XY speed: fsqrt(Y*Y + X*X) on the stack (0047cd4b..0047cd5d), not FVector.MagnitudeXY's order.
- The bob (0047ce2a..0047ce4a): fsin at full precision, then fmul 0.05f; the sine is not rounded first.
- CAirGuide::Unknown3's roll test (00402553..0040256d): right*d summed (Z+Y)+X on the stack, compared without store.
- CDropshipGuide's lateral projection (00448b78, 00448cc9): Y and Z combined before X (the decomp's own comment).
