# WinUI Goodies Wall Placement Evidence - 2026-05-07

## Scope

This pass made the WinUI Asset Library Goodies tab more like a Goodies browser by carrying the compiled wall position into AppCore and visible row/selection copy.

It does not create a new runtime replay, does not launch the game, and does not claim a final textured/animated model viewer.

## Changes

- `GoodieWallGridMappingService` now resolves visible Goodie indices back to wall placement labels:
  - group label, such as `Character bios`, `Unit viewer`, `Race levels`, `Developer items`, `Cutscenes`, or `Concept art`,
  - position label, such as `row 3, slot 32`.
- Hidden shipped archives such as Goodies `71..73` still return no wall position.
- `AssetGoodieItem` now carries the wall group and position labels.
- The WinUI Goodies tab row copy and selected-summary copy now show wall placement for visible rows.

## Validation

| Command | Result | What it proves |
| --- | --- | --- |
| `dotnet test .\OnslaughtCareerEditor.AppCore.Tests\OnslaughtCareerEditor.AppCore.Tests.csproj --nologo --filter "FullyQualifiedName~GoodieWallGridMappingService"` | PASS, 30/30 | Compiled Goodies wall coordinate mapping and reverse placement labels are guarded. |
| `dotnet test .\OnslaughtCareerEditor.AppCore.Tests\OnslaughtCareerEditor.AppCore.Tests.csproj --nologo --filter "FullyQualifiedName~AssetCatalogServiceTests"` | PASS, 49/49 | Asset catalog Goodie rows carry wall group/position labels and preserve hidden-slot behavior. |
| `dotnet test .\OnslaughtCareerEditor.UiTests\OnslaughtCareerEditor.UiTests.csproj --nologo --filter "FullyQualifiedName~AssetLibrary_IsNativeWinUiCatalogBrowser"` | PASS, 1/1 | WinUI Asset Library source keeps the Goodies wall labels in the product surface. |
| `dotnet build .\OnslaughtCareerEditor.WinUI\OnslaughtCareerEditor.WinUI.csproj --nologo` | PASS | WinUI builds after the Goodies browser placement changes. |
| `$env:ONSLAUGHT_WINUI_REAL_ASSET_CATALOG = "<ignored-private-catalog>"; dotnet test .\OnslaughtCareerEditor.UiTests\OnslaughtCareerEditor.UiTests.csproj --nologo --filter "FullyQualifiedName~AssetLibrary_CyclesRepresentativeRealRowsWhenCatalogProvided"` | PASS, 1/1 | The native Asset Library still cycles representative real texture/model/Goodies rows from the generated PC-install catalog after the wall-placement change. |

## Not Claimed

- No BEA runtime proof was run.
- No original or installed `BEA.exe` was read/written by this pass.
- No private catalog, save, screenshot, frame, FBX, texture, or Ghidra decompile output is committed.
- Full in-app textured/animated model viewing remains future work.

## Follow-Up

The next product step can turn these labels into a denser wall/grid visual. The next RE step should use a copied profile and windowed patch if runtime Goodies wall replay is required.
