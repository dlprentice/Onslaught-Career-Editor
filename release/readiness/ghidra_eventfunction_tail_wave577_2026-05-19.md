# Wave577 CEventFunction Tail Static Ghidra Readiness

Date: 2026-05-19

## Scope

Wave577 saved static Ghidra signatures, comments, and tags for the EventFunction.cpp queue-head tranche:

| Address | Saved signature | Notes |
| --- | --- | --- |
| `0x0052f9a0` | `void __thiscall CEventFunction__Destructor(void * this)` | Parameter CSPtrSet cleanup and `CMonitor__Shutdown`. |
| `0x0052fa50` | `void * __thiscall CEventFunction__ScalarDeletingDestructor(void * this, byte flags)` | Vtable slot `0x005e4efc`, `RET 0x4`, frees `this` when `flags&1`. |
| `0x0052fa70` | `void * __thiscall CEventFunction__CEventFunction(void * this, void * script_object_code, void * bytecode_reader)` | Reads event id/count, resolves symbol indexes, requires datatype id `3`, and appends wrappers allocated at EventFunction.cpp line `0x40`. |
| `0x0052fbb0` | `void * __thiscall CEventFunction__Clone(void * this, void * cloned_script_object_code)` | Allocates a `0x20`-byte clone, resolves symbols through owner `+0x58`, compares string getter slot `+0x38`, and appends line-`0x1b` wrappers. |
| `0x0052fda0` | `void __thiscall CEventFunction__Execute(void * this)` | Allocates `CEventFunctionParam` wrappers with vtable `0x005e4d50`, stages the observed local 10-slot array, and calls `CScriptObjectCode__CallEventDirect`. |

No renames were applied. No `source-parity` tag was applied because the current Stuart source snapshot does not include the matching implementation body.

## Evidence

- Apply script: `tools/ApplyEventFunctionTailWave577.java`.
- Focused probe: `tools/ghidra_eventfunction_tail_wave577_probe.py`.
- Scratch root: `subagents/ghidra-static-reaudit/wave577-eventfunction-tail-0052f9a0`.
- Dry/apply/final dry summaries: `updated=0 skipped=5`, `updated=5 skipped=0`, `updated=0 skipped=5`; each had `renamed=0`, `missing=0`, `bad=0`, and `REPORT: Save succeeded`.
- Post exports: `5` metadata rows, `5` tag rows, `6` xref rows, `1305` instruction rows, `5` decompile rows, and `144` vtable rows.
- Queue refresh after Wave577: `6093` total functions, `2922` commented, `3171` commentless, `1425` exact-undefined signatures, `1139` `param_N` signatures.
- Next queue head: `0x005333b0 CMonitor__ctor_like_005333b0`.

## Backup

Verified Ghidra project backup:

```text
[maintainer-local-ghidra-backup-root]\BEA_20260519-030958_post_wave577_eventfunction_verified
```

Backup verification reported `PASS`, `19` files, `160435079` bytes, `diffCount=0`, and manifest hash `103451E61F6E5D10504B6B778BBC2CEC6530FF68CAF1C320FAA68FE997299305`.

## Deferrals

This is saved static retail Ghidra evidence only. The runtime event behavior remains unproven, including concrete mission event dispatch behavior, exact EventFunction/source hierarchy, concrete symbol/datatype layouts, parameter count safety, BEA patching, and rebuild parity.
