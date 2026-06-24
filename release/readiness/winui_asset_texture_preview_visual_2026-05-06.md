# WinUI Asset Texture Preview Visual Smoke - 2026-05-06

Status: public-safe evidence

## Scope

This note records a focused WinUI Asset Library visual-smoke improvement for texture previews. It does not embed screenshots, extracted textures, private catalog files, local absolute paths, or private game assets.

## What Changed

- Asset Library now keeps the loaded-catalog banner compact so selected asset previews are visible in the first viewport.
- Texture preview now renders above secondary actions instead of below the action/background controls.
- Texture preview has Neutral, Light, and Dark background controls for dark or transparent game textures.
- A new explicit real-catalog visual smoke can run when `ONSLAUGHT_WINUI_REAL_ASSET_CATALOG` points at an ignored generated catalog.

## Private Visual Evidence

Ignored screenshots remain under `subagents/` and are not committed:

- Standard synthetic visual smoke: `ignored local visual QA screenshot (05-asset-library-texture.png)`
- Real generated catalog smoke: `subagents/winui-real-asset-visual-qa/2026-05-06/asset-library-real-texture.png`

The real generated-catalog smoke selected the `f_trooperd` texture row. The screenshot shows an extracted texture atlas visible in the first viewport on the neutral preview canvas. The private generated catalog path and private exported PNG path are intentionally not repeated here.

## Commands

| Command | Result | Important output |
| --- | --- | --- |
| `dotnet build .\OnslaughtCareerEditor.WinUI\OnslaughtCareerEditor.WinUI.csproj --nologo` | PASS | Build succeeded with 0 warnings and 0 errors. |
| `dotnet test .\OnslaughtCareerEditor.UiTests\OnslaughtCareerEditor.UiTests.csproj --nologo --filter "FullyQualifiedName~WinUiProductLaneTests.AssetLibrary_IsNativeWinUiCatalogBrowser"` | PASS | 1/1 focused product-lane test passed. |
| `dotnet test .\OnslaughtCareerEditor.UiTests\OnslaughtCareerEditor.UiTests.csproj --nologo --filter "FullyQualifiedName~WinUiVisualSmokeTests.AssetLibrary_CapturesRealTexturePreviewWhenCatalogProvided"` | PASS | 1/1 explicit real-catalog visual smoke passed with the private catalog supplied through an environment variable. |
| `dotnet test .\OnslaughtCareerEditor.UiTests\OnslaughtCareerEditor.UiTests.csproj --nologo --filter "FullyQualifiedName~WinUiVisualSmokeTests.MainWindow_CapturesPrimaryProductScreens"` | PASS | 1/1 standard visual smoke passed; the Asset Library texture screenshot shows the preview image in the first viewport. |

## Proven

- The WinUI Asset Library texture preview is not limited to a synthetic fixture.
- A real generated texture row can be searched, selected, and captured through native desktop UI automation.
- The selected texture image is visible in the first viewport after the layout compaction.
- Private generated assets and screenshots remain local/ignored.

## Not Proven

- This does not prove every texture row is visually interesting or bright.
- This does not prove public redistribution rights for extracted textures.
- This does not prove final packaged installer/MSIX behavior.
- This does not add full material/model rendering.
