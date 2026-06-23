# WinUI AppConfig Normalization Guard - 2026-05-07

Status: pass
Source/evidence commit: b53698062c470faac405044c053389adcedbbed6

## Objective

Prevent malformed user-local configuration from destabilizing the primary WinUI shell or recent-file handling.

## Product Change

- `AppConfig.Load()` now normalizes deserialized config before use.
- `AppConfig.Save()` and `AddRecentFile()` also normalize before writing or mutating recent-file state.
- Malformed `recentFiles: null`, negative `maxRecentFiles`, and unusable window dimensions are repaired at the AppCore boundary.
- The WinUI shell now reuses AppCore window-bound constants instead of duplicating the numeric limits.

## Commands

```powershell
dotnet test .\OnslaughtCareerEditor.AppCore.Tests\OnslaughtCareerEditor.AppCore.Tests.csproj --nologo --filter "FullyQualifiedName~AppConfigTests"
```

Result: pass

Important output:

```text
Passed! - Failed: 0, Passed: 3, Skipped: 0, Total: 3
```

```powershell
dotnet build .\OnslaughtCareerEditor.WinUI\OnslaughtCareerEditor.WinUI.csproj --nologo
```

Result: pass

Important output:

```text
Build succeeded. 0 Warning(s), 0 Error(s)
```

```powershell
dotnet test .\OnslaughtCareerEditor.UiTests\OnslaughtCareerEditor.UiTests.csproj --nologo --filter "FullyQualifiedName~WinUiProductLaneTests.ShellWindowSize_UsesPersistedNativeAppWindowBounds"
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
Build succeeded. 0 Warning(s), 0 Error(s)
Passed! - Failed: 0, Passed: 30, Skipped: 0, Total: 30
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

- This is a local configuration robustness guard, not a release installer proof.
- No private game files, copied saves, copied executables, media payloads, screenshots, or proof JSON were committed.
- The local Battle Engine Aquila install remained read-only.
