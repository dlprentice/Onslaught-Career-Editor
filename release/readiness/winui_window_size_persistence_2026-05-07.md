# WinUI Window Size Persistence - 2026-05-07

Status: pass
Source/evidence commit: 4adbf7cd761293378eb0a4bd599e1ae0a492aed5

## Objective

Make the primary WinUI shell honor the existing `AppConfig.WindowWidth` and `AppConfig.WindowHeight` fields instead of leaving them as stale configuration data.

## Product Change

- Fresh configuration now defaults to an `1100x720` WinUI window, which is large enough for the main task shell while still fitting typical laptop displays.
- `MainWindow` resolves its native Windows App SDK `AppWindow`, applies persisted window dimensions on launch, and saves the current clamped window size when the window closes.
- Bounds are clamped to avoid unusably small or accidentally enormous persisted sizes.

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
dotnet test .\OnslaughtCareerEditor.UiTests\OnslaughtCareerEditor.UiTests.csproj --nologo --filter "FullyQualifiedName~WinUiProductLaneTests"
```

Result: pass

Important output:

```text
Passed! - Failed: 0, Passed: 13, Skipped: 0, Total: 13
```

```powershell
dotnet test .\OnslaughtCareerEditor.UiTests\OnslaughtCareerEditor.UiTests.csproj --nologo --filter "FullyQualifiedName~WinUiLaunchSmokeTests.MainWindow_LaunchesAndShowsWinUiProductChrome"
```

Result: pass

Important output:

```text
Passed! - Failed: 0, Passed: 1, Skipped: 0, Total: 1
```

```powershell
dotnet test .\OnslaughtCareerEditor.AppCore.Tests\OnslaughtCareerEditor.AppCore.Tests.csproj --nologo
```

Result: pass

Important output:

```text
Passed! - Failed: 0, Passed: 29, Skipped: 0, Total: 29
```

```powershell
npm run test:winui-primary-lane
```

Result: pass

Important output:

```text
dotnet build OnslaughtCareerEditor.WinUI.slnx: Build succeeded. 0 Warning(s), 0 Error(s)
dotnet test AppCore.Tests: Passed 29
dotnet test UiTests FullyQualifiedName!~LegacyWpf: Passed 45
dotnet build-server shutdown: completed
```

## What It Proves

- The WinUI app still builds after using the native `AppWindow` API.
- The product-lane static checks cover the new persisted-window behavior.
- The native desktop launch smoke still opens the app successfully.
- AppCore tests still pass after changing fresh-window defaults.
- The primary WinUI lane wrapper still passes and shuts down build servers after validation.

## What Did Not Change

- No game files were launched or mutated.
- No installed `BEA.exe` was patched.
- No archived Electron/WPF/Python app lane was reactivated.
- No release scope was expanded.
