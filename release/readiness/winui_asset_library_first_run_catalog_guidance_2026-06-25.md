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
- Asset Library startup uses persisted/test catalog candidates, but does not use
  the detected Steam install as a catalog candidate.
- Asset Library empty-state copy now says the release loads an existing
  generated catalog only, does not include game assets, and does not generate a
  catalog in place.
- The browse button is labeled as a folder picker and the placeholder says users
  can paste a `catalog.json` path or browse to a generated export folder.

## Non-Claims

- No in-app asset exporter was added.
- No raw game files, copied executables, extracted assets, or generated catalogs
  are bundled in the app ZIP.
- No installed Steam folder or original `BEA.exe` mutation is involved.
- No full native 3D rendering, runtime gameplay proof, or rebuild parity claim
  is added.

## Validation

Accepted local validation:

- `dotnet test .\OnslaughtCareerEditor.AppCore.Tests\OnslaughtCareerEditor.AppCore.Tests.csproj --nologo --filter "FullyQualifiedName~LoreBrowserServiceTests|FullyQualifiedName~AssetCatalogServiceTests"` passed `101/101` in read-only consult review.
- `dotnet test .\OnslaughtCareerEditor.UiTests\OnslaughtCareerEditor.UiTests.csproj --nologo --filter "FullyQualifiedName~WinUiProductLaneTests.AssetLibrary_IsNativeWinUiCatalogBrowser"` passed `1/1` in read-only consult review.
- `npm run test:winui-zip-package-probe` passed with the Asset Library copy in the extracted app smoke context.
- `npm run test:winui-zip-release-candidate-probe` passed with the Asset Library copy in the versioned release-candidate context.

Broader docs/release/public/hygiene gates remain part of final active-slice
closeout before commit, push, or release.
