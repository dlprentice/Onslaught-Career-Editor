# WinUI Asset Library Export-Folder QOL - 2026-06-25

Status: accepted focused slice

## Scope

This slice tightens Asset Library first-run wording for users who have a Battle
Engine Aquila install available but have not generated an asset catalog yet.

Changed paths:

- `OnslaughtCareerEditor.WinUI/Pages/AssetLibraryPage.xaml`
- `OnslaughtCareerEditor.WinUI/Pages/AssetLibraryPage.xaml.cs`
- `OnslaughtCareerEditor.AppCore/AssetCatalogLoadStatusText.cs`
- `OnslaughtCareerEditor.AppCore.Tests/AssetCatalogServiceTests.cs`
- `OnslaughtCareerEditor.UiTests/WinUiProductLaneTests.cs`
- `CURRENT_CAPABILITIES.md`

## Accepted Evidence

- The catalog browse button now says `Browse export folder`, matching the
  generated-catalog requirement.
- The first-run guide now explicitly says to use the game install as source for
  the external extractor, then load the separate generated export folder.
- If the selected catalog path is a full BEA install, the missing-catalog status
  says that path is the game install, not the generated export folder.
- The missing-catalog status text now lives in `AssetCatalogLoadStatusText`,
  keeping the install-vs-export-folder branch executable by AppCore tests.
- Static product-lane guards pin the new button copy, the install-vs-export
  status text, the `AppConfig.InspectGameDirectory(attemptedPath)` branch, and
  the UIA name `Browse generated export folder`.
- An executable AppCore regression creates a temp game-install-shaped folder
  with `BEA.exe` plus `data/`, verifies the status calls it the game install
  rather than the generated export folder, and verifies the status does not
  include the full temp path.

## Non-Claims

This slice does not add in-app extraction, catalog generation, game asset
bundling, raw game-file browsing, runtime proof, full 3D rendering, rebuild
parity, release packaging, or installed Steam folder / original `BEA.exe`
mutation.

## Consult Review

- Specialist review recommended a text-only first-run/catalog-picker QOL edit:
  rename the browse action, make game-install-vs-export-folder wording clearer,
  and keep `AssetCatalogService` behavior unchanged.
- Closeout review found the visible browse text and UIA name should both use
  export-folder wording; accepted and fixed.
- Adversarial review allowed only a narrow local generated-catalog browser
  improvement and blocked any edit that auto-generates catalogs, writes under
  the game install, bundles exported assets, publishes private paths, or
  upgrades claims beyond generated local catalog browsing.
- Adversarial closeout review noted the new status branch was initially only
  statically pinned; accepted and fixed by moving the decision into
  `AssetCatalogLoadStatusText` plus an executable AppCore temp-directory test.

## Validation

```powershell
dotnet test .\OnslaughtCareerEditor.AppCore.Tests\OnslaughtCareerEditor.AppCore.Tests.csproj --nologo --filter "FullyQualifiedName~BuildMissingCatalogStatus_CallsOutSelectedGameInstallWithoutLeakingPath"
dotnet test .\OnslaughtCareerEditor.UiTests\OnslaughtCareerEditor.UiTests.csproj --nologo --filter "FullyQualifiedName~WinUiProductLaneTests.AssetLibrary_IsNativeWinUiCatalogBrowser"
dotnet test .\OnslaughtCareerEditor.AppCore.Tests\OnslaughtCareerEditor.AppCore.Tests.csproj --nologo --filter "FullyQualifiedName~AssetCatalogServiceTests"
dotnet build .\OnslaughtCareerEditor.WinUI\OnslaughtCareerEditor.WinUI.csproj --nologo
dotnet test .\OnslaughtCareerEditor.UiTests\OnslaughtCareerEditor.UiTests.csproj --nologo --filter "FullyQualifiedName~WinUiRuntimeAccessibilitySmokeTests.MainWindow_ShellNavigationIsNamedEnabledAndInvokableThroughUiAutomation"
```

Results: all passed.
