# WinUI Primary Lane Validation Wrapper - 2026-05-06

Status: public-safe tooling/test evidence

Source branch: `wip/sandbox`
Source commit before this wave: `6e1acaa235f8195eb6663cde65196e0686b321b2`
Evidence-report commit: `ebf0b2767f038d51d2c5cb98c9b962c18275b39c`

## Purpose

Record the cleanup-aware validation wrapper for the primary WinUI lane.

## What Changed

- Added `tools/winui_primary_lane_validation.py`.
- Added `npm run test:winui-primary-lane`.
- The wrapper runs the WinUI solution build, AppCore tests, and active UiTests serially.
- The wrapper sets `MSBUILDDISABLENODEREUSE=1` for child `dotnet` commands and calls `dotnet build-server shutdown` in a `finally` block.

## Commands

| Command | Working directory | Result | Important output | What it proves |
| --- | --- | --- | --- | --- |
| `npm run test:winui-primary-lane` | repo root | PASS | WinUI solution build passed with 0 warnings/errors; AppCore tests passed 28/28; active UiTests passed 41/41; `dotnet build-server shutdown` reported MSBuild and compiler server shutdown success. | The wrapper can run the primary-lane validation sequence and shut down build servers. |
| Process check for `OnslaughtCareerEditor.WinUI,dotnet,MSBuild,vstest.console,testhost,java,javaw` | repo root | PASS | `none` | The wrapper run left no relevant app/build/test/Ghidra processes behind in this session. |

## Post-Guard Rerun

After the automation-ID uniqueness guard landed, `npm run test:winui-primary-lane` was rerun against the updated active UI test set:

- WinUI solution build: PASS, 0 warnings, 0 errors.
- AppCore tests: PASS, 28/28.
- Active UiTests: PASS, 42/42.
- `dotnet build-server shutdown`: reported MSBuild and compiler server shutdown success.
- Follow-up process check: `none` for `OnslaughtCareerEditor.WinUI,dotnet,MSBuild,vstest.console,testhost,java,javaw`.

## Public-Safe Boundaries

- No BEA.exe launch.
- No original game-install mutation.
- No private screenshots or media artifacts committed.
- No runtime Game Harness proof.
- No installer-grade release claim.

## Not Proven

- This wrapper does not replace focused runtime/media/package proofs.
- This wrapper does not prove trusted install/launch/uninstall.
- This wrapper does not guarantee unrelated user-owned MSBuild processes should be stopped outside the wrapper run.
