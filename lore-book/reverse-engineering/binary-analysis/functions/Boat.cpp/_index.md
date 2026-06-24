# Boat.cpp Functions

Wave1219 final current-risk closure note: `CBoat__Init` and `CBoatGuide__ctor` remain mapped to the Boat init/guide-construction path; verified backup `G:\GhidraBackups\BEA_20260607-230027_post_wave1219_final_score16_current_risk_review_verified`. Runtime boat/guide behavior, exact layouts, and rebuild parity remain separate proof.

> Source File: Boat.cpp | Binary: BEA.exe
> Debug Path: 0x00623990

> **Queue status (2026-05-26):** Ghidra export-contract closure **6113/6113** (Wave900: every function commented; clean-signature proxy; not evidence-grade semantics). Lines below that reference a "next raw commentless" row are **archival wave progress**, not open work.

## Overview

Water vehicle (boat) implementation. CBoat handles surface vessel mechanics. Wave 310 hardened the saved `CBoat__Init` signature and corrected adjacent BoatAI/UnitAI lifecycle wrappers from older vfunc/ctor-like labels to bounded destructor names. Wave 312 corrected the adjacent `CBoatGuide` constructor wrapper signature from an over-wide constructor-like decompile. Wave1026 re-read the adjacent BoatAI/UnitAI destructor lifecycle rows under `ai-dtor-lifecycle-review-wave1026` with no mutation.

## Wave1026 AI Destructor Lifecycle Review

Wave1026 (`ai-dtor-lifecycle-review-wave1026`) re-read the Boat.cpp-adjacent destructor lifecycle rows `0x00414fa0 CBoatAI__scalar_deleting_dtor`, `0x00414fc0 CBoatAI__dtor_body_00414fc0`, `0x00415060 CUnitAI__scalar_deleting_dtor`, and `0x00415080 CUnitAI__dtor_body_00415080`. Fresh metadata/tags/xrefs/instructions/decompile confirmed the scalar wrappers call their body rows, test the scalar-delete flag, optionally free through `CDXMemoryManager__Free`, and return `this`; the destructor bodies restore vtable `0x005d8d1c`, remove reader cells at `+0x28/+0x24/+0x0c` through `CSPtrSet__Remove`, and call `CMonitor__Shutdown`. Context re-read covered `0x00414e50 CBoat__Init`, `0x00415d70 CBoatGuide__ctor`, `0x00417390 CBuilding__CreateRepairPadAI`, and `0x004a03b0 CUnitAI__dtor_base`. Verified backup: `G:\GhidraBackups\BEA_20260601-013000_post_wave1026_ai_dtor_lifecycle_review_verified`. Runtime cleanup behavior, exact source-body identity, exact class hierarchy/layouts, allocator ownership beyond observed static calls, BEA patching, gameplay outcomes, and rebuild parity remain separate proof.

## Functions

| Address | Name | Purpose | Size |
|---------|------|---------|------|
| 0x00414e50 | CBoat__Init | Initializes boat state after `CGroundUnit__Init`; allocates 0x20 and 0x60 byte helper objects | ~300 bytes |
| 0x00414fa0 | CBoatAI__scalar_deleting_dtor | Scalar-deleting destructor wrapper; calls `CBoatAI__dtor_body_00414fc0` and optionally frees the object | ~30 bytes |
| 0x00414fc0 | CBoatAI__dtor_body_00414fc0 | Destructor body; resets vtable, unregisters pointer-set links, and calls `CMonitor__Shutdown` | ~160 bytes |
| 0x00415060 | CUnitAI__scalar_deleting_dtor | Scalar-deleting destructor wrapper; calls `CUnitAI__dtor_body_00415080` and optionally frees the object | ~30 bytes |
| 0x00415080 | CUnitAI__dtor_body_00415080 | Destructor body; resets vtable, unregisters pointer-set links, and calls `CMonitor__Shutdown` | ~160 bytes |
| 0x00415d70 | CBoatGuide__ctor | Constructor wrapper called by `CBoat__Init`; calls `CGuide__ctor_like_0047e290`, writes vtable `0x005d8d5c`, and returns `this` | ~24 bytes |

## Exception Handlers

| Address | Name | Line | Purpose |
|---------|------|------|---------|
| 0x005d1360 | Unwind@005d1360 | 30 | Cleanup for first allocation (0x20 bytes, pool 0x17) |
| 0x005d1376 | Unwind@005d1376 | 31 | Cleanup for second allocation (0x60 bytes, pool 0x16) |

Wave742 unwind continuation saved both Boat.cpp rows as `void __cdecl Unwind@...(void)` with `unwind-continuation-wave742` and `wave742-readback-verified` tags. The saved comments record Boat.cpp debug path `0x00623990`, scope-table DATA xrefs `0x0061a1ec` and `0x0061a1f4`, `OID__FreeObject_Callback` on the pointer at `EBP+4`, line `0x1e` / memtype `0x17` for `0x005d1360 Unwind@005d1360`, and line `0x1f` / memtype `0x16` for `0x005d1376 Unwind@005d1376`. The same tranche spans `0x005d1170 Unwind@005d1170` through `0x005d13b3 Unwind@005d13b3`; next high-signal queue head is `0x005d13d0 Unwind@005d13d0`, and earliest raw commentless row remains `0x0042f220 CSPtrSet__Clear`.

Verified backup: `G:\GhidraBackups\BEA_20260522-153147_post_wave742_unwind_continuation_verified`. This is saved static retail Ghidra evidence only. Exact parent source body, runtime exception behavior, runtime cleanup behavior, BEA patching, and rebuild parity remain unproven.

## Key Observations

- **Two allocations** - 0x20 and 0x60 byte objects at lines 30-31
- **Member offsets** - Stores at +0x208 and +0x13c
- **State flags** - Sets +0x7c, +0x80 to 2, ORs +0x70 with 0x2100000
- **VTable** - Second object uses vtable at 0x005d8ce8
- **Zeroed fields** - Clears +0x260, +0x264, +0x268
- **Wave 310 signature** - `CBoat__Init` is saved as `void __thiscall CBoat__Init(void * this, void * init)`.
- **Destructor wrappers** - BoatAI and UnitAI scalar-deleting wrappers test flag bit 0 before optional `OID__FreeObject`.
- **Destructor bodies** - Both checked destructor bodies set vtable `0x005d8d1c`, unregister pointer-set links at `+0x28`, `+0x24`, and `+0xc`, and call `CMonitor__Shutdown`.
- **BoatGuide constructor** - The saved `CBoatGuide__ctor` signature is `void * __thiscall CBoatGuide__ctor(void * this, void * init)`; instruction evidence shows one stack argument and a `ret 0x4`.
- **Boundary** - Exact class hierarchy, concrete member layout, tag/local/type recovery, and runtime lifecycle behavior remain unproven.

## Related Files

- GroundUnit.cpp - Similar land-based unit
- Submarine.cpp - Related water vehicle (underwater)

---
*Discovered via Phase 1 xref analysis (Dec 2025)*
