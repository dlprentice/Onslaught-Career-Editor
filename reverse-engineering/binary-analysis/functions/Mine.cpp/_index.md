# Mine.cpp Functions

> Source File: Mine.cpp | Binary: BEA.exe
> Debug Path: 0x006309a4

> **Queue status (2026-05-26):** Ghidra export-contract closure **6113/6113** (Wave900: every function commented; clean-signature proxy; not evidence-grade semantics). Lines below that reference a "next raw commentless" row are **archival wave progress**, not open work.

## Overview

Mine/explosive implementation. CMine is a ground-based unit that handles explosive mine placement, orientation, and water depth checks. Inherits from CGroundUnit.

Wave1140 (`wave1140-motion-controller-current-risk-review`) re-read the motion-controller residual current-risk cluster including mine anchors `0x0049c3e0 CMCMine__Constructor` and `0x0049c440 CMCMine__VFunc_04_UpdateInterpolatedHeightOffset_0049c440`, plus `0x00497090 CMCHiveBoss__Constructor`, `0x00497140 CDestructableSegmentsMotionController__CacheNamedCollisionCylinders`, `0x00494fa0 SharedMotionController__VFunc_UpdateUnitAIIndexedEntryFlag`, `0x00494ff0 SharedMotionController__VFunc_CallUnitAIIndexedEntryVFunc10`, `0x0049c1d0 CMCMech__VFunc_05_WriteInterpolatedBoneFloat_0049c1d0`, `0x0049c5d0 CMCSentinel__Constructor`, and `0x0049f820 SharedGroundUnit__VFunc_09_InitGroundedMotionComponents_0049f820`. It covers `9 current-risk rows`; current focused accounting is `238/1179 = 20.19%`; current risk candidates: 6166; current focused candidates: 1178; live regenerated current focused candidates: 1178; remaining active focused work: 941; static debt `0 / 0 / 0`; static closure `6411/6411 = 100.00%`. This was a fresh Ghidra export, read-only review, no mutation. Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260605-142515_post_wave1140_motion_controller_current_risk_review_verified`; previous completed backup: `[maintainer-local-ghidra-backup-root]\BEA_20260605-134608_post_wave1139_battleengine_jetpart_current_risk_review_verified`. Runtime motion-controller behavior, exact layouts, and rebuild parity remain separate proof.

Wave800 gameplay object helpers corrected the adjacent helper formerly labeled `0x00449560 CMine__AssignVec3AndReturnThis` to owner-neutral `0x00449560 Vec3__AssignFromValuePointersAndReturnThis`. The body does not touch CMine fields; it copies three dereferenced 4-byte values into destination vector offsets `+0/+4/+8`, returns `this`, and ends with `RET 0xc`. Xrefs include `CMine__Init` at `0x004ba41e` plus one nearby unlabeled caller at `0x004494b8`. Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260524-070217_post_wave800_gameplay_object_helpers_verified`. Concrete Vec3 type recovery, exact source identity, runtime mine behavior, BEA patching, and rebuild parity remain deferred.

## Wave1069 GroundUnit VFunc Motion/Effects Re-Audit (2026-06-02)

Wave1069 (`groundunit-vfunc-motion-effects-review-wave1069`) re-read the CMCMine and CMine vfunc rows in this neighborhood with no mutation. The review keeps `0x0049c440 CMCMine__VFunc_04_UpdateInterpolatedHeightOffset_0049c440`, `0x004ba490 CMine__VFunc02_CleanupLinkedParticleAndForward`, and `0x004ba9d0 CMine__TryDestroyedResetAndDispatchVFunc1D4` bounded by fresh vtable/xref/decompile evidence. It also documents the adjacent cross-owner rows `0x0049c1d0 CMCMech__VFunc_05_WriteInterpolatedBoneFloat_0049c1d0`, `0x0049f820 SharedGroundUnit__VFunc_09_InitGroundedMotionComponents_0049f820`, `0x0049fc10 SharedGroundUnit__VFunc_66_UpdateVerticalDriftPickupAndEffects_0049fc10`, `0x0049fdb0 SharedGroundUnit__VFunc_71_SpawnGenericMeshBreakEffects_0049fdb0`, and `0x004d3630 CPod__VFunc_66_UpdateMotionAndAccumulateScalar` so the probe can prove the full read-only cluster in one place. Queue closure remains `6246/6246 = 100.00%`; Wave911 focused progress remains `812/1408 = 57.67%`; expanded static surface progress advances to `1266/1560 = 81.15%`; top-500 coverage remains `500/500 = 100.00%`. Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260602-013945_post_wave1069_groundunit_vfunc_motion_effects_review_verified`. Runtime mine placement/destruction/effect cleanup behavior, runtime grounded-unit/pod behavior, exact layouts, exact source identity, BEA patching, gameplay outcomes, and rebuild parity remain separate proof. Probe token anchor: Wave1069; groundunit-vfunc-motion-effects-review-wave1069; 0x0049c1d0 CMCMech__VFunc_05_WriteInterpolatedBoneFloat_0049c1d0; 0x0049c440 CMCMine__VFunc_04_UpdateInterpolatedHeightOffset_0049c440; 0x0049f820 SharedGroundUnit__VFunc_09_InitGroundedMotionComponents_0049f820; 0x0049fc10 SharedGroundUnit__VFunc_66_UpdateVerticalDriftPickupAndEffects_0049fc10; 0x0049fdb0 SharedGroundUnit__VFunc_71_SpawnGenericMeshBreakEffects_0049fdb0; 0x004ba490 CMine__VFunc02_CleanupLinkedParticleAndForward; 0x004ba9d0 CMine__TryDestroyedResetAndDispatchVFunc1D4; 0x004d3630 CPod__VFunc_66_UpdateMotionAndAccumulateScalar; 812/1408 = 57.67%; 1266/1560 = 81.15%; 500/500 = 100.00%; 6246/6246 = 100.00%; [maintainer-local-ghidra-backup-root]\BEA_20260602-013945_post_wave1069_groundunit_vfunc_motion_effects_review_verified; read-only review.

## Wave1217 Lifecycle Cleanup Tail Current-Risk Review

Wave1217 (`wave1217-lifecycle-cleanup-tail-current-risk-review`) re-read and comment/tag-normalized the CMine lifecycle/effect cleanup tail rows `CMine__VFunc02_CleanupLinkedParticleAndForward` and `CMine__TryDestroyedResetAndDispatchVFunc1D4`. The review preserved the existing cleanup-link and destroyed-reset dispatch contracts, with no rename, signature, function-boundary, or executable-byte change. Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260607-110625_post_wave1217_lifecycle_cleanup_tail_current_risk_review_verified`. Runtime mine destruction/effect behavior, exact layouts, exact source identity, BEA patching behavior, rebuild parity, and no-noticeable-difference parity remain separate proof.

## Functions

| Address | Name | Purpose | Size |
|---------|------|---------|------|
| 0x004ba150 | CMine__Init | Initializes mine orientation/state, samples heightfield normal, attaches `CMCMine` controller, and clears linked effect slots | ~0x333 bytes |
| 0x00449560 | Vec3__AssignFromValuePointersAndReturnThis | Wave800 owner-neutral Vec3 assignment helper reached by `CMine__Init`; previously over-specific CMine label | ~0x1d bytes |
| 0x004ba490 | CMine__VFunc02_CleanupLinkedParticleAndForward | Cleans linked `+0x264` node and forwards to base slot-2 cleanup | ~0x3b bytes |
| 0x004ba9d0 | CMine__TryDestroyedResetAndDispatchVFunc1D4 | Destroy/reset wrapper that dispatches vfunc `+0x1d4` after `CGroundUnit__MarkDestroyedAndResetState` succeeds | ~0x1f bytes |

## Wave759 Mine.cpp Unwind Continuation

Wave759 static read-back (`unwind-continuation-wave759`, `wave759-readback-verified`) hardened the adjacent Mine.cpp compiler-generated SEH unwind cleanup callbacks as `void __cdecl Unwind@...(void)` with no renames, no function-boundary changes, and no executable-byte changes. Exact anchors include `0x005d3c10 Unwind@005d3c10` and `0x005d3c30 Unwind@005d3c30`. Evidence ties the rows to DATA scope-table xrefs, Mine.cpp debug path `0x006309a4`, and `OID__FreeObject_Callback`. Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260523-130827_post_wave759_unwind_continuation_verified`. Exact parent source-body identity, runtime exception behavior, runtime cleanup behavior, BEA patching, and rebuild parity remain deferred.

## Exception Handlers

| Address | Name | Line | Purpose |
|---------|------|------|---------|
| 0x005d3c10 | Unwind@005d3c10 | 0x1b | Wave759 cleanup; DATA xref `0x0061c89c`; calls `OID__FreeObject_Callback` on `*(EBP-0x68)` with allocation/type value `0x1f` |
| 0x005d3c30 | Unwind@005d3c30 | 0x10 | Wave759 cleanup; DATA xref `0x0061c8c4`; calls `OID__FreeObject_Callback` on `*(EBP-0x50)` with allocation/type value `0x58` |

## Key Observations

- **Inherits CGroundUnit** - Calls CGroundUnit__Init
- **3D orientation** - Complex sin/cos calculations for placement
- **Water depth check** - Compares against DAT_006fbdfc threshold
- **Vector math** - Normalizes forward/up vectors
- **State flags** - Sets at offsets 0x70, 0x260, 0x264

## Wave456 Mine / Motion Controller Evidence

Wave456 is static retail Ghidra evidence only. It saved comments, signatures, tags, and corrected names for the `CMine` queue head plus base `CMotionController` helpers reached by `CMCMine`, `CMCSentinel`, and `CMCMech`.

| Address | Name | Evidence |
|---------|------|----------|
| 0x004ba150 | CMine__Init | Marks `init+0x70` with `0x20`, derives placement orientation from heading `init+0x44` and sampled heightfield normal, calls `CGroundUnit__Init`, allocates a `CMCMine` controller into `this+0x70`, clears `this+0x260/+0x264`, and sets the `this+0x258` threshold flag. |
| 0x004ba490 | CMine__VFunc02_CleanupLinkedParticleAndForward | Checks `this+0x264`, clears the linked particle/effect owner-link cell through `ParticleEffectLink__SetHandleStateAndClear`, removes the node from the particle manager/global list, frees it, and forwards to `VFuncSlot_02_004f95d0`. |
| 0x004ba9d0 | CMine__TryDestroyedResetAndDispatchVFunc1D4 | Vtable data xref `0x005e1c4c`; calls `CGroundUnit__MarkDestroyedAndResetState`, returns `0` on failure, otherwise dispatches vfunc `+0x1d4` and returns `1`. |
| 0x004bae10 | CMotionController__scalar_deleting_dtor | Scalar-deleting destructor wrapper for the base motion-controller vtable; calls `CMotionController__dtor_base`, tests delete flag bit 0, optionally frees `this`, and returns `this`. |
| 0x004bae30 | CMotionController__ctor_base | Base constructor helper; writes base vtable `0x005dc778` and clears `+0x04/+0x08` with zeroed `ECX`. |
| 0x004bae50 | CMotionController__dtor_base | Restores base vtable `0x005dc778` and tails `CMonitor__Shutdown`. |

Runtime mine placement/water behavior, exact virtual slot names, concrete `CMine`/motion-controller layouts, and lifecycle ownership remain unproven.

## Wave434 Motion Controller Evidence

`CMCMine` is the mine motion-controller class referenced from `CMine__Init`; it is adjacent to the gameplay `CMine` unit but uses its own vtable at `0x005dc3f4`. Wave434 is static retail Ghidra evidence only.

Wave1021 (`motion-controller-constructor-review-wave1021`) re-read `0x0049c3e0 CMCMine__Constructor` with no mutation. Fresh xrefs still show `CMine__Init` callers at `0x004ba3d0` and `0x004ba3dc`; instruction evidence calls `CMotionController__ctor_base`, installs vtable `0x005dc3f4`, stores the owner mine pointer at `+0x08`, and returns with `RET 0x4`. Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260531-222637_post_wave1021_motion_controller_constructor_review_verified`. Runtime mine motion behavior, exact source-body identity, concrete layouts, BEA patching, and rebuild parity remain separate proof.

| Address | Name | Evidence |
|---------|------|----------|
| 0x0049c3e0 | CMCMine__Constructor | Installs vtable `0x005dc3f4`, stores owner at `+0x08`, and returns with `RET 0x4`. |
| 0x0049c400 | CMCMine__ScalarDeletingDestructor | Calls `CMCMine__Destructor`, conditionally frees `this`, and returns with `RET 0x4`. |
| 0x0049c420 | CMCMine__Destructor | Restores the CMCMine vtable, clears owner `+0x08`, seeds cached `+0x0c`, and tails the base motion-controller destructor. |
| 0x0049c440 | CMCMine__VFunc_04_UpdateInterpolatedHeightOffset_0049c440 | Vtable slot 4; adjusts an output transform height from owner `+0x250/+0x254` and refreshes cached `+0x0c`. |
| 0x0049c4b0 | CMCMine__VFunc_08_CheckCachedHeightState_0049c4b0 | Recovered slot-8 boundary; compares cached `+0x0c` against owner `+0x250` and reports changed state. |

## Class Hierarchy

```
CUnit
  └── CGroundUnit
        └── CMine
```

## Related Files

- GroundUnit.cpp - CGroundUnit parent class
- Unit.cpp - CUnit base class

---
*Discovered via Phase 1 xref analysis (Dec 2025)*
