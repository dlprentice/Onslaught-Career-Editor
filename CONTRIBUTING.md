# Contributing To Onslaught Toolkit

Status: active contributor guide
Last updated: 2026-06-23

This source tree may be the private maintainer tree or a sanitized public
candidate for a WinUI-first Battle Engine Aquila preservation and tooling
project. Public-source exports are curated from the private tree; do not assume
every tracked private file is public release material.

External contributors should work from the curated public candidate or an explicitly sanitized collaborator branch. The private sync repo can contain R4/private material and is not an onboarding or PR base unless access is explicitly covered by maintainer approval and private-data handling rules.

## Developer Start Here

1. Read this file, [SECURITY.md](SECURITY.md), [README.MD](README.MD), and
   [COLLABORATION.md](COLLABORATION.md).
2. Pick one lane: WinUI, AppCore, CLI, docs/release, or public-safe RE docs.
3. Run only the relevant local gates for that lane before review.
4. Keep private game content and private proof material out of public-scope work.
5. For public candidates, use [PUBLIC_SIGNOFF_COMMANDS.md](release/readiness/PUBLIC_SIGNOFF_COMMANDS.md), not the private maintainer sign-off runbook.

Private maintainers and approved private collaborators should also read the
private maintainer operating notes before changing private/runtime/RE/release
posture. Those private coordination notes and policy inputs are not public
release payload.

## Current Direction

- WinUI 3 is the primary user-facing Windows app.
- AppCore and the C# CLI are active support lanes for correctness, patching, and analysis.
- Python under `tools/` is active RE/tooling/lab support, not a product GUI lane.
- Electron, WPF, and the old Python GUI/CLI app are archived/reference surfaces only.
- Static Ghidra RE is closed for function-quality and current-risk accounting; runtime behavior, patch behavior, online play, rebuild parity, and exact no-noticeable-difference parity are separate proof classes.

## Safety Rules

- Never patch or rename the installed Steam game folder or the original `BEA.exe`.
- Patch copied executables only, through the safe-copy profile/patch paths.
- Do not add real game assets, private media, saves, screenshots, runtime proof bundles, Ghidra backups, secrets, state files, `.codex`, `subagents`, `game`, `media`, or `save-attempts` to public-scope work.
- Do not synthesize `.bes` saves from scratch. Start from a real baseline and preserve unknown bytes.
- Do not add GitHub Actions, CI/CD workflows, hosted validation gates, or release automation. Validation for this repo is local.

## License And Game Content Boundary

The MIT license applies only to original project code, docs, metadata, and public-safe tooling. Battle Engine Aquila, its trademarks, executable, media, manuals, save files, screenshots, extracted assets, and third-party runtime components are not licensed by this repository.

Contributors must use a legally obtained local copy of the game and must not submit proprietary game content.

## Development Setup

Required for normal product work:

```powershell
npm run test:public-candidate-inventory # fresh public candidate only
npm install
dotnet build .\OnslaughtCareerEditor.WinUI.slnx --nologo
npm run dev
```

All `npm run ...` gates are defined in the candidate root `package.json`.
Run `npm run test:public-candidate-inventory` before install/build/test outputs
are created when validating a freshly exported public candidate.

Tooling prerequisites:

| Tool | Why it is needed |
| --- | --- |
| Windows 10/11 | WinUI 3 desktop app and UIA tests |
| .NET 10 SDK | WinUI, AppCore, AppCore.Host, CLI, and tests |
| Node.js with npm `11.12.1` target | local script runner and docs/release checks |
| Python 3 with Windows `py` launcher | public-safe tooling, release, patch, and docs checks |
| Git Bash or another `bash` provider | private maintainer release dry-run scripts only |

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
- Preserve existing user/private changes and do not clean up unrelated files.
- Prefer existing AppCore, WinUI, patch catalog, and tooling patterns over new frameworks.
- Put canonical RE findings under `reverse-engineering/`, product strategy under `roadmap/`, and release posture under `release/readiness/`.
- Keep user-facing WinUI wording plain. Avoid internal proof IDs, raw offsets, and maintainer jargon in normal app surfaces.
- Bulky live runtime proof artifacts should use an approved external/private
  artifact root plus the documented arm phrase. Keep only active working copies
  under `subagents/`, and never paste raw runtime proof paths, captures, or CDB
  logs into public docs or PRs.

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

Public-source export is manifest-driven, not a broad copy of the private repo. The current public package manifest is `release/readiness/public_package.json`; the curated export materializes that file as root `package.json` in public candidate trees. The export also materializes `release/readiness/public_AGENTS.md` as root `AGENTS.md` and `release/readiness/public_gitignore.txt` as root `.gitignore` so public contributors do not inherit private maintainer guidance.

Before public-source packaging or sharing work, follow
[PUBLIC_SIGNOFF_COMMANDS.md](release/readiness/PUBLIC_SIGNOFF_COMMANDS.md).
For a freshly exported candidate, run `npm run test:public-candidate-inventory`
before install/build/test outputs are created and verify `EXPORT_PROVENANCE.json`
is present. For ordinary PR work after a tree has build outputs, run the
lane-relevant checks below instead:

```powershell
npm run test:doc-commands
npm run test:md-links
npm run test:public-allowlist
npm run test:repo-hygiene
npm run test:winui-notices
```

Private maintainers run the private release profile, curated manifest, and
`release_package.sh --dry-run` gates from the private source tree before
materializing a public candidate. Those private manifest/accounting gates are
not public PR gates.

Do not publish a public release, push a public release branch, sign binaries, ship an installer, or claim public package readiness without explicit maintainer authorization.

## Opening A PR

- Base public PRs on the sanitized public candidate or an explicitly approved collaborator branch, not a private maintainer clone.
- Fill out the handoff template in [COLLABORATION.md](COLLABORATION.md); it is also suitable as a PR description when no separate template exists.
- Keep the PR scoped to one lane and name the lane in the description.
- Include the exact local gates you ran and any gates intentionally skipped.
- Do not add GitHub Actions, CI/CD workflows, release automation, private assets, saves, screenshots, raw proof bundles, or state files.
- Public contributors changing public/private boundaries should run
  `npm run test:public-allowlist` and `npm run test:repo-hygiene` before
  review. Private maintainers run the release-profile and curated-manifest
  export gates before materializing a new public candidate.

## Review Checklist

Before opening a PR or handing work to another developer:

- The change is narrow and described in plain language.
- Relevant local tests passed and are named in the handoff.
- Public/private boundaries are unchanged or intentionally tightened.
- No private path, game asset, save, screenshot, raw proof artifact, secret, or state file leaked into public-scope docs or manifests.
- WinUI/AppCore changes preserve safe-copy behavior and do not mutate installed game files.
- Online/multiplayer wording separates proof rungs from player-ready capabilities.
- Release accounting artifacts are regenerated only when their inputs changed.

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
- Public-safe RE docs are curated through `reverse-engineering/RE-INDEX.md` in
  public candidates. Private proof forests stay private unless rewritten as
  bounded, link-closed public summaries.
