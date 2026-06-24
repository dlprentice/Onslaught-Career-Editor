# CUMTexture.cpp - Function Analysis

Last updated: 2026-05-18

## Source And Evidence Status

Current `CUMTexture` coverage is saved Steam retail Ghidra evidence only. The Wave522 tranche used metadata, decompile, xrefs, instruction RET cleanup, vtable-slot exports, and caller context from `CLandscapeTexture`, `CDXShadows`, and `CDXFrontEndVideo`.

Treat this page as static binary evidence, not source-body parity, runtime GPU behavior proof, BEA launch proof, game patching, or rebuild parity.

## Wave849 D3D State/Cache Core Read-Back

Wave849 D3D state/cache core (`d3d-state-cache-core-wave849`, `wave849-readback-verified`) strengthened the external texture-format/create helpers used by `CUMTexture__RecreateTextureResource`: `0x00513760 CEngine__TextureFormatField32FD4ToIndex` and `0x00513a10 CEngine__CreateTextureUnchecked`. Probe token anchor: `Wave849 D3D state/cache core`; `0x00513760 CEngine__TextureFormatField32FD4ToIndex`; `0x00513a10 CEngine__CreateTextureUnchecked`; `CUMTexture__RecreateTextureResource`; `5691/6098 = 93.33%`; `0x00513a80 PlatformInput__GetKeyState3Core`; `G:\GhidraBackups\BEA_20260525-073710_post_wave849_d3d_state_cache_core_verified`.

The rename from stale `CEngine__ReleaseField32FD4` to `CEngine__TextureFormatField32FD4ToIndex` is based on the helper loading `this+0x32fd4`, calling `CEngine__TextureFormatD3DToIndex`, and callers using `EAX` as a texture-format index. Exact CEngine field name, complete format table semantics, runtime texture behavior, BEA patching, and rebuild parity remain deferred.

> **Queue status (2026-05-26):** Ghidra export-contract closure **6113/6113** (Wave900: every function commented; clean-signature proxy; not evidence-grade semantics). Lines below that reference a "next raw commentless" row are **archival wave progress**, not open work.

## Overview

`CUMTexture` is a small texture-resource wrapper used by landscape mip textures, shadow textures, and frontend Bink video texture allocation. The observed body stores texture creation mode fields, owns a texture/resource pointer at `+0x08`, can recreate that resource through `CEngine__CreateTextureUnchecked`, and can release it through the pointed object's virtual release slot.

## Vtable Context

| Address | Current evidence |
| --- | --- |
| `0x005df908` | Primary `CUMTexture` vtable. Slot 0 is `CUMTexture__scalar_deleting_dtor`, slot 2 is `CUMTexture__RecreateTextureResource`, slot 3 is `CUMTexture__VFunc_03_ReleaseTextureResource`, and slots 1/4 currently resolve to shared return-zero behavior. Rows beyond slot 4 include non-vtable spillover candidates and must not be treated as complete vtable recovery. |
| `0x005dc1f0` | `CLandscapeTexture` secondary vtable-adjacent table. Slot 3 points to `CUMTexture__VFunc_03_ReleaseTextureResource`; surrounding rows still include unresolved/non-function pointers and remain provisional. |

## Key Observed Offsets

| Offset | Observed role |
| ---: | --- |
| `+0x00` | Vtable pointer. |
| `+0x08` | Owned texture/resource pointer released through virtual slot `+0x08`. |
| `+0x0c` | Requested texture format/mode-derived format selector. |
| `+0x10` | Mode-derived mip/flag value passed to texture creation. |
| `+0x14` | Texture size/pointer-sized value passed by callers. |
| `+0x18` | Texture count/depth value passed by callers. |
| `+0x1c` | Mode-derived shared/usage flag passed to texture creation. |
| `+0x24` | Resolved D3D texture format, copied from `+0x0c` or computed via `CEngine__TextureFormatIndexToD3D`. |

The offsets above are observed static use-sites, not a complete concrete class layout.

## Functions

| Address | Saved signature | Evidence notes |
| --- | --- | --- |
| `0x004f79d0` | `void * __fastcall CUMTexture__ctor_base(void * this)` | Installs vtable `0x005df908`, clears owned texture pointer `+0x08`, calls `CShaderBase__Init`, and returns `this`. Xrefs include `CLandscapeTexture__ConstructorMip`, `CDXShadows__Init`, and `CDXFrontEndVideo__InitVideo`. |
| `0x004f7a20` | `void * __thiscall CUMTexture__scalar_deleting_dtor(void * this, byte delete_flags)` | Vtable `0x005df908` slot 0. `RET 0x4` proves one explicit stack argument after ECX. Calls `CUMTexture__dtor_base`, then frees `this` through `CDXMemoryManager__Free` when `delete_flags & 1` is set. |
| `0x004f7a40` | `void __fastcall CUMTexture__dtor_base(void * this)` | Restores vtable `0x005df908`, calls Wave561 `CShaderBase__UnlinkFromRenderObjectLists` for the shared render/device-object lists, releases owned texture pointer `+0x08` when present, clears it, and delegates to base cleanup label `0x00512d50`. |
| `0x004f7ab0` | `int __thiscall CUMTexture__ConfigureByMode(void * this, void * texture_size, int mode, int texture_count_or_depth)` | `RET 0x0c` proves three explicit stack arguments after ECX. Stores size/count fields, maps observed modes `0`, `1`, `3`, `4`, and `5` into format/mip/shared fields, dispatches vtable slot `+0x08`, and preserves the result for callers that check failure. |
| `0x004f7b60` | `int __fastcall CUMTexture__RecreateTextureResource(void * this)` | Vtable `0x005df908` slot 2 and direct `CLandscapeTexture__Reset` target. Resolves format into `+0x24`, releases any existing `+0x08` resource, then calls `CEngine__CreateTextureUnchecked` with fields from `+0x14/+0x18/+0x10/+0x24/+0x1c` and output pointer `this+0x08`. |
| `0x004f7bd0` | `int __fastcall CUMTexture__VFunc_03_ReleaseTextureResource(void * this)` | Vtable `0x005df908` slot 3 and `CLandscapeTexture` secondary table `0x005dc1f0` slot 3. Releases owned texture pointer `+0x08` when present, clears it, and returns `0`. |

## Caller Context

| Caller | Evidence |
| --- | --- |
| `CLandscapeTexture__ConstructorMip` | Calls `CUMTexture__ctor_base(this)` before installing the landscape texture secondary vtable. |
| `CLandscapeTexture__Init` | Calls `CUMTexture__ConfigureByMode(this, DAT_0062d864, 1, 1)` after Wave522 signature correction removes the stale extra register-carryover argument. |
| `CLandscapeTexture__Reset` | Calls `CUMTexture__RecreateTextureResource(this)` and treats a negative result as failure. |
| `CDXShadows__Init` | Allocates `CUMTexture` objects, configures them with shadow texture size, mode `0`, and count/depth `1`, and reports failures through the HRESULT path. |
| `CDXFrontEndVideo__InitVideo` | Allocates two `CUMTexture` objects for video double buffering and calls `CUMTexture__ConfigureByMode(texture, selected_size, 5 - (DAT_008a9a54 != 0), 1)`. |

## Wave522 Saved Corrections

Wave522 saved signatures, comments, tags, and owner corrections for the six `CUMTexture` targets listed above.

| Address | Previous state | Saved state |
| --- | --- | --- |
| `0x004f79d0` | `CUMTexture__ctor_like_004f79d0` with `param_1` | `CUMTexture__ctor_base(void * this)` |
| `0x004f7a20` | `CUMTexture__VFunc_00_004f7a20` with stale generic params | `CUMTexture__scalar_deleting_dtor(void * this, byte delete_flags)` |
| `0x004f7a40` | `CUMTexture__ctor_like_004f7a40` | `CUMTexture__dtor_base(void * this)` |
| `0x004f7ab0` | Four explicit `param_N` arguments in Ghidra | Three explicit stack arguments after ECX: `texture_size`, `mode`, and `texture_count_or_depth` |
| `0x004f7b60` | `CUMTexture__VFunc_02_004f7b60` | `CUMTexture__RecreateTextureResource(void * this)` |
| `0x004f7bd0` | `VFuncSlot_03_004f7bd0` | `CUMTexture__VFunc_03_ReleaseTextureResource(void * this)` |

The dry run reported `updated=0 skipped=6 renamed=0 would_rename=5 missing=0 bad=0`; the apply reported `updated=6 skipped=0 renamed=5 would_rename=0 missing=0 bad=0`, with `REPORT: Save succeeded`.

Read-back verified `6` metadata rows, `6` tag rows, `15` xref rows, `366` instruction rows, `6` target decompile exports, `6` context metadata rows, `6` context decompile exports, `16` vtable-slot rows, focused probe status `PASS`, and refreshed queue counts of `6082` functions, `2477` commented functions, `3605` commentless functions, `1594` exact-undefined signatures, and `1381` `param_N` signatures. The actual live Ghidra project backup was verified at `G:\GhidraBackups\BEA_20260517-235521_post_wave522_cumtexture_verified` with `19` files, `158731143` bytes, `MissingCount=0`, `ExtraCount=0`, and `HashDiffCount=0`.

## Remaining Limits

- Runtime GPU texture creation/upload behavior is not proven.
- Runtime texture lifetime behavior is not proven.
- Complete concrete `CUMTexture`, `CLandscapeTexture`, and texture-resource layouts are not proven.
- Exact source class/file identity and source-body parity are not proven.
- Vtable-adjacent rows remain provisional beyond the validated slots.
- BEA was not launched, patched, or debugged in this wave.
- This does not prove rebuild parity or game-behavior equivalence.
