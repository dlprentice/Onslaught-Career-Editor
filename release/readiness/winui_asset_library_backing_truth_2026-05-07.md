# WinUI Asset Library Backing Truth - 2026-05-07

## Scope

This note answers the product/provenance question raised during the WinUI/RE campaign: whether the Asset Library and Goodies browser are showing actual extracted Battle Engine Aquila retail content, source/reference material, or sample data.

This pass is public-safe. Raw catalogs, extracted files, screenshots, and private paths remain ignored under `subagents/` or other private locations.

## Current Answer

The WinUI Asset Library is backed by generated catalog data from the user's read-only PC install and private extracted/exported artifacts. It is not just a wall of hard-coded sample rows.

The current Goodies browser combines:

- retail PC resource archive inventory,
- generated texture/model/video/language catalog rows,
- exported private PNG/FBX assets when available,
- source/binary RE labels for unlock and wall-placement explanations,
- and explicit "not proven yet" copy for runtime-only behavior.

## Fresh Probe Results

The following public-safe probes were rerun without launching BEA, mutating `BEA.exe`, mutating Ghidra, or committing private assets.

| Probe | Result | Public-safe output summary |
| --- | --- | --- |
| `py -3 tools/goodies_asset_matrix.py --check` | PASS | Goodie archives: `232 / 233` displayable slots; unique refs resolved: textures `206/206`, meshes `42/42`. |
| `py -3 tools/goodies_catalog_linkage_check.py --check` | PASS | Goodie linkage: textures `194/194`, models `45/45`, videos `34`. |
| `py -3 tools/goodies_source_access_probe.py --check` | PASS | Source Goodie API lines: set `3`, get `3`, direct 71-73 API calls `0`. |
| `py -3 tools/goodies_runtime_readback_probe.py --check` | PASS | Source/runtime-static token groups: `15/15` passing. |
| `py -3 tools/goodies_script_corpus_probe.py --require-root --check` | PASS | Mission-script corpus: `733` scripts, `32` Goodie calls, indices `51,53,68,69,70,71`, target `72-74=0`. |

## What Is Actually Backed By Retail Extraction

| Asset Library area | Backing status |
| --- | --- |
| Texture rows | Generated from the retail asset catalog with exported PNG previews when available. |
| Model rows | Generated from mesh catalog rows with FBX exports and wireframe metadata when available. |
| Goodies artwork | Backed by retail Goodie archive texture refs and matched exported texture rows. |
| Goodies models | `45/45` model-bearing Goodies currently match loose mesh catalog rows. |
| Goodies videos | `34` Goodie video rows link to Media video inventory and hand off to the Media page. |
| Goodies levels | `5` rows are metadata/unlock entries, not local preview assets. |
| Goodies titles | Derived from extracted language/catalog data where available, with source/reference naming used only as evidence context. |

## Important Goodies Counts

| Count | Meaning |
| ---: | --- |
| `233` | Displayable Goodie rows represented by the current catalog model. |
| `232` | Shipped Goodie resource archives found for displayable slots. |
| `232` | Displayable FMV slot 33 with no separate `goodie_232_res_PC.aya` archive expected. |
| `194` | Texture-bearing Goodie rows with matched texture catalog rows. |
| `45` | Model-bearing Goodie rows with matched mesh catalog rows. |
| `34` | Video Goodie rows linked to video inventory. |
| `5` | Level/metadata Goodie rows without local preview assets. |
| `71-73` | Shipped texture-only archives not exposed by the known source-grid wall mapping. |

## What Works In WinUI Today

- Texture/artwork Goodies can use local exported PNG preview paths when a generated catalog is configured.
- Model Goodies can use matched FBX exports and current wireframe/export-based preview metadata.
- Model rows can link to matched texture catalog entries for inspection.
- Video Goodies can hand off to Media and select a representative linked video row, proven for `Goodie 077 - Development` -> `UsTheMovie` -> `Credits Video`.
- The app labels static catalog coverage separately from runtime Goodies wall proof.

## Post-Maximized WinUI Smoke Refresh

After the WinUI app was changed to start maximized by default, the private full-catalog native smokes were rerun with the current generated catalog:

| Smoke | Result | What it proves |
| --- | --- | --- |
| `AssetLibrary_CyclesRepresentativeRealRowsWhenCatalogProvided` | PASS, `1/1` | Representative real texture/model catalog rows still render and interact in the maximized WinUI app. |
| `AssetLibrary_CapturesRealGoodiesBrowserWhenCatalogProvided` | PASS, `1/1` | Representative real Goodies model/artwork/video rows still render, and the video Goodie handoff still selects `Credits Video` in Media. |

The screenshots and raw catalog paths remain private under ignored `subagents/` outputs.

## What Is Still Not Proven

- A full textured and animated in-app 3D model viewer.
- Runtime replay of the Goodies wall in the running game.
- Runtime unlock animation or state transition for every Goodie.
- Runtime reachability for Goodies `71-73`.
- Public redistribution rights or public packaging of extracted Goodie assets.
- Recreating the whole game from scratch from the current extracted/static evidence.

## Product Boundary

The current WinUI Asset Library should continue to say "cataloged", "extracted", "previewed", "linked", or "wireframe/export-based" when that is the actual evidence.

It should not imply:

- live runtime proof,
- complete textured model viewing,
- complete game reconstruction,
- or public-safe redistribution of private extracted assets.

## Next Best Targets

- Harden a real Goodies wall/grid product design only after explicitly approving the visual interaction.
- Improve in-app model viewing from wireframe/export-based toward textured previews using the already matched texture links.
- Run copied-profile runtime proof for representative Goodies wall selections once static coverage is stable.
- Continue Ghidra/static RE on Goodies 71-73 and Goodies viewer behavior without mutating the installed game.
