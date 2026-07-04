# Wave1164 Engine / Render-Resource Current-Risk Review

Status: complete static read-only evidence pending validation
Date: 2026-06-06
Tag: `wave1164-engine-render-resource-current-risk-review`

Wave1164 re-read `19 CEngine/CDXEngine/CDXLandscape/CUnit/render-resource current-risk rows` from the active `wave1108-current-risk-rank` current-risk denominator with fresh Ghidra metadata, tag, xref, instruction, and decompile exports. The pass is read-only: no Ghidra mutation, no rename, no signature change, no comment/tag change, no function-boundary change, no executable-byte change, no BEA launch, no installed-game mutation, no save mutation, and no runtime-file mutation.

This wave extends the mesh/resource/render static contract with fresh current-risk read-back for engine viewpoint/camera state, per-view landscape update, dynamic unit render handoff, briefing overlay rendering, terrain mixer texture loading, unit render fade, Kempy cube cleanup, landscape cache/LOD update, and snow/overlay render state.

Representative anchors:

| Address | Evidence |
| --- | --- |
| `0x0044a020 CEngine__SetViewpoint` | `RET 0x10` helper storing selected viewpoint viewport/player/camera-wrapper state and allocating a `CInterpolatedCamera`. |
| `0x0044a1c0 CEngine__UpdatePos` | Checks render-landscape state and forwards camera/viewpoint context to `CDXLandscape__SetTileData`. |
| `0x00476fe0 CVBufTexture__RenderDynamicUnitPass` | Active-unit list walk reaching `CDXEngine__BuildProjectedSprites` and `CRenderQueue__InsertSortedByDepth`. |
| `0x0048f5c0 CLevelBriefingLog__dtor` | Restores vtable `0x005dc208`, releases the HUD texture/ref handle when present, then calls `CMonitor__Shutdown`. |
| `0x0048f620 CLevelBriefingLog__Render` | `CDXEngine__PostRender` overlay slot for level briefing/post-mission text and cursor/arrow texture path. |
| `0x004911c0 CMapTex__LoadTexture` | `RET 0xc` terrain/mixer TGA loader and min/max texture-channel tracker. |
| `0x004914b0 CMapTex__LoadMixerTextureSet` | Mixer texture-set allocation and per-slot `CMapTex__LoadTexture` dispatch. |
| `0x004901e0 MathMatrix3x4__AssignFromEightScalars` | `RET 0x20` matrix helper used by light/frontend/tree render setup callsites. |
| `0x004f6fd0 CUnit__RenderWithDistanceFade` | Unit render-fade helper with handled/not-handled return and global render-state restore. |
| `0x004fd500 CUnit__ApplyRenderPositionDeltaToVector` | HUD/world target marker vector adjustment using actor render-position delta. |
| `0x00528b00 CEngine__InvokeCallbackIfStateMinusOne` | One-argument callback gate for state `this+0x0c == -1`. |
| `0x00528b20 CTweakInt_SetNumViewpoints__ctor` | Tweak constructor installing `PTR_CEngine__SetNumViewpoints_005e4aa4` and storing initial value. |
| `0x00541f50 CDXEngine__GenerateLandscapeCacheTileChunk` | Landscape cache tile generator sampling source pixels and writing ARGB cache pixels. |
| `0x00544040 CDXEngine__ClearKempyCubeTextureSlots` | Clears five Kempy cube texture slots in the engine resource block. |
| `0x00544060 CDXEngine__ReleaseKempyCubeTexturesAndVertexBuffer` | Releases Kempy cube textures and global CVBuffer pointer `0x008aa908`. |
| `0x00544a00 CDXLandscape__Constructor` | Initializes the 0x40-byte CDXLandscape object and vtable `0x005e50d0`. |
| `0x00544fb0 CDXLandscape__ResetWrapper` | `RET 0x8` wrapper that ignores two stack values and calls `CDXLandscape__Reset(this)`. |
| `0x00546b40 CDXLandscape__UpdateLOD` | Landscape LOD/tile/patch update loop over 64x64 tile records and CLandscapeTexture update queue. |
| `0x00555600 CAtmosphericsProfile__VFunc08_UpdateSnowAndRenderOverlay` | Atmospherics vtable slot for snow-density gated state updates and overlay rendering. |

Fresh read-back evidence:

- Pre exports: `19` metadata rows, `19` tag rows, `52` xref rows, `3400` instruction rows, and `19` decompile rows.
- Static closure remains `6411/6411 = 100.00%` with static debt `0 / 0 / 0`.
- Expanded post-100 static surface remains `1560/1560 = 100.00%`.
- Wave1108 current focused accounting advances to `583/1179 = 49.45%`; remaining active focused work: `596`.
- Current risk candidates: `6166`; current focused candidates: `1178`; live regenerated current focused candidates: `1178`.
- Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260606-033330_post_wave1164_engine_render_resource_current_risk_review_verified`, `19` files, `175999879` bytes, `DiffCount=0`, `HashDiffCount=0`.

What this proves:

- The reviewed engine, render-resource, terrain texture, landscape, unit-render, and atmospherics rows exist in the saved Ghidra project and have coherent names, signatures, comments, tags, xrefs, instructions, and decompile exports.
- The mesh/resource/render contract now has a current-risk bridge from engine viewpoint/camera state through terrain texture loading, landscape cache/LOD, dynamic unit render handoff, and atmospherics overlay state.
- No saved Ghidra correction was needed for this tranche.

What remains separate:

- Runtime render behavior.
- Runtime landscape, terrain texture, atmospherics, and unit-render behavior.
- Exact `CEngine`, `CDXEngine`, `CDXLandscape`, `CMapTex`, `CUnit`, `CVBufTexture`, and atmospherics layouts.
- Exact source-body identity.
- BEA patching behavior.
- Visual QA.
- Gameplay outcomes.
- Rebuild parity.

Probe token anchor: Wave1164; wave1164-engine-render-resource-current-risk-review; 583/1179 = 49.45%; 19 CEngine/CDXEngine/CDXLandscape/CUnit/render-resource current-risk rows; current focused candidates: 1178; live regenerated current focused candidates: 1178; remaining active focused work: 596; current risk candidates: 6166; fresh Ghidra export; read-only review; no mutation; Codex read-only consults used; 0 / 0 / 0; 6411/6411 = 100.00%; 52 xref rows; 3400 instruction rows; CEngine__SetViewpoint; CEngine__UpdatePos; CVBufTexture__RenderDynamicUnitPass; CMapTex__LoadTexture; CMapTex__LoadMixerTextureSet; CUnit__RenderWithDistanceFade; CDXEngine__GenerateLandscapeCacheTileChunk; CDXEngine__ReleaseKempyCubeTexturesAndVertexBuffer; CDXLandscape__UpdateLOD; CAtmosphericsProfile__VFunc08_UpdateSnowAndRenderOverlay; [maintainer-local-ghidra-backup-root]\BEA_20260606-033330_post_wave1164_engine_render_resource_current_risk_review_verified; mesh-resource-render-static-contract.md; wave1108-current-risk-rank; current-risk denominator; focused threshold `15`; not Wave911 reconstruction.
