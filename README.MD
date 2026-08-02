# Onslaught Toolkit

Status: active — the product and lane overview
Last updated: 2026-08-01. A player-facing quick start was added at the top,
including the SmartScreen warning a stranger meets before anything else; the
lane sections below it were not re-reviewed and keep their 2026-07-29 boundary.
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
   **Create an empty folder and extract into that** — the ZIP has no top-level
   folder of its own, so extracting into Downloads scatters its contents.
2. Right-click the ZIP → Properties → tick **Unblock** before you extract. That
   is the easiest way to avoid the next step.
3. Run `Launch Onslaught Toolkit.cmd`. The build is unsigned, so if you skipped
   the Unblock step Windows shows *"Windows protected your PC"* — choose
   **More info → Run anyway**.
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
(visual only — it saves nothing), Level 100 selector, mission briefing, select
configuration, and loading. Loading constructs the Level 100 world; the
first-time intro then plays before gameplay activation. An Options page and a
quit confirmation are reachable from
the main menu. The video sequences are currently silent because their Bink
audio streams have not been decoded or assigned to a language. The
frontend owns no gameplay, save, result, or later campaign-selection state. It
currently renders the released Aquila walker/jet, first-person walker cockpit,
bounded original HUD composition, all 33 visible static objects serialized by
Level 100, 1,481 released pine placements, water, the complete height lattice,
the released macro/detail terrain blend, and sky at their bounded reconstruction state; it
does not claim retail parity. The exact retail inputs used by that slice are
materialized locally from the user's own installation and are not distributed
as files in the current source tree or its release packages.

> **Extended 2026-07-28.** The entry-path sentence previously read "It now
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

Retired Electron, Python GUI, WPF, generated readiness waves, and mirrored
documentation remain available in Git history; they are not current source
lanes. [`CURRENT_CAPABILITIES.md`](CURRENT_CAPABILITIES.md) describes what the
current product does and what remains unproven.

## Build and run

Everything from here down is for contributors. Players need only the section
above.

Requirements:

- Windows 10 or 11
- .NET 10 SDK for WinUI/AppCore/CLI and .NET 8 for the rebuild
- Node.js 24.x with npm 11.12.x
- Python 3 through the Windows `py` launcher
- PowerShell 7 for rebuild tooling
- A lawfully obtained Battle Engine Aquila installation for retail-aware and
  rebuild workflows

For a fresh checkout:

```powershell
git clone --recurse-submodules https://github.com/dlprentice/Onslaught-Career-Editor.git
cd Onslaught-Career-Editor
```

For an existing checkout, initialize the pinned source references once with
`git submodule update --init --recursive`. From the repository root:

```powershell
npm test
npm run dev
```

`npm test` builds the active solution once, then checks the consequential
save/codec/write/copy/patch contracts and the static WinUI accessibility audit.
It deliberately excludes broad UI, native Godot, release packaging, Ghidra,
local runtime evidence, and historical accounting.
Use the smallest focused command for narrower work:

```powershell
npm run test:appcore
npm run test:ui
npm run test:safe-copy
npm run test:cli
npm run test:docs
npm run test:safety
npm run test:rebuild-core
```

Root [`package.json`](package.json) is the command authority. See
[`VALIDATION.md`](VALIDATION.md) for proportional command selection and
[`CONTRIBUTING.md`](CONTRIBUTING.md) for contribution boundaries.

The Level 100 Opening Slice can be launched independently:

```powershell
npm run run:rebuild-godot
```

Its first run downloads and verifies the pinned Godot .NET archive into a
per-user cache, detects the user's retail installation, and materializes the
exact supported rebuild inputs to ignored local paths. If auto-detection does
not find a custom Steam library, run
`pwsh rebuild/tools/Run-FirstFlight.ps1 -GameRoot "<game folder>"`.

## Data and mutation safety

- Never synthesize `.bes` saves from scratch. Start from a real baseline and
  preserve file length, reserved fields, and unknown bytes.
- Never patch an installed `BEA.exe`. Executable changes are allowed only on a
  verified copied target or an app-created safe game copy.
- Keep game binaries, real saves, Ghidra backups/alternate projects, debugger
  transcripts, private captures, secrets, bulk extraction output, and build
  output out of Git. The reviewed canonical Ghidra project is the sole database
  exception under `reverse-engineering/ghidra/`.
- Do not commit retail assets or their converted copies. Keep them in ignored
  local owners and retain credits/provenance when a deterministic recipe uses
  them. Parser success establishes format support, not visual fidelity.
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
technical evidence front door. Static analysis proves only the identities and
structures it directly demonstrates; controlled copied-runtime work is needed
for observed behavior and measured values. Stuart's source and the pinned
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
[`rebuild/LICENSE`](rebuild/LICENSE), [`rebuild/PROVENANCE.md`](rebuild/PROVENANCE.md),
and [`reverse-engineering/project-meta/attribution.md`](reverse-engineering/project-meta/attribution.md).
