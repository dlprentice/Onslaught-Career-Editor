# FEPDevelopment.cpp Functions

> Source File: FEPDevelopment.cpp | Binary: BEA.exe
> Debug Path String: 0x0062921c (`[maintainer-local-source-export-root]\FEPDevelopment.cpp`)

## Overview

`CFEPDevelopment` is the retail frontend development/debug page cluster for world-list selection. Wave 384 corrected the saved Ghidra metadata for this cluster after fresh retail read-back. Stuart's checked source snapshot does not currently provide a matching `FEPDevelopment.cpp` source body, so these names and signatures are retail-binary evidence, not source-body proof.

The important correction is that the earlier `0x00458100` function object started in the middle of the world-file enumeration body. The saved function boundary is now `0x00458090`, and `0x00458100` is intentionally absent as a stale-boundary guard.

Wave957 (`cfepdevelopment-world-list-review-wave957`) re-read the cluster with fresh serialized metadata/tags/xref/instruction/decompile exports and made no mutation. It verified `0x004584d0 CFEPDevelopment__Render`, `0x00458ce0 CFEPDevelopment__ResolveActiveStorageDevice`, `0x00458710 CFEPDevelopment__RefreshWorldListCore`, the stale-boundary guard `0x00458100`, and the surrounding world-list/storage context. Wave911 focused re-audit progress is `292/1408 = 20.74%`; static closure remains `6151/6151 = 100.00%`; verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260528-111610_post_wave957_cfepdevelopment_world_list_review_verified`. Layout notes stay mode-qualified because world-file listing, storage/save refresh, and timer scheduling share offsets.

## Functions

| Address | Name | Saved signature | Evidence boundary |
| --- | --- | --- | --- |
| `0x00458050` | `CFEPDevelopment__CompareWorldFileNamePtrs` | `int __cdecl CFEPDevelopment__CompareWorldFileNamePtrs(char * * left, char * * right)` | Comparator passed to the generic quick-sort wrapper for world-file name ordering. |
| `0x00458090` | `CFEPDevelopment__EnumerateWorldFiles` | `bool __fastcall CFEPDevelopment__EnumerateWorldFiles(void * this)` | Corrected true boundary for world-file enumeration/allocation/filter/sort; supersedes stale mid-body `0x00458100`. |
| `0x004581e0` | `CFEPDevelopment__Shutdown` | `void __fastcall CFEPDevelopment__Shutdown(void * this)` | Releases world-list state and resets list fields. |
| `0x004583c0` | `CFEPDevelopment__RenderWorldListEntries` | `void __fastcall CFEPDevelopment__RenderWorldListEntries(void * this)` | Renders world-list rows for the development frontend page. |
| `0x004584d0` | `CFEPDevelopment__Render` | `void __thiscall CFEPDevelopment__Render(void * this, float transition, int dest)` | Corrected calling convention; renders the page and delegates list-entry rendering. |
| `0x00458710` | `CFEPDevelopment__RefreshWorldListCore` | `bool __fastcall CFEPDevelopment__RefreshWorldListCore(void * this)` | Core refresh helper after storage-device context resolution. |
| `0x004589f0` | `CFEPDevelopment__RefreshWorldList` | `void __fastcall CFEPDevelopment__RefreshWorldList(void * this)` | Wrapper that pushes zero to the resolver and refreshes the list core. |
| `0x00458ce0` | `CFEPDevelopment__ResolveActiveStorageDevice` | `void __thiscall CFEPDevelopment__ResolveActiveStorageDevice(void * this, int unused_refresh_arg)` | Corrected to `ret 0x4` thiscall shape; observed caller pushes zero and current body does not consume the argument. |
| `0x00459580` | `CFEPDevelopment__ScheduleWorldListRefresh` | `void __thiscall CFEPDevelopment__ScheduleWorldListRefresh(void * this, int ignored_arg)` | Corrected to `ret 0x4` thiscall shape; schedules or triggers the world-list refresh path. |

## Evidence

- Wave957 read-only review verified `13` metadata rows, `13` tag rows, `221` xref rows, `877` instruction rows, and `13` decompile-index rows. `0x00458100` remains `MISSING`; instruction evidence at that address is still a `PUSH 0x62921c` inside `CFEPDevelopment__EnumerateWorldFiles`, not a function prologue.
- Wave957 preserved the Wave384 calling-convention evidence: `0x004584d0 CFEPDevelopment__Render` ends with `RET 0x8`, while `0x00458ce0 CFEPDevelopment__ResolveActiveStorageDevice` and `0x00459580 CFEPDevelopment__ScheduleWorldListRefresh` use `RET 0x4`; `0x004589f0` and `0x00459580` both push zero before calling the resolver.
- Wave957 documented the static bridge from `0x004623e0 CFEPMain__DoAction` into `CFEPDevelopment__RefreshWorldList`, then into storage-device query/dialog routing through `0x00458710 CFEPDevelopment__RefreshWorldListCore`, `0x00466ae0 CFrontEnd__SetPage`, and `0x00468770 CFrontEnd__PlaySound`.
- `ApplyFepDevelopmentWave384.java` dry/apply created the comparator, moved `CFEPDevelopment__EnumerateWorldFiles` from `0x00458100` to `0x00458090`, and saved signatures/comments/tags for `9` current targets.
- Post-apply metadata read-back verifies `0x00458100` as missing, which is expected after the boundary correction.
- Instruction/callsite evidence shows `CFEPDevelopment__RefreshWorldList` and `CFEPDevelopment__ScheduleWorldListRefresh` push a zero argument before calling `CFEPDevelopment__ResolveActiveStorageDevice`.
- `CFEPDevelopment__ResolveActiveStorageDevice`, `CFEPDevelopment__ScheduleWorldListRefresh`, and `CFEPDevelopment__Render` use `ret 0x4` / `ret 0x8` stack cleanup patterns that justify the saved thiscall signatures.
- The refreshed whole-database quality queue after Wave 384 reports `6027` functions, `1423` commented functions, `4604` commentless functions, `1935` undefined signatures, and `1917` `param_N` signatures.

## Not Proven

- Runtime development-menu world-list behavior or storage-device behavior.
- Runtime development-menu reachability or save-dialog behavior.
- Exact `FEPDevelopment.cpp` source-body recovery from Stuart's checked source snapshot.
- Concrete `CFEPDevelopment` structure layout, local variable names/types, or field semantics for every touched offset.
- BEA launch behavior, game patching, packaged-app behavior, or rebuildable gameplay parity.
