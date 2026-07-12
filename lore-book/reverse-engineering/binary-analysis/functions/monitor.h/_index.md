# monitor.h / Monitor.h (Deletion Event System)

> **Current semantic correction (2026-07-12):** several rows historically
> assigned to Monitor are BattleEngine/JetPart methods. Current authority is the
> [movement static crosswalk](../../battleengine-movement-static-crosswalk-2026-07-12.md).
> Old wave paragraphs below remain historical records; the live Ghidra names
> have not yet been mutated.

> Binary: `BEA.exe` (Steam build)
>
> Debug paths in `.rdata`:
> - `[maintainer-local-source-export-root]\monitor.h` @ `0x0062551c`
> - `[maintainer-local-source-export-root]\Monitor.h` @ `0x00622b80`

> **Queue status (2026-05-26):** Ghidra export-contract closure **6113/6113** (Wave900: every function commented; clean-signature proxy; not evidence-grade semantics). Lines below that reference a "next raw commentless" row are **archival wave progress**, not open work.

## Overview

This header-level system implements the **ActiveReader / Monitor** pattern used throughout the game to prevent dangling pointers.

Wave909 engine/platform support static review (`engine-platform-support-static-review-wave909`) records the monitor/active-reader side of a static-coherent engine/platform/math/memory support core. Monitor anchors include `CMonitor__AddDeletionEvent` and `CGenericActiveReader__SetReader`; `CSPtrSet__Clear` is part of the same slice. Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260526-120420_post_wave909_engine_platform_support_static_review_verified`. Runtime monitor/safe-pointer behavior remains separate proof.

Wave1154 (`wave1154-unitai-deploy-target-current-risk-review`) historically re-read `0x00410c50` as a Monitor movement/effect helper called from the then-saved `CMonitor__Process` label. Current static evidence instead identifies `0x00410c50` as `CBattleEngineJetPart__Move`, called from `0x004081c0 CBattleEngine__Move`. Fresh metadata, xrefs, instruction, and decompile evidence were read only; no mutation was made. Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260605-215410_post_wave1154_unitai_deploy_target_current_risk_review_verified`. Runtime movement/effect behavior, exact layouts, gameplay outcomes, visual QA, and rebuild parity remain separate proof.

Wave1187 (`wave1187-cmonitor-movement-audio-animation-render-current-risk-review`) saved comment/tag normalization for six rows under the names held by Ghidra at that time. Current static evidence preserves the four actual Monitor/render rows but reassigns `0x00411630` to `CBattleEngineJetPart__HandleGroundEffect` and `0x00411aa0` to `CBattleEngineJetPart__GetFriction`; their caller is now identified as `0x00410c50 CBattleEngineJetPart__Move`, reached from `0x004081c0 CBattleEngine__Move`. Apply reported `updated=6 skipped=0`, `comment_only_updated=6`, `tags_added=79`, and final dry updated=0 skipped=6; no rename, no signature change, no function-boundary change, and no executable-byte change occurred. One Codex read-only consult used; no Cursor/Composer. Static closure remains `6411/6411 = 100.00%` with `0 / 0 / 0`; Wave1108 current focused accounting is historical campaign telemetry, not semantic-completeness proof. Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260606-151617_post_wave1187_cmonitor_movement_audio_animation_render_current_risk_review_verified`. Runtime audio, movement, terrain, animation, rendering, exact layouts, BEA patching behavior, gameplay/visual outcomes, and rebuild parity remain separate proof.

At a high level:
- Objects that can be safely referenced inherit from a **monitor base** (`CMonitor` in Stuart's source naming).
- A `CActiveReader<T>` is a very small object (often just a 4-byte `mToRead` pointer).
- When an ActiveReader starts pointing at a monitor-derived object, it registers its **cell pointer** in the monitor's deletion list.
- When the monitored object dies, it iterates the deletion list and **nulls each cell** (`*cell = NULL`), matching `CGenericActiveReader::ToReadDied()`.

## Key Layout (Steam build)

Observed by RE (call sites + decompilation):
- `CMonitor + 0x04` is a lazily-allocated pointer to a `CSPtrSet` used as a deletion-event list.
- The deletion list stores **pointers to ActiveReader cells** (the address of `mToRead`), not a separate "listener object".

This matches Stuart's `activereader.h/.cpp` intent:
- `CGenericActiveReader::ToReadDied()` sets `mToRead = NULL`
- `CGenericActiveReader::SetReader()` removes from old monitor list and adds to new

## Functions (Steam build)

| Address | Name | Status | Notes |
|---------|------|--------|------|
| 0x00401040 | `CMonitor__AddDeletionEvent` | RENAMED | Allocates `CSPtrSet` at `monitor+0x04` (if needed) and adds `reader_cell` |
| 0x0042d9b0 | `CMonitor__DeleteDeletionEvent` | RENAMED | Removes `reader_cell` from `monitor+0x04` deletion list when present |
| 0x00401000 | `CGenericActiveReader__SetReader` | RENAMED | Unregister from old `mToRead+0x04`, assign, then register with new monitor |
| 0x00419a20 | `CMonitor__scalar_deleting_dtor` | RENAMED | Scalar deleting dtor wrapper: calls monitor shutdown then frees when delete-flag bit is set |
| 0x0044b1d0 | `CGenericActiveReader__dtor` | RENAMED | Unregister helper used before freeing an ActiveReader (removes from `mToRead+0x04`) |
| 0x00466120 | `CMonitor__ctor` | RENAMED | Monitor base constructor: sets vtable and initializes `monitor+0x04` to NULL |
| 0x0046dbc0 | `CMonitor__Shutdown_Thunk` | RENAMED | Thin compiler thunk that forwards to `0x004bac40` |
| 0x004bac40 | `CMonitor__Shutdown` | RENAMED | Monitor shutdown/destructor: iterates `monitor+0x04` and nulls each reader cell (`*cell = NULL`), then clears+frees the `CSPtrSet` |
| 0x004bacb0 | `CMonitor__Shutdown_Core` | RENAMED | Shared cleanup implementation (same null+clear+free behavior) used across many vtables |
| 0x0044e2c0 | `CMonitor__CheckSVFAnimationAndAdvanceState` | SIGNED | Wave 368 hardens the monitor receiver signature; checks current animation against `SVF` token and triggers monitor state-advance callback when matched |
| 0x0040a580 | `CBattleEngine__Morph` | SIGNED | Former monitor-transition alias; current saved Ghidra name is the source-backed BattleEngine morph bridge, tracked in `BattleEngine.cpp/_index.md` |
| 0x0040dcc0 | `CMonitor__ResetTransitionFlagAndUpdateIfState3_Thunk` | RENAMED | Resets a transition-state flag and conditionally calls the current `CBattleEngine__Morph` target; source identity still deferred |
| 0x00412ad0 | `CMonitor__UpdateSurfaceAlignmentAngle` | RENAMED | Updates angle-like surface-alignment state from linked-object orientation context; signature, source identity, and runtime behavior remain deferred |
| 0x00407a50 | `CMonitor__UpdateCameraVectorsAndInput` | SIGNED | Camera/input update helper with saved `void * monitor` signature; exact layout/runtime behavior remains deferred |
| 0x004081c0 | [`CBattleEngine__Move`](../BattleEngine.cpp/CBattleEngine__Move.md) | SUPERSEDED MONITOR NAME | `CBattleEngine` RTTI vtable slot 66 plus field/call/source agreement; live Ghidra rename pending |
| 0x00409880 | `CMonitor__GetLastValidRangeStep100` | SIGNED | Scans five 100-step slots from monitor `+0xa4` and returns the last nonnegative slot; exact layout/runtime behavior remains deferred |
| 0x004098c0 | `CLine__VFunc_01_004098c0` | SIGNED | Wave388 hardens the CLine vtable-slot wrapper signature/comment; it forwards the ECX receiver plus four stack args to `dispatch_target` vfunc `+0x10`; exact dispatch target class/runtime behavior remains deferred |
| 0x00412900 | `CBattleEngineJetPart__AutoLevel` | SUPERSEDED MONITOR NAME | Main-part, ground/velocity, energy, and barrel-count decision sequence matches source; live Ghidra rename pending |
| 0x00414010 | `CMonitor__ClearCurrentTrackedEntryFlag60` | SIGNED | Wave388 hardens the monitor receiver signature/comment; calls `CBattleEngineWalkerPart__GetCurrentWeapon` and clears current weapon/tracked-entry field `+0x60` when present |
| 0x00413760 | `CBattleEngineWalkerPart__Move` | SIGNED | Wave308 source-parity correction supersedes the Wave307 monitor tracking/surface-alignment label; tracked in `BattleEngineWalkerPart.cpp/_index.md` |
| 0x00413a70 | `CBattleEngineWalkerPart__GoingIntoWater` | SIGNED | Wave308 source-parity correction supersedes the Wave307 monitor path-predicate label; tracked in `BattleEngineWalkerPart.cpp/_index.md` |
| 0x00413b90 | `CBattleEngineWalkerPart__Slide` | SIGNED | Wave308 source-parity correction supersedes the Wave307 monitor surface-alignment label; tracked in `BattleEngineWalkerPart.cpp/_index.md` |
| 0x00411630 | `CBattleEngineJetPart__HandleGroundEffect` | SUPERSEDED MONITOR NAME | JetPart Move caller and source-compatible terrain/ground-effect body; live Ghidra rename pending |
| 0x00411aa0 | `CBattleEngineJetPart__GetFriction` | SUPERSEDED MONITOR NAME | JetPart Move caller and source-compatible friction predicate; live Ghidra rename pending |
| 0x0047ec60 | `CMonitor__SampleHeightfieldNormalAtXY` | SIGNED | Wave394 hardens the saved receiver/out/world-position signature for terrain-normal sampling; owner remains bounded/provisional and runtime terrain-normal behavior remains deferred |
| 0x0040b120 | `CBattleEngine__UpdateAutoAim` | SIGNED | Former monitor target-tracking alias; current saved Ghidra name is the source-backed BattleEngine auto-aim bridge, tracked in `BattleEngine.cpp/_index.md` |
| 0x00409950 | `CMonitor__UpdateSoundEventPlaybackForReader` | SIGNED | Updates engine/health/energy/lock/walk sound chains and active-reader state; runtime audio behavior remains deferred |
| 0x0047d3b0 | `CMonitor__TryQueuePrefireAnimation` | SIGNED | Wave393 hardens this `CGroundVehicle` vtable slot `86` helper: calls deploy/charge update, validates `prefire`, and dispatches vfunc `+0xf0`; runtime animation behavior remains deferred |
| 0x004ef120 | `CMonitor__SpawnParticleEffectFromIndexedListInHeightBand` | SIGNED | Wave512 saved `void __fastcall ... (void * this)`; walks indexed global list entry and emits particle effect only if sampled Z position is in configured height band |
| 0x005078f0 | `CMonitor__UpdateTrackedRenderPair` | SIGNED | Wave553 saved `void __thiscall ...(void * this, int update_projected_volume)`; updates two tracked render slots and optional projected-volume orientation data |

## Wave765 monitor and active-reader unwind callbacks

Wave765 unwind continuation saved `void __cdecl Unwind@...(void)` signatures, comments, and tags for monitor/active-reader cleanup callbacks including `0x005d4ac0 Unwind@005d4ac0`, `0x005d4ae0 Unwind@005d4ae0`, `0x005d4b10 Unwind@005d4b10`, `0x005d4ba8 Unwind@005d4ba8`, and `0x005d4bb3 Unwind@005d4bb3`. These rows use `unwind-continuation-wave765` and `wave765-readback-verified`; observed bodies jump to `CGenericActiveReader__dtor` or `CMonitor__Shutdown` through DATA scope-table xrefs. Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260523-155528_post_wave765_unwind_continuation_verified`. This is saved static retail Ghidra evidence only; exact parent source body, runtime exception behavior, runtime cleanup behavior, BEA patching, and rebuild parity remain unproven.

## Wave766 monitor.h unwind callback

Wave766 unwind continuation saved the monitor.h allocation-cleanup callback at `0x005d4d0e Unwind@005d4d0e` as `void __cdecl Unwind@005d4d0e(void)` with the `unwind-continuation-wave766` and `wave766-readback-verified` tags. DATA scope-table xref `0x0061d5bc` points at the body; instruction/decompile evidence calls `OID__FreeObject_Callback(*(EBP+0x4))` with monitor.h debug path `0x0062551c`, line token `0x18`, and allocation/type value `0x5e`. Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260523-161835_post_wave766_unwind_continuation_verified`. This is saved static retail Ghidra evidence only; exact parent source body, runtime exception behavior, runtime cleanup behavior, BEA patching, and rebuild parity remain unproven.

## Wave764 monitor.h unwind callback

Wave764 unwind continuation saved a monitor.h allocation-cleanup callback at `0x005d4756 Unwind@005d4756` as `void __cdecl Unwind@005d4756(void)` with the `unwind-continuation-wave764` and `wave764-readback-verified` tags. DATA scope-table xref `0x0061cfec` points at the body; instruction evidence calls `OID__FreeObject_Callback(*(EBP-0x10))` with monitor.h debug path `0x0062551c`, line token `0x18`, and allocation/type value `0x5e`. Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260523-152957_post_wave764_unwind_continuation_verified`. This is saved static retail Ghidra evidence only; exact parent source body, runtime exception behavior, runtime cleanup behavior, BEA patching, and rebuild parity remain unproven.

## Wave741 unwind head callbacks

Wave741 unwind head saved `void __cdecl Unwind@...(void)` signatures, comments, and tags for the Monitor/active-reader cleanup callbacks at `0x005d0f10`, `0x005d0f30`, `0x005d0f38`, `0x005d0f50`, and `0x005d0fd0`. These rows have scope-table DATA xrefs from `0x00619e04`, `0x00619e2c`, `0x00619e34`, `0x00619e5c`, and `0x00619edc`; the bodies call `OID__FreeObject_Callback`, `CMonitor__Shutdown_Thunk`, `CGenericActiveReader__dtor`, or `CMonitor__Shutdown`. Tags include `unwind-head-wave741` and `wave741-readback-verified`.

This is saved static retail Ghidra evidence only. Exact parent source body, runtime exception behavior, runtime cleanup behavior, BEA patching, and rebuild parity remain unproven.

## Wave742 unwind continuation callbacks

Wave742 unwind continuation saved `void __cdecl Unwind@...(void)` signatures, comments, and tags for the Monitor/active-reader cleanup callbacks at `0x005d13a0 Unwind@005d13a0`, `0x005d13a8 Unwind@005d13a8`, and `0x005d13b3 Unwind@005d13b3`. These rows have scope-table DATA xrefs from `0x0061a21c`, `0x0061a224`, and `0x0061a22c`; the bodies call `CMonitor__Shutdown` on `EBP-0x10`, then `CGenericActiveReader__dtor` on embedded fields `+0xc` and `+0x24`. Tags include `unwind-continuation-wave742` and `wave742-readback-verified`.

The same Wave742 tranche spans `0x005d1170 Unwind@005d1170` through `0x005d13b3 Unwind@005d13b3`, including BattleEngine.cpp cleanup at `0x005d11f0 Unwind@005d11f0`, CLine stack-local cleanup at `0x005d1220 Unwind@005d1220`, and Boat.cpp cleanup at `0x005d1360 Unwind@005d1360`. Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260522-153147_post_wave742_unwind_continuation_verified`. Next high-signal queue head is `0x005d13d0 Unwind@005d13d0`; earliest raw commentless row remains `0x0042f220 CSPtrSet__Clear`.

This is saved static retail Ghidra evidence only. Exact parent source body, runtime exception behavior, runtime cleanup behavior, BEA patching, and rebuild parity remain unproven.

## Wave744 unwind continuation callbacks

Wave744 unwind continuation saved `void __cdecl Unwind@...(void)` signatures, comments, and tags for the Monitor.h allocation-cleanup callbacks at `0x005d164b Unwind@005d164b` and `0x005d16e0 Unwind@005d16e0`. Both rows call `OID__FreeObject_Callback` on the pointer at `EBP+4` with Monitor.h debug path `0x00622b80`, line `0x18`, and memtype `0x5e`; their scope-table DATA xrefs are `0x0061a4c4` and `0x0061a53c`.

## Wave758 monitor/pointer-set cleanup callbacks

Wave758 unwind continuation saved `void __cdecl Unwind@...(void)` signatures, comments, and tags for monitor, active-reader, and pointer-set cleanup callbacks in the `0x005d3b30 Unwind@005d3b30` through `0x005d3bb0 Unwind@005d3bb0` range. Exact anchors include `0x005d3b38 Unwind@005d3b38` and `0x005d3bb0 Unwind@005d3bb0`. The tranche uses the `unwind-continuation-wave758` and `wave758-readback-verified` tags and verified backup `[maintainer-local-ghidra-backup-root]\BEA_20260523-123821_post_wave758_unwind_continuation_verified`.

| Address | Evidence |
| --- | --- |
| 0x005d3b30 | DATA xref `0x0061c764`; jumps to `CMonitor__Shutdown_Thunk(*(EBP-0x14))`. |
| 0x005d3b38 | DATA xref `0x0061c76c`; jumps to `CGenericActiveReader__dtor((*(EBP-0x14))+0x30)`. |
| 0x005d3b50 | DATA xref `0x0061c794`; jumps to `CMonitor__Shutdown_Thunk(*(EBP-0x10))`. |
| 0x005d3b70 | DATA xref `0x0061c7bc`; jumps to `CMonitor__Shutdown(*(EBP-0x18))`. |
| 0x005d3b78 | DATA xref `0x0061c7c4`; jumps to `CSPtrSet__Clear((*(EBP-0x18))+0x0c)`. |
| 0x005d3b90 | DATA xref `0x0061c7ec`; jumps to `CMonitor__Shutdown(*(EBP-0x10))`. |
| 0x005d3b98 | DATA xref `0x0061c7f4`; jumps to `CSPtrSet__Clear((*(EBP-0x10))+0x0c)`. |
| 0x005d3bb0 | DATA xref `0x0061c81c`; jumps to `CSPtrSet__Clear(EBP-0x1c)`. |

This is saved static retail Ghidra evidence only. Exact parent source body, runtime exception behavior, runtime cleanup behavior, BEA patching, and rebuild parity remain unproven.

## Wave759 monitor/pointer-set cleanup callbacks

Wave759 unwind continuation saved `void __cdecl Unwind@...(void)` signatures, comments, and tags for the next monitor/pointer-set cleanup head rows at `0x005d3bd0 Unwind@005d3bd0`, `0x005d3bf0 Unwind@005d3bf0`, and `0x005d3bf8 Unwind@005d3bf8`. DATA scope-table xrefs `0x0061c844`, `0x0061c86c`, and `0x0061c874` point at the bodies; the first two jump to `CMonitor__Shutdown_Thunk` on `*(EBP-0x10)`, and the third jumps to `CSPtrSet__Clear` on `(*(EBP-0x10))+0x18`.

The same Wave759 tranche spans `0x005d3bd0 Unwind@005d3bd0` through `0x005d3d7e Unwind@005d3d7e`, including Mine.cpp, Missile.cpp, oids.cpp, and unit/object cleanup rows. Tags include `unwind-continuation-wave759` and `wave759-readback-verified`. Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260523-130827_post_wave759_unwind_continuation_verified`. Next high-signal queue head is `0x005d3d94 Unwind@005d3d94`; earliest raw commentless row remains `0x0042f220 CSPtrSet__Clear`.

This is saved static retail Ghidra evidence only. Exact parent source body, runtime exception behavior, runtime cleanup behavior, BEA patching, and rebuild parity remain unproven.

## Wave760 active-reader cleanup callbacks

Wave760 unwind continuation saved `void __cdecl Unwind@...(void)` signatures, comments, and tags for active-reader cleanup callbacks at `0x005d3e28 Unwind@005d3e28`, `0x005d3e7d Unwind@005d3e7d`, and `0x005d3f2a Unwind@005d3f2a`. DATA scope-table xrefs `0x0061ca2c`, `0x0061ca54`, and `0x0061caa4` point at the bodies. The rows jump to `CGenericActiveReader__dtor` on object fields `+0x7c`, `+0x854`, and `+0x7c`.

The same Wave760 tranche spans `0x005d3d94 Unwind@005d3d94` through `0x005d3f35 Unwind@005d3f35`, including oids.cpp allocation cleanup, `0x005d3dd6 Unwind@005d3dd6` actor cleanup, complex-thing destructor-base cleanup, and `0x005d3eeb Unwind@005d3eeb` particle-list cleanup. Tags include `unwind-continuation-wave760` and `wave760-readback-verified`. Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260523-133538_post_wave760_unwind_continuation_verified`. Next high-signal queue head is `0x005d3f4b Unwind@005d3f4b`; earliest raw commentless row remains `0x0042f220 CSPtrSet__Clear`.

This is saved static retail Ghidra evidence only. Exact parent source body, runtime exception behavior, runtime cleanup behavior, BEA patching, and rebuild parity remain unproven.

The same Wave744 tranche spans `0x005d1610 Unwind@005d1610` through `0x005d1828 Unwind@005d1828`, including camera cleanup, Cannon.cpp allocation cleanup, and SPtrSet stack-local cleanup. Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260522-163423_post_wave744_unwind_continuation_verified`. Next high-signal queue head is `0x005d1840 Unwind@005d1840`; earliest raw commentless row remains `0x0042f220 CSPtrSet__Clear`.

This is saved static retail Ghidra evidence only. Exact parent source body, runtime exception behavior, runtime cleanup behavior, BEA patching, and rebuild parity remain unproven.

## Wave746 unwind continuation callbacks

Wave746 unwind continuation saved `void __cdecl Unwind@...(void)` signatures, comments, and tags for the monitor/active-reader callbacks at `0x005d1ac0 Unwind@005d1ac0`, `0x005d1ac8 Unwind@005d1ac8`, `0x005d1ad3 Unwind@005d1ad3`, `0x005d1b47 Unwind@005d1b47`, and `0x005d1bb1 Unwind@005d1bb1`. The monitor allocation-cleanup rows use monitor.h debug path `0x0062551c`, line `0x5e`, memtype `0x18`, and DATA scope-table xrefs `0x0061a9bc` and `0x0061aa24`; the adjacent active-reader rows call `CGenericActiveReader__dtor` on embedded fields `+0xc` and `+0x24`.

The same Wave746 tranche spans `0x005d1aa3 Unwind@005d1aa3` through `0x005d1cc0 Unwind@005d1cc0`, including Controller.cpp cleanup, CPhysicsScript.cpp allocation cleanup, and WorldPhysicsManager.h cleanup. Tags include `unwind-continuation-wave746` and `wave746-readback-verified`. Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260522-173500_post_wave746_unwind_continuation_verified`. Next high-signal queue head is `0x005d1cd9 Unwind@005d1cd9`; earliest raw commentless row remains `0x0042f220 CSPtrSet__Clear`.

This is saved static retail Ghidra evidence only. Exact parent source body, runtime exception behavior, runtime cleanup behavior, BEA patching, and rebuild parity remain unproven.

## Wave748 unwind continuation callbacks

Wave748 unwind continuation saved `void __cdecl Unwind@...(void)` signatures, comments, and tags for the monitor.h allocation-cleanup callback at `0x005d2199 Unwind@005d2199`. The row has scope-table DATA xref `0x0061b07c`; instruction evidence calls `OID__FreeObject_Callback` on `EBP-0x10` with monitor.h debug path `0x0062551c`, line `0x5e`, and allocation/type value `0x18`.

The same Wave748 tranche spans `0x005d1fc8 Unwind@005d1fc8` through `0x005d222b Unwind@005d222b`, including Cutscene.cpp cleanup, `CDXLandscape__DestroyResourceDescriptorArray_Thunk`, `CParticleManager__RemoveFromGlobalList_Thunk`, and DestructableSegmentsController.cpp cleanup. Tags include `unwind-continuation-wave748` and `wave748-readback-verified`. Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260522-183258_post_wave748_unwind_continuation_verified`. Next high-signal queue head is `0x005d2250 Unwind@005d2250`; earliest raw commentless row remains `0x0042f220 CSPtrSet__Clear`.

This is saved static retail Ghidra evidence only. Exact parent source body, runtime exception behavior, runtime cleanup behavior, BEA patching, and rebuild parity remain unproven.

## Wave751 unwind continuation callbacks

Wave751 unwind continuation saved `void __cdecl Unwind@...(void)` signatures, comments, and tags for the monitor.h allocation-cleanup callback at `0x005d27a9 Unwind@005d27a9`. The row has scope-table DATA xref `0x0061b60c`; instruction evidence calls `OID__FreeObject_Callback` on `*(EBP-0x10)` with monitor.h debug path `0x0062551c`, line `0x5e`, and allocation/type value `0x18`.

The same Wave751 tranche spans `0x005d2730 Unwind@005d2730` through `0x005d29d8 Unwind@005d29d8`, including FrontEnd.cpp and game.cpp cleanup rows. Tags include `unwind-continuation-wave751` and `wave751-readback-verified`. Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260522-204801_post_wave751_unwind_continuation_verified`. Next high-signal queue head is `0x005d29f1 Unwind@005d29f1`; earliest raw commentless row remains `0x0042f220 CSPtrSet__Clear`.

This is saved static retail Ghidra evidence only. Exact parent source body, runtime exception behavior, runtime cleanup behavior, BEA patching, and rebuild parity remain unproven.

## Wave756 unwind continuation callbacks

Wave756 unwind continuation saved `void __cdecl Unwind@...(void)` signatures, comments, and tags for monitor/active-reader cleanup callbacks at `0x005d3480 Unwind@005d3480`, `0x005d3488 Unwind@005d3488`, `0x005d3493 Unwind@005d3493`, `0x005d34b0 Unwind@005d34b0`, `0x005d34ce Unwind@005d34ce`, and `0x005d34f0 Unwind@005d34f0`. DATA scope-table xrefs `0x0061c1c4`, `0x0061c1cc`, `0x0061c1d4`, `0x0061c1fc`, `0x0061c214`, and `0x0061c23c` point at the bodies. The monitor rows jump to `CMonitor__Shutdown` or `CMonitor__Shutdown_Thunk`; the active-reader rows call `CGenericActiveReader__dtor` on embedded fields `+0x0c`, `+0x24`, and `+0x44`.

The same Wave756 tranche spans `0x005d3392 Unwind@005d3392` through `0x005d360c Unwind@005d360c`, including UnitAI/landscape cleanup rows around `0x005d34b8` through `0x005d3503`. Tags include `unwind-continuation-wave756` and `wave756-readback-verified`. Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260523-112625_post_wave756_unwind_continuation_verified`. Next high-signal queue head is `0x005d3614 Unwind@005d3614`; earliest raw commentless row remains `0x0042f220 CSPtrSet__Clear`.

This is saved static retail Ghidra evidence only. Exact parent source body, runtime exception behavior, runtime cleanup behavior, BEA patching, and rebuild parity remain unproven.

## Wave757 unwind continuation callbacks

Wave757 unwind continuation saved `void __cdecl Unwind@...(void)` signatures, comments, and tags for monitor/active-reader cleanup callbacks at `0x005d3614 Unwind@005d3614`, `0x005d3638 Unwind@005d3638`, `0x005d3640 Unwind@005d3640`, `0x005d3668 Unwind@005d3668`, `0x005d3670 Unwind@005d3670`, `0x005d3698 Unwind@005d3698`, `0x005d36b0 Unwind@005d36b0`, and `0x005d36d0 Unwind@005d36d0`. DATA scope-table xrefs `0x0061c354`, `0x0061c384`, `0x0061c38c`, `0x0061c3bc`, `0x0061c3c4`, `0x0061c3f4`, `0x0061c41c`, and `0x0061c444` point at the bodies. The active-reader rows call `CGenericActiveReader__dtor`; the allocation cleanup rows use Monitor.h debug path `0x00622b80`; the set cleanup rows call `CSPtrSet__Clear`.

The same Wave757 tranche spans `0x005d3614 Unwind@005d3614` through `0x005d38a0 Unwind@005d38a0`, including MenuItem.cpp and mesh.cpp cleanup rows. Tags include `unwind-continuation-wave757` and `wave757-readback-verified`. Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260523-120201_post_wave757_unwind_continuation_verified`. Next high-signal queue head is `0x005d38bc Unwind@005d38bc`; earliest raw commentless row remains `0x0042f220 CSPtrSet__Clear`.

This is saved static retail Ghidra evidence only. Exact parent source body, runtime exception behavior, runtime cleanup behavior, BEA patching, and rebuild parity remain unproven.

## Wave553 Tracked Render-Pair Update Helper

`CMonitor__UpdateTrackedRenderPair` (`0x005078f0`) is called from `0x00410c50 CBattleEngineJetPart__Move` with `update_projected_volume = 1` and from `CBattleEngineWalkerPart__Move` with `update_projected_volume = 0`; `RET 0x4` proves one explicit stack flag after `ECX`.

The body walks two tracked render entries at `this+0x18/+0x20`, calls the owner vfunc `+300` to refresh transform state, copies basis data into linked render objects, and when the flag is nonzero applies optional projected-volume orientation data from owner `+0xa0/+0x5c`. This is static Ghidra evidence only; exact Monitor source identity, concrete object layouts, runtime render behavior, and rebuild parity remain unproven.

Wave948 read-only review (`battleengine-transition-effects-review-wave948`) refreshed `0x00410c50` and its BattleEngine bridge under the then-saved Monitor labels. Current static evidence reassigns the caller/callee pair to `0x004081c0 CBattleEngine__Move` and `0x00410c50 CBattleEngineJetPart__Move`, with `0x00411630 CBattleEngineJetPart__HandleGroundEffect` among the child helpers. No mutation was needed. Focused Wave911 re-audit progress after Wave948 is historical campaign telemetry; static export-contract closure remains a metadata-hygiene measure, not semantic proof. Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260528-073152_post_wave948_battleengine_transition_effects_review_verified`. Runtime movement, morph, ground-effect behavior, exact layouts, BEA patching, and rebuild parity remain unproven.

### CMonitor__AddDeletionEvent (0x00401040)

**Purpose:** Register a reader cell with a monitor so the reader can be nulled on monitor deletion.

**Behavior (decompiled):**
1. If `*(monitor + 0x04) == NULL`:
   - allocates `0x10` bytes via `OID__AllocObject(0x10, 0x5e, "Monitor.h", 0x18)`
   - initializes it as an empty `CSPtrSet` (`CSPtrSet__Init`)
   - stores it into `monitor + 0x04`
2. Adds `reader_cell` to the set: `CSPtrSet__AddToHead(*(monitor+0x04), reader_cell)`

**Notes:**
- Many call sites inline equivalent logic instead of calling this helper directly.
- This function uses the `Monitor.h` debug path string (`0x00622b80`), while other call sites use `monitor.h` (`0x0062551c`).
- Some inlined sites initialize the newly allocated set via the thin wrapper `CSPtrSet__ctor` (`0x00505d00`): it calls `CSPtrSet__Init(this)` and returns `this`.

### CMonitor__DeleteDeletionEvent (0x0042d9b0)

**Purpose:** Remove a reader cell from a monitor's deletion list.

**Behavior (decompiled):**
1. If `*(monitor + 0x04) != NULL`:
   - call `CSPtrSet__Remove(*(monitor + 0x04), reader_cell)`
2. Return.

**Notes:**
- This is the explicit unregister companion to `CMonitor__AddDeletionEvent`.
- Called in cleanup paths (for example `CController__dtor`) and listener-removal flows.

### CGenericActiveReader__SetReader (0x00401000)

**Purpose:** The canonical "move this reader to a new target" helper.

Matches Stuart source (`references/Onslaught/activereader.cpp`):
- If `to_read == mToRead`: return
- If old `mToRead`: remove this reader cell from `old + 0x04`
- Assign `mToRead = to_read`
- If new `mToRead`: add this reader cell to `to_read + 0x04`

### CGenericActiveReader__dtor (0x0044b1d0)

**Purpose:** Unregister helper used before freeing/destroying an ActiveReader.

Behavior:
- If `mToRead != NULL` and `*(mToRead + 0x04) != NULL`, remove this reader cell from that set.

### CMonitor__ctor (0x00466120)

**Purpose:** Monitor base constructor.

Behavior:
- Assigns the monitor vtable.
- Initializes `this+0x04` (deletion-list pointer) to NULL.

### CMonitor__scalar_deleting_dtor (0x00419a20)

**Purpose:** Scalar deleting dtor wrapper for monitor-base semantics.

Behavior:
- Calls `CMonitor__Shutdown(this)` first.
- If `(free_flag & 1) != 0`, calls `OID__FreeObject(this)`.

### CMonitor__Shutdown_Thunk (0x0046dbc0)

**Purpose:** Compiler-generated thunk/wrapper.

Behavior:
- Forwards directly to `CMonitor__Shutdown(0x004bac40)`.

### CMonitor::Shutdown / Destructor (0x004bac40)

This is the missing lifecycle half of the system: when a monitor-derived object is shutting down, it walks the deletion list at `this+0x04` and nulls every registered ActiveReader cell.

Decompiled behavior summary:
1. If `this+0x04` (deletion list) is non-null:
   - Initialize iteration (`set->mIterator = set->mFirst`)
   - While iterating:
     - `cell = node->value` (value is a pointer to an ActiveReader cell)
     - `*cell = NULL` (prevents dangling pointer)
     - advance iterator to next node
   - `CSPtrSet__Clear(set)` and `OID__FreeObject(set)`
   - `this+0x04 = NULL`

This matches the internal source intent of `CGenericActiveReader::ToReadDied()` (set `mToRead = NULL`) applied to all registered cells.

### CMonitor__Shutdown_Core (0x004bacb0)

**Purpose:** Shared monitor cleanup implementation used by many class vtables.

Behavior:
- Performs the same deletion-list walk/null and set clear/free as `CMonitor__Shutdown`.
- Does **not** perform the vtable write seen at the start of `CMonitor__Shutdown(0x004bac40)`.

## Cross-References (Examples)

The deletion-list allocation debug path `monitor.h` (`0x0062551c`) is referenced from:
- `CController__Init` (controller monitor list usage)
- `CController__SetToControl` (registers a `CActiveReader<IController>` with `to_control+0x04`)
- `CDestructableSegmentsController__Init` (registers an embedded cell like `obj + 0x10`)
- `CPlayer__dtor` (unregisters embedded cells)
- `CSphereTrigger__Hit` (uses monitor list allocation patterns; Wave505 corrected stale `Update` label)

## Open Questions

| Question | Why it matters |
|----------|----------------|
| Determine which classes actually embed `CMonitor` as a base (vs just using the `monitor+0x04` pattern) | Helps distinguish true monitor-derived objects from other structs that coincidentally have a `+0x04` pointer field |
