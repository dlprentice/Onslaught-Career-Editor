# Mech.cpp Functions

<!-- ghidra-full-reaudit-20260713:start -->
> **2026-07-13 semantic revalidation:** `0x0049faa0` comment correction. Older conflicting text below is superseded for these rows. Use the [closeout](../../ghidra-full-reaudit-closeout-2026-07-13.md); exact records are in `reverse-engineering/binary-analysis/ghidra-full-reaudit-corrections-2026-07-13.json` and `reverse-engineering/binary-analysis/ghidra-targeted-revalidation-corrections-2026-07-13.json`.
<!-- ghidra-full-reaudit-20260713:end -->

> Source File: Mech.cpp | Binary: BEA.exe

## Overview

> **Queue status (2026-05-26):** Ghidra export-contract closure **6113/6113** (Wave900: every function commented; clean-signature proxy; not evidence-grade semantics). Lines below that reference a "next raw commentless" row are **archival wave progress**, not open work.

Player mech specialization extending `CUnit` / `CGroundUnit` initialization. Wave436 corrected the adjacent retail `0x0049f820` through `0x0049faa0` cluster: one shared grounded-unit vtable slot body and three `CMech` component-initialization slots. Wave437 then hardened the constructor/destructor/update helpers for the `CMechAI` and `CMechGuide` objects those slots allocate. Wave756 added saved static read-back comments/tags/signatures for the adjacent Mech.cpp unwind cleanup callbacks. Wave810 added saved static read-back comment/tags for the adjacent recursive `CMCMech` bone hierarchy update helper. Wave816 added the bounded `CMCMech__BuildInterpolatedPoseAndAnchor` signature/comment evidence tied to mesh-part interpolation. Current evidence is saved retail Ghidra metadata, vtable slots, allocation sizes, strings, and local control flow; runtime cockpit/targeting/leg-motion/pose behavior remains unproven.

Wave1140 (`wave1140-motion-controller-current-risk-review`) re-read the motion-controller residual current-risk cluster including mech/shared-ground anchors `0x0049c1d0 CMCMech__VFunc_05_WriteInterpolatedBoneFloat_0049c1d0` and `0x0049f820 SharedGroundUnit__VFunc_09_InitGroundedMotionComponents_0049f820`, plus `0x00497090 CMCHiveBoss__Constructor`, `0x00497140 CDestructableSegmentsMotionController__CacheNamedCollisionCylinders`, `0x00494fa0 SharedMotionController__VFunc_UpdateUnitAIIndexedEntryFlag`, `0x00494ff0 SharedMotionController__VFunc_CallUnitAIIndexedEntryVFunc10`, `0x0049c3e0 CMCMine__Constructor`, `0x0049c440 CMCMine__VFunc_04_UpdateInterpolatedHeightOffset_0049c440`, and `0x0049c5d0 CMCSentinel__Constructor`. It covers `9 current-risk rows`; current focused accounting is `238/1179 = 20.19%`; current risk candidates: 6166; current focused candidates: 1178; live regenerated current focused candidates: 1178; remaining active focused work: 941; static debt `0 / 0 / 0`; static closure `6411/6411 = 100.00%`. This was a fresh Ghidra export, read-only review, no mutation. Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260605-142515_post_wave1140_motion_controller_current_risk_review_verified`; previous completed backup: `[maintainer-local-ghidra-backup-root]\BEA_20260605-134608_post_wave1139_battleengine_jetpart_current_risk_review_verified`. Runtime motion-controller behavior, exact layouts, and rebuild parity remain separate proof.

## Wave1069 GroundUnit VFunc Motion/Effects Re-Audit (2026-06-02)

Wave1069 (`groundunit-vfunc-motion-effects-review-wave1069`) re-read the CMCMech and shared GroundUnit vfunc motion/effects rows in this neighborhood with no mutation. The review keeps `0x0049c1d0 CMCMech__VFunc_05_WriteInterpolatedBoneFloat_0049c1d0`, `0x0049f820 SharedGroundUnit__VFunc_09_InitGroundedMotionComponents_0049f820`, `0x0049fc10 SharedGroundUnit__VFunc_66_UpdateVerticalDriftPickupAndEffects_0049fc10`, and `0x0049fdb0 SharedGroundUnit__VFunc_71_SpawnGenericMeshBreakEffects_0049fdb0` bounded by vtable/xref/decompile evidence. It also documents the adjacent cross-owner rows `0x0049c440 CMCMine__VFunc_04_UpdateInterpolatedHeightOffset_0049c440`, `0x004ba490 CMine__VFunc02_CleanupLinkedParticleAndForward`, `0x004ba9d0 CMine__TryDestroyedResetAndDispatchVFunc1D4`, and `0x004d3630 CPod__VFunc_66_UpdateMotionAndAccumulateScalar` so the probe can prove the full read-only cluster in one place. Queue closure remains `6246/6246 = 100.00%`; Wave911 focused progress remains `812/1408 = 57.67%`; expanded static surface progress advances to `1266/1560 = 81.15%`; top-500 coverage remains `500/500 = 100.00%`. Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260602-013945_post_wave1069_groundunit_vfunc_motion_effects_review_verified`. Runtime grounded-unit, pickup, mesh-break, particle/effect cleanup, motion behavior, exact layouts, exact source identity, BEA patching, gameplay outcomes, and rebuild parity remain separate proof. Probe token anchor: Wave1069; groundunit-vfunc-motion-effects-review-wave1069; 0x0049c1d0 CMCMech__VFunc_05_WriteInterpolatedBoneFloat_0049c1d0; 0x0049c440 CMCMine__VFunc_04_UpdateInterpolatedHeightOffset_0049c440; 0x0049f820 SharedGroundUnit__VFunc_09_InitGroundedMotionComponents_0049f820; 0x0049fc10 SharedGroundUnit__VFunc_66_UpdateVerticalDriftPickupAndEffects_0049fc10; 0x0049fdb0 SharedGroundUnit__VFunc_71_SpawnGenericMeshBreakEffects_0049fdb0; 0x004ba490 CMine__VFunc02_CleanupLinkedParticleAndForward; 0x004ba9d0 CMine__TryDestroyedResetAndDispatchVFunc1D4; 0x004d3630 CPod__VFunc_66_UpdateMotionAndAccumulateScalar; 812/1408 = 57.67%; 1266/1560 = 81.15%; 500/500 = 100.00%; 6246/6246 = 100.00%; [maintainer-local-ghidra-backup-root]\BEA_20260602-013945_post_wave1069_groundunit_vfunc_motion_effects_review_verified; read-only review.

## Wave816 Mesh Animation Tail (2026-05-24)

Wave816 mesh animation tail (`mesh-animation-tail-wave816`, `wave816-readback-verified`) saved comments/tags for `0x004b0cd0 CMesh__SelectModeSpecificPtr`, `0x004b0d00 CMeshPart__InterpolateSegmentTransform`, and `0x004b0fb0 CMCMech__BuildInterpolatedPoseAndAnchor`. The pass corrected two stale locked no-argument signatures to observed `__thiscall` stack-cleanup forms, made no renames, no function-boundary changes, and no executable-byte changes.

Static read-back evidence:

| Address | Evidence |
| --- | --- |
| `0x004b0cd0 CMesh__SelectModeSpecificPtr` | Mesh-side selector included as the tranche head; reads mode field `+0x8c` and returns `this`, alternate pointer `+0x124`, or null depending on mode. |
| `0x004b0d00 CMeshPart__InterpolateSegmentTransform` | MeshPart interpolation companion called by the CMCMech pose builder; sole direct callsite `0x004b17fc` proves five stack arguments and callee `RET 0x14`. |
| `0x004b0fb0 CMCMech__BuildInterpolatedPoseAndAnchor` | Representative callsites push nine stack dwords and the body exits with `RET 0x24`. Evidence ties it to global pose cache slots `DAT_00704cf0`/`DAT_00704d20`, anchors `DAT_00704cd0`/`DAT_00704ce0`, parent part `+0x98`, cache fields `+0x104`/`+0x108`/`+0x118`/`+0x11c`/`+0x120`, `CMeshPart__InterpolateSegmentTransform`, and optional pose-controller vtable callbacks `+0x70`/`+0x4`/`+0xc`/`+0x10`. |

Queue telemetry after Wave816 is 6098 total, 5602 commented, 496 commentless, 0 exact-undefined signatures, 0 `param_N`, comment-backed proxy `5602/6098 = 91.87%`, strict proxy `5602/6098 = 91.87%`, and next raw commentless row `0x004b4ba0 CMeshPart__PopulatePoseCacheRecursive`. Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260524-151844_post_wave816_mesh_animation_tail_verified`. Exact concrete CMesh/CMeshPart/CMCMech/controller layouts, exact source-body identity, runtime animation/render/collision behavior, BEA patching, and rebuild parity remain deferred.

## Wave810 CMCMech Bone Recursive (2026-05-24)

Wave810 CMCMech bone recursive static read-back (`cmcmech-bone-recursive-wave810`, `wave810-readback-verified`) saved a comment/tag-only correction for `0x0049bd50 CMCMech__UpdateBoneHierarchyRecursive`. The saved signature intentionally remains `void CMCMech__UpdateBoneHierarchyRecursive(void)`: instruction evidence proves a `RET 0x54` cleaned stack contract, but the by-value `FVector`/`FMatrix` stack payload should not be forced into Ghidra's ordinary parameter model until the shared aggregate types are recovered. Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260524-123030_post_wave810_cmcmech_bone_recursive_verified`. Queue after Wave810 is `5585/6098 = 91.59%` strict-clean with next raw commentless row `0x0049c2d0 CMeshPart__HasAnimationToken_623074`. Exact by-value `FVector`/`FMatrix` parameter type contract, concrete `CMCMech`/`CMeshPart` layouts, exact source-body identity, runtime leg/bone animation behavior, BEA patching, and rebuild parity remain deferred.

| Address | Static read-back evidence |
| --- | --- |
| `0x0049bd50 CMCMech__UpdateBoneHierarchyRecursive` | Calls `CMCMech__UpdateBone`, reads child count at `mesh_part+0x90`, descends child table `mesh_part+0x94`, recursively calls itself at `0x0049bddf`, and exits with `RET 0x54`. |
| `0x00498ac6` | `CMCMech__Reset` callsite for one reset path; prepares a `0x10` vector payload and `0x30` matrix payload copied with `MOVSD.REP ECX=0xc`. |
| `0x00498bad` | `CMCMech__Reset` alternate reset-path callsite with the same stack-payload shape. |
| `0x0049bddf` | Recursive callsite inside the target; passes the descendant mesh part from the parent child table. |

## Wave756 Mech.cpp Unwind Continuation (2026-05-23)

Wave756 static read-back (`unwind-continuation-wave756`, `wave756-readback-verified`) hardened Mech.cpp-adjacent compiler-generated SEH unwind cleanup callbacks from `0x005d33c0 Unwind@005d33c0` through `0x005d3460 Unwind@005d3460`. Evidence includes Mech.cpp debug path `0x0062e0e0`, DATA scope-table xrefs `0x0061c0d4` through `0x0061c19c`, four `OID__FreeObject_Callback` rows, `CParticleManager__RemoveFromGlobalList_Thunk`, and `CUnitAI__dtor_body_00415080`. Exact anchors include `0x005d3420 Unwind@005d3420` and `0x005d3440 Unwind@005d3440`. Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260523-112625_post_wave756_unwind_continuation_verified`. Exact parent source-body identity, runtime exception behavior, runtime cleanup behavior, BEA patching, and rebuild parity remain deferred.

| Address | Static read-back evidence |
| --- | --- |
| `0x005d33c0 Unwind@005d33c0` | `OID__FreeObject_Callback(*(EBP-0x10))`, line token `0x1b`, allocation/type value `0x3d`, DATA xref `0x0061c0d4`. |
| `0x005d33e0 Unwind@005d33e0` | `OID__FreeObject_Callback(*(EBP-0x10))`, line token `0x16`, allocation/type value `0x48`, DATA xref `0x0061c0fc`. |
| `0x005d3400 Unwind@005d3400` | `OID__FreeObject_Callback(*(EBP-0x10))`, line token `0x17`, allocation/type value `0x4e`, DATA xref `0x0061c124`. |
| `0x005d3420 Unwind@005d3420` | `OID__FreeObject_Callback(*(EBP+0x4))`, line token `0x5c`, allocation/type value `0x57`, DATA xref `0x0061c14c`. |
| `0x005d3440 Unwind@005d3440` | `CParticleManager__RemoveFromGlobalList_Thunk(EBP-0x8c)`, DATA xref `0x0061c174`. |
| `0x005d3460 Unwind@005d3460` | `CUnitAI__dtor_body_00415080(*(EBP-0x10))`, DATA xref `0x0061c19c`. |

## Functions

| Address | Name | Purpose | Size |
|---------|------|---------|------|
| 0x0049f820 | SharedGroundUnit__VFunc_09_InitGroundedMotionComponents_0049f820 | Shared vtable slot 9 body for vtables `0x005e0684` and `0x005e3074`; calls `CGroundUnit__Init`, invokes slots 117/118/119, and resolves a named child reference | ~280 bytes |
| 0x0049f940 | [CMech__InitLegMotion](./CMech__InitLegMotion.md) | Finds `LegMotion`, allocates a `0xf0` `CMCMech` controller, stores `this+0x70`, and passes init-context values to `CMCMech__SetParams` | ~220 bytes |
| 0x0049fa30 | [CMech__InitCockpit](./CMech__InitCockpit.md) | Allocates a `0x64` object through `CMechAI__ctor` and stores it at `this+0x13c` | ~110 bytes |
| 0x0049faa0 | [CMech__InitTargeting](./CMech__InitTargeting.md) | Allocates a `0x48` object through `CMechGuide__ctor` and stores it at `this+0x208` | ~100 bytes |
| 0x004a02e0 | CMechAI__ctor | Constructs the `0x64` cockpit/AI helper allocated by `CMech__InitCockpit`, installs vtable `0x005dc4c0`, and randomizes the `+0x60` state flag | ~180 bytes |
| 0x004a0390 | CMechAI__scalar_deleting_dtor | Vtable `0x005dc4c0` slot 1 scalar-deleting destructor wrapper around `CUnitAI__dtor_base` | ~30 bytes |
| 0x004a0a20 | CMechGuide__ctor | Constructs the `0x48` targeting guide allocated by `CMech__InitTargeting`, installs vtable `0x005dc4f4`, allocates path buffers, and schedules event `2000` | ~240 bytes |
| 0x004a0b10 | CMechGuide__scalar_deleting_dtor | Vtable `0x005dc4f4` slot 1 scalar-deleting destructor wrapper around `CMechGuide__dtor_base` | ~30 bytes |
| 0x004a0b30 | CMechGuide__dtor_base | Removes active reader state, frees guide buffers, and calls `CMonitor__Shutdown` | ~120 bytes |
| 0x004a0bc0 | CMechGuide__VFunc_03_UpdateGuidanceState_004a0bc0 | Vtable `0x005dc4f4` slot 3 guidance update body using owner, active-reader, AI-state, and path-buffer fields | ~1700 bytes |
| 0x004a1270 | CMechGuide__SelectNearestHostileTargetReader | Clears active reader field `+0x44`, scans nearby `CMapWho` entries, and stores the nearest compatible hostile reader | ~280 bytes |

## Key Observations

- **Shared slot-9 body** - `0x0049f820` appears in two vtable tables (`0x005e0684` and `0x005e3074`) and is intentionally saved with shared grounded-unit naming instead of a single concrete owner.
- **Slot arity read-back** - `0x0049f820`, `0x0049f940`, and `0x0049fa30` each end in `RET 0x4`; `0x0049faa0` is register-only.
- **Component storage offsets** - `CMech__InitLegMotion` writes `this+0x70`, `CMech__InitCockpit` writes `this+0x13c`, and `CMech__InitTargeting` writes `this+0x208`.
- **AI/guide lifecycle** - Wave437 saved the CMechAI constructor/scalar destructor and the CMechGuide constructor/scalar/base destructors plus slot-3 guidance update and nearest-target helper. The slot names remain evidence-bounded; exact source method names and runtime targeting behavior are still open.
- **Source-path evidence** - Object allocations reference `[maintainer-local-source-export-root]\Mech.cpp` lines `0x3d`, `0x48`, and `0x4e`.
- **Proof boundary** - Exact virtual method names, concrete `CMech` layout, local variable names/types, source-body identity, runtime behavior, and rebuild parity remain open.

## Related Files

- Unit.cpp - Base class functions (CUnit__Init, CUnit__ApplyDamage, etc.)
- Career.cpp - Kill tracking (player kills tracked as TK_MECHS)
- Player.cpp - Player-specific invincibility (runtime `CPlayer::mIsGod` / `SetVulnerable(FALSE)`; cheat-gated in retail)
- GroundUnit.cpp - Shared `CGroundUnit` initialization context and slot-9 body
- MCMech.cpp - Motion-controller construction and `CMCMech__SetParams`
- World.cpp - Level data and animation assets such as `LegMotion`

---
*Migrated from ghidra-analysis.md (Dec 2025); updated with Wave436 and Wave437 saved Ghidra evidence (2026-05-16).*
