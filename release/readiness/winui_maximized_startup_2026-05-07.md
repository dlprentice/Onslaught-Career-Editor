# WinUI Maximized Startup Evidence - 2026-05-07

## Scope

This pass made the primary WinUI product window start maximized by default. The goal is to give users and visual automation the broadest practical workspace on launch without changing page layout or redesigning screens.

## Product Change

- `App.OnLaunched` now activates `MainWindow` and then calls `MaximizeForUserWorkspace()`.
- `MainWindow.MaximizeForUserWorkspace()` uses the native WinUI `OverlappedPresenter` to maximize the app window.
- The existing persisted window-size code remains in place as a bounded size fallback and close-time record, but the default session workspace is maximized.

## Commands

```powershell
dotnet build OnslaughtCareerEditor.WinUI/OnslaughtCareerEditor.WinUI.csproj --nologo
```

Result: PASS

Important output:

```text
Build succeeded.
0 Warning(s)
0 Error(s)
```

```powershell
dotnet test OnslaughtCareerEditor.UiTests/OnslaughtCareerEditor.UiTests.csproj --nologo --filter FullyQualifiedName~MainWindow_LaunchesAndShowsWinUiProductChrome
```

Result: PASS

Important output:

```text
Passed!  - Failed: 0, Passed: 1, Skipped: 0, Total: 1
```

The launch smoke now asserts the live UIA window state is `Maximized`.

```powershell
dotnet test OnslaughtCareerEditor.UiTests/OnslaughtCareerEditor.UiTests.csproj --nologo --filter FullyQualifiedName~WinUiProductLaneTests
```

Result: PASS

Important output:

```text
Passed!  - Failed: 0, Passed: 14, Skipped: 0, Total: 14
```

## What This Proves

- The WinUI app still builds.
- The product-lane static tests recognize the maximize startup hook.
- The live desktop launch smoke verifies the app starts with a maximized window state.
- The app process was closed by the smoke harness after the test.

## What This Does Not Prove

- It does not replace scrolled-section screenshots. Long pages still need explicit UIA scrolling for below-viewport proof.
- It does not prove narrow-window responsive behavior.
- It does not change any archived Electron/WPF/Python app lane.
