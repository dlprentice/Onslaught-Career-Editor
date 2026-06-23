# WinUI Scroll Surface Accessibility Guard - 2026-05-07

Status: pass
Source/evidence commit: 4fca10c5b35168b670189c4267ae0690ee136a92

## Objective

Make long WinUI page and workflow scroll areas explicitly targetable by UI Automation so runtime smokes and screenshot reviews can distinguish first-viewport evidence from scrolled-section evidence.

## Change

- Added stable automation IDs and human accessible names to long-page ScrollViewer surfaces on Home, Save Lab, Asset Library, Patch Bench, Settings, and About.
- Added a source-level UiTests guard that fails if the named long-page scroll surfaces lose their AutomationId/Name pair.
- This is a testability/accessibility hardening change only; it does not redesign layouts or alter runtime save/media/patch behavior.

## Commands

```powershell
dotnet test .\OnslaughtCareerEditor.UiTests\OnslaughtCareerEditor.UiTests.csproj --nologo --filter "FullyQualifiedName~WinUiAccessibilityAuditTests.LongWinUiScrollSurfaces_ExposeAutomationIdsAndNames"
```

Result: pass

Important output:

```text
Passed! - Failed: 0, Passed: 1, Skipped: 0, Total: 1
```

```powershell
npm run test:winui-primary-lane
```

Result: pass

Important output:

```text
dotnet build OnslaughtCareerEditor.WinUI.slnx: Build succeeded, 0 warnings, 0 errors
AppCore tests: Passed 30/30
Active UiTests: Passed 47/47
dotnet build-server shutdown: compiler and MSBuild servers shut down successfully
process cleanup check: none
```

```powershell
git diff --check
```

Result: pass

Important output:

```text
exit 0 with LF/CRLF working-copy warnings for generated TSV files only
```

## Evidence Boundary

- This is a WinUI source/testability change, not runtime proof.
- No private screenshots, copied executables, copied saves, media files, runtime proof JSON, or original game install files were committed.
- No Electron, WPF, or old Python GUI/CLI app lane was reactivated.
