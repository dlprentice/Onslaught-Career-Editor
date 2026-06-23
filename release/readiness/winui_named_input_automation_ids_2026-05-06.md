# WinUI Named Input Automation IDs Evidence - 2026-05-06

Status: public-safe source evidence

Source branch: `wip/sandbox`
Source commit before this wave: `ea015214b5df5c7d4139c23dd51be854770af205`
Evidence-report commit: `b5513d26dbed6c4d18e547664c71c2e9b0f74645`

## Purpose

Record the focused WinUI named-input testability/accessibility hardening pass for the primary Windows product lane.

## What Changed

- Added stable UI Automation IDs to remaining named WinUI page inputs, including sliders, combo boxes, toggles, check boxes, text boxes, number boxes, and list views.
- Added a source-level audit that scans WinUI page XAML files and fails if any named interactive input lacks `AutomationProperties.AutomationId`.
- Deliberately did not require duplicate IDs inside repeated item templates; this pass guards named page-level controls used by automation and accessibility review.

## Commands

| Command | Working directory | Result | Important output | What it proves |
| --- | --- | --- | --- | --- |
| `dotnet build OnslaughtCareerEditor.WinUI/OnslaughtCareerEditor.WinUI.csproj --nologo` | repo root | PASS | Build succeeded with 0 warnings and 0 errors; .NET preview SDK informational banner only. | The WinUI app still builds after named-input automation ID additions. |
| `dotnet test OnslaughtCareerEditor.UiTests/OnslaughtCareerEditor.UiTests.csproj --nologo --filter FullyQualifiedName~WinUiAccessibilityAuditTests` | repo root | PASS | 5/5 focused accessibility audit tests passed. | The new named-input automation ID audit passes and existing static accessibility checks remain green. |
| `git diff --check` | repo root | PASS | No whitespace errors reported. | The patch has no diff whitespace issues. |

## Public-Safe Boundaries

- No BEA.exe launch.
- No original game-install mutation.
- No private screenshots or media artifacts committed.
- No runtime Game Harness proof.
- No accessibility certification claim.

## Not Proven

- Full screen-reader certification.
- Keyboard tab-order review for each named input.
- Windows high-contrast theme review.
- Manual Accessibility Insights review.
- Runtime value-change coverage for every newly identified input.
