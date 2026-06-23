# WinUI Model Sidecar Texture Preview - 2026-05-08

Status: public-safe WinUI/AppCore sidecar texture preview affordance

## Scope

This pass makes the static model-texture evidence more usable in the WinUI Asset Library. The prior probe proved that exported FBX model texture references resolve to mesh-export sidecar textures, but the native UI could only hand off to direct texture catalog rows. WinUI now keeps the direct-catalog handoff when available and falls back to a local sidecar texture preview when a model binding resolves only through the FBX sidecar texture folder.

No BEA runtime was launched. No `BEA.exe`, save, Ghidra project, installed game file, exported FBX, texture sidecar, screenshot, or private catalog artifact was mutated or committed.

## Commands

| Command / Check | Result | Important output | What it proves |
| --- | --- | --- | --- |
| `dotnet test .\OnslaughtCareerEditor.AppCore.Tests\OnslaughtCareerEditor.AppCore.Tests.csproj --nologo --filter "FullyQualifiedName~AssetCatalogServiceTests"` | PASS | `55/55` passed. | Confirms AppCore resolves sidecar textures from both loose-mesh and embedded-mesh export paths without relying on private assets. |
| Parallel `dotnet build` launched during the AppCore test | FAIL/expected tooling error | `CS2012` file lock on AppCore `obj` output. | Reconfirms the known repo rule: .NET build/test commands sharing AppCore outputs must be run serially. |
| `dotnet build .\OnslaughtCareerEditor.WinUI\OnslaughtCareerEditor.WinUI.csproj --nologo` | PASS | Build succeeded with `0 Warning(s)` and `0 Error(s)`. | Confirms the sidecar preview UI compiles after the serial rerun. |
| `dotnet test .\OnslaughtCareerEditor.UiTests\OnslaughtCareerEditor.UiTests.csproj --nologo --filter "FullyQualifiedName~WinUiProductLaneTests"` | PASS | `14/14` passed. | Confirms source-level WinUI product-lane assertions guard the sidecar preview affordance. |
| `ONSLAUGHT_WINUI_REAL_ASSET_CATALOG=<ignored-private-catalog>; dotnet test .\OnslaughtCareerEditor.UiTests\OnslaughtCareerEditor.UiTests.csproj --nologo --filter "FullyQualifiedName~WinUiVisualSmokeTests.AssetLibrary_CyclesRepresentativeRealRowsWhenCatalogProvided"` | PASS | `1/1` passed. | Confirms the native WinUI Asset Library still cycles representative full-install texture/model rows and renders the updated model texture-link text against the ignored private catalog. |
| `cmd.exe /c npm run test:md-links` | PASS | Markdown link check passed. | Confirms the public readiness note links safely. |
| `cmd.exe /c npm run test:doc-commands` | PASS | Documented npm commands checked `1107`. | Confirms documented command references remain synchronized after the new readiness note. |
| `py -3 tools\docsync_check.py` | PASS | Docsync policy check passed. | Confirms mirrored docs remain synchronized. |
| `cmd.exe /c npm run test:repo-hygiene` | PASS | Repo text hygiene check passed. | Confirms the copy/evidence wording does not trip stale/private wording guards. |
| `py -3 tools\release_curated_manifest.py` and `--check` | PASS | Selected files `1403`. | Adds the public-safe readiness note to curated release accounting and verifies allowlist synchronization. |
| `py -3 tools\release_profile_snapshot.py` and `--check` | PASS | Counts `R0=1461 R2=0 R3=2 R4=18187`. | Confirms release profile outputs are current after the sidecar preview evidence update. |
| `cmd.exe /c npm run test:public-allowlist` | PASS | Rows checked `1403`. | Confirms public allowlist safety still excludes private/runtime/generated asset families. |
| State/manifest JSON parse | PASS | `json ok`. | Confirms repo state files and curated release manifest remain valid JSON. |
| `git diff --check` | PASS | No whitespace errors; known generated-TSV line-ending warnings only. | Confirms the tracked diff is whitespace-clean. |
| Process check for `BEA`, `cdb`, `ghidra`, `analyzeHeadless`, and `OnslaughtCareerEditor.WinUI` | PASS | `process cleanup ok`. | Confirms this sidecar preview wave left no game, debugger, Ghidra, headless, or WinUI process running. |

## Public-Safe Findings

- `AssetModelTextureLinkService` now resolves sidecar texture files from the generated export root for loose and embedded model exports.
- The selected-model link text reports sidecar preview file coverage separately from direct catalog links.
- The `View linked texture` button still opens direct catalog texture rows when a direct catalog match exists.
- If no direct catalog texture row exists but a sidecar texture file is present, the button becomes `Preview sidecar texture` and loads that local sidecar image in the Asset Library preview surface.

## What This Proves

- The WinUI Asset Library can use sidecar-backed texture evidence as a native preview affordance instead of only as documentation.
- The AppCore path resolution works for both loose model exports and embedded model exports.
- The feature remains public-safe: private asset files, paths, screenshots, and generated catalog data stay local/ignored.

## Still Not Claimed

- Native WinUI textured 3D model rendering.
- Material, shader, alpha, animation, skeleton, or lighting parity with the retail renderer.
- Runtime in-game model-viewer playback.
- Public redistribution rights for extracted textures or raw exported FBX files.
