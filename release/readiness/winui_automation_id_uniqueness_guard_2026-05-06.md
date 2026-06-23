# WinUI Automation ID Uniqueness Guard - 2026-05-06

Status: public-safe source/test evidence

Source branch: `wip/sandbox`
Source commit before this wave: `3d4313f57991625ac8d58e22656d11c10b54a6a4`
Evidence-report commit: `28c8db70edbf6646f380a935fc746fca431ad7cb`

## Purpose

Record the source-level guard that keeps WinUI UI Automation IDs unique across XAML source.

## What Changed

- Added a focused `WinUiAccessibilityAuditTests` check that scans WinUI source XAML for duplicate `AutomationProperties.AutomationId` values.
- This complements the page-button and named-input ID guards by preventing future duplicate IDs from making UI Automation selectors ambiguous.

## Commands

| Command | Working directory | Result | Important output | What it proves |
| --- | --- | --- | --- | --- |
| `dotnet test OnslaughtCareerEditor.UiTests/OnslaughtCareerEditor.UiTests.csproj --nologo --filter FullyQualifiedName~WinUiAccessibilityAuditTests` | repo root | PASS | 6/6 focused accessibility audit tests passed. | The duplicate-ID guard passes and the existing WinUI accessibility audit checks remain green. |
| `git diff --check` | repo root | PASS | No whitespace errors reported. | The patch has no diff whitespace issues. |

## Public-Safe Boundaries

- No BEA.exe launch.
- No original game-install mutation.
- No private screenshots or media artifacts committed.
- No runtime Game Harness proof.
- No accessibility certification claim.

## Not Proven

- Runtime uniqueness inside repeated item templates.
- Full screen-reader certification.
- Keyboard tab-order review.
- Manual Accessibility Insights review.
