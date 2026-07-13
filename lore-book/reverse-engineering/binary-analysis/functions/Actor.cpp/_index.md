# Actor.cpp

<!-- ghidra-full-reaudit-20260713:start -->
> **2026-07-13 live correction closeout:** `0x004df520` → `CActor__dtor_base_Thunk` (was `CActor__dtor_base`); `0x004e0300` comment correction. Current live Ghidra reflects confirmed rows only; older conflicting text below is superseded only where confirmed. Use the [closeout](../../ghidra-full-reaudit-closeout-2026-07-13.md); final per-address decisions and exact before/after metadata are in `reverse-engineering/binary-analysis/ghidra-reviewed-correction-decisions-2026-07-13.jsonl` and `reverse-engineering/binary-analysis/ghidra-reviewed-correction-plan-2026-07-13.json`.
<!-- ghidra-full-reaudit-20260713:end -->

> Actor movement and render interpolation helpers from BEA.exe

## Overview

> **Queue status (2026-05-26):** Ghidra export-contract closure **6113/6113** (Wave900: every function commented; clean-signature proxy; not evidence-grade semantics). Lines below that reference a "next raw commentless" row are **archival wave progress**, not open work.

`CActor` extends the base thing hierarchy with movement state, previous-frame position/orientation, event-driven movement scheduling, and render interpolation helpers. Stuart's source is useful for method names and behavior shape, but saved Ghidra names and signatures remain retail-binary evidence that can be corrected when later source/xref/decompile review disagrees.

Wave1211 (`wave1211-score17-residual-current-risk-review`) re-read and tag-normalized `0x00402030 CActor__StickToGround` as one of `8 score-17 residual current-risk rows` in the current-risk denominator. Fresh evidence preserved the Wave912 source-backed contract: the body calls the base `CThing::StickToGround` path and then copies current position into old-position storage (`mOldPos=mPos`). No rename, signature, comment, function-boundary, or executable-byte change was made. Active current-risk accounting after the wave is `1110/1179 = 94.15%`; verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260607-061324_post_wave1211_score17_residual_current_risk_review_verified`. Runtime actor grounding, exact `CActor` layout, BEA patching behavior, rebuild parity, and no-noticeable-difference parity remain separate proof.

Wave827 actor/SoundManager raw head (`actor-soundmanager-raw-head-wave827`, `wave827-readback-verified`) corrected the raw commentless actor destructor thunk at `0x004df520 CActor__dtor_base_Thunk` and, in the same adjacent raw-head tranche, saved SoundManager/CEffect rows `0x004e0300 CSoundManager__UpdateVolumeForAllSoundEvents`, `0x004e06b0 CSoundManager__DeleteAllSamples`, and `0x004e0820 CEffect__scalar_deleting_dtor`. The actor row is a one-instruction jump thunk to the already-commented `0x004013d0 CActor__dtor_base` body; xref evidence comes from `CActorBase__shared_scalar_deleting_dtor_004bfd00`. Post-Wave827 queue telemetry is `6098` total, `5640` commented, `458` commentless, and strict proxy `5640/6098 = 92.49%`; next raw commentless row is `0x004e1260 CMonitor__UpdateTrackedValueAndDirection`. Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260524-203238_post_wave827_actor_soundmanager_raw_head_verified`. Exact `CSoundManager`, `CSoundEvent`, `CSample`, and `CEffect` field schemas, runtime audio behavior, runtime lifetime behavior, BEA patching, and rebuild parity remain deferred.

Wave1217 (`wave1217-lifecycle-cleanup-tail-current-risk-review`) re-read and comment/tag-normalized the actor-base lifecycle tail rows `CActorBase__shared_scalar_deleting_dtor_004bfd00` and `CActor__dtor_base_Thunk`. Fresh static evidence keeps the shared scalar-deleting wrapper tied to the actor destructor thunk and the canonical `CActor__dtor_base` body, with no rename, signature, function-boundary, or executable-byte change. Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260607-110625_post_wave1217_lifecycle_cleanup_tail_current_risk_review_verified`. Runtime actor cleanup behavior, exact layouts, exact source identity, BEA patching behavior, rebuild parity, and no-noticeable-difference parity remain separate proof.

## Functions

| Address | Name | Status | Source shape | Notes |
| --- | --- | --- | --- | --- |
| `0x00401b50` | `CActor__GetFractionTime` | RENAMED | `CActor::GetFractionTime()` | Corrected on 2026-05-09 from the stale `CMCMine__ComputeClampedScaleFactor` label; calls virtual `GetMoveMultiplier`, reads a last-move-time-style field at `this+0xd8`, and clamps the interpolation fraction. |
| `0x00401be0` | `CActor__GetRenderPos` | RENAMED | `CActor::GetRenderPos()` | Corrected on 2026-05-09 from generic `VFuncSlot_00_00401be0`; writes a hidden-return `FVector` output from old/current position interpolation. |
| `0x00401c50` | `CActor__GetRenderOrientation` | RENAMED | `CActor::GetRenderOrientation()` | Corrected on 2026-05-09 from generic `VFuncSlot_01_00401c50`; writes a hidden-return `FMatrix` output from old/current orientation interpolation and row-copy helpers. |
| `0x00402030` | `CActor__StickToGround` | RENAMED | `CActor::StickToGround()` | Wave912 corrected the provisional slot-18 label to the source-backed actor method name. Retail body calls the base `CThing::StickToGround` path, then copies current position/vector dwords into old-position storage (`mOldPos=mPos`). |

## Details

### Wave761 Actor Unwind Continuation

Wave761 static read-back (`unwind-continuation-wave761`, `wave761-readback-verified`) saved `0x005d3f69 Unwind@005d3f69` and `0x005d3f80 Unwind@005d3f80` as `void __cdecl Unwind@...(void)` compiler-generated SEH unwind cleanup callbacks. DATA scope-table xrefs `0x0061cac4` and `0x0061caec` point at the bodies; instruction/decompile evidence loads `ECX` from `*(EBP+0x4)` and `*(EBP-0x10)` respectively, then jumps to `CActor__dtor_base`. Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260523-140318_post_wave761_unwind_continuation_verified`. This is saved static retail Ghidra evidence only; exact parent source-body identity, runtime actor cleanup behavior, runtime exception behavior, BEA patching, and rebuild parity remain deferred.

### Wave760 Actor Unwind Continuation

Wave760 static read-back (`unwind-continuation-wave760`, `wave760-readback-verified`) saved `0x005d3dd6 Unwind@005d3dd6` as a `void __cdecl Unwind@005d3dd6(void)` compiler-generated SEH unwind cleanup callback. DATA scope-table xref `0x0061ca04` points at the body; instruction/decompile evidence loads `ECX` from `*(EBP+0x4)` and jumps to `CActor__dtor_base`. Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260523-133538_post_wave760_unwind_continuation_verified`. This is saved static retail Ghidra evidence only; exact parent source-body identity, runtime actor cleanup behavior, runtime exception behavior, BEA patching, and rebuild parity remain deferred.

### Actor Render Signature Correction (2026-05-09)

- `0x00401b50` now has the saved signature `float __thiscall CActor__GetFractionTime(void * this)`.
- `0x00401be0` now has the saved signature `void __thiscall CActor__GetRenderPos(void * this, void * outRenderPos)`.
- `0x00401c50` now has the saved signature `void __thiscall CActor__GetRenderOrientation(void * this, void * outRenderOrientation)`.
- The old CMCMine scale-helper label at `0x00401b50` was corrected because source parity, position in the Actor function cluster, virtual `GetMoveMultiplier` usage, `this+0xd8` timing context, and clamp behavior match `CActor::GetFractionTime()`.
- The two adjacent generic `VFuncSlot_*` labels were corrected because source parity and decompile shape match Actor render-position and render-orientation by-value returns, represented in Ghidra as hidden output pointer parameters.
- This is saved name/signature/comment refinement only; concrete `CActor`, `FVector`, or `FMatrix` layouts, tags, local names, structure types, runtime rendering behavior, complete subclass vtable ownership, and rebuild parity remain open.

### Wave912 Actor StickToGround Correction (2026-05-27)

- `0x00402030` now has the saved signature `void __thiscall CActor__StickToGround(void * this)`.
- Wave912 supersedes the provisional `CActor__VFunc_18_SyncOldVectorAfterBaseCall` label. Source `CActor::StickToGround()` calls `SUPERTYPE::StickToGround()` and then assigns `mOldPos=mPos`, matching the retail body call to the base `CThing::StickToGround` path and copies from `this+0x1c..0x28` into `this+0x8c..0x98`.
- This is source-backed naming plus retail read-back evidence; concrete `CActor`/`FVector` layout, runtime movement behavior, BEA patching, and rebuild parity remain separate proof.
