# SpawnerThng.cpp Functions

> Source File: SpawnerThng.cpp | Binary: BEA.exe
> Debug Path: 0x00632650 (`[maintainer-local-source-export-root]\SpawnerThng.cpp`)

## Overview

> **Queue status (2026-05-26):** Ghidra export-contract closure **6113/6113** (Wave900: every function commented; clean-signature proxy; not evidence-grade semantics). Lines below that reference a "next raw commentless" row are **archival wave progress**, not open work.

CSpawnerThng handles retail gameplay object spawning: enemy waves, unit creation, reinforcements, timing, position validation, wave counts, and coordination with the object-management path. This page is static retail Ghidra/source-reference documentation; it does not by itself prove runtime spawn scheduling or exact object layouts.

## Wave1022 Destructor Owner-Prefix Normalization

Wave1022 (`object-lifecycle-dtor-review-wave1022`) saved a narrow owner-prefix normalization for the vtable-backed SpawnerThng destructor pair. The saved rows are `0x004bfd80 CSpawnerThng__scalar_deleting_dtor` and `0x004bfed0 CSpawnerThng__dtor_base`, replacing stale `CSpawnerThing__...` spelling. Vtable `0x005dd16c` ties slot 1 to the scalar-deleting destructor, slot 2 to `CSpawnerThng__Shutdown`, and slot 9 to `CSpawnerThng__Init`; the base destructor removes the `+0x7c` owner/list link through `CSPtrSet__Remove` before delegating to `CComplexThing__dtor_base`. Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260531-230345_post_wave1022_object_lifecycle_dtor_review_verified`.

Probe token anchor: Wave1022; object-lifecycle-dtor-review-wave1022; 0x004bfd80 CSpawnerThng__scalar_deleting_dtor; 0x004bfed0 CSpawnerThng__dtor_base; 0x005dd16c; 539/1408 = 38.28%; 768/1493 = 51.44%; 467/500 = 93.40%; 6238/6238 = 100.00%; [maintainer-local-ghidra-backup-root]\BEA_20260531-230345_post_wave1022_object_lifecycle_dtor_review_verified; renamed=2.

Runtime spawner cleanup behavior, exact source-body identity, concrete object layout, BEA patching, and rebuild parity remain separate proof.

## Wave504 Read-Back Status

Wave504 saved signatures/comments/tags for all thirteen known `CSpawnerThng` functions in the live Ghidra project on 2026-05-17. Source debug path `[maintainer-local-source-export-root]\SpawnerThng.cpp` and `CSpawnerInitThing` source fields were used as hints; the saved retail Ghidra database remains the authority.

Verification artifacts live under `subagents/ghidra-static-reaudit/wave504-spawnerthng-004e3010/`. `ApplySpawnerThngWave504.java` reported clean dry/apply/final-verify runs, post exports verified `13` metadata rows, `13` tag rows, `20` xref rows, `481` instruction rows, and `13` decompile exports, and both the focused probe and `npm run test:ghidra-spawnerthng-wave504` passed. The refreshed queue reports `6078` functions, `2311` commented, `3767` commentless, `1638` undefined signatures, and `1490` `param_N` signatures. Backup `[maintainer-local-ghidra-backup-root]\BEA_20260517-145950_post_wave504_spawnerthng_verified` verified `19` files, `158010247` bytes, and zero missing/extra/hash-diff files.

Not proven by Wave504: exact `CSpawnerThng`, `CSpawnerInitThing`, global spawner table, map-who, object factory, collision/grid, or spawned-object layouts; runtime spawn scheduling/collision/wave behavior; BEA launch behavior; game patching; or rebuild parity.

Wave837 CUnit Spawn Cooldown correction note: the later raw-head pass corrected the callee previously documented in ProcessSpawnWave evidence as stale `CSpawnerThng__SetCooldownState3`. The saved Ghidra row at `0x004fc3a0` is now `CUnit__SetSpawnCooldownState3` with signature `void __thiscall CUnit__SetSpawnCooldownState3(void * this, float cooldown_delay)` and tags `cunit-spawn-cooldown-wave837` / `wave837-readback-verified`. The sole xref remains `0x004e430f CSpawnerThng__ProcessSpawnWave`, where the caller runs after `CWorldPhysicsManager__CreateThingByType`, initializes the spawned object through vfunc `+0x24`, sets `ECX` to the created object, and pushes spawner config `+0x1c`. `FADD [ESP+0x4]` at `0x004fc3b0` and `RET 0x4` at `0x004fc3ba` prove one float delay argument; the callee writes state literal `3` to `this+0x168` and `DAT_00672fd0 + cooldown_delay` to `this+0x16c`. Post-Wave837 strict proxy is `5659/6098 = 92.80%`; next raw commentless row is `0x004fce40 CUnitAI__CallAttachedNodeVFunc14IfPresent`. Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260525-013914_post_wave837_cunit_spawn_cooldown_verified`. This is static retail Ghidra evidence only; exact Unit.cpp source-body identity, exact state enum meaning, concrete CUnit field names/layout, runtime spawn activation/cooldown behavior, BEA patching, and rebuild parity remain deferred.

Wave845 CSpawner Type Allowed note: the raw-head pass hardened related predicate `0x0050f680 CSpawnerThng__IsSpawnTypeAllowed` as `bool __cdecl CSpawnerThng__IsSpawnTypeAllowed(int spawn_type)` with the `spawner-type-allowed-wave845` and `wave845-readback-verified` tags. This row is compact but important connective spawner infrastructure: `CSpawnerThng__Init` at `0x004e32cc` and `CSpawnerThng__Constructor` at `0x004e39b2` both push a definition type enum from `+0xe0`, call the helper, and then `TEST EAX,EAX` before branching. The helper subtracts `4`, bounds-checks `0x14`, dispatches through `0x0050f6a4/0x0050f6ac`, returns false for `4 through 0x14 and 0x16 through 0x18`, and returns true for default/out-of-range plus the unlisted `0x15` slot. Post-Wave845 strict proxy is `5669/6098 = 92.96%`; next raw commentless row is `0x00510520 CWorldPhysicsManager__ResolveLoadedDefinitionReferences`. Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260525-053251_post_wave845_spawner_type_allowed_verified`. Exact enum names, source method identity, concrete spawner/definition field meanings, runtime spawn admission behavior, BEA patching, and rebuild parity remain deferred.

## Saved Signatures

| Address | Saved signature |
|---------|-----------------|
| 0x004e3010 | `void __thiscall CSpawnerThng__Init(void * this, void * init)` |
| 0x004e3330 | `void __fastcall CSpawnerThng__Shutdown(void * this)` |
| 0x004e3370 | `void __fastcall CSpawnerThng__Update(void * this)` |
| 0x004e36c0 | `int __cdecl CSpawnerThng__FindSpawnerByName(char * spawner_name)` |
| 0x004e37f0 | `void * __thiscall CSpawnerThng__Constructor(void * this, void * spawner_init, void * owner_context)` |
| 0x004e39f0 | `void * __thiscall CSpawnerThng__ScalarDeletingDestructor(void * this, byte flags)` |
| 0x004e3a10 | `void __fastcall CSpawnerThng__Destructor(void * this)` |
| 0x004e3aa0 | `void __fastcall CSpawnerThng__CleanupAndDelete(void * this)` |
| 0x004e3ac0 | `void __fastcall CSpawnerThng__UpdateSpawnCount(void * this)` |
| 0x004e3c60 | `bool __fastcall CSpawnerThng__DoSpawn(void * this)` |
| 0x004e3f90 | `void __fastcall CSpawnerThng__ProcessSpawnWave(void * this)` |
| 0x004e4430 | `bool __fastcall CSpawnerThng__IsSpawnComplete(void * this)` |
| 0x004e44d0 | `bool __thiscall CSpawnerThng__IsSpawnPositionClear(void * this, float * spawn_position)` |

## Functions

| Address | Name | Size | Purpose |
|---------|------|------|---------|
| 0x004e3010 | CSpawnerThng__Init | ~800 bytes | Initialize spawner from spawn configuration data |
| 0x004e3330 | CSpawnerThng__Shutdown | ~64 bytes | Clean up spawner, free allocated memory |
| 0x004e3370 | CSpawnerThng__Update | ~896 bytes | Main update loop - manages spawn timing and wave progression |
| 0x004e36c0 | CSpawnerThng__FindSpawnerByName | ~144 bytes | Search spawner list by name string, returns index or -1 |
| 0x004e37f0 | CSpawnerThng__Constructor | ~512 bytes | Constructor - initializes vtable, exception handling, spawn params |
| 0x004e39f0 | CSpawnerThng__ScalarDeletingDestructor | ~32 bytes | MSVC scalar deleting destructor wrapper |
| 0x004e3a10 | CSpawnerThng__Destructor | ~144 bytes | Destructor - cleans up spawned objects, handles exceptions |
| 0x004e3aa0 | CSpawnerThng__CleanupAndDelete | ~32 bytes | Cleanup wrapper, calls destructor then virtual delete |
| 0x004e3ac0 | CSpawnerThng__UpdateSpawnCount | ~416 bytes | Validate and update spawn count, handles spawn modes |
| 0x004e3c60 | CSpawnerThng__DoSpawn | ~816 bytes | Execute spawn - get position, create object, update counters |
| 0x004e3f90 | CSpawnerThng__ProcessSpawnWave | ~1008 bytes | Process spawn wave - collision check, orientation, type mapping |
| 0x004e4430 | CSpawnerThng__IsSpawnComplete | ~80 bytes | Check if spawner has completed all waves |
| 0x004e44d0 | CSpawnerThng__IsSpawnPositionClear | ~176 bytes | Check spawn position for collision (6.0 unit radius) |

**Total: 13 functions identified**

## Wave845 CSpawner Type Allowed Related Predicate

| Address | Saved signature | Static evidence |
|---------|-----------------|-----------------|
| 0x0050f680 | `bool __cdecl CSpawnerThng__IsSpawnTypeAllowed(int spawn_type)` | Called by `0x004e32cc` and `0x004e39b2`; dispatches through `0x0050f6a4/0x0050f6ac`; false range `4 through 0x14 and 0x16 through 0x18`; next queue head after the pass is `0x00510520 CWorldPhysicsManager__ResolveLoadedDefinitionReferences`; backup `[maintainer-local-ghidra-backup-root]\BEA_20260525-053251_post_wave845_spawner_type_allowed_verified`. |

## Vtable Layout (0x005dd190)

```
Offset  Address     Function
0x00    0x004e3010  CSpawnerThng__Init
0x04    0x00405930  (inherited - likely base class)
0x08    0x00405930  (inherited - likely base class)
0x0C    0x004014c0  (inherited)
0x10    0x00401420  (inherited)
0x14    0x004f43d0  (related class method)
0x18    0x004bfc60  (related class method)
...
```

## Key Class Members (observed retail fields)

Offsets below are observed from current retail decompilation and should be treated as field-role evidence, not a complete recovered C++ layout.

| Offset | Type | Purpose |
|--------|------|---------|
| 0x0468 | char* | Spawner name string (dynamically allocated) |
| 0x007c | ptr | Pointer to parent/owner object |
| 0x0080 | float | Next spawn time |
| 0x0084-0x008c | float[3] | Spawn timing parameters |
| 0x0090 | int | Spawn batch size |
| 0x0094 | int | Total spawn count (waves) |
| 0x0098 | int | Current wave count |
| 0x009c | int | Current batch count |
| 0x00a0 | int | Infinite spawn flag |
| 0x00a4 | int | Active flag |
| 0x00b0 | int | Spawn mode (0 or 1) |

## Key Observations

### Spawn Timing System
- Uses `DAT_00672fd0` as global game time reference
- Timer callback via `FUN_0044b370(3000, ...)` - likely a 3-second timer ID
- Timing controlled by floats at offsets 0x84, 0x88, 0x8c

### Spawn Position Validation
- Grid-based collision check (256x256 grid)
- Proximity check with 6.0 unit radius (36.0 squared distance)
- Object flag filtering: requires 0x10, excludes 0xc4900

### Spawn Type Mapping
Switch in ProcessSpawnWave maps spawn types:
- 10 -> 15
- 11 -> 16
- 12 -> 17
- 13 -> 18
- 14 -> 19

### Error Handling
- "Spawned more than we should be able to!!!" warning at 0x00632690
- Exception frame setup in constructor/destructor

### Linked List Management
- Uses global spawner list at `DAT_008553f4` for spawner iteration; `DAT_008553fc` is the thing-definition list used by related type/name checks.
- String comparison for spawner lookup by name

## Related Strings

| Address | String |
|---------|--------|
| 0x00632650 | `[maintainer-local-source-export-root]\SpawnerThng.cpp` |
| 0x00632690 | `Spawned more than we should be able to!!!` |

## Related Functions (Not in SpawnerThng.cpp)

- `FUN_0050df80` - Object factory/creation
- `FUN_0050f4b0` - Object type lookup
- `0x0050f680 CSpawnerThng__IsSpawnTypeAllowed` - Wave845 CSpawner Type Allowed static spawn-type predicate
- `CSPtrSet__First`/`CSPtrSet__Next` - List iteration helpers
- `FUN_00511510` - Distance/influence calculation
- `CUnit__GetGridMapByType` - Grid map access by unit type
- `FUN_0044b370` - Timer/scheduler system

---
*Discovered via Phase 1 xref analysis (Dec 2025). Wave504 refreshed and saved all 13 signatures/comments/tags on 2026-05-17.*
*13 functions mapped from SpawnerThng.cpp debug path reference.*
