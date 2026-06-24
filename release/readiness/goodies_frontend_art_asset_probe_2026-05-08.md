# Goodies FrontEnd Art Asset Probe - 2026-05-08

Status: public-safe catalog/export probe over ignored full-install artifacts

## Scope

This pass adds a repeatable probe for the FrontEnd artwork used around the Goodies wall and gallery shell. It answers a narrower question than the full Asset Library provenance recheck: whether specific Goodies UI/icon/background textures exist in the generated local PC-install catalog and have readable exported PNGs.

No BEA runtime was launched. No `BEA.exe`, save, Ghidra project, installed game file, or generated private asset was mutated. Raw catalog paths, absolute source paths, and exported PNG files remain ignored under `subagents/`.

## Commands

| Command / Check | Result | Important output | What it proves |
| --- | --- | --- | --- |
| `py -3 -m py_compile tools\goodies_frontend_art_probe.py tools\goodies_frontend_art_probe_test.py` | PASS | No compiler output. | Confirms the probe and unit fixture are syntactically valid. |
| `cmd.exe /c npm run test:goodies-frontend-art` | PASS | Parser fixture tests `2/2`. | Confirms the probe reports required rows/dimensions while stripping private source/export paths, and fails when required rows are missing. |
| `py -3 tools\goodies_frontend_art_probe.py --catalog subagents\asset-full-install-2026-05-07\full-export\asset_catalog\catalog.json --check` | PASS | Required FrontEnd Goodies textures `8/8`; adjacent FrontEnd texture rows `28`. | Confirms the ignored full-install catalog contains the targeted Goodies artwork rows and readable PNG exports. |
| `cmd.exe /c npm run test:md-links` | PASS | Markdown link check passed. | Confirms the new readiness note links safely. |
| `cmd.exe /c npm run test:doc-commands` | PASS | Documented npm commands checked `1063`. | Confirms the new npm script reference is synchronized with docs. |
| `py -3 tools\docsync_check.py` | PASS | Docsync policy check passed. | Confirms the lessons mirror update stayed synchronized. |
| `cmd.exe /c npm run test:repo-hygiene` | PASS | Hygiene unit tests `29/29`; live repo hygiene PASS. | Confirms public docs avoid stale/private wording violations. |
| `py -3 tools\release_curated_manifest.py` and `--check` | PASS | Selected files `1398`. | Adds the public-safe probe, test, and readiness note to curated release accounting and verifies generated allowlist synchronization. |
| `py -3 tools\release_profile_snapshot.py` and `--check` | PASS | Counts `R0=1453 R2=0 R3=2 R4=18187`. | Confirms release profile outputs are current after the new public-safe files. |
| `cmd.exe /c npm run test:public-allowlist` | PASS | Rows checked `1398`. | Confirms public allowlist safety still excludes private/runtime/generated asset families. |
| State/manifest JSON parse | PASS | `json ok`. | Confirms repo state files and curated release manifest remain valid JSON. |
| `git diff --check` | PASS | No whitespace errors; known generated-TSV line-ending warnings only. | Confirms the tracked diff is whitespace-clean. |
| Process check for `BEA`, `cdb`, `ghidra`, `analyzeHeadless`, and `OnslaughtCareerEditor.WinUI` | PASS | `process cleanup ok`. | Confirms this static/catalog probe wave left no game, debugger, Ghidra, or WinUI process running. |

## Public-Safe Findings

Required FrontEnd Goodies artwork rows are present and readable:

| Key | Canonical ref | Dimensions |
| --- | --- | --- |
| Goodies icon 1 | `frontend\v2\fe_goodies1.tga` | `32x32` |
| Goodies icon 2 | `frontend\v2\fe_goodies2.tga` | `32x32` |
| Goodies icon 3 | `frontend\v2\fe_goodies3.tga` | `32x32` |
| Goodies icon 4 | `frontend\v2\fe_goodies4.tga` | `64x64` |
| Goodies navigation symbol | `frontend\v3\fe_bea_title_nav_symbol_goodies01.tga` | `128x128` |
| Metal ring transition 1 | `frontend\v2\fe_metal_ring_trans_from_levsel1.tga` | `512x512` |
| Metal ring transition 2 | `frontend\v2\fe_metal_ring_trans_from_levsel2.tga` | `512x512` |
| Rock background | `frontend\v2\fe_rock_background.tga` | `1024x512` |

The generated public-safe summary strips absolute source paths and export paths. It reports counts, canonical refs, dimensions, and proof boundaries only.

## What This Proves

- The local PC-install extraction/catalog pipeline exposes the targeted Goodies FrontEnd artwork assets.
- The extractor produced readable PNG previews for those targeted rows.
- The current Goodies UI work can use real extracted FrontEnd art evidence as a future design input without committing private art.

## Still Not Claimed

- Runtime Goodies wall layout, animation, unlock transition, or input hit testing.
- Runtime in-game model-viewer playback.
- A final WinUI Goodies Browser design or implementation.
- Public redistribution rights for extracted textures or raw private catalogs.
- Any mutation of saves, Ghidra, or `BEA.exe`.
