# AGENTS.md

Status: public-primary contributor agent guide
Last updated: 2026-07-11

This file is the public-primary agent guide for Onslaught Toolkit. Treat this
checkout as the normal collaboration and day-to-day working repo. Raw project
history and working material are allowed here when useful: RE docs, wave notes,
state batons, agent reports, readiness docs, proof summaries, checkers, and
tooling. Ignored local overlays are reserved for hard payloads such as actual
game files, copied executables, private media/input files, full Ghidra databases
or backups, secrets, build output, and bulky generated runtime captures.

## Current Direction

- WinUI 3 is the primary user-facing Windows app.
- `OnslaughtCareerEditor.AppCore` holds shared correctness logic for saves,
  options, patch planning, media/catalog support, and safe-copy workflows.
- `OnslaughtCareerEditor.Cli` is a C# support CLI.
- Python under `tools/` supports repo tooling, validation, asset/RE support,
  and local lab workflows. It is not a product GUI lane.
- Electron, WPF, and the old Python GUI/CLI are archived/reference lanes only.
- Static reverse-engineering docs, runtime proof summaries, state batons, and
  agent reports are tracked project material unless they embed actual game
  payloads or secrets.

## First Rules

- Read `README.MD`, `CONTRIBUTING.md`, `SECURITY.md`, and
  `COLLABORATION.md` before making changes.
- Keep changes narrow and path-scoped.
- Give each substantive objective or related release batch one normal/adversarial
  review envelope. Codex root and Codex-owned subagents use
  `gpt-5.6-sol`/`ultra`; bounded external normal/adversarial consults use
  `cursor-agent --model grok-4.5-fast-xhigh` when the required read-only
  sandbox and authentication are available. Trivial lookups and routine
  follow-through inside an accepted envelope do not create recursive consult
  loops. External prompts stay bounded and non-secret; Codex root owns edits,
  validation, state, commits, pushes, publication decisions, and final
  acceptance.
- Do not add game binaries, extracted assets, copied executables, arbitrary
  local save payloads, screenshots/frame dumps, raw CDB logs, full Ghidra
  databases, credentials, or `.env*` files. The narrow exception is the tracked
  immutable regression fixture `tests_shared/fixtures/gold_career_save.bin`.
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
- Read [LOCAL_LAB_OVERLAY.md](LOCAL_LAB_OVERLAY.md) before adding or moving
  game/Ghidra/proof material.

## Product Lanes

| Area | Status | Main paths |
| --- | --- | --- |
| WinUI 3 app | Primary product | `OnslaughtCareerEditor.WinUI/` |
| Shared core | Active support | `OnslaughtCareerEditor.AppCore/` |
| C# CLI | Active support | `OnslaughtCareerEditor.Cli/` |
| Tests | Active | `OnslaughtCareerEditor.AppCore.Tests/`, `OnslaughtCareerEditor.UiTests/` |
| Tooling | Active support | `tools/` |
| Reverse-engineering docs | Specs/research/proof summaries | `reverse-engineering/RE-INDEX.md`, `reverse-engineering/quick-reference/`, `roadmap/ROADMAP-INDEX.md` |
| Archived apps | Reference only | `archive/` |

## Setup

From repo root:

```powershell
git submodule update --init --recursive
node --version # must be v24.x
npm --version  # must satisfy >=11.12 <12; npm@11.12.1 is the packageManager target
npm run test:hard-payload-safety
npm install
dotnet build .\OnslaughtCareerEditor.WinUI.slnx --nologo
npm run dev
```

Use this repo's `package.json` for contributor commands. Validation also
requires Python 3 through the Windows `py` launcher because docs/release/tooling
checks use `py -3`.

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
npm run build:cli
npm run test:doc-commands
npm run test:md-links
npm run test:public-allowlist
npm run test:repo-hygiene
npm run test:winui-notices
```
<!-- public-package-commands:end -->

Run `npm run test:hard-payload-safety` before pushing boundary-sensitive work.
It checks for tracked hard payloads and obvious secrets; it is not meant to hide
normal RE notes, state batons, agent reports, or proof summaries.

Run .NET build/test commands serially. UI Automation and visual claims require
native WinUI checks; browser or fixture success is not native runtime proof.
The public repo should contain the useful source/docs/tools/RE/runtime-proof
surface, not only a tiny release export. Full Ghidra databases, copied runtime
outputs, raw frame dumps, and secrets remain ignored local overlays.

## Public / Local Overlay Boundary

This public checkout is the normal working repo. Local lab material can be kept
inside ignored overlay folders so tools and agents can use it without publishing
it.

Keep out of git:

- `game/**`, private media/input payloads, copied executable bytes, raw saves,
  extracted assets, full Ghidra project databases/backups, secrets, `.env*`,
  build/test output, screenshots, frame captures, and raw CDB logs
- Narrow exception: `tests_shared/fixtures/gold_career_save.bin` is the tracked
  immutable regression baseline. Do not generalize that to arbitrary `.bes`,
  `.bea`, options, or `save-attempts/` payloads.

Use `SECURITY.md` for private-data reporting and `README.RELEASE.md` /
`release/readiness/PUBLIC_SIGNOFF_COMMANDS.md` for release-safety posture.

## Agent Skill Guidance

Repo-specific Codex knowledge should be durable in normal repo files:
`AGENTS.md`, `CONTRIBUTING.md`, `LOCAL_LAB_OVERLAY.md`, `tools/README.md`,
`reverse-engineering/`, `roadmap/`, release readiness notes, and state batons.
Maintainer-local Codex skills such as `aya-assets`, `bea-binary-re`,
`bes-career-save`, and `onslaught-engine-source` are conveniences that route
agents to those tracked docs and tools; public contributors do not need those
user-local skill files to build, test, or review the repo.

Do not commit repo-local `.codex/skills`, Codex auth/session/cache/log/plugin
state, or copied runtime skill caches. If the project later needs an installable
public skill pack, create it as an explicit source artifact with its own review
and hard-payload checks instead of copying a user runtime directory.

For coordinated multi-thread campaigns, read
[coordination/README.md](coordination/README.md) before assigning or accepting
worker changes. That contract defines coordinator, worker, reviewer,
integration, acceptance, path-ownership, resource-lease, report, and local-log
boundaries. Unknown ownership is read-only until the coordinator or integration
owner records a clear lease.

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
- Confirm no game assets, copied executables, save payloads, screenshots/frame
  dumps, raw CDB logs, secrets, or credential material were added.
- Confirm installed game files and original `BEA.exe` were not mutated.
- Keep archived app changes out of scope unless the task explicitly targets an
  archive.
