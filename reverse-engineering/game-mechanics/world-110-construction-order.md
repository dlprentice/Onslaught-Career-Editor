# World 110 construction order, transition and first frames

Status: active static contract for the rebuild's World 110
Last updated: 2026-09-26
Summary: how a Level 100 win leads to World 110, the order in which World 110's
construction consumes the shared gameplay stream and queues events, what the first
flush delivers and draws, and when the player gains control.
Evidence: MEASURED static reads of the pristine specimen, the pinned GPL source, and
the shipped World 110 world files, mission scripts, meshes and `default physics.dat`.
Two read-only research passes traced the level-world rows. The RE lane re-read every
address, class, event, draw and profile value given here, and re-ran the squad
formation model. The squad target choices are a static calculation from positions and
scores. There is no runtime capture.
Specimen: pristine `local-lab/safe-copy-bea-pristine/BEA.exe.original.backup`, SHA-256
`74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`;
interpreted `110_RLWD` JSON SHA-256 prefix `495511efc7a8d412`; `110_BSWD` is
byte-identical to `100_BSWD`; `data/default physics.dat` SHA-256 prefix
`e1fb3dedbeb29b4b`; meshes `m_mtanklight` (`57b513c8`), `m_fpulsetank` (`80da933e`),
`m_m_dropship` (`f586cc84`), `m_muspfite` (`dd3be0da`).

The laws World 110 shares with Level 100 are in the
[Level 100 construction order](level100-construction-order.md) and are not repeated:
event placement, the flush, the Actor, Unit, AI, guide and squad events, the
influence map and the per-event draw table. The serialized rows are admitted in the
[World 110 seed contract](world-110-initial-constructor-seeds.md), and the player's
Start in the [player-start contract](world-110-player-start-admission.md).

## From a Level 100 win to World 110

- **The win.** `LevelWon()` (`IScript::LevelWon` `0x005381e0`) calls
  `CGame::DeclareLevelWon` (`0x0046f2f0`, `game.cpp:2384-2411`). Past game state 3
  (playing) it does nothing. Otherwise it:
  - stops controller vibration;
  - sets state 5 (won);
  - sets the end count `+0x48` to 5.0 (0 for levels 741 and 742);
  - pauses (`0x0046fb00`).
- **The end count.** Each `CGame::Update` in state 5 takes 0.05 from the count while
  it is not negative (`0x0046ec5a-0x0046ecd3`, `game.cpp:1997-2005`). The quit code
  `+0x34` becomes 1 (to front end) once the count is below 0, about 100 updates after
  the win. Retail adds a hold that the GPL source lacks: when the count reaches 0.05
  or less, it is held at 0.05 while `0x0089be58` is nonzero, or on levels 851-899
  while `0x0089be64` is nonzero. Both flags belong to the controller-reconnect
  routing.
- **Leaving the level.** `CGame::RestartLoopRunLevel` records the end-level data,
  including the base-world survivor list (`FillOutEndLevelData` `0x0046d470`, called
  at `0x0046e1cb`). `CGame::Shutdown` (`0x0046c990`) runs the outro-film check
  (`0x0046d9f0`).
- **The career.** The front end's `CFrontEnd::Init` calls `CCareer::Update`
  (`0x0041bd00`, at `0x00466315`). A won level marks its node complete, and
  `ReCalcLinks` promotes its outgoing links to state 1 and copies the survivor list
  into World 110's node bitmap
  ([carry-over](world-110-initial-constructor-seeds.md#level-100-to-world-110-base-world-carry-over),
  [career graph](../save-file/career-graph.md#retail-unlock-gate-steam-beaexe)).
- **The map.** The level-select page offers a world when `0x00461a50` passes: with
  the unlock-all cheat, for world 100, or when any incoming link of its node has
  state 1. The player starts World 110 there; it does not start by itself.
- **The new run.** `RunLevel` runs `InitRestartLoop` again (`game.cpp:292-410`):
  - it resets the event manager (`CEventManager::Init`, called at `0x0046c587`);
  - it queues FINISHED_PRE_RUN 2001 at now + 3.0 (`0x0046c5f0`), before any world
    is loaded;
  - it creates the fear grids;
  - it creates the gameplay stream afresh with seed 123456 (`0x0046c7e4-0x0046c80d`).

Only the career crosses between the two levels: node and link states, ranking and the
base-world survivor bitmap. The random stream, the event queue, the world and the
player are rebuilt.

## Load order

The loader is Level 100's.
1. World 110's 13 scripts load first, in file order (`LoadScriptEvents` at
   `0x0050bbde`).
2. The base pass loads the shared base world:
   - the 1,481 pines, one draw and one collision 3000 each;
   - the influence map: one draw (`0x0048bf0f`), 1000 at now + 1.0 +
     (r mod 65536) × 2⁻¹⁶, and 1002 at now + 0.5;
   - base rows 0-34 in file order, each gated by `DoesBaseThingExist` from the
     career. A base row that Level 100 lost is skipped. A lost building costs twenty
     damage-stamp draws instead
     ([carry-over](world-110-initial-constructor-seeds.md#level-100-to-world-110-base-world-carry-over)).
   On a full carry-over the base rows' sequences are Level 100's.
3. The level pass builds World 110's 40 rows in file order (below).
4. `LoadWorld` then reads the level world's settings. Words 3 and 4 are the pre-run
   and pan lengths, stored at `0x0050d2b8` and `0x0050d2c5`:
   - The pre-run value arrives after FINISHED_PRE_RUN was queued, so every level's
     pre-run lasts 3.0 s.
   - The pan length is used. It is 2.0 s for World 110 and 6.0 s for Level 100.
5. The tail runs `SpawnInitialThings`, one influence draw with its new 1000, and
   1001 at now + 0.25. World 110's scripts call no `SpawnThing`, so there are no
   warm-up units.

## Level-world rows

- "Col" is a collision component: its readiness 3000 at −1 and its neighbour scan.
- "A(m)" is the Actor draw with move multiplier m, then MOVE 3000 or LF_MOVE 3001 at
  −1.
- "FC" is the fire-control draw, then 4001.
- "U" is 4003 at −1, "H" the hover draw and "An" an animation 3000.
- "S" is INIT_SCRIPT 2001 at −1.
- "AI" is the AI constructor's events: 2003 at −1 when the unit has a script, then
  3000 at now. No World 110 unit row has a target, so none takes the 3001 path.

All events are priority 0 unless stated.

| Rows | Class | Construction sequence | Draws |
| --- | --- | --- | ---: |
| 0 (`LevelScript`), 2 (`Setup`), 39 (`Weather`) | `CLevelScriptThing` | S | 0 |
| 1 | `CStart`, then the Battle Engine | motion controller 3000; Col; A(1); U; cockpit 2001 (priority 2); receiver 4000 (priority 2); draw; 6002; draw; 6003 | 3 |
| 3, 4, 6, 7, 10, 11, 15, 21-24, 26-33 | `CWaypoint` | nothing | 0 |
| 5 | `CSpawnerThing`, inactive | 3000 at −1 (`0x004e3322`) | 0 |
| 8, 12, 20 (`Lander`, `Lander2`, `Lander`) | `CDropship`, Muspell Light Landing Craft | S; Col; A(1); turret child [Col; A(1); U; An; AI]; U; An; AI | 2 |
| 9 | `CSphereTrigger`, no script | Col | 0 |
| 13 (`Lander3`) | `CDropship`, Muspell Light Landing Empty | as row 8 | 2 |
| 14, 16, 18 | `CNormalSquad`, 5 × Light Gun Tank | 5 × [Col; A(4); FC; U; H; AI]; squad draws | 18, 17, 17 |
| 17 | `CNormalSquad`, 3 × AV-14B Sabre Pulse Tank | 3 × [Col; A(4); FC; U; H; AI]; squad draws | 12 |
| 19 (`Scout`) | `CNormalSquad`, 4 × AV-14B | 4 × [Col; A(4); FC; U; H; AI]; S; squad draws | 15 |
| 25; 34-38 | `CPlane`: Muspell Fighter; Muspell Light Fighter | Col; A(1); U; guide 2000; guide 2001; AI; An; draw (`0x004d1bae`) | 2 each |

- **Squad draws.** A squad takes the draws before its 4000 (`0x004e8177`) and its 4001
  (`0x004e8486`). When `Process` returns 0 it also takes 4002's draw (`0x004e709c`);
  otherwise 4002 is queued at −1 with no draw ([squads](#type-28-squads)).
- **Totals.** Under the static target estimate, the level rows take 102 draws and the
  tail takes one more.

### Type-28 squads

- **Loading.** A type-28 row builds a `CSquadInitThing` whose loader (`0x0048d8d0`)
  stores the amount at `+0x3bc` (the member count) and, for version 50, the mode at
  `+0x4c0`. The loader then calls `CreateSquad(profile +0xe0)` (`0x0050bd8a`); a null
  result would drop the row. Light Gun Tank and AV-14B are both behaviour 3 →
  selector 2 → `CNormalSquad` with `CGroundVehicle` members.
- **Scripts.** A type-28 row leaves squad `+0x84` at 0, unlike a type-8 squad row.
  - So `CSquad::Init` clears the member template's script and name (`0x004e6049-0x004e6076`),
    and members get no 2001 or 2003.
  - The squad keeps its own script: row 19's `Scout` is bound by the squad's
    `CComplexThing::Init` (`0x004e61b4`), after all its members.
- **Members.** Each member takes, in `CGroundVehicle::Init` order, the Actor draw
  (multiplier 4), the fire-control draw, 4003, the hover draw and the AI events.
  Fire control is on for every member:
  - Both profiles set a turret turn rate.
  - `CUnit::Init` inspects each weapon's emitter (`0x004f889a-0x004f89fb`), and each
    tank's main gun sits on `GunA` under a part named `barrel`:
    - Light Gun Tank: Light Cannon 88mm on `m_mtanklight`'s blaster < barrel < turret
      < Tank_Hull;
    - AV-14B: IS2 Pulse Cannon on `m_fpulsetank`'s Emit01 < barrel < turret <
      tankbody.
  - The secondary weapons on `GunB` have no barrel, which does not matter: one
    barrel is enough
    ([fire-control law](level100-final-drone-wave.md#fire-control-control)).
- **Placement.** Each member starts at the squad point. `AddMember` places it on a
  grid, and the squad's position update then moves every member onto its formation
  slot, rotated by the row's yaw (`0x004e9600`, columns = ceil(√n), `0x004e8730`).
- **Target at construction.** The squad's target search (`0x00477cb0`) reads the
  opposite side's list: allegiance 1 reads `0x008550b0`, allegiance 0 reads
  `0x008550c0`. Things built earlier are already on it:
  - the enemy squads (rows 14, 16 and 18) see the base world's allegiance-0 buildings
    and turrets, the Battle Engine and any friendly squad before them;
  - the friendly squads (rows 17 and 19) see the landing craft and the enemy squads
    before them.

  For a candidate whose stealth is 0 there is no range limit. The score is
  10 × priority + 1000 − distance (`0x00477eb1-0x00477ec5`), plus a range bonus from
  the lead unit's weapon (`0x004fb780`, `0x004fb7e0`):
  - 100000 between its minimum and maximum range;
  - 10000 beyond its maximum;
  - nothing inside its minimum.
- **`Process` at construction.** It returns 1 only when at least a third of the
  members are more than 1.5 × radius from their slots and the member centroid is
  within 20 × 0.06 × speed of the squad (`0x004e7cf0`, `0x004e7f40`). That needs a
  large facing change toward the target.

The static first targets and 4002 draws:

| Row | First target | Facing change | Far members | `Process` | 4002 draw |
| --- | --- | ---: | ---: | ---: | --- |
| 14 | Turret 04, 30.6 away, inside the 88 mm range band | 13.7° | 0/5 | 0 | yes |
| 16 | Turret 04, 54.0 (score 10956.0 against the Battle Engine's 10953.4) | 60.7° | 4/5 | 1 | no |
| 17 | row 14's squad, 60.7 | 13.2° | 0/3 | 0 | yes |
| 18 | Turret 04, 44.0 | 174° | 4/5 | 1 | no |
| 19 | row 14's squad, 24.4 | 17.3° | 0/4 | 0 | yes |

- **Row 16's margin.** It is 2.6 score points. With the Battle Engine as its target
  (76.6 away, 24.8°) no member would be far, and row 16 would take the draw.
- **Row 18.** Its alternative target, row 17's squad, gives the same result.

### Landing craft and their turrets

- **Classes.** Both landing-craft profiles are behaviour 12 → `CDropship` (vtable
  `0x005e1dd8`) with `CDropshipAI` (`0x005db1f4`) and `CDropshipGuide`
  (`0x005db228`).
- **Airborne start.** All four start above the ground, so each takes the airborne
  branch: state `+0x27c` = 0 and `SetAnimMode(wingflat)`.
- **Spawners.** Inside `CUnit::Init` the Landing Craft first copies its two attached
  spawners, with no events or draws: SpawnerA holds five Light Gun Tanks and SpawnerB
  two Muspell Grunts. The Empty craft has none.
- **Turret child.** The child ("Dropship Gun Turret", a `CComponent`, Init
  `0x00427b80`) is built after the parent's Actor draw: Col; A(1); U; An; AI. The
  four children are built in row order 8, 12, 13, 20.
- **No fire control.** The turret child runs none: its turn rate writes profile
  `+0xb8`, not `+0xbc`. The landers set a turret turn rate but carry no weapon, so
  there is nothing to inspect.

### Fighters, spawner and trigger

- **Fighters.** Rows 25 and 34-38 are behaviour 9 → `CPlane` with `CPlaneAI`
  (vtable `0x005de73c`). They have no script and no turret turn rate.
- **Spawner (row 5).** The inactive spawner sets mask −1 and makes no MapWho entry.
  - Its initializer's active word is 0, so `+0xa4` = 1 and its first-delay 3000 is
    skipped (`0x004e3118-0x004e3136`, `0x004e31e3`). Only the final 3000 at −1
    remains.
  - Its spawn script `MuspellFighter2` is stored but not bound.
  - No World 110 script activates it.
- **Trigger (row 9).** The sphere trigger (radius 50) has no script and only a
  collision component.

### Profiles that gate draws

In `default physics.dat` the three sweep and target-draw flags are set only on:
- Thunderhead, Warspite and Warspite Turret (`CUnitIndiscriminate`);
- Sentinel (`CUnitSweeping`);
- Arachnadrone (`CUnitIgnoreThreats`).

World 110 uses none of them. So its AI target searches never draw, and the AI
constructor's four sweep draws never run.

| Profile | Turret turn rate `+0xbc` | Hover `+0x10c` | Fire control |
| --- | ---: | ---: | --- |
| Light Gun Tank | 0.0698 | 1.0 | yes |
| AV-14B Sabre Pulse Tank | 0.0785 | 1.0 | yes |
| Muspell Light Landing Craft; Muspell Light Landing Empty | 0.01745 | 0 | no (no weapon) |
| Muspell Fighter; Muspell Light Fighter | 0 | 0 | no |
| Dropship Gun Turret (component) | 0 | — | no |

## The first flush and the first frames

The first flush (frame 1) delivers bucket 0 lane by lane, in queue order, as in
Level 100:
- lane 0 holds the pines' 3000s, then the base rows' events, then the level rows'
  events in the order of the table above;
- lane 1 holds any collision 2000s;
- lane 2 holds the Battle Engine's cockpit 2001 and receiver 4000.

The Battle Engine's 6002 and 6003, the squads' 4000 and 4001, the influence events
and the tanks' 4001s queued later than now + 0.051 are not in it.

### Script inits

From the shipped `.msl` sources:
- `LevelScript` deactivates the player (`GetPlayer(1).Deactivate()`). It then calls
  `PrimaryObjectiveFailed` and `SecondaryObjectiveFailed`, starts its first message,
  and loops on `Pause(1)` and `GetNumUnits`.
- `Setup` activates the Tank Factory and Turrets 01-04 (base rows 1, 3, 10, 11 and 12,
  all inactive at load). It also binds `VitalBuilding` to Forseti Research Building 1,
  whose 2001 lands in frame 2.
- `Weather` sets the snow density to 1.
- `Lander` (rows 8 and 20) sets AI state 4 (`AI_ONF`) and follows "Lander Path 1"
  (`FollowWaypointWait`, which suspends it).
- `Lander2` (row 12) sets AI state 4, then calls `Land()`, then sets AI state 0
  (`AI_ON`), then pauses.
  - `Land()` is `CDropship` slot 93 (`0x00447f50`). It lands where the craft is and
    sets landing state 2 through slot 118 (`0x00447a40`).
  - The native's guard (`+0x34` bit `0x10`) is set by `CUnit`'s `SetThingType`
    (`0x004fcdc0`) on every unit.
- `Lander3` has no `init()`. `Scout` has none either; it answers "game playing".

None of these natives reaches the shared generator through direct calls
(reachability from each handler against the census). Activate, Deactivate and Land
reach it through their virtual targets `0x004fd6a0`, `0x004fd700` and
`0x00447f50`/`0x00447a40`, which also reach no generator call.

### What the first deliveries draw

The base rows' deliveries are Level 100's
([per-event table](level100-construction-order.md#what-each-first-delivery-draws)):
- The Tank Factory, the four turrets and the Airfield are inactive when their AI
  events arrive, so each takes the polling draw (`0x004ff371`) and a 3003 at
  now + 2.0 + (r mod 65536) × 2⁻¹⁵.
- `Setup` activates all but the Airfield later in the same flush. The 3003 then
  requeues its 3000 at −1 (`0x004ff442`), so each first thinks one frame after its
  3003: frames 42-82.

The level rows' deliveries:

| Delivery | Draws |
| --- | --- |
| Unit 4003 (the Battle Engine, landers, turret children, tanks, fighters) | one, then 4003 at now + 3.0 + (r mod 65536)/65536 |
| Tank fire control 4001, when its delay put it in bucket 0 | one, then 4001 at now + (r mod 65536) × 0.1/65536 |
| Turret child MOVE (`CComponent` Move `0x00428110`) | one (`0x004284a1`); on its normal path it draws once per Move, and it moves every frame |
| Battle Engine, landing-craft, tank and fighter MOVEs | none. The dropship guide update draws only in landing states 3 and 5 (Level 100 table) |
| Fighter guide 2000 and 2001 | one each, then requeue at now + 0.5 + (r mod 65536) × 2⁻¹⁷ |
| Lander AI 3000, rows 8 and 20 (AI state 4) | two. The dispatcher (`0x004ff330`) calls `CDropshipAI::Update` (`0x004487e0`: draw `0x0044880f`), then polls (draw `0x004ff371`), then queues 3003 at now + 2.0 + (r mod 65536) × 2⁻¹⁵ |
| Lander AI 3000, row 12 (landing state 2) | one. Slot 9 (`0x00448580`) does nothing in state 2, then draws (`0x00448763`) and queues 3000 at now + 1.0 + (r mod 65536) × 2⁻¹⁶ |
| Lander AI 3000, row 13 (airborne) | one (`0x00448763`), same requeue. Its state-0 branch runs the target search (no draw) and steers |
| Fighter AI 3000 (`CPlaneAI` slot 9 `0x004d21c0`) | the Update's arm draw (see below), then one (`0x004d2434`) and 3000 at now + 0.25 + (r mod 65536) × 2⁻¹⁸ |
| Turret child and tank AI 3000 (`CUnitAI` slot 9 `0x004fec60`) | the Update's arm draw (see below) |
| Squad 4002 at −1 (rows 16 and 18) | none while `Process` still returns 1 |
| Spawner 3000 (row 5) | none; while inactive it re-polls every 0.1 s (`0x004e367d-0x004e36a9`) |
| INIT_SCRIPT 2001, 2003, collision 3000, animation 3000, motion controller 3000, cockpit 2001, receiver 4000 | none |

- **Update arms.** `CUnitAI::Update` (`0x004fef40`) draws once in its target arm
  (`0x004ff1aa`) or its idle arm, not in its fire-support arm. A target arm can also
  fire through slot 74.
- **What stays open.** Which arm each turret child, tank and fighter takes at its first
  think, and whether that think fires, depends on target selection and weapon charge
  (open questions below).
- **Landing-craft Update.** Its three unit calls reach no draw at the first think:
  - weapon charge (slot 86, `0x004fbcb0`);
  - can-deploy (slot 84, `0x004fc000`);
  - fire-or-spawn (slot 74, `0x004fc080`).
  They act only on a selected weapon `+0x140` or spawner `+0x144`, and no landing
  craft has one selected at construction; only `0x004fb840` sets `+0x144`.

### Later draw sources

- **Rows 8 and 20.** They take two draws per poll, every 2-4 s, while in AI state 4,
  until `FollowWaypointWait` returns and their script sets AI state 0.
- **Rows 12 and 13.** They think every 1-2 s with one draw, or poll every 2-4 s
  while `+0x244` is 1 or 2 (row 13's move order with no target sets 1,
  `0x004fdd4c`).
- **Landed craft.** A landing craft in landing state 3 or 5 also draws in its guide
  update on every Move (`0x00448d4c`, `0x004491a1`).
- **Fighters.** One draw per think, every 0.25-0.5 s, plus the Update's arm draw.
- **Turret children.** One draw per Move, every frame.
- **Tanks.** Fire control draws once per 4001 (every 0-0.1 s), and every unit draws
  once per 4003 (every 3-4 s).
- **Squads, influence map and Battle Engine.** Squad events, the two influence 1000
  chains, and the Battle Engine's
  [crosshair and auto-aim refresh](level100-final-drone-wave.md#crosshair-and-auto-aim-refresh)
  follow the Level 100 laws.
- **`VitalBuilding`.** When the Research Building first falls below 60% of its
  initial health, the script calls `Rand(3)`. `IScript::Rand` (`0x00538230`) takes
  one shared draw (`0x00538237`) and returns r mod n. The script's `switch` has no
  `break`, so case 0 plays all three warnings, case 1 the last two and case 2 the
  last one.

## Player start

- **Construction.** The Start (RLWD row 1) is at (264.75, 258.8125) with yaw −0.5195
  and plane mode 0. The engine is built in walker state, shields equal to energy,
  from the Aquila Prototype configuration. `CStart::Init`'s height clamp gives z
  −9.599889755249023
  ([player-start contract](world-110-player-start-admission.md#bounded-cstartinit-terrain-clamp)).
  Its construction draws and events are Level 100's (row 1 above).
- **First flush.** `LevelScript` deactivates it.
- **Frame 60.** FINISHED_PRE_RUN arrives. Its handler (`0x0046ff5a`) starts the pan
  because the pan length (2.0) is above 0: game state 2, `GotoPanView` for each
  player (`0x004d2c10`), and FINISHED_PANNING 2002 at now + 2.0 (`0x00470018`).
  - That event lands in bucket 60 + floor((5.0 − 3.0 − 0.001) × 20) = 99.
  - The player's own camera handoff 4000, at pan − 0.05, lands in bucket 98.
- **Frame 99.** The camera hands over to the first-person view.
- **Frame 100.** The FINISHED_PANNING handler (`0x00470024`, an inlined
  `StartPlayingState`; the standalone copy is `0x0046fec0`, `game.cpp:3025-3031`) sets
  game state 3 and posts "game playing".
- **Level 100 check.** The same arithmetic gives frame 180 (time 9.0) for its 6.0
  pan. That matches the measured change from panning to playing at 9.0 and the
  camera handoff at 8.95
  ([pan measurement](../binary-analysis/functions/Player.cpp/CPlayer__GotoPanView.md)).
- **Control.** The `Scout` script answers "game playing" with "Enemy Engaged".
  `LevelScript`'s handler then waits two seconds and activates the Airfield and the
  player. No weapon or flight mode is restricted.

## Open questions

| Question | Cheapest falsifier |
| --- | --- |
| The whole static order above, from load through frame 2 | Log the return address of every `Random__NextLCGAbs` call on `0x008a9d9c`, and every `AddEvent` call, during a copied-runtime World 110 load and its first frames |
| Each squad's first target (row 16's margin is 2.6 points) | Log squad `+0xc4` after load |
| Which arm each turret child, tank and fighter takes at its first think, and whether that think fires | The draw log above, or log AI `+0xc` and the owner's `+0x140`/`+0x1e8` at each first `0x004fef40` |
| The collision-scan 2000s (members 2..n start on the squad point; tanks near landers and Turret 04) | Log `0x00480ed0` arguments during load |
| Whether the Tank Factory's spawner is ready at its first active think | Read spawner `+0x3f4`, `+0x3ec` and `+0x3e0` at that point |
