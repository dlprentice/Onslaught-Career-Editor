# Onslaught Companion

Status: active — the project overview
Last updated: 2026-11-11 (the Companion-to-CE move stated in the intro)
Summary: what this project is, where each part lives, which checks a public clone can run, and what Companion builds require.

Onslaught Companion is the player app of a preservation project for *Battle Engine Aquila* (2003, Lost Toys); this
repository holds it and the project's overview. The repository is named Onslaught-Career-Editor; its documents also
call it the Toolkit.

The Companion's player features are moving into [Onslaught CE](https://github.com/dlprentice/onslaught-ce). The app
stays until each feature is replaced there and verified, and new player features go to CE.

To contribute to any part of the project, start with [Where to contribute](CONTRIBUTING.md#where-to-contribute): it says
which public repository takes which kind of work, and everyone contributes by fork and pull request.

| I want to | Start at |
| --- | --- |
| Play the game | [Onslaught CE](https://github.com/dlprentice/onslaught-ce) (you need your own copy of the game) |
| Build and run the Companion | [Build and run](#build-and-run) |
| Contribute a change | [CONTRIBUTING.md](CONTRIBUTING.md) |
| Choose the checks for a change | [VALIDATION.md](VALIDATION.md) |
| Find where code and documents live | [PROJECT-INDEX.md](PROJECT-INDEX.md) |
| See the direction and the open work | [GOAL.md](GOAL.md) and [PROGRAM.md](PROGRAM.md) |
| See what is demonstrated today | [CURRENT_CAPABILITIES.md](CURRENT_CAPABILITIES.md) |
| Read the lore | [lore/_index.md](lore/_index.md) |

- **The byte-matching decompilation is the reverse-engineering authority.** Its public export,
  [onslaught-decomp](https://github.com/dlprentice/onslaught-decomp), documents matching coverage, excluded code and
  source and build concessions. Matching function sections and relocations is separate from reproducing the
  complete linked executable or proving gameplay parity.
- **The game documentation lives in [onslaught-preservation](https://github.com/dlprentice/onslaught-preservation).**
  It is the one home of the findings on the game's file formats, saves, mechanics, levels and engine (prose and specs,
  CC BY-SA 4.0), and new findings go there. [`reverse-engineering/`](reverse-engineering/RE-INDEX.md) here is a frozen
  copy; its [RE-INDEX](reverse-engineering/RE-INDEX.md#what-the-freeze-leaves-open) names the few tool-owned files
  that still change.
- **Onslaught CE is the native Windows and Linux port.** Its source and downloads are published separately as
  **[Onslaught CE](https://github.com/dlprentice/onslaught-ce)** (GPL-3.0-only, no game files), not from this repository.
  Its [release notes](https://github.com/dlprentice/onslaught-ce/releases/latest) identify the tested routes,
  corrections and remaining limits.
- **The companion, Onslaught Companion, manages careers for the original game and Onslaught CE.** It is a Godot
  .NET app that shows progress and Goodies, edits careers and settings after a verified backup and a clear choice,
  and keeps automatic backups that can be put back. It offers CE launch, two CE launcher settings and the steps for
  updating CE (the companion itself contacts nothing; CE checks its own signed feed). It also plays and explains the game's own music, voices and lore.
  The [companion's limits](companion/OnslaughtToolkit.Godot/README.md#known-limits) distinguish tested file operations
  from game launch and Windows behavior that still need to be tried.
- **The Godot rebuild** aims to be 1:1 with retail from startup to exit, with level 100 playable to completion. It
  is developed in [onslaught-godot](https://github.com/dlprentice/onslaught-godot), which keeps its measured parity.
  `rebuild/` here is retained as a frozen reference. Its application is not built or gated here; some retained
  Python helpers still support this repository's format tools and have focused checks.

This repository holds the companion, the lore, our own tools, a frozen copy of the game documentation and a frozen
copy of the Godot rebuild. It holds no game files, Ghidra database, decompiler output or decomp source.

This is an unofficial community project. It is not affiliated with or endorsed by the game's publishers or rights
holders. Repository licenses cover their respective project code and documentation; they grant no rights in the
retail game, its assets, names, or trademarks.

## Play: Onslaught CE

To play the game, use Onslaught CE, the native source port. It needs your own installation of the game for its data.
Its source and downloads are at [Onslaught CE](https://github.com/dlprentice/onslaught-ce).

## Report a problem

- The game (Onslaught CE): [Onslaught CE's issues](https://github.com/dlprentice/onslaught-ce/issues).
- The companion, lore, tools or this repository's own documents: [this repository's issues](https://github.com/dlprentice/Onslaught-Career-Editor/issues).
- The game documentation (formats, saves, mechanics, levels, engine): [onslaught-preservation's issues](https://github.com/dlprentice/onslaught-preservation/issues).
- The Godot rebuild: [onslaught-godot's issues](https://github.com/dlprentice/onslaught-godot/issues).

## Related repositories

| Repository | What it holds |
| --- | --- |
| This repository | The companion, lore, our tools, and frozen copies of the game documentation and the Godot rebuild |
| [Onslaught CE](https://github.com/dlprentice/onslaught-ce) | The native source port's source and its Windows and Linux downloads; GPL-3.0-only |
| [onslaught-decomp](https://github.com/dlprentice/onslaught-decomp) | The byte-matching decompilation of the retail executable, for MSVC 6; bring your own game and compiler; GPL-3.0-only |
| [onslaught-godot](https://github.com/dlprentice/onslaught-godot) | The Godot 4 C# rebuild, compared Present by Present with recorded runs of the native port and of the original game; a proof of concept, not yet playable; GPL-3.0-only |
| [onslaught-preservation](https://github.com/dlprentice/onslaught-preservation) | The one home of the game documentation: file formats, saves, mechanics, levels and engine; CC BY-SA 4.0 |
| [`stuart73/Onslaught`](https://github.com/stuart73/Onslaught) | Stuart Gillam's GPL Onslaught project; this repository pins David's fork, [`dlprentice/Onslaught`](https://github.com/dlprentice/Onslaught), as [`references/Onslaught`](references/Onslaught) |
| [`stuart73/AYAResourceExtractor`](https://github.com/stuart73/AYAResourceExtractor) | Stuart Gillam's resource extractor; this repository pins David's fork, [`dlprentice/AYAResourceExtractor`](https://github.com/dlprentice/AYAResourceExtractor), as [`references/AYAResourceExtractor`](references/AYAResourceExtractor) |

The two forks are pinned references, not contribution targets.

## Using the companion

The companion has no published release yet. You can build and test it from this public repository on Linux;
see [Build and run](#build-and-run).
It needs your own installation of the game to work on your careers, settings and media. The older Windows-only WinUI toolkit on the
[Releases](https://github.com/dlprentice/Onslaught-Career-Editor/releases) page (v1.0.11, tag `winui-v1.0.11`) is
retired and no longer maintained; its source is in the project's private pre-flatten history. Its executable patching
and copied-install "safe launch" are not in the current companion and are not coming back: Onslaught CE replaces them:
it reads your install and keeps its own files in its own folder. Their last code here (the AppCore library and the `patches/` catalog) was removed on
2026-10-22; Git keeps it. A player who used that toolkit's safe launch on Windows finds any careers left in its copies
on the companion's Home page, where each can be saved as a copy elsewhere.

## Where things live

| Path | Owner |
| --- | --- |
| [`companion/OnslaughtToolkit.Godot/`](companion/OnslaughtToolkit.Godot/README.md) | The companion for original-game and CE careers, settings, launch and the level/mission editor, C# built in code on Godot 4.8 beta1 .NET and .NET 10 |
| [`reverse-engineering/`](reverse-engineering/RE-INDEX.md) | A frozen copy of the game documentation (formats, mechanics, saves, assets, function notes and contracts) as at commit `fae54b7`. Its home is [onslaught-preservation](https://github.com/dlprentice/onslaught-preservation), where new findings go |
| [`lore/`](lore/_index.md) | The canonical lore and history library, embedded in the companion |
| [`tools/`](tools/README.md) | Format decoders, the [local content catalogue](tools/README.md#content-catalogue), asset exporters, capture analysis and the repository's checks |
| [`rebuild/`](rebuild/README.md) | A frozen GPL Godot rebuild reference, with retained Python helpers used by Toolkit tools. Current rebuild development, builds and parity gates live in [onslaught-godot](https://github.com/dlprentice/onslaught-godot) |

[`PROJECT-INDEX.md`](PROJECT-INDEX.md) maps source ownership and dependencies;
[`CURRENT_CAPABILITIES.md`](CURRENT_CAPABILITIES.md) says what is demonstrated today and what is not.
Retired surfaces (WinUI, the CLI, Electron, the Python GUI, WPF) remain in Git history.

## Build and run

Build and test the Companion on Linux x86-64 using the public setup below. No other project checkout, private
repository, maintainer tool or game installation is required for its authored tests. Windows contributors can use
WSL2 as described below; exported Windows applications still need separate native Windows validation.

### On Windows

The repository's development commands run inside Linux. Use [WSL2](https://learn.microsoft.com/en-us/windows/wsl/install)
with an x86-64 Ubuntu or Debian installation, then follow the commands below in its Linux terminal. Check
`wsl --list --verbose` in Windows first. If WSL is absent, the machine owner can install it using `wsl --install`;
that enables Windows features and can require administrator access and a restart. An automated agent should
explain those changes and obtain the owner's approval before doing them.

Keep the checkout in the [WSL Linux filesystem](https://learn.microsoft.com/en-us/windows/wsl/filesystems),
such as `~/src/Onslaught-Career-Editor`, rather than under `/mnt/c`. Install Git, Python and the native .NET libraries
inside that distribution. The [WSLg prerequisites](https://learn.microsoft.com/en-us/windows/wsl/tutorials/gui-apps)
apply to opening the Companion with `npm run dev`; headless tests do not need a graphical desktop. A WSL run tests
the Linux application, not native Windows file or input behavior. This setup was reproduced on native Linux;
the WSL recipe follows Microsoft's documented route and has not been exercised by this project.

### Public setup

Start with:

- Git, including the pinned public source-reference submodules for the full documentation and safety scans
- Python 3.12 or newer with `venv` for setup/build/runtime checks (the repository's wider Python tools are tested on 3.14)
- Optionally, Node.js 26.7 and npm 11.19 for the command shortcuts in `package.json`; equivalent Python commands
  are listed below, so Node is not needed to build or test the application

Some tool checks also require NumPy or Pillow, and catalogue schema checks need `jsonschema` to avoid skips.
See the [Python prerequisite scopes](tools/README.md#python-prerequisites) before choosing a tooling suite.

The commands below use the npm shortcuts, which need Node.js. Without Node, use the Python commands listed after the
block.

```bash
git clone --recurse-submodules https://github.com/dlprentice/Onslaught-Career-Editor.git
cd Onslaught-Career-Editor
python3 -m venv local-data/venv
. local-data/venv/bin/activate
npm run test:docs
npm run test:safety
python tools/companion_toolchain.py setup
npm run build
npm test
```

The setup downloads pinned official Godot .NET and .NET SDK archives into ignored `local-data/`, verifies them
and installs them there without administrator access or changes to your system tools. The
[Companion build guide](companion/OnslaughtToolkit.Godot/README.md#build-test-capture-run-and-export)
lists system-library prerequisites, verification and optional export templates. `npm run dev` opens the Companion.
If you only work on docs or Python tools, skip the Godot/.NET setup and use the relevant checks instead;
for example, `python tools/content_catalog_tests.py` uses authored catalogue inputs.

For an existing checkout or a fresh Git worktree, run `git submodule update --init --recursive` from that
checkout's root before the full documentation and safety gates. Initialize each worktree separately, even if the
main checkout already has the reference files. The command uses the recorded pins; documentation checks follow
local links into those public sources and need no retail inputs. A lawfully obtained Battle Engine Aquila
installation is needed for tools that read the actual game.

Companion commands use the .NET 10 SDK pinned in
[`global.json`](global.json), repeated by [the Companion's pin](companion/OnslaughtToolkit.Godot/global.json),
and [its toolchain manifest](companion/OnslaughtToolkit.Godot/toolchain.json): Godot 4.8 beta1 .NET,
matching templates when exporting, and .NET SDK 10.0.402. Existing explicitly selected shared installations
remain supported; they are optional. Follow [CONTRIBUTING.md](CONTRIBUTING.md) to establish the baseline,
implement a feature and submit a PR from your fork.

Activating the virtual environment supplies the `python` command used by npm, including on distributions that
otherwise provide only `python3`. Without Node/npm, documentation checks are
`python3 tools/md_link_check.py --check-only` and `python3 tools/doc_header_check.py`; the payload check is
`python3 tools/public_allowlist_safety_check.py --include-submodules`.
The equivalent application commands are `python3 tools/companion_godot.py build`,
`python3 tools/companion_godot.py test` and `python3 tools/companion_godot.py run`. Run both
`python3 tools/companion_toolchain_tests.py` and `python3 tools/companion_godot_tests.py` for the tooling stage of
`npm test`. The npm commands are convenience entry points, not a second build system.

Root [`package.json`](package.json) is the command authority; [`VALIDATION.md`](VALIDATION.md) selects the check
for a change and [`CONTRIBUTING.md`](CONTRIBUTING.md) sets contribution boundaries.

| Task | Command |
| --- | --- |
| Companion build, run, test, export | `npm run build:companion-godot`; `npm run run:companion-godot`; `npm run test:companion-godot`; `npm run export:companion-godot -- --platform both` |
| Optional maintainer capture workflow | `npm run capture:companion-godot` requires the separate wrapper described in the [Companion build guide](companion/OnslaughtToolkit.Godot/README.md#build-test-capture-run-and-export) |
| Tool checks | Affected cases in `python tools/<name>_tests.py`; `npm run test:tools` includes retail-dependent checks, as [the tools guide](tools/README.md#python-prerequisites) explains |

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
maintained and where new findings go; [`reverse-engineering/`](reverse-engineering/RE-INDEX.md) here is a frozen copy.
Findings name the specimen, capture, test or source line they rest on. Stuart Gillam's GPL Onslaught project (GitHub `stuart73/Onslaught`) in the
pinned [`references/Onslaught`](references/Onslaught) submodule is a source reference, not proof of retail behaviour.
Earlier Ghidra-era records, the tracked Ghidra checkpoint and the campaign machinery are kept privately.

The lore library begins at [`lore/_index.md`](lore/_index.md); [`lore-book/BOOK.md`](lore-book/BOOK.md) is a short
reading guide.

## Licenses

| Path | Licence |
| --- | --- |
| Code: `companion/`, `tools/` scripts, build files | GPL-3.0-only ([`LICENSE`](LICENSE)) |
| `rebuild/` | GPL-3.0-only ([`rebuild/LICENSE`](rebuild/LICENSE), [`rebuild/PROVENANCE.md`](rebuild/PROVENANCE.md)) |
| Documentation (`*.md`, `reverse-engineering/`, `roadmap/`, data tables) and `lore/`, `lore-book/` | CC BY-SA 4.0 ([`LICENSES/CC-BY-SA-4.0.txt`](LICENSES/CC-BY-SA-4.0.txt)) |
| `reverse-engineering/source-code/`: notes quoting the upstream GPL Onslaught source by Stuart Gillam | CC BY-SA 4.0 and GPL-3.0-only (the quoted source keeps its licence and credit) |
| `reverse-engineering/source-code/aya-*`: notes quoting Stuart Gillam's AYAResourceExtractor | CC BY-SA 4.0 and MIT (the quoted extractor keeps its licence and credit) |
| ExuberantParrot's PR #1 passages in two function notes | CC BY-SA 4.0 and MIT ([`LICENSES/MIT.txt`](LICENSES/MIT.txt)) |
| `references/` submodules | their own licences |

[`REUSE.toml`](REUSE.toml) maps every path to its licence; quotations in the lore stay with their authors.
Repository licensing, source attribution and the rebuild's GPL boundary are in [`LICENSE`](LICENSE),
[`rebuild/LICENSE`](rebuild/LICENSE), [`rebuild/PROVENANCE.md`](rebuild/PROVENANCE.md),
[`companion/OnslaughtToolkit.Godot/PROVENANCE.md`](companion/OnslaughtToolkit.Godot/PROVENANCE.md) and
[`reverse-engineering/project-meta/attribution.md`](reverse-engineering/project-meta/attribution.md).
