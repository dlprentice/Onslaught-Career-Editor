# WinUI Goodies Facts Panel - 2026-05-07

Status: public-safe WinUI product evidence

## Objective

Make selected Goodies easier to understand in the native WinUI Asset Library without changing asset extraction, save parsing, media playback, runtime behavior, or backend contracts.

The selected Goodie view previously relied on a single long summary sentence for save state, wall placement, unlock requirement, reward type, and preview linkage. This was correct but hard to scan.

## Change

- Added a structured `Goodie facts` section to the selected Goodie details.
- The facts section exposes stable UI Automation ids:
  - `AssetGoodieFactsPanel`
  - `AssetGoodieFactState`
  - `AssetGoodieFactWall`
  - `AssetGoodieFactUnlock`
  - `AssetGoodieFactReward`
  - `AssetGoodieFactEvidence`
- Kept the asset preview first in the first viewport. The details are available below the preview and via UI Automation.
- Shortened the selected Goodie summary so it introduces the reward/preview result without repeating every fact.
- Preserved the explicit boundary that runtime reachability still requires copied-profile proof.

## Validation

- `dotnet build OnslaughtCareerEditor.WinUI/OnslaughtCareerEditor.WinUI.csproj --nologo` - PASS, 0 warnings/errors.
- `dotnet test OnslaughtCareerEditor.UiTests/OnslaughtCareerEditor.UiTests.csproj --nologo --filter AssetLibrary_IsNativeWinUiCatalogBrowser` - PASS, 1/1.
- `dotnet test OnslaughtCareerEditor.UiTests/OnslaughtCareerEditor.UiTests.csproj --nologo --filter AssetLibrary_CapturesRealGoodiesBrowserWhenCatalogProvided` with `ONSLAUGHT_WINUI_REAL_ASSET_CATALOG` and maximized capture enabled - PASS, 1/1.
- `npm run test:winui-primary-lane` - PASS; WinUI solution build PASS, AppCore tests PASS 82/82, active UiTests PASS 48/50 with two private real-catalog smokes skipped by default.
- Release/docs/state safety checks - PASS: curated manifest, release profile, markdown links, documented command references, docsync, public allowlist, repo hygiene, state JSON parse, and diff check.
- Process cleanup checks - PASS; no WinUI app process and no `BEA.exe` process remained.

## Private Visual Evidence

Captured screenshots remain ignored/private under `subagents/winui-real-asset-visual-qa/2026-05-07/`:

- `asset-library-real-goodie-model.png`
- `asset-library-real-goodie-artwork.png`
- `asset-library-real-goodie-video.png`
- `asset-library-real-goodie-video-media-handoff.png`

## Not Claimed

- This does not prove Goodies 71-73 runtime reachability.
- This does not launch or patch `BEA.exe`.
- This does not change extraction output.
- This does not implement textured/animated native 3D model rendering.
- This does not make private screenshots or extracted assets public.
