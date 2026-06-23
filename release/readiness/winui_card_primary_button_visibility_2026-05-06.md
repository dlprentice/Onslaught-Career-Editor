# WinUI Card Primary Button Visibility - 2026-05-06

Status: GREEN

Source branch: `wip/sandbox`
Source commit under validation: `cace5b1ba8327a0add169ae0b220c8fad37e40e4`
Evidence-report commit: `cace5b1ba8327a0add169ae0b220c8fad37e40e4`

## Purpose

Record the follow-up fix after the light theme default exposed header-only button styling inside normal card surfaces.

`HeroActionButtonStyle` is tuned for the blue product header with translucent white chrome. Reusing it inside light page cards made Home's `Open Save Lab` action and Asset Library's `Load catalog` action too low-contrast. This pass adds a card-safe primary action style and guards page XAML against future `HeroActionButtonStyle` reuse.

## Commands

| Command | Working directory | Result | Important output | What it proves |
| --- | --- | --- | --- | --- |
| `dotnet test OnslaughtCareerEditor.UiTests/OnslaughtCareerEditor.UiTests.csproj --nologo --filter FullyQualifiedName~ThemeContrastAuditTests.WinUiPages_DoNotUseHeroButtonStyleInsideCardSurfaces` | repo root | FAIL before implementation | The audit found `HeroActionButtonStyle` in `Pages\AssetLibraryPage.xaml` and `Pages\HomePage.xaml`. | The new source audit detected the hidden/low-contrast card button issue before the XAML fix. |
| `dotnet test OnslaughtCareerEditor.UiTests/OnslaughtCareerEditor.UiTests.csproj --nologo --filter FullyQualifiedName~ThemeContrastAuditTests` | repo root | PASS | Failed 0, Passed 5, Skipped 0, Total 5. | Theme contrast, light default, named page colors, and page/card button-style guards pass together. |
| `dotnet build .\OnslaughtCareerEditor.WinUI\OnslaughtCareerEditor.WinUI.csproj --nologo` | repo root | PASS | Build succeeded with 0 warnings and 0 errors. | The WinUI app executable was rebuilt before native visual proof. |
| `dotnet test .\OnslaughtCareerEditor.UiTests\OnslaughtCareerEditor.UiTests.csproj --nologo --filter "FullyQualifiedName~WinUiVisualSmokeTests.MainWindow_CapturesPrimaryProductScreens"` | repo root | PASS | Failed 0, Passed 1, Skipped 0, Total 1, Duration 53 s. | The rebuilt native WinUI app launches and captures the primary screens after the card-button fix. |
| process cleanup check | repo root | PASS | No `OnslaughtCareerEditor.WinUI`, `dotnet`, `MSBuild`, `vstest.console`, `testhost`, `java`, or `javaw` processes remained. | The validation pass did not leave idle app/build/test helpers running. |

## Private Screenshot Set

The refreshed screenshots and contact sheet are private ignored artifacts under:

```text
ignored local visual QA artifact folder
```

The Home screenshot was visually inspected locally. `Open Save Lab` now renders as a visible blue primary action beside the secondary `Review Settings` button.

## Proven

- Header-only hero button styling is no longer used inside WinUI page/card XAML.
- Home's primary Save Lab action is visibly styled in the light shell.
- Asset Library's Load Catalog action uses the same card-safe primary style.
- A source-level UI test prevents reintroducing `HeroActionButtonStyle` into active page XAML.
- The native visual smoke passes after rebuilding the WinUI executable.

## Not Proven

- Manual high-contrast theme certification.
- Runtime theme switching.
- Full visual polish of every card and panel.
- Exhaustive keyboard/tab-order review.

## Public-Safe Boundaries

- No BEA.exe launch.
- No original game-install mutation.
- No private screenshots committed.
- No archived app lane reactivation.

## Verdict

GREEN for card primary-action visibility in the light WinUI shell.
