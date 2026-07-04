# ibuffer.cpp - Index Buffer System

**Retail debug path:** `[maintainer-local-source-export-root]\ibuffer.cpp`
**Debug string address:** `0x0062d390`
**RTTI type:** `.?AVCIBuffer@@` at `0x0062d380`
**VTable address:** `0x005dbec4`

> **Queue status (2026-05-31):** Ghidra export-contract closure **6238/6238** (Wave1013: every function commented; clean-signature proxy; not evidence-grade semantics). Lines below that reference a "next raw commentless" row are **archival wave progress**, not open work.

## Overview

`CIBuffer` is the retail Direct3D index-buffer wrapper. The available Stuart source snapshot does not include the `ibuffer.cpp` body, so this page is based on Steam retail Ghidra read-back, debug strings, RTTI, vtable pointers, decompile evidence, and callsite review rather than source-body identity.

Wave413 re-audited the CIBuffer lifecycle/create/lock/release cluster. It recovered two previously missing vtable-slot function boundaries at `0x00488460` and `0x004884f0`, corrected `CIBuffer__CreateConfigured` to four stack arguments, hardened signatures/comments/tags for twelve CIBuffer targets, and verified the saved Ghidra project through post-apply read-back.

Wave414 corrected the adjacent direct-lock helper at `0x004885e0` from the stale `CVBufTexture__SetTextureStageFilterByFlag200` label to `CIBuffer__LockDirect`. CVBufTexture and CDXLandscape callers pass a CIBuffer receiver and test the returned HRESULT, while the body locks the D3D index-buffer pointer at `+0x08` with lock flags selected from usage field `+0x10`.

Wave1013 (`hud-lifecycle-render-support-review-wave1013`) re-read `0x00488330 CIBuffer__CreateConfigured` and `0x004885e0 CIBuffer__LockDirect` as part of HUD lifecycle/render-support review with no mutation. The configured-create helper still stores four stack arguments at CIBuffer offsets `+0x0c/+0x10/+0x14/+0x18` and exits with `RET 0x10`; the direct-lock helper still locks the D3D index-buffer pointer at `+0x08`, with usage flags at `+0x10` selecting `0x2800` or `0x800` lock flags. Queue closure remains `6238/6238 = 100.00%`; Wave911 focused re-audit progress remains `505/1408 = 35.87%`; expanded static surface progress is `718/1493 = 48.09%`; Wave911 top-500 risk-ranked coverage is `420/500 = 84.00%`. Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260531-182125_post_wave1013_hud_lifecycle_render_support_review_verified`. Runtime index-buffer behavior, exact source-body identity, concrete CIBuffer/D3D object layouts, BEA patching, and rebuild parity remain separate proof. Probe token anchor: Wave1013; hud-lifecycle-render-support-review-wave1013; 0x00481450 CHud__Init; 0x004815c0 CHud__Reset; 0x00481650 CHud__LoadTextures; 0x00481af0 CHud__PostLoadProcess; 0x00481f40 CHud__SetHudComponent; 0x004821e0 CDXCompass__ApplyRenderStateAdditive; 0x00488330 CIBuffer__CreateConfigured; 0x004885e0 CIBuffer__LockDirect; 0x0048f540 CLevelBriefingLog__ctor; 0x0048f5a0 CLevelBriefingLog__scalar_deleting_dtor; 0x0048f5c0 CLevelBriefingLog__dtor; 505/1408 = 35.87%; 718/1493 = 48.09%; 420/500 = 84.00%; 6238/6238 = 100.00%; [maintainer-local-ghidra-backup-root]\BEA_20260531-182125_post_wave1013_hud_lifecycle_render_support_review_verified; no mutation.

Wave1213 (`wave1213-render-resource-lifecycle-tail-current-risk-review`) re-read `0x00488330 CIBuffer__CreateConfigured` and `0x004885e0 CIBuffer__LockDirect` as current-risk denominator rows inside the mesh/resource/render contract. Fresh xrefs tie configured create to `CVBufTexture__ResizeIndexBuffer` and `CDXLandscape__Init`, while direct lock is used by `CVBufTexture__ResizeIndexBuffer`, `CVBufTexture__AddIndices`, `CVBufTexture__GetIndexPtr`, and `CDXLandscape__UpdateLOD`. The wave made no mutation. Active current-risk progress moved to `1125/1179 = 95.42%`; verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260607-074242_post_wave1213_render_resource_lifecycle_tail_current_risk_review_verified`. Runtime Direct3D behavior, runtime terrain/HUD output, exact CIBuffer/CVBufTexture/CDXLandscape layouts, exact source identity, BEA patching behavior, rebuild parity, and no-noticeable-difference parity remain separate proof.

## Class Structure

Based on observed member access patterns:

| Offset | Observed role | Notes |
| --- | --- | --- |
| `0x00` | vtable | Set to `0x005dbec4` by constructor/destructor paths. |
| `0x08` | D3D index-buffer pointer | COM released by destructor and static/dynamic release slots. |
| `0x0c` | size bytes | Stored by configured/default create and used for shadow-copy upload. |
| `0x10` | usage flags | `0x200` selects `0x2800` lock flags in direct-lock path. |
| `0x14` | index format | Default create stores `0x65`, consistent with 16-bit index format usage. |
| `0x18` | buffer type | `0` static, `1` dynamic in observed create/release gates. |
| `0x1c` | shadow-copy storage | Allocated by default create and copied to the D3D buffer on dirty unlock/dynamic create. |
| `0x20` | shadow dirty flag | Set by shadow lock path and cleared by upload-on-unlock. |

Concrete C++ type declarations, allocator ownership, field names, and runtime rendering behavior remain unproven.

## VTable Layout

Observed CIBuffer vtable slots at `0x005dbec4`:

| Slot | Slot address | Target | Function |
| ---: | --- | --- | --- |
| `0` | `0x005dbec4` | `0x00488270` | `CIBuffer__ScalarDeletingDestructor` |
| `1` | `0x005dbec8` | `0x00488460` | `CIBuffer__CreateDynamic` |
| `2` | `0x005dbecc` | `0x004884f0` | `CIBuffer__CreateStatic` |
| `3` | `0x005dbed0` | `0x00488520` | `CIBuffer__ReleaseStatic` |
| `4` | `0x005dbed4` | `0x00488550` | `CIBuffer__ReleaseDynamic` |

Rows after slot `4` in the wider pointer read-back are adjacent data or neighboring tables, not CIBuffer slots under the current evidence.

## Functions

Documented CIBuffer-related targets: `13` total. Wave413 covered the lifecycle/create/lock/release targets through `CIBuffer__Destructor_thunk`; Wave414 corrected the direct-lock helper at `0x004885e0`; Wave415 supersedes the former `CIBuffer__GetEntryHeightByOwnerSlot` attribution at `0x00488aa0` with `CImposter__GetFrameHeightForOwnerSlot`.

### CIBuffer__Constructor

- **Address:** `0x00488210`
- **Saved signature:** `void * __thiscall CIBuffer__Constructor(void * this)`
- **Evidence:** Sets the CIBuffer vtable, clears the D3D index-buffer pointer, initializes the base render/device-object path, clears shadow-copy storage at `+0x1c`, and clears the dirty flag at `+0x20`.

### CIBuffer__ScalarDeletingDestructor

- **Address:** `0x00488270`
- **Saved signature:** `void * __thiscall CIBuffer__ScalarDeletingDestructor(void * this, byte flags)`
- **Evidence:** Calls `CIBuffer__Destructor` and conditionally frees the object when `flags & 1` is set.

### CIBuffer__Destructor

- **Address:** `0x00488290`
- **Saved signature:** `void __thiscall CIBuffer__Destructor(void * this)`
- **Evidence:** Restores the CIBuffer vtable, runs the base unlink/shutdown path, releases the D3D index-buffer interface when present, clears `+0x08`, frees shadow-copy storage at `+0x1c`, and then runs the base device-object destructor path.

### CIBuffer__CreateConfigured

- **Address:** `0x00488330`
- **Saved signature:** `int __thiscall CIBuffer__CreateConfigured(void * this, int size_bytes, int usage_flags, int index_format, int buffer_type)`
- **Evidence:** Stores `size_bytes` at `+0x0c`, `usage_flags` at `+0x10`, `index_format` at `+0x14`, and `buffer_type` at `+0x18`. Dispatches vtable slot `+0x04` for dynamic buffers or slot `+0x08` for static buffers, then runs the localized HRESULT fatal-check gate.
- **Correction:** Earlier docs treated this as a five-argument helper with a caller-line parameter. Wave413 read-back confirms `RET 0x10`: four stack arguments plus `this`.

### CIBuffer__Create

- **Address:** `0x00488380`
- **Saved signature:** `int __thiscall CIBuffer__Create(void * this, int index_count)`
- **Evidence:** Allocates `index_count * 2` bytes from the `ibuffer.cpp` debug path, stores size/usage/format/type fields, dispatches the dynamic-create vtable slot, and checks the HRESULT with the localized fatal gate.

### CIBuffer__Unlock

- **Address:** `0x004883f0`
- **Saved signature:** `int __thiscall CIBuffer__Unlock(void * this)`
- **Evidence:** Returns zero when no D3D buffer exists, directly unlocks when the shadow-copy dirty flag is clear, or locks the D3D buffer with `0x800`, copies `+0x0c` bytes from shadow storage at `+0x1c`, clears `+0x20`, and unlocks.

### CIBuffer__CreateDynamic

- **Address:** `0x00488460`
- **Saved signature:** `int __thiscall CIBuffer__CreateDynamic(void * this)`
- **Evidence:** Recovered Wave413 function boundary for vtable slot `1`. Checks `buffer_type +0x18 == 1`, calls the D3D `CreateIndexBuffer` wrapper at `0x005137d0` with size/usage/format and dynamic pool token `1`, returns `0x80004005` on create or follow-up lock failure, and copies the shadow buffer into the locked D3D buffer before unlocking when shadow storage exists.

### CIBuffer__CreateStatic

- **Address:** `0x004884f0`
- **Saved signature:** `int __thiscall CIBuffer__CreateStatic(void * this)`
- **Evidence:** Recovered Wave413 function boundary for vtable slot `2`. Checks `buffer_type +0x18 == 0`, calls the D3D `CreateIndexBuffer` wrapper at `0x005137d0` with size/usage/format and pool token `0`, returns `0x80004005` on failure, and otherwise returns zero.

### CIBuffer__ReleaseStatic

- **Address:** `0x00488520`
- **Saved signature:** `int __thiscall CIBuffer__ReleaseStatic(void * this)`
- **Evidence:** Releases and clears `+0x08` only when `buffer_type +0x18` is static zero and the D3D index-buffer pointer is present. Returns zero.

### CIBuffer__ReleaseDynamic

- **Address:** `0x00488550`
- **Saved signature:** `int __thiscall CIBuffer__ReleaseDynamic(void * this)`
- **Evidence:** Releases and clears `+0x08` only when `buffer_type +0x18` is dynamic one and the D3D index-buffer pointer is present. Returns zero.

### CIBuffer__Lock

- **Address:** `0x00488580`
- **Saved signature:** `int __thiscall CIBuffer__Lock(void * this, void * * out_data)`
- **Evidence:** Returns shadow storage `+0x1c` through `out_data` and sets dirty flag `+0x20` when a shadow copy exists. Otherwise locks the D3D index buffer at `+0x08` with `0x2800` when usage flag `0x200` is set or `0x800` otherwise.

### CIBuffer__LockDirect

- **Address:** `0x004885e0`
- **Saved signature:** `int __thiscall CIBuffer__LockDirect(void * this, void * * out_data)`
- **Evidence:** Corrected by Wave414 from stale CVBufTexture ownership. This direct lock helper locks the D3D index-buffer pointer at `+0x08` into `out_data` and returns the HRESULT. Usage flags at `+0x10` select `0x2800` when bit `0x200` is set, or `0x800` otherwise.
- **Known callers:** `CVBufTexture__ResizeIndexBuffer`, `CVBufTexture__AddIndices`, `CVBufTexture__GetIndexPtr`, and landscape index-buffer update context.

### CIBuffer__Destructor_thunk

- **Address:** `0x0048e350`
- **Saved signature:** `void __thiscall CIBuffer__Destructor_thunk(void * this)`
- **Evidence:** Preserves the thiscall receiver and jumps to `CIBuffer__Destructor`.

## Cross-References

- `CFastVB__Render` (`0x0051a510`) creates and fills an index buffer for quad rendering.
- `CVBufTexture__ResizeIndexBuffer` (`0x005007f0`) calls `CIBuffer__CreateConfigured` for runtime resized index-buffer allocation; the caller-side fatal context pushes are not part of the callee signature.
- CVBufTexture index-buffer write paths call `CIBuffer__LockDirect` (`0x004885e0`) when they need a direct D3D index-buffer lock and HRESULT return rather than the shadow-copy path.
- `CDXLandscape__Init` (`0x00544af0`) uses the configured create path for landscape index-buffer setup.
- `CDXTrees__BuildTreeGeometry` (`0x0055a420`) used to be cited here because `0x00488aa0` carried a stale CIBuffer label. Wave415 corrects that target to CImposter frame-height context, so it is documented under `imposter.cpp` instead.

## Wave413 Validation

- Headless mutation script: `tools/ApplyCIBufferIndexBufferWave413.java`.
- Focused proof guard: `tools/ghidra_cibuffer_index_buffer_wave413_probe.py`.
- Focused tests: `tools/ghidra_cibuffer_index_buffer_wave413_probe_test.py`.
- Package script: `test:ghidra-cibuffer-index-buffer-wave413`.
- Dry run: `updated=0 skipped=10 created=0 would_create=2 renamed=0 would_rename=0 missing=0 bad=0`.
- Apply run: `updated=12 skipped=0 created=2 would_create=0 renamed=0 would_rename=0 missing=0 bad=0`.
- Read-back verified `12` metadata rows, `12` tag rows, `37` xref rows, `12` target decompile exports, `564` target instruction rows, and CIBuffer vtable slots `0` through `4`.
- Refreshed queue telemetry reports `6030` total functions, `1589` commented functions, `4441` commentless functions, `1900` undefined signatures, and `1839` `param_N` signatures.
- The live Ghidra project backup was verified at `[maintainer-local-ghidra-backup-root]\BEA_20260514_105233_post_wave413_cibuffer_index_buffer_verified` with `19` files, `154831751` bytes, and `HashDiffCount=0`.

## Wave414 Direct-Lock Correction

- Headless mutation script: `tools/ApplyCImageLoaderWave414.java`.
- Focused proof guard: `tools/ghidra_cimageloader_wave414_probe.py`.
- Package script: `test:ghidra-cimageloader-wave414`.
- Dry run: `updated=0 skipped=8 created=0 would_create=5 renamed=0 would_rename=1 missing=0 bad=0`.
- Apply run: `updated=13 skipped=0 created=5 would_create=0 renamed=1 would_rename=0 missing=0 bad=0`.
- Read-back verified `0x004885e0` as `CIBuffer__LockDirect` with signature `int __thiscall CIBuffer__LockDirect(void * this, void * * out_data)` and public-safe comments/tags.
- Refreshed queue telemetry reports `6035` total functions, `1602` commented functions, `4433` commentless functions, `1893` undefined signatures, and `1838` `param_N` signatures.

## Wave415 Stale Owner Supersession

- Wave415 corrects `0x00488aa0` from the stale `CIBuffer__GetEntryHeightByOwnerSlot` label to `CImposter__GetFrameHeightForOwnerSlot`.
- The target's observed caller is `CDXTrees__BuildTreeGeometry`; the body uses owner `+0x08` vtable slot `+0x6c` to select a frame index and reads a frame-table float from `this+0x3c +0x10 + index*0x18`.
- This is no longer counted as a CIBuffer-owned helper under the current saved Ghidra metadata.

## Claim Boundary

This page records saved static Ghidra name/signature/comment/tag correction and public-safe retail binary evidence. It does not prove runtime rendering behavior, concrete CIBuffer memory layout beyond observed offsets, exact Stuart source-body identity, local-variable or structure recovery, BEA launch behavior, game patching, or rebuild parity.
