# WinUI Goodies Catalog Foundation Evidence - 2026-05-07

## Scope

This pass added a real Goodies catalog foundation for the WinUI Asset Library. It does not run BEA, mutate `BEA.exe`, patch the installed game, or commit extracted assets.

## What Changed

- `tools/export_asset_catalog.py` now emits Goodies rows into `catalog.json` and `goodies.json`.
- Goodies rows are derived from packed `GDIE` family evidence, cutscene `.vid` inventory, and extracted language titles.
- `OnslaughtCareerEditor.AppCore` now parses Goodies rows through `AssetCatalogService`.
- WinUI Asset Library now has a Goodies tab that can select Goodies rows and reuse existing texture/model preview paths when the row points to an exported asset.

## Private Corpus Result

The private full-corpus probe wrote ignored output under `subagents/goodie_catalog_probe_2026-05-07/`.

Public-safe counts:

- texture rows: `828`
- loose mesh rows: `213`
- embedded mesh rows: `139`
- video rows: `66`
- language rows: `2571`
- Goodies rows: `233`
- total catalog rows: `4050`

Goodies breakdown:

- artwork: `149`
- model: `45`
- video: `34`
- level: `5`

Important provenance:

- `232` Goodies rows come from `goodie_00_res_PC.aya` through `goodie_231_res_PC.aya`.
- display slot `232` maps to cutscene `33` and has no separate `goodie_232_res_PC.aya`.
- extracted language titles now name rows such as `BE:A Unit-01 'Pulsar'` and `BE:A Unit-04S 'Sniper'`.

## Commands Run

```powershell
py -3 tools/export_asset_catalog.py --self-test
```

Result: pass.

```powershell
dotnet test OnslaughtCareerEditor.AppCore.Tests/OnslaughtCareerEditor.AppCore.Tests.csproj --nologo --filter AssetCatalogServiceTests
```

Result: pass, `5` tests.

```powershell
dotnet build OnslaughtCareerEditor.WinUI/OnslaughtCareerEditor.WinUI.csproj --nologo
```

Result: pass.

```powershell
dotnet test OnslaughtCareerEditor.UiTests/OnslaughtCareerEditor.UiTests.csproj --nologo --filter "FullyQualifiedName~WinUiProductLaneTests|FullyQualifiedName~WinUiAccessibilityAuditTests"
```

Result: pass, `21` tests.

```powershell
npm run test:winui-primary-lane
```

Result: pass. The wrapper built `OnslaughtCareerEditor.WinUI.slnx`, ran AppCore tests (`30 / 30`), ran active UiTests (`47 / 47`), and shut down build servers.

```powershell
npm run test:md-links
npm run test:doc-commands
py -3 tools/docsync_check.py
npm run test:repo-hygiene
npm run test:public-allowlist
py -3 tools/release_curated_manifest.py --check
py -3 tools/release_profile_snapshot.py --check
git diff --check
```

Result: pass.

## What This Proves

- The Goodies browser foundation is backed by generated PC-resource catalog data, not hard-coded sample rows.
- The catalog can carry real Goodies titles from extracted language data.
- WinUI can surface Goodies rows without needing private assets in git.
- Existing texture/model preview paths remain the first rendering layer for Goodies entries that resolve to local exports.

## Not Proven Yet

- Save-aware Goodies unlock state visualization.
- Full in-app textured/animated 3D Goodies model viewer.
- Runtime Goodies behavior.
- Public redistribution of extracted Goodies assets.
