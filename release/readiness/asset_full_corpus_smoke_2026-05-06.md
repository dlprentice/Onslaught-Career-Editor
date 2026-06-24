# Asset Full-Corpus Smoke Evidence - 2026-05-06

Status: public-safe RE/tooling evidence, GREEN after follow-up

## Scope

This note records a full-corpus Battle Engine Aquila asset backend smoke against a local read-only game install. The command ran the current Python/.NET asset orchestrator without the bounded export limits used in the prior smoke.

This is not a public asset release and not a claim that every model is reconstructable. It is a coverage proof for the current extractor pipeline. Generated outputs remained local and ignored under `subagents/`.

This report is public-safe. It does not include private absolute Windows paths, raw game asset paths, extracted PNG/FBX files, raw media files, screenshots, hashes of private payloads, data URLs, base64, copied executables, save contents, or proof JSON.

## Command Evidence

| Command | Result | Important output summary | What it proves |
| --- | --- | --- | --- |
| `py -3 tools\export_game_assets.py --game-root <read-only local install> --out-root subagents\asset_full_export_2026-05-06 --progress-every 50` | PASS/YELLOW | The orchestrator completed all five phases and wrote a final summary. Texture export, language export, video manifest, and catalog generation completed. Mesh conversion completed partially. | Confirms the full pipeline can run across the current local corpus and exposes exact remaining extractor coverage gaps. |
| `py -3 tools\export_game_assets.py --game-root <read-only local install> --out-root subagents\asset_full_export_split_2026-05-06 --progress-every 200` after split-lane orchestrator hardening | PASS | The orchestrator completed all five phases with one asset-export harness process per lane. Texture, loose mesh, embedded mesh, language, video, and catalog generation completed. | Confirms the full corpus extracts successfully when the legacy exporter lanes are isolated and run serially. |

## Post-Hardening Resolution

The initial full-corpus run was YELLOW because the single harness process reported loose-mesh and embedded-mesh failures. Follow-up diagnostics showed the same mesh files succeed when the legacy extractor lanes run independently. `tools/export_game_assets.py` now invokes the texture, loose-mesh, and embedded-mesh harness lanes as separate serial processes and writes a combined summary with `process_model = "separate_process_per_lane"`.

The follow-up full run is the accepted current proof for full-corpus backend extraction.

## Full-Corpus Results

| Lane | Result | Public-safe summary |
| --- | --- | --- |
| Packed resource AYA inventory | PASS | Packed resource inventory resolved 601 text texture references, 209 reference mesh references, 206 goodie texture references, and 42 goodie mesh references. |
| Loose texture export | PASS | 847 attempted, 847 succeeded, 0 failed. |
| Loose mesh export | PASS after follow-up | Initial single-process run was 141/213. Split-lane follow-up run was 213 attempted, 213 succeeded, 0 failed. |
| Embedded packed mesh export | PASS after follow-up | Initial single-process run was 0/139. Split-lane follow-up run was 139 attempted, 139 succeeded, 0 failed. |
| Language corpus export | PASS | Six languages exported and merged; each language reported 2,571 rows. |
| Video manifest export | PASS | 66 local `.vid` files inventoried; detected magic was `BIKi`. |
| Cross-surface asset catalog | PASS after follow-up | Catalog generation completed with 828 texture entries, 213 loose mesh entries, 139 embedded mesh entries, 66 video entries, 2,571 language entries, and 3,817 total entries. |

## What Is Proven

- The full current texture corpus exported through the existing backend path.
- The full current language corpus and video manifest paths still work.
- Packed resource inventory resolves texture and mesh references across the local resource corpus.
- The catalog builder can produce a full cross-surface catalog from complete manifests.
- The existing loose-mesh exporter works for all 213 current loose mesh files when run in an isolated harness lane.
- The existing embedded-mesh exporter works for all 139 current embedded mesh bodies when run in an isolated harness lane.
- The pipeline records failures with improved detail when they occur.

## What Is Not Proven

- WinUI asset browser/preview integration.
- Public redistribution rights for extracted assets.
- Rebuildability of the full game from extracted assets.
- Semantic gameplay logic reconstruction.

## Follow-Up

WinUI asset browser/preview integration is still not proven. The backend extraction proof should feed a later product slice that imports the generated catalog from an app-owned/local artifact root and presents textures/models without shipping private asset payloads.

## Privacy And Release Boundary

Generated extraction outputs, logs, catalogs, and private asset files remain under ignored local output. Public release accounting must continue to exclude generated asset payloads, raw media, private game paths, `subagents/**`, and any extracted PNG/FBX/media output unless a later review explicitly sanitizes and reclassifies a narrow public-safe fixture.
