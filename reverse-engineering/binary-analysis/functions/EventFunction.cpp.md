# EventFunction.cpp - Function Mappings

> Source file/debug path: `[maintainer-local-source-export-root]\MissionScript\EventFunction.cpp` (0x0064cce0)
> Last updated: 2026-08-18 (ctor entry-PC + Execute CallEventDirect pin;
> named-event occupancy) — RTTI 2026-08-17; prior text 2026-05-19

## Overview

`CEventFunction` is the retail MissionScript event-function container. Wave577 saved clean Ghidra signatures, comments, and tags for the full five-function EventFunction.cpp slice after headless dry/apply/read-back. The binary initializes through the `CMonitor` base vtable during construction/destruction setup (RTTI-settled 2026-08-17: `CEventFunction : CMonitor : IListener`; see the note after the vtable table). Source-body identity against the current Stuart source snapshot remains unproven.

Key retail evidence:

- Event-function vtable: `0x005e4ef8`.
- Event-function latch wrapper vtable: `0x005e4d50` (`CBoolDataType`).
- Constructor reads a 4-byte **entry PC** into `this+8` and a 4-byte
  param count, then one symbol index per param (datatype must be `3`).
- Execute stages one `CBoolDataType` (vtable `0x005e4d50`) per listen-name
  from `byte [listenerElement+0x14]`, then
  `CallEventDirect(owner=this+0x1c, entryPC=this+8, …)`.
  That is the only `E8` to `CallEventDirect`. Every shipped entry PC is
  `JMPFALSE` over that bool.

The runtime event behavior remains unproven. This page records saved static Ghidra evidence only, not runtime dispatch behavior, concrete layout finality, BEA patching, or rebuild parity.

The current static contract places `CEventFunction__Execute` in the event path
`IScript__ScheduleEvent` → `CScriptEventNB__PostEvent` →
`CEventFunction__Execute` → `CScriptObjectCode__CallEventDirect`.
Runtime callback execution and exact event-parameter layout remain separate
proof.

## Wave577 static read-back

Wave577 targeted the adjacent queue-head EventFunction tranche and applied no renames:

| Address | Saved signature | Evidence summary |
| --- | --- | --- |
| `0x0052f9a0` | `void __thiscall CEventFunction__Destructor(void * this)` | Installs `0x005e4ef8`, walks the CSPtrSet at `this+0x0c` through iterator slot `this+0x14`, frees 8-byte wrappers through `DAT_009c3df0`, clears the set twice, then calls `CMonitor__Shutdown`. |
| `0x0052fa50` | `void * __thiscall CEventFunction__ScalarDeletingDestructor(void * this, byte flags)` | Vtable slot at `0x005e4efc`; `RET 0x4` confirms one `flags` stack argument after `ECX=this`; frees `this` when `flags&1` is set. |
| `0x0052fa70` | `void * __thiscall CEventFunction__CEventFunction(void * this, void * script_object_code, void * bytecode_reader)` | `RET 0x8`; switches from the `0x005d92d4` `CMonitor` base vtable to `0x005e4ef8`, stores owner at `this+0x1c`, reads **entry PC** into `this+8` then param count, resolves each symbol index through `[owner+0x58]`, requires datatype id `3`, and appends wrappers allocated at EventFunction.cpp line `0x40`. |
| `0x0052fbb0` | `void * __thiscall CEventFunction__Clone(void * this, void * cloned_script_object_code)` | `RET 0x4`; allocates a `0x20`-byte clone at line `0x4e`, copies the event id, initializes the parameter list, resolves source symbols through owner `+0x58`, verifies datatype id `3`, compares string getter slot `+0x38`, and appends line-`0x1b` wrapper nodes. |
| `0x0052fda0` | `void __thiscall CEventFunction__Execute(void * this)` | Register-only `this`; walks `this+0x0c`, allocates 8-byte `CBoolDataType` wrappers (vtable `0x005e4d50`, line `0x96`), copies `byte [listenerElement+0x14]` into `wrapper+4`, and calls `CScriptObjectCode__CallEventDirect`. The 994 shipped entry PCs are all `JMPFALSE` on that bool. |

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
| `0x005e4d50` | `CBoolDataType` vtable (RTTI `.?AVCBoolDataType@@`) | Execute installs this on the transient 8-byte latch wrapper. Slot `+0x3c` is `CBoolDataType__VFunc_15_0052e480`. The live name-cohort label superseded `CEventFunctionParam`. |
| `0x005d92d4` | `CMonitor` base vtable | Constructor/destructor setup uses this before switching to `CEventFunction`. RTTI-settled 2026-08-17, not `CRelaxedSquad`-like. |

### Error Strings

| Address | Message | Context |
| --- | --- | --- |
| `0x0064cd38` | `FATAL ERROR: Event Function was expecting a string` | Constructor datatype guard. |
| `0x0064cd6c` | `FATAL ERROR can't find event string in symbol table` | Clone symbol lookup failure. |
| `0x0064cda0` | `FATAL ERROR: Data type wrong type in clone for event function` | Clone datatype guard. |

## RTTI hierarchy note (2026-08-17)

The COLOC walk from the pristine `74154bfa…` image settles the class hierarchy
the 2026-05-19 text left open. `CEventFunction`'s Complete Object Locator is
`0x00619538`, stored at `vtable-4` (`0x005e4ef4`); its type descriptor
`0x0064cd18` carries the mangled name `.?AVCEventFunction@@`, and its base
array is `CEventFunction` → `CMonitor` (`.?AVCMonitor@@`) →
`IListener` (`.?AVIListener@@`). The vtable `0x005e4ef8` therefore overrides
the three `CMonitor` virtuals as: slot 0 `HandleEvent` = the shared base no-op
`0x004014c0` (a `CEventFunction` used as an event-manager `to_call` ignores
the event), slot 1 = `CEventFunction__ScalarDeletingDestructor`
(`0x0052fa50`), slot 2 = base `CMonitor__Shutdown_Core` (`0x004bacb0`). The
dword at `0x005e4f04` (`vtable+0xc`) is the adjacent `IScript` vtable's COLOC
`0x00619588`, not a fourth `CEventFunction` slot. See
[`CScriptEventNB.cpp.md`](CScriptEventNB.cpp.md) for the sibling classes
(`IScript`, `CVM`, `CPostEventData`, `CScriptEventNB`).
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

Wave577 improves saved static Ghidra readability and queue telemetry for the EventFunction.cpp slice. The runtime event behavior remains unproven, including actual mission event firing behavior, concrete parameter payload semantics, parameter count safety, BEA patching, and rebuild parity. The class hierarchy is no longer in that set: RTTI settles it as `CEventFunction : CMonitor : IListener` (2026-08-17 note below).
