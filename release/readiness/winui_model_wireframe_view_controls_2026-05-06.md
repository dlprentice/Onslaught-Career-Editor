# WinUI Model Wireframe View Controls - 2026-05-06

Status: public-safe evidence

## Scope

This note records a focused Asset Library model-preview improvement in the WinUI product lane. It does not claim full native 3D rendering, materials, textures, skeletal animation, or GLB/glTF export.

## What Changed

- Enlarged the lightweight in-app model wireframe canvas.
- Added model view controls for `Front`, `Side`, `Top`, and `Iso` projections.
- Kept the implementation on the existing parsed FBX geometry-preview data; no speculative 3D dependency was added in this slice.
- Updated the WinUI product-lane guard so the model-view controls and projection code remain present.
- Refreshed the ignored Asset Library model screenshot.

## Private Visual Evidence

Ignored screenshot:

- `ignored local visual QA screenshot (06-asset-library-model.png)`

The screenshot shows the selected model row, the larger wireframe panel, and the model view controls. No raw private asset exports or private absolute paths are included here.

## Commands

| Command | Result | Important output |
| --- | --- | --- |
| `dotnet test .\OnslaughtCareerEditor.UiTests\OnslaughtCareerEditor.UiTests.csproj --nologo --filter "FullyQualifiedName~WinUiProductLaneTests.AssetLibrary_IsNativeWinUiCatalogBrowser"` | FAIL then PASS | The guard failed before model-view controls existed; after the XAML/code update it passed 1/1. |
| `dotnet build .\OnslaughtCareerEditor.WinUI\OnslaughtCareerEditor.WinUI.csproj --nologo` | PASS | Build succeeded with 0 warnings and 0 errors. |
| `dotnet test .\OnslaughtCareerEditor.UiTests\OnslaughtCareerEditor.UiTests.csproj --nologo --filter "FullyQualifiedName~WinUiVisualSmokeTests.MainWindow_CapturesPrimaryProductScreens"` | PASS | 1/1 explicit native visual smoke passed and refreshed the Asset Library model screenshot. |
| Local screenshot inspection with `view_image` | PASS | The Asset Library model screenshot shows the enlarged wireframe and `Front` / `Side` / `Top` / `Iso` view controls. |
| `dotnet test .\OnslaughtCareerEditor.UiTests\OnslaughtCareerEditor.UiTests.csproj --nologo --filter "FullyQualifiedName!~LegacyWpf"` | PASS | 36/36 active UiTests passed. |
| `py -3 tools\release_profile_snapshot.py` | PASS | Regenerated release profile artifacts; counts `R0=1184 R2=0 R3=2 R4=18186`. |
| `py -3 tools\release_curated_manifest.py` | PASS | Regenerated curated manifest and public allowlist; selected files: 1171. |
| `py -3 tools\release_profile_snapshot.py --check` | PASS | Release profile snapshot check passed; counts `R0=1184 R2=0 R3=2 R4=18186`. |
| `py -3 tools\release_curated_manifest.py --check` | PASS | Curated allowlist check passed; selected files: 1171. |
| `py -3 tools\docsync_check.py` | PASS | Dsync policy check passed. |
| `npm run test:doc-commands` | PASS | 396 documented npm commands checked. |
| `npm run test:md-links` | PASS | Markdown link check passed. |
| `npm run test:public-allowlist` | PASS | 1171 public allowlist rows checked. |
| `npm run test:repo-hygiene` | PASS | 24 hygiene unit tests passed; live scan checked 19 text and 2 path rules. |

## Proven

- Asset Library model preview now exposes selectable 2D projections over the existing geometry-preview data.
- The visual smoke still captures a visible model preview in the native WinUI app.
- The active WinUI static/product-lane test suite remains green after the model-preview change.

## Not Proven

- This is not full 3D rendering.
- This does not prove materials, texture binding, lighting, animation, skeletons, or camera controls.
- This does not prove packaged installer/MSIX behavior.
- This does not replace future model-rendering pipeline selection if a full viewer is required.
