# Sentinel.cpp Functions

Wave1219 final current-risk closure note: `CSentinel__Init` remains mapped to Sentinel init/motion-control/helper setup; verified backup `[maintainer-local-ghidra-backup-root]\BEA_20260607-230027_post_wave1219_final_score16_current_risk_review_verified`. Runtime Sentinel behavior, exact helper layouts, and rebuild parity remain separate proof.

> Source File: Sentinel.cpp | Binary: BEA.exe
> Debug Path: 0x0063221c

> **Queue status (2026-05-26):** Ghidra export-contract closure **6113/6113** (Wave900: every function commented; clean-signature proxy; not evidence-grade semantics). Lines below that reference a "next raw commentless" row are **archival wave progress**, not open work.

## Overview

Sentinel unit implementation. `CSentinel` appears to be a defensive/turret-type unit with activation/deactivation animations and flamethrower-style weapon behavior.

Wave1140 (`wave1140-motion-controller-current-risk-review`) re-read the motion-controller residual current-risk cluster including sentinel anchor `0x0049c5d0 CMCSentinel__Constructor`, plus `0x00497090 CMCHiveBoss__Constructor`, `0x00497140 CDestructableSegmentsMotionController__CacheNamedCollisionCylinders`, `0x00494fa0 SharedMotionController__VFunc_UpdateUnitAIIndexedEntryFlag`, `0x00494ff0 SharedMotionController__VFunc_CallUnitAIIndexedEntryVFunc10`, `0x0049c1d0 CMCMech__VFunc_05_WriteInterpolatedBoneFloat_0049c1d0`, `0x0049c3e0 CMCMine__Constructor`, `0x0049c440 CMCMine__VFunc_04_UpdateInterpolatedHeightOffset_0049c440`, and `0x0049f820 SharedGroundUnit__VFunc_09_InitGroundedMotionComponents_0049f820`. It covers `9 current-risk rows`; current focused accounting is `238/1179 = 20.19%`; current risk candidates: 6166; current focused candidates: 1178; live regenerated current focused candidates: 1178; remaining active focused work: 941; static debt `0 / 0 / 0`; static closure `6411/6411 = 100.00%`. This was a fresh Ghidra export, read-only review, no mutation. Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260605-142515_post_wave1140_motion_controller_current_risk_review_verified`; previous completed backup: `[maintainer-local-ghidra-backup-root]\BEA_20260605-134608_post_wave1139_battleengine_jetpart_current_risk_review_verified`. Runtime motion-controller behavior, exact layouts, and rebuild parity remain separate proof.

Wave498 supersedes the older manual-creation note for `0x004dea50`: the saved Ghidra project now has a function object named `CSentinel__Init` at that address.

Wave1021 (`motion-controller-constructor-review-wave1021`) re-read `0x0049c5d0 CMCSentinel__Constructor` with no mutation. Fresh xrefs still show `CSentinel__Init` callers at `0x004deafd` and `0x004deb09`; instruction evidence calls `CMotionController__ctor_base`, installs vtable `0x005dc420`, stores the owner sentinel pointer at `+0x08`, and seeds `+0x0c/+0x10` with `0xc479c000`. Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260531-222637_post_wave1021_motion_controller_constructor_review_verified`. Runtime sentinel motion behavior, exact source-body identity, concrete layouts, BEA patching, and rebuild parity remain separate proof.

## Wave498 Gameplay Sentinel Functions

| Address | Saved name | Purpose |
| --- | --- | --- |
| `0x004dea50` | `CSentinel__Init` | Primary table slot-0 init path; delegates to `CGroundUnit__Init`, allocates/attaches Sentinel helpers, and installs `CMCSentinel`. |
| `0x004dec00` | `CSentinel__ScalarDeletingDestructor` | Delete-flags wrapper around `CSentinel__Destructor` plus optional `CDXMemoryManager__Free`. |
| `0x004dec20` | `CSentinel__Destructor` | Restores base CMonitor-style vtable, removes linked cells, then calls `CMonitor__Shutdown`. |
| `0x004decc0` | `CSentinel__UpdateFlamethrowers` | Walks flamethrower candidates, checks range/slot gates, and spawns projectile bursts. |
| `0x004ded30` | `CSentinel__Activate` | Dispatches the `activate` animation index through the render/model vtable. |
| `0x004ded60` | `CSentinel__Deactivate` | Switches from `activate` to looping `inactive` animation when appropriate and returns `0`. |
| `0x004dee00` | `CSentinel__CheckWeaponSlot` | Maps weapon context values `2..9` to slot ids `9..16` and rejects occupied slots. |

## Vtable Evidence

| Table | Slot | Pointer | Saved function |
| --- | ---: | --- | --- |
| `0x005e0904` | 0 | `0x004dea50` | `CSentinel__Init` |
| `0x005e0904` | 13 | `0x004ded30` | `CSentinel__Activate` |
| `0x005e0904` | 50 | `0x004ded60` | `CSentinel__Deactivate` |
| `0x005e0904` | 57 | `0x004decc0` | `CSentinel__UpdateFlamethrowers` |
| `0x005deca0` | 0 | `0x004dec00` | `CSentinel__ScalarDeletingDestructor` |

## Xrefs to Debug Path

| Address | Type | Notes |
| --- | --- | --- |
| `0x004dead4` | Main code | Sentinel.cpp line-backed helper allocation path in `CSentinel__Init`. |
| `0x004deb14` | Main code | Sentinel.cpp line-backed helper allocation path in `CSentinel__Init`. |
| `0x004deb4f` | Main code | Sentinel.cpp line-backed helper allocation path in `CSentinel__Init`. |
| `0x005d4b50` | Unwind handler | Exception cleanup. |
| `0x005d4b66` | Unwind handler | Exception cleanup. |
| `0x005d4b7c` | Unwind handler | Exception cleanup. |

## Exception Handlers

| Address | Name | Purpose |
| --- | --- | --- |
| `0x005d4b50` | `Unwind@005d4b50` | Cleanup handler. |
| `0x005d4b66` | `Unwind@005d4b66` | Cleanup handler. |
| `0x005d4b7c` | `Unwind@005d4b7c` | Cleanup handler. |

Wave765 static read-back (`unwind-continuation-wave765`, `wave765-readback-verified`) hardened Sentinel.cpp unwind callbacks at `0x005d4b50 Unwind@005d4b50`, `0x005d4b66 Unwind@005d4b66`, and `0x005d4b7c Unwind@005d4b7c`, plus Sentinel-adjacent monitor/active-reader cleanup at `0x005d4ba0 Unwind@005d4ba0`, `0x005d4ba8 Unwind@005d4ba8`, and `0x005d4bb3 Unwind@005d4bb3`. Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260523-155528_post_wave765_unwind_continuation_verified`. This is saved static retail Ghidra evidence only; exact parent source-body identity, runtime cleanup behavior, BEA patching, and rebuild parity remain deferred.

## Status

**SAVED STATIC RE** - Wave498 created/recovered the `0x004dea50` function boundary and saved seven gameplay `CSentinel` names/signatures/comments/tags with dry/apply/read-back evidence.

Evidence artifacts:

- `tools/ApplySentinelWave498.java`
- `tools/ghidra_sentinel_wave498_probe.py`
- `subagents/ghidra-static-reaudit/wave498-sentinel-safeside-004de1d0/`
- `release/readiness/ghidra_sentinel_wave498_2026-05-17.md`

This is not runtime proof, concrete layout recovery, exact source body proof, BEA launch behavior, game patching, rebuild parity, or full Sentinel subsystem completion.

Wave542 later resolved the deferred non-Sentinel `0x004de1d0` target as `CSafeSide__ShutdownAndUnlinkFactionAnchor`.

## Wave542 CSafeSide Follow-Up

| Address | Saved name | Purpose |
| --- | --- | --- |
| `0x004de1d0` | `CSafeSide__ShutdownAndUnlinkFactionAnchor` | Vtable-backed register-only shutdown helper that removes `this` from `DAT_00855160` through `CSPtrSet__Remove`, then forwards to `CComplexThing__Shutdown`. |

Evidence artifacts:

- `tools/ApplySafeSideShutdownWave542.java`
- `tools/ghidra_safeside_shutdown_wave542_probe.py`
- `subagents/ghidra-static-reaudit/wave542-safeside-vfunc-004de1d0/`
- `release/readiness/ghidra_safeside_shutdown_wave542_2026-05-18.md`

The `DAT_00855160` list role is bounded as faction-anchor context because `CUnit__FindNearestFactionAnchor` scans it. Wave542 is static retail evidence only; exact `CSafeSide` source identity, concrete list/object layout, runtime faction-anchor behavior, BEA patching, and rebuild parity remain open.

Wave1119 (`wave1119-mixed-score26-current-risk-review`) re-read `0x004de1d0 CSafeSide__ShutdownAndUnlinkFactionAnchor` with a fresh read-only Ghidra export and no mutation. DATA xref `0x005dcce4`, `DAT_00855160`, `CSPtrSet__Remove`, and `CComplexThing__Shutdown` still bound the function as the SafeSide/faction-anchor unlink path. Current focused accounting moves to `110/1179 = 9.33%`; verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260605-022812_post_wave1119_mixed_score26_current_risk_review_verified`. Runtime faction-anchor behavior, exact layout/source identity, BEA patching, and rebuild parity remain separate proof.

## Wave434 Motion Controller Evidence

`CMCSentinel` is the sentinel motion-controller class referenced by the sentinel init path; it is distinct from the gameplay `CSentinel` unit and uses vtable `0x005dc420`.

| Address | Name | Evidence |
| --- | --- | --- |
| `0x0049c5d0` | `CMCSentinel__Constructor` | Installs vtable `0x005dc420`, stores owner at `+0x08`, seeds cached `+0x0c/+0x10`, and returns with `RET 0x4`. |
| `0x0049c600` | `CMCSentinel__ScalarDeletingDestructor` | Calls `CMCSentinel__Destructor`, conditionally frees `this`, and returns with `RET 0x4`. |
| `0x0049c620` | `CMCSentinel__Destructor` | Restores the CMCSentinel vtable, clears owner `+0x08`, and tails the base motion-controller destructor. |
| `0x0049c640` | `CMCSentinel__VFunc_04_UpdateX1TurretOrBarrelTransform_0049c640` | Recovered slot-4 boundary; checks `X1 turret` / `X1 barrel`, updates transform output, and refreshes cached owner fields `+0xe0/+0xe8`. |

## Related Files

- `Unit.cpp` - likely parent class.
- `Cannon.cpp` - similar turret/weapon unit.
