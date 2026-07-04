# Ghidra CDX Render Resource Lifecycle Review Wave1028

Status: complete read-only static review
Date: 2026-06-01
Scope: `cdx-render-resource-lifecycle-review-wave1028`

Wave1028 re-read five DX render-resource lifecycle rows from the Wave911 residual surface. The review made no mutation: no Ghidra mutation, no rename, no signature change, no comment/tag change, no function-boundary change, and no executable-byte change.

Primary targets:

| Address | Saved state | Fresh evidence |
| --- | --- | --- |
| `0x0054bff0 CDXMeshVB__scalar_deleting_dtor` | `void * __thiscall CDXMeshVB__scalar_deleting_dtor(void * this, byte flags)` | CDXMeshVB vtable `0x005e50fc` slot 0 points here; body calls `CDXMeshVB__dtor_base`, conditionally frees `this` through `CDXMemoryManager__Free` when `flags & 1`, and returns `this`. |
| `0x0054c010 CDXMeshVB__dtor_base` | `void __thiscall CDXMeshVB__dtor_base(void * this)` | Called by the scalar-deleting wrapper; body reinstalls the CDXMeshVB vtable, calls `CDXMeshVB__ReleaseResources`, frees the name pointer, unlinks render/shader object state, and runs base device-object teardown. |
| `0x00547d70 CDXMemBuffer__ctor` | `void * __fastcall CDXMemBuffer__ctor(void * this)` | Constructor row remains owner-corrected away from stale CChunker wording; body zeros the file/data/CRC/state fields used by `CDXMemBuffer__Read` and chunk/resource load callers. |
| `0x004f2790 CDXSurf__UnlinkNodeFromGlobalList` | `void __fastcall CDXSurf__UnlinkNodeFromGlobalList(void * texture_base)` | Xrefs from `CDXSurf__dtor` and unwind cleanup rows still load ECX with `object+0x08` or null; body walks global list head `DAT_0083d9b0` through `node+0xa0` links and unlinks a matching `texture_base-0x08` node. |
| `0x00527de0 CWaterRenderSystem__ResetAndMarkSourceFlag` | `void __fastcall CWaterRenderSystem__ResetAndMarkSourceFlag(void * validation_record)` | Three xrefs from `CWaterRenderSystem__RenderMainPass`; body clears `DAT_00854dd8` and sets `DAT_00854dd9` from whether `validation_record+0x10` is zero. |

Context evidence covered `0x0054bf80 CDXMeshVB__ctor`, `0x0054d3f0 CDXMeshVB__ReleaseResources`, `0x00548570 CDXMemBuffer__Read`, `0x004f2710 CTextureBase__Init`, and `0x0053e2e0 CDXEngine__Render`. Vtable evidence covered `0x005e50fc`: slot 0 resolves to `CDXMeshVB__scalar_deleting_dtor`, slot 4 resolves to `CDXMeshVB__ReleaseResources`, slots 2 and 3 resolve to `SharedVFunc__ReturnZero_00405930`, and slot 7 resolves to `CDXPatch__RestoreAndRebuildIfDirty`; slots 1, 5, and 6 remain non-function pointer targets in the exported window.

Evidence counts:

- Primary exports: 5 metadata rows, 5 tag rows, 28 xref rows, 87 body-instruction rows, and 5 decompile rows.
- Context exports: 5 metadata rows, 5 tag rows, 648 xref rows, 1020 body-instruction rows, and 5 decompile rows.
- Vtable export: 8 rows from `0x005e50fc`.
- Queue closure remains `6238/6238 = 100.00%` with 0 commentless, 0 exact-undefined signatures, and 0 `param_N`.
- Wave911 focused re-audit progress after Wave1028: `605/1408 = 42.97%`; expanded static surface progress: `834/1493 = 55.86%`; Wave911 top-500 risk-ranked coverage remains `500/500 = 100.00%`.
- Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260601-021726_post_wave1028_cdx_render_resource_lifecycle_review_verified`, 19 files, 173968263 bytes, `DiffCount=0`, `HashDiffCount=0`.

What this proves:

- The saved CDXMeshVB lifecycle, CDXMemBuffer constructor/read context, CDXSurf global-list unlink, and CWaterRenderSystem validation-helper rows remain internally coherent under fresh metadata/tag/xref/instruction/decompile/vtable exports.
- The old CChunker-owner and cdecl-stack-argument pitfalls remain corrected in the saved database.
- The CDXMeshVB destructor pair remains tied to vtable slot 0 and release-helper slot 4.

What remains unproven:

- Runtime D3D/render-resource lifetime behavior or visible render output.
- Exact `CDXMeshVB`, `CDXMemBuffer`, `CDXSurf`, `CTextureBase`, `CWaterRenderSystem`, or `CDXEngine` layouts.
- Exact source-body identity beyond static source/decompile parity.
- BEA patch behavior, gameplay outcomes, and rebuild parity.

Probe token anchor: Wave1028; cdx-render-resource-lifecycle-review-wave1028; 0x0054bff0 CDXMeshVB__scalar_deleting_dtor; 0x0054c010 CDXMeshVB__dtor_base; 0x00547d70 CDXMemBuffer__ctor; 0x004f2790 CDXSurf__UnlinkNodeFromGlobalList; 0x00527de0 CWaterRenderSystem__ResetAndMarkSourceFlag; 605/1408 = 42.97%; 834/1493 = 55.86%; 500/500 = 100.00%; 6238/6238 = 100.00%; [maintainer-local-ghidra-backup-root]\BEA_20260601-021726_post_wave1028_cdx_render_resource_lifecycle_review_verified; no mutation.
