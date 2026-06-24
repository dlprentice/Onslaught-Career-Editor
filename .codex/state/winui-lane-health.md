# WinUI Lane Health State

Status: complete pending review
Last updated: 2026-05-04

## Scope

This pass assessed WinUI 3 lane health after the three-lane strategy reset. It did not redesign UX, migrate features from Electron, modify Electron product code, modify Python tooling, move directories, expand public release scope, or commit.

## Baseline

- Branch: `wip/sandbox`
- Start HEAD: `ace94b5b1d1f89812363fbd241d3cc30d96f572c`
- Start working tree: clean
- Strategy truth: WinUI 3 is primary user-facing Windows product lane; Electron is shelved maintainer/agentic RE infrastructure; active Python scripts are RE/tooling/lab support; the historical Python GUI/CLI app and WPF are archived/reference only.

## Commands Identified

Build:

```powershell
dotnet build .\OnslaughtCareerEditor.WinUI\OnslaughtCareerEditor.WinUI.csproj --nologo
```

Run:

```powershell
dotnet run --project .\OnslaughtCareerEditor.WinUI\OnslaughtCareerEditor.WinUI.csproj
```

Core tests:

```powershell
dotnet test .\OnslaughtCareerEditor.AppCore.Tests\OnslaughtCareerEditor.AppCore.Tests.csproj --nologo
```

UI/static tests:

```powershell
dotnet test .\OnslaughtCareerEditor.UiTests\OnslaughtCareerEditor.UiTests.csproj --nologo --filter "FullyQualifiedName!~LegacyWpf"
```

Existing C# parity/support solution:

```powershell
dotnet build .\OnslaughtCareerEditor.Release.slnx --nologo
```

## Solution Posture

`OnslaughtCareerEditor.Release.slnx` remains a C# parity/support solution. It references AppCore, AppCore.Host, AppCore.Tests, C# CLI, and UiTests. It intentionally does not include `OnslaughtCareerEditor.WinUI`.

No solution structure change was made. The WinUI project builds directly, and the release support solution also builds. Adding WinUI to `OnslaughtCareerEditor.Release.slnx` is not required to make this lane verifiable. A separate Windows-lane solution can be considered later if it improves developer ergonomics, but it is not a health blocker.

## Results

- WinUI build: PASS.
- AppCore tests: PASS, 19/19.
- UiTests filtered away from legacy WPF explicit tests: PASS, 21/21.
- Existing release support solution build: PASS.
- WinUI run command: identified and documented; not launched because this health pass did not require UI launch proof.

## Warnings

- .NET emitted `NETSDK1057` informational messages because the installed SDK is preview `10.0.300-preview.0.26177.108`. Builds/tests still exited 0 with no project warnings or errors.

## Product Code

No product code was modified.

## Documentation Updates

- Root and capability docs now show the passing WinUI build/test baseline.
- UI test command docs now use the filtered active-lane command: `--filter "FullyQualifiedName!~LegacyWpf"`.
- The WinUI run command is documented in active docs.
- Strategy docs now point to this health evidence before the next WinUI product sprint.

## Remaining Risks

- The WinUI app was not launched or visually smoke-tested in this pass.
- Some visible WinUI copy may still reflect older strategy language. For example, the About page should be reviewed during the WinUI UX/product sprint.
- No public WinUI packaging or release-inclusion review was performed.
- No feature parity assessment against Electron was performed.

## Next Classification

Next step: WinUI UX/product sprint, not WinUI build stabilization.

Build stabilization is not currently blocked because the WinUI build and relevant AppCore/UI test gates pass.
