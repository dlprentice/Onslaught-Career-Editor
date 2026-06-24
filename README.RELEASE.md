# Onslaught Toolkit Release Notes

Status: active public safety/export note
Last updated: 2026-06-23

This file describes the current source-release and public-safety posture. The repo is WinUI-first for the user-facing Windows product. Electron, WPF, and the old Python GUI/CLI parity app are archived/reference surfaces.

Contributor setup, local validation expectations, and public/private contribution boundaries are in [CONTRIBUTING.md](CONTRIBUTING.md). Private-data and vulnerability reporting guidance is in [SECURITY.md](SECURITY.md). Public candidate sign-off commands are in [PUBLIC_SIGNOFF_COMMANDS.md](release/readiness/PUBLIC_SIGNOFF_COMMANDS.md), and the public candidate agent guide is [public_AGENTS.md](release/readiness/public_AGENTS.md). These guides are part of the curated public-source candidate. A validated public-source candidate is not automatically a GitHub Release; portable ZIP publication, source pushes, signing, installer release, and announcement are separate maintainer actions.

## Downloadable App Releases

Current downloadable app releases use an unsigned portable Windows x64 ZIP
attached to GitHub Releases with a SHA-256 checksum sidecar. Extract the full
ZIP and run `OnslaughtCareerEditor.WinUI.exe`.

The ZIP release does not include Battle Engine Aquila game files, saves, media,
or private proof material. Users provide their own retail/Steam installation,
and mutating workflows operate on copied files or safe game copies. This is not
an MSIX, installer, Store package, signed release, or SmartScreen/reputation
claim.

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

The curated source-tree/export boundary centers on public-safe WinUI/AppCore/C# CLI/docs/tooling source. It excludes private assets, runtime evidence, local state, archived apps, generated bundles, archived UI material, and local proof/backup roots. Private maintainer disposable packaging probes are recorded as maintainer evidence only; signed installer-grade WinUI packaging remains a separate future proof, not a current public claim.

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

Private-maintainer validation from the private source tree can include:

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
npm run test:public-candidate-inventory
npm run test:public-allowlist
npm run test:repo-hygiene
```

Do not run that private-maintainer block from a public candidate. Public
candidates use the smaller root `package.json` script surface and the sign-off
sequence below.

`npm run test:md-links` writes ignored reports under `subagents/md-link-check`; those reports are validation artifacts, not release payload.

Archived Electron checks are private-maintainer reference checks only. Public
source candidates exclude `archive/**`, so archive commands are not public
package commands or product gates.

Public-candidate source-tree safety gates:

<!-- public-package-commands:start -->
```powershell
npm run test:doc-commands
npm run test:md-links
npm run test:public-candidate-inventory
npm run test:public-allowlist
npm run test:repo-hygiene
npm run test:winui-notices
```
<!-- public-package-commands:end -->

Private maintainers run `py -3 tools\release_profile_snapshot.py --check`,
`py -3 tools\release_curated_manifest.py --check`, and
`bash tools/release_package.sh --dry-run` from the private source tree before
materializing a public candidate. Those private manifest/accounting gates are
not public PR gates because the public candidate does not include the private
curated manifest or private inventory artifacts.

For the authoritative public validation order, including the fresh-export
inventory and `EXPORT_PROVENANCE.json` check, use
[PUBLIC_SIGNOFF_COMMANDS.md](release/readiness/PUBLIC_SIGNOFF_COMMANDS.md).

The private root `package.json`, root `AGENTS.md`, root `.gitignore`, and private sign-off runbook are not public payload because they carry private/runtime maintainer posture. The curated export uses `release/readiness/public_package.json` as root `package.json`, `release/readiness/public_AGENTS.md` as root `AGENTS.md`, and `release/readiness/public_gitignore.txt` as root `.gitignore` in exported public-candidate trees.

The curated export also materializes public-safe RE, roadmap, lore, and
lore-book entrypoint variants so public candidates expose a link-closed
documentation surface without copying private proof forests, state batons,
runtime evidence, or backup-root details.

Generated release accounting is owned by `py -3 tools\release_profile_snapshot.py --check` and `py -3 tools\release_curated_manifest.py --check` in the private source tree; do not copy stale count literals from old prose. Path allowlisting alone is not enough: `npm run test:public-allowlist` scans candidate text payloads, Java/Python/tooling text, required public guide rows, JSON-escaped paths, public Python imports, public package script references, and binary/save-like suffixes for private/local proof material. In the private source tree, `npm run test:public-candidate-inventory` runs the inventory checker self-test. After a public candidate is materialized, the exported candidate's `package.json` runs the self-test plus `--candidate-root .` before build/test commands create generated local artifacts. After product/docs validation, regenerate a fresh candidate before sharing so `EXPORT_PROVENANCE.json` names the source commit and the inventory gate passes on a clean payload. The real-save regression fixture and private release-accounting/export scripts are private maintainer-tree material and are not public candidate payload.

## Archive Posture

`archive/electron-workbench/release/Build-ElectronBundle.ps1` and related scripts are retained only so the archived Electron workbench can be inspected later. They are excluded from the WinUI-first public source candidate and must not be treated as the community product release path.

## Maintainer Notes

- WinUI 3 is the product UX focus.
- In the private source tree, `release/readiness/curated_release_manifest.json`, `release/readiness/public_candidate_allowlist.tsv`, and `release/readiness/private_only_inventory.tsv` are generated release-scope authority. In public candidates, use root `package.json`, `AGENTS.md`, `release/readiness/PUBLIC_SIGNOFF_COMMANDS.md`, `release/readiness/public_candidate_allowlist.tsv`, and `EXPORT_PROVENANCE.json` as the local source-candidate authority.
- The public candidate materializes selected public summaries under `release/readiness/public_*.txt`, including current capabilities, roadmap index, UI/UX redesign radar, RE index, quick-reference index, lore entrypoints, and MSL scripting. Those generated summaries are the preferred public entrypoints over private maintainer evidence notes.
- Private readiness notes may remain useful maintainer evidence in this source tree even when the current generated inventory denies them from public release. Treat denied notes as private maintainer context, not public payload.
- `release/readiness/curated_release_manifest.json` is the private-side source candidate policy input used to generate public-candidate accounting and export payloads; do not treat it as end-user release evidence.
- `.codex/**`, `archive/**`, `game/**`, `media/**`, `save-attempts/**`, `subagents/**`, repo state files, private runtime evidence, private release inventories, private sign-off runbooks, and local proof/backup-root payloads remain public-release deny material unless explicitly sanitized.
- Halt broad Electron, Python GUI, and WPF product work. Port only narrow, reviewed logic into WinUI/AppCore/tools if needed.
