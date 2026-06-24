# GroundUnit.cpp Functions

> Source File: GroundUnit.cpp | Binary: BEA.exe
> Debug Path: 0x0062cb0c

> **Queue status (2026-05-26):** Ghidra export-contract closure **6113/6113** (Wave900: every function commented; clean-signature proxy; not evidence-grade semantics). Lines below that reference a "next raw commentless" row are **archival wave progress**, not open work.

Wave1218 (wave1218-generic-shared-vfunc-thunk-tail-current-risk-review) re-read 0x0049fc10 SharedGroundUnit__VFunc_66_UpdateVerticalDriftPickupAndEffects_0049fc10 as part of the generic/shared vfunc-thunk tail current-risk review. The row remains shared GroundUnit slot-66 static evidence over vertical drift, pickup, and linked-effect handoff, with no mutation, no rename, no signature change, no comment change, no tag change, no function-boundary change, and no executable-byte change. Verified backup: G:\GhidraBackups\BEA_20260607-222830_post_wave1218_generic_shared_vfunc_thunk_tail_current_risk_review_verified. Runtime pickup/effect behavior, exact owner coverage, exact layouts, and rebuild parity remain separate proof.

## Overview

Base class for ground-based units. Current retail Ghidra read-back shows `CGroundUnit` handling thruster setup, collision geometry, linked-effect height-clearance helpers, destruction/reset helpers, and ground-unit linked-state cleanup. Parent class for `CGroundVehicle`. The available repo source does not make every retail helper source-complete, so this page records saved retail-binary evidence rather than full source parity.

Wave1140 (`wave1140-motion-controller-current-risk-review`) re-read the motion-controller residual current-risk cluster including shared-ground anchor `0x0049f820 SharedGroundUnit__VFunc_09_InitGroundedMotionComponents_0049f820`, plus `0x00497090 CMCHiveBoss__Constructor`, `0x00497140 CDestructableSegmentsMotionController__CacheNamedCollisionCylinders`, `0x00494fa0 SharedMotionController__VFunc_UpdateUnitAIIndexedEntryFlag`, `0x00494ff0 SharedMotionController__VFunc_CallUnitAIIndexedEntryVFunc10`, `0x0049c1d0 CMCMech__VFunc_05_WriteInterpolatedBoneFloat_0049c1d0`, `0x0049c3e0 CMCMine__Constructor`, `0x0049c440 CMCMine__VFunc_04_UpdateInterpolatedHeightOffset_0049c440`, and `0x0049c5d0 CMCSentinel__Constructor`. It covers `9 current-risk rows`; current focused accounting is `238/1179 = 20.19%`; current risk candidates: 6166; current focused candidates: 1178; live regenerated current focused candidates: 1178; remaining active focused work: 941; static debt `0 / 0 / 0`; static closure `6411/6411 = 100.00%`. This was a fresh Ghidra export, read-only review, no mutation. Verified backup: `G:\GhidraBackups\BEA_20260605-142515_post_wave1140_motion_controller_current_risk_review_verified`; previous completed backup: `G:\GhidraBackups\BEA_20260605-134608_post_wave1139_battleengine_jetpart_current_risk_review_verified`. Runtime motion-controller behavior, exact layouts, and rebuild parity remain separate proof.

Wave1069 (`groundunit-vfunc-motion-effects-review-wave1069`) re-read `0x0049f820 SharedGroundUnit__VFunc_09_InitGroundedMotionComponents_0049f820`, `0x0049fc10 SharedGroundUnit__VFunc_66_UpdateVerticalDriftPickupAndEffects_0049fc10`, and `0x0049fdb0 SharedGroundUnit__VFunc_71_SpawnGenericMeshBreakEffects_0049fdb0` with CMCMech/CMCMine/CMine/CPod context and no mutation. Fresh evidence ties the shared rows to multiple ground-unit vtables, `CGroundUnit__Init`, `CGroundUnit__UpdateLinkedEffectsByHeightClearance`, and `CMCMech__BuildInterpolatedPoseAndAnchor`. Runtime grounded-unit, pickup, mesh-break, particle/effect cleanup, and motion behavior remain separate proof.


## Wave1199 GillM/GroundUnit AI-Motion-Effects Current-Risk Review (2026-06-06)

Wave1199 (`wave1199-gillm-groundunit-ai-motion-effects-current-risk-review`) saved comment/tag normalization for `0x0049fdb0 SharedGroundUnit__VFunc_71_SpawnGenericMeshBreakEffects_0049fdb0`, now re-read as the score19 shared ground-unit/GillM-adjacent mesh break-effect dispatcher. Fresh DATA refs `0x005e3190`, `0x005e10fc`, `0x005e0c4c`, and `0x005e07a0` cover sampled ground-unit vtables. Corrected current-risk accounting is `870/1179 = 73.79%`; remaining active focused work: 309. Verified backup: `G:\GhidraBackups\BEA_20260606-225205_post_wave1199_gillm_groundunit_ai_motion_effects_current_risk_review_verified`. Runtime mesh-effect behavior, exact concrete owner coverage, and rebuild parity remain separate proof.

## Functions

| Address | Name | Purpose | Size |
|---------|------|---------|------|
| 0x0047c730 | CGroundUnit__Init | Initialize ground-unit state, movement/profile fields, thruster-linked nodes, and collision setup context | ~380 bytes |
| 0x0047c8e0 | CGroundUnit__CreateCollisionSphere | Create radius-derived collision sphere state and add collision context | ~130 bytes |
| 0x0047c970 | CGroundUnit__UpdateLinkedEffectsByHeightClearance | Update linked-effect and motion/attachment state using height-clearance context | ~1290 bytes |
| 0x0047ce80 | CGroundUnit__MarkDestroyedAndResetState | Call unit destruction cleanup and clear `+0x25c` on success | ~30 bytes |
| 0x0047cea0 | CGroundUnit__ClearLinkedThingFlagsAndResetCounter | Walk linked `+0x1d4` set and clear/reset associated `+0x1e4` state | ~60 bytes |
| 0x0049f820 | [SharedGroundUnit__VFunc_09_InitGroundedMotionComponents_0049f820](./SharedGroundUnit__VFunc_09_InitGroundedMotionComponents_0049f820.md) | Shared slot-9 grounded-unit init body used by vtable tables `0x005e0684` and `0x005e3074`; calls `CGroundUnit__Init` and then slots 117/118/119 | ~280 bytes |
| 0x0049fc10 | SharedGroundUnit__VFunc_66_UpdateVerticalDriftPickupAndEffects_0049fc10 | Shared/default slot-66 body for vtables `0x005e0684` and `0x005e3074`; concrete GillM/ThunderHead-style slot-66 overrides call into it | ~410 bytes |
| 0x0049fdb0 | SharedGroundUnit__VFunc_71_SpawnGenericMeshBreakEffects_0049fdb0 | Shared slot-71 body across sampled Mech/GillM/ThunderHead-style ground tables; spawns generic mesh break effects from child mesh parts | ~520 bytes |
| 0x0050ed10 | CGroundUnit__Constructor | Install `CGroundUnit` primary/secondary vtables after the `CActor` constructor path | ~30 bytes |

## Exception Handlers

| Address | Name | Debug line / allocation type | Purpose |
|---------|------|------|---------|
| 0x005d2bb0 | Unwind@005d2bb0 | line `0x10`, type `0x23` | Wave752 cleanup for `*(EBP+0x4)` through `OID__FreeObject_Callback` with GroundUnit.cpp debug path `0x0062cb0c`. |

Wave752 saved `0x005d2bb0 Unwind@005d2bb0` with `unwind-continuation-wave752` and `wave752-readback-verified` tags. Verified backup: `G:\GhidraBackups\BEA_20260522-212829_post_wave752_unwind_continuation_verified`. The row is static retail Ghidra evidence only; exact parent source-body identity, runtime ground-unit cleanup behavior, BEA patching, and rebuild parity remain deferred.

## Key Observations

- **Thruster setup** - References "Thruster" string at 0x00623080
- **Two-phase init** - Basic setup, then collision/physics
- **Collision sphere** - 0x1c bytes, radius calculation with 0.8 scale factor
- **Parent of CGroundVehicle** - Called by CGroundVehicle__Init
- **Wave 392 owner correction** - `0x0047c970` and `0x0047ce80` are now saved as `CGroundUnit` helpers, superseding older over-specific Cannon-local labels.
- **Wave 392 cleanup correction** - `0x0047cea0` is now saved as `CGroundUnit__ClearLinkedThingFlagsAndResetCounter`, superseding the older broad `CUnitAI` label.
- **Wave 436 shared slot correction** - `0x0049f820` is saved as a shared grounded-unit slot-9 initializer because two vtable tables point to it; the exact concrete owner remains intentionally deferred.
- **Wave 437 shared slot correction** - `0x0049fc10` is saved as shared/default slot 66 for the sampled Mech pair, while `0x0049fdb0` is saved as shared slot 71 across sampled Mech/GillM/ThunderHead-style ground tables.
- **Current boundary** - Runtime ground-unit movement, collision, destruction, concrete layouts, locals/types, exact source identities, and rebuild parity remain unproven.

## Class Hierarchy

```
CUnit
  └── CGroundUnit
        └── CGroundVehicle
```

## Related Files

- Unit.cpp - CUnit base class
- GroundVehicle.cpp - CGroundVehicle derived class

---
*Discovered via Phase 1 xref analysis (Dec 2025); updated with Wave 392 saved Ghidra owner/signature/comment evidence (2026-05-14), Wave436 shared slot-9 evidence, and Wave437 shared slot-66/71 evidence (2026-05-16).*

## Wave1152 Current-Risk Review

Wave1152 (`wave1152-gillm-groundunit-terrain-current-risk-review`) re-read `0x0047c970 CGroundUnit__UpdateLinkedEffectsByHeightClearance`, `0x0047ce80 CGroundUnit__MarkDestroyedAndResetState`, and `0x0047cea0 CGroundUnit__ClearLinkedThingFlagsAndResetCounter` with fresh metadata/tags/xrefs/instructions/decompile evidence and no mutation. It confirms the saved GroundUnit linked-effect/destruction helper boundaries as static Ghidra evidence only. Verified backup: `G:\GhidraBackups\BEA_20260605-203535_post_wave1152_gillm_groundunit_terrain_current_risk_review_verified`. Runtime behavior, exact layouts, exact source-body identity, BEA patching behavior, gameplay outcomes, visual QA, and rebuild parity remain separate proof.
