# WinUI Goodies Preview Coverage Evidence - 2026-05-07

## Scope

This pass added AppCore coverage for the WinUI Asset Library Goodies preview path. The goal is to prove what the native product can honestly preview today:

- texture-bearing Goodies can be matched to exported texture rows,
- model-bearing Goodies can be matched to exported model rows,
- model rows can report whether an FBX-derived wireframe is available,
- FMV/video Goodies are handled as Media handoff rows,
- shipped-but-not-source-grid-visible rows remain marked as such.

This is a product/readiness bridge over the existing RE evidence. It does not claim a final textured/animated in-app model viewer.

## Changes

- Added `GoodiePreviewCoverageService`.
- The service summarizes Goodies preview readiness by local preview route:
  - texture preview,
  - model export,
  - model wireframe,
  - media handoff,
  - no local preview.
- Focused AppCore tests now include a hidden Goodie `71` fixture row so the preview coverage keeps resource availability separate from known in-game wall visibility.

## Commands

```powershell
dotnet test .\OnslaughtCareerEditor.AppCore.Tests\OnslaughtCareerEditor.AppCore.Tests.csproj --nologo --filter "FullyQualifiedName~AssetCatalogServiceTests"
```

Result: PASS

Important output:

```text
Passed!  - Failed: 0, Passed: 19, Skipped: 0, Total: 19
```

## What This Proves

- The AppCore catalog layer can measure Goodie preview readiness without absolute paths in public reports.
- A model Goodie with a valid FBX export can be counted as model-export-ready and wireframe-ready.
- A texture Goodie with a valid PNG export can be counted as texture-preview-ready.
- A video Goodie can be counted as linked to the Media handoff route.
- Goodie `71` remains marked as not exposed by the known in-game wall mapping even when a local texture preview exists.

## What This Does Not Prove

- It does not prove final textured/animated in-app model viewing.
- It does not run the full private Goodies catalog through AppCore in this public evidence note.
- It does not launch BEA.exe or replay the runtime Goodies wall.
- It does not commit private catalog JSON, extracted assets, screenshots, frames, or proof outputs.

## Related Evidence

- `release/readiness/goodies_asset_matrix_2026-05-07.md` proves the shipped Goodies archive family counts.
- `release/readiness/goodies_catalog_linkage_2026-05-07.md` proves the full private catalog links `194/194` texture-bearing Goodies and `45/45` model-bearing Goodies to exported catalog rows.
- This note proves the native AppCore preview-readiness model over a focused fixture.
