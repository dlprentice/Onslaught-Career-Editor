# AGENTS.md

Status: public-primary contributor agent guide
Last updated: 2026-07-12

This file is the public-primary agent guide for Onslaught Toolkit. Treat this
checkout as the normal collaboration and day-to-day working repo. Raw project
history and working material are allowed here when useful: RE docs, wave notes,
state batons, agent reports, readiness docs, proof summaries, checkers, and
tooling. Ignored local overlays are reserved for hard payloads such as actual
game files, copied executables, private media/input files, full Ghidra databases
or backups, secrets, build output, and bulky generated runtime captures.

Maintainer Codex sessions follow their current global model/consult contract.
That local contract governs review tooling and acceptance; it is not project
architecture and public contributors do not need it to use this repo.

## Current Direction

- WinUI 3 is the primary user-facing Windows app.
- `OnslaughtCareerEditor.AppCore` holds shared correctness logic for saves,
  options, patch planning, media/catalog support, and safe-copy workflows.
- `OnslaughtCareerEditor.Cli` is a C# support CLI.
- Python under `tools/` supports repo tooling, validation, asset/RE support,
  and local lab workflows. It is not a product GUI lane.
- `rebuild/` is the active GPL-licensed, RE-informed original-code rebuild
  lane. Its deterministic Core remains independent of WinUI, render engines,
  reference-source projects, and proprietary payloads.
- Electron, WPF, and the old Python GUI/CLI are archived/reference lanes only.
- Static reverse-engineering docs, runtime proof summaries, state batons, and
  agent reports are tracked project material unless they embed actual game
  payloads or secrets.

## First Rules

- Always read `README.MD`, the nearest nested `AGENTS.md`, and the files directly
  related to the change. Use `CONTRIBUTING.md` for setup, lane gates, state, or
  handoff details and the task router below for other context; do not load every
  front-door document by default.
- Keep changes narrow and path-scoped.
- For substantive or high-risk work, obtain independent review proportionate
  to the risk. Maintainer Codex sessions use one review envelope from their
  global contract; routine follow-through does not recursively start new
  reviews. The assigned writer owns only its leased edits and validation;
  commit, push, publication, and final acceptance require explicit current
  authorization and are never granted by branch ownership or review output.
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
- Do not create recursive readiness, checklist, command-arm, or proof-plan
  chains. Prefer executable code, a focused test/checker, one accepted behavior
  contract, or a plainly documented concrete blocker.
- Stuart's source and the legacy AYA extractor are architecture/tooling
  references, not Steam behavior or format-completeness authority. Steam static
  evidence is authority for bounded released-code identity/structure claims at
  its demonstrated confidence; controlled copied-runtime evidence establishes
  observed causality, behavior, and measured values.

## Project Map

- Product: `OnslaughtCareerEditor.WinUI/`; shared correctness:
  `OnslaughtCareerEditor.AppCore/`; support CLI: `OnslaughtCareerEditor.Cli/`.
- Tests: `OnslaughtCareerEditor.AppCore.Tests/` and
  `OnslaughtCareerEditor.UiTests/`; tooling: `tools/`.
- Rebuild: `rebuild/`; current RE front door: the short header at the top of
  `reverse-engineering/RE-INDEX.md`; archived apps: `archive/`.

## Task Router And Validation

Root `package.json` is command authority. `npm test` is the fresh-clone and
broad active-product baseline; `npm run dev` launches WinUI. Do not run the
roughly whole-repo release/payload suites for every narrow edit. Select the
smallest gate that proves the changed contract, and name intentionally skipped
gates in the handoff.

- WinUI/AppCore/CLI/patch work: use the matching `CONTRIBUTING.md` lane and
  focused tests. Patch work also reads `patches/CATALOG_CONTRACT.md` and uses
  patch-engine/safe-copy gates when those contracts change.
- Executable RE, runtime, Ghidra, saves/options, or assets: read `SECURITY.md`,
  `LOCAL_LAB_OVERLAY.md`, and the current subsystem doc. Use read-only
  inspection first and the focused checker/test; live mutation or launch needs
  separate authority. Private-corpus breadth never proves completeness.
- Rebuild: read `rebuild/AGENTS.md`, `rebuild/PROVENANCE.md`, and
  `rebuild/README.md`. Run `npm run test:rebuild`; add the native Godot smoke
  only for native render/input/toolchain/launch changes.
- Docs: use `git diff --check` and only the affected mirror, JSON, command, or
  link checks. Release or repo-boundary work instead follows `README.RELEASE.md`
  and `release/readiness/PUBLIC_SIGNOFF_COMMANDS.md`.
- Explicit `/goal`: read `goal.policy.md`, then `goal.campaign.md`, then
  `goal.md`. For the durable full-reconstruction campaign use the slash text in
  `roadmap/goals/full-rebuild-campaign-slash-goal.md`. One explicitly designated
  sole sequential worker may own implementation, integration, canonical state,
  validation, and version control while its parent only supervises and reports.
  Two normal Codex Desktop tasks may use verified `list_threads`, `read_thread`,
  and `send_message_to_thread` controls plus a no-action round-trip probe. A
  directly spawned subordinate agent with native collaboration controls is an
  alternative. This compact topology does not activate the coordination
  overlay.

## Setup

```powershell
dotnet --version # must be .NET SDK 10.x
dotnet --list-runtimes # must include Microsoft.NETCore.App 8.x
node --version # must be v24.x
npm --version  # must satisfy >=11.12 <12; npm@11.12.1 is the packageManager target
py -3 --version
npm test
npm run dev
```

This active-product path needs no game install, submodule checkout, Ghidra
database, or `npm install`. Root `package.json` is the command authority;
`npm install` is only for deliberate archived Electron inspection. Initialize
submodules before public allowlist or release signoff. Validation also requires
Python 3 through the Windows `py` launcher because docs/release/tooling checks
use `py -3`.

## Common Local Gates

Run the smallest gate set that matches your change.
Use [VALIDATION.md](VALIDATION.md) for the measured change-class matrix. Do not
run the individual WinUI build/AppCore/UI commands cumulatively with
`test:winui-primary-lane` unless diagnosing a failure.

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
npm run build:rebuild-core
npm run test:rebuild
```
<!-- public-package-commands:end -->

Run `npm run test:hard-payload-safety` before pushing boundary-sensitive work.
It checks for tracked hard payloads and obvious secrets; it is not meant to hide
normal RE notes, state batons, agent reports, or proof summaries.

Current-doc edit loops use `npm run test:doc-commands` and
`npm run test:md-links:public-core`. Broad historical-doc closeout uses
`npm run test:doc-commands-all` and `npm run test:md-links`. Runtime-helper
changes use `npm run test:runtime-tooling-safety`; the 95-child copied-runtime
proof aggregate is not an ordinary contributor gate.

Run .NET build/test commands serially. UI Automation and visual claims require
native WinUI checks; browser or fixture success is not native runtime proof.
In `reverse-engineering/RE-INDEX.md`, start with the short current front door
and targeted subsystem links. Do not load or follow its historical proof-plan
body unless a current document names a specific record or the task genuinely
requires claim lineage; historical plans never override current evidence.

## Public / Local Boundary

The public repo tracks useful source, tools, RE notes, compact proof summaries,
and state. Keep actual/copy game payloads, arbitrary saves, extracted media,
full Ghidra stores/backups, raw captures/logs, secrets, and generated output in
ignored roots from `LOCAL_LAB_OVERLAY.md`. The only tracked real-save exception
is immutable `tests_shared/fixtures/gold_career_save.bin`; do not generalize it.

## Agent Skill Guidance

Maintainer-local Codex skills such as `aya-assets`, `bea-binary-re`,
`bes-career-save`, and `onslaught-engine-source` are conveniences that route
agents to tracked repo truth; they are not authority and public contributors do
not need them. If a skill conflicts with current repo evidence, preserve the
repo truth and report the drift; maintainers correct the skill in its separate
durable source. Never commit runtime skill/plugin/auth/session/cache/log state.

For genuinely concurrent multi-writer campaigns, read
[coordination/README.md](coordination/README.md) before assigning or accepting
worker changes. Unknown ownership is read-only. A supervising parent plus one
sole sequential implementation worker remains single-writer work: the worker
reconciles `goal.md`, canonical state batons, and shared front-door truth, while
the parent does not make competing repository or campaign mutations. Do not
use concurrent `codex exec resume` calls to simulate parent-to-worker steering.
If a resumed or CLI-origin task lacks Desktop thread tools, start a fresh
Desktop supervisor task instead of resuming or forking the stale task.

## WinUI Rules

- Keep normal user wording plain. Hide proof IDs, raw offsets, and maintainer
  jargon behind details surfaces or docs.
- Back user-visible behavior with AppCore where practical.
- Preserve stable automation IDs. Use focused WinUI/AppCore tests plus the
  relevant native visual/UIA proof, rebuilding WinUI before native UIA smoke.

## Patch/Mod Rules

- Patch only copied executables and app-owned artifact roots.
- Verify original bytes before applying a patch and patched bytes after.
- Live runtime proof must bind executable path/hash, PID/start time, exact
  top-level window, and loaded `BEA.exe` module path/base/size. PID alone is not
  identity. Derive runtime addresses from live module base plus RVA, and
  revalidate the same receipt before debugger/input actions; preferred VAs and
  file offsets are not process identity.
- Keep patch descriptions bounded to what is proven.
- Do not claim gameplay improvement, online play, or runtime behavior unless a
  matching proof exists.

## Rebuild Rules

- Read `rebuild/AGENTS.md` and `rebuild/PROVENANCE.md` before editing the
  rebuild.
- Keep deterministic simulation in `OnslaughtRebuild.Core`; rendering clients
  are input/snapshot adapters and must not own simulation truth.
- Translate retail findings through an accepted public-safe behavior contract
  that separates source hypotheses, Steam static evidence, copied-runtime
  measurements, tolerances, and non-claims. The rebuild cannot prove retail
  truth by agreeing with itself.
- Do not call the active RE-informed implementation strict clean-room or
  parity-complete. A strict clean-room lane is a future, separately staffed
  specification/implementation/acceptance process.

## Online And Handoff

Online multiplayer is research, not a released capability. Host/Join stays
disabled until distinct-endpoint command-source and source-bound copied-runtime
causality proofs are accepted; loopback or same-workstation evidence is not
player-ready netplay. Use `COLLABORATION.md` for the handoff, naming changed
paths, exact validation, skipped gates, payload boundary, state disposition,
and confirmation that installed game files/original `BEA.exe` were untouched.
