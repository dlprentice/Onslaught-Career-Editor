# WinUI Asset Library Integration - 2026-05-06

Status: public-safe WinUI product evidence

## Scope

This note records the first native WinUI Asset Library integration. The app can now load a generated local asset catalog and browse texture, loose-mesh, and embedded-mesh rows without bundling private extracted assets.

This report is public-safe. It does not include private absolute Windows paths, raw game asset paths, extracted PNG/FBX files, raw media files, screenshots, copied executables, save contents, hashes of private payloads, data URLs, base64, or proof JSON.

## Changes

| File | Change | Why |
| --- | --- | --- |
| `OnslaughtCareerEditor.AppCore/AssetCatalogService.cs` | Added generated `catalog.json` parsing for summary counts, textures, loose meshes, embedded meshes, local export-path resolution, and safe empty-state behavior. | Moves asset catalog interpretation into the shared C# core instead of leaving the WinUI page to parse private backend output directly. |
| `OnslaughtCareerEditor.WinUI/Pages/AssetLibraryPage.xaml(.cs)` | Added a native Asset Library page with catalog load/change controls, collapsed path details, catalog summary, filter tabs, searchable rows, texture preview, and mesh export-status detail. | Gives the primary WinUI app a user-facing bridge from the proven asset backend to a browsable product surface. |
| `OnslaughtCareerEditor.WinUI/MainWindow.xaml(.cs)` and `HomePage.xaml` | Added Asset Library navigation and Home routing. | Makes the asset surface discoverable from the product shell. |
| `OnslaughtCareerEditor.AppCore/AppConfig.cs` | Added persisted `assetCatalogPath`. | Lets users reopen a previously selected generated catalog. |
| `OnslaughtCareerEditor.UiTests/*` | Added AppCore catalog parser tests, product-lane static checks, launch-smoke shell coverage, and visual-smoke Asset Library capture with a synthetic catalog fixture. | Keeps the new surface testable without private assets. |

## Command Evidence

| Command | Result | Important output summary | What it proves |
| --- | --- | --- | --- |
| `dotnet test .\OnslaughtCareerEditor.AppCore.Tests\OnslaughtCareerEditor.AppCore.Tests.csproj --nologo --filter "FullyQualifiedName~AssetCatalogServiceTests"` before implementation | FAIL as expected | The test failed because `AssetCatalogService`, `AssetCatalogSnapshot`, and item record types did not exist. | Confirms the AppCore catalog parser tests were red before production implementation. |
| `dotnet test .\OnslaughtCareerEditor.AppCore.Tests\OnslaughtCareerEditor.AppCore.Tests.csproj --nologo --filter "FullyQualifiedName~AssetCatalogServiceTests"` after implementation | PASS | 3/3 focused AssetCatalogService tests passed. | Confirms generated catalog parsing, directory/file resolution, export-path resolution, and missing-catalog behavior. |
| `dotnet build .\OnslaughtCareerEditor.WinUI\OnslaughtCareerEditor.WinUI.csproj --nologo` | PASS | Build succeeded with 0 warnings and 0 errors. | Confirms the native Asset Library page compiles in the primary WinUI app. |
| `dotnet test .\OnslaughtCareerEditor.AppCore.Tests\OnslaughtCareerEditor.AppCore.Tests.csproj --nologo` | PASS | 23/23 AppCore tests passed. | Confirms the new parser did not regress existing core behavior. |
| `dotnet test .\OnslaughtCareerEditor.UiTests\OnslaughtCareerEditor.UiTests.csproj --nologo --filter "FullyQualifiedName~WinUiProductLaneTests"` | PASS | 10/10 focused product-lane tests passed. | Confirms Home/shell routing, Asset Library source files, and primary path-hiding guardrails are present. |
| `dotnet test .\OnslaughtCareerEditor.UiTests\OnslaughtCareerEditor.UiTests.csproj --nologo --filter "FullyQualifiedName~WinUiLaunchSmokeTests.MainWindow_LaunchesAndShowsWinUiProductChrome"` | PASS | 1/1 explicit launch smoke passed. | Confirms the desktop shell launches and includes Asset Library navigation. |
| `dotnet test .\OnslaughtCareerEditor.UiTests\OnslaughtCareerEditor.UiTests.csproj --nologo --filter "FullyQualifiedName~WinUiVisualSmokeTests.MainWindow_CapturesPrimaryProductScreens"` | PASS | 1/1 explicit visual smoke passed; screenshots remain under ignored `subagents/`. | Confirms primary WinUI screens render, including Asset Library with a synthetic loaded catalog fixture. |

## Release Validation

| Command | Result | Important output summary |
| --- | --- | --- |
| `dotnet test .\OnslaughtCareerEditor.UiTests\OnslaughtCareerEditor.UiTests.csproj --nologo --filter "FullyQualifiedName!~LegacyWpf"` | PASS | 31/31 active UiTests passed. |
| `py -3 tools\release_profile_snapshot.py --check` | PASS after regeneration | Profile counts `R0=1150 R2=0 R3=2 R4=18186`. |
| `py -3 tools\release_curated_manifest.py --check` | PASS | Curated allowlist selected 1,142 files and passed. |
| `py -3 tools\docsync_check.py` | PASS | Protected docs mirrors are synchronized. |
| `npm run test:public-allowlist` | PASS | Public allowlist safety check passed for 1,142 rows. |
| `npm run test:repo-hygiene` | PASS | 24 hygiene tests passed and live scan passed. |
| `npm run test:md-links` | PASS | Markdown link check passed. |
| `npm run test:doc-commands` | PASS | 241 documented npm commands checked. |
| `node -e "<parse state/manifest JSON>"` | PASS | State files and curated manifest parse successfully. |
| `git diff --check` | PASS | No whitespace errors; generated line-ending warnings only. |

## Screenshot Review

Ignored private/local screenshot reviewed:

- `ignored local visual QA screenshot (05-asset-library.png)`: PASS/YELLOW. The screen now shows a loaded catalog summary, visible texture row, collapsed path details, and no private absolute path in primary text. Remaining polish: the load card is still visually tall, and selecting a texture before capture would better exercise the preview pane.

## What Is Proven

- WinUI can load a generated asset catalog from a local file or folder.
- AppCore can parse the current generated catalog shape for textures, loose meshes, embedded meshes, and summary counts.
- The native app exposes Asset Library navigation from the shell and Home page.
- Texture export rows can point to local generated PNG outputs and show a preview when the export exists.
- Mesh rows show local FBX export status honestly while stating that native 3D viewing is future work.
- Full local paths are collapsed under details instead of shown as primary loaded-state text.

## What Is Not Proven

- Native 3D model preview for FBX exports.
- Shipping or redistributing extracted private game assets.
- Running asset extraction from inside WinUI.
- Broad visual polish for very large catalogs.
- Signed/installer-grade release behavior.

## Privacy And Release Boundary

The Asset Library is a bring-your-own-local-catalog surface. Generated extraction outputs, local catalogs, screenshots, and private game-derived files remain ignored and release-excluded. Public releases must continue to exclude `subagents/**`, private game/media/save folders, raw extracted PNG/FBX/media payloads, and private runtime evidence unless a later review explicitly sanitizes and reclassifies a narrow public-safe fixture.
