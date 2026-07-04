# Wave1115 UnitAI/Carver Motion Activation Current-Risk Review Readiness Note

Status: complete static read-only Ghidra review
Date: 2026-06-05
Scope: `wave1115-unitai-carver-motion-activation-current-risk-review`

Wave1115 accounts for `13 rows` from the Wave1108 current focused denominator as the score-26 UnitAI/Carver motion/activation head. This pass used a fresh read-only Ghidra export and verified backup. It made no mutation, no executable-byte change, no BEA launch, and no installed-game/runtime-file mutation.

Accounting after Wave1115:

- Static Ghidra function-quality closure: `6410/6410 = 100.00%`.
- Commentless / exact-undefined / `param_N` debt: `0 / 0 / 0`.
- Expanded post-100 static surface: `1560/1560 = 100.00%`.
- Wave1108 current focused candidates: current focused candidates: 1179.
- Wave1108 current focused accounting: `56/1179 = 4.75%`.

Representative anchors:

| Address | Fresh read-back evidence |
| --- | --- |
| `0x00415140 CUnitAI__HandleLandedStateTransition` | DATA xref `0x005e2400`; landed trace path, `+0x12c`, and flag `+0x264`. |
| `0x00415a50 CUnitAI__CanCompleteDeployUndeployTransition` | DATA xref `0x005e23bc`; transition gates `+0x10c`, `+0x168`, `+0x214`, and `+0x2c`. |
| `0x00421c40 CUnit__ApplyFlag4DampingAndScaleSpeed` | DATA xref `0x005e2140`; flag-bit-4 path, `+0x11c`, and `CUnit__UpdateMotionAndTrailEffects`. |
| `0x00422620 CCarver__UpdateMotionAndWingPose` | DATA xref `0x005e0e94`; Carver motion update and wing/blend evidence. |
| `0x00422fd0 CCarverGuide__dtor_base` | Call xref from scalar-deleting dtor; active-reader removal and `CMonitor__Shutdown`. |
| `0x00428110 CUnitAI__UpdateActivationStateAndSpawnPickup` | Activation/pickup update with `Gill_M_Claw_Hit` and `CWorldPhysicsManager__CreatePickup`. |
| `0x00428500 CUnitAI__RefreshCachedComponentTransform` | Cached transform refresh with `DAT_008a9aac`, active-reader field `+0x26c`, and `Mat34__SetRows`. |
| `0x00428800 CUnitAI__HandleTriggerEventAndMoveToOffset` | Trigger/event and movement-offset helper with destroyed-state cleanup and active-reader path. |
| `0x004289b0 CUnitAI__AdvanceActivationAnimationState` | Activation animation state machine over saved animation tokens. |
| `0x00428b50 CUnit__SetReaderAndComputeRelativeYaw` | Call xref from `CUnit__Init`; active-reader storage and relative-yaw field `+0x274`. |
| `0x00428bc0 CUnitAI__GetTargetHeadingWithOffset` | Call xref from heading clamp helper; active-reader heading plus offset path. |
| `0x00428cb0 CUnitAI__PlayHitAnimationAndSetFlag` | Hit animation token and flag field `+0x2bc`. |
| `0x00429270 CUnitAI__UpdateHeadingTowardTargetClamped` | DATA xref `0x005d9660`; true entry `0x00429270` and `turnContext` load path. |

Read-back evidence:

- Fresh exports: `13` metadata rows, `13` tag rows, `20` xref rows, `1261` instruction rows, and `13` decompile rows.
- Export logs: `targets=13 found=13 missing=0`; `rows=13 missing=0`; `Wrote 20 rows`; `targets=13 missing=0`; `targets=13 dumped=13 missing=0 failed=0`.
- Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260605-010428_post_wave1115_unitai_carver_motion_activation_current_risk_review_verified`, `19` files, `175541127` bytes, `DiffCount=0`.
- Previous latest completed Ghidra review backup: `[maintainer-local-ghidra-backup-root]\BEA_20260604-200748_post_wave1100_cmeshpart_load_geometry_review_verified`.

Probe token anchor: Wave1115; wave1115-unitai-carver-motion-activation-current-risk-review; 56/1179 = 4.75%; 13 rows; current focused candidates: 1179; score-26 UnitAI/Carver motion/activation head; fresh read-only Ghidra export; no mutation; 0x00415140 CUnitAI__HandleLandedStateTransition; 0x00415a50 CUnitAI__CanCompleteDeployUndeployTransition; 0x00421c40 CUnit__ApplyFlag4DampingAndScaleSpeed; 0x00422620 CCarver__UpdateMotionAndWingPose; 0x00422fd0 CCarverGuide__dtor_base; 0x00428110 CUnitAI__UpdateActivationStateAndSpawnPickup; 0x00428500 CUnitAI__RefreshCachedComponentTransform; 0x00428800 CUnitAI__HandleTriggerEventAndMoveToOffset; 0x004289b0 CUnitAI__AdvanceActivationAnimationState; 0x00428b50 CUnit__SetReaderAndComputeRelativeYaw; 0x00428bc0 CUnitAI__GetTargetHeadingWithOffset; 0x00428cb0 CUnitAI__PlayHitAnimationAndSetFlag; 0x00429270 CUnitAI__UpdateHeadingTowardTargetClamped; [maintainer-local-ghidra-backup-root]\BEA_20260605-010428_post_wave1115_unitai_carver_motion_activation_current_risk_review_verified; [maintainer-local-ghidra-backup-root]\BEA_20260604-200748_post_wave1100_cmeshpart_load_geometry_review_verified.

Boundary: this is static read-only Ghidra evidence only. Runtime AI behavior, runtime movement behavior, runtime steering behavior, runtime Carver behavior, exact concrete layouts, exact source-body identity, BEA patching behavior, gameplay outcomes, visual QA, and rebuild parity remain separate proof.
