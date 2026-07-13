# World / Thing / Spawn Copied-Corpus Schema Proof

<!-- ghidra-full-reaudit-20260713:start -->
> **2026-07-13 live correction closeout:** `0x0050b9c0` signature/comment correction. Current live Ghidra reflects confirmed rows only; older conflicting text below is superseded only where confirmed. Use the [closeout](ghidra-full-reaudit-closeout-2026-07-13.md); final per-address decisions and exact before/after metadata are in `reverse-engineering/binary-analysis/ghidra-reviewed-correction-decisions-2026-07-13.jsonl` and `reverse-engineering/binary-analysis/ghidra-reviewed-correction-plan-2026-07-13.json`.
<!-- ghidra-full-reaudit-20260713:end -->

Status: copied-corpus schema proof complete, not runtime proof
Last updated: 2026-06-08
Scope: `world-thing-spawn-copied-corpus-schema`

This result turns the [World / Thing / Spawn Copied-Corpus Object-Reference Schema Proof Plan](world-thing-spawn-copied-corpus-schema-proof-plan.md) into a deterministic public-safe schema artifact:

- [world-thing-spawn-copied-corpus-schema.v1.json](../game-assets/world-thing-spawn-copied-corpus-schema.v1.json)

This is not a new static re-audit wave, not a Ghidra mutation, not runtime MissionScript proof, not runtime object identity proof, not runtime spawn behavior proof, not live loose-MSL loading proof, not BEA patching, not visual QA, not Godot work, and not rebuild parity.

## Static Closeout Context

| Track | Current |
| --- | --- |
| Static Ghidra function-quality closure | `6411/6411 = 100.00%` |
| Commentless / exact-undefined / `param_N` debt | `0 / 0 / 0` |
| Expanded post-100 static surface | `1560/1560 = 100.00%` |
| Active current-risk focused accounting | `1179/1179 = 100.00%` |
| Remaining active focused work | `0` |
| Latest verified Ghidra backup | `[maintainer-local-ghidra-backup-root]\BEA_20260607-230027_post_wave1219_final_score16_current_risk_review_verified` |

Remaining active focused work remains `0`; this proof does not change `static-reaudit-progress.json`, `static-reaudit-current-risk-ledger.json`, or the static percentages.

## Schema Evidence

| Schema field | Value |
| --- | --- |
| Schema version | `world-thing-spawn-copied-corpus-schema.v1` |
| Source | `reverse-engineering/game-assets/mission-thing-usage.md` |
| Raw detailed key | `Level + Dir + File + Call + Thing + Spawner + call occurrence` |
| Unique object-reference key | `Level + Dir + Call + Thing` |
| Spawn-preserving key | `Level + Dir + Call + Thing + Spawner` |
| Raw detailed rows | `574` `GetThingRef`, `70` `SpawnThing`, `644` total |
| Published unique object-reference rows | `418` `GetThingRef`, `18` `SpawnThing`, `436` total |
| Spawn-preserving unique rows | `418` `GetThingRef`, `29` `SpawnThing`, `447` total |
| Selected family | `training-target-spawn-family` |
| Selected raw rows | `34` raw `SpawnThing` rows |
| Selected unique object-reference rows | `6` unique `Level + Dir + Call + Thing` rows |
| Selected unique thing labels | `4`: `Air Trainer`, `Target Drone`, `Target Tank`, `Target Truck` |
| Selected unique file/thing/spawner rows | `8` unique `Level + Dir + File + Thing + Spawner` rows |

## Selected Family Rows

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

## Static Handoff Anchors

The schema carries static handoff anchors for later proof/rebuild planning: `IScript__SpawnThing`, `IScript__GetThingRef`, `ScriptCommandRegistry__InitBuiltins`, `0x005392a0 CScriptObjectCode__CollectSpawnThings`, opcode `0x18`, `CWorldMeshList__Add`, `0x0050b9c0 CWorld__LoadWorld`, `0x0050dcb0 CWorld__SpawnInitialThings`, `0x0050df80 CWorldPhysicsManager__CreateThingByType`, `0x0050f970 CWorldPhysicsManager__CreateSpawner`, `0x005115b0 CWorldPhysicsManager__MapGunOrSpawnerTagToIndex`, `0x00511ad0 CWorldPhysicsManager__AddSpawnerByName`, `DAT_008553f4`, `0x004e3c60 CSpawnerThng__DoSpawn`, `0x00511440 CWorldPhysicsManager__IsSpawnerThingTypeAllowedByName`, `CUnit__VFunc08_InitAndAddToWorld`, and `CThing__InitRenderThingFromInitMeshName`.

## What This Proves

- The selected copied-corpus schema can be rebuilt from the tracked loose-MSL mission thing usage table.
- Raw detailed call rows, public deduped object-reference rows, and spawner-preserving rows are distinct metrics.
- The first training-target `SpawnThing` family preserves level, directory, file, thing, spawner, casing, and duplicate-call counts.
- The result is public-safe because it publishes only tracked loose-MSL aggregate/schema data and no private bytes, runtime captures, saves, executable patches, installed-game paths, user-profile paths, secrets, or operator-only evidence. Ghidra backup path strings remain provenance markers only.

## Not Claimed

This does not prove runtime `GetThingRef` behavior, runtime `SpawnThing` behavior, runtime MissionScript execution, runtime object identity, runtime object lookup by name, runtime world loading, runtime spawner behavior, runtime Unit/BattleEngine spawn behavior, live loose-MSL loading, packed-resource script selection, exact handler address, exact VM/object-code/world/thing/spawner layouts, exact source-body identity, BEA patching behavior, visual QA, Godot parity, rebuild parity, or no-noticeable-difference parity.

## Next Useful Static-To-Proof Step

The next World / Thing / Spawn child lane selected and completed from this schema is [World / Thing / Spawn Spawner Handoff Static Proof](world-thing-spawn-spawner-handoff-static-proof.md), backed by [world-thing-spawn-spawner-handoff-static.v1.json](world-thing-spawn-spawner-handoff-static.v1.json). Status: static spawner handoff proof complete, not runtime proof. It maps the selected `training-target-spawn-family` through static MissionScript, bytecode preload, world load/factory, spawner gate, Unit cooldown, and mesh/resource handoff anchors without claiming runtime spawn behavior. The following object-reference child lane is [World / Thing / Spawn GetThingRef Object-Reference Static Proof](world-thing-spawn-getthingref-object-reference-static-proof.md), backed by [world-thing-spawn-getthingref-object-reference-static.v1.json](world-thing-spawn-getthingref-object-reference-static.v1.json). Status: static GetThingRef object-reference proof complete, not runtime proof. It maps the selected `training-target-zone-getthingref-family` through `9` raw selected `GetThingRef` rows, `8` selected unique object-reference rows, `8` selected unique file/thing rows, `1` duplicate-call row, `9` empty-spawner rows, `IScript__GetThingRef`, `CThingPtrDataType`, `0x0052ff30`, `0x0064ce50`, and `0x0064f210` without claiming runtime object lookup behavior.
