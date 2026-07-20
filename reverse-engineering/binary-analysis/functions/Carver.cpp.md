# Carver.cpp Functions

> Source File: Carver.cpp | Binary: BEA.exe
> Debug Path: 0x00624400 (`[maintainer-local-source-export-root]\Carver.cpp`)

## Overview

The Carver is a flying enemy unit with wing/attack behavior and a guide/AI helper pair in the retail binary. `Carver.cpp` source is not present in the current `references/Onslaught/` snapshot, so this page documents saved retail-binary Ghidra findings rather than source-perfect identities.

Wave1178 (`wave1178-carver-current-risk-consolidation-review`) re-read and tag-normalized `20 Carver current-risk rows` as a coherent CCarver/CCarverAI/CCarverGuide init, wing, attack, target-reader, guide, aim-global, and destructor slice. Fresh Ghidra exports verified `20` metadata rows, `20` tag rows, `23 xref rows`, `873 instruction rows`, and `20` decompile rows. The apply/final dry read-back added `tags_added=206` with `updated=20 skipped=0`, then final dry `skipped=20`; there was no rename, no signature change, no comment change, no function-boundary change, and no executable-byte change. Codex read-only consult used; consult narrowed to 11 rows, while Codex root final judgment widened to a 20-row coherent Carver slice. Current focused accounting is `715/1179 = 60.64%`; current focused candidates: 1178; live regenerated current focused candidates: 1178; remaining active focused work: 464; current risk candidates: 6166; static closure remains `6411/6411 = 100.00%` with `0 / 0 / 0` debt. Static anchors include `CCarver__Init`, `CCarverAI__dtor_base`, `CCarver__UpdateMotionAndWingPose`, `CCarverAI__OpenWings`, `CCarverAI__CloseWings`, `CCarverAI__Fire`, `CCarverAI__CheckNearbyEnemies`, `CCarverGuide__AcquireNearestTargetReader`, and `CCarver__Destructor_VFunc01`. Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260606-095003_post_wave1178_carver_current_risk_consolidation_review_verified`. Runtime Carver behavior, runtime wing timing, runtime attack/target selection behavior, runtime guide/navigation behavior, exact `CCarver`/`CCarverAI`/`CCarverGuide` layouts, exact source-body identity, BEA patching behavior, visual QA, gameplay outcomes, and rebuild parity remain separate proof. Static reconstruction target: preserve rebuild-grade static contracts for a future independent reconstruction aiming at no noticeable difference; actual no-noticeable-difference parity still requires later runtime, asset, visual, control, timing, save, patch, and rebuild proof. Probe token anchor: Wave1178; wave1178-carver-current-risk-consolidation-review; 715/1179 = 60.64%; 20 Carver current-risk rows; current focused candidates: 1178; live regenerated current focused candidates: 1178; remaining active focused work: 464; current risk candidates: 6166; fresh Ghidra export; tag-only normalization; updated=20 skipped=0; tags_added=206; no rename; no signature change; no comment change; no function-boundary change; no executable-byte change; Codex read-only consult used; Codex root final judgment; consult narrowed to 11 rows; root widened to 20-row coherent Carver slice; 0 / 0 / 0; 6411/6411 = 100.00%; 23 xref rows; 873 instruction rows; CCarver__Init; CCarverAI__dtor_base; CCarver__UpdateMotionAndWingPose; CCarverAI__OpenWings; CCarverAI__CloseWings; CCarverAI__Fire; CCarverAI__CheckNearbyEnemies; CCarverGuide__AcquireNearestTargetReader; CCarver__Destructor_VFunc01; [maintainer-local-ghidra-backup-root]\BEA_20260606-095003_post_wave1178_carver_current_risk_consolidation_review_verified; wave1108-current-risk-rank; current-risk denominator; focused threshold `15`; not Wave911 reconstruction.

Wave 318 recovered missing Carver-region function boundaries and saved current names/signatures/comments after metadata, decompile, xref, instruction, and callsite-boundary review. Runtime Carver behavior, exact source virtual names, concrete layouts, tags, locals, and rebuild parity remain unproven.

Wave915 re-reviewed six Carver AI/guide targeting helpers (`0x00422db0`, `0x00423510`, `0x00422970`, `0x00422aa0`, `0x00422b90`, and `0x00423490`) with fresh metadata, tag, instruction, and decompile exports. The saved names/signatures/comments remain appropriate for the current evidence; no Ghidra mutation was performed.

Wave945 (`carver-vtable-boundary-wave945`) recovered three CCarver-local vtable function boundaries that were still `NO_FUNCTION_AT_POINTER` rows in the vtable export: `0x00422750 CCarver__Thunk_CallGuideVFunc08`, `0x004228b0 CCarver__VFunc35_RenderWithFadeGlobal`, and `0x00422910 CCarver__VFunc104_IsWingBlendAboveThreshold`. The pass created the three function objects, saved signatures/comments/tags, refreshed the queue to `6116/6116 = 100.00%`, and moved Wave911 focused re-audit progress to `206/1408 = 14.63%`. Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260528-054358_post_wave945_carver_vtable_boundary_review_verified`. Exact source virtual names, exact field/layout names, runtime wing/guide/render/attack behavior, BEA patching, and rebuild parity remain separate proof.

Wave965 (`carver-init-combat-wing-review-wave965`) re-reviewed the remaining Carver init/combat/wing helper band that Wave945 left as context. Fresh read-only exports verified `0x00422440 CCarver__Init`, `0x00422580 CCarverAI__dtor_base`, `0x00422620 CCarver__UpdateMotionAndWingPose`, `0x00422760 CCarverAI__OpenWings`, `0x004227a0 CCarverAI__CloseWings`, `0x004227e0 CCarverAI__OnHit`, `0x00422820 CCarverAI__Fire`, `0x00422930 CCarverAI__SetLastAttackTime`, `0x00422940 CCarverAI__IsRecentlyAttacked`, `0x004229b0 CarverAimGlobals__ResetVector`, and `0x004229d0 CarverAimGlobals__InitMatrix`, with CCarver vtable `0x005e0d90` continuity. No mutation was needed. Fresh exports verified `28` metadata rows, `28` tag rows, `46` xref rows, `4060` around-address instruction rows, `1522` body-instruction rows, `28` decompile rows, `128` CCarver vtable rows, and `4` Carver aim-global xref rows. Wave911 focused re-audit progress moved to `334/1408 = 23.72%`; static closure remains `6152/6152 = 100.00%`. Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260528-144929_post_wave965_carver_init_combat_wing_review_verified`. Runtime wing timing, damage, fire, aim, guide, render, or attack behavior; exact `CCarver`/`CCarverAI`/`CCarverGuide` layouts; exact source method or virtual names; BEA patching; and rebuild parity remain separate proof.

Wave989 (`carver-guide-lifecycle-review-wave989`) re-reviewed the CarverGuide lifecycle trio and Wave915 guide regression anchors. Fresh read-only exports verified `0x00422f90 CCarverGuide__ctor`, `0x00422fb0 CCarverGuide__scalar_deleting_dtor`, `0x00422fd0 CCarverGuide__dtor_base`, `0x00423490 CCarverGuide__HandleEvent`, and `0x00423510 CCarverGuide__AcquireNearestTargetReader`, plus context rows `0x00422440 CCarver__Init` and `0x004bac40 CMonitor__Shutdown`. Vtable type evidence resolves `0x005d947c` to `CCarverGuide`; vtable slots confirm `0x005d947c[0] -> CCarverGuide__HandleEvent`, `0x005d947c[1] -> CCarverGuide__scalar_deleting_dtor`, and `0x005e0d90[8] -> CCarver__Init`. No mutation was needed. Fresh exports verified `7` metadata rows, `7` tag rows, `121` xref rows, `238` body-instruction rows, `7` decompile rows, `256` vtable-slot rows, and `2` vtable-type rows. Wave911 focused re-audit progress is `438/1408 = 31.11%`; expanded static surface progress is `509/1478 = 34.44%`; static closure remains `6222/6222 = 100.00%`. Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260531-034107_post_wave989_carver_guide_lifecycle_review_verified`. Runtime CarverGuide navigation/targeting behavior, exact `CCarverGuide` layout, exact source method or virtual names, BEA patching, and rebuild parity remain separate proof.

Wave1125 (`wave1125-carver-targeting-current-risk-review`) re-read and tag-normalized `0x00422db0 CCarverAI__CheckNearbyEnemies` and `0x00423510 CCarverGuide__AcquireNearestTargetReader` as the score-23 Carver targeting current-risk cluster. Fresh Ghidra export evidence verified `2` metadata rows, `2` tag rows, `2` xref rows, `190` instruction rows, and `2` decompile rows; dry/apply/final-dry added `22 tags` with no rename, signature, comment, function-boundary, or executable-byte change. Current focused accounting is `135/1179 = 11.45%` of current focused candidates: 1179; static closure remains `6410/6410 = 100.00%` with `0 / 0 / 0` commentless / exact-undefined / `param_N` debt. Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260605-053504_post_wave1125_carver_targeting_current_risk_review_verified`; previous completed Ghidra review backup: `[maintainer-local-ghidra-backup-root]\BEA_20260605-050726_post_wave1124_repairpad_current_risk_review_verified`. Runtime Carver AI behavior, runtime CarverGuide navigation or target acquisition behavior, exact `CCarverAI`/`CCarverGuide` layouts, exact source-body identity, BEA patching, gameplay outcomes, visual QA, and rebuild parity remain separate proof.

Wave1129 (`wave1129-lifecycle-init-current-risk-review`) re-read and tag-normalized `0x00422440 CCarver__Init` and `0x00422970 CCarverAI__CanStartAttack` as part of a `5 rows` score-22 lifecycle/init current-risk cluster with fresh Ghidra export evidence. The same wave also covered `0x00405970 CDXCockpit__scalar_deleting_dtor`, `0x00421a80 CCarrier__Init`, and `0x00424710 CCockpit__scalar_deleting_dtor`. Current focused accounting is `155/1179 = 13.15%`; current focused candidates: 1178; live regenerated current focused candidates: 1178; remaining active focused work: 1024; static closure remains `6410/6410 = 100.00%` with `0 / 0 / 0` debt. Mutation status was comment/tag normalization (`69 tags`) with no rename, signature, function-boundary, or executable-byte change. Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260605-075206_post_wave1129_lifecycle_init_current_risk_review_verified`; previous completed backup: `[maintainer-local-ghidra-backup-root]\BEA_20260605-072044_post_wave1128_generalvolume_current_risk_review_verified`. Runtime Carver/CarverAI attack behavior, exact source-body identity, concrete layouts, BEA patching, gameplay outcomes, visual QA, and rebuild parity remain separate proof. Probe token anchor: Wave1129; wave1129-lifecycle-init-current-risk-review; 155/1179 = 13.15%; 5 rows; current focused candidates: 1178; live regenerated current focused candidates: 1178; remaining active focused work: 1024; score-22 lifecycle/init current-risk cluster; fresh Ghidra export; comment/tag normalization; 69 tags; 0 / 0 / 0; 0x00405970 CDXCockpit__scalar_deleting_dtor; 0x00421a80 CCarrier__Init; 0x00422440 CCarver__Init; 0x00422970 CCarverAI__CanStartAttack; 0x00424710 CCockpit__scalar_deleting_dtor; [maintainer-local-ghidra-backup-root]\BEA_20260605-075206_post_wave1129_lifecycle_init_current_risk_review_verified; [maintainer-local-ghidra-backup-root]\BEA_20260605-072044_post_wave1128_generalvolume_current_risk_review_verified.

## Functions

| Address | Name | Current saved signature | Evidence boundary |
|---------|------|-------------------------|-------------------|
| 0x00422440 | CCarver__Init | `void __thiscall CCarver__Init(void * this, void * init)` | Recovered boundary; init path calls base air-unit init, creates guide/AI-style helpers, starts launch animation, and seeds wing/attack state fields. |
| 0x00422560 | CCarverAI__scalar_deleting_dtor | `void * __thiscall CCarverAI__scalar_deleting_dtor(void * this, byte flags)` | Scalar-deleting destructor wrapper; corrects stale capitalized destructor label. |
| 0x00422580 | CCarverAI__dtor_base | `void __fastcall CCarverAI__dtor_base(void * this)` | Destructor-base cleanup context with monitor-style reader unlink/shutdown behavior. |
| 0x00422620 | CCarver__UpdateMotionAndWingPose | `void __fastcall CCarver__UpdateMotionAndWingPose(void * this)` | Recovered boundary; motion update and wing/blend pose context. |
| 0x00422750 | CCarver__Thunk_CallGuideVFunc08 | `void __fastcall CCarver__Thunk_CallGuideVFunc08(void * this)` | Wave945 recovered CCarver vtable slot 63 thunk; loads guide/controller pointer from `this+0x208` and tail-jumps guide vtable byte offset `+0x20` (slot 8). |
| 0x00422760 | CCarverAI__OpenWings | `void __fastcall CCarverAI__OpenWings(void * this)` | Wing-open animation helper. |
| 0x004227a0 | CCarverAI__CloseWings | `void __fastcall CCarverAI__CloseWings(void * this)` | Wing-close animation helper. |
| 0x004227e0 | CCarverAI__OnHit | `void __thiscall CCarverAI__OnHit(void * this, void * otherThing, void * collisionReport)` | Hit override with explicit stack arguments. |
| 0x00422820 | CCarverAI__Fire | `int __fastcall CCarverAI__Fire(void * this)` | Fire/animation helper; runtime weapon behavior remains unproven. |
| 0x004228b0 | CCarver__VFunc35_RenderWithFadeGlobal | `void __thiscall CCarver__VFunc35_RenderWithFadeGlobal(void * this, uint render_flags)` | Wave945 recovered CCarver vtable slot 35 render wrapper; compares `this+0x280` against `0x005d856c`, wraps `CThing__Render(this, render_flags | 0x40)` with global `0x0063012c`, and returns with `RET 0x4`. |
| 0x00422910 | CCarver__VFunc104_IsWingBlendAboveThreshold | `int __fastcall CCarver__VFunc104_IsWingBlendAboveThreshold(void * this)` | Wave945 recovered CCarver vtable slot 104 predicate; compares `this+0x280` against `0x005d856c` and returns `1` on the above-threshold path or `0` otherwise. |
| 0x00422930 | CCarverAI__SetLastAttackTime | `void __fastcall CCarverAI__SetLastAttackTime(void * this)` | Stores current global time into the last-attack timestamp field. |
| 0x00422940 | CCarverAI__IsRecentlyAttacked | `int __fastcall CCarverAI__IsRecentlyAttacked(void * this)` | Short cooldown predicate using the last-attack timestamp. |
| 0x00422970 | CCarverAI__CanStartAttack | `int __fastcall CCarverAI__CanStartAttack(void * this)` | Recovered boundary for attack-start predicate. |
| 0x004229b0 | CarverAimGlobals__ResetVector | `void __cdecl CarverAimGlobals__ResetVector(void)` | Recovered global helper boundary; resets Carver aim/vector globals. |
| 0x004229d0 | CarverAimGlobals__InitMatrix | `void __cdecl CarverAimGlobals__InitMatrix(void)` | Recovered global helper boundary; initializes Carver aim/orientation matrix globals. |
| 0x00422aa0 | CCarverAI__RefreshTargetReaderAndScheduleMove | `void __thiscall CCarverAI__RefreshTargetReaderAndScheduleMove(void * this, void * event)` | Recovered event-handler boundary; refreshes target reader and schedules movement/close-wing behavior. |
| 0x00422b90 | CCarverAI__UpdateAttackAndReschedule | `void __thiscall CCarverAI__UpdateAttackAndReschedule(void * this, void * event)` | Recovered event-handler boundary; updates target/attack state and reschedules event 3000. |
| 0x00422db0 | CCarverAI__CheckNearbyEnemies | `void __fastcall CCarverAI__CheckNearbyEnemies(void * this)` | Nearby-enemy scan / last-attack update helper. |
| 0x00422f90 | CCarverGuide__ctor | `void * __thiscall CCarverGuide__ctor(void * this, void * guideTarget)` | Guide constructor that delegates to the air-guide constructor path and installs the guide vtable. |
| 0x00422fb0 | CCarverGuide__scalar_deleting_dtor | `void * __thiscall CCarverGuide__scalar_deleting_dtor(void * this, byte flags)` | Scalar-deleting destructor wrapper; corrects stale capitalized destructor label. |
| 0x00422fd0 | CCarverGuide__dtor_base | `void __fastcall CCarverGuide__dtor_base(void * this)` | Guide destructor-base cleanup context. |
| 0x00423490 | CCarverGuide__HandleEvent | `void __thiscall CCarverGuide__HandleEvent(void * this, void * event)` | Recovered guide event-handler boundary; forwards non-target-refresh events to air-guide handling and reschedules target refresh. |
| 0x00423510 | CCarverGuide__AcquireNearestTargetReader | `void __fastcall CCarverGuide__AcquireNearestTargetReader(void * this)` | CarverGuide-specific nearest-target reader refresh; exact layout, runtime targeting behavior, and source identity remain unproven. |

## Wave965 Static Review Anchors

Wave965 was read-only and confirms the saved helper-band evidence remains coherent after the Wave945 vtable-boundary recovery:

| Anchor | Evidence |
| --- | --- |
| `0x00422667 CALL 0x00402fa0` | `CCarver__UpdateMotionAndWingPose` still calls `CUnit__UpdateMotionAndTrailEffects`. |
| `0x0042273b CALL [EDX + 0x70]` | Motion/wing update still dispatches the owner vfunc at byte offset `+0x70`. |
| `0x00422791 MOV [ESI + 0x27c], 0x1` | `CCarverAI__OpenWings` marks the wing state as opening after animation dispatch. |
| `0x004227d0 MOV [ESI + 0x27c], 0x2` | `CCarverAI__CloseWings` marks the wing state as closing after animation dispatch. |
| `0x0042281c RET 0x8` | `CCarverAI__OnHit` retains the two-stack-argument cleanup shape. |
| `0x0042282a CALL [EAX + 0x58]` | `CCarverAI__Fire` checks an owner readiness/fire-style vfunc before animation state changes. |
| `0x00422930 MOV [0x00672fd0]` and `0x00422935 MOV [ECX + 0x288]` | `CCarverAI__SetLastAttackTime` copies global time to the last-attack timestamp field. |
| `0x004229b0 MOV [0x00662c60]` | `CarverAimGlobals__ResetVector` resets the first aim/vector global. |
| `0x00422a07 MOV [0x00662c30]` | `CarverAimGlobals__InitMatrix` writes the first matrix/global slot. |

Probe token anchor: Wave965; carver-init-combat-wing-review-wave965; 0x00422440 CCarver__Init; 0x00422580 CCarverAI__dtor_base; 0x00422620 CCarver__UpdateMotionAndWingPose; 0x00422760 CCarverAI__OpenWings; 0x004227a0 CCarverAI__CloseWings; 0x004227e0 CCarverAI__OnHit; 0x00422820 CCarverAI__Fire; 0x00422930 CCarverAI__SetLastAttackTime; 0x00422940 CCarverAI__IsRecentlyAttacked; 0x004229b0 CarverAimGlobals__ResetVector; 0x004229d0 CarverAimGlobals__InitMatrix; 0x005e0d90; 334/1408 = 23.72%; 6152/6152 = 100.00%; [maintainer-local-ghidra-backup-root]\BEA_20260528-144929_post_wave965_carver_init_combat_wing_review_verified; no mutation.

Probe token anchor: Wave989; carver-guide-lifecycle-review-wave989; 0x00422f90 CCarverGuide__ctor; 0x00422fb0 CCarverGuide__scalar_deleting_dtor; 0x00422fd0 CCarverGuide__dtor_base; 0x00423490 CCarverGuide__HandleEvent; 0x00423510 CCarverGuide__AcquireNearestTargetReader; 438/1408 = 31.11%; 509/1478 = 34.44%; 6222/6222 = 100.00%; [maintainer-local-ghidra-backup-root]\BEA_20260531-034107_post_wave989_carver_guide_lifecycle_review_verified.

Probe token anchor: Wave1125; wave1125-carver-targeting-current-risk-review; 135/1179 = 11.45%; 2 rows; current focused candidates: 1179; score-23 Carver targeting current-risk cluster; fresh Ghidra export; tag-only normalization; 22 tags; Wave915; Wave965; Wave989; 0x00422db0 CCarverAI__CheckNearbyEnemies; 0x00423510 CCarverGuide__AcquireNearestTargetReader; [maintainer-local-ghidra-backup-root]\BEA_20260605-053504_post_wave1125_carver_targeting_current_risk_review_verified; [maintainer-local-ghidra-backup-root]\BEA_20260605-050726_post_wave1124_repairpad_current_risk_review_verified.

## Exception Handlers

Wave745 saved static Ghidra comments/tags/signatures for the Carver-region portion of the `unwind-continuation-wave745` tranche:

Anchor rows include `0x005d18b0 Unwind@005d18b0` through `0x005d1920 Unwind@005d1920`.

| Address | Name | Evidence boundary |
|---------|------|-------------------|
| 0x005d18b0 | Unwind@005d18b0 | DATA scope-table xref `0x0061a714`; calls `OID__FreeObject_Callback` on `EBP+4` with Carver.cpp debug path `0x00624400`, line `0x16`, memtype `0x17`. |
| 0x005d18c6 | Unwind@005d18c6 | DATA scope-table xref `0x0061a71c`; calls `OID__FreeObject_Callback` on `EBP+4` with Carver.cpp debug path `0x00624400`, line `0x17`, memtype `0x16`. |
| 0x005d18f0 | Unwind@005d18f0 | DATA scope-table xref `0x0061a744`; calls `CMonitor__Shutdown` on `EBP-0x10`. |
| 0x005d18f8 | Unwind@005d18f8 | DATA scope-table xref `0x0061a74c`; calls `CGenericActiveReader__dtor` on `*(EBP-0x10)+0xc`. |
| 0x005d1903 | Unwind@005d1903 | DATA scope-table xref `0x0061a754`; calls `CGenericActiveReader__dtor` on `*(EBP-0x10)+0x24`. |
| 0x005d1920 | Unwind@005d1920 | DATA scope-table xref `0x0061a77c`; calls `CMonitor__Shutdown_Thunk` on `EBP-0x10`. |

The full Wave745 tranche spans `0x005d1840 Unwind@005d1840` through `0x005d1a98 Unwind@005d1a98`, leaves raw commentless head `0x0042f220 CSPtrSet__Clear`, moves the high-signal head to `0x005d1aa3 Unwind@005d1aa3`, and has verified backup `[maintainer-local-ghidra-backup-root]\BEA_20260522-170426_post_wave745_unwind_continuation_verified`. Exact parent source-body identity, runtime exception behavior, runtime cleanup behavior, BEA patching, and rebuild parity remain unproven.

## Validation

Saved metadata, decompile, xref, and instruction read-back support the function boundaries summarized above.

## Notes

- The previous placeholder state is superseded by the Wave 318 saved-Ghidra mapping.
- These are public-safe summaries only; raw decompile excerpts and ignored proof JSON remain outside public release scope.
- Source absence means these labels should stay evidence-bounded until stronger source, vtable, runtime, or layout proof appears.

---

*Initial stub created 2025-12-16; refreshed by Wave 318 Ghidra Carrier/Carver correction on 2026-05-10.*
