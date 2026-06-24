# WinUI Asset Library Preview Stability Evidence - 2026-05-07

## Scope

This pass tightened the WinUI Asset Library preview hierarchy and native UI automation smoke for real extracted asset catalogs.

The selected asset title, selected summary, and inline model facts now appear before the preview canvas and wireframe controls. This keeps the answer to "what am I looking at?" visible first for users and stable for automation on laptop-sized and maximized windows.

This pass does not add a new Goodies wall grid, does not launch the game, does not run runtime proof, and does not claim textured or animated model rendering.

## Changes

- Moved `AssetSelectedTitle`, `AssetSelectedSummary`, and `AssetModelMetadataInline` to the top of the Asset Library preview details stack.
- Kept the existing texture, model, embedded model, and Goodies browsing behavior intact.
- Hardened the WinUI visual smoke helper so search boxes are set directly instead of using a simulated typed-entry burst that can race native WinUI collection refreshes.
- Hardened automation ID lookup to retry through transient WinUI Automation COM exceptions.

## Validation

| Command | Result | What it proves |
| --- | --- | --- |
| `dotnet build .\OnslaughtCareerEditor.WinUI\OnslaughtCareerEditor.WinUI.csproj --nologo` | PASS | WinUI builds after the preview hierarchy change. |
| `$env:ONSLAUGHT_WINUI_REAL_ASSET_CATALOG = "<ignored-private-catalog>"; dotnet test .\OnslaughtCareerEditor.UiTests\OnslaughtCareerEditor.UiTests.csproj --nologo --filter "FullyQualifiedName~AssetLibrary_CyclesRepresentativeRealRowsWhenCatalogProvided"` | PASS, 1/1 | The native Asset Library still cycles representative real texture/model/embedded/Goodies rows from the generated PC-install catalog, including model wireframe metadata checks. |

## Real Data Boundary

The smoke uses an ignored private generated catalog from the user's PC install. It does not rely on Stuart's source tree as the asset source and does not commit private catalog JSON, textures, FBX files, screenshots, copied game files, or raw proof output.

## Not Claimed

- No original or installed `BEA.exe` was modified.
- No copied-profile runtime Goodies replay was run.
- No all-row visual proof was run for every extracted texture/model.
- In-app model preview remains a lightweight wireframe/metadata check, not a full textured or animated model viewer.

## Follow-Up

The attempted dense Goodies wall-grid experiment was not kept because the real-catalog native automation path was not stable enough. A future Goodies browser grid should be implemented behind a fresh red/green test with explicit virtualization and accessibility proof.
