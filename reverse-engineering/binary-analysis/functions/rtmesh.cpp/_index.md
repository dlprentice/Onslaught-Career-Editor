# rtmesh.cpp Function Mappings

<!-- ghidra-full-reaudit-20260713:start -->
> **2026-07-13 semantic revalidation:** `0x004dd0c0` comment correction. Older conflicting text below is superseded for these rows. Use the [closeout](../../ghidra-full-reaudit-closeout-2026-07-13.md); exact records are in `reverse-engineering/binary-analysis/ghidra-full-reaudit-corrections-2026-07-13.json` and `reverse-engineering/binary-analysis/ghidra-targeted-revalidation-corrections-2026-07-13.json`.
<!-- ghidra-full-reaudit-20260713:end -->

> Functions from rtmesh.cpp mapped to BEA.exe binary
> Debug Path: `[maintainer-local-source-export-root]\rtmesh.cpp` (0x00631f28)
> RTTI: `.?AVCRTMesh@@` (0x00631db8)

> **Queue status (2026-05-26):** Ghidra export-contract closure **6113/6113** (Wave900: every function commented; clean-signature proxy; not evidence-grade semantics). Lines below that reference a "next raw commentless" row are **archival wave progress**, not open work.

## Overview
- **Functions Mapped:** 10
- **Status:** Phase 1 xref analysis plus Wave496/Wave497 signature/comment hardening, re-read by Wave1068
- **Classes:** CRTMesh, adjacent CRTBuilding render-object vtable slice, shared CRTMesh/CRTTree resource getter
- **Purpose:** Real-Time Mesh rendering system with LOD, imposters, effects, render-object cleanup, and quality controls

Wave1068 (`rtbuilding-rtmesh-lifecycle-review-wave1068`) re-read the existing Wave496 CRTBuilding/CRTMesh lifecycle, pose-data, effect-cleanup, and mesh-LOD quality cluster with no mutation. Fresh primary/context exports verified `10/10/14/788/10` and `23/23/60/2661/23` rows, including seven intentional no-function context rows from raw CRTBuilding/CRTMesh vtable pointers; vtable export verified `48` rows from `0x005de9c0` and `0x005deb1c`. Primary anchors are `0x004db850 CRTBuilding__Destructor`, `0x004db8d0 CRTBuilding__ScalarDeletingDestructor`, `0x004dba40 CRTBuilding__VFuncSlot10_PickRandomLinkedEntry`, `0x004dc370 CRTMesh__Init`, `0x004dc950 CRTMesh__Destructor`, `0x004dcb00 CRTMesh__FreePoseData`, `0x004dcb70 CRTMesh__ScalarDeletingDestructor`, `0x004dd0c0 CRTMesh__CleanupAllEffects`, `0x004dd6b0 CRTMesh__SetQualityLevel`, and `0x004dd770 CRTMesh__GetQualityLevel`. Queue closure remains `6246/6246 = 100.00%`; Wave911 focused progress remains `812/1408 = 57.67%`; expanded static surface progress advances to `1258/1560 = 80.64%`; top-500 coverage remains `500/500 = 100.00%`. Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260602-010648_post_wave1068_rtbuilding_rtmesh_lifecycle_review_verified`, `19` files, `174721927` bytes, `DiffCount=0`, `HashDiffCount=0`. Runtime RTMesh/building render behavior, runtime mesh LOD/imposter/particle-effect cleanup behavior, exact `CRTBuilding`/`CRTMesh`/`CRenderThing`/meshpose/imposter/effect/list layouts, exact source identity for absent `rtmesh.cpp`, BEA patching, gameplay outcomes, and rebuild parity remain separate proof. Probe token anchor: Wave1068; rtbuilding-rtmesh-lifecycle-review-wave1068; 0x004db850 CRTBuilding__Destructor; 0x004db8d0 CRTBuilding__ScalarDeletingDestructor; 0x004dba40 CRTBuilding__VFuncSlot10_PickRandomLinkedEntry; 0x004dc370 CRTMesh__Init; 0x004dc950 CRTMesh__Destructor; 0x004dd0c0 CRTMesh__CleanupAllEffects; 0x004dd6b0 CRTMesh__SetQualityLevel; 0x004dd770 CRTMesh__GetQualityLevel; 812/1408 = 57.67%; 1258/1560 = 80.64%; 500/500 = 100.00%; 6246/6246 = 100.00%; [maintainer-local-ghidra-backup-root]\BEA_20260602-010648_post_wave1068_rtbuilding_rtmesh_lifecycle_review_verified; read-only review.

Wave1217 (`wave1217-lifecycle-cleanup-tail-current-risk-review`) re-read and comment/tag-normalized `CRTBuilding__ScalarDeletingDestructor` as part of the lifecycle cleanup tail. Fresh evidence preserves the CRTBuilding scalar-deleting wrapper contract and its relationship to `CRTBuilding__Destructor`, with no rename, signature, function-boundary, or executable-byte change. Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260607-110625_post_wave1217_lifecycle_cleanup_tail_current_risk_review_verified`. Runtime building/RTMesh cleanup behavior, exact layouts, exact source identity, BEA patching behavior, rebuild parity, and no-noticeable-difference parity remain separate proof.

Wave1046 (`renderthing-crttree-review-wave1046`) re-read the shared CRTMesh/CRTTree resource getter and adjacent RenderThing helpers with no mutation. Fresh evidence reconfirmed `0x004de060 SharedVFunc__ReturnResourceField150_004de060` through CRTMesh vtable `0x005deb1c` and CRTTree vtable `0x005deb9c`, plus shared `CRenderThing` helper refs through `0x005dea38` and `0x005deaac`. The review also reconfirmed `0x004dd960 CRTTree__VFuncSlot02_BuildRenderOutputs`, `DAT_0083cd58`, `0x0083ccd8`, and `0x004b6260 CSphere__RenderAnimatedRecursive` context. Queue closure remains `6246/6246 = 100.00%`; expanded static surface progress is `993/1509 = 65.81%`. Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260601-120449_post_wave1046_renderthing_crttree_review_verified`. Runtime mesh/tree render behavior, exact resource/output-record layouts, exact source virtual names, BEA patching, gameplay outcomes, and rebuild parity remain separate proof.

## Function List

| Address | Name | Status | Purpose |
|---------|------|--------|---------|
| 0x004dc370 | CRTMesh__Init | NAMED | Constructor - initializes mesh, pose data, imposters, and console vars |
| 0x004dc950 | CRTMesh__Destructor | NAMED | Destructor - frees all allocated resources and unlinks from list |
| 0x004dcb00 | CRTMesh__FreePoseData | NAMED | Helper to free pose data arrays |
| 0x004dcb70 | CRTMesh__ScalarDeletingDestructor | NAMED | MSVC scalar deleting destructor |
| 0x004dd0c0 | CRTMesh__CleanupAllEffects | NAMED | Static - iterates all RTMesh instances and cleans up effects |
| 0x004dd6b0 | CRTMesh__SetQualityLevel | NAMED | Static - sets LOD/quality parameters (0=low, 1=med, 2=high) |
| 0x004dd770 | CRTMesh__GetQualityLevel | NAMED | Static - returns current quality level based on threshold |

## Adjacent CRTBuilding Targets

Wave496 also hardened the adjacent CRTBuilding vtable slice that forwards into CRTMesh cleanup:

| Address | Name | Status | Purpose |
|---------|------|--------|---------|
| 0x004db850 | CRTBuilding__Destructor | NAMED | Resets CRTBuilding vtable, decrements mesh/resource refcount, clears field `+0x54`, and chains to `CRTMesh__Destructor` |
| 0x004db8d0 | CRTBuilding__ScalarDeletingDestructor | NAMED | Vtable slot 0 scalar-deleting destructor wrapper; frees `this` when delete flag bit 0 is set |
| 0x004dba40 | CRTBuilding__VFuncSlot10_PickRandomLinkedEntry | NAMED | Vtable slot 10 helper; selects a random linked entry from list/count fields at `+0x54/+0x58` |

## Console Variables (registered in Init)

| Variable | Description | Type | Global |
|----------|-------------|------|--------|
| cg_forceobjectimposters | Force use of object imposters | bool | 0x0083cd58 |
| cg_imposterfadestart | Distance at which imposters start | float | 0x00631e94 |
| cg_imposterfadeend | Distance at which imposters stop | float | 0x00631e98 |
| cg_meshlodbias | Mesh LOD bias (use <1 to increase) | float | 0x00631e88 |
| cg_meshlodmedthreshold | Mesh LOD high<->medium threshold | float | 0x00631e8c |
| cg_meshlodlowthreshold | Mesh LOD medium<->low threshold | float | 0x00631e90 |
| cg_meshlodignorezoom | Ignore zoom factor for LOD | bool | 0x0083cd5a |
| cg_snowlayerenable | Enable/disable snow layer | bool | 0x0083cd5b |
| cg_meshtexturelodbias | Mesh texture LOD bias | float | 0x00631e9c |
| cg_meshsurfacelodbias | Mesh surface LOD bias | float | 0x00631ea0 |

## Class Layout (partial)

```
CRTMesh (size ~0x4C+ bytes)
+0x00: vtable*
+0x04: float (from mesh +0x168)
+0x08: CAnimation* (animation pointer)
+0x0c: CMeshPose* (pose data)
+0x14: CMesh* (mesh pointer)
+0x18: CImposter* (imposter for distant rendering)
+0x1c: byte* (imposter state)
+0x20: unknown (from mesh +0x164)
+0x24: unknown (from param +0x404)
+0x28: int effectCount (number of effects with '_' prefix)
+0x2c: byte* effectFlags
+0x30: int* effectIndices
+0x34: int* effectTypes
+0x38: int* effectBoneIndices
+0x3c: int* effectStartFrames
+0x40: int* effectDurations
+0x44: unknown
+0x48: CRTMesh* next (linked list)
```

## Vtable (at 0x005deb1c)

| Offset | Address | Function |
|--------|---------|----------|
| +0x00 | 0x004dcb70 | CRTMesh__ScalarDeletingDestructor |
| +0x04 | 0x004dc370 | CRTMesh__Init |
| +0x08 | 0x004dcba0 | (not analyzed) |
| +0x0c | 0x004dcea0 | (not analyzed) |
| +0x10 | 0x004de060 | SharedVFunc__ReturnResourceField150_004de060 (Wave497 shared CRTMesh/CRTTree resource getter) |
| +0x14 | 0x004db8a0 | (not analyzed) |
| +0x18 | 0x004dcaf0 | (not analyzed) |
| +0x1c | 0x004dd160 | (not analyzed) |
| +0x20 | 0x004dd400 | (not analyzed) |
| +0x24 | 0x004de070 | SharedVFunc__ReturnField14_004de070 (Wave414 shared getter boundary) |
| +0x28 | 0x00405930 | (inherited/shared) |
| +0x2c | 0x004dcb90 | (not analyzed) |

## CRTBuilding Vtable Slice (at 0x005de9c0)

| Offset | Address | Function |
|--------|---------|----------|
| +0x00 | 0x004db8d0 | CRTBuilding__ScalarDeletingDestructor |
| +0x28 | 0x004dba40 | CRTBuilding__VFuncSlot10_PickRandomLinkedEntry |

## Key Observations

1. **Imposter System**: RTMesh uses imposters (billboard sprites) for distant objects to reduce polygon count. Console vars control fade distances.

2. **LOD System**: Three-tier LOD system (low/medium/high) with configurable thresholds and bias values.

3. **Effect System**: Effects are named with '_' prefix in bone names. The system tracks effect indices, types, bone associations, start frames, and durations.

4. **Linked List**: All CRTMesh instances are maintained in a global linked list (head at DAT_0083cd5c, tail at DAT_0083cd60) for batch operations like cleanup.

5. **Memory Allocation**: Uses game's heap allocator (OID__AllocObject) with allocation tags 0x7d (rtmesh) and 0x3b (effects). Also allocates from meshpose.h structures. Wave765 static read-back (`unwind-continuation-wave765`, `wave765-readback-verified`) tied `0x005d4a50 Unwind@005d4a50` to a meshpose.h unwind allocation cleanup: DATA xref `0x0061d2cc`, debug path `0x00631ed8`, line token `0x21`, allocation/type value `0x7d`, and verified backup `[maintainer-local-ghidra-backup-root]\BEA_20260523-155528_post_wave765_unwind_continuation_verified`. Exact meshpose layout, parent source-body identity, runtime cleanup behavior, BEA patching, and rebuild parity remain deferred.

6. **Snow Layer**: Has a dedicated enable/disable for snow rendering on meshes.

7. **Shared getter slots**: Wave497 created `0x004de060` as `SharedVFunc__ReturnResourceField150_004de060`, a compact `*(this+0x14)+0x150` getter referenced by CRTMesh vtable `0x005deb1c` and CRTTree vtable `0x005deb9c`. Wave414 created `0x004de070` as `SharedVFunc__ReturnField14_004de070`, a compact `+0x14` getter shared by ImageLoader, CTGALoader, CRTMesh, and other vtables. These identify vtable target shapes, not exact CRTMesh slot semantics.

## Wave496 CRTBuilding / CRTMesh Hardening

Fresh metadata, decompile, xref, instruction, tag, and vtable-slot read-back on 2026-05-17 hardened ten queue-head CRTBuilding/CRTMesh targets. `ApplyRTBuildingRTMeshWave496.java` dry/apply/verify-dry reported clean read-back, and `tools/ghidra_rtbuilding_rtmesh_wave496_probe.py --check` passed.

Wave1068 re-read these same ten rows on 2026-06-02 with no mutation, preserving the Wave496 names/signatures/comments/tags and adding post-100 re-audit evidence. Fresh read-only exports verified `10` metadata rows, `10` tag rows, `14` xref rows, `788` instruction rows, `10` decompile rows, and `48` vtable rows from `0x005de9c0` and `0x005deb1c`. Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260602-010648_post_wave1068_rtbuilding_rtmesh_lifecycle_review_verified`.

| Address | Saved signature | Evidence |
| --- | --- | --- |
| `0x004db850` | `void __fastcall CRTBuilding__Destructor(void * this)` | Resets vtable `0x005de9c0`, decrements the referenced mesh/resource counter at `this+0x54 -> +0x170`, clears `this+0x54`, and chains into `CRTMesh__Destructor`. |
| `0x004db8d0` | `void * __thiscall CRTBuilding__ScalarDeletingDestructor(void * this, byte flags)` | CRTBuilding vtable slot 0 wrapper that calls the destructor, frees on `flags & 1`, and returns `this`. |
| `0x004dba40` | `void * __fastcall CRTBuilding__VFuncSlot10_PickRandomLinkedEntry(void * this)` | CRTBuilding vtable slot 10 helper; returns null for zero count, otherwise walks linked entries rooted at `this+0x54` after `rand() % *(this+0x58)`. |
| `0x004dc370` | `void __thiscall CRTMesh__Init(void * this, void * init)` | CRTMesh vtable slot 1 init; initializes base render thing state, registers RTMesh console variables, resolves/falls back to a CMesh, allocates meshpose/effect arrays, and optionally creates an imposter. |
| `0x004dc950` | `void __fastcall CRTMesh__Destructor(void * this)` | Unlinks from global RTMesh list globals `DAT_0083cd5c/DAT_0083cd60`, clears particle effects, frees pose/imposter/effect resources, decrements mesh refcount, and restores base vtable before child cleanup. |
| `0x004dcb00` | `void __fastcall CRTMesh__FreePoseData(void * poseData)` | Frees and nulls the four pose-data pointer fields at `+0x00/+0x04/+0x08/+0x0c`. |
| `0x004dcb70` | `void * __thiscall CRTMesh__ScalarDeletingDestructor(void * this, byte flags)` | CRTMesh vtable slot 0 wrapper that calls the destructor, frees on `flags & 1`, and returns `this`. |
| `0x004dd0c0` | `void __cdecl CRTMesh__CleanupAllEffects(void)` | Static helper walks the global RTMesh list and clears/removes active effect handles from each mesh. |
| `0x004dd6b0` | `void __cdecl CRTMesh__SetQualityLevel(int qualityLevel)` | Static quality setter writes low/medium/high distance, LOD-bias, scale, and CVar values for quality levels `0/1/2`. |
| `0x004dd770` | `int __cdecl CRTMesh__GetQualityLevel(void)` | Static getter maps `g_MeshQualityDistance` thresholds back to quality levels `0/1/2`; callers include PauseMenu/CPauseMenu quality UI paths and the CTreeDetail setter boundary. |

This is saved static Ghidra evidence only. Exact source virtual names, concrete `CRTBuilding`/`CRTMesh`/meshpose/imposter/effect/list layouts, runtime render behavior, BEA launch behavior, game patching, and rebuild parity remain open.

## Wave497 Shared CRTMesh / CRTTree Getter

Wave497 recovered `0x004de060` as `SharedVFunc__ReturnResourceField150_004de060` with signature `void * __fastcall SharedVFunc__ReturnResourceField150_004de060(void * this)`. The body loads the resource pointer from `this+0x14` and returns the field at `resource+0x150`; CRTMesh vtable slot `+0x10` and CRTTree vtable slot `+0x10` both reference it. This is static vtable/decompile evidence only; exact field type, owner contract, runtime behavior, and rebuild parity remain open.


## Related Strings

| Address | String |
|---------|--------|
| 0x00631db8 | `.?AVCRTMesh@@` (RTTI type info) |
| 0x00631ea3 | `Warning : not enough thing heap for RTMesh effects` |
| 0x00631ef8 | `Warning : not enough thing heap for RTMesh` |
| 0x00631f28 | `[maintainer-local-source-export-root]\rtmesh.cpp` (debug path) |
| 0x00632a58 | `Thing at 0x%x has no RTMesh when trying to statically shadow!` |

## Related Files
- meshpose.h - Referenced for pose data allocation
- CMesh - Base mesh system (`CMesh__FindOrCreate`)
- CImposter - Imposter/billboard system (`CImposter__FindOrCreate`)

## Parent
- [../README.md](../README.md)

---
*Discovered via Phase 1 xref analysis (Dec 2025); Wave496 signature/comment hardening and Wave497 shared getter recovery added 2026-05-17; Wave1068 post-100 read-only re-audit added 2026-06-02.*

## Wave1151 Current-Risk Tag Normalization

Wave1151 tag-only normalization also covers `0x004dba40 CRTBuilding__VFuncSlot10_PickRandomLinkedEntry` as a score21 current-risk row. It preserves the RTBuilding random linked-entry selector evidence and adds Wave1151/current-risk tags only. Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260605-201419_post_wave1151_mixed_score21_current_risk_review_verified`. Runtime behavior, exact layouts, exact source-body identity, BEA patching behavior, gameplay outcomes, visual QA, and rebuild parity remain separate proof.
