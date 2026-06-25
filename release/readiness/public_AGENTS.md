# AGENTS.md

Status: package/export compatibility agent guide; root AGENTS.md is the canonical public-primary contributor guide
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
| Reverse-engineering docs | Payload/secret-safe specs/research | `reverse-engineering/RE-INDEX.md`, `reverse-engineering/quick-reference/`, `roadmap/ROADMAP-INDEX.md` |
| Archived apps | Reference only | `archive/` is tracked reference source, not shipped app payload |

## Setup

From repo root:

```powershell
npm run test:hard-payload-safety
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

Maintainers may still run release profile and curated-manifest gates before
packaging or export. Public agents working in the normal repo should use the
root `AGENTS.md` and `npm run test:hard-payload-safety`; run
`npm run test:public-candidate-inventory` only on a fresh materialized
package/export candidate before install/build/test outputs are created. Before
trusting a shared export candidate, verify `EXPORT_PROVENANCE.json` is present
and then run `npm run test:public-candidate-inventory` on a clean tree.

Run .NET build/test commands serially. UI Automation and visual claims require
native WinUI checks; browser or fixture success is not native runtime proof.
The normal public-primary source repo can track broad source/docs/tools/RE
history, compact non-secret state batons, text subagent reports, readiness
notes, and proof summaries. Package/export candidates may still be smaller than
the source repo and must exclude raw hard payloads, bulky generated proof
output, full Ghidra databases/backups, secrets, and machine-only runtime
material.

## Public/Private Boundary

This file may be materialized into package/export candidates. It is not a
reason to reduce the public-primary source repo to a sparse export.

Package/export candidates and app ZIP payloads must exclude hard payloads:

- `game/**`, private `media/**`, `save-attempts/**`, copied executable bytes,
  arbitrary saves/options, extracted assets, screenshots/frame captures, raw CDB
  logs, full Ghidra databases/backups, secrets, local config, and bulky local
  proof bundles.
- Generated/raw payloads under `subagents/**`; compact text reports and proof
  summaries may be tracked in public source.
- Runtime `.codex` sessions/cache/auth/log material; compact non-secret
  `.codex/goals/**` and `.codex/state/**` markdown may be tracked in public
  source when useful.
- Portable app ZIPs and legacy curated exports may omit state batons and
  maintainer-only accounting surfaces, but that does not make compact
  non-secret state files invalid in the public-primary source repo.

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
- Confirm no private assets, arbitrary saves/options, screenshots/frame dumps,
  raw CDB logs, copied executables, bulky proof bundles, secrets, runtime
  cache/session/auth/log material, or copied runtime outputs were added.
- Confirm any state batons or text agent reports added are compact, non-secret,
  and free of hard payloads or raw local proof output.
- Confirm installed game files and original `BEA.exe` were not mutated.
- Keep archived app changes out of scope unless the task explicitly targets an
  archive.
