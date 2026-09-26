# Onslaught Toolkit companion

Status: C# application built entirely in code on Godot 4.8 dev6 .NET, organised around the player: careers, Goodies, editing, cheats, game settings, backups, music, voices and lore; Linux executed checks, Windows runtime acceptance pending
Last updated: 2026-09-26 (player-first pages, saving into the game, automatic backups, catching up with the game)
Summary: the MIT companion for Battle Engine Aquila players: it opens on their game and careers, shows progress and Goodies, changes careers and settings only after a verified backup and a clear choice, keeps automatic backups that can be put back, and plays and explains the game's own music, voices and lore.

The companion is for players. It opens on their game and careers, and everything it
changes in the game is backed up first and can be put back. Retail reverse engineering and
the faithful GPL game rebuild have separate owners; this project neither launches nor
depends on that rebuild. Tools for looking at raw bytes are kept, folded away under
Advanced.

## Layout

Everything is C# on Godot 4.8 dev6 .NET. [Main.tscn](Main.tscn) is a one-node wrapper
that attaches [CompanionApp](Ui/CompanionApp.cs); every control, container, dialog
and style below it is constructed in code. There is no GDScript, saved resource or
editor-authored scene, and `npm run build` refuses to stage one.

| Folder | Owner of |
| --- | --- |
| [Careers](Careers/) | The career byte codec (`CareerSave`), immutable open snapshots (`SaveSession`), the open/publish/compare/install workflow (`CareerWorkspace`) and each Goodie's rule and evidence (`GoodieFacts`) |
| [Files](Files/) | The protected OS file boundary (`ProtectedSaveFiles`), its worker thread, and game-folder writes: backup sets, the running-game check and the verified write on Linux and elsewhere (`GameWrites`) |
| [Game](Game/) | Steam library discovery, the game folder and its files, the companion's remembered choices and backup folder (`GameFolder`), and the game's own text read from the install (`GameText`) |
| [Options](Options/) | The `defaultoptions.bea` reader and editor (`OptionsFile`) and the physical-key table |
| [Media](Media/) | The game's music, voice lines and cutscene list (`GameAudio`) and the bounded folder inventory |
| [Lore](Lore/) | The embedded lore library and its Markdown renderer |
| [Ui](Ui/) | The Flight-deck theme and icons, the shell, career cards, the save-choice dialog, the game's art read from the install (`GameArt`) and one class per page |
| [Tests](Tests/) | Every behavioral contract, run headlessly inside Godot |
| [Development](Development/) | Development-only entries: screen captures, export license metadata and the Windows program icon (`IconWriter`) |

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
bytes, Goodie edits, settings edits and the key table, the protected adapter and six Linux
publication races, Steam discovery, the game's text on a synthetic language table,
backups, automatic backups and writes into the game on both the Linux and the portable
(Windows) path, including a file that takes the name just before the swap and a career the
game saved after it was opened, music and voice grouping, every lore article and link, and
the interface driving its real controls: saving into the game, putting files back, and
catching up after the game closes.

`npm run capture:companion-godot` renders every page and state at 1280×800 and
1920×1080 through `godot-offscreen`: first a machine without the game, then a fake install
built from the fixture. Add `--capture-arg=--steam-root=DIR` to render against a real Steam
library instead; that library is only read, and nothing is saved into it in that mode. Add
`--beside-gpu-jobs` to render next to a job on the NVIDIA card instead of queuing behind the
machine-wide GPU lock: the run gets its own hidden output and queues on the lanes' shared Intel
GPU lock, `/var/tmp/godot-igpu.lock`. The companion's Compatibility renderer runs on the laptop's
Intel GPU through Mesa, so it does not compete with a film rendering on the NVIDIA card, and it
never overlaps another job on the Intel GPU (David allowed this on 2026-09-26).

## What it does

The sidebar groups the pages the way a player thinks about them: **Home**; **Your
career** (Summary, Goodies, Edit career, Cheats); **Your game** (Game settings, Backups);
**Extras** (Music & voices, Lore); and **Advanced**, folded away (Compare careers, Raw
values, Media files). The header names the page, shows **Game running** while the game
is open, and switches careers (or opens a career file, Ctrl+O). While Edit career or Game
settings has unsaved changes, a bar under the page counts them and offers Save (Ctrl+S)
and Undo.

**Home** finds the game through Steam (native, Flatpak and Snap on Linux; the registry and
Program Files on Windows) or a folder you choose, and checks `BEA.exe` against the Steam
release by SHA-256. It shows the render from the game's manual as its banner when the
install has it, a Play button for a Steam install (`steam://rungameid/1346400`), your
careers as cards with their progress, adding a career file to the game, the safety net
(automatic backups, Back up now, and the three promises below), and ways into Goodies,
Lore, Music & voices and the game's own manual. The career saved most recently opens by
itself, read-only.

- **Summary**: the career's path through the campaign as a map, from 1.00 to 8.00: each
  mission's rank, the routes the career took and the routes the game recorded as not taken,
  read from the links the career stores. Below it, missions with the game's own names,
  status and rank letters by the game's grading, the Goodie strip and kills.
- **Goodies**: the 230 Goodies the game's gallery shows, row by row as on its wall, in the
  game's colours (gold new, blue viewed), with filters and, for each, its title from your
  game's text, its unlock rule and how that rule is known. Slots 071–073 are stored and can
  be earned but never shown; they are listed apart and always kept as they are.
- **Edit career**: kill counts (only the three count bytes; the fourth is kept) and Goodies
  (unlock every Goodie, or pick them). Your changes are listed in words; the exact bytes
  are shown on request. **Save changes…** offers a new career in your game (named by you),
  replacing this career in your game, or a copy somewhere else.
- **Cheats**: a byte-identical copy of the career whose name switches on the cheats seen
  working in the Steam game (`MALLOY`, `TURKEY`, `Maladim`), added to your game or saved
  elsewhere.
- **Game settings**: the game's default settings or any career's own (loading a career in
  the game uses its settings): sound and music volume; invert flight and walking,
  vibration and controller layout for each player; mouse sensitivity (the game's own slider
  steps) and screen shape; keyboard keys captured from a key press. Controller and mouse
  bindings are kept unless replaced; language and display mode are kept.
- **Backups**: automatic backups (when the companion opens and after the game closes while
  it is open, only when something changed), the folder (`Battle Engine Aquila Backups` in
  Documents unless you choose another), Back up now, and every backup set, newest first,
  with why it was made and **Put back** for each file.
- **Music & voices** plays the soundtrack and voice lines from your install, grouped by
  mission with the game's own transcripts. Only files with an Ogg Vorbis header reach the
  decoder. Cutscenes are Bink video and are listed, not played.
- **Lore** reads the repository's lore library offline: the front door's shelves and
  reading order, a section outline, search, Back, Forward and Home (Alt+Left, Alt+Right;
  Ctrl+F searches), the map of Allium from your game's manual, and the manual itself in
  your browser. The campaign's mission list is read from your game's text, never shipped.
- **Advanced**: **Compare careers** lists every differing byte between two careers, named
  by region; **Raw values** shows the stored values read-only, including both players' god
  flags; **Media files** inventories a chosen folder with bounded traversal.

When the game closes while the companion is open, or you come back to the companion, it
notices careers and settings the game saved, reads them again, backs them up if automatic
backups are on (after the game closed), and shows the latest. Changes you have not saved
are never thrown away for this; the companion says so instead.

## How files stay safe

Home makes three promises, and the code keeps them:

- **Nothing in your game changes without a backup first.** Only a career in `savegames/`
  or `defaultoptions.bea` is ever written. First, every career and the settings file are
  copied to a new backup set outside the game folder, each copy read back and verified and
  listed with its SHA-256 in a manifest. A file being replaced must still match its fresh
  backup, and a career or settings file you opened must still match what you opened: if
  the game saved it since, nothing is written. The new file is staged, verified, swapped in
  and reopened. On Linux the swap is `renameat2` with `RENAME_EXCHANGE`; if the file it
  displaced is not the one backed up, it is swapped back.
- **Nothing is written while the game is running.** A write is refused while `BEA.exe`
  runs; on Linux that is a process Wine names `BEA.exe` (a tool that merely opens the file
  does not count), a check not yet seen against a live game.
- **Any earlier version can be put back from Backups.** Putting a file back is itself a
  write into the game, so it backs up the current files first.

Everything else only reads. Careers and settings open read-only as verified snapshots. A
copy saved elsewhere is always a **new** file: publication re-checks the source's identity
and content, stages and verifies every byte, publishes without replacing any existing file,
and reopens the result to compare it with the plan. Malformed inputs, changed sources,
linked paths, existing destinations and unavailable protected access fail closed; there is
no ordinary write fallback. File dialogs cannot delete files or create folders. An
uncertain result says a file may exist; it is never deleted or reported as verified. File
work runs on one worker thread, and closing waits for it.

On Windows the same writes use portable .NET file calls: a new file is moved into place
without replacing anything, and a replaced file is swapped with `File.Replace`, which keeps
the displaced file so it can be compared with its backup and the swap undone. That path's
logic runs in the tests on Linux; it has not been executed on Windows.

A receipt concerns that operation, not later changes by another program or what the game
does with the file. These checks do not prove behavior after power loss.

## File-safety boundary

[ProtectedSaveFiles](Files/ProtectedSaveFiles.cs) links the MIT
[`SaveLabFileTransaction.cs`](../../OnslaughtCareerEditor.AppCore/SaveLabFileTransaction.cs) and
[`FileMutationSafety.cs`](../../OnslaughtCareerEditor.AppCore/FileMutationSafety.cs) unchanged; it
imports no AppCore assembly or media library. On Linux it opens sources descriptor-relative
without following links, compares physical identity and link count, stages into an unnamed
file, flushes it, and publishes with a no-clobber link. [GameWrites](Files/GameWrites.cs)
builds backups and game-folder writes on the same primitives, with the portable path
described above for other systems. The Windows copy path locks ancestors and verifies
identity, but releases its staging quarantine and closes the handle before a path-based
move, then verifies the published identity; Windows execution remains unverified here, and
a Windows cross-export is not acceptance.

## Exact toolchain and rollback

[toolchain.json](toolchain.json) records the measured engine, SDK and template hashes and
the shared lock revision; `tools/companion_godot.py` verifies the installation and refuses
mismatches. `global.json` pins .NET SDK 8.0.424; the Godot SDK is `4.8.0-dev.6` and the
runtime `8.0.30`. Export presets target Linux x86_64 and Windows x86_64, and Godot's normal
.NET export bundles the runtime, so packages need no installed .NET. The Windows package
carries the companion's name and its emblem as the program icon, drawn by
[Emblem](Ui/Emblem.cs) at export time; the project itself stores no icon file. Adopt a later engine
only in an isolated worktree with updated pins, matching templates and a full rerun of the
suite, exports and captures; roll back with the preceding commit and its preserved engine.

See [PROVENANCE.md](PROVENANCE.md) for licensing and data boundaries.
