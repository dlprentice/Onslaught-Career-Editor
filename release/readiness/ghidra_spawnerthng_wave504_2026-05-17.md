# Ghidra CSpawnerThng Wave504 Readiness Note

Date: 2026-05-17

## Summary

Wave504 saved static Ghidra signatures, comments, and tags for thirteen adjacent `CSpawnerThng` functions. The tranche covers spawner initialization, shutdown, update, name lookup, constructor/destructor wrappers, spawn-count accounting, spawn execution, wave processing, completion checking, and spawn-position clearance.

This is static retail Ghidra evidence only. It does not prove exact `CSpawnerThng`, `CSpawnerInitThing`, global spawner table, map-who, object factory, collision/grid, or spawned-object layouts, nor runtime spawn scheduling/collision/wave behavior, BEA launch behavior, game patching, or rebuild parity.

## Targets

| Address | Saved signature |
| --- | --- |
| `0x004e3010` | `void __thiscall CSpawnerThng__Init(void * this, void * init)` |
| `0x004e3330` | `void __fastcall CSpawnerThng__Shutdown(void * this)` |
| `0x004e3370` | `void __fastcall CSpawnerThng__Update(void * this)` |
| `0x004e36c0` | `int __cdecl CSpawnerThng__FindSpawnerByName(char * spawner_name)` |
| `0x004e37f0` | `void * __thiscall CSpawnerThng__Constructor(void * this, void * spawner_init, void * owner_context)` |
| `0x004e39f0` | `void * __thiscall CSpawnerThng__ScalarDeletingDestructor(void * this, byte flags)` |
| `0x004e3a10` | `void __fastcall CSpawnerThng__Destructor(void * this)` |
| `0x004e3aa0` | `void __fastcall CSpawnerThng__CleanupAndDelete(void * this)` |
| `0x004e3ac0` | `void __fastcall CSpawnerThng__UpdateSpawnCount(void * this)` |
| `0x004e3c60` | `bool __fastcall CSpawnerThng__DoSpawn(void * this)` |
| `0x004e3f90` | `void __fastcall CSpawnerThng__ProcessSpawnWave(void * this)` |
| `0x004e4430` | `bool __fastcall CSpawnerThng__IsSpawnComplete(void * this)` |
| `0x004e44d0` | `bool __thiscall CSpawnerThng__IsSpawnPositionClear(void * this, float * spawn_position)` |

## Evidence

- Source debug path `C:\dev\ONSLAUGHT2\SpawnerThng.cpp` and `CSpawnerInitThing` source fields supplied naming/layout hints.
- Retail Ghidra decompile, xrefs, instructions, caller exports, and callsite exports supplied the saved evidence.
- Artifacts are under `subagents/ghidra-static-reaudit/wave504-spawnerthng-004e3010/`.

## Verification

- `ApplySpawnerThngWave504.java` dry: `updated=0 skipped=13 created=0 would_create=0 renamed=0 would_rename=0 missing=0 bad=0`.
- `ApplySpawnerThngWave504.java` apply: `updated=13 skipped=0 created=0 would_create=0 renamed=0 would_rename=0 missing=0 bad=0`.
- `ApplySpawnerThngWave504.java` final verify dry: `updated=0 skipped=13 created=0 would_create=0 renamed=0 would_rename=0 missing=0 bad=0`.
- All three mutation passes reported `REPORT: Save succeeded`.
- Post-readback verified `13` metadata rows, `13` tag rows, `20` xref rows, `481` instruction rows, and `13` decompile exports.
- `py -3 tools\ghidra_spawnerthng_wave504_probe.py --check` passed.
- `npm run test:ghidra-spawnerthng-wave504` passed.
- `npm run test:ghidra-static-reaudit-queue` passed after queue refresh.
- Refreshed queue: `6078` functions, `2311` commented, `3767` commentless, `1638` undefined signatures, `1490` `param_N` signatures.
- Telemetry proxy: comment-backed `2311/6078 = 38.02%`; strict comment-plus-clean-signature `2257/6078 = 37.13%`. These are telemetry only, not completion certification.
- Backup `G:\GhidraBackups\BEA_20260517-145950_post_wave504_spawnerthng_verified` verified `19` files, `158010247` bytes, `MissingCount=0`, `ExtraCount=0`, and `HashDiffCount=0`.
