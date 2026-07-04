# DXShadows.cpp Functions

> Source File: DXShadows.cpp | Binary: BEA.exe
> Debug Path: 0x00652410 (`[maintainer-local-source-export-root]\DXShadows.cpp`)

Last updated: 2026-05-20

## Source And Evidence Status

Current `CDXShadows` coverage is saved Steam retail Ghidra evidence only. Wave614 replaced the old stub with read-back signatures, comments, tags, xrefs, instruction exports, decompiles, and caller context for the three known `DXShadows.cpp` functions.

Runtime shadow behavior remains unproven. Treat this page as static binary evidence, not source-body parity, runtime GPU/D3D behavior proof, BEA launch proof, game patching, or rebuild parity.

## Overview

`CDXShadows` is the DirectX shadow manager used by the engine lifecycle. The observed retail functions initialize shared render-object list linkage, allocate/configure per-shadow-map texture wrappers, register shadow console variables, initialize the blob-shadow texture/index/vertex buffer resources, and release those resources during shutdown.

## Functions

| Address | Saved signature | Evidence notes |
| --- | --- | --- |
| `0x00552060` | `void __thiscall CDXShadows__Destructor(void * this)` | `CEngine__Shutdown` callsite `0x004498a4` passes `ECX=0x009c7550`. Body walks count `+0x5bc`, releases texture pointers from `+0x640`, clears blob texture/resource fields `+0x5b4/+0x5b8`, invokes vtable slot `+0x0c`, and unlinks from `CShaderBase` render lists. |
| `0x005520f0` | `void __thiscall CDXShadows__Init(void * this)` | `CEngine__Init` callsite `0x00449d05` passes `ECX=0x009c7550`. Body calls the shared `CShaderBase` init path, selects shadow-map count `0x10` or `0x20` from `DAT_00662f10`, allocates/configures `CUMTexture` entries from `DXShadows.cpp` line `0x69`, registers shadow cvars, and invokes vtable slot `+0x08`. |
| `0x00552330` | `void __thiscall CDXShadows__InitBlobShadows(void * this)` | `CEngine__InitResources` callsite `0x00449d62` passes `ECX=0x009c7550`. Body loads `shadowblob.tga`, stores it at `+0x5b4`, allocates a `0x68`-byte `CVBufTexture` from `DXShadows.cpp` line `0x97`, stores it at `+0x5b8`, and configures vertex/index buffer formats. |

## Key Observed Offsets

| Offset | Observed role |
| ---: | --- |
| `+0x08` | Fade distance float initialized to `30.0f` and exposed as `cg_BlobShadowFadeDist`. |
| `+0x5b0` | Byte flag exposed as `cg_ShowShadowMap`. |
| `+0x5b4` | Blob-shadow texture pointer from `shadowblob.tga`. |
| `+0x5b8` | Blob-shadow `CVBufTexture`-style render resource pointer. |
| `+0x5bc` | Shadow-map entry count: `0x10` or `0x20` depending on `DAT_00662f10`. |
| `+0x5c0` | Shadow texture size table initialized to `0x40` per entry. |
| `+0x640` | Texture wrapper pointer table released during destructor cleanup. |
| `+0x704` | Byte flag exposed as `cg_Shadows`. |
| `+0x705` | Byte flag exposed as `cg_ShowShadowExtents`. |
| `+0x706` | Byte flag exposed as `cg_BlobShadows`. |

The offsets above are observed static use-sites, not a complete concrete class layout.

## Wave614 Saved Corrections

Wave614 saved signatures, comments, and tags in Ghidra after dry/apply/read-back:

| Address | Previous state | Saved state |
| --- | --- | --- |
| `0x00552060` | `undefined CDXShadows__Destructor(void)` | `void __thiscall CDXShadows__Destructor(void * this)` |
| `0x005520f0` | `undefined CDXShadows__Init(void)` | `void __thiscall CDXShadows__Init(void * this)` |
| `0x00552330` | `undefined CDXShadows__InitBlobShadows(void)` | `void __thiscall CDXShadows__InitBlobShadows(void * this)` |

The dry run reported `updated=0 skipped=3 renamed=0 would_rename=0 missing=0 bad=0`; the apply reported `updated=3 skipped=0 renamed=0 would_rename=0 missing=0 bad=0`; the final dry reported `updated=0 skipped=3 renamed=0 would_rename=0 missing=0 bad=0`, with `REPORT: Save succeeded`.

Read-back verified `3` metadata rows, `3` tag rows, `3` xref rows, `783` instruction rows, `3` target decompile rows, and `141` callsite instruction rows. The queue refresh after Wave614 reports `6093` functions, `3159` commented functions, `2934` commentless functions, `1272` exact-undefined signatures, `1056` `param_N` signatures, and next head `0x0055515e CDXSnow__Init`. The actual live Ghidra project backup was verified at `[maintainer-local-ghidra-backup-root]\BEA_20260520-004026_post_wave614_cdxshadows_head_verified` with `19` files, `161614727` bytes, and `DiffCount=0`.

## Related Systems

- `CUMTexture` texture-resource wrapper: `CDXShadows__Init` allocates and configures per-shadow-map entries.
- `CVBufTexture` render buffer wrapper: `CDXShadows__InitBlobShadows` allocates and configures the blob-shadow render resource.
- `CTexture`: `shadowblob.tga` is found through `CTexture__FindTexture`.
- `CShaderBase`: init/unlink calls tie `CDXShadows` into the shared render-object lists.
- `CEngine`: lifecycle callsites are `CEngine__Init`, `CEngine__InitResources`, and `CEngine__Shutdown`.

## Remaining Limits

- Runtime shadow behavior remains unproven.
- Runtime blob-shadow rendering remains unproven.
- Concrete `CDXShadows`, `CUMTexture`, `CVBufTexture`, texture-resource, render-list, and console-variable layouts remain partial.
- Vtable slot identities for the observed `+0x08` and `+0x0c` calls remain deferred.
- Exact source-body identity and source parity are not proven.
- BEA was not launched, patched, or debugged in Wave614.
- This does not prove rebuild parity or game-behavior equivalence.
