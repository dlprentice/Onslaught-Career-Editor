# CPhysicsScript.cpp - Function Mappings

> Retail-binary function mappings for `CPhysicsScript.cpp`
> Last updated: 2026-05-12

## Current Status

Wave1019 re-read the five manager lifecycle/load/factory rows with fresh metadata, tags, xrefs, instructions, decompile, context exports, and a verified live-project backup. The review made no mutation: the Wave330 names/signatures/comments remain coherent with current static Ghidra evidence. Probe token anchor: Wave1019; physics-script-manager-lifecycle-review-wave1019; 0x0042e880 CPhysicsScript__Create; 0x0042e8f0 CPhysicsScript__Destroy; 0x0042e950 CPhysicsScript__Load; 0x0042ea60 CPhysicsScript__Update; 0x0042eb90 CPhysicsScript__CreateStatement; 523/1408 = 37.14%; 752/1493 = 50.37%; 452/500 = 90.40%; 6238/6238 = 100.00%; [maintainer-local-ghidra-backup-root]\BEA_20260531-211749_post_wave1019_physics_script_manager_lifecycle_review_verified; no mutation.

Wave 330 saved Ghidra signature/comment/tag refinements for the five already named `CPhysicsScript` manager helpers. The current evidence is retail-binary read-back from Ghidra metadata, decompile, xref, instruction, and tag exports. Treat these as bounded static findings, not proof of exact source body identity, complete statement layouts, runtime physics-script behavior, or rebuild parity.

Wave1103 consolidated these rows into the subsystem-level [PhysicsScript static contract](../physics-script-static-contract.md) alongside statement loader/create/recurse/lifetime and registry/apply evidence. The contract is a static map for schema and rebuild planning only; runtime PhysicsScript behavior, serialized file-format completeness, exact layouts, and rebuild parity remain separate proof.

Debug path evidence still points at `[maintainer-local-source-export-root]\CPhysicsScript.cpp` (`0x0062568c`). Related statement implementations reference `CPhysicsScriptStatements.cpp` (`0x00625818`).

## Wave747 unwind continuation callbacks

Wave747 unwind continuation saved `void __cdecl Unwind@...(void)` signatures, comments, and tags for the CPhysicsScript-adjacent cleanup callbacks at `0x005d1d00 Unwind@005d1d00`, `0x005d1d50 Unwind@005d1d50`, `0x005d1da0 Unwind@005d1da0`, `0x005d1df0 Unwind@005d1df0`, `0x005d1e60 Unwind@005d1e60`, `0x005d1eb0 Unwind@005d1eb0`, `0x005d1f00 Unwind@005d1f00`, `0x005d1f20 Unwind@005d1f20`, `0x005d1f40 Unwind@005d1f40`, `0x005d1f60 Unwind@005d1f60`, `0x005d1f80 Unwind@005d1f80`, and `0x005d1fa0 Unwind@005d1fa0`. The statement rows call `CPhysicsScriptStatement__dtor` on the pointer at `EBP-0x10`; the value rows call `CPhysicsUnitValue__dtor_base` or `CPhysicsRoundValue__dtor_base` on the same local pointer shape.

The same `unwind-continuation-wave747` tranche spans `0x005d1cd9 Unwind@005d1cd9` through `0x005d1fc0 Unwind@005d1fc0`, including WorldPhysicsManager.h free-object callbacks and the adjacent `0x005d1fc0 Unwind@005d1fc0` CComplexThing teardown callback. Tags include `wave747-readback-verified`. Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260522-180520_post_wave747_unwind_continuation_verified`. Next high-signal queue head is `0x005d1fc8 Unwind@005d1fc8`; earliest raw commentless row remains `0x0042f220 CSPtrSet__Clear`. Exact parent source-body identity, runtime physics-script cleanup behavior, BEA patching, and rebuild parity remain unproven.

## Wave746 unwind continuation callbacks

Wave746 unwind continuation saved `void __cdecl Unwind@...(void)` signatures, comments, and tags for the CPhysicsScript allocation/statement cleanup callbacks at `0x005d1be0 Unwind@005d1be0`, `0x005d1c50 Unwind@005d1c50`, and `0x005d1ca0 Unwind@005d1ca0`. `0x005d1be0` calls `OID__FreeObject_Callback` on `EBP-0x10` with CPhysicsScript.cpp debug path `0x0062568c`, line `0x18`, memtype `0x10`, and DATA scope-table xref `0x0061aa4c`; `0x005d1c50` and `0x005d1ca0` call `CPhysicsScriptStatement__dtor` on the pointer at `EBP-0x10`.

The same `unwind-continuation-wave746` tranche spans `0x005d1aa3 Unwind@005d1aa3` through `0x005d1cc0 Unwind@005d1cc0`, including Controller.cpp and WorldPhysicsManager.h cleanup. Tags include `wave746-readback-verified`. Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260522-173500_post_wave746_unwind_continuation_verified`. Next high-signal queue head is `0x005d1cd9 Unwind@005d1cd9`; earliest raw commentless row remains `0x0042f220 CSPtrSet__Clear`. Exact parent source-body identity, runtime physics-script cleanup behavior, BEA patching, and rebuild parity remain unproven.

## Global

| Address | Name | Notes |
| --- | --- | --- |
| `0x0066e99c` | `g_pPhysicsScript` | Global singleton pointer used by create/destroy/load/update paths. |

## Saved Functions

| Address | Saved signature | Current evidence |
| --- | --- | --- |
| `0x0042e880` | `void __cdecl CPhysicsScript__Create(void)` | Allocates a `0x10` byte manager object with object type `0x18`, initializes the `CSPtrSet`/list fields, stores `g_pPhysicsScript`, and clears the global on allocation failure. |
| `0x0042e8f0` | `void __cdecl CPhysicsScript__Destroy(void)` | Iterates the statement list, removes each node, calls vtable slot `0` with delete flag `1`, clears the set, frees the manager object with `OID__FreeObject`, and nulls `g_pPhysicsScript`. |
| `0x0042e950` | `bool __cdecl CPhysicsScript__Load(void * memBuffer)` | Destroys/recreates the singleton, reads `0x12` from `memBuffer`, loops statement type ids until `-1`, creates statements, calls statement load slot `+0xc` when creation succeeds, and skips bytes when the factory returns null. |
| `0x0042ea60` | `void __cdecl CPhysicsScript__Update(void)` | Iterates the `g_pPhysicsScript` statement list and calls vtable slot `+0x4` for each statement. The null-singleton caller contract remains unproven. |
| `0x0042eb90` | `void * __cdecl CPhysicsScript__CreateStatement(int statementType)` | Factory for observed statement type ids `1..9`; allocates `0x110` byte statement objects, assigns statement-specific vtables, initializes common fields, and returns null outside the known range. |

## Statement Factory Evidence

| Type id | Object type id | Vtable | Notes |
| ---: | ---: | --- | --- |
| `1` | `0x11` | `0x005d9878` | Unit statement candidate from saved vtable label. |
| `2` | `0x13` | `0x005d9850` | Weapon statement candidate from saved vtable label. |
| `3` | `0x12` | `0x005d9864` | Weapon-mode statement candidate from saved vtable label. |
| `4` | `0x14` | `0x005d983c` | Round statement candidate from saved vtable label. |
| `5` | `0x15` | `0x005d9828` | Spawner statement candidate from saved vtable label. |
| `6` | `0x16` | `0x005d9814` | Explosion statement candidate from saved vtable label. |
| `7` | `0x17` | `0x005d9800` | Component statement candidate from saved vtable label. |
| `8` | `0x18` | `0x005d97ec` | Feature statement candidate from saved vtable label. |
| `9` | `0x19` | `0x005d97d8` | Hazard statement candidate from saved vtable label. |

Common observed initialization writes include vtable at `+0x00`, type id at `+0x04`, zero at `+0x08`, byte zero at `+0x0c`, and zero at `+0x10c`. The concrete base class, full field layout, subtype semantics, and runtime behavior remain open.

## Read-Back Summary

Wave1019 read-only re-audit verified `5` metadata rows, `5` tag rows, `5` xref rows, `321` body-instruction rows, and `5` decompile rows for the manager rows, plus `8` context metadata rows, `19` context xref rows, `776` context body-instruction rows, and `8` context decompile rows across `CPhysicsScriptStatement__dtor`, statement load rows, skip-byte fallback, and registry/apply context. Queue closure remains `6238/6238 = 100.00%`; Wave911 focused re-audit progress is `523/1408 = 37.14%`; expanded static surface progress is `752/1493 = 50.37%`; Wave911 top-500 risk-ranked coverage is `452/500 = 90.40%`. Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260531-211749_post_wave1019_physics_script_manager_lifecycle_review_verified`. Runtime physics-script behavior, exact statement and value-list layouts, exact source-body identity, MSL/file-format completeness, BEA patching, and rebuild parity remain separate proof.

Wave 330 headless dry/apply reported `updated=0 skipped=5 renamed=0 missing=0 bad=0` and `updated=5 skipped=0 renamed=0 missing=0 bad=0`, with Ghidra `REPORT: Save succeeded`.

Final read-back verified `5/5` metadata rows, `5/5` decompile exports, `5` xref rows, `425` instruction rows, `5/5` tag rows, and focused probe status `PASS`. The refreshed queue reports `5884` functions, `823` commented functions, `5061` commentless functions, `1983` undefined signatures, and `2269` `param_N` signatures.

## See Also

- [PhysicsScript static contract](../physics-script-static-contract.md)
- [CPhysicsScriptStatements.cpp](CPhysicsScriptStatements.cpp.md)
- [Retained function index](_index.md)
