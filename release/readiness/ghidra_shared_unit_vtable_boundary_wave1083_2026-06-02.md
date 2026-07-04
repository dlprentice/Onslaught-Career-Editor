# Ghidra Shared Unit Vtable Boundary Wave1083 Readiness Note

Status: complete static mutation/read-back evidence
Date: 2026-06-02
Scope: `shared-unit-vtable-boundary-review-wave1083`

Wave1083 recovered and saved thirteen previously unresolved shared unit-family vtable-boundary functions in the loaded Steam retail Ghidra database. The pass focused on repeated `.text` code pointers from sampled `CAirUnit`, `CRadar`, `CGillMHead`, `CHiveBoss`, `CGroundUnit`, `CInfantryUnit`, `CSimpleBuilding`, `CPod`, `CSubmarine`, and `CSentinel` vtable rows.

Recovered targets:

| Address | Saved name | Static evidence |
| --- | --- | --- |
| `0x00405d90` | `SharedUnitVFunc__ReturnField130ColorMask_00405d90` | Reads `this+0x130` and returns one of two packed color/mask constants; 17 sampled vtable references now resolve. |
| `0x00405e60` | `SharedUnitVFunc__ReturnFloat005d8ba0_00405e60` | Returns static float `0x005d8ba0`; 11 sampled vtable references now resolve. |
| `0x004f9260` | `SharedUnitVFunc__BuildField164TargetVectorContext_004f9260` | Builds a large stack-local target/vector context when `this+0x164` is present; stops before `0x004f9430 CUnit__ApplyRandomDestructibleDamageBurst`; 8 sampled vtable references now resolve. |
| `0x004fda90` | `SharedUnitVFunc__FindActiveMemberByField18c_004fda90` | Walks `this+0x18c`, calls `0x004e43d0`, and returns a boolean-style result; stops before `0x004fdad0 CUnit__TrySpawnMembersForTarget`; 10 sampled vtable references now resolve. |
| `0x004fdd00` | `SharedUnitVFunc__SetField244ModeAndDispatchF4_004fdd00` | Checks `this+0x244`, builds a context through `0x004fd910`, dispatches virtual slot `+0xf4`, and writes mode `1`; 10 sampled vtable references now resolve. |
| `0x004fe2b0` | `SharedUnitVFunc__MarkField17cEntriesForName_004fe2b0` | Walks `this+0x17c`, compares a name-like field through `0x00568390`, and sets entry `+0x9c` on non-matches; 10 sampled vtable references now resolve. |
| `0x004fe310` | `SharedUnitVFunc__TestField17cEntryNameMatch_004fe310` | Walks `this+0x17c`, compares a name-like field through `0x00568390`, and returns a boolean-style result; stops before `0x004fe390 CEngine__EnableThingByNameFlag`; 10 sampled vtable references now resolve. |
| `0x00417630` | `SharedUnitVFunc__ReturnObject114OrOne_00417630` | Returns object `+0x114` when present and `1` otherwise; stops before `0x004176a0 CBuilding__scalar_deleting_dtor`; 10 sampled vtable references now resolve. |
| `0x00405e70` | `SharedUnitVFunc__IsField168Null_00405e70` | Tests `this+0x168` and returns whether it is null; stops before `SharedVFunc__WriteZeroVectorRet04_00405e80`; 10 sampled vtable references now resolve. |
| `0x004fe5c0` | `SharedUnitVFunc__ReturnField164B4ScaledByMode_004fe5c0` | Returns `this+0x164+0xb4` directly or scaled by static float `0x005d8bd8` for modes `1`/`2`; 10 sampled vtable references now resolve. |
| `0x00405ea0` | `SharedUnitVFunc__ReturnFloat005d8578_00405ea0` | Returns static float `0x005d8578`; 10 sampled vtable references now resolve. |
| `0x00405eb0` | `SharedUnitVFunc__CopyVector1cToOut_00405eb0` | `RET 0x4` helper copies four dwords from `this+0x1c` into caller output; 9 sampled vtable references now resolve. |
| `0x004fe5f0` | `SharedUnitVFunc__ScheduleEvent7d0WithMinusOne_004fe5f0` | Builds a small `-1.0` payload and calls the event-manager-like object at `0x00672fc8` with event id `0x7d0`; 10 sampled vtable references now resolve. |

Read-back evidence:

- `ApplySharedUnitVtableBoundaryWave1083.java` dry/apply/final dry reported `updated=0 skipped=0 created=0 would_create=13 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=0 bad=0`, then `updated=13 skipped=0 created=13 would_create=0 renamed=0 would_rename=0 signature_updated=13 comment_only_updated=0 bad=0`, then `updated=0 skipped=13 created=0 would_create=0 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=0 bad=0`, with `REPORT: Save succeeded`.
- Pre exports verified `13` missing metadata rows, `0` tag rows with `13` missing, `425` xref rows, `1131` around-instruction rows, and `1600` selected vtable-slot rows.
- Post exports verified `13` metadata rows, `13` tag rows, `425` xref rows, `335` function-body instruction rows, `13` decompile rows, and `1600` selected vtable-slot rows.
- The selected vtable-slot export improved from `1109` OK / `491` `NO_FUNCTION_AT_POINTER` to `1244` OK / `356` `NO_FUNCTION_AT_POINTER`; the thirteen recovered targets account for `135` sampled vtable-slot occurrences now resolving to saved functions.
- Queue closure after Wave1083 is `6307/6307 = 100.00%`, with `0` commentless, `0` exact-undefined signatures, and `0` `param_N` signatures. Wave911 focused progress remains `812/1408 = 57.67%`; expanded static re-audit surface advances to `1418/1560 = 90.90%`; top-500 coverage remains `500/500 = 100.00%`.
- Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260602-114534_post_wave1083_shared_unit_vtable_boundary_verified`, 19 files, 174820231 bytes, `DiffCount=0`.

What this proves:

- The thirteen target function rows exist in the saved Ghidra project.
- The saved signatures, names, comments, and tags read back from the loaded retail database.
- The sampled unit-family vtable rows now resolve the recovered code pointers instead of reporting `NO_FUNCTION_AT_POINTER`.
- The observed bodies are static retail Ghidra evidence tied to vtable slots, xrefs, instruction exports, decompile exports, and read-back metadata.

What remains separate proof:

- Exact source virtual names.
- Concrete unit-family layout semantics.
- Runtime targeting/render/event/list behavior.
- Runtime gameplay outcomes.
- BEA patching behavior.
- Rebuild parity.

Probe token anchor: Wave1083; shared-unit-vtable-boundary-review-wave1083; `0x00405d90 SharedUnitVFunc__ReturnField130ColorMask_00405d90`; `0x004f9260 SharedUnitVFunc__BuildField164TargetVectorContext_004f9260`; `0x004fe5f0 SharedUnitVFunc__ScheduleEvent7d0WithMinusOne_004fe5f0`; `0x005e3700`; `0x005dd710`; `1418/1560 = 90.90%`; `812/1408 = 57.67%`; `6307/6307 = 100.00%`; `[maintainer-local-ghidra-backup-root]\BEA_20260602-114534_post_wave1083_shared_unit_vtable_boundary_verified`; boundary recovery.
