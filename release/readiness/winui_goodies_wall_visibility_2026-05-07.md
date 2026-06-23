# WinUI Goodies Wall Visibility Evidence - 2026-05-07

## Scope

This pass made the WinUI/AppCore Goodies catalog more honest about the difference between shipped Goodie resource archives and the known in-game Goodies wall mapping.

The concrete issue found during the asset-matrix pass:

- Goodie archives `71-73` exist in the shipped PC resource folder and are now statically classified as resolved texture-only entries.
- Stuart's `get_goodie_number(x, y)` source mapping exposes Goodies `0-70`, `74-77`, `78-200`, and `201-232`.
- Therefore Goodies `71-73` should not look like ordinary visible wall entries until a runtime/non-grid path is proven.

## Changes

- Added `GoodieWallVisibilityService`.
- `AssetCatalogService` now enriches each `AssetGoodieItem` with wall-visibility summary/evidence and a source-grid-visible flag.
- WinUI Asset Library only adds a wall-visibility warning to the Goodie summary when the slot is not known to be visible in the in-game wall mapping.
- Focused AppCore tests cover Goodies `70`, `71`, `73`, `74`, `78`, `232`, and reserved slot `233`.

## Commands

```powershell
dotnet test .\OnslaughtCareerEditor.AppCore.Tests\OnslaughtCareerEditor.AppCore.Tests.csproj --nologo --filter "FullyQualifiedName~AssetCatalogServiceTests"
```

Result: PASS

Important output:

```text
Passed!  - Failed: 0, Passed: 18, Skipped: 0, Total: 18
```

```powershell
dotnet build .\OnslaughtCareerEditor.WinUI\OnslaughtCareerEditor.WinUI.csproj --nologo
```

Result: PASS

Important output:

```text
Build succeeded.
0 Warning(s)
0 Error(s)
```

```powershell
dotnet test .\OnslaughtCareerEditor.UiTests\OnslaughtCareerEditor.UiTests.csproj --nologo --filter "FullyQualifiedName~WinUiProductLaneTests|FullyQualifiedName~WinUiAccessibilityAuditTests"
```

Result: PASS

Important output:

```text
Passed!  - Failed: 0, Passed: 21, Skipped: 0, Total: 21
```

## What This Proves

- WinUI/AppCore no longer treats shipped-but-not-source-grid-visible Goodies `71-73` as ordinary in-game wall entries.
- Goodie `78` remains correctly classified as concept art.
- Goodie `232` remains correctly classified as a visible FMV slot 33 with no matching `goodie_232_res_PC.aya` archive expected.
- The native WinUI build and focused product/accessibility tests still pass.

## What This Does Not Prove

- It does not prove runtime replay of the in-game Goodies wall.
- It does not prove final textured/animated model rendering.
- It does not extract, commit, or redistribute private game assets.
