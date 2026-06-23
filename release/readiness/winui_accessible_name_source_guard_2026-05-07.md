# WinUI Accessible Name Source Guard - 2026-05-07

Status: pass
Source/evidence commit: 3ce299c9904e71d0e61e67abea5fdb3502fd483b

## Objective

Tighten the WinUI automation/accessibility surface so laptop-sized and scrolled workflows remain testable through UI Automation and expose useful names to assistive technology.

## Product Change

- Added accessible names to library/list controls, media progress and volume sliders, readonly output logs, and repeated patch/save row controls that previously relied on visual context alone.
- Added a source-XAML guard requiring interactive WinUI controls to expose a human name source through content, header, placeholder text, or `AutomationProperties.Name`.
- No visual layout, backend behavior, release scope, game runtime behavior, or archived Electron/WPF/Python lane was changed.

## Commands

```powershell
dotnet build .\OnslaughtCareerEditor.WinUI\OnslaughtCareerEditor.WinUI.csproj --nologo
```

Result: pass

Important output:

```text
Build succeeded. 0 Warning(s), 0 Error(s)
```

```powershell
dotnet test .\OnslaughtCareerEditor.UiTests\OnslaughtCareerEditor.UiTests.csproj --nologo --filter "FullyQualifiedName~WinUiAccessibilityAuditTests"
```

Result: pass

Important output:

```text
Passed! - Failed: 0, Passed: 7, Skipped: 0, Total: 7
```

```powershell
npm run test:winui-primary-lane
```

Result: pass

Important output:

```text
Build succeeded. 0 Warning(s), 0 Error(s)
Passed! - Failed: 0, Passed: 29, Skipped: 0, Total: 29
Passed! - Failed: 0, Passed: 46, Skipped: 0, Total: 46
dotnet build-server shutdown completed
```

```powershell
Get-Process -Name OnslaughtCareerEditor.WinUI,dotnet,MSBuild,vstest.console,testhost,java,javaw -ErrorAction SilentlyContinue
```

Result: pass

Important output:

```text
none
```

```powershell
py -3 tools\release_profile_snapshot.py --check
py -3 tools\release_curated_manifest.py --check
npm run test:public-allowlist
npm run test:md-links
npm run test:doc-commands
git diff --check
node -e "<parse developer_agent_state.json and documentation_agent_state.json>"
```

Result: pass

Important output:

```text
Release profile snapshot check: PASS
Curated allowlist check: PASS
Public allowlist safety check: PASS
Markdown link check: PASS
NPM script documentation check: PASS
git diff --check exit 0; line-ending warnings only
state json ok
```

## Evidence Boundary

- This is a source/testability guard, not a runtime proof.
- No screenshots, private media, game files, copied saves, copied executables, or proof JSON were committed.
- The local Battle Engine Aquila install remained read-only.
