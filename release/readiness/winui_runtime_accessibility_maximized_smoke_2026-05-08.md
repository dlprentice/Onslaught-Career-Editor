# WinUI Runtime Accessibility Maximized Smoke - 2026-05-08

Status: public-safe native UI Automation proof update
Date: 2026-05-08
Branch: `wip/sandbox`

## Purpose

Align the native runtime accessibility smoke with the current workstation lesson that WinUI UIA and visual runs should maximize the app window by default. This keeps shell-navigation accessibility proof closer to real laptop use, where important sections can otherwise sit outside the first viewport.

This pass does not redesign the WinUI app. It only tightens the test harness so the existing shell-navigation accessibility smoke maximizes the launched WinUI window unless `ONSLAUGHT_WINUI_VISUAL_CAPTURE_MAXIMIZE=0` or `false` is set.

## Implementation Summary

- Added a source guard in `WinUiProductLaneTests.RuntimeAccessibilitySmoke_MaximizesWindowByDefault`.
- Updated `WinUiRuntimeAccessibilitySmokeTests` to call `MaximizeForRuntimeSmoke(app.MainWindowHandle)` after the main window is available.
- The helper uses `ShowWindow(..., SW_MAXIMIZE)` and `SetForegroundWindow(...)`, matching the existing native visual-smoke posture.
- The helper honors `ONSLAUGHT_WINUI_VISUAL_CAPTURE_MAXIMIZE` so constrained environments can still opt out.

## Validation

| Command | Result | Important output | What it proves |
| --- | --- | --- | --- |
| `dotnet test .\OnslaughtCareerEditor.UiTests\OnslaughtCareerEditor.UiTests.csproj --nologo --filter "FullyQualifiedName~WinUiProductLaneTests.RuntimeAccessibilitySmoke_MaximizesWindowByDefault"` before implementation | FAIL, expected red | Source guard failed on missing `MaximizeForRuntimeSmoke(app.MainWindowHandle);`. | Confirms the guard failed for the intended missing maximize behavior before the smoke was changed. |
| `dotnet test .\OnslaughtCareerEditor.UiTests\OnslaughtCareerEditor.UiTests.csproj --nologo --filter "FullyQualifiedName~WinUiProductLaneTests.RuntimeAccessibilitySmoke_MaximizesWindowByDefault"` after implementation | PASS | `1/1` passed. | Confirms the source guard sees the maximize helper, environment opt-out, and user32 calls. |
| `dotnet build .\OnslaughtCareerEditor.WinUI\OnslaughtCareerEditor.WinUI.csproj --nologo` | PASS | Build succeeded with `0` warnings and `0` errors. | Confirms the current WinUI executable is freshly built before native UIA smoke. |
| `dotnet test .\OnslaughtCareerEditor.UiTests\OnslaughtCareerEditor.UiTests.csproj --nologo --filter "FullyQualifiedName~WinUiRuntimeAccessibilitySmokeTests"` | PASS | `1/1` passed. | Confirms the real native runtime accessibility smoke still drives named, enabled shell navigation after the window is maximized. |
| `dotnet test .\OnslaughtCareerEditor.UiTests\OnslaughtCareerEditor.UiTests.csproj --nologo --filter "FullyQualifiedName~WinUiProductLaneTests"` | PASS | `16/16` passed. | Confirms broader WinUI product-lane source guards remain green. |
| `cmd.exe /c npm run test:md-links` | PASS | Markdown link check passed. | Confirms this evidence note and checklist links resolve. |
| `cmd.exe /c npm run test:doc-commands` | PASS | Documented npm commands checked `1359`. | Confirms documented command references remain synchronized. |
| `py -3 tools\docsync_check.py` | PASS | Docsync policy check passed. | Confirms protected mirrors remain synchronized. |
| `cmd.exe /c npm run test:repo-hygiene` | PASS | Hygiene unit tests `29/29`; live repo hygiene PASS. | Confirms the wording avoids stale/private wording guards. |
| `py -3 tools\release_curated_manifest.py` and `py -3 tools\release_curated_manifest.py --check` | PASS | Selected files `1421`. | Confirms this public-safe evidence note is in curated release accounting. |
| `py -3 tools\release_profile_snapshot.py` and `py -3 tools\release_profile_snapshot.py --check` | PASS | Counts `R0=1486 R2=0 R3=2 R4=18188`. | Confirms release profile outputs are synchronized. |
| `cmd.exe /c npm run test:public-allowlist` | PASS | Rows checked `1421`. | Confirms public allowlist safety remains intact. |
| State/manifest JSON parse | PASS | `json ok`. | Confirms state files and curated manifest remain valid JSON. |
| `git diff --check` and `git diff --cached --check` | PASS | No whitespace errors. | Confirms working and staged diffs are whitespace-clean. |
| Process cleanup check | PASS | `process cleanup ok`. | Confirms no `BEA`, CDB, Ghidra, headless Ghidra, WinUI, `testhost`, or `dotnet` process remained after this wave. |

## Boundaries

- No product UI layout, user-facing copy, game file, save file, `BEA.exe`, Ghidra project, or release package was changed.
- No screenshots, private paths, private proof JSON, generated packages, copied executables, or game assets are included in this report.
- This remains UI Automation shell-navigation proof. It does not claim full screen-reader review, tab-order review, high-contrast certification, manual Accessibility Insights certification, or visual approval of every scrolled surface.
