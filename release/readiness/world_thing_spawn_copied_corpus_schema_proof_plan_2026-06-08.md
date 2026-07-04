# World / Thing / Spawn Copied-Corpus Schema Proof Plan Readiness Note

Status: schema proof plan complete, not runtime proof
Date: 2026-06-08
Scope: `world-thing-spawn-copied-corpus-schema-proof-plan`

This readiness note records the selected child lane after the completed World / Thing / Spawn / Object-Reference Bridge Proof Plan: a copied-corpus object-reference schema proof plan for the loose-MSL `SpawnThing` surface.

This is not a new static re-audit wave, not a Ghidra mutation, not a runtime test, not a mission execution proof, not a live loose-MSL loading proof, not a save/career mutation proof, not a screenshot/capture proof, not a native input proof, not a BEA patch, not a Godot slice, and not a rebuild parity claim.

Current static closeout remains unchanged:

- Static Ghidra function-quality closure: `6411/6411 = 100.00%`.
- Static debt: `0 / 0 / 0`.
- Expanded post-100 static surface: `1560/1560 = 100.00%`.
- Active current-risk focused accounting: `1179/1179 = 100.00%`.
- Remaining active focused work: `0`.
- Latest verified Ghidra review backup remains `[maintainer-local-ghidra-backup-root]\BEA_20260607-230027_post_wave1219_final_score16_current_risk_review_verified`.

Corpus count vocabulary:

| Count layer | Key | GetThingRef | SpawnThing | Total |
| --- | --- | ---: | ---: | ---: |
| Raw detailed call rows | `Level + Dir + File + Call + Thing + Spawner + call occurrence` | `574` | `70` | `644` |
| Published unique object-reference rows | `Level + Dir + Call + Thing` | `418` | `18` | `436` |
| Spawn-preserving unique rows | `Level + Dir + Call + Thing + Spawner` | `418` | `29` | `447` |

Selected first `SpawnThing` family:

| Level | Dir | File | Thing | Spawner | Raw rows |
| ---: | --- | --- | --- | --- | ---: |
| `22` | `level022` | `Hangar.msl` | `Target Drone` | `SpawnerA` | `3` |
| `22` | `level022` | `Hangar.msl` | `Target Drone` | `SpawnerB` | `6` |
| `22` | `level022` | `TankFactory.msl` | `Target Tank` | `SpawnerA` | `5` |
| `100` | `level100` | `Hangar.msl` | `Target Drone` | `SpawnerA` | `3` |
| `100` | `level100` | `Hangar.msl` | `Target Drone` | `SpawnerB` | `6` |
| `100` | `level100` | `LevelScript.msl` | `Air Trainer` | `SpawnerB` | `1` |
| `100` | `level100` | `TankFactory.msl` | `Target Tank` | `SpawnerA` | `4` |
| `100` | `level100` | `TankFactory.msl` | `Target Truck` | `SpawnerA` | `6` |

This selected family has `34` raw `SpawnThing` rows, `6` unique `Level + Dir + Call + Thing` rows, `4` unique thing labels, and `8` unique `Level + Dir + File + Thing + Spawner` rows. The schema plan preserves exact `Dir`, `File`, `Thing`, `Spawner`, casing, and duplicate-call counts.

Static anchors retained for later copied/app-owned proof:

- `IScript__SpawnThing`, `SpawnThing`, `IScript__GetThingRef`, `CThingPtrDataType`, `ScriptCommandRegistry__InitBuiltins`, `0x0052ff30`, `0x0064ce50`, and `0x0064f210`.
- `0x005392a0 CScriptObjectCode__CollectSpawnThings`, opcode `0x18`, and `CWorldMeshList__Add`.
- `0x0050b9c0 CWorld__LoadWorld`, `0x0050ac70 CWorld__LoadScriptEvents`, `CWorld__LoadWorldFile`, `CWorld__DeserializeWorld`, `CWorld__LoadWorldHeader`, and `0x0050d9e0 CWorldMeshList__Add`.
- `0x0050dcb0 CWorld__SpawnInitialThings`, `0x0050df80 CWorldPhysicsManager__CreateThingByType`, `CWorldPhysicsManager__CreateProjectile`, `0x0048c650 InitThing__CreateThingByType`, `0x0040e280 CInitThing__LoadFromMemBuffer`, and `0x0048dcf0 CInitThing__ctor`.
- `0x004e3010 CSpawnerThng__Init`, `0x004e36c0 CSpawnerThng__FindSpawnerByName`, `0x004e3c60 CSpawnerThng__DoSpawn`, `0x004e3f90 CSpawnerThng__ProcessSpawnWave`, `0x0050f680 CSpawnerThng__IsSpawnTypeAllowed`, and `0x00511440 CWorldPhysicsManager__IsSpawnerThingTypeAllowedByName`.
- `CUnit__VFunc08_InitAndAddToWorld`, `CWorld__AddUnitToOccupancyGridAndRebuildShadows_Thunk`, `CUnit__SetSpawnCooldownState3`, `CThing__InitRenderThingFromInitMeshName`, and `mesh-resource-render-static-contract.md`.

No runtime `GetThingRef` behavior, runtime `SpawnThing` behavior, runtime MissionScript execution, runtime object identity, runtime object lookup by name, runtime world loading, runtime spawner behavior, runtime Unit/BattleEngine spawn behavior, runtime mesh/resource loading, live loose-MSL loading, packed-resource script selection, exact handler address proof, exact VM/object-code/world/thing/spawner layouts, exact source-body identity, BEA patching behavior, visual QA, Godot parity, rebuild parity, or no-noticeable-difference parity claim is made.
