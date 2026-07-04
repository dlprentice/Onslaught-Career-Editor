# Ghidra AI Destructor Lifecycle Review Wave1026 Readiness Note

Status: complete read-only static review
Date: 2026-06-01
Scope: `ai-dtor-lifecycle-review-wave1026`

Wave1026 re-read twelve adjacent BoatAI, UnitAI, BomberAI, BomberGuide, RepairPadAI, and Building scalar-deleting destructor wrappers/bodies from the expanded Wave911 post-top-500 surface. The review made no mutation: no Ghidra mutation, no rename, no signature change, no comment/tag change, no function-boundary change, and no executable-byte change.

Primary targets:

| Address | Saved state | Fresh evidence |
| --- | --- | --- |
| `0x00414fa0 CBoatAI__scalar_deleting_dtor` | `void * __thiscall CBoatAI__scalar_deleting_dtor(void * this, int flags)` | DATA xref `0x005d8cec`; calls `0x00414fc0`; tests `flags & 1`; optionally frees through `CDXMemoryManager__Free`; returns `this`. |
| `0x00414fc0 CBoatAI__dtor_body_00414fc0` | `void __fastcall CBoatAI__dtor_body_00414fc0(void * this)` | Body installs vtable `0x005d8d1c`, removes reader cells at `+0x28/+0x24/+0x0c` through `CSPtrSet__Remove`, then calls `CMonitor__Shutdown`. |
| `0x00415060 CUnitAI__scalar_deleting_dtor` | `void * __thiscall CUnitAI__scalar_deleting_dtor(void * this, int flags)` | DATA xref `0x005d8d20`; calls `0x00415080`; tests `flags & 1`; optionally frees through `CDXMemoryManager__Free`; returns `this`. |
| `0x00415080 CUnitAI__dtor_body_00415080` | `void __fastcall CUnitAI__dtor_body_00415080(void * this)` | Called by the scalar wrapper and unwind callbacks `0x005d2b2c`/`0x005d3460`; removes reader cells at `+0x28/+0x24/+0x0c`; calls `CMonitor__Shutdown`. |
| `0x004161a0 CBomberAI__scalar_deleting_dtor` | `void * __thiscall CBomberAI__scalar_deleting_dtor(void * this, int flags)` | DATA xref `0x005d8d8c`; calls `0x004161c0`; tests `flags & 1`; optionally frees through `CDXMemoryManager__Free`; returns `this`. Bomber.cpp source remains missing. |
| `0x004161c0 CBomberAI__dtor_body_004161c0` | `void __fastcall CBomberAI__dtor_body_004161c0(void * this)` | Body installs vtable `0x005d8d1c`, removes reader cells at `+0x28/+0x24/+0x0c`, then calls `CMonitor__Shutdown`. Bomber.cpp source remains missing. |
| `0x00416260 CBomberGuide__scalar_deleting_dtor` | `void * __thiscall CBomberGuide__scalar_deleting_dtor(void * this, int flags)` | DATA xref `0x005d8dc0`; calls `0x00416280`; tests `flags & 1`; optionally frees through `CDXMemoryManager__Free`; returns `this`. |
| `0x00416280 CBomberGuide__dtor_body_00416280` | `void __fastcall CBomberGuide__dtor_body_00416280(void * this)` | Removes the guide reader cell at `+0x2c` through `CSPtrSet__Remove`, then calls `CMonitor__Shutdown`. |
| `0x00417480 CRepairPadAI__scalar_deleting_dtor` | `void * __thiscall CRepairPadAI__scalar_deleting_dtor(void * this, int flags)` | DATA xref `0x005d8e0c`; calls `0x004174a0`; tests `flags & 1`; optionally frees through `CDXMemoryManager__Free`; returns `this`. |
| `0x004174a0 CRepairPadAI__dtor_body_004174a0` | `void __fastcall CRepairPadAI__dtor_body_004174a0(void * this)` | Body installs vtable `0x005d8d1c`, removes reader cells at `+0x28/+0x24/+0x0c`, then calls `CMonitor__Shutdown`. |
| `0x00417590 CBuilding__dtor_body_00417590` | `void __fastcall CBuilding__dtor_body_00417590(void * this)` | Called by `0x004176a0`; resets vtable `0x005d8eb4` and render-position table pointer `0x005d8e3c`, then calls `CUnit__dtor_base`. |
| `0x004176a0 CBuilding__scalar_deleting_dtor` | `void * __thiscall CBuilding__scalar_deleting_dtor(void * this, int flags)` | DATA xref `0x005d8eb8`; calls `0x00417590`; tests `flags & 1`; optionally frees through `CDXMemoryManager__Free`; returns `this`. |

Context evidence covered `0x00414e50 CBoat__Init`, `0x00415d70 CBoatGuide__ctor`, `0x00417390 CBuilding__CreateRepairPadAI`, and `0x004a03b0 CUnitAI__dtor_base`.

Evidence counts:

- Primary exports: 12 metadata rows, 12 tag rows, 14 xref rows, 301 body-instruction rows, and 12 decompile rows.
- Context exports: 4 metadata rows, 4 tag rows, 4 xref rows, 215 body-instruction rows, and 4 decompile rows.
- Queue closure remains `6238/6238 = 100.00%` with 0 commentless, 0 exact-undefined signatures, and 0 `param_N`.
- Wave911 focused re-audit progress after Wave1026: `588/1408 = 41.76%`; expanded static surface progress: `817/1493 = 54.72%`; Wave911 top-500 risk-ranked coverage remains `500/500 = 100.00%`.
- Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260601-013000_post_wave1026_ai_dtor_lifecycle_review_verified`, 19 files, 173968263 bytes, `DiffCount=0`, `HashDiffCount=0`.

What this proves:

- The saved destructor wrapper/body names, signatures, comments, xrefs, instruction bodies, and decompiles for the selected BoatAI, UnitAI, BomberAI, BomberGuide, RepairPadAI, and Building teardown rows remain internally coherent.
- The scalar wrappers still show one explicit delete flag stack argument and return `this`.
- The AI destructor bodies still preserve the monitor/safe-reader cleanup pattern through `CSPtrSet__Remove` and `CMonitor__Shutdown`; `CBomberGuide` remains the narrower guide-reader cleanup case at `+0x2c`.
- The CBuilding destructor body still resets the Building vtable/render-position table state before forwarding to CUnit cleanup.

What remains unproven:

- Runtime cleanup behavior or destructor side-effect completeness.
- Exact source-body identity, especially for Bomber.cpp rows where source remains missing.
- Exact class hierarchy, concrete layouts, field names, or allocator ownership beyond observed static offsets/calls.
- Runtime boat/bomber/repair-pad/building behavior.
- BEA patch behavior, gameplay outcomes, and rebuild parity.
