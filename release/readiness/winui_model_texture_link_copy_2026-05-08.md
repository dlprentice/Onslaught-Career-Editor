# WinUI Model Texture Link Copy Boundary - 2026-05-08

Status: public-safe WinUI copy and UIA assertion update after the model texture sidecar probe

## Scope

This pass tightens the Asset Library wording around model texture links. The prior UI copy described model rows as having "catalog-matched texture links", which was too broad after the model texture linkage probe showed that some exported FBX texture references resolve through mesh-export sidecar textures instead of direct texture catalog rows.

No BEA runtime was launched. No `BEA.exe`, save, Ghidra project, installed game file, exported FBX, texture sidecar, screenshot, or private catalog artifact was mutated or committed.

## Commands

| Command / Check | Result | Important output | What it proves |
| --- | --- | --- | --- |
| `git status --short --branch` | PASS | Clean branch at start. | Confirms the wave started without clobbering uncommitted work. |
| `dotnet build .\OnslaughtCareerEditor.WinUI\OnslaughtCareerEditor.WinUI.csproj --nologo` | PASS | Build succeeded with `0 Warning(s)` and `0 Error(s)`. | Confirms the visible-copy update compiles in the primary WinUI product lane. |
| `dotnet test .\OnslaughtCareerEditor.UiTests\OnslaughtCareerEditor.UiTests.csproj --nologo --filter "FullyQualifiedName~WinUiProductLaneTests"` | PASS | `14/14` passed. | Confirms the source-level product-lane test now guards the direct-catalog versus sidecar wording boundary. |
| `cmd.exe /c npm run test:md-links` | PASS | Markdown link check passed. | Confirms the public readiness note links safely. |
| `cmd.exe /c npm run test:doc-commands` | PASS | Documented npm commands checked `1095`. | Confirms documented command references remain synchronized after the new readiness note. |
| `py -3 tools\docsync_check.py` | PASS | Docsync policy check passed. | Confirms mirrored docs remain synchronized. |
| `cmd.exe /c npm run test:repo-hygiene` | PASS | Repo text hygiene check passed. | Confirms the copy/evidence wording does not trip stale/private wording guards. |
| `py -3 tools\release_curated_manifest.py` and `--check` | PASS | Selected files `1402`. | Adds the public-safe readiness note to curated release accounting and verifies allowlist synchronization. |
| `py -3 tools\release_profile_snapshot.py` and `--check` | PASS | Counts `R0=1460 R2=0 R3=2 R4=18187`. | Confirms release profile outputs are current after the WinUI copy-boundary evidence update. |
| `cmd.exe /c npm run test:public-allowlist` | PASS | Rows checked `1402`. | Confirms public allowlist safety still excludes private/runtime/generated asset families. |
| State/manifest JSON parse | PASS | `json ok`. | Confirms repo state files and curated release manifest remain valid JSON. |
| `git diff --check` | PASS | No whitespace errors; known generated-TSV line-ending warnings only. | Confirms the tracked diff is whitespace-clean. |
| Process check for `BEA`, `cdb`, `ghidra`, `analyzeHeadless`, and `OnslaughtCareerEditor.WinUI` | PASS | `process cleanup ok`. | Confirms this copy-boundary wave left no game, debugger, Ghidra, headless, or WinUI process running. |

## Public-Safe Findings

- The Asset Library catalog summary now says model rows have **direct catalog texture links** when the count comes from direct catalog matching.
- The selected-model detail now says sidecar coverage is tracked separately when direct catalog links are present.
- When no direct catalog row exists for a selected model binding, the UI now says sidecar textures may still be used by the FBX export instead of implying the texture is missing.
- The existing real-catalog visual smoke assertions were updated to expect the direct-catalog wording whenever that explicit native UIA smoke is run with a private generated catalog.

## What This Proves

- WinUI visible copy no longer conflates direct texture catalog rows with mesh-export sidecar texture coverage.
- The primary product lane remains buildable after the copy correction.
- Source-level UI tests guard the wording boundary without requiring private assets.

## Still Not Claimed

- Native WinUI textured model rendering.
- Material, shader, alpha, animation, skeleton, or lighting parity with the retail renderer.
- Runtime in-game model-viewer playback.
- Public redistribution rights for extracted textures or raw exported FBX files.
