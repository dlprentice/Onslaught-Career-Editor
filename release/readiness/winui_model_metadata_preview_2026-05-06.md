# WinUI Model Metadata Preview - 2026-05-06

Status: public-safe release readiness evidence

## Scope

This note records a focused WinUI Asset Library improvement for generated model exports. It does not claim native in-app 3D rendering. It proves the app can read lightweight metadata from local binary FBX exports and show immediate model facts in the WinUI detail panel without bundling private extracted assets.

This report is public-safe. It does not include private game paths, extracted assets, screenshots, raw FBX/PNG payloads, local media cache paths, copied executables, or raw proof JSON.

## Discovery

- The current generated asset catalog records texture exports, loose mesh exports, and embedded mesh exports.
- Current generated mesh exports are binary FBX files with a `Kaydara FBX Binary` header and FBX version `7400`.
- A full native 3D renderer remains a separate product slice because it needs deliberate renderer/parser dependency selection, camera controls, material handling, and packaging/licensing review.

## Changes

- Added `FbxModelSummaryReader` in AppCore for read-only binary FBX header/node metadata.
- Asset catalog mesh rows now carry `AssetModelSummary` facts for generated `.fbx` exports.
- WinUI Asset Library mesh detail now shows a visible compact model-facts line, including format, vertex count, and polygon index entry count when metadata is readable.
- WinUI Asset Library keeps `Open model` and `Copy path` scoped to existing generated `.fbx` exports.
- Full local paths remain collapsed under path details by default.
- Native in-app 3D rendering is still labeled honestly as not enabled yet.
- Visual smoke now captures both the texture tab and model tab with synthetic public-safe fixtures.

## Command Evidence

| Command | Result | Important output summary | What it proves |
| --- | --- | --- | --- |
| Private catalog inspection with `ConvertFrom-Json` | PASS | Local ignored catalog showed 828 texture rows, 213 loose mesh rows, and 139 embedded mesh rows. | Confirms the model metadata work targets the current generated catalog shape without committing private catalog data. |
| Private FBX header inspection | PASS/WARN | Sample private exported FBX files reported `Kaydara FBX Binary`; a PowerShell `Format-Hex -Count` parameter was unavailable in this shell, but header bytes were still read directly. | Confirms current generated model exports are binary FBX files while documenting the shell limitation. |
| Binary FBX node probe with Node.js | PASS | Private sample probe identified FBX version `7400` plus standard `Geometry`, `Vertices`, `PolygonVertexIndex`, `Model`, `Material`, and `Texture` nodes. | Confirms a lightweight read-only metadata reader is feasible without a full renderer. |
| Focused AppCore FBX/catalog test filter | PASS | 5/5 focused AppCore tests passed. | Confirms the FBX metadata reader and catalog wiring work on synthetic public-safe fixtures and non-binary fallback inputs. |
| `dotnet build .\OnslaughtCareerEditor.WinUI\OnslaughtCareerEditor.WinUI.csproj --nologo` | PASS after fix | Initial build exposed a duplicate local-variable bug in `RenderModelSummary`; final build succeeded with 0 warnings and 0 errors. | Confirms the WinUI app compiles after the model metadata panel and inline summary changes. |
| `dotnet test .\OnslaughtCareerEditor.UiTests\OnslaughtCareerEditor.UiTests.csproj --nologo --filter "FullyQualifiedName~WinUiProductLaneTests"` | PASS | 11/11 focused product-lane tests passed. | Confirms static WinUI guards cover Asset Library model facts, safe export actions, and route visibility. |
| `dotnet test .\OnslaughtCareerEditor.UiTests\OnslaughtCareerEditor.UiTests.csproj --nologo --filter "FullyQualifiedName~WinUiVisualSmokeTests.MainWindow_CapturesPrimaryProductScreens"` | PASS after fix | Visual smoke initially exposed that model details were below the fold and that page-local style lookup could crash the Asset Library startup path; final run passed 1/1 and captured separate texture/model Asset Library screenshots under ignored `subagents/`. | Confirms primary WinUI screens render and the model tab visibly shows compact model facts. |
| `dotnet test .\OnslaughtCareerEditor.AppCore.Tests\OnslaughtCareerEditor.AppCore.Tests.csproj --nologo` | PASS | 25/25 AppCore tests passed. | Confirms the full shared-core test suite remains green after adding the FBX metadata reader. |
| `dotnet test .\OnslaughtCareerEditor.UiTests\OnslaughtCareerEditor.UiTests.csproj --nologo --filter "FullyQualifiedName!~LegacyWpf"` | PASS | 32/32 active UiTests passed. | Confirms active WinUI/static/runtime automation remains green. |
| Guarded `Get-Process -Name OnslaughtCareerEditor.WinUI` check | PASS | No `OnslaughtCareerEditor.WinUI` process remained after smoke tests. | Confirms the visual smoke did not leave the app open. |
| `py -3 tools\release_profile_snapshot.py` and `py -3 tools\release_curated_manifest.py` | PASS | Profile regenerated with `R0=1162 R2=0 R3=2 R4=18186`; curated allowlist selected 1151 files. | Accounts for this public-safe evidence report in release artifacts. |
| `py -3 tools\release_profile_snapshot.py --check` and `py -3 tools\release_curated_manifest.py --check` | PASS | Release profile and curated allowlist checks passed after regeneration. | Confirms release accounting is synchronized. |
| `py -3 tools\docsync_check.py` | PASS | Dsync policy check passed. | Confirms mirrored docs remain synchronized. |
| `npm run test:doc-commands` | PASS | 286 documented npm commands checked. | Confirms command documentation remains valid. |
| `npm run test:md-links` | PASS | Markdown link check passed. | Confirms docs links remain valid. |
| `npm run test:public-allowlist` | PASS | Public allowlist safety check passed; 1151 rows checked. | Confirms public release candidates still exclude private/runtime/generated asset families. |
| `npm run test:repo-hygiene` | PASS | 24 hygiene unit tests passed; live scan checked 19 text and 2 path rules. | Confirms public docs/evidence did not reintroduce guarded stale/private wording. |
| `npm run test:winui-notices` | PASS | Third-party notices check passed for 74 packages. | Confirms WinUI notice draft remains current. |
| JSON parse and `git diff --check` | PASS | State files and curated manifest parsed; whitespace check passed with line-ending normalization warnings only for generated TSV/inventory files. | Confirms state/manifest JSON validity and diff hygiene. |

## Screenshot Review

Private screenshots reviewed locally:

- `ignored local visual QA screenshot (05-asset-library-texture.png)`
- `ignored local visual QA screenshot (06-asset-library-model.png)`

The model screenshot shows the generated model row selected, `Open model` and `Copy path` actions available, path details collapsed, and a visible compact facts line such as binary FBX version, vertex count, and polygon index entry count. Screenshots stay ignored/private.

## What Is Proven

- AppCore can read public-safe metadata from binary FBX 7400 files without bringing private model payloads into public release scope.
- WinUI Asset Library can show immediate model facts for selected generated loose and embedded mesh exports.
- Visual smoke covers both texture and model Asset Library states with synthetic fixtures.
- Native 3D rendering remains unclaimed.

## What Is Not Proven

- Native in-app 3D model rendering.
- Material preview fidelity.
- Texture binding preview.
- Animation, skeleton, camera, or lighting controls.
- Packaged-output behavior for model metadata preview.
- Public redistribution approval for extracted model assets.

## Current Decision

Keep lightweight model facts in the WinUI Asset Library as the honest near-term model-inspection surface. Treat full native 3D preview as a deliberate future renderer/parser decision rather than an opportunistic dependency addition.
