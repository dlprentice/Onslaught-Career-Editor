# Submarine.cpp Functions

> Source File: Submarine.cpp | Binary: BEA.exe
> Debug Path: 0x00632abc

> **Queue status (2026-05-26):** Ghidra export-contract closure **6113/6113** (Wave900: every function commented; clean-signature proxy; not evidence-grade semantics). Lines below that reference a "next raw commentless" row are **archival wave progress**, not open work.

## Overview

Submarine unit implementation. CSubmarine handles underwater vessel mechanics including AI behavior and guidance systems. Inherits from CUnit.

Wave767 static read-back (`unwind-continuation-wave767`, `wave767-readback-verified`) saved comments/tags/signatures for Submarine.cpp-adjacent compiler-generated unwind cleanup callbacks from `0x005d4fc0 Unwind@005d4fc0` through `0x005d5030 Unwind@005d5030`. Exact anchors include `0x005d5000 Unwind@005d5000`. Evidence includes Submarine.cpp debug path `0x00632abc`, DATA scope-table xrefs `0x0061d83c` through `0x0061d8a4`, two allocation-free callbacks, monitor/active-reader cleanup rows, and the `0x005d5030 Unwind@005d5030` `CController__dtor_Thunk` row. Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260523-164622_post_wave767_unwind_continuation_verified`. Exact parent source-body identity, runtime exception behavior, runtime cleanup behavior, BEA patching, and rebuild parity remain deferred.

## Functions

| Address | Name | Purpose | Size |
|---------|------|---------|------|
| 0x004eec80 | CSubmarine__Init | Init body that creates SubmarineAI and SubmarineGuide components | ~400 bytes |
| 0x004eedc0 | CSubmarineAI__ScalarDeletingDestructor | Scalar-deleting destructor wrapper for the submarine AI component | ~32 bytes |
| 0x004eede0 | CSubmarineAI__DestructorBody | Derived submarine AI destructor body that restores CUnitAI base state and unregisters tracked links | ~160 bytes |

## Exception Handlers

| Address | Name | Line | Purpose |
|---------|------|------|---------|
| 0x005d4fc0 | Unwind@005d4fc0 | 29 | Cleanup for CSubmarineAI allocation (0x60 bytes) |
| 0x005d4fd6 | Unwind@005d4fd6 | 30 | Cleanup for CSubmarineGuide allocation (0x20 bytes) |

## Key Observations

- **Component classes** - CSubmarineAI (AI behavior) and CSubmarineGuide (pathfinding)
- **Inherits CUnit** - Calls CUnit__Init as base class
- **RTTI found** - `.?AVCSubmarine@@`, `.?AVCSubmarineAI@@`, `.?AVCSubmarineGuide@@`
- **VTables** - Main: 0x005e14b4, AI: 0x005df404, Guide: 0x005df438

## Component Functions

| Address | Name | Purpose |
|---------|------|---------|
| 0x004fe710 | CWarspite__Init | Shared AI/base init helper invoked during `CSubmarine__Init` before the AI vtable is set to `0x005df404` (schedules fighting/waypoint events; name likely not final) |
| 0x004ef570 | CSubmarineGuide__CSubmarineGuide | Guidance/pathfinding constructor; saved as `void * __thiscall CSubmarineGuide__CSubmarineGuide(void * this, void * owner_submarine)` and sets vtable `0x005df438` |

## Wave512 Static Read-Back (2026-05-17)

Wave512 saved signatures/comments/tags for the init and component lifecycle helpers above. The pass corrected the stale `CSubmarineAI__VFunc_01_004eedc0` name to `CSubmarineAI__ScalarDeletingDestructor` and the stale `CUnitAI__ctor_like_004eede0` owner/purpose to `CSubmarineAI__DestructorBody`.

This is static retail Ghidra evidence only. Runtime submarine behavior, exact source-body identity, concrete CSubmarine/CSubmarineAI/CSubmarineGuide layouts, pathfinding behavior, game launch, patching, and rebuild parity remain unproven.

## Wave767 Submarine.cpp Unwind Continuation

Wave767 hardened six Submarine.cpp-adjacent unwind callbacks as `void __cdecl Unwind@...(void)` without renames, function-boundary changes, or executable-byte changes.

| Address | Evidence |
| --- | --- |
| 0x005d4fc0 | DATA xref `0x0061d83c`; `OID__FreeObject_Callback(*(EBP+0x4))` with Submarine.cpp line token `0x1d` and allocation/type value `0x16`. |
| 0x005d4fd6 | DATA xref `0x0061d844`; `OID__FreeObject_Callback(*(EBP+0x4))` with Submarine.cpp line token `0x1e` and allocation/type value `0x17`. |
| 0x005d5000 | DATA xref `0x0061d86c`; `CMonitor__Shutdown(*(EBP-0x10))`. |
| 0x005d5008 | DATA xref `0x0061d874`; `CGenericActiveReader__dtor((*(EBP-0x10))+0x0c)`. |
| 0x005d5013 | DATA xref `0x0061d87c`; `CGenericActiveReader__dtor((*(EBP-0x10))+0x24)`. |
| 0x005d5030 | DATA xref `0x0061d8a4`; `CController__dtor_Thunk(EBP-0x184)`. |

This is static saved-Ghidra metadata/decompile/xref evidence only. Runtime submarine behavior, exact component/controller layout, exact source-body identity, BEA patching, and rebuild parity remain unproven.

## Related Files

- Unit.cpp - CUnit base class
- Boat.cpp - Related water vehicle (surface)

---
*Discovered via Phase 1 xref analysis (Dec 2025)*
