# WinUI Scrolled Visual QA Maximized - 2026-05-07

Status: pass
Source/evidence commit: c4bb7f76e3c1401d0be63e44b8d2dfd2c6f2cfc9

## Objective

Capture native WinUI visual evidence for long/scrolled workflow sections with the app maximized, so the review covers more than first-viewport page shells.

## Change

- Added `WinUiVisualSmokeTests.MainWindow_CapturesScrolledWorkflowSections`.
- The visual smoke now maximizes the app window by default before screenshot capture.
- Fixed-size capture remains available by setting `ONSLAUGHT_WINUI_VISUAL_CAPTURE_MAXIMIZE=0`.
- Scrolled-section screenshots are written only under ignored `subagents/winui-scrolled-visual-qa/2026-05-07/`.

## Private Screenshot Set

Screenshots were captured locally and remain ignored/private:

| Screenshot | Result | Visible note |
| --- | --- | --- |
| `01-home-scrolled.png` | pass | Maximized Home shows all primary task cards without cramped first-viewport pressure. |
| `02-save-editor-scrolled.png` | pass | Save Editor lower workflow shows patch summary and patch output at native width. |
| `03-configuration-editor-scrolled.png` | yellow | Configuration Editor lower workflow is readable, but the no-file-selected configuration area leaves a large blank region before the patch summary. |
| `04-asset-preview-scrolled.png` | pass | Asset Library preview/actions are visible at native width with fixture texture preview. |
| `05-patch-bench-scrolled.png` | pass | Patch Bench lower workflow shows selected patch groups, copy/actions column, and operation log without path leakage. |
| `06-settings-scrolled.png` | pass | Settings shows install summary, save-file summary, media toggles, and reload action without needing a tiny viewport. |
| `07-about-scrolled.png` | pass | About page shows capability, project, retail behavior, and version sections clearly. |

All PNGs were `1936x1048` and non-empty in the maximized capture run.

## Commands

```powershell
dotnet test .\OnslaughtCareerEditor.UiTests\OnslaughtCareerEditor.UiTests.csproj --nologo --filter "FullyQualifiedName~WinUiVisualSmokeTests.MainWindow_CapturesScrolledWorkflowSections"
```

Result: pass

Important output:

```text
Passed! - Failed: 0, Passed: 1, Skipped: 0, Total: 1
Captured 7 screenshots under subagents/winui-scrolled-visual-qa/2026-05-07/
process cleanup check: none
```

```powershell
npm run test:winui-primary-lane
```

Result: pass

Important output:

```text
WinUI solution build: Build succeeded, 0 warnings, 0 errors
AppCore tests: Passed 30/30
Active UiTests: Passed 47/47
dotnet build-server shutdown completed
```

```powershell
py -3 tools\release_profile_snapshot.py --check
py -3 tools\release_curated_manifest.py --check
npm run test:public-allowlist
node -e "<parse developer_agent_state.json and documentation_agent_state.json>"
git diff --check
```

Result: pass

Important output:

```text
Markdown link check: PASS
NPM script documentation check: PASS, 489 script references checked
Docsync policy check: PASS
Curated allowlist check: PASS
Release profile snapshot check: PASS
Public allowlist safety check: PASS, rows checked 1273
state json ok
git diff --check exit 0 with LF/CRLF working-copy warnings for generated TSV files only
process cleanup check: none
```

## Evidence Boundary

- This is native WinUI visual/test harness evidence, not runtime game proof.
- Private screenshots stay under ignored `subagents/` and are not committed.
- No private media, copied executable, copied save, original game file, or runtime proof JSON was committed.
- No Electron, WPF, or old Python GUI/CLI app lane was reactivated.
