# Cannon.cpp Functions

> Source File: Cannon.cpp | Binary: BEA.exe
> Debug Path: 0x00623dd4

> **Queue status (2026-05-26):** Ghidra export-contract closure **6113/6113** (Wave900: every function commented; clean-signature proxy; not evidence-grade semantics). Lines below that reference a "next raw commentless" row are **archival wave progress**, not open work.

## Overview

Cannon/turret implementation evidence. Current tracked repo source does not include the `Cannon.cpp` body, so this page records retail Ghidra read-back for saved Cannon names, signatures, comments, vtable ownership, and bounded behavior notes. It should not be read as complete source parity or runtime firing proof.

Wave906 (`unit-battleengine-gameplay-static-review-wave906`) records a `static-coherent Unit/BattleEngine/gameplay core` after export-contract queue closure `6113/6113 = 100.00%` (static review slice only): `633` rows across `75` families, including `CUnit` `90`, `CUnitAI` `63`, `CBattleEngine` `47`, `CSquadNormal` `31`, `CBattleEngineWalkerPart` `27`, `CBattleEngineJetPart` `23`, `CGeneralVolume` `23`, `CDestructableSegmentsController` `19`, and `CCollisionSeekingRound` `17`; anchors include `CUnit__ApplyDamage`, `CUnitAI__UpdateActivationStateAndSpawnPickup`, `CBattleEngine__UpdateAutoTargetSetAndFireProjectiles`, `CBattleEngine__AddProjectile`, `CBattleEngine__Morph`, `CBattleEngine__HandleCloak`, `CBattleEngine__AugmentWeapon`, `CBattleEngineJetPart__WeaponFired`, `CBattleEngineWalkerPart__WeaponFired`, `CWeapon__HandleFireBurstEvent`, `CRound__SpawnConfiguredProjectile`, `CSpawnerThng__DoSpawn`, and `CDestroyableSegment__VFunc_03_ApplyDamage`. Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260526-105331_post_wave906_unit_battleengine_gameplay_static_review_verified`.

Wave992 (`cannon-turret-activation-review-wave992`, `wave992-readback-verified`) re-audited the Cannon activation/update/cleanup/target-selection cluster after the Wave900-Wave991 recheck gate and saved seven comment/tag normalizations without renames, signature changes, function-boundary changes, executable-byte changes, BEA launch, or runtime/game-file mutation. It keeps this page tied to current retail Ghidra evidence: `0x0041b370 CCannon__UpdateState` calls `0x0047c970 CGroundUnit__UpdateLinkedEffectsByHeightClearance` from both activation paths; `0x0041b590 CCannon__VFuncSlot_50_MarkDestroyedResetDeployGraph` calls `0x0047ce80 CGroundUnit__MarkDestroyedAndResetState`; `0x0041b1a0 CCannon__Init` calls `0x00495230 CMCCannon__Ctor`; and `0x004fd4d0 CCannon__SelectTarget` falls back through `CThing__GetCentrePos` when no linked target exists. Queue closure remains `6222/6222 = 100.00%`; Wave911 focused re-audit progress is `446/1408 = 31.68%`; expanded static surface progress is `538/1478 = 36.40%`. Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260531-053822_post_wave992_cannon_turret_activation_review_verified`. Runtime turret activation behavior, runtime firing behavior, exact `CCannon`/`CGroundUnit`/`CMCCannon` layouts, exact source-body or virtual-method identity, BEA patching, and rebuild parity remain separate proof.

## Functions

| Address | Name | Purpose | Size |
|---------|------|---------|------|
| 0x0041b1a0 | CCannon__Init | Initialize Cannon state/effects and occupancy-grid registration | ~450 bytes |
| 0x0041b370 | CCannon__UpdateState | Update activation enable/target-controller state and linked effects | ~220 bytes |
| 0x0041b450 | CCannon__VFuncSlot_02_RemoveFromWorldAndForward | Remove from occupancy-grid state and forward slot-2 teardown/remove behavior | ~30 bytes |
| 0x0041b470 | CCannon__AdvanceActivationAnimationState | Advance Activate/Deactivate transitions to Active/Inactive state | ~200 bytes |
| 0x0041b540 | CCannon__GetMidpoint | Calculate an output midpoint from selected target and this position | ~80 bytes |
| 0x0041b590 | CCannon__VFuncSlot_50_MarkDestroyedResetDeployGraph | Mark destroyed/reset Cannon state and reset the unit deployment graph | ~50 bytes |

## Related Retail Helpers

| Address | Name | Purpose | Boundary |
|---------|------|---------|----------|
| 0x0047c970 | CGroundUnit__UpdateLinkedEffectsByHeightClearance | Samples world height, updates linked-effect fields, and refreshes motion/attachments | Wave 392 owner correction; `CGroundUnit` vtable slot `66`, reused by Cannon/GroundVehicle subclass paths |
| 0x0047ce80 | CGroundUnit__MarkDestroyedAndResetState | Calls unit destruction cleanup, clears field `+0x25c` on success, returns success flag | Wave 392 owner correction; `CGroundUnit` vtable slot `50`, reused by Cannon/GroundVehicle subclass paths |
| 0x004fd4d0 | CCannon__SelectTarget | Writes `outTargetPosition` from linked target or this unit targeting position | Exact source method name and runtime target semantics open |

## Wave992 Cannon/Turret Activation Re-Audit

Wave992 saved refreshed comments and tags for the seven primary Cannon rows below:

| Address | Static read-back evidence |
| --- | --- |
| `0x0041b1a0 CCannon__Init` | Calls `CGroundUnit__Init`, chooses Active/Inactive animation state from `+0x214`, allocates/stores helper objects at `+0x208/+0x13c/+0x70`, seeds state/timestamp fields `+0x260/+0x264`, registers with world occupancy grid, and sets height-threshold flag `+0x258`. |
| `0x0041b370 CCannon__UpdateState` | Tests enable/target-controller state through `+0x214/+0x13c`, requests Activate/Deactivate animations, updates state/timestamp fields, and calls `CGroundUnit__UpdateLinkedEffectsByHeightClearance` in both active and inactive paths. |
| `0x0041b450 CCannon__VFuncSlot_02_RemoveFromWorldAndForward` | DATA refs place this slot-2 entry in CCannon/CSentinel/CWarspiteDome tables; body removes the unit from world occupancy-grid wrapper and forwards to `CUnit__VFunc02_CleanupWorldLinksAndForward`. |
| `0x0041b470 CCannon__AdvanceActivationAnimationState` | Reads current animation, resolves Activate/Deactivate/Active/Inactive animation ids, advances completed transitions, and writes state `+0x260` to Active or Inactive. |
| `0x0041b540 CCannon__GetMidpoint` | Calls `CCannon__SelectTarget`, adds this unit position at `+0x1c/+0x20/+0x24`, and scales by the 0.5 constant to produce an output midpoint. |
| `0x0041b590 CCannon__VFuncSlot_50_MarkDestroyedResetDeployGraph` | Current evidence rejects the old CanFire label; DATA refs place this slot-50 entry in CCannon/CWarspiteDome/CGroundVehicle tables, and the body calls `CGroundUnit__MarkDestroyedAndResetState` before `CUnit__ResetDeploymentGraphAndScheduleEvent` on success. |
| `0x004fd4d0 CCannon__SelectTarget` | Linked target `+0x178` forwards to `CDiveBomber__SelectTarget`; fallback writes this unit center position through `CThing__GetCentrePos`. |

Read-back counts: `13` metadata rows, `13` tag rows, `57` xref rows, `1044` body-instruction rows, and `13` decompile rows. The saved `cannon-turret-activation-review-wave992` tags are static Ghidra evidence only; runtime turret activation/firing behavior and rebuild parity remain separate proof.

## Exception Handlers

| Address | Name | Line | Purpose |
|---------|------|------|---------|
| 0x005d1760 | Unwind@005d1760 | 0x22 | Wave744 saved `void __cdecl` cleanup callback; frees pointer at `EBP+4` through `OID__FreeObject_Callback` with Cannon.cpp debug path `0x00623dd4` and memtype `0x17` |
| 0x005d1776 | Unwind@005d1776 | 0x23 | Wave744 saved `void __cdecl` cleanup callback; frees pointer at `EBP+4` through `OID__FreeObject_Callback` with Cannon.cpp debug path `0x00623dd4` and memtype `0x16` |
| 0x005d178c | Unwind@005d178c | 0x26 | Wave744 saved `void __cdecl` cleanup callback; frees pointer at `EBP+4` through `OID__FreeObject_Callback` with Cannon.cpp debug path `0x00623dd4` and memtype `0x1b` |

Wave744 unwind continuation saved static Ghidra comments/tags/signatures for these Cannon.cpp unwind callbacks with `unwind-continuation-wave744` and `wave744-readback-verified`. Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260522-163423_post_wave744_unwind_continuation_verified`; next high-signal queue head after the wave is `0x005d1840 Unwind@005d1840`, while the raw commentless head remains `0x0042f220 CSPtrSet__Clear`. Runtime cannon allocation cleanup behavior, exact source body identity, and rebuild parity remain unproven.

## State Machine

CCannon uses a 4-state machine for activation:

| Value | State | Description |
|-------|-------|-------------|
| 0 | Active | Cannon is operational and can fire |
| 1 | Inactive | Cannon is disabled |
| 2 | Deactivating | Transitioning to inactive (10s timeout) |
| 3 | Activating | Transitioning to active |

**State Strings:**
- `"Active"` at 0x00623e00
- `"Inactive"` at 0x00623e08
- `"Activate"` at 0x00623e14
- `"Deactivate"` at 0x00623e20

## Key Observations

- **RTTI/vtable evidence includes 0x005e24dc** - CCannon type row observed in the Wave 315 selected vtable read-back
- **Slot 2 at 0x0041b450** - Shared by CCannon, CSentinel, and CWarspiteDome vtable evidence; not a destructor body
- **Slot 50 at 0x0041b590** - Shared by CCannon, CWarspiteDome, and CGroundVehicle vtable evidence; calls `CGroundUnit__MarkDestroyedAndResetState` and is not a firing-condition check
- **State at offset 0x260** - Current state (0-3)
- **Timestamp at offset 0x264** - Last state change time
- **Fire controller at 0x208** - Controls weapon firing
- **10.0 second timeout** - Deactivation delay

## Class Structure (Partial)

| Offset | Size | Field | Notes |
|--------|------|-------|-------|
| 0x00 | 4 | vtable | CCannon vtable pointer |
| 0x08 | 4 | pAnimController | Animation controller |
| 0x1c-0x24 | 12 | boundMin | Min bounding box (float[3]) |
| 0x70 | 4 | flags | Various flags |
| 0x13c | 4 | pTarget | Target/linked object |
| 0x208 | 4 | mFireController | Fire controller |
| 0x214 | 4 | mIsEnabled | Enable flag |
| 0x260 | 4 | mState | Current state (0-3) |
| 0x264 | 4 | mLastStateChangeTime | Timestamp |

## Related Files

- Unit.cpp - Base unit class
- BattleEngine.cpp - Weapon firing system

## Current Boundary

Wave 315 saved the Cannon-local Ghidra names, signatures, and comments after headless dry/apply/read-back. Wave 392 later corrected the related `0x0047c970` and `0x0047ce80` helpers from over-specific Cannon-local names to `CGroundUnit` helpers while preserving Cannon subclass reuse evidence. Wave992 refreshed the Cannon-local comments/tags against current post-100 re-audit evidence. These passes do not prove exact source virtual names, concrete class layout, runtime turret activation, runtime firing behavior, or rebuild parity.

---
*Initial page discovered via Phase 1 xref analysis (Dec 2025); updated with Wave 315 saved Ghidra correction evidence (2026-05-10), Wave 392 GroundUnit owner correction evidence (2026-05-14), and Wave992 Cannon/turret activation re-audit evidence (2026-05-31).*
