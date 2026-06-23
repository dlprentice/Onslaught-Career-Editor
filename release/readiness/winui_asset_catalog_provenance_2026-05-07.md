# WinUI Asset Catalog Provenance - 2026-05-07

Status: public-safe WinUI product evidence

## Objective

Make the native Asset Library answer the recurring provenance question directly in the UI: loaded catalog rows are local generated outputs, previews come from exported PNG/FBX files, private assets stay local, and runtime Goodies behavior is a separate proof lane.

## Change

- Added a visible `Catalog provenance` line with UI Automation id `AssetCatalogProvenanceSummary`.
- Broad generated catalog loads now describe the source as a `broad PC-install export profile` when the loaded counts match a large retail-install-style catalog.
- Smaller catalogs are described as smaller generated catalogs instead of being overclaimed.
- The text explicitly says model display is metadata and wireframe geometry, not final textured 3D rendering.
- The text explicitly says private assets stay local and runtime Goodies behavior is separate proof.

## Validation

- `dotnet build OnslaughtCareerEditor.WinUI/OnslaughtCareerEditor.WinUI.csproj --nologo` - PASS, 0 warnings/errors.
- `dotnet test OnslaughtCareerEditor.UiTests/OnslaughtCareerEditor.UiTests.csproj --nologo --filter AssetLibrary_IsNativeWinUiCatalogBrowser` - PASS, 1/1.
- `dotnet test OnslaughtCareerEditor.UiTests/OnslaughtCareerEditor.UiTests.csproj --nologo --filter AssetLibrary_CyclesRepresentativeRealRowsWhenCatalogProvided` with private full-install catalog and maximized native capture enabled through a PowerShell `$env:` wrapper - PASS, 1/1.

## Tooling Note

An initial `cmd.exe` environment wrapper produced a skipped real-catalog smoke because the private catalog environment variable did not reach the test process reliably from the Node wrapper. The same test passed when the environment was set with PowerShell `$env:` assignments.

## Not Claimed

- This does not extract new assets.
- This does not change catalog generation behavior.
- This does not launch or patch `BEA.exe`.
- This does not prove final textured/animated native 3D rendering.
- This does not prove runtime Goodies unlock or wall behavior.
- This does not make private extracted assets, screenshots, manifests, or local paths public.
