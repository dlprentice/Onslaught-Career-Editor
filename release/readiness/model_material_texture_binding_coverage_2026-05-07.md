# Model Material and Texture-Binding Coverage - 2026-05-07

## Scope

This pass extended the AppCore model preview coverage report so the project can distinguish four levels of model readiness:

1. FBX export exists.
2. FBX geometry metadata and wireframe preview are readable.
3. FBX material and texture-binding nodes are present.
4. FBX texture filename references can be matched back to generated catalog texture rows.

This is still static/export evidence. It does not claim final textured native rendering.

Raw generated JSON remains ignored/private under:

```text
subagents/model-preview-material-coverage/current/asset-model-preview-coverage.json
subagents/model-texture-binding-resolution/current/asset-model-preview-coverage.json
```

## Commands

```powershell
dotnet build OnslaughtCareerEditor.AppCore.Host/OnslaughtCareerEditor.AppCore.Host.csproj --nologo
dotnet test OnslaughtCareerEditor.AppCore.Tests/OnslaughtCareerEditor.AppCore.Tests.csproj --nologo --filter "FullyQualifiedName~AssetCatalogServiceTests"
dotnet run --project OnslaughtCareerEditor.AppCore.Host/OnslaughtCareerEditor.AppCore.Host.csproj -- inspect-asset-model-preview <private catalog.json> --sample-limit 16
```

Results:

- AppCore.Host build: PASS, 0 warnings, 0 errors.
- Focused AppCore AssetCatalog tests: PASS, 49 passed, 0 failed, 0 skipped.
- Private full-catalog model preview coverage: PASS.

## Public-Safe Summary

Catalog summary:

| Catalog family | Count |
| --- | ---: |
| Total catalog entries | 4,050 |
| Texture rows | 828 |
| Loose mesh rows | 213 |
| Embedded mesh rows | 139 |

Model preview and material/texture-binding coverage:

| Coverage check | Count |
| --- | ---: |
| Total model rows | 352 |
| Loose mesh rows | 213 |
| Embedded mesh rows | 139 |
| Existing FBX exports | 352 |
| Missing FBX exports | 0 |
| Metadata-readable exports | 352 |
| Wireframe-ready exports | 352 |
| Rows with FBX material nodes | 352 |
| Rows with FBX texture-binding nodes | 352 |
| Rows with catalog-matched FBX texture binding files | 352 |
| Rows without catalog-matched FBX texture binding files | 0 |
| Catalog-matched FBX texture binding files | 1,268 |
| Total material nodes | 8,448 |
| Total texture-binding nodes | 8,448 |
| Metadata-readable but no wireframe | 0 |
| Unreadable exports | 0 |

## What This Proves

- The generated private full-install catalog has FBX exports for every loose and embedded model row currently in scope.
- Every exported model row has readable FBX metadata and wireframe geometry.
- Every exported model row has at least one material node and at least one texture-binding node in the exported FBX.
- The FBX reader can now extract sanitized material names and texture file names without exposing private paths.
- 352 of 352 model rows have at least one FBX texture filename that resolves back to a generated catalog texture row.
- The compact texture-name normalizer resolves spacing/case variants such as FBX `DeadTree01_Bark.png` to catalog `dead tree 01_bark` entries.
- The private report now includes unmatched samples; after compact normalization the unmatched sample list is empty for the current full-install catalog.
- The WinUI model viewer's current limitation is renderer capability, not missing exported FBX geometry/material metadata in the catalog.

## What This Does Not Prove

- It does not prove a final textured or animated native WinUI model renderer.
- It does not prove UV/material fidelity against the original runtime renderer.
- It does not prove every FBX texture filename is a game texture; exporter `default*.png` placeholders still appear beside real matched texture names.
- It does not prove skeleton, animation, lighting, or in-game camera behavior.
- It does not commit extracted models, textures, private paths, screenshots, frames, or raw proof JSON.
