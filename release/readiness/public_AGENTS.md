# AGENTS.md

Status: public-primary contributor agent guide
Last updated: 2026-06-24

This file is the public-primary contributor agent guide for Onslaught Toolkit.
The root `AGENTS.md` is now the normal working guide. Public candidate exports
may still materialize this file for package/export compatibility, but the public
repo is no longer a sparse subset of a private source tree.

## Current Direction

- WinUI 3 is the primary user-facing Windows app.
- `OnslaughtCareerEditor.AppCore` holds shared correctness logic for saves,
  options, patch planning, media/catalog support, and safe-copy workflows.
- `OnslaughtCareerEditor.Cli` is a C# support CLI.
- Python under `tools/` supports repo tooling, validation, asset/RE support,
  local lab workflows, and release-policy support. It is not a product GUI lane.
- Electron, WPF, and the old Python GUI/CLI are archived/reference lanes only.
- Static reverse-engineering docs, wave notes, state batons, agent reports, and
  compact proof summaries are tracked project material. Actual game payloads,
  copied executables, screenshots/frame dumps, arbitrary saves/options, raw CDB
  logs, full Ghidra databases/backups, secrets, and bulky local proof bundles
  are ignored local overlays.

## First Rules

- Read `README.MD`, `CONTRIBUTING.md`, `SECURITY.md`, and
  `COLLABORATION.md` before making changes.
- Keep changes narrow and path-scoped.
- Do not add game binaries, extracted assets, arbitrary saves/options,
  screenshots/frame dumps, raw CDB logs, bulky local proof bundles, credentials,
  `.env*`, or copied runtime outputs.
- Do not patch or mutate an installed Battle Engine Aquila folder or original
  `BEA.exe`. App workflows must operate on copied targets only.
- Do not synthesize `.bes` saves from scratch; use real baselines and preserve
  unknown bytes.
- Do not add GitHub Actions, hosted CI, release automation, or workflow
  scaffolding. Validation is local.
- Public issue/PR templates are allowed when they remain documentation-only and
  do not add hosted validation or workflow automation.
- Public docs must separate proven features from plans, runtime experiments,
  online/multiplayer research, and rebuild aspirations.

## Product Lanes

| Area | Status | Main paths |
| --- | --- | --- |
| WinUI 3 app | Primary product | `OnslaughtCareerEditor.WinUI/` |
| Shared core | Active support | `OnslaughtCareerEditor.AppCore/` |
| C# CLI | Active support | `OnslaughtCareerEditor.Cli/` |
| Tests | Active | `OnslaughtCareerEditor.AppCore.Tests/`, `OnslaughtCareerEditor.UiTests/` |
| Tooling | Active support | `tools/` |
| Reverse-engineering docs | Public-safe specs/research | `reverse-engineering/RE-INDEX.md`, `reverse-engineering/quick-reference/`, `roadmap/ROADMAP-INDEX.md` |
| Archived apps | Reference only | `archive/` is tracked reference source, not shipped app payload |

## Setup

From repo root:

```powershell
npm run test:public-candidate-inventory
npm install
dotnet build .\OnslaughtCareerEditor.WinUI.slnx --nologo
npm run dev
```

Use this repo's `package.json` for contributor commands. Public-source
validation also requires Python 3 through the Windows `py` launcher because
docs/release/tooling checks use `py -3`.

## Common Local Gates

Run the smallest gate set that matches your change.

<!-- public-package-commands:start -->
```powershell
npm run build:winui
npm run test:appcore
npm run test:winui
npm run test:winui-primary-lane
npm run test:winui-safe-copy-preflight
npm run test:winui-patch-engine-safety
npm run build:host
npm run test:doc-commands
npm run test:md-links
npm run test:public-allowlist
npm run test:repo-hygiene
npm run test:winui-notices
```
<!-- public-package-commands:end -->

Private maintainers run the private release profile and curated-manifest gates
before export. Public agents should not require those private manifest files in
the public candidate.
Run `npm run test:public-candidate-inventory` only on a fresh exported payload
before install/build/test outputs are created.
Before trusting a shared public candidate, verify `EXPORT_PROVENANCE.json` is
present and then run `npm run test:public-candidate-inventory` on a clean tree.

Run .NET build/test commands serially. UI Automation and visual claims require
native WinUI checks; browser or fixture success is not native runtime proof.
Public candidates include a curated, link-closed RE/lore/roadmap documentation
surface. Private proof forests, raw wave evidence, backup paths, runtime
artifacts, and operator-only docs remain excluded unless they are rewritten as
bounded public summaries.

## Public/Private Boundary

Public source candidates are manifest-driven. Do not assume that a private
working tree is public-shaped.

Public candidates must exclude:

- `game/**`, private `media/**`, `save-attempts/**`, `subagents/**`, `.codex/**`
- repo state files such as `developer_agent_state.json`
- private runtime evidence, local proof bundles, screenshots, frame captures,
  copied executable bytes, raw saves, extracted assets, secrets, and operator
  directives

Use `SECURITY.md` for private-data reporting and `README.RELEASE.md` /
`PUBLIC_SIGNOFF_COMMANDS.md` for release-safety posture.

## WinUI Contribution Rules

- Keep normal user wording plain. Hide proof IDs, raw offsets, and maintainer
  jargon behind details surfaces or docs.
- Back user-visible behavior with AppCore where practical.
- Add or preserve stable `AutomationProperties.AutomationId` values for
  actionable controls and named inputs.
- For UI behavior changes, prefer focused WinUI/AppCore tests plus the relevant
  visual/UIA proof.
- Rebuild WinUI before native UIA smoke tests so tests do not launch stale
  binaries.

## Patch/Mod Rules

- Patch only copied executables and app-owned artifact roots.
- Verify original bytes before applying a patch and patched bytes after.
- Keep patch descriptions bounded to what is proven.
- Do not claim gameplay improvement, online play, or runtime behavior unless a
  matching proof exists.

## Online/Multiplayer Boundary

Online multiplayer is active research, not a released public capability.
Host/Join UI must remain disabled until distinct-endpoint command-source proof
and source-bound copied-runtime causality proof are accepted. Loopback,
synthetic, same-process, or same-workstation proofs do not equal player-ready
netplay.

## Pull Request Checklist

Before asking for review:

- Describe the change and affected paths plainly.
- Name the local gates you ran.
- Confirm no private assets, saves, screenshots, proof bundles, secrets, or
  state files were added.
- Confirm installed game files and original `BEA.exe` were not mutated.
- Keep archived app changes out of scope unless the task explicitly targets an
  archive.
