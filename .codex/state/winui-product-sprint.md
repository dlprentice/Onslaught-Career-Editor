# WinUI Product Sprint State

Status: in progress, first batch complete pending review
Last updated: 2026-05-04

## Scope

This sprint treats WinUI 3 as the primary user-facing Windows product lane. It does not reopen broad Electron product polish, does not turn Python into a product app, does not archive Electron/Python in the traditional sense, and does not move directories.

## Baseline

- Branch: `wip/sandbox`
- Start HEAD: `ace94b5b1d1f89812363fbd241d3cc30d96f572c`
- Start working tree: carried forward uncommitted WinUI lane health evidence/docs from the prior no-commit pass.
- Strategy truth: WinUI is the product lane; Electron remains shelved maintainer/agentic RE infrastructure; active Python scripts remain RE/tooling/lab support; the historical Python GUI/CLI app and WPF remain archived/reference.

## First Batch

- Updated WinUI shell copy to describe the app as the primary Windows toolkit.
- Renamed visible navigation from `Saves` to `Save Lab` and from `Binary Patches` to `Patch Bench`.
- Renamed the Save Lab page title and status prefix so the shell and page agree.
- Changed the footer game directory display to show a friendly folder label while preserving the full path in a tooltip.
- Rewrote About page copy so it no longer claims WinUI is a legacy reference or Electron is the active product direction.
- Reworked Patch Bench to treat retail `BEA.exe` as a read-only source and require an app-owned working copy before verification, apply, or restore.
- Added focused UiTests that guard WinUI product-lane copy and Patch Bench copied-executable safety.

## Product Code

Product code was modified in the WinUI lane only:

- `OnslaughtCareerEditor.WinUI/MainWindow.xaml`
- `OnslaughtCareerEditor.WinUI/MainWindow.xaml.cs`
- `OnslaughtCareerEditor.WinUI/Pages/AboutPage.xaml`
- `OnslaughtCareerEditor.WinUI/Pages/BinaryPatchesPage.xaml`
- `OnslaughtCareerEditor.WinUI/Pages/BinaryPatchesPage.xaml.cs`
- `OnslaughtCareerEditor.WinUI/Pages/SettingsPage.xaml`

No Electron UI/product code, Python tooling, AppCore patch semantics, IPC contracts, job IDs, schema IDs, or release scope were changed.

## Validation So Far

- `dotnet build .\OnslaughtCareerEditor.WinUI\OnslaughtCareerEditor.WinUI.csproj --nologo`: PASS/WARN, preview SDK info only.
- `dotnet test .\OnslaughtCareerEditor.UiTests\OnslaughtCareerEditor.UiTests.csproj --nologo --filter "FullyQualifiedName!~LegacyWpf"`: PASS/WARN, `26/26` passed after adding WinUI product-lane tests.
- `dotnet test .\OnslaughtCareerEditor.AppCore.Tests\OnslaughtCareerEditor.AppCore.Tests.csproj --nologo`: PASS/WARN, `19/19`.
- Docs, markdown links, repo hygiene, public allowlist, release profile snapshot, curated manifest, state JSON parse, and diff hygiene checks pass after regenerating stale release/profile artifacts.

## Remaining Work Before Sprint Close

- Consider manual WinUI launch/visual smoke if the desktop session supports it.
- Continue product sprinting only with focused WinUI changes; avoid importing broad Electron workflows.
- Public WinUI release inclusion remains deferred until build/license/dependency/public-safety review.
