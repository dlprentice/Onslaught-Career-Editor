# WinUI Home Accessibility IDs Evidence - 2026-05-06

Status: public-safe source evidence

Source branch: `wip/sandbox`
Source commit before this wave: `dc19b088f38a5087dcbdf33d021ed77a73a3aa0e`
Evidence-report commit: `2d8d691e7eab8197ae04d6b1d228576e0ef84102`

## Purpose

Record the focused Home page accessibility/testability hardening pass for the primary WinUI 3 product lane.

## What Changed

- Added stable UI Automation IDs to the Home page title, purpose copy, setup status text, and primary task buttons.
- Added explicit accessible names for the Home page navigation buttons.
- Extended the WinUI accessibility audit to require those Home page IDs so future regressions are caught by source-level tests.

## Commands

| Command | Working directory | Result | Important output | What it proves |
| --- | --- | --- | --- | --- |
| `dotnet build OnslaughtCareerEditor.WinUI/OnslaughtCareerEditor.WinUI.csproj --nologo` | repo root | PASS | Build succeeded with 0 warnings and 0 errors; .NET preview SDK informational banner only. | The WinUI app still builds after the Home page XAML accessibility changes. |
| `dotnet test OnslaughtCareerEditor.UiTests/OnslaughtCareerEditor.UiTests.csproj --nologo --filter FullyQualifiedName~WinUiAccessibilityAuditTests` | repo root | PASS | 3/3 focused accessibility audit tests passed. | The static WinUI accessibility audit now covers Home page automation IDs and keeps the prior page checks passing. |
| `git diff --check` | repo root | PASS | No whitespace errors reported. | The patch has no diff whitespace issues. |

## Public-Safe Boundaries

- No BEA.exe launch.
- No original game-install mutation.
- No private screenshots or media artifacts committed.
- No runtime Game Harness proof.
- No accessibility certification claim.

## Not Proven

- Full screen-reader certification.
- Keyboard tab-order review.
- Windows high-contrast theme review.
- Manual Accessibility Insights review.
- Visual screenshot review for this specific Home page pass.
