# WinUI Asset Library First-Run Catalog Guidance - 2026-06-25

Status: local source/package-candidate follow-up; not a new GitHub Release.

## Scope

This slice tightens the Asset Library first-run path so a public ZIP user does
not mistake a detected Battle Engine Aquila install for a browsable asset
catalog.

## Changes

- `AssetCatalogService.FindCatalogCandidates(...)` resolves `catalog.json`,
  catalog directories, and `asset_catalog/catalog.json` candidates with stable
  de-duplication.
- A regression test now confirms a plain game-install-shaped folder without
  `asset_catalog/catalog.json` is not treated as an Asset Library catalog.
- Asset Library startup uses persisted/test catalog candidates, but does not use
  the detected Steam install as a catalog candidate.
- Asset Library first-run copy now says to generate a catalog from the user's
  own game install outside the app, then choose the generated export folder
  containing `asset_catalog/catalog.json`, not the game install folder itself.
- The first-run guide is exposed through a stable `AssetCatalogFirstRunGuide`
  UI Automation element so native UIA tests and assistive tools can read the
  guidance.
- The game-assets index now opens with a plain current entrypoint that points
  to `reverse-engineering/game-assets/extraction-pipeline.md` and the local
  overlay rules before older evidence notes.

## Non-Claims

- No in-app asset exporter was added.
- No raw game files, copied executables, extracted assets, or generated catalogs
  are bundled in the app ZIP.
- No installed Steam folder or original `BEA.exe` mutation is involved.
- No full native 3D rendering, runtime gameplay proof, or rebuild parity claim
  is added.

## Validation

Accepted local validation:

- `dotnet test .\OnslaughtCareerEditor.AppCore.Tests\OnslaughtCareerEditor.AppCore.Tests.csproj --nologo --filter "FullyQualifiedName~AssetCatalogServiceTests"` passed `94/94`.
- `dotnet test .\OnslaughtCareerEditor.UiTests\OnslaughtCareerEditor.UiTests.csproj --nologo --filter "FullyQualifiedName~WinUiProductLaneTests.AssetLibrary_IsNativeWinUiCatalogBrowser|FullyQualifiedName~WinUiAccessibilityAuditTests.PrimaryShellAndLongWorkflowControls"` passed `2/2`.
- `dotnet build .\OnslaughtCareerEditor.WinUI\OnslaughtCareerEditor.WinUI.csproj --nologo` passed with `0` warnings and `0` errors.
- `dotnet test .\OnslaughtCareerEditor.UiTests\OnslaughtCareerEditor.UiTests.csproj --nologo --filter "FullyQualifiedName~WinUiRuntimeAccessibilitySmokeTests.MainWindow_ShellNavigationIsNamedEnabledAndInvokableThroughUiAutomation"` passed `1/1`.

Final closeout validation:

- `npm run test:md-links` passed: `3623` Markdown files and `6125` local links.
- `npm run test:hard-payload-safety` passed: `19312` public candidate files.
- `npm run test:public-allowlist` passed: hard payload safety, submodule payload
  safety over `19496` candidate files, and public-primary migration inventory.
- `npm run test:repo-hygiene` passed: text hygiene plus `18465` explicit text
  files in the line-ending check.
