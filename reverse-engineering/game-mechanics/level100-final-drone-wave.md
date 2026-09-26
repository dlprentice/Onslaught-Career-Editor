# Level 100 final drone wave, Help Player turrets and abort

Status: active contract for the rebuild's final-wave route; per-unit RNG ordering
across the whole level remains open
Date: 2026-09-25
Summary: the abort after one kill is a designed retail branch, but retail gives the
player two helps the rebuild lacks: four friendly turrets that come online after the
first poll below 80 % health, and the jet Missile Pod. Activated turrets can see the
enemy drones (original-code control, 16/16 cases). Every base-world Building and
Cannon owns an AI that draws shared RNG from level start, and all four turrets run
a fire-control refresh that draws once per event 4001 from construction onward
(original-code control, 21/21 cases).
Evidence: MEASURED — pristine instruction bytes read with objdump, shipped script
source and compiled script symbols, shipped physics/configuration records and
turret meshes, and two controlled original-code experiments; SOURCE — pinned GPL `references/Onslaught`
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

### Fire-control control

Every turret mesh enables Unit fire control. `CUnit::Init` inspects the weapon's
`Gun*` emitter part (`CMesh::FindPartField40ByNameAndOwner`, `0x004aa820`, returns
emitter `+0x40` for a name and selector) and climbs its parent links (`+0x98`, set
from the file's parent index by the mesh loader at `0x004a730a-0x004a7313`) when
profile `+0xbc` is positive (`CUnitTurretTurnRate` stores it at `0x00432b17`). A part
named exactly `turret`, or starting `X1 Turret` in any case, sets weapon `+0x94`; a
part starting `barrel` (case-sensitive) or `X1 Barrel` sets Unit `+0x224`, weapon
`+0x98`, barrel pointer `+0x220` and rest angle `+0xf4`.

| Mesh | `GunA` selector 1 part | Parent chain | `+0x224` | Turret flag |
| --- | --- | --- | ---: | ---: |
| `m_ft_blaster` (`9833cd45…`) | `Emit01` (9) | `arse`, `barrel` (4), `turret` (2), `turretbase`, `base` | 1 | 1 |
| `m_ft_sam` (`9a82f274…`) | `Emit01` (11) | `barrel` (3), `support`, `turretbase`, `base` | 1 | 0 |
| `m_ft_pulse` (`1cc39993…`) | `Emit01` (6) | `barrel` (5), `turret` (2), `turretbase`, root | 1 | 1 |

The refresh `CUnit::UpdateFireControlYawAndQueueEvent` (`0x004fb280`) returns at
once when `+0x224` is zero or the Unit is dying. Otherwise it aims `+0xec` with the
ballistic solver when the AI has a target (deadline `+0x20c` = time + 10.0), restores
the rest angle when the deadline has passed, clamps to [−π/2, π], takes **one** shared
draw and queues event 4001 at time + (low16 × 0.1/65536), which delivers the next
refresh (`CUnit::HandleEvent`). It never reads the active flag `+0x214`. `CUnit::Init`
calls it once at `0x004f90ce`, so each turret takes one draw at construction and then
roughly one per frame or two for the whole level, active or not.

`python -P local-data/test-runs/level100-final-wave-20260925/turret_fire_control_control.py`
passed **21 cases**. The ELF runs the unchanged inspection range
`[0x004f889a,0x004f89fb)` with its jump table, the emitter lookup, CRT `stricmp`,
`_strnicmp` and `_strncmp` (C-locale fast path supplied), the refresh body and
`Random__NextLCGAbs` against part and emitter structures built from the three
shipped meshes by the repository parser; the Euler constructor and `AddEvent` are
recording stubs. Controls cover zero turn rate, a missing `GunB` emitter, the Pulse
`GunB` chain (turret without barrel), a capitalised `Barrel` and `Turret`, an
`x1 barrel` prefix, a missing selector 1, lookup through a linked mesh, disabled and
dying refreshes, both clamps, active and inactive owners, and two consecutive draws
matched against an exact int32 model of the shipped generator. Receipt
`fire-control-run-ob8ydblf/turret_fire_control.json` SHA-256
`4efecff6d05e6a33a408fff564688ab96b21d245d58fc09e3596bc104245efe2`; ELF SHA-256
`0a6ff38de4811e088cd116327ea89b9174c0582b4e3f441cf43592f2a2178683`. The first run
failed only because its generator model lacked 32-bit wraparound for a deliberately
out-of-range seed; that run is retained beside it.

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

### Turret aiming

Cannons use Actor multiplier 4 (`CCannon` vtable `0x005e24dc` slot 24 is
`0x0050e940`, returning 4.0), so a full MOVE runs every fourth frame, phased by the
Actor Init draw ([Actor owner](../binary-analysis/functions/Actor.cpp.md)); let
M = 4.0. `CCannon` Move (slot 66, `0x0041b370`) reaches
`CUnit::UpdateMotionAttachmentsAndEffects` (`0x004fa8d0`) through `0x0047c970`.
Each call:

1. Saves turret yaw `+0xe0` to `+0xe4` and barrel pitch `+0xe8` to `+0xf0`
   (`0x004fad00-0x004fad17`). `CMCCannon` (`0x004952a0`) draws the yaw between
   `+0xe4` and `+0xe0` and applies the pitch between `+0xf0` and `+0xe8` to parts
   whose names start with `barrel`.
2. Skips steps 3 and 4 unless the AI exists, the dying bit (`+0x2c` bit 2) is
   clear and slot 109 (`0x00405e70`, true when `+0x168` is null) returns true.
3. Turret yaw (`0x004fad4f-0x004fafe3`). With an AI target the aim point is the
   target's slot 90 midpoint, taken relative to the pivot: Unit position `+0x1c`
   plus the orientation rows at `+0x3c` and `+0x4c` applied to offset `+0x1f8`
   (copied by `CUnit::Init` from mesh part 2 when a `turret` part exists; SAT has
   none, so its offset is zero). Desired = −atan2(dx, dy) − body yaw (slot 92,
   `+0x114`) and the deadline `+0x20c` becomes time + 10.0. Without a target the
   desired yaw is 0.0 once the deadline is strictly past, otherwise the current
   yaw. Desired is wrapped once into [−π, π] and clamped to ±M × profile `+0xdc`.
   Let s = M × profile `+0xbc` (`CUnitTurretTurnRate`). The yaw snaps to desired
   when |current − desired′| ≤ s, where desired′ is desired − 2π when current
   < −π/2 and desired > π/2, desired + 2π when current > π/2 and desired < −π/2,
   and desired otherwise. Otherwise it moves by s, upward when
   0 < desired − current ≤ π or current − desired > π and downward in the other
   cases, is wrapped once into [−π, π] and is clamped to ±`+0xdc`. The profile
   defaults (`0x0042efd0`, stores at `0x0042f0ff-0x0042f110`) set `+0xdc` to 2π,
   so neither clamp bites for these turrets.
4. Barrel pitch (`0x004fafe5-0x004fb04d`), only with `+0x224`: snaps to `+0xec`
   when |`+0xe8` − `+0xec`| ≤ M × `+0xbc`, otherwise steps by that amount toward it.

The desired pitch `+0xec` comes from the fire-control refresh, not the Move. With
an AI target and a current weapon, mode and round, the refresh stores the solver
result at `0x004fb302`. The solver `0x005094b0` takes its no-gravity branch
(`0x00509529-0x00509557`) when the round's `CRoundGravity` `+0x3c` is zero or its
beam or torpedo flag is set. `CRoundData__CreateAndRegisterByName`
(`0x0042ffa0`) defaults all three to zero (`0x004300fc`, `0x0043011f`,
`0x00430108`) and none of the Blaster, SAT 1 or Pulse Bolt Medium records sets
them. The pitch is therefore asin(dz/|d|) from the Unit position `+0x1c`
(`CCannon` slot 113 is `0x00405eb0`, a copy of `+0x1c`), or 0.0 when |d| is 0.
The helper `0x0055dcb0` is the CRT asin: it computes atan2(x, √(1 − x²)), returns
±π/2 at |x| = 1 and names `asin` in its error record at `0x00653310`.

Fire gate A ([`0x00507ab0`](../binary-analysis/functions/IScript.cpp.md)) takes the
weapon's facing from the body orientation plus turret yaw `+0xe0` when the weapon's
turret flag is set (Blaster, Pulse), its elevation from `+0xe8` with the barrel
flag (all three), and fires only when the yaw error is below
`CWeaponYawTolerance`. Selection, preparation, readiness and firing are the shared
Unit chain already contracted for aircraft
([controller owner](../binary-analysis/functions/CComplexThing.cpp.md#remaining-selected-provider-integration)).

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
`LevelScript.msl` disables the Missile Pod only in the abort handler (`:357`).

### Missile Pod locks

`CBattleEngine::Move` (`0x004081c0`) calls `HandleLocks` (`0x00406560`) at
`0x00408b84` on every Move while the Battle Engine is not dying
(`BattleEngine.cpp:1330-1476`); its Actor multiplier is 1 (vtable `0x005d89c4` slot
24 is `0x004de700`, returning 1.0), so that is every frame. `HandleLocks` returns
at once while the current part is firing (`0x00414b30`) and otherwise follows
`BattleEngine.cpp:586-760`, with these retail specifics:

- Every lock parameter comes from the weapon's current mode. Each getter rounds
  charge `+0x60` with `fistp`, divides by 100 with truncation and takes that
  level's mode from the weapon profile, falling back to lower levels when an entry
  is missing: `0x00506350` maximum locks `+0x90`, `0x00506440` lock time `+0x94`,
  `0x00506620` lock deflection `+0x98`, `0x00506710` lock range `+0x9c`,
  `0x00506800` lock radius `+0xa0`, `0x00506530` lock mode `+0xa8`.
- Both pod modes store `CWeaponLockMode` 0, direct. The dispatch at `0x0040682b`
  sends 0 to `0x00406b1f` (crosshair unit), 1 to `0x00406a5e` (proximity) and 2
  to `0x00406842` (sequence).
- The lock-loss pass (`0x00406724`) and direct acquisition (`0x00406ce4`) compare
  the normalised heading's forward component with cos(`CWeaponLockDeflection`),
  where the source uses `GetMaxDeflection`: −0.34906584 for the launcher (cos
  0.9396926) and −0.69813168 for the salvo (cos 0.7660444). A new lock needs the
  forward component strictly greater.
- Direct acquisition uses the crosshair unit `+0x4c8`, or the outer-sphere probe
  below when that is null. It skips units already locked, applies the side gate
  `0x004fd3d0` and `CanLock` (`0x005061f0`), requires distance² < (lock range ×
  (1 − stealth × 0.01))² with stealth from the target's slot 91, and then starts a
  lock for the mode's lock time (`0x00406fc0`).
- `CanLock` requires the target's active flag `+0x214`; `+0x228` clear unless the
  target profile's `+0x12c` is set; `+0x22c` clear; a nonzero profile `+0x114`; and
  a nonzero intersection of the target's thing type `+0x34` with the mode's
  `CWeaponLockUnit` `+0xa4`. Both pod modes carry `0x000e8400`, which includes the
  air-unit bit `0x400` that every `CPlane` has (its type mask is `0x40000400`).
- The burst spawner calls `FireLock` (`0x00407060`) from `0x005074c9` with the
  Battle Engine's current target (slot 81, `0x004071b0`, the source's
  `GetCurrentTarget`); a finished lock moves to the fired set with a 0.5 s window
  ([owner](../binary-analysis/functions/BattleEngine.cpp/CBattleEngine__FireLock.md)).

### Crosshair and auto-aim refresh

Both refreshes exist in retail and draw from the shared gameplay stream.

- `CBattleEngine::Init` (`0x00404dd0`) queues event 6002 (`CALC_UNIT_OVER_CROSSHAIR`)
  at `0x004058b2`, after `0x00406460` and before `HandleAutoAim`, for time + 0.1 +
  (r mod 65536) × 0.2/65536 at priority 0 (start of frame), taking one draw at
  `0x0040586e`.
- `CBattleEngine::HandleEvent` (`0x0040c180`) sends 6002 to
  `CalcUnitOverCrossHair(event, TRUE, TRUE)` (`0x0040acc0`) and stores the result
  in `+0x4c8`. Every call with an event requeues 6002 the same way with one draw
  (`0x0040b091`), whether or not a player is attached.
- `CalcUnitOverCrossHair` casts a 1000-unit line from the player's view point
  along the view orientation times the auto-aim matrix, ignoring the Battle Engine
  itself, trees (`0x2000000`) and rounds (`0x4`). It returns a unit that is not a
  lifeless building, when the weapon's actual maximum range (1000.0 when not
  positive) exceeds the hit distance. The event path also stores the unit
  regardless of range in `+0x4cc`.
- The line query `CWorld::FindFirstThingToHitLine` (`0x0050b030`) first traces the
  heightfield (`0x00490a40`). A terrain hit records class 1 and its distance, and a
  thing counts only when it is strictly nearer. Candidates skip the ignored thing,
  things with `+0x2c` bit `0x10`, masked types and dying non-buildings. Each must
  have a collision shape whose sphere the line intersects (`0x004780f0`); its
  distance is |sphere centre − line start| − radius (thing slot 17).
- The event path (level 2) replaces that distance with a mesh test whenever the
  shape has mesh data. The `HandleLocks` fallback (level 0, mesh flag 0) accepts
  the sphere result and draws nothing. The nearest candidate wins, and the call
  returns 3 for a thing, 1 for ground and 0 for nothing.
- `HandleAutoAim` (`0x0040b6d0`) runs once from Init and then on each event 6003.
  When `GAME+0x20` (`0x008a9ab8`) is zero it clears the auto-aim offsets and
  returns without requeueing. `CGame::InitRestartLoop` sets it to 1 at every level
  start (`0x0046c4c2`; the global `CGame` is `0x008a9a98`), and only the pause
  menu (`0x00472d1b`/`0x00472d2f`) changes it. Otherwise it ends with one draw
  (`0x0040bf57`) and queues 6003 for time + 0.2 + (r mod 65536) × 0.1/65536.

Battle Engine construction therefore draws three times: the Actor draw inside
its Unit Init (called at `0x004054c6`), then 6002, then 6003. Afterwards each
6002 delivery takes one draw, and each 6003 delivery takes one while auto-aim
is allowed.

### Seeking rounds

SAT 1, Micro Missile and Forseti Missile are plain `CRound`s (no missile, beam or
torpedo flag), moved every frame by `CRound::Move` (`0x004d8e40`; `CRound` vtable
`0x005de82c` slot 24 returns 1.0). The only value compare on `CRoundSeek` in round
or weapon code is `== 1` at `0x004dac9c`, the self-acquire selector; every other
reader tests only nonzero. Seek modes 2 and 3 both keep the launch target and
never self-acquire.

- With `CRoundWiggle` `+0x38` above zero every Move first takes two shared draws
  (`0x004d8ffc`, `0x004d9036`).
- For a damaging round a bound non–Battle Engine target is released when its
  dying bit is set or its slot 104 returns zero (`0x004d9382-0x004d93c7`).
  `CUnit` slot 104 (`0x00417630`) returns profile `+0x114`, or 1 without a profile.
- A Battle Engine target is released when within 15 units (squared distance
  below 225.0) and its slot 104 returns zero.
- Steering (`0x004d93cc-0x004d9838`) requires nonnegative damage, a positive turn
  rate, a bound target, seek delay < age and age < `CRoundSeekTerminationTime`
  (default 1000.0, `0x004300e3`).
- Let f be the forward component of the normalised direction to the target's aim
  point in the round frame, and c = cos(`CRoundSeekAngle`). A round without
  `CRoundWeirdoSeek` steers when f ≥ c and otherwise drops the target
  permanently, unless it is a torpedo.
- SAT 1 has `CRoundWeirdoSeek` (`+0x54`). It keeps the target and does the
  opposite: it holds its course while f ≥ c and steers only when f < c
  (`0x004d95c8-0x004d95d6`).
- Steering turns by the yaw error −atan2(x, y) and the pitch error
  atan2(z, √(x² + y²)), each clamped to ±turn rate.
- Whenever a round owned by a Battle Engine releases its target, including
  `CRound::Shutdown` on impact (`0x004d8e00`), it calls `LockHit` (`0x00407140`;
  the six callers are `0x004d8e00`, `0x004d9351`, `0x004d93a7`, `0x004d959a`,
  `0x004daafc` and `0x004dab6b`).

### Shared-stream draws by rounds and weapons

Every `Random__NextLCGAbs` call in the round, weapon, fire-control, AI, crosshair
and auto-aim paths above loads `ecx` from `0x008a9d9c`, the single gameplay
generator. Player and enemy rounds use the same code and stream.
`ProjectileBurst__SpawnFromCurrentPreset` (`0x005069f0`) loops over
`CWeaponVolleySize` (`+0x48`) rounds per burst event and, for each one:

- takes two draws (`0x00506e0a`, `0x00506e3e`), whatever the inaccuracy, scaling
  (r mod 65536) × 2/65536 − 1 by `CWeaponInaccuracy` `+0x34` for pitch (first) and
  yaw (second);
- takes one more (`0x00507453`) only for a `CRoundFlak` round whose owner target
  lies within speed × life span;
- takes three (`0x005076f6-0x00507710`) only when the mode names a
  `CWeaponClip` (`+0x00`).

The Missile Pod modes, the M6 Blaster, the SAT Launcher and both drone weapons
name no clip and fire no flak rounds, so each spawned round costs exactly two
draws at launch, plus two per Move while a wiggling round flies.

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
| 4–9 icebergs, 30–34 city buildings, 21–22 SafeSides (type 37) | Feature, `CSimpleBuilding`, `CSafeSide` | none | — |

Level-world and spawned units also own AIs: Target Tank and Target Truck
(`CGroundVehicle`, squad-wrapped when spawned by the Tank Factory), Warehouse
(`CBuilding`), U-17 Highside Transporter (`CDropship`), Air Trainer and Target Drone
(`CPlane`, squad-less).

The four turrets also run the fire-control cycle above. Each AI queues event 3000
at its construction time. An inactive owner then draws
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
| Whether the turret, lock, crosshair and seek laws above hold at runtime as composed | An original-code composition of `0x004fa8d0`'s turret section, `HandleLocks`, `CalcUnitOverCrossHair` and `CRound::Move` over a supplied world |
| Exact first-flush order of all AI, 4003 and Actor draws in Level 100 | Extend the World 110 construction order to all base rows and the level-world rows |
| Whether the Hangar AI's all-squads spawning probe runs (owner `+0x188`) | Read the Hangar and Airfield spawner uses and `0x004fda90` |
| How often stray turret rounds hit the player | A copied-retail observation once David releases the desktop |
| Whether retail aborts on a given player trajectory | Not reproducible without a retail run of the same inputs |
