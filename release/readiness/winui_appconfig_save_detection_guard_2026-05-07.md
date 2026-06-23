# WinUI AppConfig Save Detection Guard - 2026-05-07

Status: pass

Source/evidence commit: 7918f9147f48c78c1e2538d40cd68602a89a5e9a

## Objective

Add focused AppCore coverage for the configuration/save discovery behavior used by WinUI first-run setup, Settings, and Save Lab.

## Change

- Added an AppConfig unit test that creates a disposable game-like directory.
- The test verifies discovery of:
  - root `defaultoptions.bea`
  - `savegames/*.bes`
  - invalid/corrupt `.bea` rows marked as not valid
- The test uses synthetic temporary files with the known save/options buffer size and version word. It does not read or mutate the user's installed game.

## Commands

```powershell
dotnet test .\OnslaughtCareerEditor.AppCore.Tests\OnslaughtCareerEditor.AppCore.Tests.csproj --nologo --filter "FullyQualifiedName~AppConfigTests"
```

Result: pass

Important output:

```text
Passed! - Failed: 0, Passed: 2, Skipped: 0, Total: 2
```

```powershell
dotnet test .\OnslaughtCareerEditor.AppCore.Tests\OnslaughtCareerEditor.AppCore.Tests.csproj --nologo
```

Result: pass

Important output:

```text
Passed! - Failed: 0, Passed: 29, Skipped: 0, Total: 29
```

## What It Proves

- AppConfig still honors the isolated config-root test path used by WinUI smokes.
- Save discovery includes both global options and career-save locations relevant to the Steam build.
- Invalid save/options-shaped filenames remain visible as rows but are marked invalid by AppCore validation.

## What Did Not Change

- No WinUI product UI changed.
- No installed game files were read or mutated.
- No original `BEA.exe` was patched.
- No archived Electron/WPF/Python app lane was reactivated.
