# WinUI Model UV Mapping Modes Evidence - 2026-05-08

## Scope

This note records a static renderer-readiness follow-up for binary FBX texture-coordinate semantics. AppCore now preserves UV mapping and reference modes from `LayerElementUV` children, specifically `MappingInformationType` and `ReferenceInformationType`.

This matters because a future native textured model viewer needs to know whether UVs are polygon-vertex scoped, indexed, direct, or otherwise arranged before it can honestly map texture coordinates to geometry. This pass does not implement rendering and does not launch the game.

No BEA runtime was launched. No installed game files, saves, Ghidra project, exported FBX files, texture sidecars, or original `BEA.exe` were mutated. Raw full-install host JSON stayed under ignored `subagents/model-uv-modes-2026-05-08/`.

## Validation

| Command / Check | Result | Important output | What it proves |
| --- | --- | --- | --- |
| `dotnet test .\OnslaughtCareerEditor.AppCore.Tests\OnslaughtCareerEditor.AppCore.Tests.csproj --nologo --filter "FullyQualifiedName~FbxModelSummaryReaderTests"` before implementation | FAIL, expected red | Compile failed because `AssetModelSummary` did not expose `TextureCoordinateMappingModes` or `TextureCoordinateReferenceModes`. | Confirms the reader assertion was added before AppCore exposed UV mapping/reference modes. |
| `dotnet test .\OnslaughtCareerEditor.AppCore.Tests\OnslaughtCareerEditor.AppCore.Tests.csproj --nologo --filter "FullyQualifiedName~FbxModelSummaryReaderTests"` | PASS | Focused FBX reader tests passed `3/3`. | Confirms the binary FBX reader preserves UV mapping/reference mode strings for uncompressed and compressed fixture arrays. |
| `dotnet test .\OnslaughtCareerEditor.AppCore.Tests\OnslaughtCareerEditor.AppCore.Tests.csproj --nologo --filter "FullyQualifiedName~AssetCatalogServiceTests.ModelPreviewCoverage_SummarizesWireframeAvailability"` before coverage implementation | FAIL, expected red | Coverage object did not expose UV mapping/reference aggregate fields. | Confirms aggregate coverage assertions were added before coverage surfaced UV mode metadata. |
| `dotnet test .\OnslaughtCareerEditor.AppCore.Tests\OnslaughtCareerEditor.AppCore.Tests.csproj --nologo --filter "FullyQualifiedName~AssetCatalogServiceTests.ModelPreviewCoverage_SummarizesWireframeAvailability"` | PASS | Focused coverage test passed `1/1`. | Confirms AppCore coverage rows and aggregates expose UV mapping/reference modes. |
| `dotnet test .\OnslaughtCareerEditor.UiTests\OnslaughtCareerEditor.UiTests.csproj --nologo --filter "FullyQualifiedName~WinUiProductLaneTests.AppCoreHost_ModelPreviewCoverageIncludesMaterialSlotCoverage"` before host implementation | FAIL, expected red | Source guard failed because `Program.cs` did not contain the UV mode fields. | Confirms the AppCore host diagnostic assertion was added before the host payload exposed UV modes. |
| `dotnet test .\OnslaughtCareerEditor.UiTests\OnslaughtCareerEditor.UiTests.csproj --nologo --filter "FullyQualifiedName~WinUiProductLaneTests.AppCoreHost_ModelPreviewCoverageIncludesMaterialSlotCoverage"` | PASS | Focused host source guard passed `1/1`. | Confirms the read-only host diagnostic payload includes UV mapping/reference mode fields. |
| `dotnet build .\OnslaughtCareerEditor.AppCore.Host\OnslaughtCareerEditor.AppCore.Host.csproj --nologo` | PASS | Build succeeded with `0` warnings and `0` errors. | Confirms the host compiles after extending the diagnostic payload. |
| `dotnet run --project .\OnslaughtCareerEditor.AppCore.Host\OnslaughtCareerEditor.AppCore.Host.csproj --no-build -- inspect-asset-model-preview .\subagents\asset-full-install-2026-05-07\full-export\asset_catalog\catalog.json --sample-limit 100` | PASS | Public-safe summary: total model rows `352`, UV mapping rows `352`, UV reference rows `352`, UV mapping mode `ByPolygonVertex`, UV reference mode `IndexToDirect`. | Confirms the current ignored full-install export corpus reports consistent UV coordinate semantics through the read-only host diagnostic. |
| `dotnet test .\OnslaughtCareerEditor.AppCore.Tests\OnslaughtCareerEditor.AppCore.Tests.csproj --nologo` | PASS | AppCore tests passed `86/86`. | Confirms the AppCore parser and catalog changes did not regress the broader core test suite. |
| `dotnet build .\OnslaughtCareerEditor.WinUI\OnslaughtCareerEditor.WinUI.csproj --nologo` | PASS | Build succeeded with `0` warnings and `0` errors. | Confirms the primary WinUI lane still builds after the AppCore shape change. |
| `dotnet test .\OnslaughtCareerEditor.UiTests\OnslaughtCareerEditor.UiTests.csproj --nologo --filter "FullyQualifiedName~WinUiProductLaneTests"` | PASS | Product-lane source/UI guard tests passed `15/15`. | Confirms product-lane guard coverage remains green. |
| `cmd.exe /c npm run test:md-links` | PASS | Markdown link check passed. | Confirms the new readiness and extraction-doc links resolve. |
| `cmd.exe /c npm run test:doc-commands` | PASS | Documented script references checked: `1263`. | Confirms the documentation command references remain valid. |
| `py -3 tools\docsync_check.py` | PASS | Docsync policy check passed. | Confirms mirrored docs remain synchronized. |
| `cmd.exe /c npm run test:repo-hygiene` | PASS | Repo text hygiene tests passed `29/29`; repo hygiene scanner passed. | Confirms public text rules did not regress. |
| `py -3 tools\release_curated_manifest.py --check`, regenerate, recheck | PASS | Initial check found stale allowlist output after adding the evidence note; regenerated output selected `1407` public files and recheck passed. | Confirms the new public-safe evidence note is included in the curated release manifest and allowlist. |
| `py -3 tools\release_profile_snapshot.py --check`, regenerate, recheck | PASS | Initial check found stale release-profile artifacts; regenerated snapshot reports `R0=1471`, `R2=0`, `R3=2`, `R4=18188`; recheck passed. | Confirms release profile accounting is current. |
| `cmd.exe /c npm run test:public-allowlist` | PASS | Public allowlist safety check passed for `1407` rows. | Confirms the curated public candidate list remains safe after adding the evidence note. |

## Result

- `AssetModelSummary` now records UV mapping/reference modes.
- `AssetModelPreviewCoverage` now aggregates rows with UV mapping/reference modes and distinct mode names.
- `OnslaughtCareerEditor.AppCore.Host inspect-asset-model-preview` now emits those fields in its public-safe read-only diagnostic payload.
- Current full-install static UV-mode evidence is:
  - `352/352` model rows with UV mapping modes,
  - `352/352` model rows with UV reference modes,
  - UV mapping mode `ByPolygonVertex`,
  - UV reference mode `IndexToDirect`.

## Boundary

This is static FBX UV-coordinate metadata. It does not prove native textured WinUI rendering, material/shader/alpha parity, animation, skeletons, lighting, runtime Goodies model-viewer playback, or redistribution rights for private extracted assets.
