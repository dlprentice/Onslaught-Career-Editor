# World / Thing / Spawn GetThingRef Object-Reference Static Proof

Status: static GetThingRef object-reference proof complete, not runtime proof
Last updated: 2026-06-08
Scope: `world-thing-spawn-getthingref-object-reference-static`

This result turns the completed [World / Thing / Spawn Copied-Corpus Schema Proof](world-thing-spawn-copied-corpus-schema-proof.md) into a narrow static object-reference contract for the first selected `GetThingRef` family:

- [world-thing-spawn-getthingref-object-reference-static.v1.json](world-thing-spawn-getthingref-object-reference-static.v1.json)

This is not a new Ghidra re-audit wave, not a Ghidra mutation, not runtime MissionScript proof, not runtime object identity proof, not runtime `GetThingRef` behavior proof, not live loose-MSL loading proof, not BEA patching, not visual QA, not Godot work, and not rebuild parity.

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

The selected family is the copied-corpus `training-target-zone-getthingref-family`.

| Metric | Value |
| --- | ---: |
| Raw detailed `GetThingRef` rows | `574` |
| Raw detailed `SpawnThing` rows | `70` |
| Raw detailed total rows | `644` |
| Published unique `GetThingRef` rows | `418` |
| Published unique `SpawnThing` rows | `18` |
| Published unique total rows | `436` |
| Selected training target-zone raw `GetThingRef` rows | `9` |
| Selected unique object-reference rows | `8` |
| Selected unique thing labels | `4`: `Target Zone 1`, `Target Zone 2`, `Target Zone 3`, `Target Zone 4` |
| Selected unique file/thing rows | `8` |
| Selected duplicate-call rows | `1` |
| Selected empty-spawner rows | `9` |

Selected rows preserve `level022`, `level100`, `Level22Script.msl`, `LevelScript.msl`, `Target Zone 1`, `Target Zone 2`, `Target Zone 3`, `Target Zone 4`, exact casing, empty spawner cells, and duplicate-call counts from [mission-thing-usage.md](../game-assets/mission-thing-usage.md). The one duplicate is `level100` / `LevelScript.msl` / `Target Zone 4`.

## Selected Rows

| Level | Dir | File | Thing | Raw rows |
| ---: | --- | --- | --- | ---: |
| `22` | `level022` | `Level22Script.msl` | `Target Zone 1` | `1` |
| `22` | `level022` | `Level22Script.msl` | `Target Zone 2` | `1` |
| `22` | `level022` | `Level22Script.msl` | `Target Zone 3` | `1` |
| `22` | `level022` | `Level22Script.msl` | `Target Zone 4` | `1` |
| `100` | `level100` | `LevelScript.msl` | `Target Zone 1` | `1` |
| `100` | `level100` | `LevelScript.msl` | `Target Zone 2` | `1` |
| `100` | `level100` | `LevelScript.msl` | `Target Zone 3` | `1` |
| `100` | `level100` | `LevelScript.msl` | `Target Zone 4` | `2` |

## Static Linkage Layers

| Layer | Anchors | Static contract |
| --- | --- | --- |
| Corpus object-reference family | `mission-thing-usage.md`, `world-thing-spawn-copied-corpus-schema.v1.json`, `training-target-zone-getthingref-family`, `level022`, `level100`, `Level22Script.msl`, `LevelScript.msl`, `Target Zone 1`, `Target Zone 2`, `Target Zone 3`, `Target Zone 4` | Preserve level, directory, file, thing label, casing, empty spawner column, and duplicate-call counts for the selected `GetThingRef` target-zone family. |
| MissionScript command descriptor | `IScript__GetThingRef`, `GetThingRef`, `CThingPtrDataType`, `ScriptCommandRegistry__InitBuiltins`, `0x0052ff30`, `0x0064ce50`, `0x0064f210` | Tie the selected corpus family to the saved MissionScript command registry and thing-pointer datatype surface without claiming exact handler address or runtime dispatch. |
| World object-reference boundary | `world-thing-spawn-object-reference-proof-plan.md`, `CWorld__LoadWorld`, `CWorldPhysicsManager__CreateThingByType`, `InitThing__CreateThingByType`, `CThing__InitRenderThingFromInitMeshName` | Carry the selected object-reference labels to the existing world/load/factory boundary while preserving runtime object identity as unproven. |
| Spawn handoff context | `world-thing-spawn-spawner-handoff-static-proof.md`, `world-thing-spawn-spawner-handoff-static.v1.json`, `training-target-spawn-family`, `DAT_008553f4`, `0x0050f970 CWorldPhysicsManager__CreateSpawner`, `0x004e3c60 CSpawnerThng__DoSpawn` | Use the completed `SpawnThing` handoff as context only; this `GetThingRef` proof does not claim runtime spawn or lookup behavior. |

## What This Proves

- The selected training target-zone `GetThingRef` copied-corpus family has a reproducible static object-reference row set derived from the tracked loose-MSL mission thing usage table.
- The proof preserves raw rows, unique object-reference rows, unique file/thing rows, empty spawner values, exact target-zone casing, and the duplicate `Target Zone 4` call in `level100`.
- The selected family is tied to MissionScript command registry, thing-pointer datatype, and existing World / Thing / Spawn static boundary docs without claiming runtime lookup behavior.

## Not Claimed

This does not prove runtime `GetThingRef` behavior, runtime object identity, runtime object lookup by name, runtime MissionScript execution, runtime world loading, runtime `SpawnThing` behavior, runtime spawner behavior, live loose-MSL loading, packed-resource script selection, exact descriptor layout, exact handler address, exact VM/object-code/world/thing/spawner layouts, exact source-body identity, BEA patching behavior, visual QA, Godot parity, rebuild parity, or no-noticeable-difference parity.

## Next Useful Static-To-Proof Step

The next MissionScript child lane can move to a finite command-effect family such as camera plus position/vector commands, or to another object-reference family if a broader object-name corpus check is useful. Any runtime `GetThingRef` proof must remain copied/app-owned and must define stop conditions for duplicate names, missing object labels, packed-vs-loose selection uncertainty, and exact-layout ambiguity.
