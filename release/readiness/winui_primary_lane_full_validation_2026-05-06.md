# WinUI Primary Lane Full Validation - 2026-05-06

Status: public-safe source/test evidence

Source branch: `wip/sandbox`
Source commit under validation: `48fa1351bf51f977ad93194c99de88b4ab241794`
Evidence-report commit: `b8759dbe0a47c8dd732fca836ef9b3e6bfb79ed7`

## Purpose

Record the broader primary-lane validation run after the WinUI automation ID hardening waves.

## Commands

| Command | Working directory | Result | Important output | What it proves |
| --- | --- | --- | --- | --- |
| `dotnet build OnslaughtCareerEditor.WinUI.slnx --nologo` | repo root | PASS | Build succeeded with 0 warnings and 0 errors; .NET preview SDK informational banner only. | The primary WinUI aggregate solution builds after the accessibility/testability hardening waves. |
| `dotnet test OnslaughtCareerEditor.AppCore.Tests/OnslaughtCareerEditor.AppCore.Tests.csproj --nologo` | repo root | PASS | 28/28 AppCore tests passed. | Shared correctness/core support remains green. |
| `dotnet test OnslaughtCareerEditor.UiTests/OnslaughtCareerEditor.UiTests.csproj --nologo --filter FullyQualifiedName!~LegacyWpf` | repo root | PASS | 41/41 active UI tests passed. | Active WinUI product-lane/static/smoke tests remain green while archived WPF regression tests stay excluded by filter. |

## Public-Safe Boundaries

- No BEA.exe launch.
- No original game-install mutation.
- No private screenshots or media artifacts committed.
- No runtime Game Harness proof.
- No claim of installer-grade release readiness.

## Not Proven

- Signed or installer-grade release.
- Trusted install/launch/uninstall.
- Full manual exploratory WinUI review.
- Full accessibility certification.
- Runtime gameplay behavior.
