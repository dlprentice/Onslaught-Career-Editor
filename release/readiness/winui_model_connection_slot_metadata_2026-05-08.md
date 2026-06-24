# WinUI Model Connection Slot Metadata Evidence - 2026-05-08

## Scope

This note records a focused follow-up to the static model connection metadata work. Binary FBX `OP` texture-to-material connections now preserve readable material slot/property names, such as `DiffuseColor`, when the connection exposes one. The WinUI Asset Library includes those slot names in the selected-model connection summary.

No BEA runtime was launched. No installed game files, saves, private screenshots, private asset payloads, Ghidra project files, or `BEA.exe` bytes were mutated or committed. This is static FBX metadata evidence only. It does not claim material-to-texture correctness, textured 3D rendering, shader/material parity, animation, skeletons, lighting, or runtime Goodies model-viewer behavior.

## Validation

| Command / Check | Result | Important output | What it proves |
| --- | --- | --- | --- |
| `dotnet test .\OnslaughtCareerEditor.AppCore.Tests\OnslaughtCareerEditor.AppCore.Tests.csproj --nologo --filter "FullyQualifiedName~FbxModelSummaryReaderTests"` before implementation | FAIL, expected red | Compile failed because `AssetModelSummary` did not expose `TextureToMaterialSlotNames`. | Confirms the reader assertion was written before AppCore exposed slot-name metadata. |
| `dotnet test .\OnslaughtCareerEditor.AppCore.Tests\OnslaughtCareerEditor.AppCore.Tests.csproj --nologo --filter "FullyQualifiedName~FbxModelSummaryReaderTests"` | PASS | Focused FBX reader tests passed `3/3`. | Confirms binary FBX OP connection slot names are captured for uncompressed and compressed fixture exports. |
| `dotnet test .\OnslaughtCareerEditor.UiTests\OnslaughtCareerEditor.UiTests.csproj --nologo --filter "FullyQualifiedName~WinUiProductLaneTests.AssetLibrary_IsNativeWinUiCatalogBrowser"` before WinUI copy implementation | FAIL, expected red | Source guard failed because Asset Library code did not reference `TextureToMaterialSlotNames`. | Confirms the WinUI assertion was written before the model facts panel surfaced slot names. |
| `dotnet test .\OnslaughtCareerEditor.UiTests\OnslaughtCareerEditor.UiTests.csproj --nologo --filter "FullyQualifiedName~WinUiProductLaneTests.AssetLibrary_IsNativeWinUiCatalogBrowser"` | PASS | Focused source guard passed `1/1`. | Confirms the Asset Library source includes texture-to-material slot names in the connection summary. |
| `dotnet test .\OnslaughtCareerEditor.AppCore.Tests\OnslaughtCareerEditor.AppCore.Tests.csproj --nologo` | PASS | AppCore tests passed `86/86`. | Confirms the expanded model summary record does not regress broader AppCore behavior. |
| `dotnet build .\OnslaughtCareerEditor.WinUI\OnslaughtCareerEditor.WinUI.csproj --nologo` | PASS | Build succeeded with `0` warnings and `0` errors. | Confirms the primary WinUI app compiles after the slot-name copy update. |
| `dotnet test .\OnslaughtCareerEditor.UiTests\OnslaughtCareerEditor.UiTests.csproj --nologo --filter "FullyQualifiedName~WinUiProductLaneTests"` | PASS | Product-lane source tests passed `14/14`. | Confirms broader WinUI source guards remain green after adding slot-name metadata copy. |
| `cmd.exe /c npm run test:md-links` | PASS | Markdown link check passed. | Confirms the new evidence/checklist/extraction links resolve. |
| `cmd.exe /c npm run test:doc-commands` | PASS | Documented npm commands checked: `1214`. | Confirms documented npm command references remain synchronized after the final slot-name metadata evidence update. |
| `py -3 tools\docsync_check.py` | PASS | Docsync policy check passed. | Confirms extraction-pipeline mirrors remain synchronized. |
| `cmd.exe /c npm run test:repo-hygiene` | PASS | Repo text hygiene check passed. | Confirms the slot-name metadata wording avoids stale/private wording guards. |
| `py -3 tools\release_curated_manifest.py --check` | PASS | Selected files `1404`. | Confirms curated release accounting remains synchronized after adding the public-safe evidence note. |
| `py -3 tools\release_profile_snapshot.py --check` before regeneration | FAIL, expected | Profile artifacts were stale after staging the new public-safe evidence note. | Confirms release profile accounting detected the new tracked readiness file. |
| `py -3 tools\release_profile_snapshot.py` | PASS | Counts `R0=1467 R2=0 R3=2 R4=18187`. | Regenerates release profile artifacts after the new evidence note. |
| `py -3 tools\release_profile_snapshot.py --check` | PASS | Counts `R0=1467 R2=0 R3=2 R4=18187`. | Confirms release profile outputs are synchronized after regeneration. |
| `cmd.exe /c npm run test:public-allowlist` | PASS | Rows checked `1404`. | Confirms public allowlist safety still excludes private/runtime/generated asset families. |
| State/manifest JSON parse | PASS | `json ok`. | Confirms state files and the curated manifest remain valid JSON after the metadata evidence update. |
| `git diff --check` and `git diff --cached --check` | PASS | No whitespace errors. | Confirms the working and staged diffs are clean. |
| Process cleanup check | PASS | `process cleanup ok`. | Confirms no managed BEA, CDB, Ghidra, headless Ghidra, or WinUI smoke process was left running. |

## Result

- `AssetModelSummary` now records `TextureToMaterialSlotNames`.
- `FbxModelSummaryReader` now extracts the property-name side of OP texture-to-material connections when object ids resolve to Texture -> Material.
- The WinUI Asset Library selected-model facts panel includes material slot names in the existing `Texture-material links` row.

## Boundary

This improves renderer-readiness metadata because it preserves which FBX material property a texture link claims to target. It still does not prove that the slot maps to the retail runtime material shader, that the referenced texture is visually correct, or that native textured 3D rendering matches the in-game Goodies model viewer.
