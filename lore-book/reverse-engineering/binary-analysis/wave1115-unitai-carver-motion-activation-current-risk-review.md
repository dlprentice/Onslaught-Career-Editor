# Wave1115 UnitAI/Carver Motion Activation Current-Risk Review

Status: complete static read-only Ghidra review
Last updated: 2026-06-05
Scope: `wave1115-unitai-carver-motion-activation-current-risk-review`

Wave1115 re-read `13 rows` from the Wave1108 current focused denominator: the score-26 UnitAI/Carver motion/activation head after Wave1109 through Wave1114 are subtracted. This wave uses a fresh read-only Ghidra export and a verified Ghidra project backup. It made no mutation, no executable-byte change, no BEA launch, and no installed-game/runtime-file mutation.

## Accounting

| Track | Current |
| --- | ---: |
| Static Ghidra function-quality closure | `6410/6410 = 100.00%` |
| Commentless / exact-undefined / `param_N` debt | `0 / 0 / 0` |
| Expanded post-100 static surface | `1560/1560 = 100.00%` |
| Wave1108 current focused candidates | current focused candidates: 1179 |
| Wave1115 current focused review accounting | `56/1179 = 4.75%` |

## Reviewed Rows

| Address | Saved row | Fresh read-back evidence |
| --- | --- | --- |
| `0x00415140 CUnitAI__HandleLandedStateTransition` | `void __fastcall CUnitAI__HandleLandedStateTransition(void * unitAI)` | DATA xref `0x005e2400`; decompile keeps the landed trace path, field `+0x12c` clear, vfunc dispatches, and flag `+0x264` set. |
| `0x00415a50 CUnitAI__CanCompleteDeployUndeployTransition` | `int __fastcall CUnitAI__CanCompleteDeployUndeployTransition(void * unitAI)` | DATA xref `0x005e23bc`; decompile checks vfunc `+0x10c`, gates `+0x168/+0x214`, and flag byte `+0x2c`. |
| `0x00421c40 CUnit__ApplyFlag4DampingAndScaleSpeed` | `void __fastcall CUnit__ApplyFlag4DampingAndScaleSpeed(void * this)` | DATA xref `0x005e2140`; decompile reads flag bit `0x04`, scales field `+0x11c`, and calls `CUnit__UpdateMotionAndTrailEffects`. |
| `0x00422620 CCarver__UpdateMotionAndWingPose` | `void __fastcall CCarver__UpdateMotionAndWingPose(void * this)` | DATA xref `0x005e0e94`; decompile preserves Carver motion/wing blend evidence with field `+0x280` and `CUnit__UpdateMotionAndTrailEffects`. |
| `0x00422fd0 CCarverGuide__dtor_base` | `void __fastcall CCarverGuide__dtor_base(void * this)` | Call xref from `0x00422fb3 CCarverGuide__scalar_deleting_dtor`; decompile removes the active-reader slot at `+0x2c` and calls `CMonitor__Shutdown`. |
| `0x00428110 CUnitAI__UpdateActivationStateAndSpawnPickup` | `void __fastcall CUnitAI__UpdateActivationStateAndSpawnPickup(void * this)` | DATA xrefs `0x005e4300/0x005e3e48`; decompile keeps `Gill_M_Claw_Hit`, `CWorldPhysicsManager__CreatePickup`, and activation tokens. |
| `0x00428500 CUnitAI__RefreshCachedComponentTransform` | `void __fastcall CUnitAI__RefreshCachedComponentTransform(void * this)` | Calls from render-cache helpers and activation update; decompile keeps `DAT_008a9aac`, active-reader field `+0x26c`, and `Mat34__SetRows`. |
| `0x00428800 CUnitAI__HandleTriggerEventAndMoveToOffset` | `bool __fastcall CUnitAI__HandleTriggerEventAndMoveToOffset(void * this)` | DATA xrefs `0x005e42c0/0x005e3e08`; decompile keeps `CUnit__MarkDestroyedAndCleanupLinks` and active-reader offset handling. |
| `0x004289b0 CUnitAI__AdvanceActivationAnimationState` | `bool __fastcall CUnitAI__AdvanceActivationAnimationState(void * this)` | DATA xrefs `0x005e4088/0x005e3e2c`; decompile keeps activation animation token/state evidence including `Activate` and field `+0x264`. |
| `0x00428b50 CUnit__SetReaderAndComputeRelativeYaw` | `void __thiscall CUnit__SetReaderAndComputeRelativeYaw(void * this, void * reader, void * readerContext, int unusedMode)` | Call xref from `0x004f8d7c CUnit__Init`; decompile keeps active-reader field `+0x26c` and relative-yaw field `+0x274`. |
| `0x00428bc0 CUnitAI__GetTargetHeadingWithOffset` | `double __fastcall CUnitAI__GetTargetHeadingWithOffset(void * this)` | Call xref from `0x004292c7 CUnitAI__UpdateHeadingTowardTargetClamped`; decompile keeps the active-reader heading path. |
| `0x00428cb0 CUnitAI__PlayHitAnimationAndSetFlag` | `void __fastcall CUnitAI__PlayHitAnimationAndSetFlag(void * this)` | Call xref from `0x00479eb6 CGillM__TriggerRandomArmHitAnimationIfReady`; decompile keeps the `Hit` token and flag field `+0x2bc`. |
| `0x00429270 CUnitAI__UpdateHeadingTowardTargetClamped` | `void __fastcall CUnitAI__UpdateHeadingTowardTargetClamped(void * turnContext)` | DATA xref `0x005d9660`; decompile starts at true entry `0x00429270` and keeps the `turnContext`/active-reader heading path. |

Read-back evidence:

- Fresh read-only exports: `13` metadata rows, `13` tag rows, `20` xref rows, `1261` instruction rows, and `13` decompile rows.
- Logs report `targets=13 found=13 missing=0`, `rows=13 missing=0`, `Wrote 20 rows`, `targets=13 missing=0`, and `targets=13 dumped=13 missing=0 failed=0`.
- Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260605-010428_post_wave1115_unitai_carver_motion_activation_current_risk_review_verified`, `19` files, `175541127` bytes, `DiffCount=0`.
- Previous latest completed Ghidra review backup was `[maintainer-local-ghidra-backup-root]\BEA_20260604-200748_post_wave1100_cmeshpart_load_geometry_review_verified`.

Probe token anchor: Wave1115; wave1115-unitai-carver-motion-activation-current-risk-review; 56/1179 = 4.75%; 13 rows; current focused candidates: 1179; score-26 UnitAI/Carver motion/activation head; fresh read-only Ghidra export; no mutation; 0x00415140 CUnitAI__HandleLandedStateTransition; 0x00415a50 CUnitAI__CanCompleteDeployUndeployTransition; 0x00421c40 CUnit__ApplyFlag4DampingAndScaleSpeed; 0x00422620 CCarver__UpdateMotionAndWingPose; 0x00422fd0 CCarverGuide__dtor_base; 0x00428110 CUnitAI__UpdateActivationStateAndSpawnPickup; 0x00428500 CUnitAI__RefreshCachedComponentTransform; 0x00428800 CUnitAI__HandleTriggerEventAndMoveToOffset; 0x004289b0 CUnitAI__AdvanceActivationAnimationState; 0x00428b50 CUnit__SetReaderAndComputeRelativeYaw; 0x00428bc0 CUnitAI__GetTargetHeadingWithOffset; 0x00428cb0 CUnitAI__PlayHitAnimationAndSetFlag; 0x00429270 CUnitAI__UpdateHeadingTowardTargetClamped; [maintainer-local-ghidra-backup-root]\BEA_20260605-010428_post_wave1115_unitai_carver_motion_activation_current_risk_review_verified; [maintainer-local-ghidra-backup-root]\BEA_20260604-200748_post_wave1100_cmeshpart_load_geometry_review_verified.

## Boundary

This wave closes current-risk accounting for these thirteen rows only. It proves saved static Ghidra metadata/tag/xref/instruction/decompile read-back, not runtime AI behavior, runtime movement behavior, runtime steering behavior, runtime Carver behavior, exact concrete layouts, exact source-body identity, BEA patching behavior, gameplay outcomes, visual QA, or rebuild parity.
