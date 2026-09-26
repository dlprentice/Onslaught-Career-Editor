# Onslaught Toolkit companion

Status: C# application built entirely in code on Godot 4.8 dev6 .NET; careers, Goodies, copies, options, install and backups, music, voices and lore; Linux executed checks, Windows runtime acceptance pending
Last updated: 2026-09-26 (RE save-audit corrections: gallery rows, god flags)
Summary: the MIT companion for Battle Engine Aquila players: it reads careers and the game's own files, writes changes only to verified copies, puts a copy into the game only after a confirmed, verified backup, and plays and explains the game's own music, voices and lore.

The companion owns careers, saves, recovery copies, supported patches, media and
related preservation tools. Retail reverse engineering and the faithful GPL game
rebuild have separate owners; this project neither launches nor depends on that rebuild.

## Layout

Everything is C# on Godot 4.8 dev6 .NET. [Main.tscn](Main.tscn) is a one-node wrapper
that attaches [CompanionApp](Ui/CompanionApp.cs); every control, container, dialog
and style below it is constructed in code. There is no GDScript, saved resource or
editor-authored scene, and `npm run build` refuses to stage one.

| Folder | Owner of |
| --- | --- |
| [Careers](Careers/) | The career byte codec (`CareerSave`), immutable open snapshots (`SaveSession`), the open/publish/compare/install workflow (`CareerWorkspace`) and each Goodie's rule and evidence (`GoodieFacts`) |
| [Files](Files/) | The protected OS file boundary (`ProtectedSaveFiles`), its worker thread, and game-folder writes: backup sets, the running-game check and the verified install (`GameWrites`) |
| [Game](Game/) | Steam library discovery, the game folder and its files, and the game's own text read from the install (`GameText`) |
| [Options](Options/) | The `defaultoptions.bea` reader and editor (`OptionsFile`) and the physical-key table |
| [Media](Media/) | The game's music, voice lines and cutscene list (`GameAudio`) and the bounded folder inventory |
| [Lore](Lore/) | The embedded lore library and its Markdown renderer |
| [Ui](Ui/) | The Flight-deck theme, the shell and one class per page |
| [Tests](Tests/) | Every behavioral contract, run headlessly inside Godot |
| [Development](Development/) | Development-only entries: screen captures and export license metadata |

`Tests/` and `Development/` compile only into development builds; release exports
exclude them from both the assembly and the package.

## Build, test, capture, run and export

From the repository or this lane's worktree:

```bash
npm run build:companion-godot
npm test
npm run capture:companion-godot
npm run run:companion-godot
npm run export:companion-godot -- --platform both
```

Build, test, capture and export never open a window on the desktop. **Run opens a
window**; use it when the desktop is available. Each command stages the project, its
linked MIT AppCore sources and the lore into a unique canonical `local-data/companion/`
directory with isolated imports, profiles, scratch and logs, and prints that directory.
Worktrees use the [canonical lab rules](../../LOCAL_LAB_OVERLAY.md); no research corpus
is copied.

`npm test` runs `Tests/CompanionTestRunner.cs` against an owned copy of the one tracked
[real-save fixture](../../tests_shared/fixtures/README.md) and a game-shaped folder built
from tiny original bytes, then the launcher's own checks. It covers the codec on the real
bytes, Goodie edits, options edits and the key table, the protected adapter and six Linux
publication races, Steam discovery, the game's text on a synthetic language table,
backups and installs (including a file that takes the name just before the swap), music
and voice grouping, every lore article and link, and the interface driving its real
controls.

`npm run capture:companion-godot` renders every page and state at 1280×800 and
1920×1080 through `godot-offscreen`, against the same fake install. Add
`--capture-arg=--steam-root=DIR` to render against a real Steam library instead; that
library is only read, and no game write is confirmed in that mode.

## What it does

**Home** finds the game through Steam (libraries, Flatpak and Snap), or a folder you
choose, and checks `BEA.exe` against the Steam release by SHA-256. It lists the game's
careers with an Open button, the options file, and what the install holds.

**Career** pages open a career read-only. A supported career is exactly 10,004 bytes
with version word `0x4BD1`; the app records its path, SHA-256 and physical file identity.
- **Overview**: missions with the game's own names, rank letters by the game's rule,
  Goodies, kill counts and campaign links.
- **Goodies**: the 230 Goodies the game's gallery shows, row by row as on its wall, in the
  game's colours (gold new, blue viewed), each with its title from your game's text, its
  unlock rule, and how that rule is known: seen in the game, checked in the game's code, or
  from the developers' source only. Slots 071–073 are stored and can be earned, but the
  gallery never shows them; they are listed apart and always kept as they are.
- **Edit a copy**: kill counts (only the three count bytes; the fourth byte is kept) and
  Goodie states. The preview lists every changed byte.
- **Cheat names**: a byte-identical copy whose name carries one of the three cheats seen
  working in the Steam game (`MALLOY`, `TURKEY`, `Maladim`).
- **Compare** lists every differing byte between two careers, named by region;
  **Stored values** shows the raw values read-only, including both players' god flags.

**Options** opens `defaultoptions.bea` (or another `.bea`) read-only and edits sound and
music volume, invert flight and walker, vibration, controller preset, mouse sensitivity
(the game's own slider steps), screen shape and keyboard bindings captured from a key
press. Controller and mouse bindings are kept unless replaced; language and display mode
are shown but not offered.

**Install & backups** is the one page that writes into the game folder. See the next
section.

**Music & voices** plays the game's soundtrack and voice lines from your install, grouped
by mission with the game's own transcripts. Only files with an Ogg Vorbis header
reach the decoder. Cutscenes are Bink video and are listed, not played.

**Lore** reads the repository's lore library offline: the front door's shelves and reading
order, a section outline, search, Back, Forward and Home (Alt+Left, Alt+Right; Ctrl+F
searches). Links between articles stay in the reader; links to other repository files open
their public GitHub page in your browser. The campaign's mission list is read from your
game's text when the page opens, never shipped.

**Media files** inventories an explicitly chosen folder: names, formats and sizes, with
bounded traversal, links skipped and partial results reported.

## How files stay safe

- Careers and options open read-only. Every edit is written to a **new** file in a folder
  you choose outside the game: publication re-checks the original's identity and content,
  stages and verifies all bytes, publishes without replacing any existing entry, reopens
  the result and compares it with the preview. The original stays the source until you
  open the copy.
- Writing into the game folder (a career into `savegames`, or a `.bea` as
  `defaultoptions.bea`, including a restore from a backup) needs a backup folder outside
  the game and a confirmation that names the exact file, source and backup folder. It is
  refused while `BEA.exe` is running; on Linux that means a process Wine names `BEA.exe`
  (a tool that merely opens the file does not count), a check not yet seen against a live
  game. It first makes a new backup set of every career and
  the options file, each copy verified and listed in a manifest. A file being replaced
  must still match its fresh backup; the new file is staged, verified and exchanged
  atomically (`renameat2` with `RENAME_EXCHANGE`). If the file displaced by the exchange
  is not the one that was backed up, it is swapped back and the new file withdrawn. The
  written file is reopened and verified.
- Installing into the game folder runs on Linux only; on Windows it is refused until it has
  been tested there. Reading, copies and backups on Windows use the linked Windows file
  path, which has not been executed here either.
- Malformed inputs, changed sources, same-path or linked sources, existing destinations
  and unavailable protected access fail closed; there is no ordinary write fallback. File
  dialogs cannot delete or create folders. An uncertain result says a file may exist; it
  is never deleted or reported as verified. File work runs on one worker thread, and
  closing waits for it.

A receipt concerns that operation, not later changes by another program or what the game
does with the file. These checks do not prove behavior after power loss.

## File-safety boundary

[ProtectedSaveFiles](Files/ProtectedSaveFiles.cs) links the MIT
[`SaveLabFileTransaction.cs`](../../OnslaughtCareerEditor.AppCore/SaveLabFileTransaction.cs) and
[`FileMutationSafety.cs`](../../OnslaughtCareerEditor.AppCore/FileMutationSafety.cs) unchanged; it
imports no AppCore assembly or media library. On Linux it opens sources descriptor-relative
without following links, compares physical identity and link count, stages into an unnamed
file, flushes it, and publishes with a no-clobber link. [GameWrites](Files/GameWrites.cs)
builds game-folder installs on the same primitives. The Windows copy path locks ancestors
and verifies identity, but releases its staging quarantine and closes the handle before a
path-based move, then verifies the published identity; Windows execution remains
unverified here, and a Windows cross-export is not acceptance.

## Exact toolchain and rollback

[toolchain.json](toolchain.json) records the measured engine, SDK and template hashes and
the shared lock revision; `tools/companion_godot.py` verifies the installation and refuses
mismatches. `global.json` pins .NET SDK 8.0.424; the Godot SDK is `4.8.0-dev.6` and the
runtime `8.0.30`. Export presets target Linux x86_64 and Windows x86_64, and Godot's normal
.NET export bundles the runtime, so packages need no installed .NET. Adopt a later engine
only in an isolated worktree with updated pins, matching templates and a full rerun of the
suite, exports and captures; roll back with the preceding commit and its preserved engine.

See [PROVENANCE.md](PROVENANCE.md) for licensing and data boundaries.
