# Asset Backend Smoke Evidence - 2026-05-06

Status: public-safe RE/tooling evidence

## Scope

This note records a bounded Battle Engine Aquila asset backend smoke against a local read-only game install. The goal was not a full extraction run. The goal was to prove that the current Python/.NET asset pipeline still works from the active repo after the WinUI-first lane reset.

This report is public-safe. It does not include private absolute Windows paths, raw game asset paths, extracted PNG/FBX files, raw media files, screenshots, hashes of private payloads, data URLs, base64, copied executables, save contents, or proof JSON. Generated outputs remained local and ignored under `subagents/`.

## Command Evidence

| Command | Result | Important output summary | What it proves |
| --- | --- | --- | --- |
| `py -3 tools\export_game_assets.py --game-root <read-only local install> --out-root subagents\asset_backend_smoke_2026-05-06 --limit-archives 1 --limit-loose-textures 1 --limit-loose-meshes 1 --limit-embedded-bodies 1 --progress-every 1` | PASS | Pipeline completed all five phases: AYA inventory, asset export harness, language export, video manifest, and asset catalog generation. | Confirms the bounded asset extraction backend runs against a local install without mutating it. |

## Bounded Smoke Results

| Lane | Result | Public-safe summary |
| --- | --- | --- |
| Packed resource AYA inventory | PASS | One packed archive was inventoried; texture and mesh references were resolved for that archive. |
| Loose texture export | PASS | One loose texture was exported successfully to local ignored output. |
| Loose mesh export | PASS | One loose mesh was exported successfully to local ignored output. |
| Embedded packed mesh export | PASS | One embedded mesh body was exported successfully to local ignored output. |
| Language corpus export | PASS | Six languages were exported and merged; each language reported 2,571 rows. |
| Video manifest export | PASS | 66 local `.vid` files were inventoried; detected magic was `BIKi`. |
| Cross-surface asset catalog | PASS | The bounded catalog contained one texture entry, one loose mesh entry, one embedded mesh entry, 66 video entries, and 2,571 language entries. |

## What Is Proven

- The active `tools/export_game_assets.py` orchestrator still runs end-to-end.
- The .NET `tools/BeaAssetExportHarness` still loads the local AYA extractor runtime.
- Texture PNG export works for at least one bounded loose texture.
- Mesh FBX export works for at least one bounded loose mesh.
- Embedded packed mesh export works for at least one bounded embedded body.
- Language and video inventory lanes still produce merged/catalog-ready outputs.
- The local install was treated as read-only source material; outputs went to ignored local `subagents/` evidence.

## What Is Not Proven

- Full current-corpus extraction coverage for every texture, mesh, embedded body, language row, or video file.
- WinUI asset browser integration.
- Texture/model preview inside the WinUI product.
- Public redistribution rights for extracted assets.
- Rebuildability of the full game from extracted assets.
- Semantic gameplay logic reconstruction.

## Documentation Correction

This wave also corrected stale asset-pipeline wording that still described the backend as intended for future Electron workbench integration. The current posture is WinUI/tooling integration or public bring-your-own-assets packaging; Electron remains archived/reference unless explicitly reactivated.

## Privacy And Release Boundary

Generated extraction outputs, logs, catalogs, and private asset files remain under ignored local output. Public release accounting must continue to exclude generated asset payloads, raw media, private game paths, `subagents/**`, and any extracted PNG/FBX/media output unless a later review explicitly sanitizes and reclassifies a narrow public-safe fixture.
