# WinUI Model Slot Host Diagnostic Evidence - 2026-05-08

## Scope

This note records a focused follow-up to the WinUI model slot coverage summary. The read-only `OnslaughtCareerEditor.AppCore.Host inspect-asset-model-preview` diagnostic now emits aggregate UV, material-layer, connection, texture-link, and material-slot coverage fields from `AssetModelPreviewCoverage`, including `RowsWithTextureToMaterialSlotNames` and `TextureToMaterialSlotNames`.

The diagnostic was rerun against the ignored generated full-install catalog. Raw JSON stayed under `subagents/model-slot-host-coverage-2026-05-08/asset-model-preview-coverage.json` and was not committed.

## Validation

| Command / Check | Result | Important output | What it proves |
| --- | --- | --- | --- |
| `dotnet test .\OnslaughtCareerEditor.UiTests\OnslaughtCareerEditor.UiTests.csproj --nologo --filter "FullyQualifiedName~WinUiProductLaneTests.AppCoreHost_ModelPreviewCoverageIncludesMaterialSlotCoverage"` before implementation | FAIL, expected red | Source guard failed because `OnslaughtCareerEditor.AppCore.Host/Program.cs` did not contain `RowsWithTextureToMaterialSlotNames`. | Confirms the host-output assertion was written before the host diagnostic exposed aggregate material-slot coverage. |
| `dotnet test .\OnslaughtCareerEditor.UiTests\OnslaughtCareerEditor.UiTests.csproj --nologo --filter "FullyQualifiedName~WinUiProductLaneTests.AppCoreHost_ModelPreviewCoverageIncludesMaterialSlotCoverage"` | PASS | Focused source guard passed `1/1`. | Confirms the host diagnostic source carries material-slot coverage fields. |
| `dotnet build .\OnslaughtCareerEditor.AppCore.Host\OnslaughtCareerEditor.AppCore.Host.csproj --nologo` | PASS | Build succeeded with `0` warnings and `0` errors. | Confirms the AppCore host compiles after extending the diagnostic payload. |
| `dotnet run --project .\OnslaughtCareerEditor.AppCore.Host\OnslaughtCareerEditor.AppCore.Host.csproj --no-build -- inspect-asset-model-preview .\subagents\asset-full-install-2026-05-07\full-export\asset_catalog\catalog.json --sample-limit 8 > subagents\model-slot-host-coverage-2026-05-08\asset-model-preview-coverage.json` | PASS | Public-safe summary from the ignored JSON: model rows `352`, rows with material-slot names `352`, slot names `DiffuseColor`, samples `8`. | Confirms the read-only host diagnostic can reproduce the full-install material-slot coverage without committing private paths or asset payloads. |
| `dotnet test .\OnslaughtCareerEditor.UiTests\OnslaughtCareerEditor.UiTests.csproj --nologo --filter "FullyQualifiedName~WinUiProductLaneTests"` | PASS | Product-lane source tests passed `15/15`. | Confirms the new host-output guard does not regress the broader WinUI product-lane source checks. |
| `npm run test:md-links` | PASS | Markdown link check passed. | Confirms the new evidence and extraction-pipeline links resolve. |
| `npm run test:doc-commands` | PASS | Documented npm script references checked: `1226`. | Confirms documented npm command references remain valid. |
| `py -3 tools\docsync_check.py` | PASS | Docsync policy check passed. | Confirms mirrored docs remain synchronized. |
| `npm run test:repo-hygiene` | PASS | Unit rules passed `29/29`; repo hygiene checked `23` text rules, `2` path rules, and `1` required marker. | Confirms the new public-safe evidence does not reintroduce stale lane/copy hazards. |
| `py -3 tools\release_curated_manifest.py --check` | PASS | Curated allowlist selected `1404` files. | Confirms the curated public release manifest remains safe. |
| `py -3 tools\release_profile_snapshot.py --check`, then regenerate/recheck | PASS | Initial check found stale profile artifacts; regeneration produced `R0=1469`, `R2=0`, `R3=2`, `R4=18187`; recheck passed. | Confirms release profile artifacts include this new evidence note and remain policy-consistent. |
| `npm run test:public-allowlist` | PASS | Public allowlist safety check passed for `1404` rows. | Confirms no private asset/proof paths were added to the public allowlist. |
| State JSON parse | PASS | `developer_agent_state.json`, `documentation_agent_state.json`, and `curated_release_manifest.json` parsed successfully. | Confirms state and manifest JSON remain valid. |
| `git diff --check` and `git diff --cached --check` | PASS | No whitespace errors. | Confirms working and staged diffs are clean. |
| Process cleanup check | PASS | `process cleanup ok`. | Confirms no managed BEA, CDB, Ghidra, headless Ghidra, or WinUI smoke process was left running. |

## Result

- `inspect-asset-model-preview` now emits current `AssetModelPreviewCoverage` material/UV/connection/slot fields.
- Full-install read-only diagnostic output reports `352/352` model rows with readable texture-to-material slot names.
- The only slot name in the current generated full-install catalog summary is `DiffuseColor`.

## Boundary

This is a read-only static AppCore host diagnostic. It does not launch BEA, mutate saves, mutate Ghidra, patch or read/write the original `BEA.exe`, prove textured native rendering, prove shader/material parity, prove animation/skeleton/lighting behavior, or grant redistribution rights for private assets.
