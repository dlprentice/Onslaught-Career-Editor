# World / Thing / Spawn Copied-Corpus Object-Reference Schema Proof Plan

<!-- ghidra-full-reaudit-20260713:start -->
> **2026-07-13 live correction closeout:** `0x0050b9c0` signature/comment correction. Current live Ghidra reflects confirmed rows only; older conflicting text below is superseded only where confirmed. Use the [closeout](ghidra-full-reaudit-closeout-2026-07-13.md); final per-address decisions and exact before/after metadata are in `reverse-engineering/binary-analysis/ghidra-reviewed-correction-decisions-2026-07-13.jsonl` and `reverse-engineering/binary-analysis/ghidra-reviewed-correction-plan-2026-07-13.json`.
<!-- ghidra-full-reaudit-20260713:end -->

Status: active public-safe copied-corpus schema proof plan, not runtime proof
Last updated: 2026-06-08
Scope: `world-thing-spawn-copied-corpus-schema-proof-plan`

This is the selected child lane after the completed [World / Thing / Spawn / Object-Reference Bridge Proof Plan](world-thing-spawn-object-reference-proof-plan.md). It narrows that bridge to copied-corpus object-reference accounting before any live MissionScript execution, runtime world loading, runtime spawn observation, Godot work, patching, visual QA, or rebuild prototype work.

The purpose is to make the loose-MSL thing/spawn corpus reproducible and implementation-facing. The immediate target is the `SpawnThing` family because it exercises the widest static bridge: MissionScript command anchors, `CScriptObjectCode__CollectSpawnThings`, opcode `0x18`, `CWorldMeshList__Add`, world-load/factory anchors, spawner gates, Unit/BattleEngine spawn handoff, and mesh/resource dependency boundaries.

Copied-corpus schema result: [World / Thing / Spawn Copied-Corpus Schema Proof](world-thing-spawn-copied-corpus-schema-proof.md) with tracked schema [world-thing-spawn-copied-corpus-schema.v1.json](../game-assets/world-thing-spawn-copied-corpus-schema.v1.json). The result keeps this plan's static/corpus-only boundary: no runtime object identity, no runtime `SpawnThing` behavior, no live loose-MSL loading, no patch behavior, no visual QA, no Godot parity, and no rebuild parity claim.

## Static Authority

Current static closeout remains unchanged:

- Static Ghidra function-quality closure: `6411/6411 = 100.00%`.
- Static debt: `0 / 0 / 0` commentless, exact-undefined, and `param_N` rows.
- Expanded post-100 static surface: `1560/1560 = 100.00%`.
- Active current-risk focused accounting: `1179/1179 = 100.00%`.
- Remaining active focused work: `0`.
- Latest verified Ghidra review backup remains `[maintainer-local-ghidra-backup-root]\BEA_20260607-230027_post_wave1219_final_score16_current_risk_review_verified`.

This plan does not change `static-reaudit-progress.json`, `static-reaudit-current-risk-ledger.json`, or the static percentages. It is a static/corpus schema planning artifact.

Primary inputs:

- [Mission Thing Usage (Loose MSL)](../game-assets/mission-thing-usage.md)
- [World / Thing / Spawn Copied-Corpus Schema Proof](world-thing-spawn-copied-corpus-schema-proof.md)
- [World / Thing / Spawn copied-corpus schema JSON](../game-assets/world-thing-spawn-copied-corpus-schema.v1.json)
- [World / Thing / Spawn / Object-Reference Bridge Proof Plan](world-thing-spawn-object-reference-proof-plan.md)
- [MissionScript / IScript Static Contract](missionscript-iscript-static-contract.md)
- [MissionScript / IScript Proof Plan](missionscript-iscript-proof-plan.md)
- [World.cpp function owner docs](functions/World.cpp/_index.md)
- [WorldPhysicsManager.cpp function owner docs](functions/WorldPhysicsManager.cpp/_index.md)
- [InitThing.cpp function owner docs](functions/InitThing.cpp/_index.md)
- [SpawnerThng.cpp function owner docs](functions/SpawnerThng.cpp/_index.md)
- [Unit/BattleEngine Gameplay Static Contract](unit-battleengine-gameplay-static-contract.md)
- [Mesh/Resource/Render Static Contract](mesh-resource-render-static-contract.md)

## Count Vocabulary

`mission-thing-usage.md` contains two different count layers. Both must be preserved because they answer different rebuild questions.

| Count layer | Key | GetThingRef | SpawnThing | Total | Meaning |
| --- | --- | ---: | ---: | ---: | --- |
| Raw detailed call rows | `Level + Dir + File + Call + Thing + Spawner + call occurrence` | `574` | `70` | `644` | Every recorded loose-MSL call row, including repeated calls in the same file and repeated spawner use. |
| Published unique object-reference rows | `Level + Dir + Call + Thing` | `418` | `18` | `436` | The existing public aggregate used by MissionScript and bridge docs. This deliberately dedupes duplicate rows and ignores `Spawner`. |
| Spawn-preserving unique rows | `Level + Dir + Call + Thing + Spawner` | `418` | `29` | `447` | The first rebuild-facing schema key for `SpawnThing`, because spawner identity affects static handoff planning. |

Do not use `418 / 18 / 436` as raw-row counts. Do not use the `18` unique `SpawnThing` count as a spawner-preserving count. The active schema proof must preserve exact `Dir`, `File`, `Thing`, `Spawner`, casing, and duplicate row counts before any runtime proof can select a target.

## First SpawnThing Family

The first copied-corpus schema family is the training target spawn set because it is small enough to inspect and still exercises duplicate calls, repeated spawner names, and multiple script files.

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

This family gives an initial copied-corpus schema with `34` raw `SpawnThing` rows, `6` unique `Level + Dir + Call + Thing` rows, `4` unique thing labels (`Target Drone`, `Target Tank`, `Air Trainer`, and `Target Truck`), and `8` unique `Level + Dir + File + Thing + Spawner` rows. The `LevelScript.msl` `Air Trainer` row is intentionally retained because it tests a non-factory script file in the same level family.

## Static Handoff Chain

| Layer | Required static evidence | Claim boundary |
| --- | --- | --- |
| Command-side corpus row | `SpawnThing` rows from `mission-thing-usage.md`, preserving level directory, script file, thing name, spawner name, casing, and duplicate row counts. | Loose corpus evidence only; no live loose-MSL loading or execution claim. |
| MissionScript command anchor | `IScript__SpawnThing`, companion `IScript__GetThingRef`, `SpawnThing`, `ScriptCommandRegistry__InitBuiltins`, `0x0052ff30`, `0x0064ce50`, `0x0064f210`, and `CThingPtrDataType` from the MissionScript static contract. | Command/contract anchor only; exact handler address, VM stack layout, and runtime command effect remain open. |
| Bytecode pre-scan | `0x005392a0 CScriptObjectCode__CollectSpawnThings` scans SpawnThing-style opcode `0x18` rows and calls `CWorldMeshList__Add`. | Static dependency/preload planning only; not runtime script execution. |
| World-load shell | `0x0050b9c0 CWorld__LoadWorld`, `0x0050ac70 CWorld__LoadScriptEvents`, `CWorld__LoadWorldFile`, `CWorld__DeserializeWorld`, `CWorld__LoadWorldHeader`, and `0x0050d9e0 CWorldMeshList__Add`. | Static world-load dependency map only; not runtime world loading behavior. |
| Factory/init bridge | `0x0050dcb0 CWorld__SpawnInitialThings`, `0x0050df80 CWorldPhysicsManager__CreateThingByType`, `CWorldPhysicsManager__CreateProjectile`, `0x0048c650 InitThing__CreateThingByType`, `0x0040e280 CInitThing__LoadFromMemBuffer`, and `0x0048dcf0 CInitThing__ctor`. | Static factory path only; exact concrete layouts and runtime object creation remain open. |
| Spawner shell | `0x004e3010 CSpawnerThng__Init`, `0x004e36c0 CSpawnerThng__FindSpawnerByName`, `0x004e3c60 CSpawnerThng__DoSpawn`, `0x004e3f90 CSpawnerThng__ProcessSpawnWave`, `0x0050f680 CSpawnerThng__IsSpawnTypeAllowed`, and `0x00511440 CWorldPhysicsManager__IsSpawnerThingTypeAllowedByName`. | Static spawner path only; no runtime spawner behavior or object identity claim. |
| Unit/BattleEngine handoff | `CUnit__VFunc08_InitAndAddToWorld`, `CWorld__AddUnitToOccupancyGridAndRebuildShadows_Thunk`, and `CUnit__SetSpawnCooldownState3`. | Static unit/spawn handoff only; no runtime AI activation, cooldown timing, collision, damage, or gameplay outcome claim. |
| Mesh/resource bridge | `CThing__InitRenderThingFromInitMeshName`, `CWorldMeshList__Add`, `mesh-resource-render-static-contract.md`, and AYA/resource docs. | Static resource dependency only; no render output, material parity, or visual QA claim. |

## Planned Public-Safe Schema

The first executable schema output, when this plan becomes a copied-corpus proof, should be public-safe and deterministic:

| Field | Requirement |
| --- | --- |
| `source` | `mission-thing-usage.md` or a copied/app-owned extraction of the same loose MSL rows. |
| `schemaVersion` | `world-thing-spawn-copied-corpus-schema.v1`. |
| `countKeys.raw` | `Level + Dir + File + Call + Thing + Spawner + call occurrence`. |
| `countKeys.uniqueObjectReference` | `Level + Dir + Call + Thing`. |
| `countKeys.uniqueSpawnPreservingSpawner` | `Level + Dir + Call + Thing + Spawner`. |
| `selectedFamily` | Training target spawn family from `level022` and `level100`, preserving `Hangar.msl`, `TankFactory.msl`, `LevelScript.msl`, `Target Drone`, `Target Tank`, `Target Truck`, `Air Trainer`, `SpawnerA`, and `SpawnerB`. |
| `rawRows` | `34` for the first family. |
| `uniqueObjectReferenceRows` | `6` for the first family under `Level + Dir + Call + Thing`; `4` unique thing labels when `Level + Dir` is ignored. |
| `uniqueSpawnPreservingSpawnerRows` | `8` for the first family. |
| `staticAnchors` | MissionScript command, bytecode pre-scan, world-load, factory/init, spawner shell, Unit/BattleEngine handoff, and mesh/resource bridge anchors listed above. |
| `claimBoundary` | Static/corpus schema only; no runtime object identity, spawn behavior, or rebuild parity claim. |

## Stop Conditions

Stop before claiming or building runtime proof if any of these happen:

- The source rows cannot be reproduced from copied/app-owned corpus inputs.
- A row loses exact casing, file name, level directory, thing name, spawner name, or duplicate count.
- Raw row counts and unique/deduped counts are mixed in one metric.
- The selected family requires packed-resource script selection proof before static/corpus proof is complete.
- A later runtime plan cannot isolate one copied profile, one selected level/file family, and one bounded observation target.
- Any proof would require mutating the installed Steam game directory or original executable.

## Not Claimed

This plan does not prove runtime `GetThingRef` behavior, runtime `SpawnThing` behavior, runtime MissionScript execution, runtime object identity, runtime object lookup by name, runtime world loading, runtime spawner behavior, runtime Unit/BattleEngine spawn behavior, runtime mesh/resource loading, live loose-MSL loading, packed-resource script selection, exact handler address proof, exact VM/object-code/world/thing/spawner layouts, exact source-body identity, BEA patching behavior, visual QA, Godot parity, rebuild parity, or no-noticeable-difference parity.

## Exit Gate

This schema planning slice is complete only when:

- This document and its lore-book mirror match.
- `mission-thing-usage.md` states the count vocabulary and selected first family.
- `world-thing-spawn-object-reference-proof-plan.md` points here as the selected copied-corpus child lane.
- `roadmap/static-to-proof-rebuild-transition-backlog.md`, `reverse-engineering/binary-analysis/mapped-systems.md`, `reverse-engineering/binary-analysis/_index.md`, and `reverse-engineering/RE-INDEX.md` point here as the active static-to-proof slice and mark the prior bridge proof plan complete.
- `release/readiness/world_thing_spawn_copied_corpus_schema_proof_plan_2026-06-08.md` records the same boundaries.
- `tools/world_thing_spawn_copied_corpus_schema_proof_plan_probe.py --check` passes with static closeout percentages unchanged.
