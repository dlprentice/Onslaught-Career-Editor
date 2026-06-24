# WinUI Model UV Mapping Metadata Evidence - 2026-05-08

## Scope

This note records a focused static model-metadata improvement for the WinUI Asset Library and AppCore model coverage path. Binary FBX exports now expose readable UV coordinate and UV index counts beside vertices, polygon indices, materials, and texture bindings.

No BEA runtime was launched. No installed game files, saves, private screenshots, private asset payloads, Ghidra project files, or `BEA.exe` bytes were mutated or committed. This is static FBX/catalog metadata evidence only. It does not claim native textured 3D rendering, material-to-UV assignment fidelity, shader parity, animation, skeletons, lighting, or runtime Goodies model-viewer behavior.

## Validation

| Command / Check | Result | Important output | What it proves |
| --- | --- | --- | --- |
| `dotnet test .\OnslaughtCareerEditor.AppCore.Tests\OnslaughtCareerEditor.AppCore.Tests.csproj --nologo --filter "FullyQualifiedName~FbxModelSummaryReaderTests"` before implementation | FAIL, expected red | Compile failed because `AssetModelSummary` did not expose `TextureCoordinateCount` or `TextureCoordinateIndexCount`. | Confirms the reader assertion was written before AppCore exposed UV metadata. |
| `dotnet test .\OnslaughtCareerEditor.AppCore.Tests\OnslaughtCareerEditor.AppCore.Tests.csproj --nologo --filter "FullyQualifiedName~FbxModelSummaryReaderTests"` | PASS | Focused FBX reader tests passed `3/3`. | Confirms binary FBX `UV` and `UVIndex` node array lengths are counted for uncompressed and compressed array fixtures. |
| `dotnet test .\OnslaughtCareerEditor.AppCore.Tests\OnslaughtCareerEditor.AppCore.Tests.csproj --nologo --filter "FullyQualifiedName~AssetCatalogServiceTests.ModelPreviewCoverage_SummarizesWireframeAvailability"` before coverage implementation | FAIL, expected red | Compile failed because `AssetModelPreviewCoverage` and rows did not expose UV coverage fields. | Confirms the coverage assertion was written before AppCore propagated UV metadata. |
| `dotnet test .\OnslaughtCareerEditor.AppCore.Tests\OnslaughtCareerEditor.AppCore.Tests.csproj --nologo --filter "FullyQualifiedName~AssetCatalogServiceTests.ModelPreviewCoverage_SummarizesWireframeAvailability"` | PASS | Focused coverage test passed `1/1`. | Confirms model coverage now reports rows with UV coordinates, rows with UV index arrays, and total UV coordinate/index counts. |
| `dotnet test .\OnslaughtCareerEditor.UiTests\OnslaughtCareerEditor.UiTests.csproj --nologo --filter "FullyQualifiedName~WinUiProductLaneTests.AssetLibrary_IsNativeWinUiCatalogBrowser"` before WinUI copy implementation | FAIL, expected red | Source guard failed because Asset Library XAML did not contain `UV mapping`. | Confirms the WinUI assertion was written before the model facts panel surfaced UV metadata. |
| `dotnet test .\OnslaughtCareerEditor.UiTests\OnslaughtCareerEditor.UiTests.csproj --nologo --filter "FullyQualifiedName~WinUiProductLaneTests.AssetLibrary_IsNativeWinUiCatalogBrowser"` | PASS | Focused source guard passed `1/1`. | Confirms the Asset Library source exposes UV mapping copy and an `AssetModelUvCount` automation target. |
| `dotnet test .\OnslaughtCareerEditor.AppCore.Tests\OnslaughtCareerEditor.AppCore.Tests.csproj --nologo` | PASS | AppCore tests passed `86/86`. | Confirms the expanded model summary and coverage records do not regress broader AppCore behavior. |
| `dotnet build .\OnslaughtCareerEditor.WinUI\OnslaughtCareerEditor.WinUI.csproj --nologo` | PASS | Build succeeded with `0` warnings and `0` errors. | Confirms the primary WinUI app compiles after the UV metadata panel update. |
| `dotnet test .\OnslaughtCareerEditor.UiTests\OnslaughtCareerEditor.UiTests.csproj --nologo --filter "FullyQualifiedName~WinUiProductLaneTests"` | PASS | Product-lane source tests passed `14/14`. | Confirms broader WinUI source guards remain green after adding UV metadata copy. |
| `cmd.exe /c npm run test:md-links` | PASS | Markdown link check passed. | Confirms the new evidence/checklist/extraction links resolve. |
| `cmd.exe /c npm run test:doc-commands` | PASS | Documented npm commands checked `1174`. | Confirms documented npm command references remain synchronized after final evidence updates. |
| `py -3 tools\docsync_check.py` | PASS | Docsync policy check passed. | Confirms the extraction-pipeline doc and lore-book mirror remain synchronized. |
| `cmd.exe /c npm run test:repo-hygiene` | PASS | Repo text hygiene check passed. | Confirms the new public-safe wording avoids stale/private wording guards. |
| `py -3 tools\release_curated_manifest.py --check` | PASS | Selected files `1404`. | Confirms this public-safe note is included in curated release accounting. |
| `py -3 tools\release_profile_snapshot.py --check` | PASS | Counts `R0=1464 R2=0 R3=2 R4=18187`. | Confirms release profile outputs remain synchronized. |
| `cmd.exe /c npm run test:public-allowlist` | PASS | Rows checked `1404`. | Confirms the curated public allowlist still excludes private/runtime/generated asset families. |
| State/manifest JSON parse | PASS | `json ok`. | Confirms repo state files and curated release manifest remain valid JSON. |
| `git diff --check` | PASS | No whitespace errors; Git printed line-ending conversion warnings for `.codex/state` ledgers only. | Confirms the tracked diff is whitespace-clean. |
| Process check for `BEA`, `cdb`, `ghidra`, `analyzeHeadless`, and `OnslaughtCareerEditor.WinUI` | PASS | `process cleanup ok`. | Confirms this static metadata wave left no game, debugger, Ghidra, headless, or WinUI process running. |

## Result

- `FbxModelSummaryReader` now records:
  - `TextureCoordinateCount`
  - `TextureCoordinateIndexCount`
- `AssetModelPreviewCoverage` now records:
  - `RowsWithTextureCoordinates`
  - `RowsWithTextureCoordinateIndices`
  - `TotalTextureCoordinates`
  - `TotalTextureCoordinateIndices`
- `AssetModelPreviewCoverageRow` now carries per-row UV coordinate and UV index counts.
- The WinUI Asset Library catalog coverage summary now reports how many model rows carry UV mapping metadata.
- The selected-model facts panel now has an `UV mapping` row with automation id `AssetModelUvCount`.

## Boundary

This closes one static metadata gap before textured-renderer work. It proves the current binary FBX reader can see UV coordinate/index counts in exported model files. It does not prove which material uses which UV layer, does not draw textured meshes in WinUI, and does not prove retail runtime model-viewer behavior.
