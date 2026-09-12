# Onslaught Toolkit

Status: active — the product and lane overview
Last updated: 2026-09-12 (command reference consolidated from the agent guide).
Summary: what this project is, how to play, which surfaces are active, and where
each lane's authoritative document lives.

Onslaught Toolkit is a preservation, tooling, and original-code reconstruction
project for *Battle Engine Aquila* (2003), with three coequal outcomes: retail
reverse engineering, a 1:1 Godot reconstruction, and a Godot preservation/toolkit
companion for Linux and Windows. The companion covers real save/options files,
safe game copies, evidence-backed patches, media, catalogs and lore.

The active companion is the [Godot Save Lab](companion/OnslaughtToolkit.Godot/README.md),
which reuses AppCore to inspect a real save and write a supported kill-count edit
to a separate copy. Its service tests pass on Linux and its native shell opens;
the complete UI write/reopen workflow remains to be demonstrated. The broader
WinUI toolkit stays available as migration material. The approved phase also
advances native rebuild play and targeted retail RE; see [PROGRAM.md](PROGRAM.md).

## Using the existing Windows toolkit

These instructions describe the existing Windows release, not a Godot or Linux
companion build. If you own the game and just want to play it, you do not need anything below
this section — no .NET, no Node, no Python, no build.

1. Download the portable ZIP from
   [Releases](https://github.com/dlprentice/Onslaught-Career-Editor/releases).
   The ZIP contains one `Onslaught-Toolkit/` folder. Extract it, then open that
   folder. "Extract Here" no longer scatters `app/` next to your other files.
2. Right-click the ZIP → Properties → tick **Unblock** before you extract. That
   is the easiest way to avoid the next step.
3. Run `Launch Onslaught Toolkit.cmd` from the `Onslaught-Toolkit/` folder. The
   build is unsigned, so if you skipped the Unblock step Windows shows
   *"Windows protected your PC"* — choose **More info → Run anyway**.
4. The app looks for your Steam install on its own. If it cannot find it, point
   it at your game folder once in Settings.
5. Open **Windowed & Mods**, choose **Create safe copy**, then **Launch**.

That copy runs windowed at 1600x900 with the widescreen correction applied. By
default your installed game is only read and everything happens in a separate
folder the app owns. If you would rather patch your own install, Windowed & Mods
will — after copying and verifying your original executable, so you can put it
back. Optional extras (a subtitle mod, early flight, a local
split-screen preset) stay off until you turn them on.

You can also edit a career save, browse the soundtrack, voice lines, cutscenes
and briefings, and read the lore library — all from the same app.

This is an unofficial community project. It is not affiliated with or endorsed
by the game's publishers or rights holders. Repository licenses cover their
respective project code and documentation; they grant no rights in the retail
game, its assets, names, or trademarks.

The GPL-licensed [`rebuild/`](rebuild/README.md) lane is a separate RE-informed
implementation with deterministic Core behavior and a Godot handling lab. It
now enters through the locally materialized released Lost Toys logo, opening
montage, and splash, then click-to-start, main menu, a career-name entry page
(new-name or injected read-only career selection; it creates no save), the
career-law world selector, mission briefing, select configuration, and loading.
Loading still constructs only the Level 100 world; the first-time intro then
plays before gameplay activation. After a completed Level 100 mission, the
frontend projects the bounded debrief result and applies the in-memory
career-law update; Confirm or Back then returns to the selector where unlocked
World 110 may be selected, but the host cannot yet construct that world. An
Options page and a quit confirmation are reachable
from the main menu. Startup logo/montage audio and the English Level 100 intro
are decoded locally; the intro has produced native audio, while the newly added
logo/montage tracks still need a playback check. The
frontend owns no gameplay or save-write path. It
currently renders the released Aquila walker/jet, first-person walker cockpit,
bounded original HUD composition, all 33 visible static objects serialized by
Level 100, 1,481 released pine placements, water, the complete height lattice,
the released macro/detail terrain blend, and sky at their bounded reconstruction state; it
does not claim retail parity. The exact retail inputs used by that slice are
materialized locally from the user's own installation and are not distributed
as files in the current source tree or its release packages.

## Existing source surfaces

| Path | Owner |
| --- | --- |
| `companion/OnslaughtToolkit.Godot/` | MIT Godot Save Lab; separate from the GPL rebuild |
| `OnslaughtCareerEditor.WinUI/` | Retained Windows companion shell and migration material |
| `OnslaughtCareerEditor.AppCore/` | Save, options, safe-copy, patch, media, catalog, and lore correctness |
| `OnslaughtCareerEditor.Cli/` | Unshipped maintainer adapter over AppCore |
| `rebuild/` | GPL RE-informed deterministic reconstruction |
| `reverse-engineering/` | Provenance-bounded technical evidence and format notes |
| `lore/` | Canonical public lore/history library |
| `tools/` | Focused extraction, validation, release, Ghidra, and copied-runtime helpers |

[`PROJECT-INDEX.md`](PROJECT-INDEX.md) maps source ownership, application flow,
project dependencies, tests, and the remaining root owners without duplicating
their current capability or evidence claims.

Retired Electron, Python GUI, WPF, generated readiness waves, and mirrored
documentation remain available in Git history; they are not current source
lanes. [`CURRENT_CAPABILITIES.md`](CURRENT_CAPABILITIES.md) describes what the
current product does and what remains unproven.

## Build and run

Everything from here down is for contributors. Players need only the section
above.

The engineering host is Omarchy Linux. Native Godot build/run routes use the
installed pinned Godot 4.7.2 .NET engine. The rebuild's synthetic native smoke
and a live session's two deterministic replays passed; full tutorial acceptance
is unfinished. AppCore targets .NET 8 and 10. Its complete legacy suite, WinUI,
and the Windows-targeted CLI retain Windows dependencies. The never-built evaluation
VM and installer media were retired on September 12. No Windows host is provisioned;
Linux development does not depend on one, and Linux tests do not certify Windows behavior.

Common requirements:

- .NET 10 SDK named in `global.json`, plus the rebuild's pinned .NET 8 SDK from
  `~/.local/opt/game-pipeline`
- Node.js 26.7 and npm 11.19 from mise
- Python 3.14 available as `python`; root commands use forward-slash paths
- Godot 4.7.2 .NET with its bundled C# packages; AppCore dependencies restored
  into the local NuGet cache
- A lawfully obtained Battle Engine Aquila installation for retail-aware and
  rebuild workflows
- Windows 10 or 11 and PowerShell 7 only for retained Windows procedures

For a fresh checkout:

```bash
git clone --recurse-submodules https://github.com/dlprentice/Onslaught-Career-Editor.git
cd Onslaught-Career-Editor
```

For an existing checkout, initialize the pinned source references once with
`git submodule update --init --recursive`.

On Linux, the companion needs no retail installation:

```bash
npm run build
npm run dev
npm test
npm run test:docs
npm run test:safety
```

Root [`package.json`](package.json) is the command authority. See
[`VALIDATION.md`](VALIDATION.md) for proportional command selection and
[`CONTRIBUTING.md`](CONTRIBUTING.md) for contribution boundaries.

Additional command routes, selected for the affected task:

| Task | Command or owner |
| --- | --- |
| Explicit companion build/run aliases | `npm run build:companion-godot`; `npm run run:companion-godot` (the same routes as `build` / `dev`) |
| Native rebuild smoke/capture | `npm run test:rebuild-godot-smoke`; `npm run capture:rebuild-godot`. Runtime commands require desktop availability under [AGENTS.md](AGENTS.md). |
| Focused tools checks | Affected cases in `python tools/<name>_tests.py`; function-name check alone: `python tools/re_function_doc_names_check.py --strict` |
| Rebuild Core / Client | Select affected tests using [VALIDATION.md](VALIDATION.md). Full commands: `npm run test:rebuild-core` (materializes first), `npm run test:rebuild-client`; `npm run test:rebuild-ferry-sweep` covers the excluded ferry oracle. |
| Headless replay | `npm run run:rebuild-headless -- <args>` |
| Complete-RE verification | Only the command selected by `developer_state.json` → `current_re_authority.verify`; the host attestor is `tools/re_campaign_gen32_host_attestation.py`, with receipts in `local-data/host-attestations/`. |
| Authorized Ghidra work | `ghidraRun` (12.1.3, OpenJDK 21) on `local-lab/ghidra-projects/BEA/BEA.gpr` only; headless scripts live in `tools/*.java`. Follow the [promotion gate](reverse-engineering/ghidra/README.md) for the declared cohort. |

The docs gate checks links, headers, function names and authority pointers;
`test:safety` checks the public payload boundary. [VALIDATION.md](VALIDATION.md)
retains suite timings and historical Core failure/correction receipts. Select
commands for the change; this reference does not require every suite for each edit.

The retail-backed Core/Client/headless lanes also need ignored local inputs.
On Linux, `prepare:rebuild-assets` selects the canonical checkout's real
`local-lab/rebuild-godot` staging owner. A genuinely fresh canonical clone has
no ignored `local-lab/`; create that private owner once from the canonical
checkout only—never as a child-worktree twin or link. Linux Steam libraries are
discovered automatically; an explicit `--game-root` selects another installation:

```bash
mkdir -m 700 ./local-lab
npm run prepare:rebuild-assets -- --game-root "/absolute/path/to/Battle Engine Aquila"
npm run build:rebuild-godot
npm run run:rebuild-godot
```

The launchers put scratch, logs and engine user data under canonical
`local-data/companion/` or `local-data/first-flight/`, including from a Git worktree.
[`rebuild/README.md`](rebuild/README.md) documents runtime modes, input and recording.
`npm test` runs the supported Save Lab and launcher checks without opening a window.
Core/Client changes use their focused test projects, as mapped in `VALIDATION.md`.

The former Windows defaults remain `test:winui`, `dev:winui` and `build:winui`;
`test:appcore`, `test:ui`, `test:cli` and `release:winui-zip` also retain Windows
dependencies. `tools/require_windows_host.py` makes Windows-only scripts fail fast
on Linux; they are not Linux prerequisites.
Historical Windows rebuild launchers have explicit `:windows` aliases; their
older engine manifest needs revalidation against the current managed SDK before
new Windows acceptance. This phase does not activate the VM.

## Data and mutation safety

- Never synthesize `.bes` saves from scratch. Start from a real baseline and
  preserve file length, reserved fields, and unknown bytes.
- Development work targets a verified copied target or an app-created safe game
  copy, never your own installation. The app itself can patch a user's installed
  game on request, and that route goes through
  `BinaryPatchEngine.AuthorizeInstalledGameWrite`, which will not hand back
  permission until a verified original sits beside the target — a precondition,
  not a convention you could accidentally work around.
- Keep game binaries, real saves, Ghidra backups/alternate projects, debugger
  transcripts, private captures, secrets, bulk extraction output, and build
  output out of Git. The reviewed checkpoint under `reverse-engineering/ghidra/`
  is the sole Git-tracked database exception; the only writable project is the
  ignored `local-lab/ghidra-projects/BEA/` owner.
- Do not commit retail assets or their converted copies. Keep them in ignored
  local owners and retain credits/provenance when a deterministic recipe uses
  them. Parser success establishes format support, not visual fidelity. A
  screenshot of the game running is not one of these — a few chosen ones may be
  tracked for the app's own surfaces, under the conditions in
  [`AGENTS.md`](AGENTS.md).
- File extension alone does not establish provenance. Project-authored or
  specifically developer-provided assets may be tracked outside the reserved
  retail-materialization owners when their file-level provenance, license, and
  attribution are clear. Large opaque additions require an explicit reviewed
  hash exception in the existing public-safety check.
- Online multiplayer is not player-ready. The app exposes a local split-screen
  copied-profile preset only; Host/Join remains unavailable.

The tracked regression fixture
[`tests_shared/fixtures/gold_career_save.bin`](tests_shared/fixtures/README.md)
is the reviewed narrow exception to the no-save-payload rule. See
[`SECURITY.md`](SECURITY.md) and
[`LOCAL_LAB_OVERLAY.md`](LOCAL_LAB_OVERLAY.md) for handling local inputs.

## Evidence and provenance

[`reverse-engineering/RE-INDEX.md`](reverse-engineering/RE-INDEX.md) is the
technical evidence front door. Current complete-RE replay selection lives in
[`developer_state.json`](developer_state.json) → `current_re_authority`;
Generation 73 is a projection oracle, not a parent, and Ghidra mutation has a
separate promotion gate. Static analysis proves only
the identities and structures it directly demonstrates; controlled
copied-runtime work is needed for observed behavior and measured values.
Stuart's source and the pinned
[`references/Onslaught`](references/Onslaught) submodule are source references,
not proof of Steam behavior or exact source identity.

The canonical lore library begins at [`lore/_index.md`](lore/_index.md).
[`lore-book/BOOK.md`](lore-book/BOOK.md) is a short reading guide, not a mirror.
Release candidates generate an ignored short-path offline pack from those
canonical inputs.

## Releases and licenses

Published unsigned portable Windows ZIPs, when available, are on
[GitHub Releases](https://github.com/dlprentice/Onslaught-Career-Editor/releases).
The source checkout may be newer than the latest published asset. Building a
candidate does not publish, sign, install, or announce it; see
[`README.RELEASE.md`](README.RELEASE.md).

Repository licensing, third-party notices, source attribution, and the rebuild
GPL boundary remain authoritative in [`LICENSE`](LICENSE),
[`release/readiness/THIRD_PARTY_NOTICES.winui.md`](release/readiness/THIRD_PARTY_NOTICES.winui.md),
[`rebuild/LICENSE`](rebuild/LICENSE), [`rebuild/PROVENANCE.md`](rebuild/PROVENANCE.md),
and [`reverse-engineering/project-meta/attribution.md`](reverse-engineering/project-meta/attribution.md).
Maintainer release checks live in [`README.RELEASE.md`](README.RELEASE.md) and
[`VALIDATION.md`](VALIDATION.md).
