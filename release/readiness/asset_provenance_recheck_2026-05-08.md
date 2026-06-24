# Asset Provenance Recheck - 2026-05-08

Status: public-safe recheck over ignored full-install export artifacts

## Scope

This pass rechecked the existing ignored full-install asset export after the user asked whether the current WinUI Asset Library and Goodies browser are showing assets actually extracted from the retail PC install or only source-tree/sample material.

No BEA runtime was launched. No `BEA.exe`, save, Ghidra project, or installed game file was mutated. Raw paths, exported PNG/FBX files, screenshots, manifests, and private catalog data remain ignored under `subagents/`.

## Commands

| Command / Check | Result | Important output | What it proves |
| --- | --- | --- | --- |
| Parse `subagents/asset-full-install-2026-05-07/full-export/asset_catalog/catalog.json` | PASS | Catalog rows: textures `828`, loose meshes `213`, embedded meshes `139`, Goodies `233`, videos `66`; total catalog entries `4050`. | Confirms the configured full-install catalog still contains broad retail-install asset coverage. |
| Check exported file existence from catalog rows | PASS | Texture PNG exports `828/828`; loose FBX exports `213/213`; embedded FBX exports `139/139`. | Confirms current catalog row paths resolve to local private exports, not merely metadata stubs. |
| Parse `subagents/asset-full-install-2026-05-07/full-export/extraction_summary.json` | PASS | Backend export recorded loose textures `847/847`, loose meshes `213/213`, embedded meshes `139/139`, language rows `2571`, videos `66`, Goodies rows `233`. | Confirms the broader backend extraction was run against the user's read-only local PC game install. |
| Parse `subagents/asset-full-install-2026-05-07/model-preview-coverage.json` | PASS | Model rows `352`; existing exports `352`; metadata rows `352`; wireframe rows `352`; missing exports `0`; unreadable exports `0`. | Confirms current in-app model previews are backed by readable exported FBX geometry metadata for the full model-row set. |

## Answer

The current WinUI Asset Library and Goodies browser are backed by real generated catalog/export data from the user's installed PC game files when that full-install catalog is loaded. They are not just source-tree sample art or hard-coded model/texture examples.

Current proof level:

- texture/artwork previews: local exported PNG files from the generated catalog,
- model rows and model Goodies: local exported FBX files plus readable metadata and wireframe geometry,
- video Goodies: linked to the generated media catalog and Media handoff,
- Goodies titles/families: generated from retail resource/archive/language evidence plus source/binary RE labels where documented.

## Still Not Claimed

- Full textured, material-aware, animated native WinUI 3D rendering.
- Runtime Goodies wall animation, unlock transition, or in-game model-viewer loop parity.
- Public redistribution rights for extracted textures, models, videos, or raw manifests.
- A rebuildable game runtime from the current static extraction evidence.

## Product Copy Follow-Up

The WinUI loaded-catalog provenance text now says broad catalogs are a `broad PC-install export from local game files, not source-tree sample data`. UI tests assert this wording so the product surface keeps the same boundary as this evidence note.
