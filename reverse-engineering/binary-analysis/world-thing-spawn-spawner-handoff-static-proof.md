# World / Thing / Spawn Spawner Handoff Static Proof

Status: static spawner handoff proof complete, not runtime proof
Last updated: 2026-06-08
Scope: `world-thing-spawn-spawner-handoff-static`

This result turns the completed [World / Thing / Spawn Copied-Corpus Schema Proof](world-thing-spawn-copied-corpus-schema-proof.md) into a static handoff contract for the first selected `SpawnThing` family:

- [world-thing-spawn-spawner-handoff-static.v1.json](world-thing-spawn-spawner-handoff-static.v1.json)

This is not a new Ghidra re-audit wave, not a Ghidra mutation, not runtime MissionScript proof, not runtime object identity proof, not runtime spawn behavior proof, not live loose-MSL loading proof, not BEA patching, not visual QA, not Godot work, and not rebuild parity.

## Static Closeout Context

| Track | Current |
| --- | --- |
| Static Ghidra function-quality closure | `6411/6411 = 100.00%` |
| Commentless / exact-undefined / `param_N` debt | `0 / 0 / 0` |
| Expanded post-100 static surface | `1560/1560 = 100.00%` |
| Active current-risk focused accounting | `1179/1179 = 100.00%` |
| Remaining active focused work | `0` |
| Latest verified Ghidra backup | `G:\GhidraBackups\BEA_20260607-230027_post_wave1219_final_score16_current_risk_review_verified` |

Remaining active focused work remains `0`; this proof does not change `static-reaudit-progress.json`, `static-reaudit-current-risk-ledger.json`, or the static percentages.

## Selected Family

The selected family remains the copied-corpus `training-target-spawn-family`:

| Metric | Value |
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

Selected rows preserve `level022`, `level100`, `Hangar.msl`, `TankFactory.msl`, `LevelScript.msl`, `Target Drone`, `Target Tank`, `Target Truck`, `Air Trainer`, `SpawnerA`, `SpawnerB`, exact casing, and duplicate-call counts from [world-thing-spawn-copied-corpus-schema.v1.json](../game-assets/world-thing-spawn-copied-corpus-schema.v1.json).

## Static Handoff Layers

| Layer | Anchors | Static contract |
| --- | --- | --- |
| Corpus command family | `world-thing-spawn-copied-corpus-schema.v1.json`, `mission-thing-usage.md`, `training-target-spawn-family`, `Target Drone`, `Target Tank`, `Target Truck`, `Air Trainer`, `SpawnerA`, `SpawnerB` | Preserve level, directory, file, thing, spawner, casing, and duplicate-call counts for the selected `SpawnThing` family. |
| MissionScript command descriptor | `IScript__SpawnThing`, `IScript__GetThingRef`, `CThingPtrDataType`, `ScriptCommandRegistry__InitBuiltins`, `0x0064ce50`, `0x0064f210` | Tie the selected corpus command family to the saved MissionScript command registry and thing-pointer datatype surface without claiming runtime dispatch. |
| Bytecode pre-scan | `0x005392a0 CScriptObjectCode__CollectSpawnThings`, opcode `0x18`, `CWorldMeshList__Add` | Record the static `SpawnThing` pre-scan path that adds mesh/world dependencies before live script execution proof. |
| World load / mesh dependency | `0x0050b9c0 CWorld__LoadWorld`, `0x0050ac70 CWorld__LoadScriptEvents`, `0x0050d9e0 CWorldMeshList__Add`, `DAT_00855358`, `DAT_008553fc +0xb0` | Map the world-load and mesh-list dependency surface needed before object-reference or spawn runtime proof. |
| World factory / init | `0x0050dcb0 CWorld__SpawnInitialThings`, `0x0050df80 CWorldPhysicsManager__CreateThingByType`, `0x0048c650 InitThing__CreateThingByType`, `0x0040e280 CInitThing__LoadFromMemBuffer`, `CThing__InitRenderThingFromInitMeshName` | Map the static thing-definition and init-object factory path without claiming exact object layout or runtime creation. |
| Spawner gate / wave | `0x004e3010 CSpawnerThng__Init`, `0x004e36c0 CSpawnerThng__FindSpawnerByName`, `0x004e3c60 CSpawnerThng__DoSpawn`, `0x004e3f90 CSpawnerThng__ProcessSpawnWave`, `0x0050f680 CSpawnerThng__IsSpawnTypeAllowed`, `0x0050f970 CWorldPhysicsManager__CreateSpawner`, `0x00511440 CWorldPhysicsManager__IsSpawnerThingTypeAllowedByName`, `0x005115b0 CWorldPhysicsManager__MapGunOrSpawnerTagToIndex`, `0x00511ad0 CWorldPhysicsManager__AddSpawnerByName`, `DAT_008553f4` | Map the spawner name/tag/type-gate shell required for selected `SpawnThing` handoff proof. |
| Unit world-add / cooldown | `CUnit__VFunc08_InitAndAddToWorld`, `CWorld__AddUnitToOccupancyGridAndRebuildShadows_Thunk`, `0x004fc3a0 CUnit__SetSpawnCooldownState3` | Record the Unit/BattleEngine spawn-add and post-spawn cooldown handoff anchors without claiming runtime activation. |
| Mesh/resource/render boundary | `CThing__InitRenderThingFromInitMeshName`, `mesh-resource-render-static-contract.md`, `texture-resource-decode-static-contract.md` | Preserve the render/resource dependency boundary for rebuild planning without claiming visual output or GPU parity. |

## Static Field Roles

These labels are static field roles only. They are not final C++ layouts.

| Role anchor | Static role |
| --- | --- |
| `CSpawnerThng+0x0468` | spawner name string role |
| `CSpawnerThng+0x007c` | parent or owner role |
| `CSpawnerThng+0x0080` | next spawn time role |
| `CSpawnerThng+0x0090` | batch size role |
| `CSpawnerThng+0x0094` | total count role |
| `CSpawnerThng+0x0098` | current wave count role |
| `CSpawnerThng+0x009c` | current batch count role |
| `CSpawnerThng+0x00a0` | infinite spawn flag role |
| `CSpawnerThng+0x00a4` | active flag role |
| `CSpawnerThng+0x00b0` | spawn mode role |
| `CUnit+0x0168` | spawn cooldown state role |
| `CUnit+0x016c` | spawn cooldown timestamp role |

## What This Proves

- The selected training-target `SpawnThing` copied-corpus family has a bounded static handoff map from loose corpus rows to MissionScript descriptor/datatype anchors, bytecode pre-scan, world load/mesh dependencies, spawner gates, world factory/init, Unit world-add/cooldown, and mesh/resource boundaries.
- The proof preserves raw, unique object-reference, and spawner-preserving corpus count vocabulary from the copied-corpus schema.
- Field-role offsets are preserved as static roles only, not final C++ layouts.

## Not Claimed

This does not prove runtime `SpawnThing` behavior, runtime `GetThingRef` behavior, runtime MissionScript execution, runtime object identity, runtime object lookup by name, runtime world loading, runtime spawner behavior, runtime Unit/BattleEngine spawn behavior, runtime AI activation, runtime collision, runtime damage, runtime HUD/message/audio output, live loose-MSL loading, packed-resource script selection, exact descriptor layout, exact VM/object-code/world/thing/spawner/Unit layouts, exact source-body identity, BEA patching behavior, visual QA, Godot parity, rebuild parity, or no-noticeable-difference parity.

## Next Useful Static-To-Proof Step

The next World / Thing / Spawn child lane selected and completed after this result is [World / Thing / Spawn GetThingRef Object-Reference Static Proof](world-thing-spawn-getthingref-object-reference-static-proof.md), backed by [world-thing-spawn-getthingref-object-reference-static.v1.json](world-thing-spawn-getthingref-object-reference-static.v1.json). Status: static GetThingRef object-reference proof complete, not runtime proof. It maps the selected `training-target-zone-getthingref-family` through `9` raw selected `GetThingRef` rows, `8` selected unique object-reference rows, `8` selected unique file/thing rows, `1` duplicate-call row, `9` empty-spawner rows, `IScript__GetThingRef`, `CThingPtrDataType`, `0x0052ff30`, `0x0064ce50`, and `0x0064f210` without claiming runtime object lookup behavior. Any runtime proof must remain copied/app-owned and must first define stop conditions for duplicate names, missing object labels, missing spawners, packed-vs-loose selection uncertainty, and exact-layout ambiguity.
