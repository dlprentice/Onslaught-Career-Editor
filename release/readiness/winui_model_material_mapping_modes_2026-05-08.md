# WinUI Model Material Mapping Modes Evidence - 2026-05-08

## Scope

This note records a static renderer-readiness follow-up for binary FBX material semantics. AppCore now preserves material-layer mapping and reference modes from `LayerElementMaterial` children, specifically `MappingInformationType` and `ReferenceInformationType`.

This matters because a future native textured model viewer needs to know whether material assignments are global, polygon-scoped, indexed, or direct before it can honestly map textures to polygons. This pass does not implement rendering and does not launch the game.

No BEA runtime was launched. No installed game files, saves, Ghidra project, exported FBX files, texture sidecars, or original `BEA.exe` were mutated. Raw full-install host JSON stayed under ignored `subagents/model-material-modes-2026-05-08/`.

## Validation

| Command / Check | Result | Important output | What it proves |
| --- | --- | --- | --- |
| `dotnet test .\OnslaughtCareerEditor.AppCore.Tests\OnslaughtCareerEditor.AppCore.Tests.csproj --nologo --filter "FullyQualifiedName~FbxModelSummaryReaderTests"` before implementation | FAIL, expected red | Compile failed because `AssetModelSummary` did not expose `MaterialMappingModes` or `MaterialReferenceModes`. | Confirms the reader assertion was added before AppCore exposed material mapping/reference modes. |
| `dotnet test .\OnslaughtCareerEditor.AppCore.Tests\OnslaughtCareerEditor.AppCore.Tests.csproj --nologo --filter "FullyQualifiedName~FbxModelSummaryReaderTests"` | PASS | Focused FBX reader tests passed `3/3`. | Confirms the binary FBX reader preserves material mapping/reference mode strings for uncompressed and compressed fixture arrays. |
| `dotnet test .\OnslaughtCareerEditor.AppCore.Tests\OnslaughtCareerEditor.AppCore.Tests.csproj --nologo --filter "FullyQualifiedName~AssetCatalogServiceTests.ModelPreviewCoverage_SummarizesWireframeAvailability"` before coverage implementation | FAIL, expected red | Coverage object did not expose material mapping/reference aggregate fields, then reported `0` until the fixture carried mode nodes. | Confirms aggregate coverage assertions were added before coverage surfaced material mode metadata. |
| `dotnet test .\OnslaughtCareerEditor.AppCore.Tests\OnslaughtCareerEditor.AppCore.Tests.csproj --nologo --filter "FullyQualifiedName~AssetCatalogServiceTests.ModelPreviewCoverage_SummarizesWireframeAvailability"` | PASS | Focused coverage test passed `1/1`. | Confirms AppCore coverage rows and aggregates expose material mapping/reference modes. |
| `dotnet test .\OnslaughtCareerEditor.UiTests\OnslaughtCareerEditor.UiTests.csproj --nologo --filter "FullyQualifiedName~WinUiProductLaneTests.AppCoreHost_ModelPreviewCoverageIncludesMaterialSlotCoverage"` before host implementation | FAIL, expected red | Source guard failed because `Program.cs` did not contain the material mode fields. | Confirms the AppCore host diagnostic assertion was added before the host payload exposed material modes. |
| `dotnet test .\OnslaughtCareerEditor.UiTests\OnslaughtCareerEditor.UiTests.csproj --nologo --filter "FullyQualifiedName~WinUiProductLaneTests.AppCoreHost_ModelPreviewCoverageIncludesMaterialSlotCoverage"` | PASS | Focused host source guard passed `1/1`. | Confirms the read-only host diagnostic payload includes material mapping/reference mode fields. |
| `dotnet build .\OnslaughtCareerEditor.AppCore.Host\OnslaughtCareerEditor.AppCore.Host.csproj --nologo` | PASS | Build succeeded with `0` warnings and `0` errors. | Confirms the host compiles after extending the diagnostic payload. |
| `dotnet run --project .\OnslaughtCareerEditor.AppCore.Host\OnslaughtCareerEditor.AppCore.Host.csproj --no-build -- inspect-asset-model-preview .\subagents\asset-full-install-2026-05-07\full-export\asset_catalog\catalog.json --sample-limit 100` | PASS | Public-safe summary: total model rows `352`, material mapping rows `352`, material reference rows `352`, mapping mode `ByPolygon`, reference mode `IndexToDirect`, material slot `DiffuseColor`. | Confirms the current ignored full-install export corpus reports consistent material assignment semantics through the read-only host diagnostic. |
| `dotnet test .\OnslaughtCareerEditor.AppCore.Tests\OnslaughtCareerEditor.AppCore.Tests.csproj --nologo` | PASS | AppCore tests passed `86/86`. | Confirms the material-mode metadata changes do not regress broader AppCore coverage. |
| `dotnet build .\OnslaughtCareerEditor.WinUI\OnslaughtCareerEditor.WinUI.csproj --nologo` | PASS | Build succeeded with `0` warnings and `0` errors. | Confirms the WinUI lane still builds after the AppCore metadata changes. |
| `dotnet test .\OnslaughtCareerEditor.UiTests\OnslaughtCareerEditor.UiTests.csproj --nologo --filter "FullyQualifiedName~WinUiProductLaneTests"` | PASS | Product-lane tests passed `15/15`. | Confirms broader WinUI product-lane source guards remain green. |
| `npm run test:md-links` | PASS | Markdown link check passed. | Confirms the new evidence and extraction-pipeline links resolve. |
| `npm run test:doc-commands` | PASS | Documented npm script references checked: `1251`. | Confirms documented npm script references remain valid. |
| `py -3 tools\docsync_check.py` | PASS | Docsync policy check passed. | Confirms mirrored docs remain synchronized. |
| `npm run test:repo-hygiene` | PASS | Unit rules passed `29/29`; repo hygiene rules passed. | Confirms the public-safe evidence does not reintroduce stale lane/copy hazards. |
| `py -3 tools\release_curated_manifest.py --check`, regenerate, recheck | PASS | Curated allowlist selected `1406` files after adding this report. | Confirms the public-safe evidence note is included in the curated release manifest. |
| `py -3 tools\release_profile_snapshot.py --check`, regenerate, recheck | PASS | Regenerated profile counts `R0=1471`, `R2=0`, `R3=2`, `R4=18188`. | Confirms release profile artifacts include this new evidence note and remain policy-consistent. |
| `npm run test:public-allowlist` | PASS | Public allowlist safety check passed for `1406` rows. | Confirms no private asset/proof paths were added to the public allowlist. |
| State/manifest JSON parse | PASS | `json ok`. | Confirms state and manifest JSON remain valid. |
| `git diff --check` and `git diff --cached --check` | PASS | No whitespace errors. | Confirms working and staged diffs are clean. |
| Process cleanup check | PASS | `process cleanup ok`. | Confirms no managed BEA, CDB, Ghidra, headless Ghidra, or WinUI smoke process was left running. |

## Result

- `AssetModelSummary` now records material mapping/reference modes.
- `AssetModelPreviewCoverage` now aggregates rows with material mapping/reference modes and distinct mode names.
- `OnslaughtCareerEditor.AppCore.Host inspect-asset-model-preview` now emits those fields in its public-safe read-only diagnostic payload.
- Current full-install static material-mode evidence is:
  - `352/352` model rows with material mapping modes,
  - `352/352` model rows with material reference modes,
  - mapping mode `ByPolygon`,
  - reference mode `IndexToDirect`,
  - texture-to-material slot `DiffuseColor`.

## Boundary

This is static FBX material-assignment metadata. It does not prove native textured WinUI rendering, material/shader/alpha parity, animation, skeletons, lighting, runtime Goodies model-viewer playback, or redistribution rights for private extracted assets.
