# Onslaught Toolkit

Onslaught Toolkit is a Battle Engine Aquila (2003) preservation and patching toolkit. The only forward-facing GUI product lane is now the WinUI 3 Windows app.

Detailed static RE status is intentionally not duplicated in this README. Public
candidates use [reverse-engineering/RE-INDEX.md](reverse-engineering/RE-INDEX.md)
and [CURRENT_CAPABILITIES.md](CURRENT_CAPABILITIES.md) for bounded public
summaries; private maintainers use the private static measurement register for
current internal accounting.

For the current feature surface, navigation order, Save Lab workflows, static-RE posture, and lane gates, see **[CURRENT_CAPABILITIES.md](CURRENT_CAPABILITIES.md)**.

## Download

Downloadable app builds are published on the
[GitHub Releases](https://github.com/dlprentice/Onslaught-Career-Editor/releases)
page as unsigned portable Windows x64 ZIP assets with SHA-256 checksum sidecars.
Extract the full ZIP and run `OnslaughtCareerEditor.WinUI.exe`.

The ZIP release does not include Battle Engine Aquila game files, saves, media,
or private proof material. Use your own retail/Steam install; patching workflows
operate on copied files and safe game copies.

For contributor setup, local validation expectations, public/private boundaries, and PR-ready change rules, see **[CONTRIBUTING.md](CONTRIBUTING.md)**.

For a concise handoff checklist for outside developers and agent reviewers, see
**[COLLABORATION.md](COLLABORATION.md)**.

For private-data, asset-leak, copied-executable safety, and future online-session reporting rules, see **[SECURITY.md](SECURITY.md)**.

**Contributor base:** use a sanitized public candidate or a
maintainer-approved collaborator branch. Private `main` is not a public PR base
unless access is explicitly granted. Public candidate gates live in
[PUBLIC_SIGNOFF_COMMANDS.md](release/readiness/PUBLIC_SIGNOFF_COMMANDS.md).
Validated public candidate does not itself mean a GitHub Release has been
published. Portable ZIP publication, source pushes, signing, installer release,
and announcement are separate maintainer actions. Signed installer-grade MSIX
trust/install remains a future proof, not a current release claim.

Electron, the old Python GUI/CLI app, and WPF are archived/reference app
surfaces in the private maintainer tree. They remain in private git for
provenance and future inspection, but they are not active product lanes and are
not part of the default public release shape.

## Active Layout

| Surface | Status | Notes |
|---|---|---|
| `OnslaughtCareerEditor.WinUI` | Primary product lane | WinUI 3 Windows app for normal user workflows |
| `OnslaughtCareerEditor.AppCore` | Shared correctness/core support | Save/options/patch/media/lore/asset-catalog behavior for the Windows lane |
| `OnslaughtCareerEditor.AppCore.Tests` | Active tests | Core regression coverage |
| `OnslaughtCareerEditor.UiTests` | Active tests | WinUI product-lane, static, contrast, and launch-smoke coverage |
| `OnslaughtCareerEditor.Cli` | Active C# support CLI | Supported analyzer/patcher CLI for Windows/AppCore workflows |
| `OnslaughtCareerEditor.AppCore.Host` | Support/reference bridge | JSON/stdio diagnostics including save patch plans and public-safe asset model preview coverage |
| `tools` | Active tooling | Release, docs, RE, extraction, validation, Ghidra/CDB, and local utility scripts |

## Quick Start

From repo root:

```powershell
npm run test:public-candidate-inventory # fresh public candidate only, before install/build outputs
npm install
dotnet build .\OnslaughtCareerEditor.WinUI.slnx --nologo
npm run dev
```

`npm run dev` launches the WinUI app (same as `dotnet run` on the WinUI project in this repo).
All `npm run ...` gates are defined by the candidate root `package.json`.
`npm run test:public-candidate-inventory` is a fresh-export cleanliness gate;
after validation creates `bin/`, `obj/`, `subagents/`, `node_modules/`, or
package-lock artifacts, regenerate a clean candidate before sharing.

Archived app scripts are private-maintainer reference checks only. Public
exports use a smaller reviewed npm manifest without archived/private runtime
scripts.

Core public-source validation:

<!-- public-package-commands:start -->
```powershell
dotnet test .\OnslaughtCareerEditor.AppCore.Tests\OnslaughtCareerEditor.AppCore.Tests.csproj --nologo
dotnet test .\OnslaughtCareerEditor.UiTests\OnslaughtCareerEditor.UiTests.csproj --nologo --filter "FullyQualifiedName!~LegacyWpf"
npm run test:winui-primary-lane
npm run test:winui-safe-copy-preflight
npm run test:winui-patch-engine-safety
npm run build:host
dotnet run --project .\OnslaughtCareerEditor.Cli\OnslaughtCareerEditor.Cli.csproj -- --help
```
<!-- public-package-commands:end -->

Public candidate sign-off commands and the required `EXPORT_PROVENANCE.json`
check live in [PUBLIC_SIGNOFF_COMMANDS.md](release/readiness/PUBLIC_SIGNOFF_COMMANDS.md).
Private maintainer/runtime proof aggregates require the full private tree and
private/runtime helper scripts; they are not public candidate gates.

Repo/docs/release safety checks:

<!-- public-package-commands:start -->
```powershell
npm run test:doc-commands
npm run test:md-links
npm run test:public-allowlist
npm run test:repo-hygiene
npm run test:winui-notices
```
<!-- public-package-commands:end -->

`npm run test:md-links` writes ignored reports under `subagents/md-link-check`; use it for validation, but do not treat the generated report folder as release payload.

## Archived Apps

The private maintainer tree preserves the historical Electron, Python GUI/CLI,
and WPF app attempts for provenance, not as public product lanes. Public exports
exclude archived app trees and their private reference scripts, so they are not
public package commands or product gates.

## Safety Rules

- Never create `.bes` career files from scratch.
- Treat retail `BEA.exe` and real save/options files as authoritative.
- Patch only copied targets for executable mutation workflows.
- Online multiplayer is not available yet. The app offers a local split-screen launch preset for safe copies; Host/Join controls stay hidden or disabled and are never advertised as player-ready.
- Preserve file size, reserved bytes, and unknown regions unless the behavior is explicitly documented.
- Keep private game/media/save/proof assets out of public release outputs.

## Requirements

- Windows 10/11 for WinUI 3.
- .NET 10 SDK for WinUI/AppCore/C# CLI.
- Node.js/npm for repo docs/release checks and optional archived Electron inspection. The tracked npm target is `npm@11.12.1`.
- Python 3 with the Windows `py` launcher for public-safe tooling checks.
- A valid Battle Engine Aquila installation for game-aware workflows.

Common Steam path:

- `C:\Program Files (x86)\Steam\steamapps\common\Battle Engine Aquila`

## Reverse Engineering Status

- Public docs summarize static status only at a bounded level. Static status is
  not runtime gameplay proof, exact layout proof, patch behavior proof, visual
  proof, online play, or rebuild parity.
- Private maintainers should use the private static measurement register for
  current percentages, debt counters, current-risk progress, latest backup
  pointers, and completion-target accounting.

## Core Docs

- [CURRENT_CAPABILITIES.md](CURRENT_CAPABILITIES.md)
- [CONTRIBUTING.md](CONTRIBUTING.md)
- [COLLABORATION.md](COLLABORATION.md)
- [SECURITY.md](SECURITY.md)
- [reverse-engineering/RE-INDEX.md](reverse-engineering/RE-INDEX.md)
- [roadmap/ROADMAP-INDEX.md](roadmap/ROADMAP-INDEX.md)
- [roadmap/public-roadmap.md](roadmap/public-roadmap.md)
- [roadmap/three-lane-product-strategy.md](roadmap/three-lane-product-strategy.md)
- [roadmap/winui-ui-ux-redesign-radar.md](roadmap/winui-ui-ux-redesign-radar.md)
- [roadmap/repo-structure-and-archive-map.md](roadmap/repo-structure-and-archive-map.md)
- [RELEASE_SCOPE_AND_TEST_COMMANDS.md](RELEASE_SCOPE_AND_TEST_COMMANDS.md)
- [lore/LORE-INDEX.md](lore/LORE-INDEX.md)
- [lore-book/BOOK.md](lore-book/BOOK.md)

## License

MIT. See [LICENSE](LICENSE).

The MIT license applies to original project code/docs/tooling only. Battle Engine Aquila, its executable, media, saves, screenshots, extracted assets, trademarks, and third-party runtime components are not licensed by this repository.
