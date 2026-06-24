# WinUI Goodies Real Model Preview Smoke - 2026-05-07

## Scope

This pass tightened the native WinUI Asset Library row-breadth smoke so representative real Goodies model rows must prove the same in-app model preview path as direct model rows.

Private generated proof remains ignored under:

```text
subagents/winui-real-asset-row-breadth/2026-05-06/asset-library-row-breadth.json
```

## Command

```powershell
$env:ONSLAUGHT_WINUI_REAL_ASSET_CATALOG = "<private catalog.json>"
dotnet test .\OnslaughtCareerEditor.UiTests\OnslaughtCareerEditor.UiTests.csproj --nologo --filter "FullyQualifiedName~AssetLibrary_CyclesRepresentativeRealRowsWhenCatalogProvided"
```

Result: PASS

Important output:

```text
Passed!  - Failed: 0, Passed: 1, Skipped: 0, Total: 1
```

## Public-Safe Coverage Summary

The strengthened smoke still cycles representative real texture, loose model, embedded model, and Goodies rows from the full private generated catalog. For Goodies, the smoke now asserts:

- selected Goodie title is visible,
- selected summary says the row is matched to an extracted model export,
- in-app wireframe status is available,
- model metadata includes vertex and polygon-index-entry counts.

Representative Goodies rows:

- `BE:A Unit-01 'Pulsar'`
- `BE:A Unit-04S 'Sniper'`

## What This Proves

- The native WinUI Asset Library can load the full private generated asset catalog.
- The selected Goodies rows are real catalog rows, not sample UI fixtures.
- Representative real Goodies model rows activate the current in-app model preview plumbing.
- The current in-app model proof is a bounded wireframe/metadata preview backed by exported FBX geometry facts.

## What This Does Not Prove

- It does not prove final textured or animated native 3D rendering.
- It does not prove every model-bearing Goodie has been manually selected in WinUI.
- It does not prove runtime replay of the in-game Goodies wall.
- It does not commit private screenshots, raw catalog JSON, extracted assets, absolute paths, frames, or proof outputs.

## Follow-Up

The next model-viewing milestone is true native 3D rendering with materials and camera controls, or a runtime copied-profile Goodies wall replay that compares representative in-game slots against the static catalog.
