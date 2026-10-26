# Onslaught Companion

Status: active — the project overview
Last updated: 2026-10-26 (decompilation concessions and native-port validation scope clarified)
Summary: what this project is, where each part lives, how to build the companion, and where each authoritative document is.

Onslaught Companion is the player app of a preservation project for *Battle Engine Aquila* (2003, Lost Toys); this
repository holds it and the project's overview.

- **The byte-matching decompilation is the reverse-engineering authority.** Its public export,
  [onslaught-decomp](https://github.com/dlprentice/onslaught-decomp), documents matching coverage, excluded code and
  source and build concessions. Matching function sections and relocations is separate from reproducing the
  complete linked executable or proving gameplay parity.
- **Onslaught CE is the native Windows and Linux port.** Its source and downloads are published separately as
  **[Onslaught CE](https://github.com/dlprentice/onslaught-ce)** (GPL-3.0-only, no game files), not from this repository.
  Its [release notes](https://github.com/dlprentice/onslaught-ce/releases/latest) identify the tested routes,
  corrections and remaining limits.
- **The companion, Onslaught Companion, manages careers for the original game and Onslaught CE.** It is a Godot
  .NET app that shows progress and Goodies, edits careers and settings after a verified backup and a clear choice,
  and keeps automatic backups that can be put back. It offers CE launch, two CE launcher settings and a check of
  the signed public update information. It also plays and explains the game's own music, voices and lore.
  The [companion's limits](companion/OnslaughtToolkit.Godot/README.md#known-limits) distinguish tested file operations
  from game launch and Windows behavior that still need to be tried.
- **The Godot rebuild** aims to be 1:1 with retail from startup to exit, with level 100 playable to completion. It
  is developed in [onslaught-godot](https://github.com/dlprentice/onslaught-godot), which keeps its measured parity; `rebuild/` here is a frozen copy,
  not built or tested, and is removed when this repository is split.

This repository holds the companion, documentation of the game (formats, behaviours and findings as prose and
specs), our own tools and a frozen copy of the Godot rebuild. It holds no game files, Ghidra database, decompiler output or decomp source.

This is an unofficial community project. It is not affiliated with or endorsed by the game's publishers or rights
holders. Repository licenses cover their respective project code and documentation; they grant no rights in the
retail game, its assets, names, or trademarks.

## Play: Onslaught CE

To play the game, use Onslaught CE, the native source port. It needs your own installation of the game for its data.
Its source and downloads are at [Onslaught CE](https://github.com/dlprentice/onslaught-ce).

## Report a problem

- The game (Onslaught CE): [Onslaught CE's issues](https://github.com/dlprentice/onslaught-ce/issues).
- The companion, lore or this repository's documentation: [this repository's issues](https://github.com/dlprentice/Onslaught-Career-Editor/issues).
- The Godot rebuild: [onslaught-godot's issues](https://github.com/dlprentice/onslaught-godot/issues).

## Related repositories

| Repository | What it holds |
| --- | --- |
| This repository | The companion, documentation of the game, lore, our tools, and a frozen copy of the Godot rebuild |
| [Onslaught CE](https://github.com/dlprentice/onslaught-ce) | The native source port's source and its Windows and Linux downloads; GPL-3.0-only |
| [onslaught-decomp](https://github.com/dlprentice/onslaught-decomp) | The byte-matching decompilation of the retail executable, for MSVC 6; bring your own game and compiler; GPL-3.0-only |
| [onslaught-godot](https://github.com/dlprentice/onslaught-godot) | The Godot 4 C# rebuild, checked against the original game Present by Present; GPL-3.0-only |
| [onslaught-preservation](https://github.com/dlprentice/onslaught-preservation) | Documentation of the game: file formats, saves, mechanics, levels and engine; CC BY-SA 4.0 |
| [`stuart73/Onslaught`](https://github.com/stuart73/Onslaught) | Stuart's partial GPL source release; this repository pins David's fork, [`dlprentice/Onslaught`](https://github.com/dlprentice/Onslaught), as [`references/Onslaught`](references/Onslaught) |

## Using the companion

The companion has no published release yet; build it from source (below). It needs your own installation of the
game to work on your careers, settings and media. The older Windows-only WinUI toolkit on the
[Releases](https://github.com/dlprentice/Onslaught-Career-Editor/releases) page (v1.0.11, tag `winui-v1.0.11`) is
retired and no longer maintained; its source is in the project's private pre-flatten history. Its executable patching
and copied-install "safe launch" are not in the current companion and are not coming back: Onslaught CE replaces them:
it reads your install and keeps its own files in its own folder. Their last code here (the AppCore library and the `patches/` catalog) was removed on
2026-10-22; Git keeps it. A player who used that toolkit's safe launch on Windows finds any careers left in its copies
on the companion's Home page, where each can be saved as a copy elsewhere.

## Where things live

| Path | Owner |
| --- | --- |
| [`companion/OnslaughtToolkit.Godot/`](companion/OnslaughtToolkit.Godot/README.md) | The companion for original-game and CE careers, settings and launch, C# built in code on Godot 4.8 beta1 .NET and .NET 10 |
| [`reverse-engineering/`](reverse-engineering/RE-INDEX.md) | Documentation of the game: formats, mechanics, saves, assets, function notes and contracts. Moved: maintained at [onslaught-preservation](https://github.com/dlprentice/onslaught-preservation); this copy is frozen |
| [`lore/`](lore/_index.md) | The canonical lore and history library, embedded in the companion |
| [`tools/`](tools/README.md) | Format decoders, asset exporters, capture analysis and the repository's checks |
| [`rebuild/`](rebuild/README.md) | A frozen copy of the GPL Godot rebuild, now developed in [onslaught-godot](https://github.com/dlprentice/onslaught-godot); not built or tested here |

[`PROJECT-INDEX.md`](PROJECT-INDEX.md) maps source ownership and dependencies;
[`CURRENT_CAPABILITIES.md`](CURRENT_CAPABILITIES.md) says what is demonstrated today and what is not.
Retired surfaces (WinUI, the CLI, Electron, the Python GUI, WPF) remain in Git history.

## Build and run

The engineering host is Omarchy Linux. Requirements:

- The .NET 10 SDK named in `global.json`, and the pinned toolchain from `~/.local/opt/game-pipeline`
  (Godot 4.8 beta1 .NET with matching templates and .NET SDK 10.0.402)
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
| Tool checks | Affected cases in `python tools/<name>_tests.py`; all of them with `npm run test:tools` |

The companion's development runner (`tools/companion_godot.py`) puts scratch, logs and user data under the canonical
checkout's `local-data/companion/`, including from a Git worktree.

## Data and mutation safety

- Never synthesize `.bes` saves from scratch. Start from a real baseline and preserve file length, reserved fields
  and unknown bytes.
- Every write into the game is a choice the player makes, after a verified backup, never while the game runs. The
  companion's [`Files/GameWrites.cs`](companion/OnslaughtToolkit.Godot/Files/GameWrites.cs) is the write path that
  ships: a verified backup set outside the game folder, a running-game check before the backup and again before the
  swap, an exchange swap that is undone if the displaced file is not the one backed up, and verification of the saved file.
- Keep game binaries and assets (or converted copies), real saves, Ghidra databases, decompiler output, debugger
  transcripts, private captures, secrets and build output out of Git; `npm run test:safety` enforces the boundary.
- Online multiplayer is not player-ready.

The tracked regression fixture [`tests_shared/fixtures/gold_career_save.bin`](tests_shared/fixtures/README.md) is
the reviewed exception to the no-save rule. See [`SECURITY.md`](SECURITY.md) and
[`LOCAL_LAB_OVERLAY.md`](LOCAL_LAB_OVERLAY.md) for handling local inputs.

## Evidence and provenance

The game documentation moved to [onslaught-preservation](https://github.com/dlprentice/onslaught-preservation), where it is
maintained; [`reverse-engineering/`](reverse-engineering/RE-INDEX.md) here is a frozen copy.
Findings name the specimen, capture, test or source line they rest on. Stuart's source release (GitHub `stuart73/Onslaught`) in the
pinned [`references/Onslaught`](references/Onslaught) submodule is a source reference, not proof of retail behaviour.
Earlier Ghidra-era records, the tracked Ghidra checkpoint and the campaign machinery are kept privately.

The lore library begins at [`lore/_index.md`](lore/_index.md); [`lore-book/BOOK.md`](lore-book/BOOK.md) is a short
reading guide.

## Licenses

| Path | Licence |
| --- | --- |
| Code: `companion/`, `tools/` and `tests_shared/` scripts, build files | GPL-3.0-only ([`LICENSE`](LICENSE)) |
| `rebuild/` | GPL-3.0-only ([`rebuild/LICENSE`](rebuild/LICENSE), [`rebuild/PROVENANCE.md`](rebuild/PROVENANCE.md)) |
| Documentation (`*.md`, `reverse-engineering/`, `roadmap/`, data tables) and `lore/`, `lore-book/` | CC BY-SA 4.0 ([`LICENSES/CC-BY-SA-4.0.txt`](LICENSES/CC-BY-SA-4.0.txt)) |
| `reverse-engineering/source-code/`: notes quoting Stuart Gillam's published source | CC BY-SA 4.0 and GPL-3.0-only (the quoted source keeps its licence and credit) |
| `reverse-engineering/source-code/aya-*`: notes quoting Stuart Gillam's AYAResourceExtractor | CC BY-SA 4.0 and MIT (the quoted extractor keeps its licence and credit) |
| ExuberantParrot's PR #1 passages in two function notes | CC BY-SA 4.0 and MIT ([`LICENSES/MIT.txt`](LICENSES/MIT.txt)) |
| `references/` submodules | their own licences |

[`REUSE.toml`](REUSE.toml) maps every path to its licence; quotations in the lore stay with their authors.
Repository licensing, source attribution and the rebuild's GPL boundary are in [`LICENSE`](LICENSE),
[`rebuild/LICENSE`](rebuild/LICENSE), [`rebuild/PROVENANCE.md`](rebuild/PROVENANCE.md),
[`companion/OnslaughtToolkit.Godot/PROVENANCE.md`](companion/OnslaughtToolkit.Godot/PROVENANCE.md) and
[`reverse-engineering/project-meta/attribution.md`](reverse-engineering/project-meta/attribution.md).
