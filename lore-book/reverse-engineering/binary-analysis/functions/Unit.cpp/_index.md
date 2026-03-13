# Unit.cpp Functions

> Source File: Unit.cpp | Binary: BEA.exe

## Overview

Core unit gameplay mechanics for all interactive actors in the game (mechs, vehicles, infantry, emplacements). This file handles initialization, damage calculation, position/rotation updates, and visual/audio effects tied to unit state.

## Functions

| Address | Name | Purpose | Size |
|---------|------|---------|------|
| 0x004f86d0 | [CUnit__Init](./CUnit__Init.md) | Spawning, weapons, turrets, equipment setup | ~2KB |
| 0x004f9a90 | [CUnit__ApplyDamage](./CUnit__ApplyDamage.md) | Damage handler with shields/armor/character effects | ~900 bytes |
| 0x004fc4e0 | [CUnit__UpdateTransform](./CUnit__UpdateTransform.md) | World-space position/rotation calculation | ~400 bytes |
| 0x004fe030 | [CUnit__TriggerEffect](./CUnit__TriggerEffect.md) | Sound/visual effects based on health state | ~500 bytes |
| 0x00428500 | CUnitAI__RefreshCachedComponentTransform | Refreshes cached component transform state used by AI heading/activation updates | ~140 bytes |
| 0x004289b0 | CUnitAI__AdvanceActivationAnimationState | Advances AI activation animation state and returns transition result | ~528 bytes |
| 0x00428bc0 | CUnitAI__GetTargetHeadingWithOffset | Computes target heading with runtime offset bias | ~704 bytes |
| 0x00429280 | CUnitAI__UpdateHeadingTowardTargetClamped | Updates heading toward target under clamped turn-rate logic | ~1248 bytes |

## Headless Semantic Wave108 Promotions (2026-02-26)

| Address | Name | Notes |
|---------|------|-------|
| 0x0042ee90 | CUnitAI__CreateAndRegisterByName | Allocates/initializes a `0x1ac` AI object by name and registers it in the global AI set. |
| 0x0042efd0 | CUnitAI__InitDefaults | Constructor-style defaults initializer for CUnitAI runtime fields, thresholds, and owned key string (`\"m_b_rubble\"`). |

## Headless Semantic Wave109 Promotions (2026-02-26)

| Address | Name | Notes |
|---------|------|-------|
| 0x00415970 | CUnitAI__HandleDeployUndeployAnimationCompletion | Handles deploy/undeploy animation completion transition and returns completion status to caller state flow. |
| 0x00424a20 | CUnitAI__UpdateDeployAimAndScheduleEvent | Updates deploy-aim progression and schedules follow-up deploy timing event. |
| 0x00424be0 | CUnitAI__AdvanceDeployAnimationPhase | Advances deploy animation phase state machine to the next phase. |
| 0x00425760 | CUnitAI__OrthonormalizeMat34Axes | Re-orthonormalizes mat34 basis vectors for stable AI orientation transforms. |
| 0x0042f280 | CUnitAI__ComputeRecursiveNodeSize_Base8 | Computes recursive node-size totals using base element size 8 bytes. |

## Headless Semantic Wave110 Promotions (2026-02-26)

| Address | Name | Notes |
|---------|------|-------|
| 0x00415780 | CUnitAI__PlayDeployingAnimationIfState0 | If transition state is `0`, plays `"deploying"` animation and sets state to `1`. |
| 0x004157c0 | CUnitAI__PlayUndeployingAnimation | Resets deploy timer field and plays `"undeploying"` animation. |
| 0x00445570 | CUnitAI__PlayOpenAnimationIfState1Or3 | Gate on states `1/3`, then plays `"open"` animation and sets state to `2`. |
| 0x004455c0 | CUnitAI__PlayCloseAnimationIfState0Or2 | Gate on states `0/2`, then plays `"close"` animation and sets state to `3`. |
| 0x00445610 | CUnitAI__AdvanceOpenCloseShootAnimationState | Animation-state stepper that transitions between `"open"`, `"close"`, and `"shoot"` phases by current index checks. |

## Headless Semantic Wave111 Promotions (2026-02-26)

| Address | Name | Notes |
|---------|------|-------|
| 0x00415a50 | CUnitAI__CanCompleteDeployUndeployTransition | Returns ready/true when deploy/undeploy transition animation has completed and gating flags allow finalization. |
| 0x00424ca0 | CUnitAI__UpdateDeployTrackingTransformTowardTarget | Updates deploy tracking transform toward target orientation with clamped angular adjustments. |
| 0x004250f0 | CUnitAI__DecayDeployTrackingTransformToNeutral | Relaxes tracking angles toward neutral and rebuilds orientation transform from decayed values. |
| 0x00430b30 | CUnitAI__ComputeRecursiveNodeSize_NodeTreeA | Recursive node-tree size accumulator (`node + 0xC + child`). |
| 0x00431470 | CUnitAI__ComputeRecursiveNodeSize_NodeTreeB | Recursive node-tree size accumulator variant for adjacent tree chain. |

## Headless Semantic Wave112 Promotions (2026-02-26)

| Address | Name | Notes |
|---------|------|-------|
| 0x004015e0 | CUnit__IntegrateVelocityAndResolveGroundCollision | Integrates velocity, resolves ground collision response, and updates map-entry position records. |
| 0x00403690 | CUnit__ReleaseAllAttachedParticleNodes | Releases both attached particle-node sets and frees each node object. |
| 0x00408150 | CUnit__ProcessStateSwapAndDeathChecks | Runs state-swap helper and applies flag/altitude-driven death/pickup checks before shared post-step helper call. |
| 0x004318c0 | CUnitAI__ComputeRecursiveNodeSize_NodeTreeC | Third recursive node-tree size accumulator variant (`node + 0xC + child`). |

## Headless Semantic Wave113 Promotions (2026-02-26)

| Address | Name | Notes |
|---------|------|-------|
| 0x004178a0 | CUnit__ProcessClosingAndUnshuttingAnimations | Handles closing/unshutting animation transitions with timer + state gating. |
| 0x004239f0 | CUnitAI__InitDefaults_AutoConfigTestPath | Constructor-style defaults initializer that stores `c:\\beaautoconfigtest\\` path in object state. |
| 0x00428c70 | CUnitAI__RunSharedStepAndMaybeTriggerFlag4Action | Runs shared step helper and conditionally invokes flag-4 action callback. |
| 0x00428cf0 | CUnitAI__ForwardCommandToAttachedNodeThenDispatch | Forwards command to attached node when eligible and then performs common dispatch helper path. |

## Headless Semantic Wave114 Promotions (2026-02-26)

| Address | Name | Notes |
|---------|------|-------|
| 0x0040e8e0 | CUnit__IsNearGroundByTerrainProbe | Terrain/shadow-height probe gate that returns boolean-like near-ground state from height-threshold comparison. |
| 0x0040eeb0 | CUnit__FinishedPlayingCurrentAnimation | Transition-completion helper that checks `flytowalk`/`walktofly` animation indices and dispatches the corresponding next-mode set call. |

## Headless Semantic Wave115 Promotions (2026-02-26)

| Address | Name | Notes |
|---------|------|-------|
| 0x00447ac0 | CUnitAI__PlayWingFoldedAnimationAndSetState3 | Plays `"wingfolded"` animation, resets cached-anchor enable flag, and sets door/wing state machine to state `3`. |
| 0x00447b10 | CUnitAI__PlayWingUnfoldedAnimationAndSetState5 | Plays `"wingunfolded"` animation and sets door/wing state machine to state `5`. |
| 0x00447b60 | CUnitAI__HasReachedCachedAnchorPoint | Returns true when XY distance to cached anchor point (`+0x280/+0x284`) is below arrival threshold. |
| 0x00447bb0 | CUnitAI__GetOrGenerateCachedAnchorPoint | Returns cached anchor point or generates one via bounded randomized search until validity check passes. |
| 0x00447fa0 | CUnitAI__AdvanceDoorWingAnimationState | Advances door/wing animation chain (`dooropening/dooropen/doorclosing/doorclosed/wing*`) and dispatches transition callbacks. |

## Headless Semantic Wave116 Promotions (2026-02-26)

| Address | Name | Notes |
|---------|------|-------|
| 0x00445ad0 | CUnitAI__UpdateDoorWingEngagement_CloseRange | Close-range engagement updater that toggles open/close animation paths and movement offsets around target proximity thresholds. |
| 0x00445f40 | CUnitAI__UpdateDoorWingEngagement_MidRange | Mid-range engagement updater that evaluates planar distance/angle and chooses direct reposition vs helper-driven tracking update. |
| 0x00446150 | CUnitAI__UpdateDoorWingEngagement_LongRange | Long-range engagement updater that applies standoff thresholds, executes open/close transitions, and updates movement target. |
| 0x00446400 | CUnitAI__EnterDoorWingOpenTrackingState | Enters/maintains open-tracking mode, randomizes follow distance threshold, and triggers open-animation path when target exists. |

## Headless Semantic Wave117 Promotions (2026-02-26)

| Address | Name | Notes |
|---------|------|-------|
| 0x00444f00 | CUnitAI__CallIndexedEntryVFunc10 | Resolves indexed entry pointer and calls entry vfunc slot `+0x10` when present. |
| 0x00447a40 | CUnitAI__SetDoorWingState2AndClampYawDelta | Enters state `2` and clamps yaw-delta field around configured bounds when transition gating passes. |
| 0x004480c0 | CUnitAI__CanContinueDoorWingTransition | Returns true when anchor/target/state gates allow door-wing transition continuation. |
| 0x00448110 | CUnitAI__SetDoorWingState6 | Writes door-wing state field `+0x27c` to state `6`. |
| 0x00448120 | CUnitAI__SetDoorWingState7AndMirrorYawOffset | Writes state `7` and mirrors yaw-offset field around a constant pivot. |

## Headless Semantic Wave118 Promotions (2026-02-27)

| Address | Name | Notes |
|---------|------|-------|
| 0x0044d1f0 | CUnitAI__RunHelper2000AndDispatchVFunc0x38IfFlag4 | Runs shared helper `0x00402000` then dispatches vfunc slot `+0x38` when bit-flag `0x4` is set. |
| 0x0044d210 | CUnitAI__RenderWithStaticShadowVisibilityUpdate | Updates static-shadow visibility gate (`CStaticShadows__UpdateVisibility`) then forwards to `CThing__Render`. |

## Headless Semantic Wave119 Promotions (2026-02-27)

| Address | Name | Notes |
|---------|------|-------|
| 0x00444f20 | CUnitAI__CanUseIndexedSegmentEntry | Indexed segment-entry eligibility predicate that resolves per-index pointers and enforces segment/core-child gates before permitting continuation. |
| 0x0044cd20 | CUnitAI__DecayEngagementMetricAndMaybeTriggerVFunc200 | Decays engagement metric field, dispatches vfunc slot `+0x200` under threshold/flag conditions, and clamps against profile maximum. |
| 0x00440b70 | CUnitAI__ResetPrimaryAndTailSentinels | Clears a primary state word and trailing sentinel field (`+0x1588c`) used by this AI object family. |

## Headless Semantic Wave122 Promotions (2026-02-27)

| Address | Name | Notes |
|---------|------|-------|
| 0x0047c040 | CUnitAI__AdvanceCloseShootAnimationState | Advances close/shoot animation transition state by current animation index and writes door/wing state field `+0x27c`. |

## Key Observations

- **CUnit is base class** for all interactive actors - player mech, enemies, vehicles, infantry, etc.
- **Damage system** uses shield/armor subsystem with character-specific multipliers
- **Transform system** integrates with collision and physics
- **Effects system** is data-driven - health state triggers visual/audio events
- **Weapons integration** - each unit may have multiple weapons, turrets, targeting

## Related Files

- Career.cpp - Kill tracking (TK_AIRCRAFT, TK_VEHICLES, TK_MECHS, TK_INFANTY (typo), TK_EMPLACEMENTS)
- Mech.cpp - Player mech subclass (extends CUnit with cockpit/camera/targeting)
- Player.cpp - Player-specific god mode and vulnerability flags
- BattleEngine.cpp - SetVulnerable(), SetInfinateEnergy() calls from units

---
*Migrated from ghidra-analysis.md (Dec 2025)*
