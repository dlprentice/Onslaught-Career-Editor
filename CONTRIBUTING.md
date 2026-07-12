# Contributing To Onslaught Toolkit

Status: active contributor guide
Last updated: 2026-07-11

This public source tree is the primary collaboration and day-to-day working repo
for a WinUI-first Battle Engine Aquila preservation and tooling project. Raw
project history and working material can be tracked here: RE notes, wave notes,
state batons, agent reports, readiness docs, proof summaries, checkers, and
tooling. Ignored overlay folders are for hard payloads: actual game files,
copied executables, private media/input files, full Ghidra databases/backups,
secrets, build output, and bulky generated runtime captures.

External contributors should work from this public repo unless a maintainer
explicitly assigns a separate branch or private workspace.

## Developer Start Here

1. Run `npm test` from a fresh clone. It checks the active product without a
   game install, submodules, Ghidra, or `npm install`.
2. Run `npm run dev` and confirm the WinUI shell opens.
3. Read the
   [repository authority map](roadmap/repo-structure-and-archive-map.md), then
   pick one lane: WinUI, AppCore/CLI, the rebuild, patch/mod safety, docs, or
   RE/Lore.
4. Run the lane-specific gates below before review.
5. Keep actual game payloads, secrets, and bulky generated runtime captures out
   of git. Maintainer policy changes may add narrow public-safe fixtures, but
   they do not authorize proprietary game payloads in public source.
6. Use [PUBLIC_SIGNOFF_COMMANDS.md](release/readiness/PUBLIC_SIGNOFF_COMMANDS.md)
   only for public-source or release signoff.

Read [LOCAL_LAB_OVERLAY.md](LOCAL_LAB_OVERLAY.md) before adding or moving local
game, media, save, Ghidra, proof, or agent-output material.

## Current Direction

- WinUI 3 is the primary user-facing Windows app.
- AppCore and the C# CLI are active support lanes for correctness, patching, and analysis.
- Python under `tools/` is active RE/tooling/lab support, not a product GUI lane.
- `rebuild/` is the active GPL-licensed, RE-informed original-code rebuild
  lane. Its deterministic Core is independent of WinUI and proprietary game
  payloads; it is not a strict clean-room or parity claim.
- Electron, WPF, and the old Python GUI/CLI app are archived/reference surfaces only.
- A prior Ghidra snapshot satisfied narrow name/comment/signature accounting;
  binary-wide semantic completion is not proven and is under deep review.
  Runtime behavior, patch behavior, online play, and rebuild parity are separate
  proof classes.

## Safety Rules

- Never patch or rename the installed Steam game folder or the original `BEA.exe`.
- Patch copied executables only, through the safe-copy profile/patch paths.
- Do not add real game assets, copied executables, private media/input payloads,
  local save payloads, screenshots, frame dumps, raw CDB logs, full Ghidra
  databases/backups, secrets, build output, `game`, `media`, or `save-attempts`
  to tracked source work. The single tracked exception is
  `tests_shared/fixtures/gold_career_save.bin`, the immutable regression
  baseline used by fixture-dependent tests.
- Do not synthesize `.bes` saves from scratch. Start from a real baseline and preserve unknown bytes.
- Do not add GitHub Actions, CI/CD workflows, hosted validation gates, or release automation. Validation for this repo is local.

## License And Game Content Boundary

The root MIT license applies only to original toolkit code, docs, metadata, and
public-safe tooling. `rebuild/` and `references/Onslaught` are separate
GPL-licensed subtrees; the root license does not relicense them. Read
[`rebuild/PROVENANCE.md`](rebuild/PROVENANCE.md) before contributing rebuild
code.

Battle Engine Aquila, its trademarks, executable, media, manuals, save files,
screenshots, extracted assets, and third-party runtime components are not
licensed by this repository.

Contributors must use a legally obtained local copy of the game and must not submit proprietary game content.

## Development Setup

Required for normal product work:

```powershell
dotnet --version # must be .NET SDK 10.x
dotnet --list-runtimes # must include Microsoft.NETCore.App 8.x
node --version # must be v24.x
npm --version  # must satisfy >=11.12 <12; npm@11.12.1 is the packageManager target
py -3 --version
npm test
npm run dev
```

No game install, Git submodule checkout, Ghidra database, or `npm install` is
required for that path. Root `package.json` is the command authority. Its
`npm install` path is retained only for deliberate archived Electron inspection.
Initialize submodules before public allowlist or release signoff because those
gates inspect reference boundaries.

Tooling prerequisites:

| Tool | Why it is needed |
| --- | --- |
| Windows 10/11 | WinUI 3 desktop app and UIA tests |
| .NET 10 SDK | WinUI, AppCore, AppCore.Host, CLI, and toolkit tests |
| .NET 8 SDK/runtime | Rebuild Core/client/headless tests and the Godot .NET client |
| PowerShell 7 (`pwsh`) | Pinned Godot toolchain tests, setup, build, launch, and native smoke |
| Node.js 24.x with npm `>=11.12 <12` (`npm@11.12.1` packageManager target) | local script runner and docs/release checks |
| Python 3 with Windows `py` launcher | public-safe tooling, release, patch, and docs checks |
| Git Bash or another `bash` provider | release dry-run scripts when packaging requires Bash |

Use `ONSLAUGHT_APP_CONFIG_ROOT` when you need isolated app config during local
tests instead of the default `%APPDATA%\OnslaughtCareerEditor` location.

Lane-specific checks:

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
npm run build:rebuild-core
npm run test:rebuild
npm run run:rebuild-headless
npm run run:rebuild-godot
npm run test:doc-commands
npm run test:md-links
npm run test:public-allowlist
npm run test:repo-hygiene
npm run test:winui-notices
```
<!-- public-package-commands:end -->

Run only the gates relevant to your change, but run them locally before asking for review. `npm run test:md-links` writes ignored reports under `subagents/md-link-check`; do not commit those reports.

## Change Expectations

- Keep patches small and path-scoped.
- Read the relevant files before editing.
- Preserve existing user changes and do not clean up unrelated files.
- Prefer existing AppCore, WinUI, patch catalog, and tooling patterns over new frameworks.
- Put canonical RE findings under `reverse-engineering/`, product strategy under `roadmap/`, and release posture under `release/readiness/`.
- Put active rebuild implementation under `rebuild/`; do not extend historical
  proof-plan chains as a substitute for executable source, tests, or a
  documented blocked dependency.
- Keep user-facing WinUI wording plain. Avoid internal proof IDs, raw offsets, and maintainer jargon in normal app surfaces.
- Bulky live runtime proof artifacts should use an approved external artifact
  root plus the documented arm phrase. Track compact proof summaries, checkers,
  and state updates; keep copied-game frames, raw captures, and raw CDB logs out
  of git.

## State Baton Updates

For agent-led or maintainer-led code, docs, runtime proof, release, or
repo-boundary changes, update the relevant state baton before handoff:

- `developer_agent_state.json` for implementation, runtime, tooling, and
  validation truth.
- `documentation_agent_state.json` for docs, release posture, collaboration
  posture, and handoff truth.
- `re_orchestrator_state.json` only when active RE orchestration changes.

Keep state concise and non-secret. For read-only audits, do not edit state just
to satisfy the rule; report the needed state update in the audit result.
External contributors may instead explain that no baton update was made; a
maintainer can fold their PR into the current state files during review.

During coordinated multi-thread campaigns, follow
[coordination/README.md](coordination/README.md). Worker branches do not all edit
canonical state batons; the integration owner reconciles `goal.md`,
`developer_agent_state.json`, `documentation_agent_state.json`, and shared
readiness/front-door docs after write leases are released. Review and acceptance
threads stay read-only.

## WinUI UI/UX Contributions

- Use `OnslaughtCareerEditor.WinUI/` for the native app and `OnslaughtCareerEditor.AppCore/` for behavior that can live below the UI.
- Preserve or add stable `AutomationProperties.AutomationId` values for actionable controls and named inputs.
- Rebuild the WinUI project before native UIA or visual smoke so tests do not launch stale binaries.
- UIA proof, static XAML/code guards, visual screenshots, and copied-runtime proof are separate evidence classes; do not substitute one for another.
- Useful public direction docs: `roadmap/winui-toolchain-and-qa-direction.md`, `roadmap/winui-ui-ux-redesign-radar.md`, `COLLABORATION.md`, and `AGENTS.md`.
- For the large `tools/` folder, start with `tools/README.md` before treating an individual helper as a public PR gate.

## Patch And Mod Work

Executable patch work must be byte-verified and specimen-specific:

- Verify original bytes before applying a patch.
- Verify patched bytes after applying a patch.
- Apply only to copied executables or app-owned artifact roots.
- Keep patch descriptions bounded to what is proven.
- Do not imply runtime behavior, online play, or gameplay improvement without a matching runtime proof.

For WinUI patch/mod UX, the preferred user shape is a safe-copy launcher/mod-manager flow: choose a source game, create a copied game profile, apply selected patches to the copy, and launch the copy from the app. A later native-feeling mega patch can exist only after its individual behaviors are proven.

## Rebuild Work

- Read [`rebuild/AGENTS.md`](rebuild/AGENTS.md) and
  [`rebuild/PROVENANCE.md`](rebuild/PROVENANCE.md) first.
- Keep simulation truth in the deterministic Core. Render clients consume
  inputs and snapshots; they do not own gameplay state.
- Use synthetic command tapes and original procedural content. Do not import
  retail binaries, extracted assets, decompiler output, or mechanically
  translated reference-source code.
- Treat the current implementation as RE-informed original code. A strict
  clean-room claim requires separately staffed specification, implementation,
  and acceptance teams with documented information barriers.
- Run `npm run test:rebuild` for the ordinary deterministic contract gate; it
  does not invoke the Godot downloader or native window, though normal .NET
  restore may use configured package sources. Intentional state or replay-
  contract changes must update and review the independent final-state and
  rolling-trace goldens.
- Run `npm run test:rebuild-godot-smoke` when Godot launch, rendering, input,
  toolchain, or native smoke behavior changes. This separate gate may download
  the pinned engine on first use and must leave no process running.

## Online Multiplayer Work

Online multiplayer is active research and implementation work, not a released capability.

Current proof classes support same-workstation safe-copy control and host-helper delivery rungs. They do not prove public matchmaking, native BEA netcode, second-host LAN play, active P3/P4 original-binary gameplay, or scalable online sessions.

Host/Join UI must stay hidden or disabled until there is a real distinct endpoint command-source proof and a source-bound runtime-causality proof for the copied game. Loopback, synthetic, WSL-only, fixture, or same-process proofs cannot be promoted to player-ready online play.

## Runtime Proof Contributions

Runtime proof work is welcome, but the submitted source change should be small
and reproducible:

- Put required local game, save, media, Ghidra, or proof inputs in ignored
  overlay folders from [LOCAL_LAB_OVERLAY.md](LOCAL_LAB_OVERLAY.md).
- Submit scripts, checkers, schemas, manifests, hashes, compact summaries, and
  bounded readiness notes, not raw frames, WAVs, screenshots, CDB logs, copied
  executables, or full proof bundles.
- Separate self-tests from live proof commands. Live copied-game, CDB, input, or
  Ghidra mutation commands need explicit arm phrases and should fail closed when
  required local inputs are absent.
- Update capability/docs/state only to the evidence level actually proven.

## Public Release Boundary

The public repo is the primary working repo, but public release assets are still
intentional release artifacts. Do not confuse local ignored lab material with
published source or ZIP payload.

Before public-source packaging or sharing work, follow
[PUBLIC_SIGNOFF_COMMANDS.md](release/readiness/PUBLIC_SIGNOFF_COMMANDS.md).
For ordinary PR work, run `npm test` as the common active-product baseline and
add only the lane-specific checks relevant to the change. The whole-repository
`test:public-allowlist`, `test:repo-hygiene`, and notice/package gates are
signoff checks for boundary, release, dependency, or broad documentation
changes; they are not required for every narrow edit.

Do not publish a public release, push a public release branch, sign binaries, ship an installer, or claim public package readiness without explicit maintainer authorization.

## Opening A PR

- Base public PRs on this public repo unless a maintainer explicitly assigns a separate branch or private workspace.
- Use the GitHub PR template for PRs; use [COLLABORATION.md](COLLABORATION.md) for agent handoffs, review requests, or non-GitHub handoff notes.
- Keep the PR scoped to one lane and name the lane in the description.
- Include the exact local gates you ran and any gates intentionally skipped.
- Do not add GitHub Actions, CI/CD workflows, release automation, game assets,
  copied executables, local saves, screenshots, frame dumps, raw CDB logs, or
  secrets.
- Contributors changing hard-payload boundaries should run
  `npm run test:public-allowlist` and `npm run test:repo-hygiene` before
  review.

## Review Checklist

Before opening a PR or handing work to another developer:

- The change is narrow and described in plain language.
- Relevant local tests passed and are named in the handoff.
- Hard-payload boundaries are unchanged or intentionally updated.
- No game asset, copied executable, local save payload, screenshot/frame dump,
  raw CDB log, secret, or credential material leaked into tracked source or
  release manifests.
- WinUI/AppCore changes preserve safe-copy behavior and do not mutate installed game files.
- Online/multiplayer wording separates proof rungs from player-ready capabilities.
- Release accounting artifacts are regenerated only when their inputs changed.
- Ignored local overlays are present only when needed for local proof/tooling and
  are not part of the PR.

## Useful Entry Points

- [README.MD](README.MD)
- [CURRENT_CAPABILITIES.md](CURRENT_CAPABILITIES.md)
- [COLLABORATION.md](COLLABORATION.md)
- [SECURITY.md](SECURITY.md)
- [RELEASE_SCOPE_AND_TEST_COMMANDS.md](RELEASE_SCOPE_AND_TEST_COMMANDS.md)
- [README.RELEASE.md](README.RELEASE.md)
- [reverse-engineering/RE-INDEX.md](reverse-engineering/RE-INDEX.md)
- [roadmap/ROADMAP-INDEX.md](roadmap/ROADMAP-INDEX.md)
- [roadmap/public-roadmap.md](roadmap/public-roadmap.md)
- [roadmap/repo-structure-and-archive-map.md](roadmap/repo-structure-and-archive-map.md)
- [rebuild/README.md](rebuild/README.md)
- RE docs are indexed through `reverse-engineering/RE-INDEX.md`. Track compact
  proof summaries and checkers; keep copied-game payloads, frames, raw CDB logs,
  and full Ghidra databases in local overlays.
