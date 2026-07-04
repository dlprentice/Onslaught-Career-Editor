# Ghidra Render Multipass Wave873 Readiness Note

Status: complete static read-back evidence
Date: 2026-05-25
Scope: `render-multipass-wave873`

Wave873 render multipass saved owner-corrected CRenderQueue names, reviewed signatures, comments, and tags for five adjacent renderer multipass / projected-sprite helpers from `0x00553960 CRenderQueue__RenderMultipassLayerA` through `0x00554df0 CRenderQueue__RenderVBufTextureWithStateToggle`. The pass made five renames, three signature/parameter corrections, no function-boundary changes, and no executable-byte changes.

These rows are high-importance, low local-evidence-density renderer infrastructure, not low-importance filler. The important correction is ownership: callsites pass `ECX=0x009c7550`, the documented global CRenderQueue, and the bodies use CRenderQueue fields such as `this+0x704`, `this+0x5b8`, `this+0x5bc`, `this+0x640`, `this+0x594`, and `this+0x598`.

Representative anchors:

| Address | Evidence |
| --- | --- |
| `0x00553960 CRenderQueue__RenderMultipassLayerA` | `CDXEngine__Render` callsite `0x0053e692` loads `ECX=0x009c7550`; body configures D3D/state-cache texture stages, copies `DAT_009c7c90` through `CDXEngine__SetWorldMatrixElements`, walks queue entries at `this+0x10c` / count `this+0x5bc`, and calls `CDXLandscape__RenderTileRange`. |
| `0x00554170 CRenderQueue__RenderMultipassLayerB` | `CDXEngine__Render` callsite `0x0053e6af` loads `ECX=0x009c7550`; body requires `this+0x704` and `this+0x5b0`, writes immediate quad/global matrix blocks, applies pending render state, and issues D3D device draw slot `+0x14c`. |
| `0x005545d0 CRenderQueue__BuildProjectedSprites` | `CVBufTexture__RenderDynamicUnitPass` callsites `0x004773ab` and `0x004779b3` push an active unit pointer and load `ECX=0x009c7550`; body samples static-shadow height, derives scale/alpha from unit vfuncs and camera distance, skips duplicate active entries, then calls the strip emitter. |
| `0x00554750 CRenderQueue__EmitBillboardStrip` | Called from `CRenderQueue__BuildProjectedSprites`; body clamps scale, blends shadow/tint colors, uses view-vector fields `this+0x594/this+0x598`, samples static-shadow height for each quad, and writes vertices/indices through `CVBufTexture__AddVertices` / `CVBufTexture__AddIndices` against `*(this+0x5b8)`. |
| `0x00554df0 CRenderQueue__RenderVBufTextureWithStateToggle` | `CDXEngine__Render` callsite `0x0053e846` loads `ECX=0x009c7550`; body toggles texture-stage/render-state values around `CVBufTexture__Render(*(this+0x5b8), 1)`, correcting the stale `CVBufTexture__RenderWithStateToggle` owner/signature. |

Read-back evidence:

- `ApplyRenderMultipassWave873.java dry`: `updated=0 skipped=5 renamed=0 would_rename=5 signature_updated=3 comment_only_updated=2 missing=0 bad=0`
- `ApplyRenderMultipassWave873.java apply`: `updated=5 skipped=0 renamed=5 would_rename=0 signature_updated=3 comment_only_updated=2 missing=0 bad=0`
- `ApplyRenderMultipassWave873.java final dry`: `updated=0 skipped=5 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=0 missing=0 bad=0`
- Post exports: 5 metadata rows, 5 tag rows, 6 xref rows, 1,385 instruction rows, 5 decompile rows, 426 call-site instruction rows, and 8 helper metadata rows.
- Queue after Wave873: 6,106 total functions, 5,862 commented, 244 commentless, 0 exact-undefined signatures, 0 `param_N`, comment-backed proxy `5862/6106 = 96.00%`, strict clean-signature proxy `5862/6106 = 96.00%`.
- Next raw commentless row: `0x00554f80 CAtmosphericsProfile__ctor`.
- Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260525-193607_post_wave873_render_multipass_verified`, 19 files, 172,526,471 bytes, `DiffCount=0`.

What this proves:

- The five target function rows exist in the saved Ghidra project.
- The saved names/signatures are owner-corrected to CRenderQueue where the static receiver evidence supports it.
- The saved comments and tags include `render-multipass-wave873` and `wave873-readback-verified`.
- The observed bodies are static retail Ghidra evidence tied to callsites, xrefs, helper metadata, decompile, and instruction exports.

What remains unproven:

- Exact CRenderQueue entry/material/CVBufTexture field layout.
- Exact Direct3D enum names and device method contracts.
- Runtime multipass/projected-sprite visual behavior.
- Runtime render-state behavior.
- BEA patching behavior.
- Rebuild parity.
