# EventFunction.cpp - Function Mappings

> Source file/debug path: `[maintainer-local-source-export-root]\MissionScript\EventFunction.cpp` (0x0064cce0)
> Last updated: 2026-05-19

## Overview

`CEventFunction` is the retail MissionScript event-function container. Wave577 saved clean Ghidra signatures, comments, and tags for the full five-function EventFunction.cpp slice after headless dry/apply/read-back. The binary initializes through a `CRelaxedSquad`-like vtable during construction/destruction setup, but exact source class hierarchy and source-body identity remain unproven from the current Stuart source snapshot.

Key retail evidence:

- Event-function vtable: `0x005e4ef8`.
- Event-function parameter wrapper vtable: `0x005e4d50`.
- Constructor and clone allocate 8-byte parameter wrapper nodes and require datatype id `3`.
- Execute stages wrapper objects into the observed local 10-slot array before calling `CScriptObjectCode__CallEventDirect`.

The runtime event behavior remains unproven. This page records saved static Ghidra evidence only, not runtime dispatch behavior, concrete layout finality, BEA patching, or rebuild parity.

2026-06-08 event/object-code lifecycle schema proof: `missionscript-event-object-code-lifecycle-proof.md` and `missionscript-event-object-code-lifecycle.v1.json` now preserve this owner file as the static callback bridge between `CScriptEventNB__PostEvent` and `CScriptObjectCode__CallEventDirect`. The schema anchors `CEventFunction__Execute`, its observed local 10-slot staging array, `0x005e4d50`, `IScript__ScheduleEvent`, `CScriptObjectCode__CallEvent`, `CScriptObjectCode__CallEventDirect`, descriptor dependency `0x0064ce50`, and `795` loose event-name counts as corpus context. This is static callback lifecycle accounting only, not runtime callback execution, exact event-parameter layout, live loose-MSL loading, patch, Godot, rebuild, or no-noticeable-difference proof.

## Wave577 static read-back

Wave577 targeted the adjacent queue-head EventFunction tranche and applied no renames:

| Address | Saved signature | Evidence summary |
| --- | --- | --- |
| `0x0052f9a0` | `void __thiscall CEventFunction__Destructor(void * this)` | Installs `0x005e4ef8`, walks the CSPtrSet at `this+0x0c` through iterator slot `this+0x14`, frees 8-byte wrappers through `DAT_009c3df0`, clears the set twice, then calls `CMonitor__Shutdown`. |
| `0x0052fa50` | `void * __thiscall CEventFunction__ScalarDeletingDestructor(void * this, byte flags)` | Vtable slot at `0x005e4efc`; `RET 0x4` confirms one `flags` stack argument after `ECX=this`; frees `this` when `flags&1` is set. |
| `0x0052fa70` | `void * __thiscall CEventFunction__CEventFunction(void * this, void * script_object_code, void * bytecode_reader)` | `RET 0x8`; switches from the `0x005d92d4` CRelaxedSquad-like vtable to `0x005e4ef8`, stores owner at `this+0x1c`, reads event id/count from the bytecode reader, resolves symbol indexes through `CScriptObjectCode__GetInstruction`, requires datatype id `3`, and appends wrappers allocated at EventFunction.cpp line `0x40`. |
| `0x0052fbb0` | `void * __thiscall CEventFunction__Clone(void * this, void * cloned_script_object_code)` | `RET 0x4`; allocates a `0x20`-byte clone at line `0x4e`, copies the event id, initializes the parameter list, resolves source symbols through owner `+0x58`, verifies datatype id `3`, compares string getter slot `+0x38`, and appends line-`0x1b` wrapper nodes. |
| `0x0052fda0` | `void __thiscall CEventFunction__Execute(void * this)` | Register-only `this`; walks `this+0x0c`, allocates 8-byte `CEventFunctionParam` wrappers at line `0x96`, installs vtable `0x005e4d50`, copies payload byte from `wrapped_object+0x04+0x14`, stores into the local 10-slot array, and calls `CScriptObjectCode__CallEventDirect`. |

Read-back artifacts:

- Dry/apply/final dry: `updated=0 skipped=5`, `updated=5 skipped=0`, `updated=0 skipped=5`; all with `missing=0`, `bad=0`, and `REPORT: Save succeeded`.
- Post exports: `5` metadata rows, `5` tag rows, `6` xref rows, `1305` instruction rows, `5` decompile rows, and `144` vtable rows.
- Queue refresh after Wave577: `6093` functions, `2922` commented, `3171` commentless, `1425` exact-undefined signatures, and `1139` `param_N` signatures.
- Verified Ghidra project backup: `[maintainer-local-ghidra-backup-root]\BEA_20260519-030958_post_wave577_eventfunction_verified`, `19` files, `160435079` bytes, manifest hash `103451E61F6E5D10504B6B778BBC2CEC6530FF68CAF1C320FAA68FE997299305`.

## Functions

| Address | Name | Wave577 status | Notes |
| --- | --- | --- | --- |
| `0x0052f9a0` | `CEventFunction__Destructor` | Signature/comment/tag saved | Parameter-list cleanup and monitor shutdown. |
| `0x0052fa50` | `CEventFunction__ScalarDeletingDestructor` | Signature/comment/tag saved | MSVC scalar-deleting destructor wrapper. |
| `0x0052fa70` | `CEventFunction__CEventFunction` | Signature/comment/tag saved | Bytecode-backed constructor over event id and string parameter symbols. |
| `0x0052fbb0` | `CEventFunction__Clone` | Signature/comment/tag saved | Clone path with symbol-table lookup and string-name comparison. |
| `0x0052fda0` | `CEventFunction__Execute` | Signature/comment/tag saved | Event dispatch wrapper allocation and `CScriptObjectCode__CallEventDirect` call. |

## Related Data

### Vtables

| Address | Evidence | Notes |
| --- | --- | --- |
| `0x005e4ef8` | `CEventFunction` vtable | Slot `+0x04` points at `CEventFunction__ScalarDeletingDestructor`. |
| `0x005e4d50` | `CEventFunctionParam`/datatype-region vtable evidence | Execute installs this vtable on the transient 8-byte event parameter wrappers. |
| `0x005d92d4` | CRelaxedSquad-like vtable candidate | Constructor/destructor setup uses this before switching to `CEventFunction`; exact hierarchy remains unproven. |

### Error Strings

| Address | Message | Context |
| --- | --- | --- |
| `0x0064cd38` | `FATAL ERROR: Event Function was expecting a string` | Constructor datatype guard. |
| `0x0064cd6c` | `FATAL ERROR can't find event string in symbol table` | Clone symbol lookup failure. |
| `0x0064cda0` | `FATAL ERROR: Data type wrong type in clone for event function` | Clone datatype guard. |
| `0x0064cde0` | `FATAL ERROR: Could not find symbol table in clone` | Clone owner/symbol-table guard. |

## Cross-References

| Function | Observed callers / data refs |
| --- | --- |
| `CEventFunction__Destructor` | Called by `CEventFunction__ScalarDeletingDestructor`. |
| `CEventFunction__ScalarDeletingDestructor` | Data ref from vtable slot `0x005e4efc`. |
| `CEventFunction__CEventFunction` | Called by `CScriptObjectCode__CScriptObjectCode`. |
| `CEventFunction__Clone` | Called by `CScriptObjectCode__Clone`. |
| `CEventFunction__Execute` | Called by `CScriptEventNB__PostEvent` and `CScriptEventNB__HandleEventMessage`. |

## Proof Boundary

Wave577 improves saved static Ghidra readability and queue telemetry for the EventFunction.cpp slice. The runtime event behavior remains unproven, including actual mission event firing behavior, concrete parameter payload semantics, parameter count safety, exact source class hierarchy, BEA patching, and rebuild parity.
