# WinUI Lane Solution - 2026-05-06

Status: pass

Source commit: 26908d3a
Evidence-report commit: eed7d507fda5697cbcaa7bdac261e3aee27a8bcf

## Objective

Add an obvious solution-level entrypoint for the primary WinUI product lane without changing archive/reference app posture or overloading the existing C# release-support solution.

## Change

Created:

```text
OnslaughtCareerEditor.WinUI.slnx
```

The solution includes:

- `OnslaughtCareerEditor.WinUI`
- `OnslaughtCareerEditor.AppCore`
- `OnslaughtCareerEditor.AppCore.Tests`
- `OnslaughtCareerEditor.UiTests`
- `OnslaughtCareerEditor.Cli`

The existing `OnslaughtCareerEditor.Release.slnx` remains a C# support/parity solution and still includes AppCore, AppCore.Host, AppCore.Tests, C# CLI, and UiTests. It was not repurposed into the primary product solution.

## Validation

Command:

```powershell
dotnet build .\OnslaughtCareerEditor.WinUI.slnx --nologo
```

Working directory:

```text
repo root
```

Result: pass

Important output:

```text
OnslaughtCareerEditor.AppCore -> ...\OnslaughtCareerEditor.AppCore.dll
OnslaughtCareerEditor.UiTests -> ...\OnslaughtCareerEditor.UiTests.dll
OnslaughtCareerEditor.Cli -> ...\OnslaughtCareerEditor.Cli.dll
OnslaughtCareerEditor.AppCore.Tests -> ...\OnslaughtCareerEditor.AppCore.Tests.dll
OnslaughtCareerEditor.WinUI -> ...\OnslaughtCareerEditor.WinUI.dll
Build succeeded.
0 Warning(s)
0 Error(s)
```

What it proves:

- the WinUI app, AppCore, UI tests, AppCore tests, and C# support CLI can be restored and built through one primary-lane solution
- WinUI product development no longer has to rely only on a raw project path or a support/parity solution
- archived Electron, WPF, old Python GUI/CLI, and legacy WinUI release helpers remain outside the primary solution

## Documentation Updates

- README quick start now shows the WinUI lane solution build command.
- Release scope and local sign-off docs now include the WinUI lane solution as the product-lane aggregate build.
- Repo structure map distinguishes `OnslaughtCareerEditor.WinUI.slnx` from `OnslaughtCareerEditor.Release.slnx`.
- AGENTS quick commands now include the product-lane solution build.

## Safety Notes

- No app behavior changed.
- No archived app lane was reactivated.
- No private assets, saves, media, screenshots, or runtime proof were committed.
- No installed game files were read or mutated by this build.
