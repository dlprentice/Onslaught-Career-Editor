# GillMHead.cpp Functions

Wave1219 final current-risk closure note: `SharedUnitAnimation__FindAnimationIndexOrZero` and `SharedUnitAnimation__PlayAnimationByNameIfPresent` remain mapped as shared animation helpers used by GillMHead and BattleEngine paths; verified backup `G:\GhidraBackups\BEA_20260607-230027_post_wave1219_final_score16_current_risk_review_verified`. Runtime animation behavior, exact owning-base layout, and rebuild parity remain separate proof.

> Source File: GillMHead.cpp | Binary: BEA.exe
> Debug Path: 0x0062ca6c (`C:\dev\ONSLAUGHT2\GillMHead.cpp`)

> **Queue status (2026-05-31):** Ghidra export-contract closure **6222/6222** after Wave1001; every current function object is commented with clean signatures, but this is not runtime proof or rebuild parity. Lines below that reference a "next raw commentless" row are **archival wave progress**, not open work.

## Overview

Wave390 corrected this page after fresh metadata, decompile, xref, instruction, RTTI/vtable, pointer-table, and tag read-back. The checked `0x0047a760..0x0047b090` cluster is now documented as a GillMHead owner path that creates and stores a `CGillMHeadAI` component, plus `CGillMHeadAI` state/targeting helpers. Wave1001 (`gillmhead-ai-review-wave1001`) re-reviewed the same island and saved two comment/tag corrections: `0x0047a900 CGillMHeadAI__AdvanceOpenAttackCloseState` now names `CUnit__HasAnyLinkedUnitBeforeTargetTimeout`, and `0x0047afc0 CGillMHeadAI__UpdateAimTransformAndTargetReader` now names `CUnit__ForwardAimTransformAndAttachTargetReader` instead of stale Wave390 `CWarspite__UpdateAimTransformAndAttachTargetReader` wording. The old `0x004d10b0` GillMHead pause-latch label was wrong for the current saved project; it is now `CPauseMenu__DeactivatePauseSession`.

Wave1118 (`wave1118-particle-message-current-risk-review`) re-read `0x0047afc0 CGillMHeadAI__UpdateAimTransformAndTargetReader` and `0x0047b090 CGillMHeadAI__UpdateTargetBallisticArcFlags` from the current score-26 focused queue with a fresh read-only Ghidra export and no mutation. Static evidence still ties both rows to `CGillMHeadAI` vtable `0x005dbcec`: slot 3 forwards aim transform / target-reader context through `CUnit__ForwardAimTransformAndAttachTargetReader`, and slot 4 updates ballistic readiness through `CUnit__CanFireAtTarget_BallisticArcB/A`. Current focused accounting moves to `100/1179 = 8.48%`; verified backup `G:\GhidraBackups\BEA_20260605-021103_post_wave1118_particle_message_current_risk_review_verified`. Runtime GillMHead targeting/firing behavior, exact source-body identity, concrete layout, BEA patching, and rebuild parity remain separate proof.

Wave1135 (`wave1135-groundattack-gillmhead-current-risk-review`) re-read this GroundAttack/GillMHead guide lifecycle cluster with fresh Ghidra export evidence as a read-only review with no mutation. It accounts for `10 rows`, moves current focused accounting to `196/1179 = 16.62%`, keeps static closure at `6410/6410 = 100.00%`, keeps expanded static surface at `1560/1560 = 100.00%`, keeps Wave911 focused at `812/1408 = 57.67%`, keeps Wave911 top-500 at `500/500 = 100.00%`, and leaves static debt at `0 / 0 / 0`; current focused candidates: 1178; live regenerated current focused candidates: 1178; remaining active focused work: 983. Exact anchors: `0x0047a760 CGillMHead__CreateGillMHeadAIComponent`, `0x0047a810 CGillMHeadAI__Destructor`, `0x0047a8b0 CGillMHeadAI__TryTransitionIdleToOpen`, `0x0047bab0 CGroundAttackAI__InitState`, `0x0047bbf0 CGroundAttackAircraft__Init`, `0x0047bd90 CGroundAttackAI__Destructor`, `0x0047be50 CGroundAttackGuide__Destructor`, `0x0047c040 CGroundAttackAircraft__AdvanceCloseShootAnimationState`, `0x0047e290 CGuide__ctor_base`, and `0x004964d0 CMCGroundAttack__Constructor`. Verified backup: `G:\GhidraBackups\BEA_20260605-111213_post_wave1135_groundattack_gillmhead_current_risk_review_verified`; previous completed backup: `G:\GhidraBackups\BEA_20260605-104845_post_wave1134_console_current_risk_review_verified`. Runtime GroundAttack/GillMHead AI behavior, runtime guide/bay-animation/motion-controller behavior, exact layouts, BEA patching, gameplay outcomes, visual QA, and rebuild parity remain separate proof.

**Component allocation size**: 100 bytes (0x64), Type ID: 0x16

**RTTI/vtable evidence**: primary checked vtable `0x005dbcec` demangles to `CGillMHeadAI`; destructor restore path references base `CUnitAI` vtable `0x005d8d1c`.


## Wave1199 GillM/GroundUnit AI-Motion-Effects Current-Risk Review (2026-06-06)

Wave1199 (`wave1199-gillm-groundunit-ai-motion-effects-current-risk-review`) saved comment/tag normalization for `0x0047a900 CGillMHeadAI__AdvanceOpenAttackCloseState`, `0x0047a730 CGillMHeadAIVFunc__ForwardArgAndSetIdleAnimation_0047a730`, and `0x0047a9c0 CGillMHeadAIVFunc__ForwardNonMode4ToEngagementSetter_0047a9c0`. Fresh DATA refs `0x005e42e4`, `0x005e421c`, and `0x005e42d0` keep the GillMHeadAI/pointer-table context bounded. Corrected current-risk accounting is `870/1179 = 73.79%`; remaining active focused work: 309. Verified backup: `G:\GhidraBackups\BEA_20260606-225205_post_wave1199_gillm_groundunit_ai_motion_effects_current_risk_review_verified`. Runtime GillMHead AI animation/engagement behavior, exact layouts, and source virtual identities remain separate proof.

## Functions

| Address | Name | Purpose | Size |
|---------|------|---------|------|
| 0x0047a760 | CGillMHead__CreateGillMHeadAIComponent | Allocates a 0x64-byte type-0x16 component, initializes it through `CWarspite__Init`, installs the `CGillMHeadAI` RTTI vtable, clears `+0x60`, and stores it at owner `+0x13c` | ~143 bytes |
| 0x0047a7f0 | CGillMHeadAI__ScalarDeletingDestructor | `CGillMHeadAI` vtable slot-1 scalar-deleting destructor wrapper | ~32 bytes |
| 0x0047a810 | CGillMHeadAI__Destructor | Restores the `CUnitAI` base vtable and removes tracked handles at `+0x28`, `+0x24`, and `+0x0c` before monitor shutdown | ~159 bytes |
| 0x0047a8b0 | CGillMHeadAI__TryTransitionIdleToOpen | Animation-state gate: transitions `idle -> open` when current state and unit conditions match | ~88 bytes |
| 0x0047a900 | CGillMHeadAI__AdvanceOpenAttackCloseState | Animation-state advance helper for `open/attack/close/idle` cycle; Wave1001 names the timeout gate as `CUnit__HasAnyLinkedUnitBeforeTargetTimeout` | ~180 bytes |
| 0x0047afc0 | CGillMHeadAI__UpdateAimTransformAndTargetReader | Updates aim transform / target-reader context using the owner-facing-vector 100.0-distance context; Wave1001 names the handoff as `CUnit__ForwardAimTransformAndAttachTargetReader` | ~197 bytes |
| 0x0047b090 | CGillMHeadAI__UpdateTargetBallisticArcFlags | Clears stale target reader context and updates ballistic firing-readiness flags through `CUnit__CanFireAtTarget_BallisticArcB/A` | ~108 bytes |

## Vtable Analysis

**Primary checked vtable**: `0x005dbcec` (`CGillMHeadAI`, installed by `CGillMHead__CreateGillMHeadAIComponent`)

| Offset | Address | Function |
|--------|---------|----------|
| 0x00 | 0x004ff330 | (inherited) |
| 0x04 | 0x0047a7f0 | CGillMHeadAI__ScalarDeletingDestructor |
| 0x08 | 0x004bacb0 | (inherited - CWarspite) |
| 0x0C | 0x0047afc0 | CGillMHeadAI__UpdateAimTransformAndTargetReader |
| 0x10 | 0x0047b090 | CGillMHeadAI__UpdateTargetBallisticArcFlags |
| ... | ... | (additional inherited methods) |

**Secondary/base vtable**: `0x005d8d1c` (`CUnitAI`, restored in destructor)

The related pointer table at `0x005e42d8` points slot `3` to `0x0047a900`, slot `30` to `0x0047a8b0`, and slot `63` to `0x0047a760`; current evidence supports a GillMHeadAI state/create dispatch context, not final source method identity.

## Wave1001 GillMHeadAI Re-Audit Evidence (2026-05-31)

Wave1001 static read-back (`gillmhead-ai-review-wave1001`, `wave1001-readback-verified`) corrected two stale/imprecise comments while preserving the Wave390 names and signatures. Exact anchor: `0x0047a760 CGillMHead__CreateGillMHeadAIComponent`. Dry/apply/final dry reported `updated=0 skipped=2 comment_only_updated=2 tags_added=8 missing=0 bad=0`, then `updated=2 skipped=0 comment_only_updated=2 tags_added=8 missing=0 bad=0`, then `updated=0 skipped=2 comment_only_updated=0 tags_added=0 missing=0 bad=0`, with `REPORT: Save succeeded`. Fresh post exports verified `7` metadata rows, `7` tag rows, `7` xref rows, `320` body-instruction rows, `7` decompile rows, `16` vtable-slot rows, `2` vtable type rows, and `64` pointer-table rows.

| Address | Wave1001 correction |
| --- | --- |
| `0x0047a900 CGillMHeadAI__AdvanceOpenAttackCloseState` | Pointer table `0x005e42d8` slot `3`; body compares `open`, `attack`, `close`, and `idle`, uses `CUnit__HasAnyLinkedUnitBeforeTargetTimeout` before requesting the close transition, and requests animation playback through `SharedUnitAnimation__PlayAnimationByNameIfPresent`. |
| `0x0047afc0 CGillMHeadAI__UpdateAimTransformAndTargetReader` | `CGillMHeadAI` vtable `0x005dbcec` slot `3`; body dispatches base update, selects support/escort target context, computes a 100-unit owner-facing-vector aim transform using constant `0x005db020`, then calls `CUnit__ForwardAimTransformAndAttachTargetReader`. |

Progress anchors after Wave1001: static queue `6222/6222 = 100.00%`, Wave911 focused re-audit `472/1408 = 33.52%`, expanded static surface `613/1478 = 41.47%`, and Wave911 top-500 risk-ranked coverage `355/500 = 71.00%`. Verified backup: `G:\GhidraBackups\BEA_20260531-104623_post_wave1001_gillmhead_ai_review_verified`. Runtime GillMHead animation behavior, runtime GillMHead targeting behavior, exact source-body identity, concrete `CGillMHeadAI`/owner/target-reader/animation-state/ballistic-flag layouts, BEA patching, and rebuild parity remain separate proof.

## Wave752 Unwind Cleanup Evidence (2026-05-22)

Wave752 saved GillMHead.cpp-adjacent compiler-generated SEH unwind cleanup callbacks with the `unwind-continuation-wave752` and `wave752-readback-verified` tags. These rows are static retail Ghidra evidence only, saved as `void __cdecl Unwind@...(void)`, with no renames, no function-boundary changes, and no executable-byte changes.

| Address | Evidence |
| --- | --- |
| `0x005d2ab0 Unwind@005d2ab0` | DATA scope-table xref `0x0061b8a4`; calls `OID__FreeObject_Callback` with GillMHead.cpp debug path `0x0062ca6c`, line `0x16`, allocation/type value `0x13`, pointer `*(EBP-0x10)`. |
| `0x005d2ad0 Unwind@005d2ad0` | DATA scope-table xref `0x0061b8cc`; calls `CMonitor__Shutdown` on `*(EBP-0x10)`. |
| `0x005d2ad8 Unwind@005d2ad8` and `0x005d2ae3 Unwind@005d2ae3` | DATA scope-table refs `0x0061b8d4` and `0x0061b8dc`; call `CGenericActiveReader__dtor` on `(*(EBP-0x10))+0xc` and `(*(EBP-0x10))+0x24`. |

Verified backup: `G:\GhidraBackups\BEA_20260522-212829_post_wave752_unwind_continuation_verified`. Exact parent source-body identity, runtime GillMHead cleanup behavior, BEA patching, and rebuild parity remain deferred.

## Key Observations

### Position Calculation (Update)
The Update function calculates the head's world position using:
```
pos.x = parent->direction.x * 100.0 + parent->pos.x
pos.y = parent->direction.y * 100.0 + parent->pos.y
pos.z = parent->direction.z * 100.0 + parent->pos.z
```
This positions the head 100 units along the parent's facing direction.

### Animation State Strings

The new semantic promotions at `0x0047a8b0` and `0x0047a900` are grounded by direct string usage:

- `idle` (`0x0062ca48`)
- `open` (`0x00623bb4`)
- `attack` (`0x00624438`)
- `close` (`0x006289e4`)

Observed behavior:
- `TryTransitionIdleToOpen` only arms `open` when current animation is `idle` and a unit-gate helper passes.
- `AdvanceOpenAttackCloseState` cycles between `open/attack/close/idle` using runtime gating checks.

### Pause-Menu Correction

Wave 390 moved the old `0x004d10b0` GillMHead pause-latch label to `CPauseMenu__DeactivatePauseSession`. `CGame__UnPause` calls it on `CGame::mPauseMenu`, and Stuart source confirms the corresponding pause-menu deactivate path. Do not treat `0x004d10b0` as GillMHead evidence in current docs.

### GroundAttackGuide Correction

Wave 391 moved the old `0x0047be30` / `0x0047be50` GillMHead destructor labels to `CGroundAttackGuide__ScalarDeletingDestructor` and `CGroundAttackGuide__Destructor`. RTTI/vtable read-back shows vtable `0x005dbd20` demangles to `CGroundAttackGuide`, and slot `1` points to `0x0047be30`. Do not treat those addresses as GillMHead evidence in current docs.

### Object Layout (partial)
| Offset | Type | Field |
|--------|------|-------|
| 0x00 | void* | vtable |
| 0x08 | ptr | Parent object pointer |
| 0x0C | ptr | Model/resource handle 1 |
| 0x10 | ptr | Enable flag (non-null = enabled) |
| 0x18 | int | Node index 1 |
| 0x1C | int | Node index 2 |
| 0x24 | ptr | Resource handle 2 |
| 0x28 | ptr | Resource handle 3 |
| 0x2C | ptr | Resource handle 4 (Destructor2 only) |
| 0x34 | vec3 | Transform data (passed to model) |
| 0x60 | int | Unknown (set to 0 in Create) |

### Parent Storage
The created `CGillMHeadAI` component pointer is stored at offset `0x13c` in the owner object. Current evidence supports the owner/component relationship but not concrete class layout completion.

### Resource Cleanup
Uses CSPtrSet__Remove to unlink resource handles from an internal SPtrSet list (returns node to pool); callers still perform resource-specific teardown separately.

## Related Files

- **GillM.cpp** - Parent class, the main GillM enemy body
- **CWarspite** - Base class providing Init function (0x004fe710)

## Notes

- The 100.0 multiplier constant is stored at 0x005db020
- DAT_006fbdfc appears to be a distance/visibility threshold for disabling updates

---
*Originally discovered via Phase 1 xref analysis (Dec 2025); Wave390 correction applied 2026-05-14; Wave391 removed stale GroundAttackGuide labels from this page; Wave1001 corrected two stale/imprecise GillMHeadAI comments on 2026-05-31.*
