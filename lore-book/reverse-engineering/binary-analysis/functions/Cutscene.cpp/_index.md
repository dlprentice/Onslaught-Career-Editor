# Cutscene.cpp Functions

> Source File: Cutscene.cpp | Binary: BEA.exe
> Debug Path: 0x0062811c

> **Queue status (2026-05-26):** Ghidra export-contract closure **6113/6113** (Wave900: every function commented; clean-signature proxy; not evidence-grade semantics). Lines below that reference a "next raw commentless" row are **archival wave progress**, not open work.

## Overview

Cutscene playback system. CCutscene handles loading, playing, and managing in-game cutscenes with animation slots and audio synchronization.

Wave908 audio/media/cutscene static review (`audio-media-cutscene-static-review-wave908`) records `CCutscene 14`, `CRTCutscene 12`, and `CCutsceneAnimNode 1` inside the static-coherent audio/media/cutscene/camera core. The read-only `171` selected-row, `26` family slice ties cutscene load/start/update/track-slot helpers to the adjacent audio/video/camera rows through anchors `CCutscene__Load`, `CCutscene__Start`, `CCutscene__Update`, `CCutscene__SetTrackSlotByFlag`, `CRTCutscene__BuildCurrentFrameOutputs`, `CDXFMV__VFunc_06_0053f180`, and `CFMV__PlayFullscreenWithLoadingGate`. Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260526-113941_post_wave908_audio_media_cutscene_static_review_verified`. Runtime cutscene playback/sync, video playback, exact layouts/source identity, patch behavior, and clean-room rebuild parity remain separate proof.

## 2026-05-25 Wave865 Render Tail Read-Back

Wave865 render tail static read-back (`render-tail-wave865`, `wave865-readback-verified`) hardened `0x0053f010 CCutscene__SetTrackSlotByFlag` as `void __thiscall CCutscene__SetTrackSlotByFlag(void * this, int track_slot, int use_primary_track)`. Static xrefs from `CGame__LoadLevel`, `CCutscene__Start`, `CCutscene__Stop`, and `CCutscene__Update` pass two stack arguments; the body writes `track_slot` to `this+0x4cc` when `use_primary_track` is nonzero and `this+0x4d0` otherwise. Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260525-160100_post_wave865_render_tail_verified`. Exact cutscene track-slot semantics, source identity, runtime cutscene behavior, BEA patching, and rebuild parity remain deferred.

## Functions

| Address | Name | Purpose | Size |
|---------|------|---------|------|
| 0x0043e8e0 | CCutscene__dtor_base | Destructor body; corrected from stale scalar-deleting wrapper label | ~400 bytes |
| 0x0043ea90 | CCutscene__scalar_deleting_dtor | Scalar-deleting destructor wrapper | ~20 bytes |
| 0x0043eab0 | CCutscene__Init | Init body that copies init-name context, calls load, and delegates base init | ~500 bytes |
| 0x0043eca0 | CCutscene__ClearAnimationsAndStop | Recovered boundary that clears animation-slot lists and calls the stop slot | ~120 bytes |
| 0x0043ed20 | CCutsceneAnimNode__DestroyRecursive | Recursive animation-node cleanup, not whole-cutscene destruction | ~80 bytes |
| 0x0043ed80 | CCutscene__Load | Load cutscene from `.cut` file and dispatch add-animation entries | ~600 bytes |
| 0x0043f210 | CCutscene__AddAnimation | Add animation node to cutscene track context | ~200 bytes |
| 0x0043f690 | CCutscene__Update | Frame-by-frame playback/update context | ~800 bytes |
| 0x0043f510 | CCutscene__InitAnimations | Initialize animation slots | ~300 bytes |
| 0x0053f010 | CCutscene__SetTrackSlotByFlag | Wave865 track-slot write helper selected by a boolean flag | read-back documented |

## Additional Functions (No debug path ref)

| Address | Name | Purpose |
|---------|------|---------|
| 0x0043f340 | CCutscene__Start | Start cutscene playback |
| 0x0043f420 | CCutscene__Stop | Stop and cleanup cutscene |
| 0x0043fa70 | CCutscene__PrepareAnimations | Calculate durations |
| 0x0043fcb0 | CCutscene__EventDispatchUpdate | Recovered event-dispatch boundary; event code `3000` calls update, otherwise delegates base handler |
| 0x0043fcd0 | CCutscene__ForceEnd | Force-end via global pointer |

## Exception Handlers

| Address | Name | Line | Purpose |
|---------|------|------|---------|
| 0x005d1fc8 | Unwind@005d1fc8 | static | Cleanup for embedded active reader at `(*(EBP-0x10))+0x854` |
| 0x005d1fd6 | Unwind@005d1fd6 | static | Cleanup for resource descriptor at `(*(EBP-0x10))+0x958` |
| 0x005d1ff0 | Unwind@005d1ff0 | 203 | Cleanup for Load 16-byte allocation |
| 0x005d2020 | Unwind@005d2020 | 549 | Cleanup for Update 156-byte allocation |

## Key Observations

- **File format** - Loads from `data\cutscenes\%s.cut`
- **Animation slots** - 32 animation slot pointers at offset 0x7c
- **Frame-based** - Playback uses frame counter with audio sync
- **Global pointer** - Current cutscene stored at DAT_0066ea20
- **VTable context** - Wave 345 read-back recorded checked slots on `0x005dad88`, `0x005dae00`, and `0x005dae80`; older single-vtable wording was incomplete.
- **Saved Ghidra state** - Wave 345 saved names, signatures, comments, and tags for 14 targets and recovered 2 missing boundaries. Runtime cutscene playback, exact source identities beyond the static evidence, complete `.cut` format recovery, concrete layouts, locals/types, and rebuild parity remain open.

## Wave748 Unwind Continuation Read-Back

Wave748 unwind continuation saved `void __cdecl Unwind@...(void)` signatures, comments, and tags for Cutscene.cpp cleanup callbacks at `0x005d1fc8 Unwind@005d1fc8`, `0x005d1fd6 Unwind@005d1fd6`, `0x005d1ff0 Unwind@005d1ff0`, and `0x005d2020 Unwind@005d2020`. The rows have DATA scope-table xrefs from `0x0061ae64`, `0x0061ae6c`, `0x0061ae94`, and `0x0061aebc`; observed bodies call `CGenericActiveReader__dtor`, `CResourceDescriptor__dtor`, or `OID__FreeObject_Callback` with the Cutscene.cpp debug path at `0x0062811c`.

The same `unwind-continuation-wave748` tranche spans `0x005d1fc8 Unwind@005d1fc8` through `0x005d222b Unwind@005d222b` and is verified by backup `[maintainer-local-ghidra-backup-root]\BEA_20260522-183258_post_wave748_unwind_continuation_verified`. Next high-signal queue head is `0x005d2250 Unwind@005d2250`; earliest raw commentless row remains `0x0042f220 CSPtrSet__Clear`.

This is saved static retail Ghidra evidence only. Exact parent source body, runtime exception behavior, runtime cleanup behavior, BEA patching, and rebuild parity remain unproven.

## CCutscene Class Structure (Partial)

| Offset | Size | Field | Notes |
|--------|------|-------|-------|
| 0x000 | 4 | vtable | CCutscene vtable |
| 0x01c | 16 | cameraData | Camera position/rotation |
| 0x07c | 128 | animSlots[32] | Animation slot pointers |
| 0x5a8 | 256 | cutsceneName | Cutscene name string |
| 0x6b8 | 1 | isPlaying | Playing flag |
| 0x6bc | 128 | animCounts[32] | Animation count per slot |
| 0x840 | 1 | cameraRestoreFlag | Restore camera on end |
| 0x841 | 1 | dirtyFlag | Needs re-initialization |
| 0x844 | 4 | frameStart | Start frame |
| 0x848 | 4 | totalFrames | Total frame count |

## CCutsceneAnim Structure

| Offset | Size | Field | Notes |
|--------|------|-------|-------|
| 0x008 | 256 | animName | Animation name |
| 0x108 | 32 | meshName | Mesh name |
| 0x12d | 256 | audioName | Audio file name |
| 0x234 | 4 | duration | Duration in frames |
| 0x23c | 4 | startFrame | Start frame in cutscene |
| 0x248 | 4 | next | Next in linked list |

## Related Files

- RTCutscene.cpp - Real-time cutscene variant
- Music.cpp - Audio playback

---
*Discovered via Phase 1 xref analysis (Dec 2025)*
