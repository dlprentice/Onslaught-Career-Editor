# Ghidra CDXEngine Render-State Tail Wave869 Readiness Note

Status: complete static read-back evidence
Date: 2026-05-25
Scope: `cdxengine-render-state-tail-wave869`

Wave869 CDXEngine render-state tail saved comments and tags for ten adjacent CDXEngine/D3D renderer-state helpers from `0x00551200 CDXEngine__ApplyCachedLight` through `0x00551510 CDXEngine__GetProjectionWithDepthBias`. Existing clean signatures were reviewed and left unchanged, including `void __thiscall CDXEngine__ApplyCachedLight(void * this, int light_index, int enabled)`. The pass made no renames, made no function-boundary changes, and made no executable-byte changes. These rows are high-importance, low local-evidence-density renderer infrastructure.

Representative anchors:

| Address | Evidence |
| --- | --- |
| `0x00551200 CDXEngine__ApplyCachedLight` | Applies one cached 0x5c-byte light record through D3D device vtable slot `0xcc`; xrefs include `CDXLandscape__Render` and `CDXEngine__ApplyPendingRenderState`. |
| `0x005512f0 CDXEngine__SetFieldE18` | Conservative field setter for `this+0xe18`; xrefs are `CMeshRenderer__RenderMeshCore` callsites. |
| `0x00551300 CDXEngine__PushTransformState` | Snapshots world/view/projection matrix blocks, calls the shared dispatch thunk, and is called by HUD world-target marker/sprite render paths. |
| `0x005513d0 CDXEngine__SetVertexFormatDeferred` | Marks `this+0xe2d` dirty and stores format at `this+0x2f0`; xref from `CDXEngine__Render`. |
| `0x005513f0 CDXEngine__SetShaderMode` | Stores mode at `this+0xe58`; mode zero restores cached vertex-shader handle and render-state compatibility bit. |
| `0x00551420 D3DStateCache__SetMipFilterByGlobalToggle` | Uses `g_DisallowMipMapping` to choose D3D state-cache value `1` or `2` for sampler state `7`. |
| `0x00551460 D3DStateCache__SetMipFilterLinear` | Sets sampler state `7` to value `2`; xrefs include CDXEngine render, HUD overlay, and landscape paths. |
| `0x00551480 D3DStateCache__SetMipFilterPoint` | Sets sampler state `7` to value `0`; xrefs include post-render, overlay sprites, briefing log, and HUD texture paths. |
| `0x005514a0 CDXEngine__SetProjectionDepthBiasIndex` | Stores `this+0xe24`, adjusts projection depth by global `0x009c742c`, pushes transform index `3` through D3D device slot `0xb0`, and clears `this+0xe2a`. |
| `0x00551510 CDXEngine__GetProjectionWithDepthBias` | Copies projection matrix from `this+0x3d4` to output and subtracts `this+0xe24 * 0x009c742c` from output matrix slot `0xe`; xrefs are vertex-shader constant setup helpers. |

Read-back evidence:

- `ApplyCDXEngineRenderStateTailWave869.java dry`: `updated=0 skipped=10 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=10 missing=0 bad=0`
- `ApplyCDXEngineRenderStateTailWave869.java apply`: `updated=10 skipped=0 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=10 missing=0 bad=0`
- `ApplyCDXEngineRenderStateTailWave869.java final dry`: `updated=0 skipped=10 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=0 missing=0 bad=0`
- Post exports: 10 metadata rows, 10 tag rows, 47 xref rows, 237 instruction rows, 10 decompile rows, and 1269 xref-site instruction rows.
- Queue after Wave869: 6105 total functions, 5838 commented, 267 commentless, 0 exact-undefined signatures, 0 `param_N` signatures, strict comment-plus-clean-signature proxy `5838/6105 = 95.63%`.
- Next raw commentless row: `0x005515a0 CDXEngine__InitConsoleVar_UseRenderQueue`.
- Verified backup: `G:\GhidraBackups\BEA_20260525-174243_post_wave869_cdxengine_render_state_tail_verified`, 19 files, 172395399 bytes, `DiffCount=0`.

What this proves:

- The ten target function rows exist in the saved Ghidra project.
- The existing clean signatures are preserved and reviewed.
- The saved comments and tags include `cdxengine-render-state-tail-wave869` and `wave869-readback-verified`.
- The observed bodies and callsites are static retail Ghidra evidence for CDXEngine lighting, transform, shader, mip-filter, and projection-depth-bias infrastructure.

What remains unproven:

- Exact CDXEngine/D3D field names and enum mappings.
- Runtime lighting, sampler, shader, depth-bias, or HUD transform behavior.
- Exact source-to-retail identity.
- BEA patching behavior.
- Rebuild parity.
