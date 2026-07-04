# Ghidra CUnitAI Activation Lifecycle Review Wave938 Readiness

Status: complete read-only static read-back evidence
Date: 2026-05-28
Scope: `cunitai-activation-lifecycle-review-wave938`

Wave938 re-reviewed the CUnitAI activation/lifecycle mini-island selected from the Wave911 risk-ranked continuation queue after a Composer 2.5 consult and fresh Ghidra exports. The cluster ties component activation, cached component transforms, trigger-driven unit cleanup/movement, activation animation state, hit-animation dispatch, and CUnit child/deploy/destruction context. Fresh evidence matched the saved correction boundary and did not justify a mutation. This wave made no Ghidra mutation, no rename, no signature change, no function-boundary change, and no executable-byte change.

Primary targets:

| Address | Saved row | Read-back evidence |
| --- | --- | --- |
| `0x00428110` | `CUnitAI__UpdateActivationStateAndSpawnPickup` | Handles activation/deactivation animation tokens, crash/explosion fall checks, `Gill_M_Claw_Hit` pickup lookup, `CWorldPhysicsManager__CreatePickup`, `CUnit__UpdateMotionAttachmentsAndEffects`, and randomized cached-transform refresh through `CUnitAI__RefreshCachedComponentTransform`. |
| `0x00428500` | `CUnitAI__RefreshCachedComponentTransform` | Skips when cached tick `this+0x278` equals `DAT_008a9aac`, derives orientation from `this+0x250/+0x254`, optionally reads component transform through an active reader, and writes rows through `Mat34__SetRows`. |
| `0x00428800` | `CUnitAI__HandleTriggerEventAndMoveToOffset` | Calls `CUnit__MarkDestroyedAndCleanupLinks`, optionally `CUnit__ResetDeploymentGraphAndScheduleEvent`, `CUnit__ReleaseChildUnits`, active-reader movement callbacks, and scheduler helper `0x0044b370`. |
| `0x004289b0` | `CUnitAI__AdvanceActivationAnimationState` | Compares current animation indexes against `Hit`, `retract`, `normal`, `Activate`, `Activated`, and `Deactivated` tokens, updates activation fields, and falls back to `CUnitAI__HandleDeployAndFireAnimationCompletion`. |
| `0x00428cb0` | `CUnitAI__PlayHitAnimationAndSetFlag` | Looks up and plays the `Hit` animation through vtable dispatch and sets activation/hit field `+0x2bc` to `1`. |

Context anchors:

- `0x00428d50 CUnitAI__PlayActivateAnimationOrFinalizeActivated` resolves the `Activate` animation token, finalizes activation immediately when missing, or plays it through vtable slot `+0xf0`.
- `0x00428b50 CUnit__SetReaderAndComputeRelativeYaw` remains the active-reader setter/yaw context, reached from `CUnit__Init`.
- `0x004fa8d0 CUnit__UpdateMotionAttachmentsAndEffects` is called by `CUnitAI__UpdateActivationStateAndSpawnPickup` and remains the broader CUnit motion/effect attachment context.
- `0x004fcfe0 CUnit__ReleaseChildUnits`, `0x004fd040 CUnit__ResetDeploymentGraphAndScheduleEvent`, and `0x004fd140 CUnit__MarkDestroyedAndCleanupLinks` preserve the shared CUnit child/deploy/destroy lifecycle context used by the trigger helper.

Fresh read-back evidence:

- Primary exports: 5 metadata rows, 5 tag rows, 11 xref rows, 726 instruction rows, and 5 decompile rows.
- Context exports: 6 metadata rows, 6 tag rows, 35 xref rows, 964 instruction rows, and 6 decompile rows.
- Primary xrefs confirm activation/update DATA refs at `0x005e4300/0x005e3e48`, cached-transform callers from render-position/orientation helpers and the activation updater, trigger/event DATA refs at `0x005e42c0/0x005e3e08`, activation-animation DATA refs at `0x005e4088/0x005e3e2c`, and the hit-animation helper caller `CGillM__TriggerRandomArmHitAnimationIfReady`.
- Context xrefs confirm the join to `CUnit__Init`, `CUnitAI__UpdateActivationStateAndSpawnPickup`, `CUnitAI__HandleTriggerEventAndMoveToOffset`, `CUnit__TryDestroyedCleanupAndResetDeploymentGraph`, `CGroundUnit__MarkDestroyedAndResetState`, and selected Unit DATA vtable refs.
- Verified read-only backup: `[maintainer-local-ghidra-backup-root]\BEA_20260528-021545_post_wave938_cunitai_activation_lifecycle_review_verified`, 19 files, 173247367 bytes, `DiffCount=0`.

Progress:

- Wave911 focused re-audit progress after Wave938: `166/1408 = 11.79%`.
- Static export-contract function-quality closure remains `6113/6113 = 100.00%`.

Probe token anchor: Wave938; `cunitai-activation-lifecycle-review-wave938`; `0x00428110 CUnitAI__UpdateActivationStateAndSpawnPickup`; `0x00428500 CUnitAI__RefreshCachedComponentTransform`; `0x00428800 CUnitAI__HandleTriggerEventAndMoveToOffset`; `0x004289b0 CUnitAI__AdvanceActivationAnimationState`; `0x00428cb0 CUnitAI__PlayHitAnimationAndSetFlag`; `0x00428d50 CUnitAI__PlayActivateAnimationOrFinalizeActivated`; `0x00428b50 CUnit__SetReaderAndComputeRelativeYaw`; `0x004fa8d0 CUnit__UpdateMotionAttachmentsAndEffects`; `0x004fcfe0 CUnit__ReleaseChildUnits`; `0x004fd040 CUnit__ResetDeploymentGraphAndScheduleEvent`; `0x004fd140 CUnit__MarkDestroyedAndCleanupLinks`; `166/1408 = 11.79%`; `6113/6113 = 100.00%`; `[maintainer-local-ghidra-backup-root]\BEA_20260528-021545_post_wave938_cunitai_activation_lifecycle_review_verified`; no mutation.

What this proves:

- The CUnitAI activation/lifecycle rows remain present in the saved Ghidra project with the expected names, signatures, comments, xrefs, tags, and decompile outputs.
- The static join between activation animation handling, component transform caching, pickup creation, hit-animation dispatch, trigger-driven lifecycle cleanup, child release, deploy-graph reset, and destruction cleanup remains coherent.
- No current Wave938 evidence justifies a rename, signature correction, function-boundary change, or executable-byte change.

What remains unproven:

- Exact source-body identity.
- Complete CUnitAI, CUnit, active-reader, animation, component-transform, child/deploy/destruction layouts.
- Runtime activation behavior.
- Runtime pickup behavior.
- Runtime trigger behavior.
- Runtime movement behavior.
- Runtime destruction/deploy event behavior.
- BEA patching behavior.
- Rebuild parity.
