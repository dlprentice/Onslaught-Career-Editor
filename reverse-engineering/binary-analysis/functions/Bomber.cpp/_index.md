# Bomber.cpp Functions

> Source File: Bomber.cpp | Binary: BEA.exe
> Debug Path: 0x00623a78

> **Queue status (2026-05-26):** Ghidra export-contract closure **6113/6113** (Wave900: every function commented; clean-signature proxy; not evidence-grade semantics). Lines below that reference a "next raw commentless" row are **archival wave progress**, not open work.

## Overview

Bomber aircraft implementation. **NOTE: Bomber.cpp is NOT in Stuart's source code dump** - this is a newly discovered source file from the binary only. Wave 312 corrected four adjacent lifecycle/vtable targets from generic vfunc/helper labels into bounded CBomberAI and CBomberGuide destructor names. Wave557 then recovered the primary CBomber scalar-deleting destructor wrapper and destructor body in the WorldPhysicsManager factory/lifecycle range. Wave1026 re-read the CBomberAI/CBomberGuide destructor rows under `ai-dtor-lifecycle-review-wave1026` with no mutation while preserving the missing-source boundary.

## Wave1026 AI Destructor Lifecycle Review

Wave1026 (`ai-dtor-lifecycle-review-wave1026`) re-read `0x004161a0 CBomberAI__scalar_deleting_dtor`, `0x004161c0 CBomberAI__dtor_body_004161c0`, `0x00416260 CBomberGuide__scalar_deleting_dtor`, and `0x00416280 CBomberGuide__dtor_body_00416280`. Fresh evidence confirmed the scalar wrappers call their body rows, test the scalar-delete flag, optionally free through `CDXMemoryManager__Free`, and return `this`. `CBomberAI__dtor_body_004161c0` keeps the same monitor/safe-reader cleanup pattern as the adjacent UnitAI bodies, while `CBomberGuide__dtor_body_00416280` remains the narrower guide-reader cleanup case at `+0x2c` before `CMonitor__Shutdown`. Verified backup: `G:\GhidraBackups\BEA_20260601-013000_post_wave1026_ai_dtor_lifecycle_review_verified`. Bomber.cpp source remains missing, so exact source-body identity, exact class hierarchy/layouts, runtime cleanup behavior, allocator ownership beyond observed static calls, BEA patching, gameplay outcomes, and rebuild parity remain separate proof.

## Functions

| Address | Name | Purpose | Status |
|---------|------|---------|--------|
| 0x004160e4 | CBomber__Constructor_1 | First constructor stage | NOT A FUNCTION (inline code) |
| 0x0041611d | CBomber__Constructor_2 | Second constructor stage | NOT A FUNCTION (inline code) |
| 0x004161a0 | CBomberAI__scalar_deleting_dtor | Scalar-deleting destructor wrapper; calls `CBomberAI__dtor_body_004161c0` and optionally frees the object | SAVED |
| 0x004161c0 | CBomberAI__dtor_body_004161c0 | Destructor body; unregisters pointer-set links at `+0x28`, `+0x24`, and `+0xc`, then calls `CMonitor__Shutdown` | SAVED |
| 0x00416260 | CBomberGuide__scalar_deleting_dtor | Scalar-deleting destructor wrapper; calls `CBomberGuide__dtor_body_00416280` and optionally frees the object | SAVED |
| 0x00416280 | CBomberGuide__dtor_body_00416280 | Destructor body; unregisters pointer-set link `+0x2c`, then calls `CMonitor__Shutdown` | SAVED |
| 0x0050ed60 | CBomber__scalar_deleting_dtor | Wave557 primary CBomber vtable slot-1 wrapper; calls `CBomber__ClearPtrSetsRemoveFromGlobalListAndDestruct` and optionally frees `this` on `delete_flags & 1` | SAVED |
| 0x0050efa0 | CBomber__ClearPtrSetsRemoveFromGlobalListAndDestruct | Wave557 primary CBomber destructor body; clears owned pointer sets, removes the global-list node, then calls `CUnit__dtor_base` | SAVED |

**Note:** The constructor code at 0x004160e4 and 0x0041611d is not recognized as standalone functions by Ghidra. These appear to be inline code blocks within a larger initialization routine.

## Exception Handlers

| Address | Name | Line | Purpose |
|---------|------|------|---------|
| 0x005d1400 | Unwind@005d1400 | 0x11 | Wave743 saved `void __cdecl` cleanup callback; frees pointer at `EBP+4` through `OID__FreeObject_Callback` with Bomber.cpp debug path `0x00623a78` and memtype `0x17` |
| 0x005d1416 | Unwind@005d1416 | 0x12 | Wave743 saved `void __cdecl` cleanup callback; frees pointer at `EBP+4` through `OID__FreeObject_Callback` with Bomber.cpp debug path `0x00623a78` and memtype `0x16` |

## Key Observations

- **Global instance** - References global CBomber object at 0x9c3df0
- **VTable pointer** - Uses vtable at 0x5D8DBC; destructor slot evidence now reaches the saved CBomberAI/CBomberGuide scalar-deleting wrappers.
- **Multi-stage init** - Constructor split across multiple code blocks
- **Missing source** - Bomber.cpp not provided by Stuart - may contain unique mechanics
- **Line numbers** - Debug info shows lines 17, 18, 22 in original source
- **Lifecycle boundary** - Saved destructor names are static retail-binary evidence only; exact source methods, class layout, runtime AI behavior, and rebuild parity remain unproven.
- **Wave557 primary destructor** - The primary `CBomber__scalar_deleting_dtor` and `CBomber__ClearPtrSetsRemoveFromGlobalListAndDestruct` names are static retail-binary evidence from vtable slot 1 and direct wrapper/body xrefs. Exact source virtual names, concrete layout, runtime destruction behavior, and rebuild parity remain unproven.
- **Wave743 unwind continuation** - `0x005d1400 Unwind@005d1400` and `0x005d1416 Unwind@005d1416` now have saved comments/tags/signatures with `unwind-continuation-wave743` and `wave743-readback-verified`. The pass also records adjacent monitor/active-reader callbacks at `0x005d13d0` through `0x005d13e3`. Verified backup: `G:\GhidraBackups\BEA_20260522-160155_post_wave743_unwind_continuation_verified`; next high-signal queue head after the wave is `0x005d1610 Unwind@005d1610`, while the raw commentless head remains `0x0042f220 CSPtrSet__Clear`. Runtime bomber cleanup behavior, exact source body identity, and rebuild parity remain unproven.

## Investigation Needed

1. Find the parent function containing 0x004160e4
2. Determine if CBomber inherits from CAirUnit or similar
3. Check if Stuart has Bomber.cpp (request if missing)
4. Continue vtable review past the corrected lifecycle wrappers at 0x004161a0 and 0x00416260

## Related Files

- AirUnit.cpp - Likely parent class (debug path at 0x00622cf4)
- DiveBomber.cpp - Related bomber variant (debug path at 0x006289c0)
- GroundAttackAircraft.cpp - Similar aircraft class (debug path at 0x0062cadc)

---
*Discovered via Phase 1 xref analysis (Dec 2025)*
*Note: Source file NOT in Stuart's code dump - binary-only discovery*
