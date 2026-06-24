# Ghidra Water Render Tail Wave877 Readiness Note

Status: complete static read-back evidence
Date: 2026-05-25
Scope: `water-render-tail-wave877`

Wave877 water render tail saved comments and tags for eight adjacent water-render/resource rows from `0x0055b0e0 CWaterRenderSystem__ctor` through `0x0055b6c0 CWaterRenderSystem__RenderMainPass`. The pass verified the existing clean signatures, made no renames, no function-boundary changes, no executable-byte changes, did not launch BEA, and did not mutate the installed game.

Representative anchors:

| Address | Evidence |
| --- | --- |
| `0x0055b0e0 CWaterRenderSystem__ctor` | `CEngine__Init` xref `0x00449b7f`; installs the scalar-deleting-destructor vtable, clears texture/resource slots `this+0x08/+0x0c/+0x10/+0x14/+0x18`, clears cache field `this+0x3ab8`, and calls `CShaderBase__Init(DAT_00855bb0)`. |
| `0x0055b140 CWaterRenderSystem__scalar_deleting_dtor` | Vtable DATA xref `0x005e5a70`; calls `CWaterRenderSystem__dtor`, then frees through `CDXMemoryManager__Free(DAT_009c3df0, this)` when `free_flag & 1`. |
| `0x0055b160 CWaterRenderSystem__dtor` | Releases global `DAT_009cc21c`, unlinks shader/render-object state, decrements texture-name refs for `this+0x08/+0x0c/+0x10/+0x14`, decrements CVBuf/resource slot `this+0x18`, then runs `DeviceObject__dtor_body`. |
| `0x0055b230 CWaterRenderSystem__LoadTextures` | Direct string dumps verify `mixers\reflection%.2d.tga`, `mixers\caustic%.2d.tga`, `sunblob.tga`, and `sunreflect.tga`; loads reflection/caustic/sun resources, creates the CVBufTexture/resource at `this+0x18`, applies VB/IB formats `0x142` and `0x65`, and dispatches vtable slot `+0x04`. |
| `0x0055b330 CWaterRenderSystem__ReloadTextures` | `CEngine__SetWater` xref `0x0044a2c8`; decrements and clears water texture slots, clears `this+0x3ab8`, then calls `CWaterRenderSystem__LoadTextures`. |
| `0x0055b440 CWaterRenderSystem__BuildGridVBuf` | Called by shadow and main water passes; debug string `Creating water VBuf\x0a`; builds a `0x18` by `0x18` water grid, writes 25x25 vertices with radial alpha/color handling, updates CVBufTexture persistence/world matrix state, and reapplies shader constants. |
| `0x0055b660 CWaterRenderSystem__RenderShadowPass` | `CDXLandscape__RenderShadowMap` xref `0x00546795`; builds the grid, applies shader constants from `DAT_0089c9b0`, checks device slot `+0x1ac`, and renders through `CVBufTexture__RenderIndexedNoValidate`. |
| `0x0055b6c0 CWaterRenderSystem__RenderMainPass` | Two `CDXEngine__Render` xrefs; gates global water/shader state, validates render records, animates caustic/reflection/sun textures through `CDXTexture__GetAnimatedFrame`, uses shader handles `0x242` and `0x142`, invokes `CDXSurf__Render`, builds water grids, and renders through `CVBufTexture__RenderIndexed` / `RenderIndexedNoValidate`. |

Read-back evidence:

- `ApplyWaterRenderTailWave877.java dry`: `updated=0 skipped=8 renamed=0 would_rename=0 missing=0 bad=0`
- `ApplyWaterRenderTailWave877.java apply`: `updated=8 skipped=0 renamed=0 would_rename=0 missing=0 bad=0`
- `ApplyWaterRenderTailWave877.java final dry`: `updated=0 skipped=8 renamed=0 would_rename=0 missing=0 bad=0`
- Post exports: 8 metadata rows, 8 tag rows, 12 xref rows, 2371 instruction rows, 8 decompile rows, 9 context metadata rows, and 9 context decompile rows.
- Queue after Wave877: 6113 total, 5893 commented, 220 commentless, 0 exact-undefined signatures, 0 `param_N`, comment-backed and strict clean-signature proxy `5893/6113 = 96.40%`.
- Next raw commentless row: `0x0055d731 CRT__SehDispatchWithScopeTable_Thunk_0055d731`.
- Verified backup: `G:\GhidraBackups\BEA_20260525-215011_post_wave877_water_render_tail_verified`, 19 files, 172690311 bytes, `DiffCount=0`.

What this proves:

- The eight target function rows exist in the saved Ghidra project with the saved comments and `water-render-tail-wave877` / `wave877-readback-verified` tags.
- The saved signatures remained clean and were read back unchanged.
- The observed behavior is static retail Ghidra decompile/xref/instruction evidence tied to CEngine, CDXLandscape, CVBufTexture, texture-string dumps, and prior Wave217/Wave570/Wave861/Wave876 context.
- These are high-importance water/render connector rows with low local evidence density, not low-importance filler.

What remains unproven:

- Exact `CWaterRenderSystem` field layout and source-body identity.
- Exact water texture sequencing, shader constant schema, and render-pass ordering.
- Runtime water visual behavior.
- BEA patching behavior.
- Rebuild parity.
