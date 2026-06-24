# WinUI Model Connection Metadata Evidence - 2026-05-08

## Scope

This note records a focused static model-metadata improvement for AppCore and the WinUI Asset Library. Binary FBX exports now expose object connection counts, property connection counts, and texture-to-material connection counts beside geometry, UV, material-layer, material-assignment, material, and texture-binding metadata.

No BEA runtime was launched. No installed game files, saves, private screenshots, private asset payloads, Ghidra project files, or `BEA.exe` bytes were mutated or committed. This is static FBX/catalog metadata evidence only. It does not claim material-to-texture correctness, textured 3D rendering, shader/material parity, animation, skeletons, lighting, or runtime Goodies model-viewer behavior.

## Validation

| Command / Check | Result | Important output | What it proves |
| --- | --- | --- | --- |
| `dotnet test .\OnslaughtCareerEditor.AppCore.Tests\OnslaughtCareerEditor.AppCore.Tests.csproj --nologo --filter "FullyQualifiedName~FbxModelSummaryReaderTests"` before implementation | FAIL, expected red | Compile failed because `AssetModelSummary` did not expose `ObjectConnectionCount`, `PropertyConnectionCount`, or `TextureToMaterialConnectionCount`. | Confirms the reader assertion was written before AppCore exposed connection metadata. |
| `dotnet test .\OnslaughtCareerEditor.AppCore.Tests\OnslaughtCareerEditor.AppCore.Tests.csproj --nologo --filter "FullyQualifiedName~FbxModelSummaryReaderTests"` | PASS | Focused FBX reader tests passed `3/3`. | Confirms binary FBX `C` connection nodes are counted and OP Texture-to-Material links are recognized from fixture object ids. |
| `dotnet test .\OnslaughtCareerEditor.AppCore.Tests\OnslaughtCareerEditor.AppCore.Tests.csproj --nologo --filter "FullyQualifiedName~AssetCatalogServiceTests.ModelPreviewCoverage_SummarizesWireframeAvailability"` before coverage implementation | FAIL, expected red | Compile failed because `AssetModelPreviewCoverage` and rows did not expose connection coverage fields. | Confirms the coverage assertion was written before AppCore propagated connection metadata. |
| `dotnet test .\OnslaughtCareerEditor.AppCore.Tests\OnslaughtCareerEditor.AppCore.Tests.csproj --nologo --filter "FullyQualifiedName~AssetCatalogServiceTests.ModelPreviewCoverage_SummarizesWireframeAvailability"` | PASS | Focused coverage test passed `1/1`. | Confirms model coverage now reports rows and totals for object, property, and texture-to-material connections. |
| `dotnet test .\OnslaughtCareerEditor.UiTests\OnslaughtCareerEditor.UiTests.csproj --nologo --filter "FullyQualifiedName~WinUiProductLaneTests.AssetLibrary_IsNativeWinUiCatalogBrowser"` before WinUI copy implementation | FAIL, expected red | Source guard failed because Asset Library XAML did not contain `Texture-material links`. | Confirms the WinUI assertion was written before the model facts panel surfaced connection metadata. |
| `dotnet test .\OnslaughtCareerEditor.UiTests\OnslaughtCareerEditor.UiTests.csproj --nologo --filter "FullyQualifiedName~WinUiProductLaneTests.AssetLibrary_IsNativeWinUiCatalogBrowser"` | PASS | Focused source guard passed `1/1`. | Confirms the Asset Library source exposes texture-material link copy and an `AssetModelConnectionCount` automation target. |
| `dotnet test .\OnslaughtCareerEditor.AppCore.Tests\OnslaughtCareerEditor.AppCore.Tests.csproj --nologo` | PASS | AppCore tests passed `86/86`. | Confirms the expanded model summary and coverage records do not regress broader AppCore behavior. |
| `dotnet build .\OnslaughtCareerEditor.WinUI\OnslaughtCareerEditor.WinUI.csproj --nologo` | PASS | Build succeeded with `0` warnings and `0` errors. | Confirms the primary WinUI app compiles after the connection metadata panel update. |
| `dotnet test .\OnslaughtCareerEditor.UiTests\OnslaughtCareerEditor.UiTests.csproj --nologo --filter "FullyQualifiedName~WinUiProductLaneTests"` | PASS | Product-lane source tests passed `14/14`. | Confirms broader WinUI source guards remain green after adding connection metadata copy. |
| `cmd.exe /c npm run test:md-links` | PASS | Markdown link check passed. | Confirms the new evidence/checklist/extraction links resolve. |
| `cmd.exe /c npm run test:doc-commands` | PASS | Documented npm commands checked: `1202`. | Confirms documented npm command references remain synchronized after the connection metadata evidence update. |
| `py -3 tools\docsync_check.py` | PASS | Docsync policy check passed. | Confirms extraction-pipeline mirrors remain synchronized. |
| `cmd.exe /c npm run test:repo-hygiene` | PASS | Repo text hygiene check passed. | Confirms the connection metadata wording avoids stale/private wording guards. |
| `py -3 tools\release_curated_manifest.py --check` | PASS | Selected files `1404`. | Confirms curated release accounting remains synchronized after adding the public-safe evidence note. |
| `py -3 tools\release_profile_snapshot.py --check` before regeneration | FAIL, expected | Profile artifacts were stale after staging the new public-safe evidence note. | Confirms release profile accounting detected the new tracked readiness file. |
| `py -3 tools\release_profile_snapshot.py` | PASS | Counts `R0=1466 R2=0 R3=2 R4=18187`. | Regenerates release profile artifacts after the new evidence note. |
| `py -3 tools\release_profile_snapshot.py --check` | PASS | Counts `R0=1466 R2=0 R3=2 R4=18187`. | Confirms release profile outputs are synchronized after regeneration. |
| `cmd.exe /c npm run test:public-allowlist` | PASS | Rows checked `1404`. | Confirms public allowlist safety still excludes private/runtime/generated asset families. |
| State/manifest JSON parse | PASS | `json ok`. | Confirms repo state files and curated release manifest remain valid JSON. |
| `git diff --check` and `git diff --cached --check` | PASS | No whitespace errors. | Confirms the working and staged diffs are whitespace-clean. |
| Process check for `BEA`, `cdb`, `ghidra`, `analyzeHeadless`, and `OnslaughtCareerEditor.WinUI` | PASS | `process cleanup ok`. | Confirms this static metadata wave left no game, debugger, Ghidra, headless, or WinUI process running. |

## Result

- `FbxModelSummaryReader` now records:
  - `ObjectConnectionCount`
  - `PropertyConnectionCount`
  - `TextureToMaterialConnectionCount`
- `AssetModelPreviewCoverage` now records:
  - `RowsWithObjectConnections`
  - `RowsWithPropertyConnections`
  - `RowsWithTextureToMaterialConnections`
  - `TotalObjectConnections`
  - `TotalPropertyConnections`
  - `TotalTextureToMaterialConnections`
- `AssetModelPreviewCoverageRow` now carries per-row connection counts.
- The WinUI Asset Library catalog coverage summary now reports how many model rows carry texture-material link metadata.
- The selected-model facts panel now has a `Texture-material links` row with automation id `AssetModelConnectionCount`.

## Boundary

This closes another static metadata gap before textured-renderer work. It proves the current binary FBX reader can see connection nodes and classify texture-to-material property links in exported model files. It does not prove the linked texture is the final runtime material, texture-slot semantic parity, shader/material parity, alpha handling, render ordering, animation, or retail runtime model-viewer behavior.
