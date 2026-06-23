# WinUI Primary Action Contrast Guard - 2026-05-06

Status: GREEN

Source branch: `wip/sandbox`
Source commit under validation: `775418c33c783bf11c17a910c59b8b9875fe7d10`
Evidence-report commit: `775418c33c783bf11c17a910c59b8b9875fe7d10`

## Purpose

Record the contrast hardening added after `PrimaryActionButtonStyle` made `ShellAccentBrush` a text-bearing button background.

The existing theme audit checked accent contrast against surfaces, but did not check white button text against the accent brush. Default/Dark used a lighter blue that passed non-text accent visibility but failed white-text contrast. This pass adds the missing assertion and darkens the Default/Dark accent enough to satisfy both requirements.

## Commands

| Command | Working directory | Result | Important output | What it proves |
| --- | --- | --- | --- | --- |
| `dotnet test OnslaughtCareerEditor.UiTests/OnslaughtCareerEditor.UiTests.csproj --nologo --filter FullyQualifiedName~ThemeContrastAuditTests.WinUiShellThemeColors_MeetMinimumContrastThresholds` | repo root | FAIL before implementation | `ShellHeroTextBrush` vs `ShellAccentBrush` contrast ratio was `3.75`, below required `4.50`. | The new assertion caught the missing text-on-accent contrast rule. |
| `dotnet test OnslaughtCareerEditor.UiTests/OnslaughtCareerEditor.UiTests.csproj --nologo --filter FullyQualifiedName~ThemeContrastAuditTests` | repo root | PASS | Failed 0, Passed 5, Skipped 0, Total 5. | Theme contrast, light default, named page colors, and page/card button-style guards pass together after the accent update. |

## Proven

- White text on primary accent buttons now meets the `4.5:1` contrast threshold in Default, Dark, and Light theme dictionaries.
- Accent visibility against shell surfaces remains guarded.
- The card-safe primary button style has a stronger theme-level contrast contract.

## Not Proven

- Full Windows high-contrast theme certification.
- Manual Accessibility Insights review.
- Runtime user-selectable theme switching.

## Public-Safe Boundaries

- No BEA.exe launch.
- No game-install mutation.
- No private screenshots committed.
- No archived app lane reactivation.

## Verdict

GREEN for source-level primary-action contrast hardening.
