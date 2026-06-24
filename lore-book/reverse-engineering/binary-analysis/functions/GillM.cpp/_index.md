# GillM.cpp Functions

> Source File: GillM.cpp | Binary: BEA.exe
> Debug Path: 0x0062c9e8

> **Queue status (2026-05-31):** Ghidra export-contract closure **6222/6222** (Wave1000: every currently exported function object commented with clean-signature proxy; not evidence-grade semantics). Lines below that reference a "next raw commentless" row are **archival wave progress**, not open work.

## Overview

Wave389 corrected the saved GillM-family Ghidra metadata for the local `0x004799c0` through `0x0047a0b0` cluster, and Wave409 corrected `0x0047a160` from an older CExplosionInitThing owner label into the same CGillM vtable family. Wave1000 re-reviewed the grounded movement, terrain, and state-vector island read-only and found the saved evidence still coherent. The strongest current evidence is binary-side RTTI/vtable read-back rather than a full source-body match: CGillM resolves through RTTI vtable `0x005e0b30`, CMCGillM through `0x005dbc74`, CGillMAI through `0x005dbcb4`, and the shared CMCMech scalar-deleting destructor is reused by CMCBattleEngine, CMCGillM, and CMCThunderHead vtable slot `1`.

Stuart's source tree is useful architecture context, but this source file is not currently available as a matching checked source body in the submodule. Saved names below are therefore conservative behavior/owner labels backed by retail Ghidra read-back, vtable slots, strings, allocation sizes, and local control-flow evidence.

## Current Saved Functions

| Address | Name | Evidence | Remaining uncertainty |
|---------|------|----------|----------------------|
| 0x004799c0 | CGillM__VFunc09_InitGroundedSpawnState | CGillM vtable slot `9`; clears/sets grounded, timer, and spawn-state fields, calls inherited slot-9 body, samples static-shadow height, and snapshots current position context. | Exact source virtual name and concrete field layout remain open. |
| 0x00479a50 | CGillM__InitLegMotion | CGillM vtable slot `117`; looks up `LegMotion`, allocates a `0xf0` CMCGillM motion-controller object, installs CMCGillM vtable `0x005dbc74`, stores it at `this+0x70`, and seeds motion parameters. | Concrete init-data layout and runtime animation behavior remain open. |
| 0x00479b40 | SharedCMCMech__ScalarDeletingDestructor | CMCBattleEngine, CMCGillM, and CMCThunderHead vtable slot `1` point here; wrapper calls `CMCMech__Destructor`, optionally frees `this`, and returns it. | Exact derived destructor ownership remains intentionally shared/deferred. |
| 0x00479b60 | CGillM__InitGillMAIComponent | CGillM vtable slot `118`; allocates a `0x60` object, calls CWarspite-style base init, installs CGillMAI vtable `0x005dbcb4`, and stores it at `this+0x13c`. | The older `InitWarspiteComponent` label was too broad; CGillMAI layout and exact source method name remain open. |
| 0x00479bf0 | CGillMAI__ScalarDeletingDestructor | CGillMAI vtable slot `1`; wrapper calls `CGillMAI__Destructor`, optionally frees `this`, and returns it. | Runtime destruction behavior remains unproven. |
| 0x00479c10 | CGillMAI__Destructor | Called by the scalar-deleting destructor; restores base AI-style vtable state, removes tracked-set entries, and calls `CMonitor__Shutdown`. | Exact inherited AI owner and concrete member layout remain open. |
| 0x00479cb0 | CGillM__InitTerrainGuideComponent | CGillM vtable slot `119`; allocates a `0x20` TerrainGuide-style object, calls `CTerrainGuide__ctor`, and stores it at `this+0x208`. Wave544 refreshed the older saved comment that still carried the constructor-like symbol. | Exact component class name, concrete guide layout, and runtime terrain-guide behavior remain open. |
| 0x00479d10 | CGillM__UpdateGroundedVerticalDrift | CGillM vtable slot `66`; uses fields around `+0x244` and `+0x274` plus static-shadow sampling to update grounded vertical drift. | Corrects older CExplosionInitThing ownership; exact source virtual name remains open. |
| 0x00479db0 | CGillM__TriggerRandomArmHitAnimationIfReady | Uses `Gill_M_Left_Arm` and `Gill_M_Right_Arm` strings, cooldown field context, child/component traversal, and hit-animation helper calls. | Corrects older CExplosionInitThing ownership; runtime animation behavior remains open. |
| 0x00479f30 | CGillM__ComputeTerrainClearanceNoiseScale | GillM movement helper in the CMCGillM slot-wrapper region; samples two static-shadow heights and computes a terrain clearance/noise scale. | Corrects older CUnitAI ownership; exact formula/source name remains open. |
| 0x0047a0b0 | CGillM__ComputeLateralSlopeAlignment | GillM movement helper using heading field `+0x114`, heightfield-normal sampling, and a lateral slope scalar. | Corrects older CUnitAI ownership; exact formula/source name remains open. |
| 0x0047a160 | CGillM__StartState1WithStoredMotionVector | CGillM vtable slot `100`; skips when state `+0x244` is already `1` or `2`, feeds the four-dword stored motion vector at `+0x278` into vtable `+0xf4` with a zero flag, then writes state `+0x244 = 1`. | Corrects older CExplosionInitThing ownership; exact source virtual name, concrete layout, and runtime movement behavior remain open. |

## Partial Layout Hints

| Offset | Observed role | Evidence boundary |
|--------|---------------|------------------|
| 0x70 | Leg-motion component pointer | Written by `CGillM__InitLegMotion`. |
| 0x13c | CGillMAI component pointer | Written by `CGillM__InitGillMAIComponent`. |
| 0x208 | TerrainGuide-style component pointer | Written by `CGillM__InitTerrainGuideComponent`. |
| 0x244 | Grounded/mode-state context | Used by `CGillM__UpdateGroundedVerticalDrift`. |
| 0x26c | Arm-hit/spawn cooldown context | Used by `CGillM__VFunc09_InitGroundedSpawnState` and arm-hit animation helper context. |
| 0x274 | Grounded flag/context | Used by `CGillM__VFunc09_InitGroundedSpawnState` and vertical-drift helper. |
| 0x278 | Stored four-dword motion-vector context | Used by `CGillM__StartState1WithStoredMotionVector` before vtable `+0xf4` dispatch. |

These are retail field-use hints, not a finalized CGillM structure definition.


## Wave1199 GillM/GroundUnit AI-Motion-Effects Current-Risk Review (2026-06-06)

Wave1199 (`wave1199-gillm-groundunit-ai-motion-effects-current-risk-review`) saved comment/tag normalization for the CGillM rows `0x00479b60`, `0x00479bf0`, `0x00479cb0`, `0x00479d10`, `0x00479db0`, and `0x0047a160`, plus the adjacent GillMHeadAI and shared ground-unit context rows documented in the companion owner pages. Fresh exports verified `10` metadata rows, `10` tag rows, `13 xref rows`, `540 instruction rows`, and `10 decompile rows`. Corrected current-risk accounting is `870/1179 = 73.79%`; remaining active focused work: 309. Verified backup: `G:\GhidraBackups\BEA_20260606-225205_post_wave1199_gillm_groundunit_ai_motion_effects_current_risk_review_verified`. Runtime GillM AI, terrain-guide, motion, arm-hit animation, and mesh-effect behavior remain separate proof.

## Wave1000 Grounded Movement / Terrain Re-Audit (2026-05-31)

Wave1000 (`gillm-grounded-movement-review-wave1000`) re-reviewed the CGillM grounded movement, terrain, and state-vector island with fresh metadata, tag, xref, instruction, decompile, and vtable-slot exports. It made no Ghidra mutation, rename, signature change, function-boundary change, executable-byte change, BEA launch, or runtime/game-file mutation.

Representative anchors:

| Address | Fresh static evidence |
| --- | --- |
| `0x004799c0 CGillM__VFunc09_InitGroundedSpawnState` | CGillM vtable `0x005e0b30` slot `9`; clears cooldown field `+0x26c`, stamps `+0x270`, marks grounded context `+0x274`, and snapshots position context into `+0x278`. |
| `0x00479d10 CGillM__UpdateGroundedVerticalDrift` | CGillM vtable slot `66`; uses `+0x274`, `+0x244`, static-shadow height sampling, and vertical drift fields before shared update dispatch. |
| `0x00479db0 CGillM__TriggerRandomArmHitAnimationIfReady` | Uses `Gill_M_Left_Arm` and `Gill_M_Right_Arm` strings, cooldown `+0x26c`, and component-list context `+0x19c`. |
| `0x00479f30 CGillM__ComputeTerrainClearanceNoiseScale` | Terrain clearance/noise scalar helper reached from the CMCGillM region; gates on grounded/state context and samples two static-shadow heights. |
| `0x0047a0b0 CGillM__ComputeLateralSlopeAlignment` | Lateral slope scalar helper using heading field `+0x114` and heightfield-normal sampling. |
| `0x0047a160 CGillM__StartState1WithStoredMotionVector` | CGillM vtable slot `100`; copies the stored four-dword motion vector at `+0x278` into vtable `+0xf4` dispatch, then writes state `+0x244 = 1`. |

Fresh exports verified `10` metadata rows, `10` tag rows, `10` xref rows, `526` body-instruction rows, `10` decompile rows, and `128` CGillM vtable-slot rows. Wave911 focused re-audit progress remains `467/1408 = 33.17%`; expanded static surface progress is `606/1478 = 41.00%`; Wave911 top-500 risk-ranked coverage is `350/500 = 70.00%`; static closure remains `6222/6222 = 100.00%`. Verified backup: `G:\GhidraBackups\BEA_20260531-101059_post_wave1000_gillm_grounded_movement_review_verified`.

Wave1000 also normalized the historical Wave409 focused probe's live-queue assertions from old Wave409 telemetry to current queue closure (`6222` total, `0` commentless, `0` exact-undefined signatures, `0` `param_N`). The evidence claim did not change.

Runtime GillM movement behavior, runtime terrain/grounding behavior, runtime arm-hit animation behavior, exact source-body identity, concrete CGillM/CMCGillM/CGillMAI/TerrainGuide layouts, BEA patching, and rebuild parity remain separate proof.

## Vtable / RTTI Evidence

| Address | Type / role |
|---------|-------------|
| 0x005e0b30 | CGillM RTTI vtable; Wave389 checked slots `9`, `66`, `117`, `118`, and `119`; Wave409 added slot `100`. |
| 0x005dbc74 | CMCGillM RTTI vtable; slot `1` reaches `SharedCMCMech__ScalarDeletingDestructor`. |
| 0x005dbcb4 | CGillMAI RTTI vtable; slot `1` reaches `CGillMAI__ScalarDeletingDestructor`. |
| 0x005d88ec | CMCBattleEngine RTTI vtable; slot `1` reaches the shared CMCMech scalar-deleting destructor. |
| 0x005df890 | CMCThunderHead RTTI vtable; slot `1` reaches the shared CMCMech scalar-deleting destructor. |

## Wave752 Unwind Cleanup Evidence (2026-05-22)

Wave752 saved GillM.cpp-adjacent compiler-generated SEH unwind cleanup callbacks with the `unwind-continuation-wave752` and `wave752-readback-verified` tags. These rows are static retail Ghidra evidence only, saved as `void __cdecl Unwind@...(void)`, with no renames, no function-boundary changes, and no executable-byte changes.

| Address | Evidence |
| --- | --- |
| `0x005d2a20 Unwind@005d2a20` | DATA scope-table xref `0x0061b7f4`; calls `OID__FreeObject_Callback` with GillM.cpp debug path `0x0062c9e8`, line `0x1b`, allocation/type value `0x2d`, pointer `*(EBP-0x10)`. |
| `0x005d2a40 Unwind@005d2a40` | DATA scope-table xref `0x0061b81c`; calls `OID__FreeObject_Callback` with GillM.cpp debug path `0x0062c9e8`, line `0x16`, allocation/type value `0x38`, pointer `*(EBP-0x10)`. |
| `0x005d2a60 Unwind@005d2a60` | DATA scope-table xref `0x0061b844`; calls `CMonitor__Shutdown` on `*(EBP-0x10)`. |
| `0x005d2a68 Unwind@005d2a68` and `0x005d2a73 Unwind@005d2a73` | DATA scope-table refs `0x0061b84c` and `0x0061b854`; call `CGenericActiveReader__dtor` on `(*(EBP-0x10))+0xc` and `(*(EBP-0x10))+0x24`. |
| `0x005d2a90 Unwind@005d2a90` | DATA scope-table xref `0x0061b87c`; calls `OID__FreeObject_Callback` with GillM.cpp debug path `0x0062c9e8`, line `0x17`, allocation/type value `0x3e`, pointer `*(EBP-0x10)`. |

Verified backup: `G:\GhidraBackups\BEA_20260522-212829_post_wave752_unwind_continuation_verified`. Exact parent source-body identity, runtime GillM cleanup behavior, BEA patching, and rebuild parity remain deferred.

## Validation

- Wave389 headless dry/apply saved `11` targets with `10` renames and `REPORT: Save succeeded`.
- Post-apply read-back verified `11` metadata rows, `11` decompile exports, `13` xref rows, `2431` instruction rows, `11` tag rows, `112` related vtable-slot rows, and `128` CGillM vtable-slot rows.
- Focused probe `tools/ghidra_gillm_family_wave389_probe.py --check` and package script `npm run test:ghidra-gillm-family-wave389` pass against ignored raw read-back exports under `subagents/`.
- Wave409 headless dry/apply corrected `0x0047a160` with `REPORT: Save succeeded`.
- Wave409 post-apply read-back verified `1` metadata row, `1` tag row, `1` DATA xref row, `121` instruction rows, post-apply decompile text, `128` CGillM vtable-slot rows, focused probe status `PASS`, queue telemetry `6028/1562/4466/1909/1854`, and backup `G:\GhidraBackups\BEA_20260514_083210_post_wave409_gillm_state_vector_verified`.
- Wave544 refreshed the saved `CGillM__InitTerrainGuideComponent` function comment from `CTerrainGuide__ctor_like_004f1ec0` to `CTerrainGuide__ctor`; dry/apply/verify read-back reported clean summaries and `REPORT: Save succeeded`.
- Wave1000 read-only re-audit verified `10` metadata rows, `10` tag rows, `10` xref rows, `526` body-instruction rows, `10` decompile rows, `128` CGillM vtable-slot rows, focused probe status `PASS`, static closure `6222/6222 = 100.00%`, and backup `G:\GhidraBackups\BEA_20260531-101059_post_wave1000_gillm_grounded_movement_review_verified`.

## Related Files

- `GillMHead.cpp` - nearby head motion controller debug path context.
- `MCMech.cpp` - motion-controller base/shared destructor context.
- `MCTentacle.cpp` - related motion-controller family context.

## Boundaries

This page records saved static Ghidra metadata, not runtime proof. Exact source method names, concrete class layouts, local variable names, type definitions, runtime GillM behavior, BEA launch behavior, game patching, and rebuild parity remain open.

## Wave1152 Current-Risk Review

Wave1152 (`wave1152-gillm-groundunit-terrain-current-risk-review`) re-read `0x00479f30 CGillM__ComputeTerrainClearanceNoiseScale` and `0x0047a0b0 CGillM__ComputeLateralSlopeAlignment` with fresh metadata/tags/xrefs/instructions/decompile evidence and no mutation. It confirms the saved GillM terrain-helper boundaries as static Ghidra evidence only. Verified backup: `G:\GhidraBackups\BEA_20260605-203535_post_wave1152_gillm_groundunit_terrain_current_risk_review_verified`. Runtime behavior, exact layouts, exact source-body identity, BEA patching behavior, gameplay outcomes, visual QA, and rebuild parity remain separate proof.
