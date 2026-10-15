# Onslaught Toolkit

Status: active — the project overview
Last updated: 2026-10-15 (decomp done and private; native port in progress; companion active; Godot rebuild parked; Ghidra and WinUI removed)
Summary: what this project is, where each part lives, how to build the companion, and where each authoritative document is.

Onslaught Toolkit is a preservation project for *Battle Engine Aquila* (2003, Lost Toys).

- **The decompilation is done.** A byte-matching decompilation of the retail executable (private for now) is the
  project's reverse-engineering authority. It is planned for publication as "Onslaught CE": GPL-3.0 source and
  binaries, no game files, once its native port plays like retail.
- **The native source port is in progress** (private, Windows and Linux).
- **The companion is active and public.** It is a Godot .NET app for players: it opens on their game and careers,
  shows progress and Goodies, edits careers and settings only after a verified backup and a clear choice, keeps
  automatic backups that can be put back, and plays and explains the game's own music, voices and lore.
- **The Godot rebuild is parked**; [`rebuild/`](rebuild/README.md) holds its parked state as reference.

This repository holds the companion, documentation of the game (formats, behaviours and findings as prose and
specs), our own tools, the AppCore patching core the companion's future mod manager builds on, and the parked
rebuild. It holds no game files, Ghidra database, decompiler output or decomp source.

This is an unofficial community project. It is not affiliated with or endorsed by the game's publishers or rights
holders. Repository licenses cover their respective project code and documentation; they grant no rights in the
retail game, its assets, names, or trademarks.

## Using the companion

The companion has no published release yet; build it from source (below). It needs your own installation of the
game to work on your careers, settings and media. The older Windows-only WinUI toolkit on the
[Releases](https://github.com/dlprentice/Onslaught-Career-Editor/releases) page (v1.0.11, tag `winui-v1.0.11`) is
retired and no longer maintained; its source is in the project's private pre-flatten history.

## Where things live

| Path | Owner |
| --- | --- |
| [`companion/OnslaughtToolkit.Godot/`](companion/OnslaughtToolkit.Godot/README.md) | The MIT companion, C# built in code on Godot 4.8 dev6 .NET |
| `OnslaughtCareerEditor.AppCore/` | The patching core (executable patch plans, guarded installed-game writes, safe copies) the companion's mod manager will build on |
| [`reverse-engineering/`](reverse-engineering/RE-INDEX.md) | Documentation of the game: formats, mechanics, saves, assets, function notes and contracts |
| [`lore/`](lore/_index.md) | The canonical lore and history library, embedded in the companion |
| [`tools/`](tools/README.md) | Format decoders, asset exporters, capture analysis and the repository's checks |
| [`patches/`](patches/README.md) | The executable-patch and safe-copy profile catalogs |
| [`rebuild/`](rebuild/README.md) | The parked GPL Godot reconstruction, kept as reference |

[`PROJECT-INDEX.md`](PROJECT-INDEX.md) maps source ownership and dependencies;
[`CURRENT_CAPABILITIES.md`](CURRENT_CAPABILITIES.md) says what is demonstrated today and what is not.
Retired surfaces (WinUI, the CLI, Electron, the Python GUI, WPF) remain in Git history.

## Build and run

The engineering host is Omarchy Linux. Requirements:

- The .NET 10 SDK named in `global.json`, and the pinned toolchain from `~/.local/opt/game-pipeline`
  (Godot 4.8 dev6 .NET with matching templates; .NET SDK 8.0.424 for the companion)
- Node.js 26.7 and npm 11.19 from mise
- Python 3.14 available as `python`; root commands use forward-slash paths
- A lawfully obtained Battle Engine Aquila installation for anything that reads the game

```bash
git clone --recurse-submodules https://github.com/dlprentice/Onslaught-Career-Editor.git
cd Onslaught-Career-Editor
npm run build      # build the companion
npm run dev        # run it (opens a window)
npm test           # the companion's contract and tooling checks, headless
npm run test:docs
npm run test:safety
```

For an existing checkout, initialize the pinned source references once with
`git submodule update --init --recursive`.

Root [`package.json`](package.json) is the command authority; [`VALIDATION.md`](VALIDATION.md) selects the check
for a change and [`CONTRIBUTING.md`](CONTRIBUTING.md) sets contribution boundaries.

| Task | Command |
| --- | --- |
| Companion build, run, test, capture, export | `npm run build:companion-godot`; `npm run run:companion-godot`; `npm run test:companion-godot`; `npm run capture:companion-godot`; `npm run export:companion-godot -- --platform both` |
| AppCore patching core | `npm run test:appcore` |
| Tool checks | Affected cases in `python tools/<name>_tests.py`; all of them with `npm run test:tools` |
| Parked rebuild | `npm run check:rebuild` (last passed at the parking point; see [rebuild/README.md](rebuild/README.md)) |

The companion launcher puts scratch, logs and user data under the canonical checkout's `local-data/companion/`,
including from a Git worktree.

## Data and mutation safety

- Never synthesize `.bes` saves from scratch. Start from a real baseline and preserve file length, reserved fields
  and unknown bytes.
- Every write into the game is a choice the player makes, after a verified backup, never while the game runs. The
  patching core's `BinaryPatchEngine.AuthorizeInstalledGameWrite` will not grant an installed-game write until a
  verified original sits beside the target.
- Keep game binaries and assets (or converted copies), real saves, Ghidra databases, decompiler output, debugger
  transcripts, private captures, secrets and build output out of Git; `npm run test:safety` enforces the boundary.
- Online multiplayer is not player-ready.

The tracked regression fixture [`tests_shared/fixtures/gold_career_save.bin`](tests_shared/fixtures/README.md) is
the reviewed exception to the no-save rule. See [`SECURITY.md`](SECURITY.md) and
[`LOCAL_LAB_OVERLAY.md`](LOCAL_LAB_OVERLAY.md) for handling local inputs.

## Evidence and provenance

[`reverse-engineering/RE-INDEX.md`](reverse-engineering/RE-INDEX.md) is the front door to the game documentation.
Findings name the specimen, capture, test or source line they rest on. Stuart Gillam's source in the pinned
[`references/Onslaught`](references/Onslaught) submodule is a source reference, not proof of retail behaviour.
Earlier Ghidra-era records, the tracked Ghidra checkpoint and the campaign machinery are kept privately.

The lore library begins at [`lore/_index.md`](lore/_index.md); [`lore-book/BOOK.md`](lore-book/BOOK.md) is a short
reading guide.

## Licenses

Repository licensing, source attribution and the rebuild's GPL boundary are in [`LICENSE`](LICENSE),
[`rebuild/LICENSE`](rebuild/LICENSE), [`rebuild/PROVENANCE.md`](rebuild/PROVENANCE.md),
[`companion/OnslaughtToolkit.Godot/PROVENANCE.md`](companion/OnslaughtToolkit.Godot/PROVENANCE.md) and
[`reverse-engineering/project-meta/attribution.md`](reverse-engineering/project-meta/attribution.md).
