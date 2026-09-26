# Level 100 construction order: shared draws and queued events

Status: active static contract for the rebuild's Level 100 start
Last updated: 2026-09-26
Summary: the order in which Level 100's construction consumes the shared gameplay
random stream and queues events, from the base-world pines to the last level-world
row, and what each event's first delivery draws.
Evidence: MEASURED static reads of the pristine specimen and the shipped Level 100
world files, scripts, meshes and `default physics.dat`. A read-only research pass
traced the level-world unit rows; the RE lane re-checked their classes, constructors,
queued events and draw sites at the addresses given. Laws already contracted
elsewhere are linked, not repeated. No runtime capture.
Specimen: pristine `local-lab/safe-copy-bea-pristine/BEA.exe.original.backup`, SHA-256
`74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`;
`100_BSWD` is byte-identical to `110_BSWD` (interpreted JSON SHA-256 prefix
`5a309d4565fb58e7`); interpreted `100_RLWD` JSON SHA-256 prefix `41f33fb6d14201b0`;
`data/default physics.dat` SHA-256 prefix `e1fb3dedbeb29b4b`.

## Shared-stream consumers

`Random__NextLCGAbs` (`0x004de8d0`) has 154 direct call sites in 77 functions. Each
call site's generator object was classified from the last load of `ecx` before the
call. 137 sites in 74 functions use the gameplay generator at `0x008a9d9c`. The
others are:
- `CGame::ReceiveButtonAction` and `CGame::RespawnPlayer` (3 sites), which use a
  generator at `CGame+0x304`;
- `CMessageBox::RenderBattleLinePulseSprites` (12 sites), which uses a local one;
- two `CWorld::LoadWorld` sites (`0x0050cc62`, `0x0050cc8b`), which use a generator
  seeded locally at `0x0050cc3f`.

The site list is kept at
`local-data/test-runs/re-lane-20260925/rng-call-sites-20260926.tsv` (SHA-256
`4c953b3e5d2ea1e2b800a839d248dcb38ef5c887a7f6d08511e703e58d7650a8`). Every draw
named below is on the gameplay generator. Draw values are used as r mod 65536
unless stated.

## Load order

`CGame::InitRestartLoop` re-initialises the event manager for every level run
(`CEventManager::Init` `0x0044b060`, called at `0x0046c587`). It zeroes the time
`+0x8`, the current bucket `+0x10`, the frame counter `+0x14` and the ready slot
`+0x1c`, so construction runs at event time 0.0 in bucket 0.

1. `CWorld::LoadWorld(RLWD, base 0, init 1)` loads the base world first, through a
   recursive `LoadWorld(BSWD, base 1)` at `0x0050bbf5`
   ([loader owner](../binary-analysis/functions/World.cpp/CWorld__LoadWorld.md)).
   The base load:
   - allocates its 35 ordinary objects;
   - initialises the explicit trees: ferns are skipped by name, and each of the
     1,481 pines takes one shared draw and then queues collision 3000
     ([World 110 owner](world-110-initial-constructor-seeds.md#connected-base-tree-prefix-and-numerical-limits));
   - runs ordinary `Init` for rows 0-34 in file order. The career gate
     `DoesBaseThingExist(world, row)` (`0x0050cf8f`) passes every row on a fresh
     career.
2. The level world then allocates its 45 rows, reads past its tree tables and runs
   `Init` for rows 0-44 in file order, with no career gate.
   - Row 0 is the Start (type 15). `CStart::Init` (`0x004eae10`) ends in
     `CStart::SpawnBattleEngine` (`0x004eaf20`), which creates the Battle Engine
     and calls its `Init` inline (`0x004eaf6a`). So the Battle Engine's
     construction draws come straight after base-world row 34 and before level-world
     row 1.
3. `CPlayer` is allocated after `LoadWorld` returns (`0x0046cea9`/`0x0046cf2d`).
   `CGame::PostLoadProcess` then runs `CPlayer::Init` (`0x0046d1b3`) and sorts
   MapWho (`0x0046d23a`).

## Event placement

`CEventManager::AddEvent_AtTime` (`0x0044b370`,
[contract](../contracts/engine-world/CEventManager__AddEvent_AtTime__0044b370.md)):
- A request at or before now + 0.051 goes to the current ring bucket; a negative
  request is stored as now + 0.0001.
- A later request goes to bucket floor((t − now − 0.001) × 20), or to the overflow
  list beyond the 200-bucket ring.
- Each bucket keeps per-priority lists in insertion order.

Each `Update` (`0x0044b5c0`) advances the frame (time = frame × 0.05), saves the old
current bucket as the ready slot and flushes it: lists in priority order, each in
insertion order, then overflow events strictly earlier than now
([event owner](../binary-analysis/functions/CEventManager.cpp.md)). Bucket b is
therefore flushed at frame b + 1. The first flush after load delivers every
construction event that landed in bucket 0, in the order the rows below queued
them. Events queued while a flush runs go to the new current bucket and wait for
the next frame.

## Base-world rows

In file order, after the 1,481 pine draws. "draw" is one shared draw; events are
listed as queued. The following events all land in the current bucket: collision
3000 (relative −1), Actor MOVE 3000 (−1), Unit 4003 (−1), AI 3000 (now) and
animation 3000 (−1). Fire-control 4001 lands at now + (r mod 65536) × 0.1/65536.

| Rows | Class | Construction sequence |
| --- | --- | --- |
| 0, 1, 2, 13-16, 18-20, 23-29 | `CBuilding` | collision; draw (Actor); MOVE; 4003; AI 3000; animation 3000 |
| 17 (Solar Pod) | `CBuilding` | collision; draw (Actor); MOVE; 4003; animation 3000; AI 3000 |
| 3, 10, 11, 12 | `CCannon` | collision; draw (Actor); MOVE or LF_MOVE; draw (fire control); 4001; 4003; animation 3000; AI 3000 |
| 4-9 | `CFeature` | collision; draw (Actor); MOVE |
| 21, 22 | `CSafeSide` | nothing |
| 30-34 | `CSimpleBuilding` | collision; draw (Actor); MOVE; 4003 |

- `CBuilding::Init` (`0x00417190`) looks up `closed`, then `notshut`, and sets
  whichever it finds before its AI (`0x004172f8-0x00417315`); the first one found
  creates the animation owner and its 3000. The unconditional `Idle` call
  (`0x00417369`) creates it afterwards otherwise. Only the Solar Pod's mesh has
  `notshut`, so its animation event comes before its AI event. The Radar Station's
  and Docks' meshes have `idle` (mode 10), which changes the mode, not the events.
- A cannon's Actor event is MOVE 3000 or LF_MOVE 3001, chosen by its Actor draw
  (multiplier 4; [Actor owner](../binary-analysis/functions/Actor.cpp.md)). Its
  4001 lands in the load bucket when (r mod 65536) × 0.1/65536 ≤ 0.051, otherwise
  in bucket 1. The four turrets are inactive, so their animation is `Inactive`.
- `CSimpleBuilding::Init` (`0x004dfa40`) sets collision mask `0x08000020`, runs
  `CUnit::Init`, seats itself on the ground and joins occupancy. It creates no AI
  (`+0x13c` = 0) and no animation owner.
- `CSafeSide::Init` (`0x004de190`) sets its collision mask to −1 and clears flag
  bit 2 (no MapWho). With no script it queues nothing and draws nothing.

A thing binds its script in `CComplexThing::Init` through `SetScript`
(`0x004f4230`), before `CThing::Init` makes its collision component. A non-empty,
resolvable script queues INIT_SCRIPT 2001 at −1 (`0x004f42da`). No base-world row
has a script. `CThing::InitCollisionSeekingThing` (`0x004f39c0`) makes no collision
component when the collision mask is −1. `CActor::Init` runs `CComplexThing::Init`
(`0x00401343`) before its draw, so a unit's 2001 and collision come before its
Actor draw.

No Level 100 unit profile sets `CUnitSweeping` (profile `+0x19c`: apply
`0x00432e20`, default 0 at `0x0042f196`). So the AI constructor never takes its four
extra draws here.

Row 2's AI is `CRepairPadAI`; the others use the shared `CUnitAI`
([owners table](level100-final-drone-wave.md#ai-owners-that-draw-shared-rng)).
Buildings and cannons: [World 110 owner](world-110-initial-constructor-seeds.md#first-three-buildings-and-the-following-features),
[fire control](level100-final-drone-wave.md#fire-control-control).

## Level-world rows

In file order, after base-world row 34. "collision" includes the new component's
neighbour scan; the scan's later-time 2000s are listed under
[collision scans](#collision-scans).

| Rows | Class | Construction sequence |
| --- | --- | --- |
| 0 | `CStart` | nothing for the Start itself, then the Battle Engine: collision; draw (Actor); MOVE; 4003; draw; 6002; draw; 6003 |
| 1-4, 6-8, 10, 18, 22-38, 41-44 | `CWaypoint` | nothing |
| 5 (`LevelScript`), 17 (`Setup`) | `CLevelScriptThing` | 2001 |
| 9, 12 (`Target Tank`) | `CNormalSquad` with one `CGroundVehicle` | member: 2001; collision; draw (Actor); MOVE or LF_MOVE; 4003; draw (hover); 2003; AI 3000. Squad: draw; 4000; draw; 4001; draw; 4002 |
| 11 (`Warehouse`) | `CBuilding` | 2001; collision, with an overlap 2000 against row 9; draw (Actor); MOVE; 4003; 2003; AI 3001; animation 3000 |
| 13-16, 19 (zones, scripts) | `CSphereTrigger` | 2001; collision, with any overlap or approach 2000 |
| 20, 39 | `CSafeSide` | nothing |
| 21 (`U-17 Highside Transporter`) | `CDropship` | 2001; collision; draw (Actor); MOVE; 4003; animation 3000; 2003; AI 3000 |
| 40 (`Air Trainer`) | `CPlane` | 2001; collision; draw (Actor); MOVE; 4003; guide 2000; guide 2001; 2003; AI 3000; animation 3000; draw |

- **Waypoints.** `CWaypoint::InitAndLink` (`0x005057b0`) calls `CThing::Init`
  directly, so it binds no script, and its collision mask is −1.
- **Script carriers.** `CLevelScriptThing::Init` (`0x004900d0`) also sets mask −1.
- **Zones.** `CSphereTrigger::Init` (`0x004e5500`) sets mask `0x20`, so a zone
  gets a collision component after its script event.
- **Battle Engine.** Its Unit Init takes the Actor draw
  ([final-wave contract](level100-final-drone-wave.md#crosshair-and-auto-aim-refresh)).
  The spawn uses the Start's initializer, whose script is empty, so it queues no
  2001, and its spawn particle effect draws nothing from the shared stream. Its
  6002 lands in buckets 1-5 and its 6003 in buckets 3-5, so neither is in the
  first flush.

### Level-world units

**Class selection.** `0x00433010` stores slot 1 of the profile's behaviour object
(`0x0043ddc0`) at profile `+0xe0`: Target Tank 3 → 2, Warehouse 8 → 7, Air Trainer
9 → 8, U-17 12 → 12.
- Pass 1 asks `CreateSquad` (`0x0050f4b0`, called at `0x0050c999`) first:
  - selectors 1, 2 and 21 (and any above 25) get a `CNormalSquad` (0x144 bytes,
    constructor `0x004e6870`);
  - 0 and 3 get the 0xb4-byte squad (constructor `0x004e5da0`);
  - every other selector gets none.
- A squad row gets a `CSquadInitThing` (type 0x1c) naming one member (`+0x3bc` = 1)
  and sets squad `+0x84` = 1 (`0x0050ca0c-0x0050ca14`).
- Other rows are created by `0x0050df80`: selector 7 is `CBuilding` (vtable
  `0x005d8eb4`), 8 `CPlane` (`0x005e1930`) and 12 `CDropship` (`0x005e1dd8`). The
  squad's member, selector 2, is a `CGroundVehicle` (`0x005e297c`).
- Actor slot 24, the move multiplier, is 4.0 for `CGroundVehicle` (`0x0050e940`) and
  1.0 for the other three (`0x004de700`). With 4, r mod 4 of 0 or 1 queues MOVE 3000
  (counter 4) and 2 or 3 queues LF_MOVE 3001 (counter r mod 4 − 1).

**AI constructor** (`0x004fe710`, shared by every unit AI):
- state `+0x20` starts at −1;
- an init `+0x3b4` link takes a 3002 path instead (none of these rows has one);
- a unit with a script (`+0x74`, set by `SetScript` at `0x004f42cf`) gets 2003 at
  −1 (`0x004fe81d`);
- a target (init `+0xa4`) gives state 0 and 3001 at now; no target gives state 1 and
  3000 at now (`0x004fe8e3`).

All these events are priority 0. Base-world AIs have no script, so they queue
only their 3000.

**Target Tank rows** (`CNormalSquad::Init` `0x004e6bb0` → `CSquad::Init`
`0x004e5e70`):
1. The row is copied into a fresh `CUnitInitThing` (constructor `0x0048dcf0`:
   collision mask `+0x70` = 0, `+0x3b4` = 0). Because squad `+0x84` = 1, the member
   keeps `StaticTarget` and the squad's own copy is cleared (`0x004e6049-0x004e6087`).
2. The member is created by `0x0050df80` and initialised (slot 9, `0x004e616a`):
   `CGroundVehicle::Init` (`0x0047cfd0`) → `CGroundUnit::Init` (`0x0047c730`) →
   `CUnit::Init` (`0x004f86d0`). That gives 2001, collision, the Actor draw with
   MOVE or LF_MOVE, and 4003.
3. `CGroundUnit::Init` then takes the hover draw (`0x0047c869`), because profile
   `+0x10c` = 1 from `CUnitHover`: `+0x25c` = (r mod 65536) × 2π/65536.
4. `CGroundVehicle::Init` makes its motion controllers and `CGroundVehicleGuide`
   (`0x0047d590`) without events, then the AI (`0x0047d198`): 2003, then 3000.
5. `AddMember` (slot 67, `0x004e6183`) and the member position update (slot 20,
   `0x004e6199`) follow. Their prune calls pass 0, which skips the prune draw.
6. The squad's own `CComplexThing::Init` (`0x004e61b4`) runs with no script, mask −1
   and no MapWho entry.
7. `CNormalSquad::Init` then takes three draws:
   - `0x004e8100`: draw `0x004e8177`, then 4000 at now + 2.0 + (r mod 65536) × 2⁻¹⁵;
   - `0x004e83b0(1)`: draw `0x004e8486`, then 4001 at now + 1.0 + (r mod 65536) × 2⁻¹⁶;
   - slot 66 (`0x004e7070`): when `CSquadNormal::Process` (`0x004e7110`) returns 0,
     draw `0x004e709c` and 4002 at now + 0.99 + (r mod 65536) × 1.5258789e-7;
     otherwise 4002 at −1 with no draw.
8. `Process` returns 0 here, so each row takes five draws. Its return slot is
   written only at `0x004e7124` (0) and `0x004e79b5` (1), and `0x004e79b5` needs a
   destination more than 1 unit away or an active path:
   - The target search (`0x00477cb0`) reads list `0x008550c0`, the allegiance-1 and
     allegiance-6 things. Every row loaded so far has allegiance 0 or 2, so it finds
     nothing and `+0xc4` stays 0.
   - The destination `+0xf4` is the squad's own position (`0x004e6c89`).
   - The side-0 fear grid (`0x008a9d7c`, rebuilt by `0x0044c440` when
     `InitRestartLoop` creates it at `0x0046c657`, before loading) holds no
     occupancy yet, so the destination is not moved to a free cell.
   - The path length `+0xdc` is 0 from the constructor (`0x004e6909`).
   With the destination 0 units away and no path, `0x004e7881` skips to
   `0x004e79ca`, from which `0x004e79b5` is unreachable.

**Warehouse** (row 11, `CBuilding::Init` `0x00417190`):
- Its target is the row-8 waypoint, so its AI queues 3001, not 3000.
- Its mesh has neither `closed` nor `notshut`, so the animation owner comes from the
  `Idle` call after the AI.
- One draw.

**U-17** (row 21, `CDropship::Init` `0x00446d70` → `CAirUnit::Init` `0x00402ad0`):
- It compares the ground height at its position with its z (`0x00446e14-0x00446e21`).
  - When the height is greater (airborne), state `+0x27c` = 0 and it calls
    `SetAnimMode(wingflat)`.
  - Otherwise (grounded) the state is 6 and it uses `doorclosed`.
  - Row 21 starts at z −15.0. Either way the animation owner's 3000 is queued here,
    before the guide and the AI (`0x00446f28`: 2003, then 3000).
- One draw.

**Air Trainer** (row 40, `CPlane::Init` `0x004d19d0`), after `CAirUnit::Init`:
- the `CAirGuide` constructor (`0x00402150`) queues guide 2000 (`0x004021bf`) and
  guide 2001 (`0x004021e2`), both at −1, priority 0;
- the AI (`0x004d1a6a`): 2003, then 3000;
- `SetAnimMode(launch)` (`0x004d1ab2` or `0x004d1ae1`) creates the animation owner
  and its 3000;
- the Engine emitters make trail links without events;
- the last draw (`0x004d1bae`) sets `+0x284` to 0.8 when (r mod 65536)/65536 > 0.5,
  otherwise −0.8.
- Two draws.

None of the four profiles sets a turret turn rate (profile `+0xbc`), so none runs
fire control.

### Collision scans

`CCSPersistentThing::Init` (`0x004269b0`) queues the new component's readiness 3000
(`0x004269e3`). It then scans the MapWho neighbours through the detector at
component `+0x24` (`0x00480a30`, called at `0x004269ec`).
- A pair passes only when neither type word meets the other's mask (`0x00426900`).
  A passing pair goes to `0x00480ed0`, which takes gap = centre distance − radius
  sum.
- **Gap above 0.** When the two things' speeds (slot 15) sum to a nonzero value,
  2000 is queued at now + gap / sum, priority 1. Otherwise nothing is queued.
- **Gap 0 or below.** `HandleCollisionEnter` (`0x00480c90`) runs at once.
  - When the MapWho cell distance exceeds 1, it only sets the detector flag
    `+0x10`.
  - Otherwise, after an exact overlap test and both mask tests, it calls the
    response (component slot 6, `0x004264a0`), sets `+0x10` and dispatches again.
    That dispatch queues 2000 at −1, priority 1.
  - The response returns at once while the component's readiness bit (`+0xc` bit
    `0x400`, set by its 3000) is clear, as it is throughout construction.
- Both queue sites target the detector, with the other component as data:
  `0x00480fdc` reuses the detector's pending event and `0x00481044` takes a new one.

Results, from static positions:
- Static things all carry type bit `0x20` inside each other's masks, so the base
  world yields no 2000s.
- Target Zone 4 (row 16) sits on the Start and overlaps the Battle Engine: one 2000
  at −1, priority 1.
- The Warehouse (row 11) overlaps the row-9 tank (centre distance about 6.2, radius
  sum 8.92): one 2000 at −1, priority 1.
- The Firing Range (row 13) sees the two Target Tanks about 11.7-12.1 units away at
  speed 3.5, giving two later 2000s.
- The research pass found later-time pairs for the tanks (the base-world Docks,
  and for row 12 also row 9 and the Warehouse) and the U-17 (base-world Turret 04, a Pulse Turret);
  the Air Trainer pairs with nothing.
- The other zones see no mover. The Battle Engine's own scan (mask 0) may pair with
  nearby pines and buildings; that count is open.

## Allegiance at construction

A unit's allegiance `+0x138` is its initializer's `+0xa0`, copied by `CUnit::Init`
at `0x004f8fba`. For a world row `CInitThing::LoadFromMemBuffer` (`0x0040e280`)
reads it from the row, after the mesh number. `onsldef.msl` names 0 friendly,
1 enemy and 2 neutral.
- The physics file's `CUnitAlligence` is parsed, but its apply slot is the shared
  no-op `0x004014c0` (vtable `0x005d9d28` slot 1), so profiles never set it.
- Level 100 base world: the Control Tower, Tank Factory, Health Pad, Turrets
  01-04, Research Building, Radar Station, Airfield and Hangar are 0. The Forseti
  buildings, Solar Pod, Docks, tall and city buildings are 2.
- Level 100 level world: both Target Tanks, the Warehouse, the U-17 and the Air
  Trainer are 0. `StaticTarget`'s "Activate Static Targets" event later calls
  `SetAllegiance(ENEMY_ALLIGENCE)`.
- A squad takes the row value into `+0x7c` (`0x004e5eb4`); `Process` then copies
  its leader's `+0x138` (`0x004e714a`).
- `SpawnThing` (`0x00536cd0`) gives the new unit the allegiance of the script's
  owner (`[script+0x10]`) when that owner is a unit (`+0x34` bit `0x10`), and 2
  otherwise (`0x00536f69-0x00536f97`). Level 100's spawners run on the Tank
  Factory (`TankFactory`) and the Airfield (`Hangar`), both 0, so their tanks,
  trucks and drones start friendly until their own scripts call `SetAllegiance`.
- `CUnit::Init` lists a unit that is not in a squad in `0x008550c0` for
  allegiance 1 or 6 and in `0x008550b0` for 0 or 6 (`0x004f9182-0x004f91b2`);
  `CNormalSquad::Init` does the same for the squad by `+0x7c`
  (`0x004e6c55-0x004e6c7f`). A squad's target search reads the opposite list.

## The first flush

`CGame::RunLevel` (`0x0046e240`) runs `InitRestartLoop` (`0x0046e2c8`):
- It resets the event manager, then queues the game's FINISHED_PRE_RUN 2001 at
  now + 3.0, which lands in bucket 59.
- Loading follows (`LoadLevel` `0x0046dc74` → `LoadWorld`), with the Battle Engine
  built inside level-world row 0.
- `PostLoadProcess` (`0x0046dcf2`) assigns the engine and runs `CPlayer::Init`;
  neither queues nor draws through direct calls.
- The pre-run loop (`0x0046e040-0x0046e05d`) then calls `CGame::Update`, which
  calls `AdvanceTime` (`0x0046eb5d`): frame 1, time 0.05, ready slot = bucket 0.
  After the controllers it calls `Flush` (`0x0046ebce`).
- Nothing flushes during load; the only callers are `0x0046eb5d`, `0x00466bfe`,
  `0x0044b5f6` and `0x0046ebce`.
- The first flush delivers lane 0 of bucket 0 in queue order: the 1,481 pine
  3000s, the base-world rows' events in the order above, then the level-world rows'
  events.
- It then delivers lane 1: the Warehouse's overlap 2000 (row 11), then Target Zone
  4's (row 16).
  - Each delivery (`0x004812d0`) re-runs `HandleCollisionEnter` with both components
    now ready, so the response runs.
  - While the pair still overlaps, it queues another 2000 at −1, which lands in
    bucket 1.
- The pre-run lasts 60 frames; FINISHED_PRE_RUN arrives on frame 60.
- The retained Level 100 opening trace saw 1,713 live events in the manager at time
  0.05, during this flush
  ([AddEvent contract](../contracts/engine-world/CEventManager__AddEvent_AtTime__0044b370.md)).
  That is a live count at one instant, a consistency check rather than a total.

Draws taken by the level-world rows' lane-0 deliveries, in order:

| Row | Draws at delivery |
| --- | --- |
| 0 (Battle Engine) | 4003 |
| 9, then 11, then 12 | row 9: 4003, AI idle arm. Row 11: 4003, AI 3001. Row 12: 4003, AI idle arm |
| 21 (U-17) | 4003, AI poll |
| 40 (Air Trainer) | 4003, guide 2000, guide 2001, AI poll |

The U-17 and the Air Trainer poll because their scripts' 2001s, delivered earlier
in the same lane, switch their AI off (`SetAIState(AI_OFF)` → `0x004fdcb0` sets unit
`+0x210` = 1). The dispatcher (`0x004ff3fc`) reads `+0x210` through unit slot 53
(`0x00405e50`).

## Scripts in the first frames

No Level 100 script calls `Rand`. Scripts reach the shared stream only through
things they construct or wake.

The scripts named in world rows run their `init()` in the first flush: `LevelScript`,
`Setup`, the five zones, `StaticTarget` (rows 9, 11 and 12), `Transporter` and
`Flyby`. Their 2001s are in bucket 0.

`Setup`'s `init()` binds scripts in this order, each `SetScript` queuing a 2001 into
bucket 1 for frame 2 (`Setup.msl`):
1. Tank Factory → `TankFactory`;
2. Airfield → `Hangar`;
3. Turrets 01, 02, 03 and 04 → `Turret`;
4. Radar Station, Research Building 1, Health Pad and Control Tower → `Facilities`;
5. the player's Battle Engine → `BattleEngine`.

In the first flush:
- `LevelScript` records the objectives, disables flight mode and two weapons, and on
  a fresh career deactivates the player and waits on its first message.
- `Transporter` and `Flyby` switch their AI off and call `FollowWaypointWait`
  (`0x00537e40`). It passes the first waypoint to the unit's move-to (slot 61,
  `0x00403a90`, which sets the guide's goal) and suspends the script with a script
  2000 at −1, delivered in frame 2.
- The four `TargetZone` scripts deactivate their zones.
- `StaticTarget` has an empty `init()`, and no script defines the `ready()` event
  that 2003 calls.

At frame 2:
- `TankFactory`'s `init()` deactivates the factory and runs
  `SpawnThing("Target Tank", "SpawnerA", 1, "TargetTank1")`. That is the first
  script-driven construction, and its draws follow the construction laws above.
- `Hangar` deactivates the Airfield.
- `Turret` and `Facilities` have empty `init()` bodies.

## What each first delivery draws

| Event | Handler | Shared draws at delivery |
| --- | --- | --- |
| collision 3000 | collision component readiness (`0x00426a20`) | none ([World 110 owner](world-110-initial-constructor-seeds.md#connected-base-tree-prefix-and-numerical-limits)) |
| detector 2000 | `0x004812d0` → `HandleCollisionEnter` | none through direct calls; for a ready overlapping pair the response `0x004264a0` runs and its virtual callees are open |
| animation 3000 | animation `Process` (`0x00404790`), requeued at −1 | none ([World 110 owner](world-110-initial-constructor-seeds.md#initial-scheduled-listeners-remain-distinct)) |
| Unit 4003 | `CUnit::HandleEvent` (`0x004f98a8-0x004f9972`) | one, then requeue at now + 3.0 + (r mod 65536)/65536 ([final wave](level100-final-drone-wave.md#ai-owners-that-draw-shared-rng)) |
| fire control 4001 | `0x004fb280` | one, then requeue at now + (r mod 65536) × 0.1/65536 |
| AI 3000, polling owner | `CUnitAI::HandleEvent` (`0x004ff330`) | one (`0x004ff371`), then 3003 at now + 2.0 + (r mod 65536) × 2⁻¹⁵. An owner polls when inactive (`+0x214` = 0), in deploy state 1 or 2 (`+0x244`), or with its AI switched off (`+0x210` ≠ 0) |
| AI 3000, active owner | `0x004fec60` → `CUnitAI::Update` | the idle arm's one draw when there is no target (delay from `+0x110`), then 3000 again (`0x004fef33`); a squad member skips the movement step |
| AI 3001 (Warehouse) | `0x004feac0` | one (`0x004feb80`) when no target is found, then 3001 at now + 1.0 + (r mod 65536) × 2⁻¹⁶ |
| script 2003 | `0x005335a0` | none; it calls the script's `ready()` event |
| guide 2000 (Air Trainer) | `CAirGuide::HandleEvent` (`0x004026e0`) → `0x004028e0` | one (`0x00402762`), then 2000 at now + 0.5 + (r mod 65536) × 2⁻¹⁷ |
| guide 2001 (Air Trainer) | `0x004026e0` → `0x004027c0` | one (`0x00402705`), then 2001 at now + 0.5 + (r mod 65536) × 2⁻¹⁷ |
| INIT_SCRIPT 2001 | the thing's script VM | none directly (no Level 100 script calls `Rand`); natives such as `SpawnThing` construct things that draw |
| 6002 / 6003 | crosshair / auto-aim refresh | one each ([final wave](level100-final-drone-wave.md#crosshair-and-auto-aim-refresh)); not in the first flush |
| Actor MOVE 3000 | the class's `Move` (slot 66) | none for any Level 100 construction class (below) |

For the MOVE row, a direct-call reachability pass from each `Move` against the
census found the following. Virtual calls were not followed, except the dropship
guide below.
- `CBuilding` (`0x004178a0`), `CSimpleBuilding` (`0x004dfaa0`), `CCannon`
  (`0x0041b370`), `CGroundVehicle` (`0x0047d1c0`), `CPlane` (`0x004d1cd0`) and
  `CDropship` (`0x00447120`) reach no call site on the shared generator.
- `CFeature` (`0x0044cc10`) reaches its pickup draws (`0x0044cee0`) only while dying
  (`0x0044cc1b`).
- `CBattleEngine::Move` reaches `CalcUnitOverCrossHair` only through `HandleLocks`'
  eventless fallback, which draws nothing.
- The dropship guide update (`0x00448930`, guide slot 3) switches on the unit's
  `+0x27c`. It draws only in state 3 (`0x00448d4c`) and state 5 (`0x004491a1`), and
  the U-17 starts in state 0 or 6.

## Open questions

| Question | Cheapest falsifier |
| --- | --- |
| Whether this static order matches retail end to end, from the first pine draw through frame 2 | Log the return address of every `Random__NextLCGAbs` call on `0x008a9d9c` from level load through frame 2 in a copied runtime |
| What the response `0x004264a0` does in the first flush for the two overlapping pairs, including its virtual callees | Trace the response's virtual calls for `CBuilding`/`CGroundVehicle` and `CSphereTrigger`/`CBattleEngine` pairs, or read lane 1 in the draw log |
| Which pairs the Battle Engine's and the units' first scans find, and their 2000 times | Recompute the scans with the Level 100 heightfield in Core, or log `0x00480ed0` arguments during load |
| Whether the member position update (slot 20 at `0x004e6199`) or `AddMember`'s formation placement (`0x004e8730`) rescans collision | Static read of `CGroundVehicle` slot 20 and `0x004e8730` |
| Whether a native run by the frame-1 inits reaches the shared generator: `PrimaryObjectiveFailed`, `DisableFlightMode`, `DisableWeapon`, `Deactivate`, `PlayCharMessageWait`, `SetAIState` | Direct-call reachability from each native's handler, or the draw log above |
