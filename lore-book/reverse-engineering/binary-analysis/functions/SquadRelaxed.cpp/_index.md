# SquadRelaxed.cpp Functions

> Source File: SquadRelaxed.cpp | Binary: BEA.exe
> Debug Path: 0x00632918 (`[maintainer-local-source-export-root]\SquadRelaxed.cpp`)

> **Queue status (2026-05-26):** Ghidra export-contract closure **6113/6113** (Wave900: every function commented; clean-signature proxy; not evidence-grade semantics). Lines below that reference a "next raw commentless" row are **archival wave progress**, not open work.

## Overview

CRelaxedSquad is an AI squad behavior state representing the idle/patrol mode for enemy squads. This is the counterpart to CSquadNormal which handles active combat. When enemies are not engaged with the player, they operate in the "relaxed" state with less aggressive behavior patterns.

**Class Name:** `CRelaxedSquad` (from RTTI at 0x0063d928)
**Display Name:** "Relaxed Squad" (string at 0x0063293c)

Wave1215 static read-back (`wave1215-unit-targeting-combat-residual-current-risk-review`) re-read `CRelaxedSquad__CreateIterator` as relaxed-squad iterator evidence. DATA xref `0x005e3b10` ties the row to the relaxed-squad table; the body allocates a `0x10`-byte `CSPtrSet`, calls `CSPtrSet__Init`, walks member nodes at `this+0xa4`, adds non-null members with `CSPtrSet__AddToHead`, and returns the set snapshot. Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260607-090802_post_wave1215_unit_targeting_combat_residual_current_risk_review_verified`. Runtime relaxed-squad AI behavior, iterator ownership/lifetime, concrete member-node layout, BEA patching behavior, rebuild parity, and no-noticeable-difference parity remain separate proof.

Wave767 static read-back (`unwind-continuation-wave767`, `wave767-readback-verified`) saved comments/tags/signatures for SquadRelaxed.cpp-adjacent compiler-generated unwind cleanup callbacks from `0x005d4e60 Unwind@005d4e60` through `0x005d4ed0 Unwind@005d4ed0`. Exact anchors include `0x005d4e90 Unwind@005d4e90`. Evidence includes SquadRelaxed.cpp debug path `0x00632918`, DATA scope-table xrefs `0x0061d6f4` through `0x0061d77c`, `OID__FreeObject_Callback`, `CComplexThing__dtor_base`, `CGenericActiveReader__dtor`, and `CParticleManager__RemoveFromGlobalList_Thunk` cleanup rows. Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260523-164622_post_wave767_unwind_continuation_verified`. Exact parent source-body identity, runtime exception behavior, runtime cleanup behavior, BEA patching, and rebuild parity remain deferred.

Wave1009 (`geometry-guide-heightfield-spine-review-wave1009`) recovered `0x004eaae0 CRelaxedSquad__VFunc_07_004eaae0` as a DATA-backed relaxed-squad static-shadow caller boundary. Queue closure is `6233/6233 = 100.00%`; verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260531-155648_post_wave1009_geometry_guide_heightfield_spine_review_verified`. Runtime relaxed-squad/debug-overlay behavior, exact source virtual name, concrete layouts, BEA patching, and rebuild parity remain separate proof.

## Functions

| Address | Name | Purpose | Size |
|---------|------|---------|------|
| 0x004ea8d0 | CRelaxedSquad__CreateIterator | Wave510 stale-purpose correction; allocates a 0x10-byte `CSPtrSet`, walks `this+0xa4`, adds non-null members, and returns the member iterator/snapshot set | ~150 bytes |
| 0x004e5840 | CSPtrSet__Init | Initialize empty pointer-set (head/tail/count = 0) | ~20 bytes |
| 0x004ea4d0 | (undefined) | Vtable entry +0x04 - likely destructor or state handler | ~unknown |
| 0x004ea780 | (undefined) | Vtable entry +0x08 - contains debug path xref | ~unknown |
| 0x004ea840 | (undefined) | Vtable entry +0x14 - member access pattern | ~unknown |
| 0x004ea980 | (undefined) | Vtable entry +0x1C - uses FPU, accesses member list | ~unknown |
| 0x004eaa5c | (undefined) | Uses "Relaxed Squad" display string | ~unknown |

## Vtable Analysis

**Vtable Address:** 0x005e3ad0

| Offset | Address | Notes |
|--------|---------|-------|
| +0x00 | 0x00405930 | Base class (shared with other squad types) |
| +0x04 | 0x004ea4d0 | CRelaxedSquad-specific |
| +0x08 | 0x004ea780 | CRelaxedSquad-specific (has debug path xref) |
| +0x0C | 0x004014c0 | Base class |
| +0x10 | 0x00405930 | Base class |
| +0x14 | 0x004ea840 | CRelaxedSquad-specific |
| +0x18 | 0x0043e9f0 | Possibly inherited |
| +0x1C | 0x004ea980 | CRelaxedSquad-specific |
| +0x20 | 0x004e8cd0 | Possibly shared |
| +0x24 | 0x0050f600 | Possibly inherited |

A second vtable reference exists at 0x005e3b10, suggesting class hierarchy or multiple inheritance.

## Key Observations

- **State Machine Pattern**: CRelaxedSquad is one state in the squad AI system. Squads transition between relaxed (patrol/idle) and normal (combat) states.
- **Member List at +0xa4**: Wave510 corrected `0x004ea8d0` from `CRelaxedSquad__Create` to `CRelaxedSquad__CreateIterator`. The function iterates through a linked list at `this+0xa4`, adding each member to a set via `CSPtrSet__AddToHead`; static evidence supports an iterator/snapshot helper rather than a relaxed-squad factory.
- **Memory Allocation**: Uses `OID__AllocObject(0x10, 8, ...)` pattern - allocates 16 bytes with type 8.
- **Exception Handling**: Create function sets up SEH with unwind handler at `Unwind@005d4e60`.
- **Undefined Code Region**: Most vtable entries point to code that hasn't been disassembled in Ghidra (0x004ea4d0-0x004eaa5c range). These need manual function creation.

## Related Files

- SquadNormal.cpp - Combat squad state (counterpart to relaxed)
- Squad.cpp - Base squad class
- Unit.cpp - Individual unit behavior (squad members)

## Strings

| Address | Value | Usage |
|---------|-------|-------|
| 0x00632918 | `[maintainer-local-source-export-root]\SquadRelaxed.cpp` | Debug path for assertions |
| 0x0063293c | `Relaxed Squad` | Display name |
| 0x0063d900 | `.?AVCRelaxedSquad@@` | RTTI type descriptor |
| 0x0063d928 | `CRelaxedSquad` | Class name |

## Wave767 SquadRelaxed.cpp Unwind Continuation

Wave767 hardened six SquadRelaxed.cpp-adjacent unwind callbacks as `void __cdecl Unwind@...(void)` without renames, function-boundary changes, or executable-byte changes.

| Address | Evidence |
| --- | --- |
| 0x005d4e60 | DATA xref `0x0061d6f4`; `OID__FreeObject_Callback(*(EBP-0x10))` with SquadRelaxed.cpp line token `0xa0` and allocation/type value `0x08`. |
| 0x005d4e90 | DATA xref `0x0061d71c`; `CComplexThing__dtor_base(*(EBP-0x10))`. |
| 0x005d4e98 | DATA xref `0x0061d724`; `CGenericActiveReader__dtor((*(EBP-0x10))+0x7c)`. |
| 0x005d4eb0 | DATA xref `0x0061d74c`; second `CComplexThing__dtor_base(*(EBP-0x10))` cleanup row. |
| 0x005d4eb8 | DATA xref `0x0061d754`; second `CGenericActiveReader__dtor((*(EBP-0x10))+0x7c)` cleanup row. |
| 0x005d4ed0 | DATA xref `0x0061d77c`; `CParticleManager__RemoveFromGlobalList_Thunk(EBP-0x14)`. |

This is static saved-Ghidra metadata/decompile/xref evidence only. Exact parent source-body identity, runtime exception behavior, runtime cleanup behavior, BEA patching, and rebuild parity remain unproven.

---
*Discovered via Phase 1 xref analysis (Dec 2025); Wave510 corrected the `0x004ea8d0` purpose/signature on 2026-05-17.*
