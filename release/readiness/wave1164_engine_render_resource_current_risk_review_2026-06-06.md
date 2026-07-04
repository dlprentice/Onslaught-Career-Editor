# Wave1164 Engine / Render-Resource Current-Risk Review Readiness Note

Status: complete static read-only evidence pending validation
Date: 2026-06-06
Scope: `wave1164-engine-render-resource-current-risk-review`

Wave1164 re-read `19 CEngine/CDXEngine/CDXLandscape/CUnit/render-resource current-risk rows` from the active `wave1108-current-risk-rank` current-risk denominator. Fresh Ghidra metadata, tag, xref, instruction, and decompile exports showed the saved names, signatures, comments, and tags remain coherent. No Ghidra mutation was performed.

Representative anchors:

| Address | Evidence |
| --- | --- |
| `0x0044a020 CEngine__SetViewpoint` | `RET 0x10` viewpoint helper storing viewport/player/camera-wrapper state and allocating a `CInterpolatedCamera`. |
| `0x0044a1c0 CEngine__UpdatePos` | Render-landscape/viewpoint bridge forwarding camera/viewpoint context to `CDXLandscape__SetTileData`. |
| `0x00476fe0 CVBufTexture__RenderDynamicUnitPass` | Active-unit dynamic pass reaching projected sprites and sorted render-queue insertion. |
| `0x0048f620 CLevelBriefingLog__Render` | Post-HUD overlay slot called from `CDXEngine__PostRender` between message-log and pause-menu rendering. |
| `0x004911c0 CMapTex__LoadTexture` | Terrain/mixer TGA loader and per-texture min/max tracker. |
| `0x004914b0 CMapTex__LoadMixerTextureSet` | Mixer texture-set allocator/loader sizing `texture_width * texture_width * 4 * texture_count`. |
| `0x004f6fd0 CUnit__RenderWithDistanceFade` | Unit render fade path with handled/not-handled return and global render-state byte restore. |
| `0x00541f50 CDXEngine__GenerateLandscapeCacheTileChunk` | Landscape texture-cache tile generator writing ARGB cache pixels. |
| `0x00544060 CDXEngine__ReleaseKempyCubeTexturesAndVertexBuffer` | Kempy cube texture and global vertex-buffer cleanup using texture refcount decrement evidence. |
| `0x00546b40 CDXLandscape__UpdateLOD` | Landscape LOD/tile/patch update loop over 64x64 tile records and CLandscapeTexture update queue. |
| `0x00555600 CAtmosphericsProfile__VFunc08_UpdateSnowAndRenderOverlay` | Atmospherics vtable slot updating snow state and rendering overlay entries. |

Read-back evidence:

- Pre exports: `19` metadata rows, `19` tag rows, `52` xref rows, `3400` instruction rows, and `19` decompile rows.
- Static closure remains `6411/6411 = 100.00%` with static debt `0 / 0 / 0`.
- Expanded post-100 static surface remains `1560/1560 = 100.00%`.
- Wave1108 current focused accounting advances to `583/1179 = 49.45%`; remaining active focused work: `596`.
- Current risk candidates: `6166`; current focused candidates: `1178`; live regenerated current focused candidates: `1178`.
- Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260606-033330_post_wave1164_engine_render_resource_current_risk_review_verified`, `19` files, `175999879` bytes, `DiffCount=0`, `HashDiffCount=0`.

What this proves:

- The reviewed engine, render-resource, terrain texture, landscape, unit-render, and atmospherics rows exist in the saved Ghidra project and have coherent names, signatures, comments, tags, xrefs, instructions, and decompile exports.
- The mesh/resource/render static map now has fresh current-risk read-back coverage across camera/viewpoint state, per-view landscape update, dynamic unit render handoff, map texture loading, landscape cache/LOD update, Kempy cube cleanup, and snow/overlay render state.
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
