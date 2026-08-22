# Units and Mechs of Allium

- **Status:** live preservation record. Class names, behaviour-type ids, and
  data-record names below are measured evidence — read from RTTI type
  descriptors in the pristine `BEA.exe`
  ([binary-strings.md](../reverse-engineering/binary-analysis/binary-strings.md)),
  the resolved PhysicsScript value-id tables
  ([physics-round-value-ids-2026-07-25.md](../reverse-engineering/binary-analysis/physics-round-value-ids-2026-07-25.md),
  raw table `local-lab/physics-value-ids-2026-07-25/all_ids.tsv`), the exact
  777-record framing of the pristine `default physics.dat`, and the tracked
  source synthesis under `reverse-engineering/source-code/`.
  In-universe flavor (who pilots what, what a faction calls its own machines)
  is carried from [world-lore.md](world-lore.md) and [characters.md](characters.md)
  and is marked as fiction. Where this page and a measurement disagree, the
  measurement wins.
- **Last updated:** 2026-08-22
- **Summary:** all 160 literal top-level unit-record names, all 25 resolved
  behaviour-type ids, and the major runtime class families that turn those
  records into the player's machine, armies, bosses, and infrastructure.

## How the game names a unit

There is no unit roster table in the executable. A "unit" in BEA is assembled at
runtime from four measured layers:

1. **Behaviour types** — one `*UnitBehaviourType` PhysicsScript record per unit
   archetype (25 resolved ids, statement tag 12). This is the closest thing the
   game has to a roster; it is data, not prose.
2. **RTTI classes** — the C++ classes that implement movement, AI, and combat
   for each archetype. Their names survive as `.?AVC…@@` type-descriptor
   strings in `.data`.
3. **PhysicsScript records** — per-unit default records (`CUnitStatement`,
   tag 1: 69 resolved value ids) that tune shields, speeds, leg machinery,
   threat values, and which weapons a unit mounts.
4. **Display strings** — weapon names reach the HUD through
   `CWeapon__GetLanguageName` → `TEXT_DB.GetString`
   (`references/Onslaught/BattleEngineJetPart.cpp:903`), so the strings corpus
   names hardware even when the unit carrying it does not carry its own label.

The 25 resolved behaviour-type ids are the shipped implementation spine. The
literal named-record census is larger because templates, faction variants,
buildings, bosses, and multiplayer/training variants can share one behaviour.

## The roster: behaviour-type ids 0x01–0x19

Measured from the statement-tag-12 factory
([physics-round-value-ids-2026-07-25.md](../reverse-engineering/binary-analysis/physics-round-value-ids-2026-07-25.md),
§"behaviour"; raw rows in `all_ids.tsv` lane T12):

| id | BehaviourType | What it drives |
|---:|---|---|
| 0x01 | `CMechUnitBehaviourType` | Mechs — including the player's Battle Engine |
| 0x02 | `CJeepBehaviourType` | Jeeps / light buggies |
| 0x03 | `CGroundUnitBehaviourType` | Generic ground vehicles (tanks et al.) |
| 0x04 | `CInfantryUnitBehaviourType` | Infantry squads |
| 0x05 | `CTurretUnitBehaviourType` | Fixed turrets |
| 0x06 | `CBoatUnitBehaviourType` | Surface boats |
| 0x07 | `CCarrierUnitBehaviourType` | Carriers — the mobile bases |
| 0x08 | `CBuildingUnitBehaviourType` | Buildings |
| 0x09 | `CFighterBehaviourType` | Fighters |
| 0x0a | `CBomberBehaviourType` | Bombers |
| 0x0b | `CGroundAttackAircraftBehaviourType` | Ground-attack aircraft |
| 0x0c | `CDropshipBehaviourType` | Dropships |
| 0x0d | `CMineBehaviourType` | Sea mines |
| 0x0e | `CHiveBossBehaviourType` | HiveBoss — episode-5 swarm boss |
| 0x0f | `CSubmarineBehaviourType` | Submarine — dives, teleports, surfaces |
| 0x10 | `CDiveBomberBehaviourType` | Dive bombers |
| 0x11 | `CThunderHeadBehaviourType` | Thunderhead — episode-3 walker boss |
| 0x12 | `CCarverBehaviourType` | Carver's enemy Battle Engine |
| 0x13 | `CGillMBehaviourType` | Gill-M — underwater boss |
| 0x14 | `CSentinelBehaviourType` | Sentinel — endgame colossus |
| 0x15 | `CWarspiteBehaviourType` | Warspite battleship body |
| 0x16 | `CFenrirBehaviourType` | Fenrir flying fortress |
| 0x17 | `CWarspiteDomeBehaviourType` | Warspite shield dome |
| 0x18 | `CPodBehaviourType` | Escape pods |
| 0x19 | `CSimpleBuildingBehaviourType` | Simple (non-turret) buildings |

Twenty-five ids resolve in the retained table (ids 0x01–0x19). Generic roles,
bosses, pods, and simple buildings are all selected through this one factory
surface. That proves shared construction vocabulary; it does not prove that a
boss has no additional class-specific logic.

## The player machine: the Battle Engine

Runtime pair: `CBattleEngine` is the gameplay unit and `CMCBattleEngine` is its
motion-controller class; the arrow is ownership, not C++ inheritance. The
tracked source synthesis and retail function notes assign the two forms to
`BattleEngineJetPart.cpp` and `BattleEngineWalkerPart.cpp`.
The machine is one unit with two states —
`BATTLE_ENGINE_STATE_MORPHING_INTO_WALKER` / `_JET` and the settled `_WALKER` /
`_JET` states (`BattleEngine.h:30-31`) — and `Morph()` (`BattleEngine.h:86`)
walks between them. The morph changes the collision volume ("call this when
morphed into new state (i.e. changes our collision shape)",
`BattleEngine.cpp:494`) and gravity handling differs by state
(`BattleEngine.cpp:1071-1081`: jet-mode falls under a 0.2× multiplier).

The released `battle engine configurations.dat` contains six exact profile
names: **Racer, Standard, Sniper, Aquila Prototype, Laser, and Blaster**.
`Sniper` is the only profile with positive stealth (`80.0`); the tutorial world
header selects `Aquila Prototype` (see [worlds.md](worlds.md#world-100--career-node-0)).
Marketing separately describes Pulsar, Blazer, Lancer, and Sniper archetypes;
the repository has not established a one-to-one join from those four labels to
the six shipped data records, so this page does not invent one.

Weapon hardpoints live in `CBattleEngineWalkerPart` / `CBattleEngineJetPart`.
For the measured Level-100 projection, walker keys are `Pulse Cannon Pod` and
`Mech Twin Vulcan Cannon`, while jet keys are `Mech Vulcan Cannon` and
`Missile Pod`. Generic per-profile assignments beyond that bounded projection
remain data-parsing work. Both part classes share the weapon-name plumbing:
`GetWeaponName()` resolves through `LanguageName` into the text database.

### The four engines' shared skeleton

Every engine carries the same measured component vocabulary — these are the
`CUnit*` value records any engine configuration may combine
(`all_ids.tsv` lane T2, 69 ids): air/ground velocity pairs (`CUnitAirVelocity`
/ `CUnitGroundVelocity`), separate air and ground shields plus regeneration
rates, thruster height bounds (`CUnitMinThrusterHeight`, `CUnitMaxThrusterHeight`,
`CUnitMinAltitude`), leg machinery for walker mode (`CUnitLegSpeed`,
`CUnitLegPlacementArea`, `CUnitStandingLegPlacementArea`, `CUnitMaxLegsLifted`),
and stealth (`CUnitStealth`) — the Sniper's invisible mode has a dedicated
data slot rather than being a scripted hack.

## Faction forces

In-universe frame (fiction, from
[world-lore.md](world-lore.md#the-two-civilizations)): Forseti machines are
curved and streamlined with clean-energy weapons; Muspell machines are jagged
and heavy with traditional explosives, and both fly on stolen hover tech. The
code does not know factions as such — it knows allegiance flags
(`CEnemyAlligence`, `CFriendlyAlligence`, `CNeutralAlligence` RTTI classes)
and lets mission data assign sides. The same `CGroundVehicle` class serves both
armies.

Ground: infantry (`CInfantryAI`, `CInfantryGuide`, squad machinery in
`CSquad`/`CNormalSquad`/`CRelaxedSquad`), jeeps and ground vehicles
(`CMCBuggy`, `CMCGroundVehicle` motion controllers), turrets
(`CTurretUnitBehaviourType`, `CCannon`), and buildings
(`CBuilding`, `CSimpleBuilding`, `CRTBuilding` render path).

Air: fighters, bombers, dive bombers and ground-attack aircraft share the
`CAirUnit`/`CSmallAirUnit`/`CBigAirUnit` base tree with per-role guides
(`CBomberGuide`, `CDiveBomberGuide`, `CGroundAttackGuide`) and AIs. Dropships
(`CDropshipAI`) ferry reinforcements and use the spawner family
(`CSpawner*` value records, lane T6) to materialize squads.

Sea: boats (`CBoat`, `CBoatAI`), carriers (`CCarrier`, `CCarrierAI` — the
mobile bases you defend and attack), mines (`CMine`, proximity-triggered via
`CRoundProximity`-style logic), and the submarine (below).

## The bosses

Each boss owns a full subsystem — guide + AI + behaviour type + dedicated
`.cpp` — visible in both RTTI and the pinned source corpus:

- **Thunderhead** (episode 3) — `CThunderHead`, `CThunderheadGuide`,
  `ThunderHead.cpp`. The walking flame-boss: four-legged like the player's
  walker, with its own leg-motion solver (`CThunderHead__CreateLegMotion` is
  the TTD mine's episode-3 exclusive). Strings name its armament:
  `"Thunderhead Main Gun"` and a flamethrower.
- **Warspite** (episode 4) — `CWarspite` + `Warspite.cpp`, the battleship arc.
  Its shield is a *separate unit*: `CWarspiteDome` + `CWarspiteDomeAI` +
  `WarspiteDome.cpp`, with dome behaviour id 0x17 distinct from hull id 0x15.
  This proves distinct hull/dome runtime owners; exact vulnerability ordering
  remains a mission/runtime claim. Armament string: `"Warspite Pulse Laser"`.
- **Submarine** (episode 5) — `CSubmarine`, `CSubmarineAI`. Dives, teleports
  between waypoints while submerged, surfaces to fight (level-500 MSL shows
  `Dive()`/`Surface()` plus teleport travel). Its sinking gates the sub branch
  of the campaign graph (slot-62 flag, see
  [worlds.md](worlds.md#episode-5--worlds-500-524-the-branching-war)).
- **HiveBoss** (episode 5) — `CHiveBoss`, `CHiveBossGuide`, behaviour id 0x0e.
  The swarm-mother: segment machinery shares the destructible-segments
  controller the player's parts use. TTD batch-3 pins its exclusive functions
  (`CHiveBoss__SetVar`, tail-jmp motion accumulator).
- **Carver** (episode 6) — `CCarver`, `CCarverAI`, `CCarverGuide`,
  `Carver.cpp`, behaviour id 0x12. Not a monster — an enemy Battle Engine
  pilot, Lewis Carver (fiction: [characters.md](characters.md#lewis-carver-antagonist)),
  whose machine flies with full player-grade mechanics because it *is* one.
- **Gill-M** (underwater) — `CGillM`, `CGillMAI`, `CGillMHead`, `CGillMHeadAI`,
  behaviour id 0x13. Named after programmer Stuart Gillam ("The Gill-m was
  named after me... wasn't my choice" —
  [cut-content-secrets.md](cut-content-secrets.md#gill-m-boss-named-after-stuart)).
  The head is its own AI object — shoot the head, not the body.
- **Fenrir** (episodes 731/732 → 741/742) — `CFenrir`, `CFenrirMainGunAI`,
  `Fenrir.cpp`-era scripts, behaviour id 0x16. A flying fortress built from
  indexed destructible components: turrets 1-10, main gun 11, plane launchers
  12-17, bomb bays 18-23, engines 24-27. Damage persists across the approach
  fight and the interior fight via career slots 1-30 (measured in
  [msl-scripting.md](../reverse-engineering/game-assets/msl-scripting.md)).
  Strings: `"Fenrir Main Gun"`, `"Fenrir Bomb Launcher"`, `"Fenrir Engines"`.
- **Sentinel** (8xx range / finale framing) — `CSentinel`, `CSentinelAI`,
  `CMCSentinel` motion controller, behaviour id 0x14, with turret/barrel
  transform updates exclusive to 8xx captures. The post-mortem's admiration
  ("the coolest to look at") lands here —
  [development-history.md](development-history.md#sentinel-appreciation).
- **Tentacle kin** (8xx) — `CTentacle`, `CTentacleAI`, `CTentacleGuide`,
  `CComponentTentacle`, `CMCTentacle`. Episode-8-exclusive factory chain in
  the coverage mine. The separate sea-monster recollection has not been bound
  to this class family and is not treated as an identity claim.

## Infrastructure and effects-adjacent entities

Not everything on the battlefield shoots. The roster also carries: escape pods
(`CPod`, behaviour id 0x18 — losing inside Fenrir spawns yours), spawn points
(`CSpawnPoint`) and the whole spawner value family, waypoints
(`CWaypoint`, `CWaypointPath`) driving every guide, hazards (`CHazard` family,
statement tag 9) for environmental damage, debris (`CDebris`), trees
(`CTree`, `CRTTree`) with knock-over support (`CUnitKnockTrees`), and feature
objects (`CFeature` family, tag 8) for scenery with life or invincibility
flags.

## Complete named unit-record census

The pinned `default physics.dat` is 175,603 bytes, SHA-256
`e1fb3dedbeb29b4b4151da2c8cbbdc940b716b1a2321e1d6a9ba1542c74ada14`.
Following the exact framing used by the repository's materializer consumes all
777 statements and encounters **160 type-1 unit statements with 160 different
literal top-level names**. This table preserves spelling and capitalization; a
name is evidence that a record ships, not that normal campaign play reaches it.
The older aggregate census's “54 Unit identities” is a different derived
roll-up and must not be substituted for this literal-record count.

| Name 1 | Name 2 | Name 3 | Name 4 |
|---|---|---|---|
| `A-19 Enforcer` | `Forseti Beam Tank Factory` | `Hive Support` | `Muspell Power Station` |
| `Air Fighter` | `Forseti Building 1` | `Homing Mine Tank` | `Muspell Prison` |
| `Air Fighter LR` | `Forseti Building 2` | `Jason Fighter` | `Muspell Radar Station` |
| `Air Trainer` | `Forseti Building 3` | `Light Gun Tank` | `Muspell Research Station` |
| `Aircarrier` | `Forseti City Building 1` | `M-1 Broadsword Main Battle Tank` | `Muspell Super Fighter Airfield` |
| `Aircarrier Light` | `Forseti City Building 2` | `Manticore BB` | `Muspell Warrior` |
| `Aircarrier Multiplayer` | `Forseti City Building 3` | `Mortar Tank` | `Plasma Artillery` |
| `Antennae` | `Forseti City Building Destroyed` | `Muspell Advanced Fighter` | `Plasma Turret` |
| `Arachnadrone` | `Forseti Commander` | `Muspell Advanced Fighter Airfield` | `Powerstation` |
| `Artillery Turret` | `Forseti Dock 1` | `Muspell Antennae` | `Pulse Turret` |
| `AV-14A Sabre Pulse Tank` | `Forseti Docks` | `Muspell APC` | `Rhino APC` |
| `AV-14B Sabre Pulse Tank` | `Forseti Dragoon` | `Muspell Battleship` | `Rocket Base` |
| `AV-14C Sabre Pulse Tank` | `Forseti Fighter Airfield` | `Muspell Bunker` | `Rocket Tank` |
| `B-4 Sky Tyrant Bomber` | `Forseti Heavy Tank Factory` | `MUSPELL CIVIL BRIDGE HIGH` | `SA-20 Lancer` |
| `B-7 Monitor Bomber` | `Forseti Light Fighter Airfield` | `MUSPELL CIVIL BRIDGE LOW` | `SAM Site` |
| `Base Air Unit` | `Forseti Pulse Tank Factory` | `MUSPELL CIVIL BRIDGE MED` | `SAT Turret` |
| `Battle Engine` | `Forseti Radar Station` | `MUSPELL CIVIL HIGH` | `Sentinel` |
| `Beam Tank` | `Forseti Repair Pad` | `MUSPELL CIVIL LOW` | `Shotgun Tank` |
| `Beam Turret` | `Forseti Research Building` | `MUSPELL CIVIL MEDIUM` | `Sub Hangar` |
| `Billy Fighter` | `Forseti Solar Pod` | `Muspell Commando` | `Sub Hangar Pier` |
| `Biodome` | `Forseti Super Airfield` | `Muspell Control Tower` | `Sub Pod` |
| `Blaster Turret` | `Forseti Tall Building 1` | `Muspell Crane` | `Super Sub` |
| `Cannon Turret` | `Forseti Tall Building 2` | `Muspell Dock 1` | `Tara` |
| `Carver Fighter` | `Forseti Tall Building 3` | `Muspell Dock 2` | `Tara Fighter` |
| `Carver Fighter Boss` | `Forseti Trooper` | `Muspell Dock 3` | `Target APC` |
| `Centaur Mech` | `Forseti Warehouse` | `Muspell Factory` | `Target Drone` |
| `Commando Transport` | `Forseti Wind_Turbine` | `Muspell Fast Landing Craft` | `Target Tank` |
| `Control Tower` | `FSV Marshall` | `Muspell Fighter` | `Target Truck` |
| `Crab Mech` | `Gill-M` | `Muspell Fighter Airfield` | `Tatiana` |
| `Dragoon Transport` | `Gnat` | `Muspell Fighter LR` | `Thunderhead` |
| `Drone Transport` | `Ground Attack Aircraft` | `Muspell Grunt` | `Trooper Barracks` |
| `Fenrir` | `Grunt Barracks` | `Muspell Gun Tank Factory` | `Turtle Landing Craft BT` |
| `Fenrir 2` | `Gun Tank` | `Muspell Hangar` | `Turtle Landing Craft Empty` |
| `Fenrir Multiplayer` | `Gun Turret` | `Muspell Landing Craft` | `Turtle Landing Craft Heavy` |
| `FG-8 Packhorse` | `Hangar` | `Muspell Light Fighter` | `Turtle Landing Craft PT` |
| `FG-8 Packhorse Heavy` | `HE Mine` | `Muspell Light Landing Craft` | `U-17 Highside Transporter` |
| `Flak Turret` | `Heavy Gun Tank` | `Muspell Light Landing Empty` | `Warehouse` |
| `Floating Mine` | `Heavy Mech` | `Muspell Mech Factory` | `Warspite` |
| `Flux Turret` | `Heavy Mech 2` | `Muspell Mine` | `Warspite Turret` |
| `Forseti Advanced Airfield` | `Hive Boss` | `Muspell Mobile SAM` | `XF-28 Venom` |

The table includes people/placeholders (`Tatiana`, `Tara`), buildings, base
templates, training targets, and multiplayer variants because the data file
puts all of them on the unit-statement surface. It does not silently narrow
“unit” to only drivable vehicles.

## Dark ranges

- Unit *display names*: the 160 names above are PhysicsScript record keys, not
  proof that the HUD localizes or prints every one. Unit records use mesh/icon
  fields; weapons separately carry `LanguageName`.
- Goodie-wall artwork names several vehicles we cannot yet bind to behaviour
  ids (goodies 71..73 artwork ships texture-only; reachability unproven —
  [save-goodies.md](../reverse-engineering/quick-reference/save-goodies.md)).
- The 850-866 hidden run uses existing families only, as far as the coverage
  mine reaches; whether it re-skins any unit with new physics records is open.

## Sources

- RTTI class inventory: `reverse-engineering/binary-analysis/binary-strings.md`
  (658 unique `C*` type descriptors, pristine specimen).
- Behaviour-type/unit/component value tables (static, byte-read):
  `local-lab/physics-value-ids-2026-07-25/all_ids.tsv` +
  [physics-round-value-ids-2026-07-25.md](../reverse-engineering/binary-analysis/physics-round-value-ids-2026-07-25.md).
- Tracked source synthesis: `reverse-engineering/source-code/stuart-source-synthesis.md`
  and the focused gameplay/system notes under that directory.
- Exact statement framing reused by the materializer:
  `rebuild/tools/materialize_retail_assets.py` (`_physics_records`).
- Boss exclusivity windows: TTD deep-mine REPORT + batches 1-10
  (`local-lab/hermes-kanban-campaign-2026-08-22/ttd-deep-mine/`).
- Mission-side boss behavior (Fenrir components, submarine dive/surface):
  [msl-scripting.md](../reverse-engineering/game-assets/msl-scripting.md).
- In-universe naming and faction flavor: [world-lore.md](world-lore.md),
  [characters.md](characters.md) — fiction, marked as such.
