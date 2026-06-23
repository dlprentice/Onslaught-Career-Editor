# WinUI Light Theme Default - 2026-05-06

Status: GREEN

Source branch: `wip/sandbox`
Source commit under validation: `84db55f03e3486b640de53f1fe79bab8aa370afe`
Evidence-report commit: `84db55f03e3486b640de53f1fe79bab8aa370afe`

## Purpose

Record the WinUI product-shell change that makes the calmer light theme the default launch experience while keeping the existing dark resources available for future theme work.

The prior visual QA pass proved the native screens rendered, but the app still launched as a heavy forced-dark shell. This pass switches the primary product default to the light theme, removes dark-only inactive sub-tab colors, adds a source-level guard, and refreshes native screenshot evidence.

## Commands

| Command | Working directory | Result | Important output | What it proves |
| --- | --- | --- | --- | --- |
| `dotnet test OnslaughtCareerEditor.UiTests/OnslaughtCareerEditor.UiTests.csproj --nologo --filter FullyQualifiedName~ThemeContrastAuditTests.WinUiApp_DefaultsToLightThemeForPrimaryProductLaunch` | repo root | FAIL before implementation | Expected `Light`, but current `RequestedTheme` was `Dark`. | The new guard detected the forced-dark launch behavior before the product XAML changed. |
| `dotnet test OnslaughtCareerEditor.UiTests/OnslaughtCareerEditor.UiTests.csproj --nologo --filter FullyQualifiedName~ThemeContrastAuditTests` | repo root | PASS | Failed 0, Passed 4, Skipped 0, Total 4. | The WinUI theme now defaults to light and the existing shell contrast audits still pass for Default, Dark, and Light resource dictionaries. |
| `dotnet build .\OnslaughtCareerEditor.WinUI\OnslaughtCareerEditor.WinUI.csproj --nologo` | repo root | PASS | Build succeeded with 0 warnings and 0 errors. | The WinUI app executable was rebuilt before native visual proof. |
| `dotnet test .\OnslaughtCareerEditor.UiTests\OnslaughtCareerEditor.UiTests.csproj --nologo --filter "FullyQualifiedName~WinUiVisualSmokeTests.MainWindow_CapturesPrimaryProductScreens"` | repo root | PASS | Failed 0, Passed 1, Skipped 0, Total 1, Duration 47 s. | The rebuilt native WinUI app launches and captures the primary screens under the new light default. |
| process cleanup check | repo root | PASS | No `OnslaughtCareerEditor.WinUI`, `dotnet`, `MSBuild`, `vstest.console`, `testhost`, `java`, or `javaw` processes remained. | The validation pass did not leave idle app/build/test helpers running. |

## Private Screenshot Set

The refreshed screenshots and contact sheet are private ignored artifacts under:

```text
ignored local visual QA artifact folder
```

The contact sheet was visually inspected locally. Screens now use light page/card surfaces with the existing blue product header, which is calmer and more readable than the previous forced-dark first viewport.

## Proven

- The primary WinUI app no longer forces a dark launch theme.
- The source-level UI test guards the light default.
- Inactive sub-tabs now use named theme resources instead of hard-coded dark colors.
- The native visual smoke passes after rebuilding the WinUI executable.
- The light shell renders across Home, Save Lab, Media audio, Media video, Asset Library texture, Asset Library model, Lore, Patch Bench, Settings, and About.

## Not Proven

- User-selectable runtime theme switching.
- Full high-contrast Windows theme certification.
- Manual Accessibility Insights review.
- Full native 3D/material rendering.
- Media playback state in broad first-viewport screenshots; focused Media interaction evidence covers playback separately.

## Public-Safe Boundaries

- No BEA.exe launch.
- No original game-install mutation.
- No private screenshots committed.
- No private media/assets committed.
- No archived Electron, WPF, or old Python GUI lane reactivation.

## Verdict

GREEN for default WinUI product-shell readability improvement.

The app still needs broader visual/product iteration, but the default launch surface is now materially calmer and guarded by source-level and native visual checks.
