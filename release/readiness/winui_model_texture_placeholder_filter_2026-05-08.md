# WinUI Model Texture Placeholder Filter Evidence - 2026-05-08

## Scope

This note records a focused correction to model texture-link semantics in AppCore and the public-safe model texture linkage probe.

Binary FBX exports contain template/default material texture placeholders such as `default10.png` and `base_color_texture.png`. These are exporter placeholders, not real Battle Engine Aquila texture references. Counting them as catalog-missing texture bindings made WinUI/AppCore coverage look weaker than the dedicated sidecar probe semantics and created stale sidecar-needed counts.

The fix keeps real sidecar texture fallback support intact, but excludes template/default placeholder names from catalog-missing texture-link coverage.

No BEA runtime was launched. No installed game files, saves, Ghidra project, exported FBX files, texture sidecars, or original `BEA.exe` were mutated. Raw full-install probe JSON stayed under ignored `subagents/model-material-semantics-2026-05-08/`.

## Validation

| Command / Check | Result | Important output | What it proves |
| --- | --- | --- | --- |
| `dotnet test .\OnslaughtCareerEditor.AppCore.Tests\OnslaughtCareerEditor.AppCore.Tests.csproj --nologo --filter "FullyQualifiedName~AssetCatalogServiceTests.ModelTextureLinks_IgnoresBlankBindingsAndMatchesPathVariants"` before implementation | FAIL, expected red | The test found `default10.png` in `TextureBindingFileNames`. | Confirms the placeholder exclusion assertion caught the stale AppCore behavior. |
| `dotnet test .\OnslaughtCareerEditor.AppCore.Tests\OnslaughtCareerEditor.AppCore.Tests.csproj --nologo --filter "FullyQualifiedName~AssetCatalogServiceTests.ModelTextureLinks_IgnoresBlankBindingsAndMatchesPathVariants"` | PASS | Focused test passed `1/1`. | Confirms AppCore now ignores default/template texture placeholders in model texture-link resolution. |
| `dotnet test .\OnslaughtCareerEditor.AppCore.Tests\OnslaughtCareerEditor.AppCore.Tests.csproj --nologo --filter "FullyQualifiedName~AssetCatalogServiceTests.ModelPreviewCoverage_SummarizesWireframeAvailability\|FullyQualifiedName~AssetCatalogServiceTests.ModelPreviewCoverage_DistinguishesAllCatalogMatchedRowsFromSidecarNeededRows\|FullyQualifiedName~AssetCatalogServiceTests.ModelTextureLinks"` | PASS | Focused AppCore texture/model coverage tests passed `6/6`. | Confirms the resolver correction preserves fixture-backed direct and sidecar-needed behavior. |
| `cmd.exe /c npm run test:model-texture-linkage` before probe resolver update | FAIL, expected red | Fixture expected one catalog-missing ref, but the probe reported two because it ignored `export_file_name` compact matching. | Confirms the Python probe lagged behind AppCore texture-name resolution semantics. |
| `cmd.exe /c npm run test:model-texture-linkage` | PASS | Probe fixture tests passed `2/2`. | Confirms the probe now matches catalog canonical refs, export filenames, and compact variants while stripping private paths. |
| `py -3 tools\model_texture_linkage_probe.py --catalog subagents\asset-full-install-2026-05-07\full-export\asset_catalog\catalog.json --check --out subagents\model-material-semantics-2026-05-08\model-texture-linkage-after-resolver.json` | PASS | Models `352`; rows with refs `352`; unique refs `213`; missing sidecars `0`; catalog missing `0`. | Confirms every checked real model texture reference resolves to local sidecar coverage and to a catalog texture row after placeholder filtering and compact export-name matching. |
| `dotnet run --project .\OnslaughtCareerEditor.AppCore.Host\OnslaughtCareerEditor.AppCore.Host.csproj -- inspect-asset-model-preview .\subagents\asset-full-install-2026-05-07\full-export\asset_catalog\catalog.json --sample-limit 100` | PASS | Full-install aggregate: all-direct rows `352`, any-missing rows `0`, catalog-matched texture bindings `1268`. | Confirms the AppCore host diagnostic now reports the same corrected texture-link semantics used by WinUI. |
| `dotnet test .\OnslaughtCareerEditor.AppCore.Tests\OnslaughtCareerEditor.AppCore.Tests.csproj --nologo` | PASS | AppCore tests passed `86/86`. | Confirms the resolver correction does not regress broader AppCore coverage. |
| `dotnet build .\OnslaughtCareerEditor.WinUI\OnslaughtCareerEditor.WinUI.csproj --nologo` | PASS | Build succeeded with `0` warnings and `0` errors. | Confirms the WinUI lane still builds after the AppCore resolver correction. |
| `dotnet test .\OnslaughtCareerEditor.UiTests\OnslaughtCareerEditor.UiTests.csproj --nologo --filter "FullyQualifiedName~WinUiProductLaneTests"` | PASS | Product-lane tests passed `15/15`. | Confirms the WinUI product-lane source guards still pass. |
| `npm run test:md-links` | PASS | Markdown link check passed. | Confirms the new evidence and extraction-pipeline links resolve. |
| `npm run test:doc-commands` | PASS | Documented npm script references checked: `1251`. | Confirms documented npm script references remain valid. |
| `py -3 tools\docsync_check.py` | PASS | Docsync policy check passed. | Confirms mirrored docs remain synchronized. |
| `npm run test:repo-hygiene` | PASS | Unit rules passed `29/29`; repo hygiene rules passed. | Confirms the public-safe evidence does not reintroduce stale lane/copy hazards. |
| `py -3 tools\release_curated_manifest.py --check`, regenerate, recheck | PASS | Curated allowlist selected `1405` files after adding this report. | Confirms the public-safe evidence note is included in the curated release manifest. |
| `py -3 tools\release_profile_snapshot.py --check`, regenerate, recheck | PASS | Regenerated profile counts `R0=1470`, `R2=0`, `R3=2`, `R4=18188`. | Confirms release profile artifacts include this new evidence note and remain policy-consistent. |
| `npm run test:public-allowlist` | PASS | Public allowlist safety check passed for `1405` rows. | Confirms no private asset/proof paths were added to the public allowlist. |
| State/manifest JSON parse | PASS | `json ok`. | Confirms state and manifest JSON remain valid. |
| `git diff --check` and `git diff --cached --check` | PASS | No whitespace errors. | Confirms working and staged diffs are clean. |
| Process cleanup check | PASS | `process cleanup ok`. | Confirms no managed BEA, CDB, Ghidra, headless Ghidra, or WinUI smoke process was left running. |

## Result

- AppCore ignores template/default FBX texture placeholders before catalog matching.
- The Python linkage probe now uses canonical refs, export filenames, and compact matching like AppCore.
- Current full-install model texture evidence is:
  - `352/352` model rows with readable real texture refs,
  - `213/213` unique real model texture refs with local sidecar coverage,
  - `213/213` unique real model texture refs represented by catalog texture rows,
  - `0` unique real model texture refs missing sidecar coverage,
  - `0` unique real model texture refs missing catalog coverage.

## Boundary

This is static model texture-link correctness evidence. It does not prove native textured WinUI rendering, material/shader/alpha parity, animation, skeletons, lighting, runtime Goodies model-viewer playback, or redistribution rights for private extracted assets.
