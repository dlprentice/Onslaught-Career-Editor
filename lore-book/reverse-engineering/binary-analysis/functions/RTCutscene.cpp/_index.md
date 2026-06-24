# RTCutscene.cpp Functions

> Source File: RTCutscene.cpp | Binary: BEA.exe
> Debug Path: 0x00631e2c (`C:\dev\ONSLAUGHT2\RTCutscene.cpp`)
> RTTI: 0x00631e18 (`.?AVCRTCutscene@@`)

> **Queue status (2026-05-26):** Ghidra export-contract closure **6113/6113** (Wave900: every function commented; clean-signature proxy; not evidence-grade semantics). Lines below that reference a "next raw commentless" row are **archival wave progress**, not open work.

Wave1218 (wave1218-generic-shared-vfunc-thunk-tail-current-risk-review) re-read 0x004d6b20 SharedVFunc__ReturnZero_004d6b20 as part of the generic/shared vfunc-thunk tail current-risk review. The row remains a broad owner-neutral return-zero vtable/callsite target, with no mutation, no rename, no signature change, no comment change, no tag change, no function-boundary change, and no executable-byte change. Verified backup: G:\GhidraBackups\BEA_20260607-222830_post_wave1218_generic_shared_vfunc_thunk_tail_current_risk_review_verified. Runtime cutscene/frontend behavior, exact owner coverage, exact layouts, and rebuild parity remain separate proof.

## Overview

`CRTCutscene` is the real-time cutscene render object created by `PCRTID__CreateObject` for type id `5`. Wave489 converted the old RTCutscene page from a mostly Phase-1/vtable skeleton into saved static Ghidra evidence for the RTCutscene vtable cluster plus adjacent `CRenderThing` base helpers and shared vtable returns.

This page is still static retail-binary evidence. It does not prove exact source identity, complete class layouts, runtime visual behavior, BEA launch behavior, or rebuild parity.

Wave908 audio/media/cutscene static review (`audio-media-cutscene-static-review-wave908`) keeps the real-time cutscene render object in the static-coherent audio/media/cutscene/camera core. The read-only slice records `CRTCutscene 12` in the `171` selected-row, `26` family evidence set, with anchor `CRTCutscene__BuildCurrentFrameOutputs` tying current-frame render outputs back to the broader `CCutscene__Update`/camera/media path. Verified backup: `G:\GhidraBackups\BEA_20260526-113941_post_wave908_audio_media_cutscene_static_review_verified`. Runtime visual behavior, exact output-record layout, source identity, patch behavior, and rebuild parity remain unproven.

Wave1046 (`renderthing-crttree-review-wave1046`) re-read the shared `CRenderThing` helpers used by the RTCutscene vtable with no mutation. Fresh evidence reconfirmed `0x004dbb80 CRenderThing__VFunc_07_ClearRenderOutputs`, `0x004dbbe0 CRenderThing__VFunc_08_ClearVec3`, `0x004dbd20 CRenderThing__dtor`, `0x004dbd50 CRenderThing__scalar_deleting_dtor`, and `0x004db880 CRenderThing__ForwardSlot26ToChildSlot68` against vtable anchors `0x005dea38` and `0x005deaac`, render-output block `0x0083ccd8`, and child-forwarding slot evidence. Queue closure remains `6246/6246 = 100.00%`; expanded static surface progress is `993/1509 = 65.81%`. Verified backup: `G:\GhidraBackups\BEA_20260601-120449_post_wave1046_renderthing_crttree_review_verified`. Runtime cutscene/render-output behavior, exact `CRenderThing`/`CRTCutscene`/output-record layouts, exact source virtual names, BEA patching, gameplay outcomes, and rebuild parity remain separate proof.

## Wave489 Status

Wave489 saved and read back `20` targets:

- `10` previously missing compact/vtable function boundaries were created or recovered.
- `6` stale names were corrected, including destructor/base-helper labels.
- `20` signatures/comments/tags were hardened and verified through metadata, tags, vtable export, xrefs, instruction export, decompile export, and the focused probe.
- The RTCutscene vtable at `0x005dea38` now has function objects at all `20` exported slots.

## Vtable Layout (0x005dea38)

| Slot | Address | Saved name | Evidence boundary |
| ---: | --- | --- | --- |
| 0 | `0x004dbc30` | `CRTCutscene__scalar_deleting_dtor` | Calls `CRTCutscene__dtor`, optional free, `RET 0x4` |
| 1 | `0x004dbd80` | `CRTCutscene__Init` | Initializes arrays/name buffers from `init_record` |
| 2 | `0x004dbec0` | `CRTCutscene__RenderCurrent` | Active/current-index gate, transform staging, render dispatch |
| 3 | `0x0040c640` | `DebugTrace` | Shared debug trace target |
| 4 | `0x00405930` | `SharedVFunc__ReturnZero_00405930` | Shared zero-return target |
| 5 | `0x00405940` | `SharedVFunc__ReturnZeroRet4_00405940` | Created compact return-0, `RET 0x4` body |
| 6 | `0x004dbfb0` | `CRTCutscene__GetDefaultScalar` | Returns global float at `0x005d856c` |
| 7 | `0x004dbb80` | `CRenderThing__VFunc_07_ClearRenderOutputs` | Clears output lanes and copies `0x0083ccd8` matrix block |
| 8 | `0x004dbbe0` | `CRenderThing__VFunc_08_ClearVec3` | Clears three dwords at caller output |
| 9 | `0x004dbf80` | `CRTCutscene__GetCurrentMesh` | Active/current-index mesh pointer getter |
| 10 | `0x00405930` | `SharedVFunc__ReturnZero_00405930` | Shared zero-return target |
| 11 | `0x00459990` | `CFrontEndPage__DeActiveNotification` | Inherited/shared target, not reclassified in Wave489 |
| 12 | `0x004dbe50` | `CRTCutscene__Activate` | Resolves element names with `CMesh__FindOrCreate(name, 1)` |
| 13 | `0x004dbe90` | `CRTCutscene__Reset` | Frees active mesh-pointer array and clears state |
| 14 | `0x004dbfc0` | `CRTCutscene__GetCurrentMeshEntryValue` | Forwards to `CMesh__FindEntryValueByTypeId` when current mesh exists |
| 15 | `0x004014a0` | `SharedVFunc__Return1_004014a0` | Shared return-1 target |
| 16 | `0x004014a0` | `SharedVFunc__Return1_004014a0` | Shared return-1 target |
| 17 | `0x004dbff0` | `CRTCutscene__BuildCurrentFrameOutputs` | Builds/falls back output records for current frame state |
| 18 | `0x004d6b20` | `SharedVFunc__ReturnZero_004d6b20` | Broad shared zero-return target |
| 19 | `0x004dbc10` | `SharedVFunc__ReturnMinusOneRet4_004dbc10` | Created compact return-minus-one, `RET 0x4` body |

## Class Layout Evidence (Partial)

| Offset | Observed role | Evidence |
| ---: | --- | --- |
| `0x00` | vtable | Constructor installs `0x005dea38`; destructor restores `CRTCutscene` then `CRenderThing` vtable states |
| `0x04` | playback/default scalar | `CRTCutscene__Init` writes `1.0f` |
| `0x08` | render/base state gate | `CRTCutscene__GetCurrentMesh` requires nonzero before returning active mesh |
| `0x10` | child/owned pointer | `CRenderThing__dtor` dispatches slot 0 with delete flag 1 when non-null |
| `0x14` | mesh-pointer array | Allocated by `CRTCutscene__Init`, populated by `CRTCutscene__Activate`, freed by reset/dtor |
| `0x18` | element count | Read from `init_record+0x418` |
| `0x1c` | name-buffer table | Holds allocated `0x100` byte name buffers copied from `init_record+0x414` |
| `0x20` | active flag | Set by activate, cleared by reset/dtor |
| `0x24` | current index | Set to `-1` (`0xffffffff`) by init/reset and written by `CRTCutscene__SetCurrentIndex` |

## Function Details

| Address | Saved name | Summary |
| --- | --- | --- |
| `0x004d6a30` | `CRenderThing__Init` | Base initializer called by `CRTCutscene__Init` and `CRTMesh__Init`; copies `init_record+0x400`, writes marker `0x3727c5ac`, clears `this+0x0c`. |
| `0x004d6b20` | `SharedVFunc__ReturnZero_004d6b20` | Broad shared vtable/callsite zero-return target; kept owner-neutral. |
| `0x00405940` | `SharedVFunc__ReturnZeroRet4_00405940` | Compact return-0 body with one stack argument cleaned by `RET 0x4`. |
| `0x004dbb60` | `CRTCutscene__CRTCutscene` | Constructor called from `PCRTID__CreateObject`; clears `this+0x10`, installs vtable, clears count. |
| `0x004dbb80` | `CRenderThing__VFunc_07_ClearRenderOutputs` | Shared render-output helper; clears three dwords of one output, writes a fourth observed lane, and copies the `0x0083ccd8` block. |
| `0x004dbbe0` | `CRenderThing__VFunc_08_ClearVec3` | Shared helper that clears three dwords at caller-provided output. |
| `0x004dbc10` | `SharedVFunc__ReturnMinusOneRet4_004dbc10` | Compact return-`-1` body with one stack argument cleaned by `RET 0x4`. |
| `0x004dbc30` | `CRTCutscene__scalar_deleting_dtor` | Wrapper calls `CRTCutscene__dtor`, optionally frees `this`, returns object pointer. |
| `0x004dbc50` | `CRTCutscene__dtor` | Frees active mesh-pointer array, name buffers/table, restores base vtable, and delegates owned child cleanup. |
| `0x004dbd20` | `CRenderThing__dtor` | Corrected away from old ctor-like wording; restores base vtable and destroys owned child pointer at `this+0x10`. |
| `0x004dbd50` | `CRenderThing__scalar_deleting_dtor` | Base scalar-deleting destructor wrapper with optional `CDXMemoryManager__Free(&DAT_009c3df0, this)`. |
| `0x004db880` | `CRenderThing__ForwardSlot26ToChildSlot68` | Wave497 recovered shared render-object forwarding helper; forwards two stack arguments through child pointer `this+0x10` vtable slot `+0x68` when present. |
| `0x004dbc00` | `SharedVFunc__ReturnFalseRet4_004dbc00` | Wave497 recovered broad shared false-return helper, `RET 0x4`; CRTTree and several other vtable families reference it. |
| `0x004dbd80` | `CRTCutscene__Init` | Calls base init, allocates mesh-pointer/name tables with RTCutscene.cpp allocator tags, copies names, clears active, sets current index to `-1`. |
| `0x004dbd40` | `SharedVFunc__ReturnFloat0Ret8_004dbd40` | Wave497 recovered broad shared float-default helper returning `_DAT_005d856c`, `RET 0x8`. |
| `0x004d6a50` | `SharedVFunc__WriteDefaultTransformOutputsRet16_004d6a50` | Wave497 recovered shared default-output helper writing identity-like transform defaults, zero vector output, and `0x42b40000`, `RET 0x10`. |
| `0x004dbe50` | `CRTCutscene__Activate` | Resolves each saved name through `CMesh__FindOrCreate(name, 1)`, stores mesh pointers, sets active. |
| `0x004dbe90` | `CRTCutscene__Reset` | If active, frees mesh-pointer array, clears active, sets current index to `-1`. |
| `0x004dbec0` | `CRTCutscene__RenderCurrent` | Active/current-index gated render path that stages transform state and calls a `CSphere__RenderAnimatedRecursive`-style renderer; exact runtime visual behavior is unproven. |
| `0x004dbf70` | `CRTCutscene__SetCurrentIndex` | Writes `current_index` into `this+0x24`; observed callers include `CCutscene__Update` and `CCutscene__PrepareAnimations`. |
| `0x004dbf80` | `CRTCutscene__GetCurrentMesh` | Returns null unless base state, active flag, and current index are valid; otherwise returns `this+0x14[currentIndex]`. |
| `0x004dbfb0` | `CRTCutscene__GetDefaultScalar` | Returns the global float at `0x005d856c`. |
| `0x004dbfc0` | `CRTCutscene__GetCurrentMeshEntryValue` | Gets current mesh and forwards `type_id/out_index` to `CMesh__FindEntryValueByTypeId`, else returns default scalar. |
| `0x004dbff0` | `CRTCutscene__BuildCurrentFrameOutputs` | Builds current-frame output records or falls back to identity/default outputs; exact argument names and record layouts remain open. |

## Evidence

- Apply/probe artifacts: `subagents/ghidra-static-reaudit/wave489-rtcutscene-renderthing-004d6a30/`
- Focused probe: `tools/ghidra_rtcutscene_wave489_probe.py`
- Read-back exports: `post_metadata.tsv`, `post_tags.tsv`, `post_vtable.tsv`, `post_xrefs.tsv`, `post_instructions.tsv`, and `post-decomp/`.
- Queue refresh after Wave489: `6068` functions, `2213` commented, `3855` commentless, `1676` undefined signatures, `1538` `param_N` signatures.

## Related Files

- [Cutscene.cpp](../Cutscene.cpp/_index.md) - full-screen cutscene/update caller context
- [PCRTID.cpp](../PCRTID.cpp/_index.md) - runtime CRT object factory
- [rtmesh.cpp](../rtmesh.cpp/_index.md) - neighboring render-object vtable/base-init context

## Outstanding Work

- Prove exact source names where the retail body differs from the broad source hints.
- Recover concrete `CRTCutscene`, `CRenderThing`, mesh-entry, and output-record types.
- Runtime-test real cutscene activation/render behavior.
- Keep shared vfunc helpers owner-neutral unless future vtable evidence proves a narrower contract.

---

Last updated by Wave489 static Ghidra re-audit (2026-05-17).
