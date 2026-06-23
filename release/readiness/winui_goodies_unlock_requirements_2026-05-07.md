# WinUI Goodies Unlock Requirements Evidence - 2026-05-07

## Scope

This pass turns the Goodies browser from a state-only view into a source-backed reading aid:

- AppCore now maps Goodie indices to unlock requirement summaries from `CCareer::UpdateGoodieStates()` and the documented scripted/cutscene paths.
- WinUI Asset Library Goodies rows and selected summaries show the unlock requirement next to the loaded save state.
- The RE docs now correct two source-correlation issues:
  - save Goodie 78 is the first concept-art row (`GOODIES_79`) and unlocks from `GRADE(100) >= GRADE_C`.
  - Goodie 66 is recomputed through `TOTAL_C_GRADES(66)`, despite the older data-table label `TK_HACK_AGRADES`.

## Files Changed

- `OnslaughtCareerEditor.AppCore/GoodieUnlockRequirementService.cs`
- `OnslaughtCareerEditor.AppCore/AssetCatalogService.cs`
- `OnslaughtCareerEditor.AppCore.Tests/AssetCatalogServiceTests.cs`
- `OnslaughtCareerEditor.WinUI/Pages/AssetLibraryPage.xaml.cs`
- `reverse-engineering/save-file/goodies-system.md`
- `lore-book/reverse-engineering/save-file/goodies-system.md`

## Commands Run

| Command | Result | What it proves |
| --- | --- | --- |
| `dotnet test OnslaughtCareerEditor.AppCore.Tests/OnslaughtCareerEditor.AppCore.Tests.csproj --nologo --filter FullyQualifiedName~AssetCatalogServiceTests` | PASS, 11/11 | AppCore catalog parsing and unlock-rule mapping behave as expected. |
| `dotnet build OnslaughtCareerEditor.WinUI/OnslaughtCareerEditor.WinUI.csproj --nologo` | PASS | WinUI builds with the new AppCore fields. |
| `dotnet test OnslaughtCareerEditor.UiTests/OnslaughtCareerEditor.UiTests.csproj --nologo --filter FullyQualifiedName~WinUiProductLaneTests\|FullyQualifiedName~WinUiAccessibilityAuditTests` | PASS, 21/21 | Product-lane source guards and accessibility checks still pass. |
| `dotnet test OnslaughtCareerEditor.UiTests/OnslaughtCareerEditor.UiTests.csproj --nologo --filter FullyQualifiedName~WinUiVisualSmokeTests.MainWindow_CapturesPrimaryProductScreens` | PASS, 1/1 | Native maximized visual smoke still captures the Asset Library Goodies screen. |
| `npm run test:winui-primary-lane` | PASS, AppCore 37/37 and active UiTests 47/47 | Full primary WinUI lane remains green. |
| `npm run test:md-links` | PASS | Markdown links remain valid after the RE-doc correction. |
| `npm run test:doc-commands` | PASS | Documented commands remain synchronized with npm scripts. |
| `py -3 tools/docsync_check.py` | PASS | Lore mirror stays synchronized with the canonical RE doc. |
| `npm run test:repo-hygiene` | PASS | Text hygiene rules still allow this wording and reject stale claims. |
| `py -3 tools/release_curated_manifest.py --check` | PASS after regeneration | Public candidate allowlist includes the new AppCore service safely. |
| `py -3 tools/release_profile_snapshot.py --check` | PASS after regeneration | Release profile artifacts remain current. |
| `npm run test:public-allowlist` | PASS, 1275 rows | Public release allowlist remains safe. |

## Visual Evidence

- Private ignored screenshot refreshed: `ignored local visual QA screenshot (07-asset-library-goodies.png)`
- The screenshot shows the selected Goodie row with `unlock: Complete level 100` and the selected summary with `save state: new; unlock: Complete level 100`.

## What Did Not Change

- No original game files were modified.
- No Ghidra project mutation or rename apply was performed.
- No runtime proof was claimed.
- No private extracted asset files or screenshots were committed.

## Remaining Follow-Up

- Runtime confirmation of all unlock triggers still requires copied-profile/windowed-patch proof.
- The in-app Goodies model view remains a lightweight wireframe check, not final textured or animated rendering.
- The next static RE target should keep correlating `CCareer__UpdateGoodieStates`, scripted Goodie calls, and cutscene handlers before broad runtime automation.
