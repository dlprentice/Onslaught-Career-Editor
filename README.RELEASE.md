# Onslaught Toolkit Release Notes

Status: active release note
Last updated: 2026-07-05

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
`app\OnslaughtCareerEditor.WinUI.exe` only as a fallback. The `v1.0.8` package
was superseded by `v1.0.9`, which bundles a generated short-path `lore-pack/`
with 949 tracked Markdown/TXT documents selected from Lore, roadmap, and
technical RE material, rewrites unbundled source links to GitHub source/search
pages, and verifies the exact ZIP with
Explorer-safe entry paths, packaged-Lore copy truth, extracted launch, Home,
Lore, representative Media UI smokes, and process cleanup. The `v1.0.9` ZIP
SHA-256 is
`e09439c40a4ff7197c4151e18651388b2515a71950ea2479b01266c00d918519`, published
beside its checksum sidecar. v1.0.9 also adds clearer first-time-user labels
for write/copy/shell actions and confirmation before the toolkit closes or
force-stops a managed copied-game process. `v1.0.7` superseded
`v1.0.3`/`v1.0.4`/`v1.0.5`/`v1.0.6`, and `v1.0.8` superseded `v1.0.7` with the
949-document Lore pack: v1.0.3 could hit Windows Explorer
`0x80010135` path-too-long extraction failures under normal Downloads paths,
v1.0.4 did not rewrite deeper unbundled Lore links, v1.0.5 did not yet surface
the source-link boundary clearly inside the app, and v1.0.6 did not yet include
the generated broad offline Lore content pack.

The 949 count records packaged breadth. It does not prove narrative
completeness, editorial quality, freshness, provenance/rights review, or that
every technical/archive document belongs in a future reader-facing pack.

`release/readiness/WINUI-ZIP-README.txt` describes ZIPs built from the current
source candidate. The published `v1.0.7` asset is documented historically by
`release/readiness/winui_zip_release_v1_0_7_2026-06-25.md`.
The published `v1.0.8` asset is documented by
`release/readiness/winui_zip_release_v1_0_8_2026-07-04.md`.
The published `v1.0.9` asset is documented by
`release/readiness/winui_zip_release_v1_0_9_2026-07-05.md`.

The ZIP release does not include Battle Engine Aquila game files, copied
executables, saves, media payloads, full Ghidra databases, or bulky generated
proof captures. Users provide their own retail/Steam installation, and mutating
workflows operate on copied files or safe game copies. The current published
portable ZIP stages a generated short-path `lore-pack/` content pack beside the
short `lore-book/BOOK.md` entry point so public Markdown/TXT Lore documents can
be searched and read offline without raw deep `lore-book/` mirror paths in the
ZIP. External references may still open in the browser. This is not an MSIX,
installer, Store package, signed release, or SmartScreen/reputation claim.
Asset Library loads generated local asset catalogs; downloadable app ZIPs do
not bundle game assets, browse raw game files directly, or generate catalogs in
place. Catalog generation is a source/lab workflow documented under
`reverse-engineering/game-assets/`.

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
secrets, while `test:public-allowlist` runs hard-payload safety, submodule
payload safety, and public-primary migration/hash inventory.

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
