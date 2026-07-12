# Onslaught Toolkit

Onslaught Toolkit is a Battle Engine Aquila (2003) preservation, patching, and
rebuild project. The WinUI 3 Windows app is the primary end-user toolkit. A
separate GPL-licensed, RE-informed original-code rebuild now lives under
[`rebuild/`](rebuild/README.md); it does not replace or modify the retail game.

This public repository is the primary collaboration and day-to-day working
checkout. The former maintainer-only tree has been folded into this repo as
project history and working material: source, tools, RE docs, wave notes, state batons,
agent reports, readiness notes, and structured proof summaries should live here
when they are useful to contributors. Ignored local overlays are only for hard
payloads such as actual game installs, copied executables, private media/input
files, full Ghidra project stores/backups, secrets, build output, and bulky
generated runtime captures. See [LOCAL_LAB_OVERLAY.md](LOCAL_LAB_OVERLAY.md).

Detailed static RE status is intentionally not duplicated in this README. Use
[reverse-engineering/RE-INDEX.md](reverse-engineering/RE-INDEX.md),
[CURRENT_CAPABILITIES.md](CURRENT_CAPABILITIES.md), and the static measurement
registers under `reverse-engineering/binary-analysis/`, especially
[static-reaudit-measurement-register.md](reverse-engineering/binary-analysis/static-reaudit-measurement-register.md),
for current accounting.

For the current feature surface, navigation order, Save Lab workflows, static-RE posture, and lane gates, see **[CURRENT_CAPABILITIES.md](CURRENT_CAPABILITIES.md)**.

## Download

Downloadable app builds are published on the
[GitHub Releases](https://github.com/dlprentice/Onslaught-Career-Editor/releases)
page as unsigned portable Windows x64 ZIP assets with SHA-256 checksum sidecars.
Extract the full ZIP and run `Launch Onslaught Toolkit.cmd` from the clean
top-level folder. The app payload lives under `app\`; run
`app\OnslaughtCareerEditor.WinUI.exe` only as a fallback. Use `v1.0.9` or newer;
it keeps the Explorer-safe ZIP layout introduced after `v1.0.3`/`v1.0.4`, labels
browser-opening Lore links clearly, and includes a generated offline Lore
content pack.

The ZIP release does not include Battle Engine Aquila game files, copied
executables, saves, media payloads, full Ghidra databases, or bulky generated
proof captures. Published `v1.0.9` keeps `lore-book\BOOK.md` as a short entry
point and adds `lore-pack\onslaught-lore.v1.jsonl` plus
`lore-pack\onslaught-lore.v1.index.json` with 949 tracked Markdown/TXT
documents selected from the Lore, roadmap, and technical RE corpus, so the app
can search and read broad offline material without raw deep `lore-book/`
filenames breaking normal Explorer extraction. The count is a packaging fact,
not a claim of narrative completeness, editorial review, freshness,
provenance/rights review, or broad public-safety approval. Its ZIP SHA-256 is
`e09439c40a4ff7197c4151e18651388b2515a71950ea2479b01266c00d918519`, with a
published checksum sidecar. v1.0.9 also improves first-time-user wording around
write/copy/shell actions and confirms before the app closes or force-stops a
managed copied-game process. External references may still open in the browser.
Media and safe copied-game workflows use your own retail/Steam install.
Asset Library loads generated local asset catalogs; the ZIP does not bundle
game assets or generate catalogs in-place. Catalog generation is a source/lab
workflow documented under `reverse-engineering/game-assets/`. Patching
workflows operate on copied files and safe game copies.

For contributor setup, local validation expectations, hard-payload boundaries, and PR-ready change rules, see **[CONTRIBUTING.md](CONTRIBUTING.md)**.

For a concise handoff checklist for outside developers and agent reviewers, see
**[COLLABORATION.md](COLLABORATION.md)**.

For asset-leak, copied-executable safety, secrets, and future online-session reporting rules, see **[SECURITY.md](SECURITY.md)**.

**Contributor base:** use this public repository unless a maintainer explicitly
assigns a separate branch or short-lived workspace. Local lab inputs are
supported through ignored overlay folders when they are actual game payloads,
secrets, copied runtime output, or other non-source artifacts. Portable ZIP
publication, source pushes, signing, installer release, and announcement are
separate maintainer actions. Signed installer-grade MSIX trust/install remains a
future proof, not a current release claim.

Electron, the old Python GUI/CLI app, and WPF are archived/reference app
surfaces in this repo for provenance and future inspection. They are not active
product lanes and are not part of the default shipped app ZIP.

## Active Layout

| Surface | Status | Notes |
|---|---|---|
| `OnslaughtCareerEditor.WinUI` | Primary product lane | WinUI 3 Windows app for normal user workflows |
| `OnslaughtCareerEditor.AppCore` | Shared correctness/core support | Save/options/patch/media/lore/asset-catalog behavior for the Windows lane |
| `OnslaughtCareerEditor.AppCore.Tests` | Active tests | Core regression coverage |
| `OnslaughtCareerEditor.UiTests` | Active tests | WinUI product-lane, static, contrast, and launch-smoke coverage |
| `OnslaughtCareerEditor.Cli` | Active C# support CLI | Supported analyzer/patcher CLI for Windows/AppCore workflows |
| `OnslaughtCareerEditor.AppCore.Host` | Support/reference bridge | JSON/stdio diagnostics including save patch plans and public-safe asset model preview coverage |
| `rebuild` | Active RE-informed rebuild | GPL deterministic Core, command-tape replay, and independent trace/final-state golden verification; visual client follows as a separate slice |
| `tools` | Active tooling | Release, docs, RE, extraction, validation, Ghidra/CDB, and local utility scripts |

## Quick Start

The normal WinUI/AppCore path does not require a game install, Git submodules,
or `npm install`. From repo root:

```powershell
dotnet --version # must be .NET SDK 10.x
dotnet --list-runtimes # must include Microsoft.NETCore.App 8.x for rebuild tests/host
node --version # must be v24.x
npm --version  # must satisfy >=11.12 <12; npm@11.12.1 is the packageManager target
py -3 --version
npm test
npm run dev
```

`npm test` is the active-product quick check: docs/mirror consistency, the
WinUI build, AppCore tests, WinUI tests, and deterministic rebuild Core tests.
`npm run dev` launches the WinUI app. Both commands use the tools already
installed on the machine; the root
`npm install` path exists only for deliberate inspection of the archived
Electron workbench and is not normal product setup. Root `package.json` is the
command authority.

`npm run test:hard-payload-safety` checks that tracked files do not include
actual copied game/runtime binaries, known local game payload roots, build
outputs, `.env` files, or credential-like key material. It does not censor raw
RE notes, state batons, agent reports, or proof summaries.

A fresh clone can build the source, run AppCore/WinUI tests, and inspect docs
without a local game install, Ghidra database, or private proof archive.
Initialize submodules only before running public allowlist/release-safety gates
because those gates also inspect reference submodule boundaries. A local
Battle Engine Aquila install is only needed for game-aware workflows such as
Media browsing, safe-copy patching, asset extraction, and live runtime proof.

Archived app scripts are reference checks only. They are not the default product
lane, but they remain part of the repository history.

Use the
[repository authority map](roadmap/repo-structure-and-archive-map.md) before
editing mirrors, generated material, release history, or archived surfaces.

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
npm run build:rebuild-core
npm run test:rebuild-core
npm run run:rebuild-headless
```
<!-- public-package-commands:end -->

Public sign-off commands live in
[PUBLIC_SIGNOFF_COMMANDS.md](release/readiness/PUBLIC_SIGNOFF_COMMANDS.md).
Runtime proof aggregates may require ignored local overlays for copied
executables, frames, captures, or full debugger logs. Track compact proof
summaries and checkers; keep the bulky generated payloads local or archived
outside git.

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

`npm run test:md-links` may write generated reports under `subagents/md-link-check`; use it for validation, but do not treat generated report payloads as app release assets.

## Archived Apps

This repo preserves the historical Electron, Python GUI/CLI, and WPF app
attempts for provenance, not as active product lanes. They may contain useful
reference implementations, but WinUI/AppCore remains the release lane.

## Safety Rules

- Never create `.bes` career files from scratch.
- Treat retail `BEA.exe` and real save/options files as authoritative.
- Patch only copied targets for executable mutation workflows.
- Online multiplayer is not available yet. The app offers a local split-screen launch preset for safe copies; Host/Join controls stay hidden or disabled and are never advertised as player-ready.
- Preserve file size, reserved bytes, and unknown regions unless the behavior is explicitly documented.
- Keep actual game/media/save payloads and bulky generated proof captures out of git and out of public release ZIPs.

## Requirements

- Windows 10/11 for WinUI 3.
- .NET 10 SDK for WinUI/AppCore/C# CLI, plus the .NET 8 runtime/targeting pack
  for the rebuild Core, tests, and headless host. Installing the .NET 8 SDK is
  the simplest way to supply the latter and prepares the Godot .NET lane.
- Node.js 24.x and npm `>=11.12 <12` for repo docs/release checks and optional archived Electron inspection. The tracked `packageManager` target is `npm@11.12.1`.
- Python 3 with the Windows `py` launcher for public-safe tooling checks.
- A valid Battle Engine Aquila installation for game-aware workflows.

Common Steam path:

- `C:\Program Files (x86)\Steam\steamapps\common\Battle Engine Aquila`

## Reverse Engineering Status

- Static docs summarize static status at a bounded level. Static status is
  not runtime gameplay proof, exact layout proof, patch behavior proof, visual
  proof, online play, or rebuild parity.
- Use the tracked static measurement registers for current percentages, debt
  counters, current-risk progress, latest backup pointers, and
  completion-target accounting.

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

The toolkit code, docs, and tooling are MIT-licensed; see [LICENSE](LICENSE).
The [`rebuild/`](rebuild/README.md) subtree is separately licensed
GPL-3.0-or-later, as is the `references/Onslaught` source submodule under its
own license. The root MIT license does not relicense either GPL subtree.

Battle Engine Aquila, its executable, media, saves, screenshots, extracted
assets, trademarks, and third-party runtime components are not licensed by
this repository.
