# World / Thing / Spawn GetThingRef Object-Reference Static Proof Readiness Note

Status: static GetThingRef object-reference proof complete, not runtime proof
Date: 2026-06-08
Scope: `world-thing-spawn-getthingref-object-reference-static`

This note records the public-safe readiness boundary for [World / Thing / Spawn GetThingRef Object-Reference Static Proof](../../reverse-engineering/binary-analysis/world-thing-spawn-getthingref-object-reference-static-proof.md) and [world-thing-spawn-getthingref-object-reference-static.v1.json](../../reverse-engineering/binary-analysis/world-thing-spawn-getthingref-object-reference-static.v1.json).

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

## Evidence Summary

| Evidence | Value |
| --- | ---: |
| Raw detailed `GetThingRef` rows | `574` |
| Raw detailed `SpawnThing` rows | `70` |
| Raw detailed total rows | `644` |
| Published unique `GetThingRef` rows | `418` |
| Published unique `SpawnThing` rows | `18` |
| Published unique total rows | `436` |
| Selected family | `training-target-zone-getthingref-family` |
| Selected raw `GetThingRef` rows | `9` |
| Selected unique object-reference rows | `8` |
| Selected duplicate-call rows | `1` |
| Selected empty-spawner rows | `9` |

Selected rows preserve `level022`, `level100`, `Level22Script.msl`, `LevelScript.msl`, `Target Zone 1`, `Target Zone 2`, `Target Zone 3`, `Target Zone 4`, exact casing, empty spawner cells, and the duplicate `Target Zone 4` call in `level100`.

## Static Anchors

- `IScript__GetThingRef`
- `CThingPtrDataType`
- `ScriptCommandRegistry__InitBuiltins`
- `0x0052ff30`
- `0x0064ce50`
- `0x0064f210`
- `world-thing-spawn-object-reference-proof-plan.md`
- `world-thing-spawn-spawner-handoff-static-proof.md`
- `DAT_008553f4`
- `0x0050f970 CWorldPhysicsManager__CreateSpawner`
- `0x004e3c60 CSpawnerThng__DoSpawn`

## What This Proves

- The selected training target-zone `GetThingRef` copied-corpus family has a reproducible static object-reference row set derived from the tracked loose-MSL mission thing usage table.
- The proof preserves raw rows, unique object-reference rows, unique file/thing rows, empty spawner values, exact target-zone casing, and the duplicate `Target Zone 4` call in `level100`.
- The selected family is tied to MissionScript command registry, thing-pointer datatype, and existing World / Thing / Spawn static boundary docs without claiming runtime lookup behavior.

## Not Claimed

This does not prove runtime `GetThingRef` behavior, runtime object identity, runtime object lookup by name, runtime MissionScript execution, runtime world loading, runtime `SpawnThing` behavior, runtime spawner behavior, live loose-MSL loading, packed-resource script selection, exact descriptor layout, exact handler address, exact VM/object-code/world/thing/spawner layouts, exact source-body identity, BEA patching behavior, visual QA, Godot parity, rebuild parity, or no-noticeable-difference parity.
