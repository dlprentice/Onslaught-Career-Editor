# SpawnPoint.cpp Functions

> Source context: `references/Onslaught/game.cpp` respawn flow and retail Ghidra evidence
> Binary: BEA.exe

> **Queue status (2026-05-26):** Ghidra export-contract closure **6113/6113** (Wave900: every function commented; clean-signature proxy; not evidence-grade semantics). Lines below that reference a "next raw commentless" row are **archival wave progress**, not open work.

## Overview

`CSpawnPoint` participates in multiplayer/co-op respawn selection. `CGame__RespawnPlayer` counts available spawn points, chooses one, and calls the spawn-point BattleEngine creation helper when available. If no available spawn point is selected, the retail fallback iterates `CStart` objects and uses the start-point availability/spawn helpers hardened in Wave510. Wave505 corrected several stale `CSpawnPoint` owner labels in this area; Wave510 corrected two stale `CGame` labels to `CStart`.

This page is static retail Ghidra/source-reference documentation only. It does not prove exact `CSpawnPoint`, `CStart`, BattleEngine init/effect, map-who, or spawned-object layouts, nor runtime respawn behavior.

## Wave510 CStart Read-Back Status

Wave510 saved names/signatures/comments/tags for six adjacent `CStart` helpers on 2026-05-17:

| Address | Saved signature | Notes |
| --- | --- | --- |
| `0x004eacc0` | `void * __thiscall CStart__Constructor(void * this)` | Constructor-like body reached by `OID__CreateObject`; initializes the active-reader cell at `this+0x7c`, embedded `CStartInitThing` storage at `this+0x84`, clears respawn/player fields, and installs CStart vtables `0x005df2ec` and `0x005df274`. |
| `0x004ead70` | `void * __thiscall CStart__ScalarDeletingDestructor(void * this, byte flags)` | `RET 0x4` proves one flags argument; wrapper calls `CStart__Destructor` and conditionally frees `this`. |
| `0x004ead90` | `void __fastcall CStart__Destructor(void * this)` | Removes this start from `DAT_00855100`, unregisters the active-reader cell when linked, then chains to `CComplexThing__dtor_base`. |
| `0x004eae10` | `void __thiscall CStart__Init(void * this, void * init)` | Vtable `0x005df2ec` slot 9; clamps init height, calls `CComplexThing__Init`, links into `DAT_00855100`, copies start init fields, and calls `CStart__SpawnBattleEngine(play_effect=0)`. |
| `0x004eaf20` | `void * __thiscall CStart__SpawnBattleEngine(void * this, int play_effect)` | Corrects stale `CGame__SetupRespawnReaderAndEffect`; creates OID type `3`, binds it through `this+0x7c`, initializes from embedded start init data at `this+0x84`, and optionally spawns ground/air respawn effects. |
| `0x004eb130` | `bool __fastcall CStart__Available(void * this)` | Corrects stale `CGame__HasNearbyHostileWithinRadius`; `CGame__RespawnPlayer` calls it during fallback start-point selection and the body rejects nearby active hostile/non-excluded owners through `CMapWho`. |

Verification artifacts live under `subagents/ghidra-static-reaudit/wave510-start-respawn-004ea8d0/`. The Wave510 apply script reported clean dry/apply/final-verify runs, post exports verified `7` metadata rows, `7` tag rows, `8` xref rows, `2247` instruction rows, `7` decompile exports, and `192` vtable-slot rows across the whole relaxed-squad/start tranche, and both direct and npm probes passed. Backup `G:\GhidraBackups\BEA_20260517-180231_post_wave510_start_respawn_verified` verified `19` files, `158272391` bytes, and zero missing/extra/hash-diff files.

Not proven by Wave510: exact `CStart`, `CStartInitThing`, BattleEngine init/effect, active-reader, map-who, or global-list layouts; runtime respawn behavior; BEA launch behavior; game patching; or rebuild parity.

## Wave505 Read-Back Status

Wave505 saved names/signatures/comments/tags for four spawn-point helpers on 2026-05-17:

| Address | Saved signature | Notes |
| --- | --- | --- |
| `0x004e46c0` | `void __thiscall CSpawnPoint__Init(void * this, void * init)` | `RET 0x4` proves one explicit init argument after `ECX`; body clamps init position against static shadow height, calls `CComplexThing__Init`, links into `DAT_00855110`, copies respawn/player/transform fields, and stores mode/effect fields. |
| `0x004e47c0` | `void __fastcall CSpawnPoint__VFuncSlot02_RemoveFromSpawnPointList(void * this)` | Register-only cleanup wrapper that removes this from `DAT_00855110` and delegates to shared `VFuncSlot_02_004f41b0`. |
| `0x004e47e0` | `void * __thiscall CSpawnPoint__SpawnBattleEngine(void * this, int play_effect)` | Corrects stale `CGame__CreateRespawnBattleEngineAndEffect`; creates OID type `3`, initializes it from `this+0x80`, seeds respawn fields, and optionally spawns ground/air respawn effects. |
| `0x004e49f0` | `bool __fastcall CSpawnPoint__Available(void * this)` | Corrects stale `CGame__IsSpawnAreaClearWithinRadius`; queried by `CGame__RespawnPlayer` during spawn-point selection and rejects occupied map-who clearance radius. |

Verification artifacts live under `subagents/ghidra-static-reaudit/wave505-spawnpoint-trigger-004e43d0/`. The Wave505 apply script reported clean dry/apply/final-verify runs, post exports verified `6` metadata rows, `6` tag rows, `7` xref rows, `726` instruction rows, and `6` decompile exports across the whole spawn-point/sphere-trigger tranche, and both direct and npm probes passed. Backup `G:\GhidraBackups\BEA_20260517-154500_post_wave505_spawnpoint_spheretrigger_verified` verified `19` files, `158010247` bytes, and zero missing/extra/hash-diff files.

Not proven by Wave505: exact `CSpawnPoint`, `CStart`, BattleEngine init/effect, map-who, particle-effect, or spawned-object layouts; runtime respawn behavior; BEA launch behavior; game patching; or rebuild parity.
