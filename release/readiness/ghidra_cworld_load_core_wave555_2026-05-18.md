# Ghidra CWorld Load/Core Wave555 Readiness Note

Date: 2026-05-18

## Scope

Wave555 saved static Ghidra owner/signature/comment/tag hardening for eleven adjacent CWorld load, registry, and cleanup helpers:

| Address | Saved state |
| --- | --- |
| `0x0050a870` | `void __fastcall CWorld__ClearSetArrays(void * world)` |
| `0x0050a9c0` | `void * __fastcall CWorld__InitSetArraysAndState(void * world)` |
| `0x0050abb0` | `void __fastcall CWorld__ShutdownAndClear_Thunk(void * world)` |
| `0x0050abc0` | `void * __thiscall CWorld__CloneScriptObjectCodeByName(void * this, char * script_name)` |
| `0x0050ac70` | `void __thiscall CWorld__LoadScriptEvents(void * this, void * mem_buffer)` |
| `0x0050ada0` | `void __fastcall CWorld__ShutdownAndClear(void * world)` |
| `0x0050af70` | `void * __thiscall CWorld__FindThingByName(void * this, char * thing_name)` |
| `0x0050b520` | `int __thiscall CWorld__LoadWorldFile(void * this, int world_id, int is_base_world)` |
| `0x0050b780` | `void __thiscall CWorld__DeserializeWorld(void * this, void * chunk_reader)` |
| `0x0050d4c0` | `void __thiscall CWorld__LoadWorldHeader(void * this, void * mem_buffer, int is_base_world)` |
| `0x0050d580` | `void __fastcall CWorld__InitLODLists(void * world)` |

## Evidence

- `ApplyCWorldLoadCoreWave555.java` dry: `updated=0 skipped=11 renamed=0 would_rename=2 missing=0 bad=0`.
- Apply: `updated=11 skipped=0 renamed=2 would_rename=0 missing=0 bad=0`, with `REPORT: Save succeeded`.
- Read-back artifacts under `subagents/ghidra-static-reaudit/wave555-cworld-load-core-0050a870/`: `11` metadata rows, `11` tag rows, `15` xref rows, `1551` target instruction rows, `285` callsite instruction rows, `11` target decompile exports, and `7` caller decompile exports.
- Focused probe: `py -3 tools\ghidra_cworld_load_core_wave555_probe.py --check` PASS.
- NPM probe: `cmd.exe /c npm run test:ghidra-cworld-load-core-wave555` PASS.
- Queue refresh: `cmd.exe /c npm run test:ghidra-static-reaudit-queue` PASS.

## Queue Telemetry

Fresh post-Wave555 queue:

| Metric | Value |
| --- | ---: |
| Function objects | 6089 |
| Functions with comments | 2691 |
| Commentless functions | 3398 |
| Exact `undefined` signatures | 1530 |
| Signatures still using `param_N` | 1256 |
| Comment-backed proxy | `2691/6089 = 44.19%` |
| Strict comment-plus-clean-signature proxy | `2637/6089 = 43.31%` |

These are queue telemetry only, not completion claims.

## Backup

Post-wave verified Ghidra backup:

```text
G:\GhidraBackups\BEA_20260518-152609_post_wave555_cworld_load_core_verified
Files: 19
Bytes: 159484807
MissingCount: 0
ExtraCount: 0
HashDiffCount: 0
```

## Not Proven

Exact CWorld member names/layouts, script-event and thing-set concrete types, resource/chunk reader schemas, runtime world load/shutdown behavior, BEA patching, and rebuild parity remain unproven.
