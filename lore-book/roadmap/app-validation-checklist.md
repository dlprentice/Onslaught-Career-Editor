# App validation checklist

> **SUPERSEDED:** Use [RELEASE_SCOPE_AND_TEST_COMMANDS.md](/RELEASE_SCOPE_AND_TEST_COMMANDS.md), [three-lane-product-strategy.md](three-lane-product-strategy.md), and `npm run test:winui-primary-lane` for current gates.

Status: superseded
Last updated: 2026-05-07

This checklist is retained as historical context. Current lane validation is documented in [three-lane-product-strategy.md](three-lane-product-strategy.md), [RELEASE_SCOPE_AND_TEST_COMMANDS.md](/RELEASE_SCOPE_AND_TEST_COMMANDS.md), and [release/readiness/release_readiness_checklist.md](/release/readiness/release_readiness_checklist.md).

## Current lane gates

Run from repo root:

```powershell
dotnet build ".\OnslaughtCareerEditor.WinUI\OnslaughtCareerEditor.WinUI.csproj" --nologo
dotnet test ".\OnslaughtCareerEditor.AppCore.Tests\OnslaughtCareerEditor.AppCore.Tests.csproj" --nologo
dotnet test ".\OnslaughtCareerEditor.UiTests\OnslaughtCareerEditor.UiTests.csproj" --nologo --filter "FullyQualifiedName!~LegacyWpf"
npm run test:winui-primary-lane
npm run typecheck
npm run build
npm run test:cli-smoke
npm run test:doc-commands
npm run test:md-links
npm run test:public-allowlist
npm run test:repo-hygiene
py -3 tools\docsync_check.py
py -3 tools\release_profile_snapshot.py --check
py -3 tools\release_curated_manifest.py --check
```

When the archived Electron renderer is deliberately inspected, use the `archive:electron:*` commands. It is not a product gate.

## Temporary parity gate

Run while C# parity oracles remain:

```powershell
dotnet build ".\OnslaughtCareerEditor.Release.slnx"
dotnet test ".\OnslaughtCareerEditor.AppCore.Tests\OnslaughtCareerEditor.AppCore.Tests.csproj"
dotnet test ".\OnslaughtCareerEditor.UiTests\OnslaughtCareerEditor.UiTests.csproj" --filter "FullyQualifiedName!~LegacyWpf"
dotnet run --project ".\OnslaughtCareerEditor.Cli\OnslaughtCareerEditor.Cli.csproj" -- --help
```

Pass criteria:

- WinUI/AppCore gates pass before claiming Windows product health.
- Archived Electron checks pass only when that archive is deliberately inspected.
- C# support/parity gates pass until their covered behavior is retired.
- Docs identify WinUI 3 as the primary product lane, Electron/Python GUI/WPF as archived reference, and active Python scripts as lab/tooling support.

## WinUI smoke

The WinUI manual smoke belongs to the active Windows product lane, but do not require UI launch when the environment cannot display the app:

```powershell
dotnet run --project ".\OnslaughtCareerEditor.WinUI\OnslaughtCareerEditor.WinUI.csproj"
```

WinUI lane health is currently green. Use this smoke command for manual/visual review during WinUI product sprints.
