# WinUI Safe-Copy Profile Catalog Status Readiness Note

Status: complete local UI/accounting slice
Date: 2026-06-24
Scope: `winui-safe-copy-profile-catalog-status`

## Summary

Windowed & Mods now shows a `Profile catalog and preset source` row beside the
selected safe-copy profile details. The row reports whether the tracked
safe-copy profile catalog or fallback built-in presets are active, includes the
profile schema, and shows a catalog SHA-256 prefix when a tracked catalog is
loaded.

The row is intentionally derived from sanitized AppCore metadata:

- `BinaryPatchPlanBuilder.SafeCopyProfileCatalogVersion`
- `BinaryPatchPlanBuilder.SafeCopyProfileCatalogSha256`
- `BinaryPatchPlanBuilder.UsingFallbackSafeCopyProfileCatalog`

It does not render `BinaryPatchPlanBuilder.SafeCopyProfileCatalogStatus`,
because that loader status may include local filesystem paths.

WinUI project output now also includes
`patches/catalog/safe-copy-profiles.v1.json` beside `patches.v2.json`, so
packaged app output can load the tracked profile catalog instead of relying on
fallback built-in presets.

## Boundary

This is product/accounting clarity only. It adds no BEA launch, CDB attach,
byte patch, Ghidra mutation, Host/Join enablement, online proof, music
audible-output proof, rebuild proof, public release, installed-game mutation, or
original executable mutation.

The installed Steam game folder and original `BEA.exe` remain read-only source
material.

## Validation

- `dotnet test OnslaughtCareerEditor.UiTests\OnslaughtCareerEditor.UiTests.csproj --nologo --filter FullyQualifiedName~WinUiProductLaneTests.PatchBench_VisibleCopyPromisesCopiedExecutableWorkflow`
- `dotnet test OnslaughtCareerEditor.UiTests\OnslaughtCareerEditor.UiTests.csproj --nologo --filter FullyQualifiedName~WinUiProductLaneTests.WinUiBuild_CopiesPatchCatalogIntoAppOutput`
