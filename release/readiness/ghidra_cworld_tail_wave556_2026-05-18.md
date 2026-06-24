# Ghidra CWorld Tail / WorldMeshList Wave556 Readiness Note

Date: 2026-05-18

## Scope

Wave556 saved static Ghidra signature/comment/tag hardening for twelve adjacent CWorld tail, WorldMeshList, and world-thing factory bridge helpers:

| Address | Saved state |
| --- | --- |
| `0x0050d680` | `void * __thiscall CWorld__ReleaseSubObject_AndMaybeFree(void * this, uint flags)` |
| `0x0050d6a0` | `void __thiscall CWorld__PushWorldTextSlot(void * this, int text_id, int slot_state)` |
| `0x0050d720` | `void __thiscall CWorld__UpdateWorldTextSlotTiming(void * this, int text_id, float primary_time, float secondary_time)` |
| `0x0050d760` | `double __thiscall CWorld__GetWorldTextSlotTimerValue(void * this, int slot_index)` |
| `0x0050d7a0` | `void __thiscall CWorld__ClearWorldTextSlot(void * this, int text_id)` |
| `0x0050d7d0` | `int __fastcall CWorld__IsMultiplayerMode(void * world)` |
| `0x0050d7f0` | `void __fastcall CWorld__ClearLinkedObjectPairSet(void * pair_set)` |
| `0x0050d9a0` | `void __cdecl CWorldMeshList__Clear(void)` |
| `0x0050d9e0` | `void __cdecl CWorldMeshList__Add(char * mesh_name)` |
| `0x0050dc20` | `void __cdecl CWorldMeshList__MarkUsed(char * mesh_name)` |
| `0x0050dcb0` | `void __cdecl CWorld__SpawnInitialThings(void)` |
| `0x0050df80` | `void * __cdecl CWorldPhysicsManager__CreateThingByType(int thing_type_index)` |

## Evidence

- `ApplyCWorldTailWave556.java` dry: `updated=0 skipped=12 renamed=0 would_rename=1 missing=0 bad=0`.
- Apply: `updated=12 skipped=0 renamed=1 would_rename=0 missing=0 bad=0`, with `REPORT: Save succeeded`.
- Read-back artifacts under `subagents/ghidra-static-reaudit/wave556-cworld-tail-0050d680/`: `12` metadata rows, `12` tag rows, `47` xref rows, `1932` target instruction rows, and `12` target decompile exports.
- Focused probe: `py -3 tools\ghidra_cworld_tail_wave556_probe.py --check` PASS.
- NPM probe: `cmd.exe /c npm run test:ghidra-cworld-tail-wave556` PASS.
- Queue refresh: `cmd.exe /c npm run test:ghidra-static-reaudit-queue` PASS after fresh `ExportFunctionQualitySnapshot.java` export.

## Queue Telemetry

Fresh post-Wave556 queue:

| Metric | Value |
| --- | ---: |
| Function objects | 6089 |
| Functions with comments | 2703 |
| Commentless functions | 3386 |
| Exact `undefined` signatures | 1525 |
| Signatures still using `param_N` | 1249 |
| Comment-backed proxy | `2703/6089 = 44.39%` |
| Strict comment-plus-clean-signature proxy | `2649/6089 = 43.50%` |

These are queue telemetry only, not completion claims.

## Backup

Post-wave verified Ghidra backup:

```text
G:\GhidraBackups\BEA_20260518-155904_post_wave556_cworld_tail_verified
Files: 19
Bytes: 159550343
MissingCount: 0
ExtraCount: 0
HashDiffCount: 0
```

## Not Proven

Exact CWorld slot structure names, text-slot state enum names, WorldMeshList node/list ownership invariants, thing-definition layouts, runtime HUD/spawn/world-load behavior, BEA patching, and rebuild parity remain unproven.
