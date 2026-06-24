# Model Texture Linkage Probe - 2026-05-08

Status: public-safe model-texture linkage probe over ignored full-install exports

## Scope

This pass adds a repeatable probe for exported FBX model texture references. It answers whether the current model exports carry usable texture filenames and whether those names resolve to local mesh texture sidecars, without committing any private textures or raw exported models.

No BEA runtime was launched. No `BEA.exe`, save, Ghidra project, installed game file, exported FBX, or texture sidecar was mutated. Raw FBX files, texture sidecars, absolute paths, and private catalog data remain ignored under `subagents/`.

## Commands

| Command / Check | Result | Important output | What it proves |
| --- | --- | --- | --- |
| `py -3 -m py_compile tools\model_texture_linkage_probe.py tools\model_texture_linkage_probe_test.py` | PASS | No compiler output. | Confirms the probe and unit fixture are syntactically valid. |
| `cmd.exe /c npm run test:model-texture-linkage` | PASS | Fixture tests `2/2`. | Confirms the probe strips private FBX/export paths, counts exact/stem sidecar matches, records row-level catalog/sidecar readiness, emits representative sanitized model samples, and fails when sidecar texture coverage is missing. |
| `py -3 tools\model_texture_linkage_probe.py --catalog subagents\asset-full-install-2026-05-07\full-export\asset_catalog\catalog.json --check --out subagents\model-material-semantics-2026-05-08\model-texture-linkage-after-resolver.json` after resolver alignment | PASS | Models `352`; rows with refs `352`; unique refs `213`; missing sidecars `0`; catalog-missing refs `0`; rows all catalog-mapped `352`; rows with catalog-missing refs `0`; rows with missing sidecars `0`; representative all-direct sample `arachnid.msh`. | Confirms every checked real model texture reference resolves to a local mesh-texture sidecar and a catalog texture row after excluding template/default material placeholders and matching catalog export filenames/compact variants. |
| `cmd.exe /c npm run test:md-links` | PASS | Markdown link check passed. | Confirms the new readiness note links safely. |
| `cmd.exe /c npm run test:doc-commands` | PASS | Documented npm commands checked `1166`. | Confirms the new npm script reference is synchronized with docs. |
| `py -3 tools\docsync_check.py` | PASS | Docsync policy check passed. | Confirms the lessons mirror update stayed synchronized. |
| `cmd.exe /c npm run test:repo-hygiene` | PASS | Hygiene unit tests `29/29`; live repo hygiene PASS. | Confirms public docs avoid stale/private wording violations. |
| `py -3 tools\release_curated_manifest.py --check` | PASS | Selected files `1403`. | Confirms the public-safe probe, test, and readiness note remain included in curated release accounting. |
| `py -3 tools\release_profile_snapshot.py` and `--check` | PASS | Counts `R0=1456 R2=0 R3=2 R4=18187`. | Confirms release profile outputs are current after the new public-safe files. |
| `cmd.exe /c npm run test:public-allowlist` | PASS | Rows checked `1401`. | Confirms public allowlist safety still excludes private/runtime/generated asset families. |
| State/manifest JSON parse | PASS | `json ok`. | Confirms repo state files and curated release manifest remain valid JSON. |
| `git diff --check` | PASS | No whitespace errors; known generated-TSV line-ending warnings only. | Confirms the tracked diff is whitespace-clean. |
| Process check for `BEA`, `cdb`, `ghidra`, `analyzeHeadless`, and `OnslaughtCareerEditor.WinUI` | PASS | `process cleanup ok`. | Confirms this static/catalog probe wave left no game, debugger, Ghidra, or WinUI process running. |

## Public-Safe Findings

| Metric | Value |
| --- | ---: |
| Model rows checked | `352` |
| Loose model rows with texture refs | `213` |
| Embedded model rows with texture refs | `139` |
| Unique model texture references | `213` |
| Mesh texture sidecar files | `213` |
| Model rows with all real texture refs represented by catalog rows | `352` |
| Model rows with one or more real texture refs not represented by catalog rows | `0` |
| Model rows with one or more missing sidecar texture refs | `0` |
| Unique refs with exact sidecar filename | `212` |
| Unique refs with sidecar stem-only match | `1` |
| Unique refs missing sidecar coverage | `0` |
| Unique refs not represented by texture catalog rows | `0` |
| Unique refs ambiguous in the texture catalog | `1` |
| First representative all-direct-catalog model sample | `arachnid.msh` with refs `a8trust5.png`, `arachtex.png`, `arachtex2.png` |

The current resolver excludes template/default material placeholders such as `default10.png` and matches catalog canonical refs, export filenames, and compact spacing/case variants. The single stem-only sidecar match is an extension mismatch case (`.tga` reference with `.png` sidecar).

## What This Proves

- Exported model FBX files carry texture filename references after excluding template/default FBX material slots.
- Every checked real model texture reference has local sidecar texture coverage by exact filename or stem and catalog-row coverage by canonical/export-name matching.
- The model-texture relationship is strong enough to become a future textured-renderer input, while still needing a separate renderer/material implementation.
- The probe now names sanitized representative rows for the next renderer spike without exposing export paths or private asset payloads.

## Still Not Claimed

- Native WinUI textured model rendering.
- Material, shader, alpha, animation, skeleton, or lighting parity with the retail renderer.
- Runtime in-game model-viewer playback.
- Public redistribution rights for extracted textures or raw exported FBX files.
- Any mutation of saves, Ghidra, or `BEA.exe`.
