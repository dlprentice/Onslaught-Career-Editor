# Asset Provenance and Viewer Truth - 2026-05-07

## Scope

This note answers a product-trust question raised during the WinUI/RE campaign:

- Are the current textures, models, videos, and Goodies rows based on real extraction from the user's installed PC game?
- Or are they only source-tree samples or accidental developer assets?
- What can the current WinUI viewer honestly display?

## Current Answer

The current asset catalog and preview evidence are based on the local retail PC install, not source-tree sample art.

The validated private baseline in `release/readiness/real_asset_full_install_export_2026-05-07.md` was generated from the user's installed game resources and produced:

| Asset family | Current extracted coverage |
| --- | ---: |
| Loose textures exported to PNG | 847 / 847 |
| Loose meshes exported to FBX | 213 / 213 |
| Embedded packed mesh bodies exported to FBX | 139 / 139 |
| Model rows with readable FBX material nodes | 352 / 352 |
| Model rows with readable FBX texture-binding nodes | 352 / 352 |
| Model rows with catalog-matched FBX texture binding files | 352 / 352 |
| Model rows without catalog-matched FBX texture binding files | 0 / 352 |
| Catalog-matched FBX texture binding files | 1,268 |
| Packed `TEXT` references resolved | 601 / 601 |
| Packed reference `MESH` rows resolved | 209 / 209 |
| Goodies `GDIE` texture references resolved | 206 / 206 |
| Goodies `GDIE` mesh references resolved | 42 / 42 |
| Bink `.vid` files inventoried | 66 |
| Language rows exported | 2,571 |
| Total generated catalog rows with Goodies | 4,050 |

Raw manifests, exported assets, screenshots, frames, paths, and proof JSON remain ignored/private under `subagents/`.

## WinUI Viewer Truth

Current WinUI support is real but bounded:

| Surface | Current behavior |
| --- | --- |
| Texture rows | Shows exported PNG previews from the generated catalog. |
| Artwork Goodies | Shows exported PNG previews when the matched texture export exists. |
| Model rows | Shows metadata and a lightweight FBX-derived wireframe geometry preview. |
| Model Goodies | Uses the same exported FBX/wireframe path as model rows. |
| Video Goodies | Routes to Media/video handoff through catalog-linked `.vid` rows. |
| Level Goodies | Shows unlock/status metadata; no local visual preview route is currently known. |

The current model preview is not a full native 3D renderer. It does not claim material, texture, UV, normal, skeleton, animation, lighting, or in-game camera fidelity. It is a local geometry check backed by exported FBX data.

Follow-up coverage in `release/readiness/model_material_texture_binding_coverage_2026-05-07.md` shows all 352 current model rows also have readable FBX material and texture-binding nodes. It now also proves all 352 model rows have at least one FBX texture filename that resolves back to a generated catalog texture row after compact texture-name normalization. That strengthens the static asset pipeline, but the WinUI viewer still needs a real textured renderer before the app can claim textured model viewing.

## Goodies Browser Reality

`release/readiness/goodies_preview_coverage_2026-05-07.md` records the current full-catalog Goodies preview counts:

- 233 displayable Goodie rows.
- 230 source-grid-visible rows.
- 3 source-grid-hidden shipped artwork rows: Goodies 71-73.
- 194 / 194 texture-bearing Goodies texture-preview-ready.
- 45 / 45 model-bearing Goodies FBX-export and wireframe-ready.
- 34 / 34 video Goodies linked to catalog videos.
- 5 level-unlock metadata rows without a local preview route.

`release/readiness/goodies_resource_archive_census_2026-05-08.md` adds a lower-level static resource guard by parsing the installed `goodie_*_res_PC.aya` archives directly instead of relying on the generated catalog. It found 232 shipped Goodie archives for 233 displayable slots, only slot 232 missing a matching archive, and `GDIE -> GDAT` content-kind counts of 149 texture/artwork, 45 model/gallery, 33 video/cutscene, and 5 level/metadata rows. That strengthens the provenance answer while still leaving runtime Goodies wall reachability and final textured model viewing unclaimed.

The catalog still reports 34 video Goodies because Goodie 232 is intentionally represented as a catalog-only handoff to cutscene 33. The archive-backed video/cutscene count is 33; the product-facing video handoff count is 34.

`release/readiness/goodies_model_viewer_alignment_2026-05-08.md` adds a model-viewer-specific static guard. Stuart's source `GT_MESH` rules, installed `GDAT` kind-1 archive metadata, and the generated private catalog agree on the same 45 model Goodie indices. This proves source/resource/catalog alignment for model Goodies, while still leaving runtime model-viewer playback and final textured WinUI rendering as separate gaps.

`release/readiness/goodies_model_viewer_readback_2026-05-08.md` adds the matching source-to-retail decompile guard. Existing ignored Ghidra exports contain the retail `CFEPGoodies__Deserialise` mesh branch plus `CFEPGoodies__ButtonPressed` and `CFEPGoodies__Process` mesh interaction/update branches keyed by content bucket `1`. This strengthens the model-viewer evidence beyond catalog classification, while still leaving runtime in-game playback and final textured WinUI rendering unclaimed.

`release/readiness/mesh_renderer_readback_2026-05-08.md` adds a renderer-adjacent guard for the retail `CMeshRenderer__RenderMesh` dispatch path, including normal render-core dispatch, particle attachment context, debug-render context, and default texture fallback. This helps scope future native textured-model work, but it still does not prove WinUI textured/material rendering or runtime Goodies model-viewer parity.

`release/readiness/dynamic_unit_render_readback_2026-05-08.md` adds the next renderer-path guard for the retail dynamic unit pass currently exported as `CVBufTexture__RenderDynamicUnitPass`, including unit-list traversal, collision-map owner traversal, projected-sprite handling, render-queue insertion, and distance/LOD gates. This still leaves camera/material/skeleton/animation parity, runtime Goodies model-viewer playback, and final WinUI textured rendering unclaimed.

## What This Proves

- The current extraction/catalog pipeline is working against the real installed PC resources.
- The current WinUI Asset Library is not merely showing source-tree samples.
- Texture/artwork previews are real exported PNG files.
- Model support is real exported geometry plus in-app wireframe preview, not final textured/animated rendering.
- All current model rows now have at least one catalog-resolved texture binding name, but exporter default placeholders still appear beside real matches.
- Goodies rows are catalog-backed and can be separated by visible wall mapping, hidden shipped rows, media handoff rows, and metadata-only level rows.

## What This Does Not Prove

- It does not prove a complete textured/animated native model viewer.
- It does not prove runtime replay of every in-game Goodies wall slot.
- It does not prove semantic game-state interpretation.
- It does not permit committing extracted assets or raw private manifests.

## Recommended Next Targets

1. Build or integrate a real native model viewing path with materials, camera controls, and clear public-safety boundaries.
2. Add wider sampled WinUI automation over Goodies/model families if run time remains acceptable.
3. Add copied-profile runtime replay for representative Goodies wall slots after static coverage stays stable.
