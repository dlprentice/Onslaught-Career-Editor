# Onslaught Toolkit

Status: active — the product and lane overview
Last updated: 2026-08-31 (Omarchy/Windows-VM contributor routing corrected;
player-facing behavior and older lane claims retain their dated boundaries).
Summary: what this project is, how to play, which surfaces are active, and where
each lane's authoritative document lives.

Onslaught Toolkit is a preservation, tooling, and original-code reconstruction
project for *Battle Engine Aquila* (2003). The primary product is a WinUI 3
Windows app for inspecting and safely editing real save/options files, preparing
copied game profiles, applying evidence-backed patches to copied executables,
and browsing locally supplied media, catalogs, and project lore.

## Playing Battle Engine Aquila on a modern PC

If you own the game and just want to play it, you do not need anything below
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

The toolkit never replaces or mutates the installed retail game. The
GPL-licensed [`rebuild/`](rebuild/README.md) lane is a separate RE-informed
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
from the main menu. The video sequences are currently silent because their
Bink audio streams have not been decoded or assigned to a language. The
frontend owns no gameplay or save-write path. It
currently renders the released Aquila walker/jet, first-person walker cockpit,
bounded original HUD composition, all 33 visible static objects serialized by
Level 100, 1,481 released pine placements, water, the complete height lattice,
the released macro/detail terrain blend, and sky at their bounded reconstruction state; it
does not claim retail parity. The exact retail inputs used by that slice are
materialized locally from the user's own installation and are not distributed
as files in the current source tree or its release packages.

> **Historical correction 2026-07-28; superseded by the current truth above.**
> The entry-path sentence previously read "It now
> enters through a bounded released-style click-to-start, main menu, Level 100
> selector, and loading handoff into the canonical Level 100 simulation." That
> understated shipped work by five screens. Nothing was withdrawn, and the
> career-name page still persists nothing — see
> [`rebuild/README.md`](rebuild/README.md)'s `## Current truth` for the full list
> and its authority.

## Active surfaces

| Path | Owner |
| --- | --- |
| `OnslaughtCareerEditor.WinUI/` | Primary Windows user experience |
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

The current engineering host is Omarchy Linux. It owns Git, documentation,
Python tools, reverse engineering, and the Core/Client/headless rebuild.
AppCore source compiles here, but its full suite, WinUI 3, the Windows-targeted
CLI, and the currently admitted Godot runtime/build/smoke/capture routes remain
Windows-only. An isolated Windows 11 evaluation VM is prepared outside the
repository at `local-data/windows-vm/`, but it is not yet
defined or running; there is no current native Windows or controlled Godot
execution route until its separate activation gate completes.

Common requirements:

- .NET 10 SDK with the .NET 8 targeting/runtime support used by the rebuild
- Node.js 24.x with npm 11.12.x
- Python 3 available as `python`
- PowerShell 7 for rebuild and Godot tooling
- A lawfully obtained Battle Engine Aquila installation for retail-aware and
  rebuild workflows
- Windows 10 or 11 for WinUI, CLI, and the currently admitted controlled Godot
  execution/capture route

For a fresh checkout:

```bash
git clone --recurse-submodules https://github.com/dlprentice/Onslaught-Career-Editor.git
cd Onslaught-Career-Editor
```

For an existing checkout, initialize the pinned source references once with
`git submodule update --init --recursive`.

On Omarchy, start with the portable gates:

```bash
npm run test:docs
npm run test:safety
```

Root [`package.json`](package.json) is the command authority. See
[`VALIDATION.md`](VALIDATION.md) for proportional command selection and
[`CONTRIBUTING.md`](CONTRIBUTING.md) for contribution boundaries.

The retail-backed Core/Client/headless lanes also need ignored local inputs.
On Linux, `prepare:rebuild-assets` selects the canonical checkout's real
`local-lab/rebuild-godot` staging owner. A genuinely fresh canonical clone has
no ignored `local-lab/`; create that private owner once from the canonical
checkout only—never as a child-worktree twin or link—then name the retail path
on its first materialization:

```bash
mkdir -m 700 ./local-lab
npm run prepare:rebuild-assets -- --game-root "/absolute/path/to/Battle Engine Aquila"
npm run test:rebuild-core
npm run test:rebuild-client
```

Inside the activated Windows VM, use the Windows lanes:

```powershell
npm test
npm run dev
npm run test:appcore
npm run test:ui
npm run test:ui-runtime
npm run test:cli
npm run run:rebuild-godot
```

`npm test` builds the active solution once, then checks the consequential
save/codec/write/copy/patch contracts and the static WinUI accessibility audit.
It deliberately excludes broad UI, native Godot, release packaging, Ghidra,
local runtime evidence, and historical accounting. It is a Windows-VM command,
not the Linux default. Use the smallest focused host-appropriate command.

The Level 100 Opening Slice currently launches only inside the activated
Windows VM. Its first run downloads and verifies the pinned Windows Godot .NET
archive into a per-user cache, detects the VM's retail installation, and
materializes the exact supported rebuild inputs to ignored local paths. For a
custom location, run `pwsh ./rebuild/tools/Run-FirstFlight.ps1 -GameRoot
"<game folder>"` in the VM. A native Linux Godot 4.7.1 installation exists, but
it is not yet admitted by the repository's per-file toolchain manifest or smoke
runner and therefore is not a supported execution route.
The VM should use its own Git checkout or verified transfer; do not share the
host checkout, home directory, SSH agent, Docker socket, or archive drives as
guest-writable state.

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
[`release/readiness/PUBLIC_SIGNOFF_COMMANDS.md`](release/readiness/PUBLIC_SIGNOFF_COMMANDS.md).
