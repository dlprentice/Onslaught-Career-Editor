# Onslaught Toolkit Release Notes

Status: active release note
Last updated: 2026-06-24

This file describes the current source-release and public-safety posture. The repo is WinUI-first for the user-facing Windows product. Electron, WPF, and the old Python GUI/CLI parity app are archived/reference surfaces.

Contributor setup, local validation expectations, and hard-payload contribution
boundaries are in [CONTRIBUTING.md](CONTRIBUTING.md). Asset-leak,
copied-executable, and vulnerability reporting guidance is in
[SECURITY.md](SECURITY.md). Source sign-off commands are in
[PUBLIC_SIGNOFF_COMMANDS.md](release/readiness/PUBLIC_SIGNOFF_COMMANDS.md). A
validated source tree is not automatically a GitHub Release; portable ZIP
publication, source pushes, signing, installer release, and announcement are
separate maintainer actions.

## Downloadable App Releases

Current downloadable app releases use an unsigned portable Windows x64 ZIP
attached to GitHub Releases with a SHA-256 checksum sidecar. Extract the full
ZIP and run `Launch Onslaught Toolkit.cmd` from the clean top-level folder. The
self-contained WinUI payload lives under `app\`; run
`app\OnslaughtCareerEditor.WinUI.exe` only as a fallback.

The ZIP release does not include Battle Engine Aquila game files, copied
executables, saves, media payloads, full Ghidra databases, or bulky generated
proof captures. Users provide their own retail/Steam installation, and mutating
workflows operate on copied files or safe game copies. This is not an MSIX,
installer, Store package, signed release, or SmartScreen/reputation claim.

## Shipping Direction

Active product/runtime surfaces:

- `OnslaughtCareerEditor.WinUI` - primary user-facing Windows product lane
- `OnslaughtCareerEditor.AppCore` - shared correctness/core support for the Windows lane
- `OnslaughtCareerEditor.Cli` - C# analyzer/patcher CLI support lane
- `OnslaughtCareerEditor.AppCore.Tests` and `OnslaughtCareerEditor.UiTests` - active regression/static/launch-smoke coverage
- Python scripts under `tools/` - RE/tooling/lab support, not a product GUI lane

Archived non-shipping app/reference surfaces:

- `archive/electron-workbench/` - former Electron/React/TypeScript workbench, TypeScript contracts, TypeScript CLI, and Electron bundle helpers
- `archive/legacy-python/` - historical Python GUI/CLI parity app
- `archive/legacy-wpf/` - historical WPF app
- `archive/legacy-winui-release/` - historical WinUI portable-bundle helpers

The source repo is the working repo, not a small exported subset. It includes
WinUI/AppCore/C# CLI/docs/tooling source, archived reference lanes, RE notes,
runtime proof summaries, state batons, readiness notes, and project history.
Ignored local overlays are for hard payloads: game binaries/assets, copied
runtime output, full Ghidra databases/backups, secrets, build outputs, and bulky
generated captures. Signed installer-grade WinUI packaging remains a separate
future proof, not a current public claim.

## Quick Start

From repo root:

```powershell
dotnet build ".\OnslaughtCareerEditor.WinUI\OnslaughtCareerEditor.WinUI.csproj" --nologo
dotnet test ".\OnslaughtCareerEditor.AppCore.Tests\OnslaughtCareerEditor.AppCore.Tests.csproj" --nologo
dotnet test ".\OnslaughtCareerEditor.UiTests\OnslaughtCareerEditor.UiTests.csproj" --nologo --filter "FullyQualifiedName!~LegacyWpf"
npm run test:winui-primary-lane
dotnet run --project ".\OnslaughtCareerEditor.Cli\OnslaughtCareerEditor.Cli.csproj" -- --help
```

## Lane Validation Gates

Maintainer validation can include:

```powershell
dotnet build ".\OnslaughtCareerEditor.WinUI\OnslaughtCareerEditor.WinUI.csproj" --nologo
dotnet publish ".\OnslaughtCareerEditor.WinUI\OnslaughtCareerEditor.WinUI.csproj" -c Release -r win-x64 --self-contained true -o ".\<ignored-scratch-root>\winui-publish-smoke\<scratch-stamp>\publish" --nologo
dotnet build ".\OnslaughtCareerEditor.Release.slnx" --nologo
dotnet test ".\OnslaughtCareerEditor.AppCore.Tests\OnslaughtCareerEditor.AppCore.Tests.csproj" --nologo
dotnet test ".\OnslaughtCareerEditor.UiTests\OnslaughtCareerEditor.UiTests.csproj" --nologo --filter "FullyQualifiedName!~LegacyWpf"
npm run test:winui-primary-lane
dotnet run --project ".\OnslaughtCareerEditor.Cli\OnslaughtCareerEditor.Cli.csproj" -- --help
npm run test:winui-installer-preflight
npm run test:winui-zip-package-probe
npm run test:winui-zip-release-candidate-probe
npm run test:doc-commands
npm run test:md-links
npm run test:hard-payload-safety
npm run test:public-allowlist
npm run test:repo-hygiene
```

Run only the gates relevant to the change. `npm run test:md-links` may write
generated reports under `subagents/md-link-check`; those reports are validation
artifacts, not app release payload. Archived Electron checks are reference
checks only, not product release gates.

Source-tree safety gates:

<!-- public-package-commands:start -->
```powershell
npm run test:doc-commands
npm run test:md-links
npm run test:hard-payload-safety
npm run test:public-allowlist
npm run test:repo-hygiene
npm run test:winui-notices
```
<!-- public-package-commands:end -->

For the authoritative source validation order, use
[PUBLIC_SIGNOFF_COMMANDS.md](release/readiness/PUBLIC_SIGNOFF_COMMANDS.md).
Generated release accounting is owned by
`py -3 tools\release_profile_snapshot.py --check` and
`py -3 tools\release_curated_manifest.py --check` when those accounting inputs
change; do not copy stale count literals from old prose. The
`test:hard-payload-safety` gate checks for tracked hard payloads and obvious
secrets, while `test:public-allowlist` currently aliases that payload boundary
for compatibility with older command docs.

## Archive Posture

`archive/electron-workbench/release/Build-ElectronBundle.ps1` and related
scripts are retained only so the archived Electron workbench can be inspected
later. They must not be treated as the community product release path.

## Maintainer Notes

- WinUI 3 is the product UX focus.
- Root `package.json`, `AGENTS.md`, `CONTRIBUTING.md`,
  `release/readiness/PUBLIC_SIGNOFF_COMMANDS.md`, and this file are the
  current source-repo entrypoints.
- `release/readiness/curated_release_manifest.json` and
  `release/readiness/public_candidate_allowlist.tsv` remain useful accounting
  artifacts, but they no longer define a small public export as the working
  source of truth.
- Keep `game/**`, copied executables, private media/input payloads, local saves,
  full Ghidra databases/backups, secrets, build outputs, screenshots/frame
  dumps, raw CDB logs, and copied runtime payloads out of git and app release
  ZIPs.
- Halt broad Electron, Python GUI, and WPF product work. Port only narrow, reviewed logic into WinUI/AppCore/tools if needed.
