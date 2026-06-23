# WinUI Model Wireframe Preview

Status: public-safe WinUI product evidence
Date: 2026-05-06
Branch: `wip/sandbox`
Source head before pass: `b5a80465ead6df5f27380cab57cdc56bd4efb957`

## Purpose

This pass moves the WinUI Asset Library beyond metadata-only model inspection by adding a bounded, dependency-free in-app wireframe preview for readable binary FBX exports. It does not add a full native 3D renderer and does not claim material, texture, animation, skeleton, camera, or runtime fidelity.

## Implementation

- `FbxModelSummaryReader` now reads a bounded sample of uncompressed binary FBX `Vertices` and `PolygonVertexIndex` array properties.
- `AssetModelSummary` now carries an `AssetModelGeometryPreview` with preview vertices and edges when the data is readable.
- The WinUI Asset Library renders that preview with a small Canvas wireframe in the selected model panel.
- The visible UI says the wireframe is a lightweight geometry check, not final material or animation rendering.
- Texture preview, external open/copy actions, path details, and model metadata panels remain intact.

## Validation

Commands:

```powershell
dotnet test ".\OnslaughtCareerEditor.AppCore.Tests\OnslaughtCareerEditor.AppCore.Tests.csproj" --nologo --filter "FullyQualifiedName~FbxModelSummaryReaderTests|FullyQualifiedName~AssetCatalogServiceTests"
dotnet build ".\OnslaughtCareerEditor.WinUI\OnslaughtCareerEditor.WinUI.csproj" --nologo
dotnet test ".\OnslaughtCareerEditor.UiTests\OnslaughtCareerEditor.UiTests.csproj" --nologo --filter "FullyQualifiedName~WinUiProductLaneTests"
dotnet test ".\OnslaughtCareerEditor.UiTests\OnslaughtCareerEditor.UiTests.csproj" --nologo --filter "FullyQualifiedName~WinUiVisualSmokeTests.MainWindow_CapturesPrimaryProductScreens"
Get-Process -Name OnslaughtCareerEditor.WinUI -ErrorAction SilentlyContinue
```

Results:

- Focused AppCore FBX/catalog tests: PASS, 5/5.
- WinUI build: PASS, 0 warnings and 0 errors.
- WinUI product-lane static tests: PASS, 12/12.
- Explicit WinUI visual smoke: PASS, 1/1.
- Visual screenshot reviewed locally: `ignored local visual QA screenshot (06-asset-library-model.png)` shows a visible wireframe triangle in the selected model panel.
- No WinUI process remained after visual smoke.

## What This Proves

- The WinUI app can render a basic in-app model geometry preview from the same generated FBX export data used by the asset catalog fixture.
- The parser can derive preview edges from standard FBX polygon index encoding, including negative end-of-polygon markers.
- The primary Asset Library model screenshot now proves visible model preview pixels, not just metadata text.

## What This Does Not Prove

- Full native 3D rendering.
- Materials, textures, UVs, normals, animation, skeletons, camera controls, or lighting.
- Fidelity against every generated private FBX export.
- Public redistribution approval for extracted game assets.
- Packaged-output behavior for the model wireframe preview.

## Follow-Up

1. Test the wireframe preview against a broader private model set and record public-safe summary counts only.
2. Decide whether the long-term runtime preview target should stay as native WinUI Canvas/Win2D-style rendering or move through a clean GLB/glTF conversion pipeline.
3. Add material/texture/UV preview only after the asset format contract is deliberate.
