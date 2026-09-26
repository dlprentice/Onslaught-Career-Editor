# Level 100 final drone wave, Help Player turrets and abort

Status: active contract for the rebuild's final-wave route; turret aim/fire law and
per-unit RNG ordering remain open
Date: 2026-09-25
Summary: the abort after one kill is a designed retail branch, but retail gives the
player two helps the rebuild lacks: four friendly turrets that come online after the
first poll below 80 % health, and the jet Missile Pod. Activated turrets can see the
enemy drones (original-code control, 16/16 cases). Every base-world Building and
Cannon owns an AI that draws shared RNG from level start.
Evidence: MEASURED — pristine instruction bytes read with objdump, shipped script
source and compiled script symbols, shipped physics/configuration records, and one
controlled original-code experiment; SOURCE — pinned GPL `references/Onslaught`
(`5352a81c`) for damage, shields, weapon creation and thing initialization. No
retail run was made; outcomes of whole fights are not measured.
Specimen: `local-lab/safe-copy-bea-pristine/BEA.exe.original.backup`, SHA-256
`74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`;
`data/default physics.dat` SHA-256
`e1fb3dedbeb29b4b4151da2c8cbbdc940b716b1a2321e1d6a9ba1542c74ada14`;
`data/battle engine configurations.dat` SHA-256
`58722b12a04cae97ad2163acb2cc2c1699f95a0688318bd8a86696714d94454a`;
`data/MissionScripts/level100/LevelScript.msl` SHA-256
`d51f8864564b5bde872092ec822df5af49daac16563f500719135f1a8c6c04a4`.

## Help and abort polling

The shipped script source is authoritative for control flow; the compiled
`LevelScript` in the Level 100 world carries the same constants (float `0.8` and
`0.4` symbols at source lines 45 and 47) and event strings.

- `LevelScript.msl:44-47`, in `init()`: `playerHelpHealth = 0.8 * GetHealth()` and
  `playerAbortHealth = 0.4 * GetHealth()`, captured once. The script native
  `GetHealth` (`0x00535920`) calls `0x004f99f0`, which returns absolute Unit life
  `+0xf8` (it defers to the segment controller when `+0x178` is set).
  `CBattleEngine` is a `CUnit` (`BattleEngine.h:72`). Aquila Prototype `mLife` is
  20.0 (configuration offset `0x2d6`), so a full-health start gives thresholds 16.0
  and 8.0.
- The poll runs inside `event("Reached Target Zone 3")` (`:248-282`). After
  `PostEvent("Activate Airborne Targets 2")`, both walker weapons are enabled and
  `PlayCharMessageWait(TUTORIAL_07)` blocks; `PlayCharMessage(TUTORIAL_STRAFE)` does
  not. Then `while (numTargets > 0)` reads `GetHealth()` twice per iteration: below
  help posts `"Help Player"` and scores −20 once; below abort posts
  `"Abort Airborne Drones"`, then `"Deactivate Turrets"`, and scores −50 once; then
  `Pause(1)`. Both comparisons are strict and both can fire in one iteration, help
  first. `Pause` schedules event 2001 at event time + 1.0 (`0x00537c70`).
- Kills: each drone's `died()` posts `"Airborne Target 2 Destroyed"` (event 2000 at
  next frame, [`CScriptEventNB`](../binary-analysis/functions/CScriptEventNB.cpp.md));
  `:284-295` decrements `numTargets` and at zero activates Target Zone 4 and completes
  objective 4. Equal-time events keep insertion order
  ([`CEventManager`](../binary-analysis/functions/CEventManager.cpp.md)).
- The abort handler (`:351-364`) sets `numTargets = 0`, disables all four player
  weapons, sets `aborted`, activates Target Zone 4 and plays `TUTORIAL_10`. Objective 4
  stays failed from `init()` (`:38`). `"Reached Target Zone 4"` plays
  `TUTORIAL_ABORTED` on this branch (`:305`) and still calls `LevelWon()`.
- `AirborneDrone2.msl` answers the abort with `SetAIState(AI_OFF)` and
  `SetAllegiance(FRIENDLY_ALLIGENCE)`.

The abort is therefore a released outcome, not a rebuild artifact. A six-kill,
no-abort requirement is a driver expectation, not a retail invariant.

## Help Player activates four friendly turrets

`event("Help Player")` (`:345-349`) is `PlayCharMessageWait(P_KRAMER,
TUTORIAL_HELP_PLAYER)` then `PostEvent("Activate Turrets")`. `Setup.msl` attaches
`Turret.msl` to `Turret 01`–`Turret 04`; its handlers call `Activate()` and
`Deactivate()`. If help and abort fire in the same poll, `"Deactivate Turrets"` is
delivered before the Kramer message ends, so the turrets end active; the drones are
friendly by then.

The four rows are in the base world, whose interpreted content is identical for
Level 100 and World 110 (both `*_BSWD.json` hash to `5a309d45…`). The lab mirror and
the rebuild's materialized static-world manifest (`17d6112a…`) agree:

| Row | Name | Profile | Position | Allegiance | Active |
| ---: | --- | --- | --- | ---: | ---: |
| 3 | Turret 03 | SAT Turret | (252.5, 261.2) | 0 | 0 |
| 10 | Turret 01 | Blaster Turret | (239.5, 266.5) | 0 | 0 |
| 11 | Turret 02 | Blaster Turret | (271.4, 240.0), yaw π | 0 | 0 |
| 12 | Turret 04 | Pulse Turret | (225.5, 282.0) | 0 | 0 |

`onsldef.msl` defines FRIENDLY 0, ENEMY 1 and NEUTRAL 2.

- Allegiance comes from the world row, not the physics profile: `CUnit::Init` copies
  initializer `+0xa0` to Unit `+0x138` (`0x004f8fb2`/`0x004f8fba`, EDI holding the
  initializer on every path). `+0xa0` is `CInitThing::mAllegiance`:
  `CBattleEngine::Init` compares it at `0x004051eb` to choose `m_be2`/`f_be2`, as
  `BattleEngine.cpp:161` does. The profile's `CUnitAlligence` value is not read here.
- Activity: the Unit constructor stores `+0x214 = 1` (`0x004f80aa`, `0x004f80e3`);
  `CThing::Init` calls `Deactivate()` for inactive rows (`thing.cpp:82-83`). In the
  `CCannon` vtable `0x005e24dc`, slot 22 is `0x004fd6a0` (sets `+0x214 = 1`) and slot
  23 is `0x004fd700` (clears it); both forward to `+0x148` and component children.
  The script `Activate` native (`0x00535d50`) calls slot 22.
- AI: `CCannon::Init` allocates a plain `CUnitAI` (`0x004fe710`, vtable `0x005d8d1c`)
  at `+0x13c`. With no waypoint or spawned-by reader it sets mode `+0x20 = 1` and
  queues event 3000 at the current event time (`0x004fe8cd-0x004fe8e3`).
- The AI event handler `0x004ff330`: event 3000 re-polls when the owner's AI state
  (`+0x210`, slot 53) is nonzero or its `+0x214` is zero, queuing event 3003 at
  time + 2.0 + r/32768 with one shared-RNG draw (`0x004ff36b`); 3003 queues 3000 for
  the next frame. An active owner runs slot 9 (`0x004fec60`), which calls
  [`CUnitAI::Update`](../contracts/unitai/CUnitAI__Update__004fef40.md) and requeues
  3000 at time + delay. Event 3001 likewise requires `+0x214`.
- Visibility: an allegiance-0 owner's close-target scan walks list `0x008550c0`
  (`0x004ff7a5-0x004ff7bb`). The Hangar's `SpawnThing` (`0x00536cd0`) gives each drone
  the Airfield's allegiance 0 (`0x00536f7a-0x00536f97`), so `CUnit::Init` lists it in
  `0x008550b0`. `SpawnThing` then calls `CreateSquad` with the Target Drone's selector
  8 (behaviour 9); the squad jump table (`0x0050f5bc`/`0x0050f5c8`) returns null, so
  the drone has no squad. Its `SetAllegiance(ENEMY)` reaches
  `CUnit::SetFactionForHierarchy` (`0x004fd830`), which removes it from both lists and,
  because it has no squad, appends it to `0x008550c0`.

### Original-code control

`python -P local-data/test-runs/level100-final-wave-20260925/turret_targeting_control.py`
passed **16 cases**. The ELF executes unchanged script `SetAllegiance`,
`SetFactionForHierarchy`, CSPtrSet add/remove, the close-target scan `0x004ff710`,
its state and side gates, `SetReader` and monitor registration at their retail
addresses; feasibility, capability and support helpers are recording stubs. Cases
cover squad-less relisting, squad members not relisted, allegiance 6 and 2, a
non-unit receiver, child recursion, list choice for both sides, the side gate,
strict range, the dying gate, nearest-of-two selection, B-false handling, and the
Level 100 order: a drone spawned friendly, switched to ENEMY by script, is then
selected by an allegiance-0 turret, while a squad-wrapped drone stays invisible.
Receipt `turret-run-1s9s58nr/turret_targeting.json` SHA-256
`6ff66c70ab7b0886163d5038e6e8cfd55eca4b0e574c43bea400195311b1602a`; ELF SHA-256
`7a6117d690170766e17e82dac1088ecd94871222c5abceadb0ace22743ebada3`. This measures
the list, allegiance and selection transaction only.

### Turret profiles

All three profiles have life 5.0 and behaviour 5 (`CCannon`).

| Profile | Range | Turret turn | Weapon | Weapon mode and round |
| --- | ---: | ---: | --- | --- |
| Blaster Turret | 60 | 0.17453 | M6 Blaster | Blaster 0.2 damage, 45/s; reload 3.0, burst 5 × 0.1, volley 2, range 60, yaw tolerance 0.0873, inaccuracy 0.00436, `CWeaponTrack` 1 |
| SAT Turret | 80 | 0.0698 | SAT Launcher | SAT 1: 0.5 + `SAT Hit` radius 2.0 damage 0.5, 14/s, turn 0.0785, seek 2, seek delay 2.0, seek angle 0.2618, weirdo seek, life 10; reload 10, burst 8 × 0.1, range 130, minimum target height 3.0, yaw tolerance 0.349 |
| Pulse Turret | 60 | 0.17453 | IS3 Pulse Cannon | Pulse Bolt Medium; reload 2.5, range 1–60, **maximum target height 3.0**, yaw tolerance 0.0873 |

The Pulse Turret cannot engage airborne drones; the two Blaster Turrets and the SAT
Turret can. None of these rounds is smart and `SAT Hit` has no smart filter, so a
stray round or blast can damage the player; turrets never select the player.

## Drones and the player

Target Drone (`default physics.dat` offset `0x24e76`): life 1.0, no shields on it or
its `Base Air Unit` parent. `GunA` is Drone Vulcan Cannon (Blaster 0.2, `Small Energy
Hit` radius 0 so no blast damage, burst 8 × 0.15, reload 1.0 from burst start, range
40, inaccuracy 0.01745, yaw tolerance 0.1745, pitch ±0.785). `GunB` is Forseti Drone
Missile Launcher (Forseti Missile 2.0 plus `Micro Missile Hit` radius 1.0 damage 0.5,
15/s, turn 0.04887, seek 3, seek delay 0.1, seek angle 0.785, life 10; reload 10,
range 20–80, yaw tolerance 0.349). Explosions scale as `((R − d) × D) / R`
([round hit](../binary-analysis/cround-hit-damage-path-2026-08-10.md)).
`CUnit::ApplyDamage` scales only deploy states and weakpoint parts
([owner](../binary-analysis/functions/Unit.cpp/CUnit__ApplyDamage.md)).

Player damage routes through `CBattleEngine::Damage` (`BattleEngine.cpp:2127-2240`).
Jet movement zeroes shields every update (`BattleEngineJetPart.cpp:499`), so jet
hits reach life in full. Walker movement sets shields to energy
(`BattleEngineWalkerPart.cpp:391`); while shields cover a hit, 98 % goes to shields
(Aquila `mShieldEfficiency` 98.0 at configuration offset `0x30b`, energy 8.0).

Player weapons against a 1.0-life drone:

| Weapon | Mode and round | Hits to kill |
| --- | --- | ---: |
| Pulse Cannon Pod (walker) | Mech Pulse Bolt Medium 0.8 + hit radius 0.5 damage 1.0; reload 0.1, 35/s | 1 |
| Mech Twin Vulcan Cannon (walker) | Mech Bullet 0.08 + 0.001; volley 4 per 0.05 | 13 |
| Mech Vulcan Cannon (jet) | Mech Air Bullet 0.15 + 0.001; volley 2 per 0.05 | 7 |
| Missile Pod (jet) | Micro Missile 1.5 + radius 1.0 damage 0.5, 15/s, turn 0.0349, seek 2, seek delay 0.05; burst 5 × 0.1, reload 0.8, lock time 0.2, lock range 100, 5 locks; charge level 1 salvo: burst 10 × 0.05, 10 locks, lock radius 20 | 1 |

Aquila Prototype's jet list is Mech Vulcan Cannon then Missile Pod (configuration
offsets `0x340`, `0x353`). `CBattleEngineJetPart::ResetConfiguration` creates every
configured jet weapon with no career gate (`BattleEngineJetPart.cpp:976-1000`), and
`LevelScript.msl` disables the Missile Pod only in the abort handler (`:357`). The
lock path is pinned source (`BattleEngine.cpp:640-1000`).

## AI owners that draw shared RNG

Every base-world `CBuilding` constructs an AI: `CBuilding::Init` calls `0x00417390`
unconditionally (`0x00417347`), which builds a plain `CUnitAI` unless the profile
name is `Forseti Repair Pad`, which gets `CRepairPadAI` (vtable `0x005d8e08`). Features
and `CSimpleBuilding` have none.

| Base-world rows | Class | AI | Active at start |
| --- | --- | --- | --- |
| 0 Control Tower, 13 Research Building, 14–19 Forseti Buildings and Solar Pod, 20 Radar Station, 24 Docks, 25 Hangar, 26–29 Tall Buildings | `CBuilding` | `CUnitAI` | yes |
| 2 Health Pad | `CBuilding` | `CRepairPadAI` | yes |
| 1 Tank Factory, 23 Airfield | `CBuilding` | `CUnitAI` | no |
| 3, 10, 11, 12 turrets | `CCannon` | `CUnitAI` | no |
| 4–9 icebergs, 30–34 city buildings, 21–22 type 37 | Feature, `CSimpleBuilding`, not created | none | — |

Level-world and spawned units also own AIs: Target Tank and Target Truck
(`CGroundVehicle`, squad-wrapped when spawned by the Tank Factory), Warehouse
(`CBuilding`), U-17 Highside Transporter (`CDropship`), Air Trainer and Target Drone
(`CPlane`, squad-less).

Each AI queues event 3000 at its construction time. An inactive owner then draws
once per re-poll, every 2.0–4.0 s plus one frame. An active owner with no target
takes `Update`'s idle arm: one draw and a delay of 1.5 + r/65536 s when owner `+0x110`
is nonzero, otherwise 3.0 + 2r/65536 s. `+0x110` is written by the Unit 4003 handler
from camera distance ([owner](../binary-analysis/functions/Unit.cpp/CUnit__HandleEvent.md)).
`0x004fec60` exits without requeueing when the owner is dying, in deploy state 1 or 2,
or in AI mode 0. These draws share the gameplay stream with each Unit's Actor Init
draw and 4003 draw; the [World 110 owner](world-110-initial-constructor-seeds.md)
already orders rows 0–9 of this same base world.

## Open questions

| Question | Cheapest falsifier |
| --- | --- |
| Turret aim and fire law: turret/barrel rotation (`CMCCannon` `0x004952a0`), fire gates A/B, bursts and volleys against a moving drone | Static read of `0x004952a0` and the Unit fire path with the existing weapon contracts, then an original-code composition with a `CCannon` owner |
| Whether turret barrels enable the fire-control refresh (`CUnit::Init` `+0x224`), which adds event 4001 and one draw per refresh | Read each turret mesh's `GunA` part chain for barrel markers |
| Exact first-flush order of all AI, 4003 and Actor draws in Level 100 | Extend the World 110 construction order to all base rows and the level-world rows |
| Whether the Hangar AI's all-squads spawning probe runs (owner `+0x188`) | Read the Hangar and Airfield spawner uses and `0x004fda90` |
| How often stray turret rounds hit the player | A copied-retail observation once David releases the desktop |
| Whether retail aborts on a given player trajectory | Not reproducible without a retail run of the same inputs |
