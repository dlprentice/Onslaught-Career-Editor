# WinUI Real Asset Visual Smoke - 2026-05-06

Status: public-safe evidence

Source branch: `wip/sandbox`

Source commit before this wave: `be905bbb99c2`

Evidence-report commit: `a818ef738b5db56f094b3b9e7970c6292362de7d`

Recorded at: 2026-05-06T13:22:08-04:00

## Scope

This smoke proves the WinUI Asset Library can open a private generated asset catalog and render selected real exported asset rows in the native desktop app.

The catalog, screenshots, extracted textures, and exported FBX files remain private ignored evidence under `subagents/`. This report intentionally does not include private absolute paths, raw screenshots, exported asset paths, binary payloads, or image data.

## Source Material

- Read-only source material: local Battle Engine Aquila install.
- Generated private catalog family: full-corpus asset export under ignored local evidence storage.
- Catalog summary used by the smoke:
  - textures: 828
  - loose meshes: 213
  - embedded meshes: 139

## Commands Run

### Build WinUI

Command:

```powershell
dotnet build .\OnslaughtCareerEditor.WinUI\OnslaughtCareerEditor.WinUI.csproj --nologo
```

Result: PASS

Important output:

- `OnslaughtCareerEditor.WinUI` built successfully.
- 0 warnings, 0 errors.

What it proves:

- The updated Asset Library XAML/code-behind compiles into the native WinUI app.

### Real Texture Visual Smoke

Command shape:

```powershell
$env:ONSLAUGHT_WINUI_REAL_ASSET_CATALOG = "<private generated catalog.json>"
$env:ONSLAUGHT_WINUI_REAL_ASSET_TEXTURE_SEARCH = "f_trooperd"
$env:ONSLAUGHT_WINUI_REAL_ASSET_TEXTURE_EXPECTED = "F Trooperd"
dotnet test .\OnslaughtCareerEditor.UiTests\OnslaughtCareerEditor.UiTests.csproj --nologo --filter "FullyQualifiedName~WinUiVisualSmokeTests.AssetLibrary_CapturesRealTexturePreviewWhenCatalogProvided"
```

Result: PASS

Important output:

- 1/1 focused UI test passed.
- The test launched the native WinUI app, loaded the private generated asset catalog, filtered to a real texture row, and captured an ignored screenshot.

What it proves:

- A selected real exported texture can be previewed in the WinUI Asset Library.
- The primary UI shows filename/catalog context rather than private absolute paths.

### Real Model Wireframe Visual Smoke

Initial RED result:

- The first test version reached the real model screen, but the wireframe proof state was only canvas-visual and not exposed through an easy UI Automation assertion.

Fix:

- Added visible `AssetModelWireframeStatus` text above the wireframe panel.
- The text makes the model preview state obvious in the native UI and gives UI Automation a stable, first-viewport proof target.

Command shape:

```powershell
$env:ONSLAUGHT_WINUI_REAL_ASSET_CATALOG = "<private generated catalog.json>"
$env:ONSLAUGHT_WINUI_REAL_ASSET_MODEL_SEARCH = "arachnid"
dotnet test .\OnslaughtCareerEditor.UiTests\OnslaughtCareerEditor.UiTests.csproj --nologo --filter "FullyQualifiedName~WinUiVisualSmokeTests.AssetLibrary_CapturesRealModelWireframeWhenCatalogProvided"
```

Result: PASS after rebuilding the WinUI app

Important output:

- 1/1 focused UI test passed.
- The test launched the native WinUI app, loaded the private generated asset catalog, filtered to a real model row, captured an ignored screenshot, and asserted:
  - `AssetModelWireframeStatus` says wireframe preview is available.
  - `AssetModelMetadataInline` includes vertex and polygon-index wording.

What it proves:

- A selected real exported FBX model can render the current bounded in-app wireframe preview.
- The preview state is visible to users and automation.
- The proof uses generated local exports, not bundled private assets.

### Combined Real Asset Visual Smoke

Command shape:

```powershell
$env:ONSLAUGHT_WINUI_REAL_ASSET_CATALOG = "<private generated catalog.json>"
$env:ONSLAUGHT_WINUI_REAL_ASSET_TEXTURE_SEARCH = "f_trooperd"
$env:ONSLAUGHT_WINUI_REAL_ASSET_TEXTURE_EXPECTED = "F Trooperd"
$env:ONSLAUGHT_WINUI_REAL_ASSET_MODEL_SEARCH = "arachnid"
dotnet test .\OnslaughtCareerEditor.UiTests\OnslaughtCareerEditor.UiTests.csproj --nologo --filter "FullyQualifiedName~WinUiVisualSmokeTests.AssetLibrary_CapturesReal"
```

Result: PASS

Important output:

- 2/2 focused UI tests passed.
- The smoke captured ignored private screenshots for the real texture and real model cases.

## Private Screenshot Evidence

Ignored screenshot filenames:

- `asset-library-real-texture.png`
- `asset-library-real-model.png`

Visual review summary:

- Texture preview: PASS. The selected real texture renders in the right preview panel on a neutral canvas.
- Model preview: PASS. The selected real model renders a visible amber wireframe with a first-viewport status line saying the wireframe preview is available.

## What Is Proven

- WinUI Asset Library can load a generated full-corpus local asset catalog.
- A real exported texture row can be selected and previewed in-app.
- A real exported FBX model row can be selected and previewed as the current bounded wireframe.
- The wireframe preview state is accessible through visible text and UI Automation.
- Private paths/assets/screenshots remain outside committed public evidence.

## What Is Not Proven

- This is not full 3D rendering with materials, animation, lighting, or camera controls.
- This is not proof that every texture or every model row renders correctly.
- This is not public redistribution approval for extracted game assets.
- This is not packaged installer/runtime proof.
- This does not mutate the installed game, copied profiles, saves, or executables.

## Release Posture

GREEN for focused WinUI Asset Library real-catalog visual smoke.

The remaining asset-product gap is full native 3D/material/animation rendering and broader row-by-row playback/rendering coverage, not basic generated-catalog loading, real texture preview, or bounded real model wireframe preview.
