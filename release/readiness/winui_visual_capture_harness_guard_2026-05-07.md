# WinUI Visual Capture Harness Guard - 2026-05-07

Status: pass

Source/evidence commit: 7e65a01b91e0b5a6366557878e2f622cead3592d
Release-profile commit: 949aba3082ed1d5b8c0f89278d45f11e9a0fec40

## Objective

Harden the native WinUI visual smoke evidence after a local screenshot review found that OS notifications can overlap `window.CaptureToFile(...)` output. The app UI was not the issue, but contaminated screenshots weaken visual evidence.

## Change

- The broad WinUI visual smoke now normalizes the app window to a deterministic top-left capture rectangle before each screenshot.
- Default capture size is `1000x640`, with `ONSLAUGHT_WINUI_VISUAL_CAPTURE_WIDTH` and `ONSLAUGHT_WINUI_VISUAL_CAPTURE_HEIGHT` overrides for larger review passes.
- This changes only the UI test harness and ignored private screenshot output. It does not change WinUI product code or runtime behavior.

## Commands

```powershell
dotnet test .\OnslaughtCareerEditor.UiTests\OnslaughtCareerEditor.UiTests.csproj --nologo --filter "FullyQualifiedName~WinUiVisualSmokeTests.MainWindow_CapturesPrimaryProductScreens"
```

Working directory:

```text
repo root
```

Result: pass

Important output:

```text
Passed! - Failed: 0, Passed: 1, Skipped: 0, Total: 1, Duration: 53 s
```

What it proves:

- the WinUI app still launches repeatedly through the visual-smoke harness
- primary product screenshots regenerate after the capture-window normalization change
- ignored screenshots under `ignored local visual QA artifact folder` are no longer dependent on a full-width/full-height desktop window that can be covered by lower-right OS toasts

## Screenshot Review

Reviewed regenerated `09-settings.png` locally. The screenshot shows the WinUI Settings page inside the normalized capture rectangle without the earlier lower-right OS notification artifact.

Screenshots remain ignored/private and are not embedded in this public-safe report.

## What Did Not Change

- No WinUI product XAML or runtime behavior changed.
- No game files were launched or mutated.
- No installed `BEA.exe` was patched.
- No private screenshots were committed.
- No archived Electron/WPF/Python app lane was reactivated.
