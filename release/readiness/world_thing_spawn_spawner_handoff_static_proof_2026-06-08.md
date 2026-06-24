# World / Thing / Spawn Spawner Handoff Static Proof Readiness Note

Status: static spawner handoff proof complete, not runtime proof
Date: 2026-06-08
Scope: `world-thing-spawn-spawner-handoff-static`

This readiness note records the public-safe static handoff result for the selected World / Thing / Spawn training-target `SpawnThing` family:

- `reverse-engineering/binary-analysis/world-thing-spawn-spawner-handoff-static-proof.md`
- `reverse-engineering/binary-analysis/world-thing-spawn-spawner-handoff-static.v1.json`
- `reverse-engineering/binary-analysis/world-thing-spawn-copied-corpus-schema-proof.md`
- `reverse-engineering/game-assets/world-thing-spawn-copied-corpus-schema.v1.json`
- `tools/world_thing_spawn_spawner_handoff_static_probe.py`

This is not a new Ghidra re-audit wave, not a Ghidra mutation, not runtime MissionScript proof, not runtime object identity proof, not runtime spawn behavior proof, not live loose-MSL loading proof, not a BEA patch, not visual QA, not Godot work, and not rebuild parity.

Current static closeout remains unchanged:

- Static Ghidra function-quality closure: `6411/6411 = 100.00%`.
- Static debt: `0 / 0 / 0`.
- Expanded post-100 static surface: `1560/1560 = 100.00%`.
- Active current-risk focused accounting: `1179/1179 = 100.00%`.
- Remaining active focused work remains `0`.
- Latest verified Ghidra review backup remains `G:\GhidraBackups\BEA_20260607-230027_post_wave1219_final_score16_current_risk_review_verified`.

Copied-corpus carry-forward:

| Layer | Count |
| --- | ---: |
| Raw detailed `GetThingRef` rows | `574` |
| Raw detailed `SpawnThing` rows | `70` |
| Raw detailed total rows | `644` |
| Published unique `GetThingRef` rows | `418` |
| Published unique `SpawnThing` rows | `18` |
| Published unique total rows | `436` |
| Spawn-preserving unique `GetThingRef` rows | `418` |
| Spawn-preserving unique `SpawnThing` rows | `29` |
| Spawn-preserving unique total rows | `447` |
| Selected training-target raw `SpawnThing` rows | `34` |
| Selected unique object-reference rows | `6` |
| Selected unique thing labels | `4`: `Air Trainer`, `Target Drone`, `Target Tank`, `Target Truck` |
| Selected unique file/thing/spawner rows | `8` |

Static handoff layers:

- Corpus family: `training-target-spawn-family`, `level022`, `level100`, `Hangar.msl`, `TankFactory.msl`, `LevelScript.msl`, `Target Drone`, `Target Tank`, `Target Truck`, `Air Trainer`, `SpawnerA`, and `SpawnerB`.
- MissionScript descriptor/datatype: `IScript__SpawnThing`, `IScript__GetThingRef`, `CThingPtrDataType`, `ScriptCommandRegistry__InitBuiltins`, `0x0064ce50`, and `0x0064f210`.
- Bytecode pre-scan: `0x005392a0 CScriptObjectCode__CollectSpawnThings`, opcode `0x18`, and `CWorldMeshList__Add`.
- World load and mesh dependency: `0x0050b9c0 CWorld__LoadWorld`, `0x0050ac70 CWorld__LoadScriptEvents`, `0x0050d9e0 CWorldMeshList__Add`, `DAT_00855358`, and `DAT_008553fc +0xb0`.
- World factory/init: `0x0050dcb0 CWorld__SpawnInitialThings`, `0x0050df80 CWorldPhysicsManager__CreateThingByType`, `0x0048c650 InitThing__CreateThingByType`, `0x0040e280 CInitThing__LoadFromMemBuffer`, and `CThing__InitRenderThingFromInitMeshName`.
- Spawner gate/wave: `0x004e3010 CSpawnerThng__Init`, `0x004e36c0 CSpawnerThng__FindSpawnerByName`, `0x004e3c60 CSpawnerThng__DoSpawn`, `0x004e3f90 CSpawnerThng__ProcessSpawnWave`, `0x0050f680 CSpawnerThng__IsSpawnTypeAllowed`, `0x0050f970 CWorldPhysicsManager__CreateSpawner`, `0x00511440 CWorldPhysicsManager__IsSpawnerThingTypeAllowedByName`, `0x005115b0 CWorldPhysicsManager__MapGunOrSpawnerTagToIndex`, `0x00511ad0 CWorldPhysicsManager__AddSpawnerByName`, and `DAT_008553f4`.
- Unit/world-add/cooldown: `CUnit__VFunc08_InitAndAddToWorld`, `CWorld__AddUnitToOccupancyGridAndRebuildShadows_Thunk`, and `0x004fc3a0 CUnit__SetSpawnCooldownState3`.
- Mesh/resource/render boundary: `CThing__InitRenderThingFromInitMeshName`, `mesh-resource-render-static-contract.md`, and `texture-resource-decode-static-contract.md`.

Static field roles preserved: `CSpawnerThng+0x0468`, `CSpawnerThng+0x007c`, `CSpawnerThng+0x0080`, `CSpawnerThng+0x0090`, `CSpawnerThng+0x0094`, `CSpawnerThng+0x0098`, `CSpawnerThng+0x009c`, `CSpawnerThng+0x00a0`, `CSpawnerThng+0x00a4`, `CSpawnerThng+0x00b0`, `CUnit+0x0168`, and `CUnit+0x016c`.

No runtime `SpawnThing` behavior, runtime `GetThingRef` behavior, runtime MissionScript execution, runtime object identity, runtime object lookup by name, runtime world loading, runtime spawner behavior, runtime Unit/BattleEngine spawn behavior, runtime AI activation, runtime collision, runtime damage, runtime HUD/message/audio output, live loose-MSL loading, packed-resource script selection, exact descriptor layout, exact VM/object-code/world/thing/spawner/Unit layouts, exact source-body identity, BEA patching behavior, visual QA, Godot parity, rebuild parity, or no-noticeable-difference parity claim is made.
