# World / Thing / Spawn Copied-Corpus Schema Proof Readiness Note

<!-- ghidra-full-reaudit-20260713:start -->
> **2026-07-13 semantic revalidation:** Historical record; `0x0050b9c0` signature/comment correction. The original text below remains provenance rather than current semantic authority. Use the [closeout](../../reverse-engineering/binary-analysis/ghidra-full-reaudit-closeout-2026-07-13.md); exact records are in `reverse-engineering/binary-analysis/ghidra-full-reaudit-corrections-2026-07-13.json` and `reverse-engineering/binary-analysis/ghidra-targeted-revalidation-corrections-2026-07-13.json`.
<!-- ghidra-full-reaudit-20260713:end -->

Status: copied-corpus schema proof complete, not runtime proof
Date: 2026-06-08
Scope: `world-thing-spawn-copied-corpus-schema`

This readiness note records the public-safe schema result for the World / Thing / Spawn copied-corpus object-reference lane:

- `reverse-engineering/game-assets/world-thing-spawn-copied-corpus-schema.v1.json`
- `reverse-engineering/binary-analysis/world-thing-spawn-copied-corpus-schema-proof.md`
- `reverse-engineering/binary-analysis/world-thing-spawn-copied-corpus-schema-proof-plan.md`
- `tools/world_thing_spawn_copied_corpus_schema_probe.py`

This is not a new static re-audit wave, not a Ghidra mutation, not runtime MissionScript proof, not runtime object identity proof, not runtime spawn behavior proof, not live loose-MSL loading proof, not a BEA patch, not a Godot slice, and not rebuild parity.

Current static closeout remains unchanged:

- Static Ghidra function-quality closure: `6411/6411 = 100.00%`.
- Static debt: `0 / 0 / 0`.
- Expanded post-100 static surface: `1560/1560 = 100.00%`.
- Active current-risk focused accounting: `1179/1179 = 100.00%`.
- Remaining active focused work remains `0`.
- Latest verified Ghidra review backup remains `[maintainer-local-ghidra-backup-root]\BEA_20260607-230027_post_wave1219_final_score16_current_risk_review_verified`.

Schema proof:

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
| Selected training-target raw `SpawnThing` rows | `34` raw `SpawnThing` rows |
| Selected unique object-reference rows | `6` unique `Level + Dir + Call + Thing` rows |
| Selected unique thing labels | `4`: `Air Trainer`, `Target Drone`, `Target Tank`, `Target Truck` |
| Selected unique file/thing/spawner rows | `8` unique `Level + Dir + File + Thing + Spawner` rows |

Selected family rows are `level022` / `Hangar.msl` / `Target Drone` / `SpawnerA` (`3`), `level022` / `Hangar.msl` / `Target Drone` / `SpawnerB` (`6`), `level022` / `TankFactory.msl` / `Target Tank` / `SpawnerA` (`5`), `level100` / `Hangar.msl` / `Target Drone` / `SpawnerA` (`3`), `level100` / `Hangar.msl` / `Target Drone` / `SpawnerB` (`6`), `level100` / `LevelScript.msl` / `Air Trainer` / `SpawnerB` (`1`), `level100` / `TankFactory.msl` / `Target Tank` / `SpawnerA` (`4`), and `level100` / `TankFactory.msl` / `Target Truck` / `SpawnerA` (`6`).

Static anchor chain: `IScript__SpawnThing`, `IScript__GetThingRef`, `ScriptCommandRegistry__InitBuiltins`, `0x005392a0 CScriptObjectCode__CollectSpawnThings`, opcode `0x18`, `CWorldMeshList__Add`, `0x0050b9c0 CWorld__LoadWorld`, `0x0050dcb0 CWorld__SpawnInitialThings`, `0x0050df80 CWorldPhysicsManager__CreateThingByType`, `0x004e3c60 CSpawnerThng__DoSpawn`, `0x00511440 CWorldPhysicsManager__IsSpawnerThingTypeAllowedByName`, `CUnit__VFunc08_InitAndAddToWorld`, and `CThing__InitRenderThingFromInitMeshName`.

No runtime `GetThingRef` behavior, runtime `SpawnThing` behavior, runtime MissionScript execution, runtime object identity, runtime world loading, runtime spawner behavior, runtime Unit/BattleEngine spawn behavior, live loose-MSL loading, packed-resource script selection, exact handler address proof, exact VM/object-code/world/thing/spawner layouts, exact source-body identity, BEA patching behavior, visual QA, Godot parity, rebuild parity, or no-noticeable-difference parity claim is made.
