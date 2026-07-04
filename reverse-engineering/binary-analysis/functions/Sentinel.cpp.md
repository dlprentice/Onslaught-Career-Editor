# Sentinel.cpp - Function Mappings

> CSentinel class - AI-controlled defensive turret/sentinel unit
> Debug path: `[maintainer-local-source-export-root]\Sentinel.cpp` (0x0063221c)

## Overview

`CSentinel` is a defensive unit with activation/deactivation animation states and flamethrower-style weapon behavior. Wave498 supersedes the older manual-creation note for `0x004dea50`: the saved Ghidra project now has a function object at that address named `CSentinel__Init`.

This page records static retail-binary evidence only. Concrete `CSentinel`/weapon/list/helper layouts, runtime firing behavior, runtime animation behavior, exact source body identity, BEA launch behavior, and rebuild parity remain unproven.

Wave1020 (`projectile-burst-spawn-spine-review-wave1020`) re-read `0x00506010 ProjectileBurst__SpawnFromPercentBucketFallback` with Sentinel caller context. Fresh xrefs still show `0x004decc0 CSentinel__UpdateFlamethrowers` calling the fallback at `0x004ded11`, while `0x004dea50 CSentinel__Init` remains the initialization context row. No mutation was needed. Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260531-214433_post_wave1020_projectile_burst_spawn_spine_review_verified`. Runtime flamethrower/projectile behavior, exact Sentinel/weapon layouts, BEA patching, and rebuild parity remain separate proof.

Wave1021 (`motion-controller-constructor-review-wave1021`) re-read `0x0049c5d0 CMCSentinel__Constructor` with no mutation. Fresh xrefs still show `CSentinel__Init` callers at `0x004deafd` and `0x004deb09`; instruction evidence calls `CMotionController__ctor_base`, installs vtable `0x005dc420`, stores the owner sentinel pointer at `+0x08`, and seeds `+0x0c/+0x10` with `0xc479c000`. Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260531-222637_post_wave1021_motion_controller_constructor_review_verified`. Runtime sentinel motion behavior, exact source-body identity, concrete layouts, BEA patching, and rebuild parity remain separate proof.

## Class Hierarchy

```text
CThing
  CUnit
    CSentinel
```

## Wave498 Saved CSentinel Evidence

| Address | Saved name | Signature | Static evidence |
| --- | --- | --- | --- |
| `0x004dea50` | `CSentinel__Init` | `void __thiscall CSentinel__Init(void * this, void * init_data)` | Primary table `0x005e0904` slot 0 points here. `RET 0x4` confirms one `init_data` stack argument after `this`. The body edits init data, delegates to `CGroundUnit__Init`, optionally selects the `inactive` animation, allocates Sentinel.cpp line-backed helpers, attaches `CMCSentinel` at `this+0x70`, stores helpers at `this+0x208` and `this+0x13c`, clears a `this+0x12c` record, and registers through `DAT_00855090`. |
| `0x004dec00` | `CSentinel__ScalarDeletingDestructor` | `void * __thiscall CSentinel__ScalarDeletingDestructor(void * this, byte flags)` | Secondary table `0x005deca0` slot 0 points here. Wrapper calls `CSentinel__Destructor(this)`, frees through `CDXMemoryManager__Free(&DAT_009c3df0, this)` when `flags & 1`, returns `this`, and ends with `RET 0x4`. |
| `0x004dec20` | `CSentinel__Destructor` | `void __fastcall CSentinel__Destructor(void * this)` | Restores base CMonitor-style vtable `0x005d8d1c`, removes `CSPtrSet`-linked cells at `this+0x28`, `this+0x24`, and `this+0x0c` when populated, then calls `CMonitor__Shutdown`. |
| `0x004decc0` | `CSentinel__UpdateFlamethrowers` | `void __fastcall CSentinel__UpdateFlamethrowers(void * this)` | Primary table slot 57 points here. Updates linked ground-unit effects, walks the `this+0x17c` linked list, filters entries named `Sentinel Flamethrower`, checks distance/range eligibility, calls `CSentinel__CheckWeaponSlot(this, weapon_context)`, and spawns a projectile burst only when all gates pass. |
| `0x004ded30` | `CSentinel__Activate` | `void __fastcall CSentinel__Activate(void * this)` | Primary table slot 13 points here. Resolves the `activate` animation through the render/model object at `this+0x30`, finds its animation index, and dispatches through vtable slot `+0xf0`. |
| `0x004ded60` | `CSentinel__Deactivate` | `int __fastcall CSentinel__Deactivate(void * this)` | Primary table slot 50 points here. Reads current animation state, compares it to the `activate` animation index, switches to looping `inactive` animation when appropriate, calls the slot-22 state-change helper, and returns `0`. |
| `0x004dee00` | `CSentinel__CheckWeaponSlot` | `int __thiscall CSentinel__CheckWeaponSlot(void * this, void * weapon_context)` | Called by `CSentinel__UpdateFlamethrowers`. Maps `weapon_context+0xac` values `2..9` to slot ids `9..16`, walks `this+0x19c`, returns `0` when an occupied entry has `+0x270` matching the slot id, and returns `1` otherwise. |

## Wave498 Read-Back

Evidence artifacts live under `subagents/ghidra-static-reaudit/wave498-sentinel-safeside-004de1d0/`.

| Evidence | Result |
| --- | --- |
| Dry run | `updated=0 skipped=6 created=0 would_create=1 renamed=0 would_rename=1 missing=0 bad=0` |
| Apply | `updated=7 skipped=0 created=1 would_create=0 renamed=1 would_rename=0 missing=0 bad=0` |
| Void correction apply | `updated=1 skipped=6 created=0 would_create=0 renamed=0 would_rename=0 missing=0 bad=0` |
| Int correction apply | `updated=1 skipped=6 created=0 would_create=0 renamed=0 would_rename=0 missing=0 bad=0` |
| Final verify dry | `updated=0 skipped=7 created=0 would_create=0 renamed=0 would_rename=0 missing=0 bad=0` |
| Probe | `py -3 tools\ghidra_sentinel_wave498_probe.py --check` PASS |
| NPM probe | `cmd.exe /c npm run test:ghidra-sentinel-wave498` PASS |
| Backup | `[maintainer-local-ghidra-backup-root]\BEA_20260517-115915_post_wave498_sentinel_verified`, 19 files, 157780871 bytes, `MissingCount=0`, `ExtraCount=0`, `HashDiffCount=0` |

Wave542 later resolved the deferred non-Sentinel `0x004de1d0` target as `CSafeSide__ShutdownAndUnlinkFactionAnchor`.

## Wave542 CSafeSide Follow-Up

| Address | Saved name | Signature | Static evidence |
| --- | --- | --- | --- |
| `0x004de1d0` | `CSafeSide__ShutdownAndUnlinkFactionAnchor` | `void __fastcall CSafeSide__ShutdownAndUnlinkFactionAnchor(void * this)` | Vtable slot data at `0x005dcce4` points here for tables `0x005dccc0`, `0x005dccc4`, and `0x005dccd0`. The body removes `this` from `DAT_00855160` through `CSPtrSet__Remove`, then forwards to `CComplexThing__Shutdown`. `CUnit__FindNearestFactionAnchor` also scans `DAT_00855160`, bounding the list role as faction-anchor context. |

Read-back artifacts live under `subagents/ghidra-static-reaudit/wave542-safeside-vfunc-004de1d0/`.

| Evidence | Result |
| --- | --- |
| Dry run | `updated=0 skipped=1 renamed=0 would_rename=1 missing=0 bad=0` |
| Apply | `updated=1 skipped=0 renamed=1 would_rename=0 missing=0 bad=0` |
| Final verify dry | `updated=0 skipped=1 renamed=0 would_rename=0 missing=0 bad=0` |
| Probe | `py -3 tools\ghidra_safeside_shutdown_wave542_probe.py --check` PASS |
| NPM probe | `cmd.exe /c npm run test:ghidra-safeside-shutdown-wave542` PASS |
| Backup | `[maintainer-local-ghidra-backup-root]\BEA_20260518-093637_post_wave542_safeside_shutdown_verified`, 19 files, 159320967 bytes, `MissingCount=0`, `ExtraCount=0`, `HashDiffCount=0` |

This is not runtime faction-anchor proof, exact `CSafeSide` source-body proof, concrete layout recovery, BEA launch behavior, game patching, or rebuild parity.

## VTables

### CSentinel Primary Table

| Table | Slot | Pointer | Saved function |
| --- | ---: | --- | --- |
| `0x005e0904` | 0 | `0x004dea50` | `CSentinel__Init` |
| `0x005e0904` | 13 | `0x004ded30` | `CSentinel__Activate` |
| `0x005e0904` | 50 | `0x004ded60` | `CSentinel__Deactivate` |
| `0x005e0904` | 57 | `0x004decc0` | `CSentinel__UpdateFlamethrowers` |

### CSentinel Secondary Table

| Table | Slot | Pointer | Saved function |
| --- | ---: | --- | --- |
| `0x005deca0` | 0 | `0x004dec00` | `CSentinel__ScalarDeletingDestructor` |

## Related Strings

| Address | String | Usage |
| --- | --- | --- |
| `0x0063221c` | `[maintainer-local-source-export-root]\Sentinel.cpp` | Debug path |
| `0x0063223c` | `inactive` | Deactivated animation state |
| `0x00632248` | `Sentinel Flamethrower` | Flamethrower candidate name |
| `0x00632260` | `activate` | Activated animation state |

## Related Classes

- `CSentinelAI` (0x00632208) - AI controller for sentinel behavior.
- `CSentinelBehaviourType` (0x00627c98) - behavior type descriptor.
- `CMCSentinel` (0x0062dfa8) - motion controller for sentinel.

## Wave434 CMCSentinel Motion Controller Read-Back

Wave434 corrected the separate `CMCSentinel` motion-controller vtable at `0x005dc420`. This is distinct from the gameplay `CSentinel` unit, but Wave498 confirms `CSentinel__Init` allocates/attaches `CMCSentinel` at `this+0x70`.

| Address | Saved name | Static evidence |
| --- | --- | --- |
| `0x0049c5d0` | `CMCSentinel__Constructor` | Installs vtable `0x005dc420`, stores owner at `+0x08`, and seeds cached fields `+0x0c/+0x10`. |
| `0x0049c600` | `CMCSentinel__ScalarDeletingDestructor` | Delete-flags wrapper around `CMCSentinel__Destructor`. |
| `0x0049c620` | `CMCSentinel__Destructor` | Restores vtable `0x005dc420`, clears owner `+0x08`, and tails the base motion-controller destructor. |
| `0x0049c640` | `CMCSentinel__VFunc_04_UpdateX1TurretOrBarrelTransform_0049c640` | Recovered vtable slot-4 boundary; checks `X1 turret` / `X1 barrel`, updates transform output, and refreshes cached owner fields `+0xe0/+0xe8`. |

## Not Proven

- Exact source virtual names for the Sentinel vtable entries.
- Concrete `CSentinel`, weapon-context, linked-list, helper-object, animation-owner, or `CMCSentinel` field layouts.
- Runtime Sentinel activation, deactivation, flamethrower firing, destruction, or helper-allocation behavior.
- BEA launch behavior, installed-game patching, source rebuild parity, or full Sentinel subsystem completeness.

## Summary

| Function | Address | Status |
| --- | --- | --- |
| `CSentinel__Init` | `0x004dea50` | SAVED |
| `CSentinel__ScalarDeletingDestructor` | `0x004dec00` | SAVED |
| `CSentinel__Destructor` | `0x004dec20` | SAVED |
| `CSentinel__UpdateFlamethrowers` | `0x004decc0` | SAVED |
| `CSentinel__Activate` | `0x004ded30` | SAVED |
| `CSentinel__Deactivate` | `0x004ded60` | SAVED |
| `CSentinel__CheckWeaponSlot` | `0x004dee00` | SAVED |

Total: 7 gameplay `CSentinel` functions saved/read back in Wave498.
