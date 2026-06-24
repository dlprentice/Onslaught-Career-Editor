# Contributing To Onslaught Toolkit

Status: active contributor guide
Last updated: 2026-06-23

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

1. Read this file, [SECURITY.md](SECURITY.md), [README.MD](README.MD), and
   [COLLABORATION.md](COLLABORATION.md).
2. Pick one lane: WinUI, AppCore, CLI, docs/release, or public-safe RE docs.
3. Run only the relevant local gates for that lane before review.
4. Keep actual game payloads, secrets, and bulky generated runtime captures out
   of git unless a maintainer explicitly changes that payload rule.
5. Use [PUBLIC_SIGNOFF_COMMANDS.md](release/readiness/PUBLIC_SIGNOFF_COMMANDS.md) for public-source/release signoff checks.

Read [LOCAL_LAB_OVERLAY.md](LOCAL_LAB_OVERLAY.md) before adding or moving local
game, media, save, Ghidra, proof, or agent-output material.

## Current Direction

- WinUI 3 is the primary user-facing Windows app.
- AppCore and the C# CLI are active support lanes for correctness, patching, and analysis.
- Python under `tools/` is active RE/tooling/lab support, not a product GUI lane.
- Electron, WPF, and the old Python GUI/CLI app are archived/reference surfaces only.
- Static Ghidra RE is closed for function-quality and current-risk accounting; runtime behavior, patch behavior, online play, rebuild parity, and exact no-noticeable-difference parity are separate proof classes.

## Safety Rules

- Never patch or rename the installed Steam game folder or the original `BEA.exe`.
- Patch copied executables only, through the safe-copy profile/patch paths.
- Do not add real game assets, copied executables, private media/input payloads,
  local save payloads, screenshots, frame dumps, raw CDB logs, full Ghidra
  databases/backups, secrets, build output, `game`, `media`, or `save-attempts`
  to tracked source work.
- Do not synthesize `.bes` saves from scratch. Start from a real baseline and preserve unknown bytes.
- Do not add GitHub Actions, CI/CD workflows, hosted validation gates, or release automation. Validation for this repo is local.

## License And Game Content Boundary

The MIT license applies only to original project code, docs, metadata, and public-safe tooling. Battle Engine Aquila, its trademarks, executable, media, manuals, save files, screenshots, extracted assets, and third-party runtime components are not licensed by this repository.

Contributors must use a legally obtained local copy of the game and must not submit proprietary game content.

## Development Setup

Required for normal product work:

```powershell
npm install
dotnet build .\OnslaughtCareerEditor.WinUI.slnx --nologo
npm run dev
```

All `npm run ...` gates are defined in the root `package.json`.

Tooling prerequisites:

| Tool | Why it is needed |
| --- | --- |
| Windows 10/11 | WinUI 3 desktop app and UIA tests |
| .NET 10 SDK | WinUI, AppCore, AppCore.Host, CLI, and tests |
| Node.js with npm `11.12.1` target | local script runner and docs/release checks |
| Python 3 with Windows `py` launcher | public-safe tooling, release, patch, and docs checks |
| Git Bash or another `bash` provider | release dry-run scripts when packaging requires Bash |

Use `ONSLAUGHT_APP_CONFIG_ROOT` when you need isolated app config during local
tests instead of the default `%APPDATA%\OnslaughtCareerEditor` location.

Useful quick checks:

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

Run only the gates relevant to your change, but run them locally before asking for review. `npm run test:md-links` writes ignored reports under `subagents/md-link-check`; do not commit those reports.

## Change Expectations

- Keep patches small and path-scoped.
- Read the relevant files before editing.
- Preserve existing user changes and do not clean up unrelated files.
- Prefer existing AppCore, WinUI, patch catalog, and tooling patterns over new frameworks.
- Put canonical RE findings under `reverse-engineering/`, product strategy under `roadmap/`, and release posture under `release/readiness/`.
- Keep user-facing WinUI wording plain. Avoid internal proof IDs, raw offsets, and maintainer jargon in normal app surfaces.
- Bulky live runtime proof artifacts should use an approved external artifact
  root plus the documented arm phrase. Track compact proof summaries, checkers,
  and state updates; keep copied-game frames, raw captures, and raw CDB logs out
  of git.

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

## Online Multiplayer Work

Online multiplayer is active research and implementation work, not a released capability.

Current proof classes support same-workstation safe-copy control and host-helper delivery rungs. They do not prove public matchmaking, native BEA netcode, second-host LAN play, active P3/P4 original-binary gameplay, or scalable online sessions.

Host/Join UI must stay hidden or disabled until there is a real distinct endpoint command-source proof and a source-bound runtime-causality proof for the copied game. Loopback, synthetic, WSL-only, fixture, or same-process proofs cannot be promoted to player-ready online play.

## Public Release Boundary

The public repo is the primary working repo, but public release assets are still
intentional release artifacts. Do not confuse local ignored lab material with
published source or ZIP payload.

Before public-source packaging or sharing work, follow
[PUBLIC_SIGNOFF_COMMANDS.md](release/readiness/PUBLIC_SIGNOFF_COMMANDS.md).
For ordinary PR work after a tree has build outputs, run the lane-relevant
checks below:

```powershell
npm run test:doc-commands
npm run test:md-links
npm run test:public-allowlist
npm run test:repo-hygiene
npm run test:winui-notices
```

Do not publish a public release, push a public release branch, sign binaries, ship an installer, or claim public package readiness without explicit maintainer authorization.

## Opening A PR

- Base public PRs on this public repo unless a maintainer explicitly assigns a separate branch or private workspace.
- Fill out the handoff template in [COLLABORATION.md](COLLABORATION.md); it is also suitable as a PR description when no separate template exists.
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
- RE docs are indexed through `reverse-engineering/RE-INDEX.md`. Track compact
  proof summaries and checkers; keep copied-game payloads, frames, raw CDB logs,
  and full Ghidra databases in local overlays.
