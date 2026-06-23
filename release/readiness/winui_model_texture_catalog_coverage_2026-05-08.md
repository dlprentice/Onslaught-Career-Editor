# WinUI Model Texture Catalog Coverage Evidence - 2026-05-08

## Scope

This note records a focused AppCore coverage improvement for the WinUI Asset Library model path. The app can now distinguish model rows where every readable FBX texture binding resolves to a direct texture catalog row from rows where one or more bindings must rely on mesh-export sidecar texture files.

No BEA runtime was launched. No installed game files, saves, private screenshots, or private asset payloads were committed. This remains static catalog/export readiness evidence, not native textured 3D rendering, material/shader parity, animation, or runtime Goodies model-viewer proof.

## Validation

| Command / Check | Result | Important output | What it proves |
| --- | --- | --- | --- |
| `dotnet test .\OnslaughtCareerEditor.AppCore.Tests\OnslaughtCareerEditor.AppCore.Tests.csproj --nologo --filter "FullyQualifiedName~AssetCatalogServiceTests"` before implementation | FAIL, expected red | Compile failed because `AssetModelTextureLinks`, `AssetModelPreviewCoverage`, and `AssetModelPreviewCoverageRow` did not expose catalog-missing texture binding properties. | Confirms the new assertions were written before production code exposed the requested coverage split. |
| `dotnet test .\OnslaughtCareerEditor.AppCore.Tests\OnslaughtCareerEditor.AppCore.Tests.csproj --nologo --filter "FullyQualifiedName~AssetCatalogServiceTests"` | PASS | Focused AssetCatalogServiceTests passed `57/57`. | Confirms AppCore now reports per-row all-direct-catalog and sidecar-needed texture coverage through fixture-backed tests. |
| `dotnet test .\OnslaughtCareerEditor.AppCore.Tests\OnslaughtCareerEditor.AppCore.Tests.csproj --nologo` | PASS | AppCore tests passed `86/86`. | Confirms the coverage record-shape change did not regress the broader AppCore correctness lane. |
| `dotnet build .\OnslaughtCareerEditor.WinUI\OnslaughtCareerEditor.WinUI.csproj --nologo` | PASS | Build succeeded with `0` warnings and `0` errors. | Confirms the primary WinUI app compiles against the expanded AppCore coverage records. |
| `cmd.exe /c npm run test:md-links` | PASS | Markdown link check passed. | Confirms the new evidence/checklist/extraction links resolve. |
| `cmd.exe /c npm run test:doc-commands` | PASS | Documented npm commands checked `1147`. | Confirms documented npm command references remain synchronized. |
| `py -3 tools\docsync_check.py` | PASS | Docsync policy check passed. | Confirms the extraction-pipeline doc and lore-book mirror remain synchronized. |
| `py -3 tools\release_curated_manifest.py` | PASS | Selected files `1404`. | Adds this public-safe note to curated release accounting. |
| `py -3 tools\release_curated_manifest.py --check` | PASS | Selected files `1404`. | Confirms curated release accounting remains synchronized. |
| `py -3 tools\release_profile_snapshot.py` | PASS | Counts `R0=1463 R2=0 R3=2 R4=18187`. | Refreshes public/review/private release classification artifacts after adding this note. |
| `py -3 tools\release_profile_snapshot.py --check` | PASS | Counts `R0=1463 R2=0 R3=2 R4=18187`. | Confirms release profile artifacts remain synchronized. |
| `cmd.exe /c npm run test:repo-hygiene` | PASS | Repo text hygiene check passed. | Confirms the new public-safe wording avoids stale/private wording guards. |
| `cmd.exe /c npm run test:public-allowlist` | PASS | Rows checked `1404`. | Confirms the curated public allowlist still excludes private/runtime/generated asset families. |
| `dotnet test .\OnslaughtCareerEditor.UiTests\OnslaughtCareerEditor.UiTests.csproj --nologo --filter "FullyQualifiedName~WinUiProductLaneTests.AssetLibrary_IsNativeWinUiCatalogBrowser"` before implementation | FAIL, expected red | Source guard failed because Asset Library copy did not contain `sidecar-needed texture rows`. | Confirms the visible-copy assertion was added before the WinUI summary exposed the coverage split. |
| `dotnet test .\OnslaughtCareerEditor.UiTests\OnslaughtCareerEditor.UiTests.csproj --nologo --filter "FullyQualifiedName~WinUiProductLaneTests.AssetLibrary_IsNativeWinUiCatalogBrowser"` | PASS | Focused source guard passed `1/1`. | Confirms the Asset Library source contains the new sidecar-needed texture-row summary copy. |
| `dotnet build .\OnslaughtCareerEditor.WinUI\OnslaughtCareerEditor.WinUI.csproj --nologo` after WinUI copy update | PASS | Build succeeded with `0` warnings and `0` errors. | Confirms the primary WinUI app compiles after the summary copy update. |
| `dotnet test .\OnslaughtCareerEditor.UiTests\OnslaughtCareerEditor.UiTests.csproj --nologo --filter "FullyQualifiedName~WinUiProductLaneTests"` | PASS | Source/product-lane tests passed `14/14`. | Confirms the broader WinUI product-lane source guards still pass. |
| `cmd.exe /c npm run test:md-links` after WinUI copy update | PASS | Markdown link check passed. | Confirms the updated evidence note remains link-clean. |
| `cmd.exe /c npm run test:doc-commands` after WinUI copy update | PASS | Documented npm commands checked `1156`. | Confirms documented npm command references remain synchronized. |
| `py -3 tools\docsync_check.py` after WinUI copy update | PASS | Docsync policy check passed. | Confirms protected doc mirrors remain synchronized. |
| `cmd.exe /c npm run test:repo-hygiene` after WinUI copy update | PASS | Repo text hygiene check passed. | Confirms the new WinUI copy/evidence wording avoids stale/private wording guards. |

## Result

- `AssetModelTextureLinks` now exposes `CatalogMissingTextureFileNames` beside direct catalog matches.
- `AssetModelPreviewCoverage` now exposes:
  - `RowsWithAllTextureBindingFilesCatalogMatched`
  - `RowsWithAnyMissingCatalogTextureBindingFiles`
- `AssetModelPreviewCoverageRow` now carries the missing binding filenames for selected samples.
- The WinUI Asset Library catalog coverage summary now says how many model rows have all texture bindings in the texture catalog and how many are sidecar-needed texture rows.
- Follow-up evidence in `release/readiness/winui_model_texture_placeholder_filter_2026-05-08.md` corrects the resolver semantics: template/default FBX material placeholders are ignored, catalog export filenames and compact variants are matched, and the full-install AppCore host diagnostic now reports `352/352` model rows with all real texture refs catalog-mapped and `0` sidecar-needed rows.

## Boundary

These metrics prepare the WinUI lane for honest model-rendering and Goodies Browser work. They do not mean WinUI renders textured 3D models yet. They make the next renderer/UI work safer by showing whether a model can navigate through direct texture catalog rows or needs sidecar fallback handling.
