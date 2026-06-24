# WinUI Asset Library Real Catalog Breadth Evidence - 2026-05-07

## Scope

This pass ran the existing explicit native WinUI Asset Library breadth smoke against the full private generated asset catalog. The test launches the native WinUI app, loads the private catalog through the normal app configuration path, and cycles representative rows across texture, loose model, embedded model, and Goodies tabs.

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

Follow-up on 2026-05-07: the same native smoke was rerun against the fresh full install export catalog recorded in `release/readiness/real_asset_full_install_export_2026-05-07.md` and passed with `Passed: 1, Skipped: 0`.

Second follow-up on 2026-05-07: the smoke was extended and rerun against the same fresh catalog to cover hidden/non-grid Goodies 71-73 as artwork rows. It passed with `Passed: 1, Skipped: 0`.

Important output:

```text
Passed!  - Failed: 0, Passed: 1, Skipped: 0, Total: 1
```

## Public-Safe Coverage Summary

The private proof file records only public-safe sample descriptors:

| Area | Sample count |
| --- | ---: |
| Texture rows | 4 |
| Loose model rows | 4 |
| Embedded model rows | 1 |
| Goodies model rows | 2 |
| Hidden/non-grid Goodies artwork rows | 3 |

Goodies rows selected by the native app:

- `BE:A Unit-01 'Pulsar'`
- `BE:A Unit-04S 'Sniper'`

Hidden/non-grid Goodies artwork rows selected by the native app:

- `Goodie 071 - All Configurations`
- `Goodie 072 - Free Camera Mode`
- `Goodie 073 - God Mode`

## What This Proves

- The native WinUI Asset Library can load the full private generated asset catalog.
- The app can navigate real texture, loose model, embedded model, and Goodies rows from that catalog.
- Representative real Goodies model rows can be found and selected in the native app.
- Representative hidden/non-grid Goodies 71-73 artwork rows can be found, selected, previewed, and opened from the native app when the fresh full install catalog is loaded.
- This closes part of the gap between catalog-level linkage checks and actual native app interaction.

## What This Does Not Prove

- It does not prove final textured/animated in-app model viewing.
- It does not prove runtime replay of the in-game Goodies wall.
- It does not commit private screenshots, raw catalog JSON, extracted assets, paths, frames, or proof outputs.
- It does not prove every one of the 45 model-bearing Goodies has been manually selected in WinUI.
- It does not prove normal in-game navigation can reach Goodies 71-73.

## Next Targets

- Broaden native Goodies smoke from representative model/artwork rows to larger sampled families if the UIA run time stays acceptable.
- Add runtime copied-profile Goodies wall replay for representative texture-only, texture+mesh, metadata-only, and FMV slots.
