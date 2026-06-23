# WinUI Asset Library Export Actions - 2026-05-06

Status: public-safe release readiness evidence

## Scope

This note records a focused WinUI Asset Library usability/safety improvement after generated-catalog browsing was proven. It does not claim native in-app 3D rendering. It proves the app can select generated asset rows by default and offers scoped actions for safe exported texture/model files.

This report is public-safe. It does not include private game paths, extracted assets, screenshots, copied executables, raw FBX/PNG payloads, runtime proof JSON, or local media cache paths.

## Changes

- Asset Library now auto-selects the first loaded catalog row so the detail panel immediately shows a real selected asset state.
- Texture rows expose an `Open texture` action for generated `.png` exports and a `Copy path` action.
- Loose-mesh and embedded-mesh rows expose an `Open model` action for generated `.fbx` exports and a `Copy path` action.
- The open action is restricted to existing `.png` and `.fbx` exports only.
- Full local paths remain collapsed under path details by default.
- Mesh copy now says that native in-app 3D preview remains a future product slice; it does not pretend binary FBX is parsed in-app.

## Command Evidence

| Command | Result | Important output summary | What it proves |
| --- | --- | --- | --- |
| `dotnet build .\OnslaughtCareerEditor.WinUI\OnslaughtCareerEditor.WinUI.csproj --nologo` | PASS | Build succeeded with 0 warnings and 0 errors. | Confirms WinUI compiles after Asset Library export actions. |
| `dotnet test .\OnslaughtCareerEditor.UiTests\OnslaughtCareerEditor.UiTests.csproj --nologo --filter "FullyQualifiedName~WinUiProductLaneTests"` | PASS | 10/10 focused product-lane tests passed. | Confirms static guards cover Asset Library export actions and safe open extension checks. |
| `dotnet test .\OnslaughtCareerEditor.AppCore.Tests\OnslaughtCareerEditor.AppCore.Tests.csproj --nologo --filter "FullyQualifiedName~AssetCatalogServiceTests"` | PASS | 3/3 focused AssetCatalogService tests passed. | Confirms generated-catalog parsing remains intact. |
| `dotnet test .\OnslaughtCareerEditor.UiTests\OnslaughtCareerEditor.UiTests.csproj --nologo --filter "FullyQualifiedName~WinUiVisualSmokeTests.MainWindow_CapturesPrimaryProductScreens"` | PASS | 1/1 explicit visual smoke passed. | Confirms the native screenshot workflow captures the selected Asset Library state. |
| `dotnet test .\OnslaughtCareerEditor.AppCore.Tests\OnslaughtCareerEditor.AppCore.Tests.csproj --nologo` | PASS | 23/23 AppCore tests passed. | Confirms core behavior remains green. |
| `dotnet test .\OnslaughtCareerEditor.UiTests\OnslaughtCareerEditor.UiTests.csproj --nologo --filter "FullyQualifiedName!~LegacyWpf"` | PASS | 31/31 active UiTests passed. | Confirms the wider active WinUI/static/runtime test set remains green. |
| `py -3 tools\release_profile_snapshot.py --check` | PASS | Counts `R0=1158 R2=0 R3=2 R4=18186`. | Confirms release profile artifacts account for this public-safe report. |
| `py -3 tools\release_curated_manifest.py --check` | PASS | Selected files: `1146`; curated allowlist check passed. | Confirms curated manifest and public allowlist are synchronized. |
| `npm run test:doc-commands` | PASS | 260 documented commands checked. | Confirms documented command references remain valid. |
| `npm run test:md-links` | PASS | Markdown link check passed. | Confirms docs links remain valid. |
| `npm run test:public-allowlist` | PASS | 1,146 rows checked. | Confirms public release candidates still exclude private/runtime/generated asset families. |
| `npm run test:repo-hygiene` | PASS | 24 hygiene tests passed; live scan passed with 19 text and 2 path rules. | Confirms public docs/evidence did not reintroduce guarded stale/private wording. |

## Screenshot Review

Private screenshot reviewed locally:

- `ignored local visual QA screenshot (05-asset-library.png)`

The screenshot shows the catalog loaded, the first texture selected, the selected asset title and summary, `Open texture` and `Copy path` actions, and path details collapsed. The synthetic test texture renders as a narrow preview strip; that is a fixture/polish issue, not a private asset leak.

## What Is Proven

- The WinUI Asset Library can present a selected generated asset immediately after catalog load.
- Export actions are scoped to generated `.png`/`.fbx` files and disabled for unavailable/unsupported exports.
- Users can open exported textures/models with their local viewer without exposing full local paths in primary UI.
- Native 3D model rendering is still represented honestly as future work.

## What Is Not Proven

- Native in-app 3D model rendering.
- Binary FBX parsing inside AppCore or WinUI.
- Model animation, materials, skeletons, or camera controls.
- Packaged-output behavior for external viewers.
- Any public redistribution approval for extracted assets.

## Current Decision

Keep the exported-model action as the safe first model-inspection affordance. Treat native in-app 3D preview as a later technical slice that should choose a renderer/parser deliberately rather than bolting a risky dependency into the product lane.
