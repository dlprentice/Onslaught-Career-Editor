# WinUI Model Slot Coverage Summary Evidence - 2026-05-08

## Scope

This note records a focused follow-up to the model connection slot metadata work. AppCore now aggregates readable FBX texture-to-material slot/property names across model preview coverage rows, and the WinUI Asset Library coverage summary reports how many model rows expose named material slots.

The ignored full-install Asset Library UIA breadth smoke was rerun against the private generated catalog and now asserts `352/352 model rows report material slots`. No BEA runtime was launched. No installed game files, saves, private screenshots, private asset payloads, Ghidra project files, or `BEA.exe` bytes were mutated or committed.

## Validation

| Command / Check | Result | Important output | What it proves |
| --- | --- | --- | --- |
| `dotnet test .\OnslaughtCareerEditor.AppCore.Tests\OnslaughtCareerEditor.AppCore.Tests.csproj --nologo --filter "FullyQualifiedName~AssetCatalogServiceTests.ModelPreviewCoverage_SummarizesWireframeAvailability"` before implementation | FAIL, expected red | Compile failed because `AssetModelPreviewCoverage` did not expose `RowsWithTextureToMaterialSlotNames` or `TextureToMaterialSlotNames`, and coverage rows did not expose `TextureToMaterialSlotNames`. | Confirms the aggregate coverage assertions were written before AppCore exposed slot-name coverage. |
| `dotnet test .\OnslaughtCareerEditor.UiTests\OnslaughtCareerEditor.UiTests.csproj --nologo --filter "FullyQualifiedName~WinUiProductLaneTests.AssetLibrary_IsNativeWinUiCatalogBrowser"` before implementation | FAIL, expected red | Source guard failed because Asset Library code did not reference `RowsWithTextureToMaterialSlotNames`. | Confirms the WinUI assertion was written before the catalog coverage summary surfaced material-slot coverage. |
| `dotnet test .\OnslaughtCareerEditor.AppCore.Tests\OnslaughtCareerEditor.AppCore.Tests.csproj --nologo --filter "FullyQualifiedName~AssetCatalogServiceTests.ModelPreviewCoverage_SummarizesWireframeAvailability"` | PASS | Focused coverage test passed `1/1`. | Confirms AppCore coverage aggregates row counts and distinct readable slot names. |
| `dotnet test .\OnslaughtCareerEditor.UiTests\OnslaughtCareerEditor.UiTests.csproj --nologo --filter "FullyQualifiedName~WinUiProductLaneTests.AssetLibrary_IsNativeWinUiCatalogBrowser"` | PASS | Focused source guard passed `1/1`. | Confirms the WinUI Asset Library source reports material-slot coverage in the catalog summary. |
| `dotnet test .\OnslaughtCareerEditor.AppCore.Tests\OnslaughtCareerEditor.AppCore.Tests.csproj --nologo` | PASS | AppCore tests passed `86/86`. | Confirms the expanded model coverage record shape does not regress broader AppCore behavior. |
| `dotnet build .\OnslaughtCareerEditor.WinUI\OnslaughtCareerEditor.WinUI.csproj --nologo` | PASS | Build succeeded with `0` warnings and `0` errors. | Confirms the primary WinUI app compiles after the coverage-summary update. |
| `dotnet test .\OnslaughtCareerEditor.UiTests\OnslaughtCareerEditor.UiTests.csproj --nologo --filter "FullyQualifiedName~WinUiProductLaneTests"` | PASS | Product-lane source tests passed `14/14`. | Confirms broader WinUI source guards remain green after adding material-slot coverage summary copy. |
| `$env:ONSLAUGHT_WINUI_REAL_ASSET_CATALOG='...\subagents\asset-full-install-2026-05-07\full-export\asset_catalog\catalog.json'; dotnet test .\OnslaughtCareerEditor.UiTests\OnslaughtCareerEditor.UiTests.csproj --nologo --filter "FullyQualifiedName~WinUiVisualSmokeTests.AssetLibrary_CyclesRepresentativeRealRowsWhenCatalogProvided"` | PASS | Private full-corpus UIA smoke passed `1/1`; the smoke asserts `352/352 model rows report material slots`. | Confirms the native WinUI Asset Library loads the ignored generated full-install catalog and surfaces material-slot coverage without committing private catalog data. |
| `cmd.exe /c npm run test:md-links` | PASS | Markdown link check passed. | Confirms the new evidence/checklist/extraction links resolve. |
| `cmd.exe /c npm run test:doc-commands` | PASS | Documented npm commands checked: `1214`. | Confirms documented npm command references remain synchronized after the material-slot coverage evidence update. |
| `py -3 tools\docsync_check.py` | PASS | Docsync policy check passed. | Confirms extraction-pipeline mirrors remain synchronized. |
| `cmd.exe /c npm run test:repo-hygiene` | PASS | Repo text hygiene check passed. | Confirms the material-slot coverage wording avoids stale/private wording guards. |
| `py -3 tools\release_curated_manifest.py --check` | PASS | Selected files `1404`. | Confirms curated release accounting remains synchronized after adding the public-safe evidence note. |
| `py -3 tools\release_profile_snapshot.py --check` before regeneration | FAIL, expected | Profile artifacts were stale after staging the new public-safe evidence note. | Confirms release profile accounting detected the new tracked readiness file. |
| `py -3 tools\release_profile_snapshot.py` | PASS | Counts `R0=1468 R2=0 R3=2 R4=18187`. | Regenerates release profile artifacts after the new evidence note. |
| `py -3 tools\release_profile_snapshot.py --check` | PASS | Counts `R0=1468 R2=0 R3=2 R4=18187`. | Confirms release profile outputs are synchronized after regeneration. |
| `cmd.exe /c npm run test:public-allowlist` | PASS | Rows checked `1404`. | Confirms public allowlist safety still excludes private/runtime/generated asset families. |
| State/manifest JSON parse | PASS | `json ok`. | Confirms state files and the curated manifest remain valid JSON after the coverage-summary update. |
| `git diff --check` and `git diff --cached --check` | PASS | No whitespace errors. | Confirms the working and staged diffs are clean. |
| Process cleanup check | PASS | `process cleanup ok`. | Confirms no managed BEA, CDB, Ghidra, headless Ghidra, or WinUI smoke process was left running. |

An initial attempted AppCore red run was accidentally started in parallel with a UI test and hit the known shared-output `CS2012` file-lock failure. The serial rerun above is the trusted red result.

## Result

- `AssetModelPreviewCoverage` now records `RowsWithTextureToMaterialSlotNames` and distinct `TextureToMaterialSlotNames`.
- `AssetModelPreviewCoverageRow` now carries each model row's readable texture-to-material slot names.
- The WinUI Asset Library catalog coverage summary now reports material-slot row coverage and a short slot-name sample.
- The private full-corpus UIA smoke proves the current generated full-install catalog reports material-slot coverage for all 352 model rows.

## Boundary

This is static FBX metadata and WinUI coverage-summary evidence. It still does not prove material-to-texture visual correctness, native textured 3D rendering, shader/material parity, animation, skeletons, lighting, runtime Goodies model-viewer behavior, or any public redistribution right for private game assets.
