# Contributing To Onslaught Toolkit

Status: active contributor guide
Last updated: 2026-07-11

This public source tree is the primary collaboration and day-to-day working repo
for a WinUI-first Battle Engine Aquila preservation and tooling project. Raw
project history and working material can be tracked here: RE notes, wave notes,
readiness docs, proof summaries, checkers, and
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

[VALIDATION.md](VALIDATION.md) is the current measured change-class matrix. It
separates focused edit-loop checks, active-product handoff, runtime-tooling
safety, boundary closeout, release signoff, and historical proof.

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

Run only the gates relevant to your change, but run them locally before asking
for review. Do not stack `build:winui`, `test:appcore`, and `test:winui` on top
of `test:winui-primary-lane` for the same broad handoff: the wrapper builds the
complete solution once, runs both test projects from that build, and shuts down
build servers. The individual commands remain focused diagnostics.

For minor current-doc changes use `npm run test:doc-commands` and
`npm run test:md-links:public-core`; add `test:doc-commands-all` and the normal
all-tree `test:md-links` only when historical or broad tree documentation
changes. Runtime-helper changes use `npm run test:runtime-tooling-safety`; the
copied-runtime proof sweep is maintainer research, not ordinary AppCore
acceptance. Receipt-bound walker measurement changes use the focused
`npm run test:battleengine-walker-measurement-contract` gate; add the broad
runtime-tooling gate only when shared profile, CDB, input, or smoke helpers also
change. `npm run test:md-links` writes ignored reports under
`.artifacts/md-link-check`; do not commit those reports.

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
  and focused documentation; keep copied-game frames, raw captures, and raw CDB logs out
  of git.

## WinUI UI/UX Contributions

- Use `OnslaughtCareerEditor.WinUI/` for the native app and `OnslaughtCareerEditor.AppCore/` for behavior that can live below the UI.
- Preserve or add stable `AutomationProperties.AutomationId` values for actionable controls and named inputs.
- Rebuild the WinUI project before native UIA or visual smoke so tests do not launch stale binaries.
- UIA proof, static XAML/code guards, visual screenshots, and copied-runtime proof are separate evidence classes; do not substitute one for another.
- Useful public direction docs: `roadmap/winui-toolchain-and-qa-direction.md`, `roadmap/winui-ui-ux-redesign-radar.md`, `COLLABORATION.md`, and `AGENTS.md`.
- For the large `tools/` folder, start with `tools/README.md` before treating an individual helper as a public PR gate.

The opt-in unattended Home arrival-focus and visual acceptance gate rebuilds
the repository WinUI app, launches isolated first-run and synthetic-ready
states, and publishes receipt-bound normal/760 evidence under ignored
`local-lab/winui-home-native-visual-focus/`:

```powershell
npm run test:winui-home-native-visual-focus
```

The command fails unless its TRX contains exactly one executed passing native
test and that test publishes exactly one fresh schema-3 manifest. Each capture
is linked to full process/start/hash/HWND identity, owner-bound UIA plus
app-side focus/input endpoints, stable visual markers, and meaningful opaque
pixel coverage. Build and test are pinned to Debug/win-x64; one invocation ID
and the runner's post-build executable/DLL hashes bind the child test and its
owned accepted/partial evidence. Partial publication, skipped/zero tests, stale
artifacts, or a nonzero Toolkit/testhost/vstest/BEA/debugger process census
fail the gate. Its evidence and runner roots are exact repository `local-lab`
children, and recursive cleanup refuses any nested reparse point. The shared
command runner captures PID/start/path for its
spawned build or test root and revalidates that identity before timeout
process-tree termination. This native command is not part of ordinary
non-runtime UI tests or release signoff; its screenshots, app data, TRX, and
manifests remain local evidence.

Save Editor first-use or Game Options workflow/layout changes use the separate
unattended native Save Lab gate. It copies the tracked immutable gold-save
fixture into owned staging, constructs a deterministic 10,004-byte options
buffer, and drives only UIA Value, Toggle, ExpandCollapse, Scroll, ScrollItem,
Selection, Focus, and Invoke patterns:

```powershell
npm run test:winui-save-lab-native-workflow
```

The command publishes eight receipt-bound normal/760 captures and two workflow
receipts under ignored `local-lab/winui-save-lab-native-workflow/`. It requires
an exact 1/1 native TRX, full repo-build process/start/hash/HWND identity,
unchanged inputs, distinct app-owned outputs whose Goodies/P1 semantics are
independently parsed from retained bytes, stable owner-bound focus and marker
geometry, one fresh schema-1 manifest, and a zero final process census. Its
ignored roots are exact repository `local-lab` children, and recursive cleanup
refuses any nested reparse point. Manifest ownership is rechecked after full
artifact validation and immediately before receipt-authorized process cleanup;
the existing regular manifest file must retain its validated hash.
Owned WinUI cleanup revalidates PID/start/path before bounded close or
process-tree kill.
A final survivor is force-cleaned only when it matches this invocation's
validated launch receipt; remediation still fails the gate. It never invokes
File Explorer or the controller-guide browser action, never reads
installed-game files, and is native Toolkit evidence—not retail behavior,
save-format completeness, or release acceptance.

Media catalog or Asset Library workflow/layout changes use a third unattended
native gate. It creates an exact zero-payload game-shaped Media tree, a
schema-2 Asset catalog, one contrast texture, and one minimal binary-FBX
triangle; the zero-byte synthetic `BEA.exe` is only a directory marker and is
never launched:

```powershell
npm run test:winui-media-asset-native-workflow
```

The command owns three isolated WinUI launches for audio selection, deferred
video selection, and texture/model inspection. It performs no Play, reveal,
browse, clipboard, export, or package action and rejects any loaded LibVLC
module. Acceptance requires an exact 1/1 native TRX, the canonical thirteen
fixture records, eight normal/760 receipt-bound captures, distinct
process/start launches, per-launch hash/HWND ownership, the exact Toolkit-owned
application payload closure, exact semantic readbacks, marker-level raster
activity, independently reparsed catalog/FBX/PNG content, and a zero final
process census. Its accepted evidence and runner scratch remain below
the exact ignored `local-lab/winui-media-asset-native-workflow/` and
`local-lab/winui-media-asset-native-workflow-runner/` roots. This is native
Toolkit evidence, not retail behavior, asset-format completeness, playback
acceptance, or release evidence.

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
- Use synthetic command tapes and original procedural content for tracked
  source and ordinary acceptance. Optional user-supplied local meshes, including
  user-extracted retail assets, may load only from ignored
  `local-lab/rebuild-godot/` through the dedicated exact-root local command.
  Bootstrap accepts converted GLB/OBJ only from `staging/from-export`, requires
  explicit or unambiguous player and terrain roles, verifies one immutable
  content-addressed generation, publishes its manifest last, and never activates FBX.
  Runtime wording stays origin-neutral unless an exporter receipt/hash is bound.
  These files are never committed, redistributed, simulation truth, or parity
  evidence. Do not import retail binaries, decompiler output, or mechanically
  translated reference-source code.
- Treat the current implementation as RE-informed original code. A strict
  clean-room claim requires separately staffed specification, implementation,
  and acceptance teams with documented information barriers.
- Run `npm run test:rebuild` for the ordinary deterministic contract gate; it
  does not invoke the Godot downloader or native window, though normal .NET
  restore may use configured package sources. Intentional state or replay-
  contract changes must update and review the independent final-state and
  rolling-trace goldens.
- Run `npm run test:rebuild-local-assets` for focused manifest, mesh-bound, and
  local-lab write-safety checks. It uses synthetic files only.
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
