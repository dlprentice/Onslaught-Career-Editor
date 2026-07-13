# Building.cpp Functions

<!-- ghidra-full-reaudit-20260713:start -->
> **2026-07-13 live correction closeout:** `0x004df520` → `CActor__dtor_base_Thunk` (was `CActor__dtor_base`). Current live Ghidra reflects confirmed rows only; older conflicting text below is superseded only where confirmed. Use the [closeout](../../ghidra-full-reaudit-closeout-2026-07-13.md); final per-address decisions and exact before/after metadata are in `reverse-engineering/binary-analysis/ghidra-reviewed-correction-decisions-2026-07-13.jsonl` and `reverse-engineering/binary-analysis/ghidra-reviewed-correction-plan-2026-07-13.json`.
<!-- ghidra-full-reaudit-20260713:end -->

> Source File: Building.cpp | Binary: BEA.exe
> Debug Path: 0x00623af4

> **Queue status (2026-05-26):** Ghidra export-contract closure **6113/6113** (Wave900: every function commented; clean-signature proxy; not evidence-grade semantics). Lines below that reference a "next raw commentless" row are **archival wave progress**, not open work.

## Overview

Building/structure implementation. CBuilding handles destructible buildings including special types like repair pads with AI behavior. Wave1026 re-read the RepairPadAI and Building destructor lifecycle rows under `ai-dtor-lifecycle-review-wave1026` with no mutation. Wave1174 re-read the active current-risk Building/CBuildingNamedMesh/CNamedMesh animation, occupancy, init, and cleanup rows with fresh Ghidra evidence and no mutation.

Wave1211 (`wave1211-score17-residual-current-risk-review`) re-read and tag-normalized `0x0040c5b0 CRepairPadAI__IsWithinRepairBounds` as one of `8 score-17 residual current-risk rows` in the current-risk denominator. Fresh evidence keeps the helper tied to `CRepairPadAI__IsCompatibleDockCandidate`, comparing repair bounds from `this+0xf8/+0xfc` against the dock candidate's repair-volume offsets under `*(this+0x4b0)+0x1c/+0x20`. No rename, signature, comment, function-boundary, or executable-byte change was made. Active current-risk accounting after the wave is `1110/1179 = 94.15%`; verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260607-061324_post_wave1211_score17_residual_current_risk_review_verified`. Runtime repair-pad docking/repair behavior, exact `CRepairPadAI` layout, BEA patching behavior, rebuild parity, and no-noticeable-difference parity remain separate proof.

## Wave1026 AI Destructor Lifecycle Review

Wave1026 (`ai-dtor-lifecycle-review-wave1026`) re-read `0x00417480 CRepairPadAI__scalar_deleting_dtor`, `0x004174a0 CRepairPadAI__dtor_body_004174a0`, `0x00417590 CBuilding__dtor_body_00417590`, and `0x004176a0 CBuilding__scalar_deleting_dtor`. Fresh evidence confirmed the scalar wrappers call their body rows, test the scalar-delete flag, optionally free through `CDXMemoryManager__Free`, and return `this`. `CRepairPadAI__dtor_body_004174a0` retains the UnitAI-style monitor/safe-reader cleanup through `CSPtrSet__Remove` and `CMonitor__Shutdown`; `CBuilding__dtor_body_00417590` resets vtable `0x005d8eb4` and render-position table pointer `0x005d8e3c` before forwarding to `CUnit__dtor_base`. Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260601-013000_post_wave1026_ai_dtor_lifecycle_review_verified`. Runtime cleanup behavior, exact source-body identity, exact CBuilding/CRepairPadAI layouts, allocator ownership beyond observed static calls, BEA patching, gameplay outcomes, and rebuild parity remain separate proof.

## Functions

| Address | Name | Purpose | Size |
|---------|------|---------|------|
| 0x0040c5b0 | CRepairPadAI__IsWithinRepairBounds | Wave 328 saved comment/tag evidence for repair-pad compatibility bounds helper | small |
| 0x0040c5e0 | CRepairPadAI__HasAnySlotBelowThreshold | Wave 328 saved comment/tag evidence for repair-pad slot-threshold helper | small |
| 0x00417390 | CBuilding__CreateRepairPadAI | Wave 313 saved `void __thiscall` signature with one `init` stack argument; creates repair-pad AI component | ~150 bytes |
| 0x00417480 | CRepairPadAI__scalar_deleting_dtor | Wave 313 corrected scalar-deleting destructor wrapper | ~0x20 bytes |
| 0x004174a0 | CRepairPadAI__dtor_body_004174a0 | Wave 313 corrected destructor body cleanup | ~0x9f bytes |
| 0x00417590 | CBuilding__dtor_body_00417590 | Wave 313 corrected CBuilding destructor body | small |
| 0x004176a0 | CBuilding__scalar_deleting_dtor | Wave 313 corrected scalar-deleting destructor wrapper | ~0x20 bytes |
| 0x00417870 | CBuilding__VFuncSlot_02_RemoveFromWorldUpdateShadowAndForward | Wave 314 corrected generic slot label using CBuilding/CSimpleBuilding vtable evidence | bounded |
| 0x004178a0 | CBuilding__ProcessClosingAndUnshuttingAnimations | Wave 314 corrected stale CUnit owner label | bounded |
| 0x00418120 | CBuilding__AdvanceOpenCloseAnimationState | Wave 314 corrected stale CCockpit owner label | bounded |
| 0x004183d0 | CBuildingNamedMesh__dtor_base | Wave 314 corrected stale CByteSprite deferral to CBuildingNamedMesh | bounded |
| 0x00418430 | CBuildingNamedMesh__scalar_deleting_dtor | Wave 314 corrected stale CByteSprite scalar-deleting destructor owner | bounded |
| 0x00418450 | CBuildingNamedMesh__VFuncSlot_02_RemoveFromWorldAndForwardNamedMesh | Wave 314 corrected stale CByteSprite vfunc owner | bounded |
| 0x004d6d10 | CRepairPadAI__VFunc_11_UpdateDockCandidateReader | Wave491 corrected the CRepairPadAI vtable slot 11 dock-candidate reader refresh helper | bounded |
| 0x004bbcd0 | CNamedMesh__VFunc_09_004bbcd0 | Wave458 comment/tag evidence for NamedMesh init/add-to-world slot with EAX-carried init pointer | bounded |
| 0x004bc050 | CNamedMesh__VFunc02_RemoveFromOccupancyAndForward | Wave458 corrected NamedMesh slot-2 cleanup helper reached by CBuildingNamedMesh forwarding | bounded |

## Exception Handlers

| Address | Name | Line | Purpose |
|---------|------|------|---------|
| 0x005d1490 | Unwind@005d1490 | 0x32 | Wave743 saved `void __cdecl` cleanup callback; frees pointer at `EBP+4` through `OID__FreeObject_Callback` with Building.cpp debug path `0x00623af4` and memtype `0x80` |
| 0x005d14a9 | Unwind@005d14a9 | 0x33 | Wave743 saved `void __cdecl` cleanup callback; frees pointer at `EBP+4` through `OID__FreeObject_Callback` with Building.cpp debug path `0x00623af4` and memtype `0x80` |
| 0x005d14d0 | Unwind@005d14d0 | 0x64 | Wave743 saved `void __cdecl` cleanup callback; frees pointer at `EBP-0x10` through `OID__FreeObject_Callback` with Building.cpp debug path `0x00623af4` and memtype `0x16` |
| 0x005d14e6 | Unwind@005d14e6 | 0x68 | Wave743 saved `void __cdecl` cleanup callback; frees pointer at `EBP-0x10` through `OID__FreeObject_Callback` with Building.cpp debug path `0x00623af4` and memtype `0x16` |

## Key Observations

- **CRepairPadAI** - 96-byte (0x60) AI component for repair buildings
- **"Forseti Repair Pad"** - Special handling for this building type
- **VTable at 0x005d8e08** - CRepairPadAI virtual function table
- **String comparison** - Uses strcmp to check model name
- **Wave 313 signature correction** - `CBuilding__CreateRepairPadAI` now has a saved `void * init` stack argument; `CRepairPadAI` and `CBuilding` lifecycle wrappers/bodies have destructor names rather than vfunc/constructor-like placeholders.
- **Wave 314 owner correction** - RTTI/vtable read-back moved `0x004178a0` and `0x00418120` into CBuilding animation context, and moved `0x004183d0`, `0x00418430`, and `0x00418450` out of ByteSprite into CBuildingNamedMesh context.
- **Wave 328 RepairPadAI helper comments/tags** - `0x0040c5b0` and `0x0040c5e0` remain the saved repair-pad compatibility leaf helpers called by `CRepairPadAI__IsCompatibleDockCandidate`; comments/tags now record the bounds/slot-threshold behavior and keep exact field names/runtime docking proof open.
- **Wave458 NamedMesh vtable evidence** - vtable `0x005dd5f0` slot `2` points to `CNamedMesh__VFunc02_RemoveFromOccupancyAndForward` and slot `9` points to `CNamedMesh__VFunc_09_004bbcd0`. Slot 2 removes the object from world occupancy through `CWorld__RemoveUnitFromOccupancyGrid_Thunk` before forwarding; slot 9 calls `CActor__Init`, sets animation/event state, and adds the object to occupancy/static-shadow tracking, but its EAX-carried init pointer remains a signature-modeling boundary.
- **Wave491 RepairPadAI vtable slot 11** - `0x004d6d10` is now `CRepairPadAI__VFunc_11_UpdateDockCandidateReader`; CRepairPadAI vtable `0x005d8e08` slot 11 points here, the function scans `CMapWho` radius results, calls `CRepairPadAI__IsCompatibleDockCandidate`, updates the active reader cell at `this+0x0c`, sets candidate flags at `this+0x18/+0x1c`, clears `this+0x10`, and returns the current reader pointer.
- **Wave924 RepairPadAI docking review** - `repairpad-docking-review-wave924` re-reviewed `0x004d6d10 CRepairPadAI__VFunc_11_UpdateDockCandidateReader`, `0x004d6e00 CRepairPadAI__IsCompatibleDockCandidate`, `0x0040c5b0 CRepairPadAI__IsWithinRepairBounds`, and `0x0040c5e0 CRepairPadAI__HasAnySlotBelowThreshold` with fresh metadata/tags/xref/instruction/decompile read-back. No mutation was warranted. Wave911 focused re-audit progress after Wave924 is `89/1408 = 6.32%`; static export-contract closure remains `6113/6113 = 100.00%`. Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260527-213142_post_wave924_repairpad_docking_review_verified`.
- **Wave1119 current-risk re-read** - `wave1119-mixed-score26-current-risk-review` re-read `0x004d6d10 CRepairPadAI__VFunc_11_UpdateDockCandidateReader` with fresh metadata/tags/xrefs/instructions/decompile evidence and no mutation. DATA xref `0x005d8e34` still ties the body to `0x005d8e08 slot 11`; decompile evidence preserves `CMapWho__GetFirstEntryWithinRadius`, `CRepairPadAI__IsCompatibleDockCandidate`, and `CGenericActiveReader__SetReader`. Current focused accounting moves to `110/1179 = 9.33%`; verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260605-022812_post_wave1119_mixed_score26_current_risk_review_verified`. Runtime repair/docking behavior, exact layouts, source virtual name, and rebuild parity remain separate proof.
- **Wave1124 current-risk RepairPadAI helper re-read** - `wave1124-repairpad-current-risk-review` re-read `0x0040c5e0 CRepairPadAI__HasAnySlotBelowThreshold` and `0x004d6e00 CRepairPadAI__IsCompatibleDockCandidate` with fresh metadata/tags/xrefs/instructions/decompile evidence and no mutation. The xref chain remains `0x004d6d10 CRepairPadAI__VFunc_11_UpdateDockCandidateReader` -> `0x004d6e00 CRepairPadAI__IsCompatibleDockCandidate` -> `0x0040c5e0 CRepairPadAI__HasAnySlotBelowThreshold`. Current focused accounting moves to `133/1179 = 11.28%`; verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260605-050726_post_wave1124_repairpad_current_risk_review_verified`. Runtime repair-pad docking behavior, runtime repair behavior, exact source-body identity, concrete layouts, and rebuild parity remain separate proof.
- **Wave944 Building/CBuildingNamedMesh lifecycle review** - `building-namedmesh-lifecycle-review-wave944` re-reviewed `0x004176c0 CThing__InitRenderThingFromInitMeshName`, `0x00417870 CBuilding__VFuncSlot_02_RemoveFromWorldUpdateShadowAndForward`, `0x004178a0 CBuilding__ProcessClosingAndUnshuttingAnimations`, `0x00418120 CBuilding__AdvanceOpenCloseAnimationState`, `0x004183d0 CBuildingNamedMesh__dtor_base`, `0x00418430 CBuildingNamedMesh__scalar_deleting_dtor`, `0x00418450 CBuildingNamedMesh__VFuncSlot_02_RemoveFromWorldAndForwardNamedMesh`, and `0x004bc050 CNamedMesh__VFunc02_RemoveFromOccupancyAndForward` with fresh metadata/tags/xref/instruction/decompile/vtable read-back. No mutation was warranted. Wave911 focused re-audit progress after Wave944 is `192/1408 = 13.64%`; static export-contract closure remains `6113/6113 = 100.00%`. Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260528-050722_post_wave944_building_namedmesh_lifecycle_review_verified`.
- **Wave1111 current-risk supersession** - `wave1111-cnamedmesh-current-risk-supersession` accounts for `1 row` from the Wave1108 current focused candidates as superseded by Wave458 (`mesh-optimization-wave458`) and Wave944 (`building-namedmesh-lifecycle-review-wave944`) evidence. Covered anchor: `0x004bc050 CNamedMesh__VFunc02_RemoveFromOccupancyAndForward`, reached from `0x00418450 CBuildingNamedMesh__VFuncSlot_02_RemoveFromWorldAndForwardNamedMesh` and vtable `0x005dd5f0` slot 2. Current focused accounting is `25/1179 = 2.12%`; current focused candidates: 1179. Wave458 backup: `[maintainer-local-ghidra-backup-root]\BEA_20260516-162849_post_wave458_mesh_optimization_verified`; Wave944 backup: `[maintainer-local-ghidra-backup-root]\BEA_20260528-050722_post_wave944_building_namedmesh_lifecycle_review_verified`; latest completed Ghidra backup: `[maintainer-local-ghidra-backup-root]\BEA_20260604-200748_post_wave1100_cmeshpart_load_geometry_review_verified`. This is no new Ghidra export and no mutation.
- **Wave1174 current-risk re-read** - `wave1174-building-namedmesh-current-risk-review` re-read `5 Building/CBuildingNamedMesh/CNamedMesh current-risk rows` with fresh metadata/tags/xrefs/instructions/decompile evidence and no mutation. The pass accounts for `0x00418450 CBuildingNamedMesh__VFuncSlot_02_RemoveFromWorldAndForwardNamedMesh`, `0x004178a0 CBuilding__ProcessClosingAndUnshuttingAnimations`, `0x004bbcd0 CNamedMesh__VFunc_09_004bbcd0`, `0x00418120 CBuilding__AdvanceOpenCloseAnimationState`, and `0x004183d0 CBuildingNamedMesh__dtor_base`. Static closure remains `6411/6411 = 100.00%` with `0 / 0 / 0` debt; Wave1108 current focused accounting is `680/1179 = 57.68%`; current focused candidates: 1178; live regenerated current focused candidates: 1178; remaining active focused work: 499; current risk candidates: 6166; fresh Ghidra export; read-only review; no mutation; Codex read-only consult used; `6 xref rows`; `288 instruction rows`; vtable/data anchors `0x005d8fbc`, `0x005d8fa0`, `0x005d910c`, `0x005d9114`, and `0x005dd5f0`; verified backup `[maintainer-local-ghidra-backup-root]\BEA_20260606-075804_post_wave1174_building_namedmesh_current_risk_review_verified`; wave1108-current-risk-rank; current-risk denominator; focused threshold `15`; not Wave911 reconstruction.
- **Wave743 unwind continuation** - `0x005d1490`, `0x005d14a9`, `0x005d14d0`, and `0x005d14e6` now have saved comments/tags/signatures with `unwind-continuation-wave743` and `wave743-readback-verified`. The adjacent wave also hardened monitor/active-reader callbacks at `0x005d1440` through `0x005d1470`. Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260522-160155_post_wave743_unwind_continuation_verified`; next high-signal queue head after the wave is `0x005d1610 Unwind@005d1610`, while the raw commentless head remains `0x0042f220 CSPtrSet__Clear`.
- **Proof boundary** - Wave 314, Wave458, Wave491, Wave743, Wave924, and Wave944 do not prove exact source virtual names, concrete CBuilding/CRepairPadAI/CBuildingNamedMesh/CNamedMesh layouts, tags, locals, runtime building/repair-pad/named-mesh behavior, runtime exception cleanup behavior, or rebuild parity.

## Wave944 Building/CBuildingNamedMesh Lifecycle Read-only Review

Fresh read-only Ghidra exports on 2026-05-28 verified the six-address Building/CBuildingNamedMesh lifecycle cluster without mutation. This `building-namedmesh-lifecycle-review-wave944` pass is a read-only review. The selected Wave911 rows remain bounded static evidence:

| Address | Fresh static evidence |
| --- | --- |
| `0x004176c0 CThing__InitRenderThingFromInitMeshName` | DATA ref `0x005d8f3c` in the CBuilding table; decompile still builds `%s.msh` render names, calls `PCRTID__CreateObject`, and stores the render object at `this+0x30`. |
| `0x00417870 CBuilding__VFuncSlot_02_RemoveFromWorldUpdateShadowAndForward` | DATA refs `0x005d8ebc` and `0x005dfd44` in CBuilding/CSimpleBuilding slot 2; decompile removes world occupancy, updates static-shadow visibility, and forwards to `0x004f95d0 CUnit__VFunc02_CleanupWorldLinksAndForward`. |
| `0x004178a0 CBuilding__ProcessClosingAndUnshuttingAnimations` | DATA ref `0x005d8fbc`; decompile preserves closing/unshutting state gates over `+0x254/+0x25c/+0x260/+0x264/+0x268`. |
| `0x00418120 CBuilding__AdvanceOpenCloseAnimationState` | DATA ref `0x005d8fa0`; decompile preserves the open/close/shut state stepper through vfunc `+0x58` comparisons and vfunc `+0xf0` transition dispatch. |
| `0x004183d0 CBuildingNamedMesh__dtor_base` | Call xref from `0x00418433 CBuildingNamedMesh__scalar_deleting_dtor`; decompile resets the CBuildingNamedMesh vtable region and forwards to `CActor__dtor_base`. |
| `0x00418450 CBuildingNamedMesh__VFuncSlot_02_RemoveFromWorldAndForwardNamedMesh` | DATA ref `0x005d9114`; decompile removes world occupancy and forwards to `0x004bc050 CNamedMesh__VFunc02_RemoveFromOccupancyAndForward`. |

Context and vtable read-back covered `0x00417590 CBuilding__dtor_body_00417590`, `0x004176a0 CBuilding__scalar_deleting_dtor`, `0x00418430 CBuildingNamedMesh__scalar_deleting_dtor`, `0x004bbcd0 CNamedMesh__VFunc_09_004bbcd0`, `0x004bc050 CNamedMesh__VFunc02_RemoveFromOccupancyAndForward`, `0x004f95d0 CUnit__VFunc02_CleanupWorldLinksAndForward`, and vtables `0x005d8eb4`, `0x005dfd3c`, `0x005d910c`, and `0x005dd5f0`.

Read-back counts: primary `6` metadata rows, `6` tag rows, `7` xref rows, `351` instruction rows, and `6` decompile rows; context `6` metadata rows, `6` tag rows, `28` xref rows, `288` instruction rows, and `6` decompile rows; `192` vtable rows. This is static retail Ghidra evidence only. Runtime building animation behavior, runtime NamedMesh/world-occupancy behavior, exact source virtual names, concrete layouts, BEA patching, and rebuild parity remain open.

## Wave1174 Building / NamedMesh Current-Risk Review

Fresh read-only Ghidra exports on 2026-06-06 verified the active current-risk subset of the Building/CBuildingNamedMesh/CNamedMesh lifecycle cluster without mutation.

| Address | Fresh static evidence |
| --- | --- |
| `0x00418450 CBuildingNamedMesh__VFuncSlot_02_RemoveFromWorldAndForwardNamedMesh` | DATA xref `0x005d9114` under CBuildingNamedMesh vtable `0x005d910c`; removes world occupancy and forwards to `CNamedMesh__VFunc02_RemoveFromOccupancyAndForward`. |
| `0x004178a0 CBuilding__ProcessClosingAndUnshuttingAnimations` | DATA xref `0x005d8fbc`; closing/unshutting gates over fields `+0x254/+0x25c/+0x260/+0x264/+0x268`, with CUnit spawner readiness context. |
| `0x004bbcd0 CNamedMesh__VFunc_09_004bbcd0` | DATA xref `0x005dd614` in CNamedMesh vtable `0x005dd5f0` slot 9; calls `CActor__Init`, schedules event `3000` when gated, and adds to occupancy/static-shadow tracking. |
| `0x00418120 CBuilding__AdvanceOpenCloseAnimationState` | DATA xref `0x005d8fa0`; compares animation ids through vfunc `+0x58`, dispatches state transitions through vfunc `+0xf0`, and updates `+0x254/+0x264`. |
| `0x004183d0 CBuildingNamedMesh__dtor_base` | Call xref from `0x00418433 CBuildingNamedMesh__scalar_deleting_dtor`; resets CBuildingNamedMesh vtable slots and forwards to `CActor__dtor_base`. |

Read-back counts: `5` metadata rows, `5` tag rows, `6 xref rows`, `288 instruction rows`, and `5` decompile rows. Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260606-075804_post_wave1174_building_namedmesh_current_risk_review_verified`. Current-risk accounting after the pass is `680/1179 = 57.68%` with remaining active focused work: 499.

This remains static retail Ghidra evidence only. Runtime building animation behavior, runtime NamedMesh/world-occupancy behavior, exact CBuilding/CBuildingNamedMesh/CNamedMesh/CUnit layouts, exact source virtual names, exact source-body identity, BEA patching behavior, visual QA, gameplay outcomes, and rebuild parity remain separate proof.

## Wave924 RepairPadAI Docking Review

Fresh read-only Ghidra exports on 2026-05-27 verified the four-address RepairPadAI dock-candidate chain without mutation. `0x004d6d10` is still vtable slot 11 from `0x005d8e34`; it calls `0x004d6e00`, which calls both leaf helpers at `0x0040c5b0` and `0x0040c5e0`. Read-back counts: `4` metadata rows, `4` tag rows, `4` xref rows, `174` instruction rows, and `4` decompile rows.

This is static retail Ghidra evidence only. Exact source virtual name, concrete `CRepairPadAI`, candidate-unit, bounds, slot, and state layouts, runtime repair-pad docking behavior, BEA patching, and rebuild parity remain open.

## Wave1124 RepairPadAI Current-Risk Read-only Review

Fresh read-only Ghidra exports on 2026-06-05 verified the two remaining score-23 RepairPadAI current-risk helper rows without mutation. `0x004d6e00 CRepairPadAI__IsCompatibleDockCandidate` is still called by `0x004d6d10 CRepairPadAI__VFunc_11_UpdateDockCandidateReader` at `0x004d6d77`, and `0x0040c5e0 CRepairPadAI__HasAnySlotBelowThreshold` is still called by the compatibility gate at `0x004d6e15`.

| Address | Fresh static evidence |
| --- | --- |
| `0x0040c5e0 CRepairPadAI__HasAnySlotBelowThreshold` | Scans six float slots from `this+0x52c`, uses reference state through `this+0x4b0`, and returns true when a zero-gated slot is below the referenced threshold. |
| `0x004d6e00 CRepairPadAI__IsCompatibleDockCandidate` | Calls `CRepairPadAI__IsWithinRepairBounds`, calls `CRepairPadAI__HasAnySlotBelowThreshold`, then compares candidate and owner state fields at `+0x138`. |

Read-back counts: `2` metadata rows, `2` tag rows, `2` xref rows, `73` instruction rows, and `2` decompile rows. Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260605-050726_post_wave1124_repairpad_current_risk_review_verified`. This remains static Ghidra evidence only; runtime repair-pad docking behavior, runtime repair behavior, exact source-body identity, concrete `CRepairPadAI`, candidate-unit, slot, bounds, state, and owner layouts, BEA patching, and rebuild parity remain separate proof.

## Wave491 RepairPadAI Vtable Slot 11 Hardening

Fresh metadata, decompile, xref, instruction, tag, and vtable-slot read-back on 2026-05-17 hardened one queue-head RepairPadAI virtual-slot target. `ApplyRepairPadVFuncWave491.java` dry/apply/verify-dry reported clean read-back after the script was corrected to compare saved signature components idempotently, and `tools/ghidra_repairpad_vfunc_wave491_probe.py --check` passed.

| Address | Saved signature | Evidence |
| --- | --- | --- |
| `0x004d6d10` | `void * __fastcall CRepairPadAI__VFunc_11_UpdateDockCandidateReader(void * this)` | CRepairPadAI vtable `0x005d8e08` slot 11 points here. The body uses ECX as the register-only receiver, clears the active reader via `CGenericActiveReader__SetReader(this+0x0c, null)`, clears `this+0x18/+0x1c`, scans `CMapWho__GetFirstEntryWithinRadius(..., 8.0)`, filters owner flag bit `0x08`, calls `CRepairPadAI__IsCompatibleDockCandidate`, applies horizontal and vertical-window checks, stores the accepted candidate reader, sets `this+0x18/+0x1c`, clears `this+0x10`, and returns the current reader pointer. |

This is saved static Ghidra evidence only. Exact source virtual name, concrete `CRepairPadAI` layout, runtime repair/docking behavior, BEA launch behavior, game patching, and rebuild parity remain open.

## Wave458 NamedMesh Vtable / Occupancy Hardening

Fresh metadata, decompile, xref, instruction, tag, and vtable-slot read-back on 2026-05-16 hardened two NamedMesh virtual-slot targets adjacent to CBuildingNamedMesh cleanup. `ApplyMeshOptimizationWave458.java` dry/apply/verify-dry reported clean read-back, and `tools/ghidra_mesh_optimization_wave458_probe.py --check` passed.

| Address | Saved signature | Evidence |
| --- | --- | --- |
| `0x004bbcd0` | `void __thiscall CNamedMesh__VFunc_09_004bbcd0(void * this, void * param_1, void * param_2)` | Comment/tag hardening only. Static evidence shows an EAX-carried init pointer not cleanly represented by ordinary Ghidra thiscall storage; the body writes init-derived state, calls `CActor__Init`, sets animation through `CMesh__FindAnimationIndexByName`, optionally schedules event `3000`, and calls `CWorld__AddUnitToOccupancyGridAndRebuildShadows_Thunk`. |
| `0x004bc050` | `void __fastcall CNamedMesh__VFunc02_RemoveFromOccupancyAndForward(void * this)` | Corrected from `CNamedMesh__VFunc_02_004bc050`; vtable `0x005dd5f0` slot 2 and `CBuildingNamedMesh__VFuncSlot_02_RemoveFromWorldAndForwardNamedMesh` xref support the owner/slot. The body calls `CWorld__RemoveUnitFromOccupancyGrid_Thunk(this)` and forwards to `VFuncSlot_02_004f41b0`. |

These are saved static Ghidra facts only. Runtime NamedMesh actor behavior, occupancy/static-shadow effects, concrete layouts, exact source-body identities, BEA launch behavior, game patching, and rebuild parity remain open.

## CBuilding Member Offsets

| Offset | Size | Field | Notes |
|--------|------|-------|-------|
| 0x13c | 4 | mAI | AI component pointer |
| 0x164 | 4 | pLevelData | Level data pointer |
| 0x1f4 | 4 | mHasRepairPad | Repair pad flag (set to TRUE) |

These offsets remain evidence labels from decompile/read-back context, not concrete class layout proof.

## Level Data Offsets

| Offset | Field | Notes |
|--------|-------|-------|
| 0xb0 | mModelName | Model name string pointer |

## Related Classes

```
CBuilding
  ├── CRepairPadAI (component, 96 bytes)
  └── CBuildingNamedMesh (adjacent RTTI/vtable-backed owner group)
```

## Related Files

- Unit.cpp - Base unit class (CBuilding likely inherits from CUnit)
- Component.cpp - Component system (also uses CRepairPadAI vtable)

---
*Updated by the Ghidra static re-audit RepairPadAI helper comment/tag tranche (2026-05-12), Wave458 NamedMesh vtable/occupancy hardening (2026-05-16), Wave491 RepairPadAI vtable-slot hardening (2026-05-17), Wave743 unwind-continuation hardening (2026-05-22), Wave944 Building/CBuildingNamedMesh lifecycle review (2026-05-28), Wave1124 RepairPadAI current-risk review (2026-06-05), and Wave1174 Building / NamedMesh current-risk review (2026-06-06).*

## Wave1151 Current-Risk Tag Normalization

Wave1151 tag-only normalization also covers `0x00417870 CBuilding__VFuncSlot_02_RemoveFromWorldUpdateShadowAndForward` as a score21 current-risk row. It preserves the occupancy/static-shadow slot-2 evidence and adds Wave1151/current-risk tags only; no semantic mutation was made. Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260605-201419_post_wave1151_mixed_score21_current_risk_review_verified`. Runtime behavior, exact layouts, exact source-body identity, BEA patching behavior, gameplay outcomes, visual QA, and rebuild parity remain separate proof.
