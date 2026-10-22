# Onslaught Companion

Status: paused (since 2026-10-16, until new requirements); C# application built entirely in code on Godot 4.8 dev6 .NET, organised around the player: careers, Goodies, editing, cheats, game settings, backups, music, voices, lore, and the game's models and textures; Linux executed checks, Windows runtime acceptance pending
Last updated: 2026-10-22 (review fixes: close never abandons a backup started while it asks, settings picker keeps unsaved changes (also when the shown file is picked again or a key edit is refused), CE check seen against a running CE on Linux (output kept), backups from another game folder go back after a confirmation naming both; data-safety fixes: restore checks the manifest hash and game folder, running check also for Onslaught CE and again before the swap, unsaved-changes prompts, right-hand Shift and Control; named Onslaught Companion; works with the original game only; relicensed GPL-3.0-only, lore CC BY-SA 4.0)
Summary: Onslaught Companion, the GPL-3.0-only app for Battle Engine Aquila players: today it works with the original game's Steam or retail install; it opens on that game and its careers, shows progress and Goodies, changes careers and settings only after a verified backup and a clear choice, keeps automatic backups that can be put back, plays and explains the game's own music, voices and lore, and saves copies of its models (glTF), textures (PNG) and sound effects (WAV).

Onslaught Companion is for players. It opens on their game and careers, and everything it
changes in the game is backed up first and can be put back. Retail reverse engineering, the
faithful game (the native source port, published separately as Onslaught CE; link added at
release) and the GPL Godot rebuild have separate owners; this project neither launches nor
depends on the rebuild. Tools for looking at raw bytes are kept, folded away under Advanced.

## Which game it works with

Today the companion works with **the original game only**: the Steam or retail install that
holds `BEA.exe`. It reads and writes that install's `savegames/*.bes` careers and its
`defaultoptions.bea`, and its Play button asks Steam to start the original game. It does not
yet read Onslaught CE's own career folder (`~/.local/share/onslaught-ce`, or
`%APPDATA%\Onslaught CE` on Windows), cannot launch Onslaught CE, and backs up only the
original game's careers and settings. It does know when Onslaught CE is running and then
writes nothing into the game folder, because CE reads the same install, and it refuses to save
a copy into CE's folder. Making it the Onslaught CE launcher and manager is the next step
(see below).

## Working lane

Development is paused (since 2026-10-16) until David sets new requirements; no branch is
active. The next item is making the companion the Onslaught CE launcher and manager: find,
launch and update CE, and show and edit its careers and settings in CE's own folder.
Original-game career and settings editing stays, with the same protected writes. Executable
patching and the copied-profile "safe launch" of the retired WinUI app are retired, not
planned; enhancements to the game belong in Onslaught CE as opt-in options. On resume, start
from `main` in a worktree of an internal-disk clone (the familiar checkout lives on a USB drive
and takes light I/O only) and run this project's `npm test`.

## Layout

Everything is C# on Godot 4.8 dev6 .NET. [Main.tscn](Main.tscn) is a one-node wrapper
that attaches [CompanionApp](Ui/CompanionApp.cs); every control, container, dialog
and style below it is constructed in code. There is no GDScript, saved resource or
editor-authored scene, and `npm run build` refuses to stage one.

| Folder | Owner of |
| --- | --- |
| [Careers](Careers/) | The career byte codec (`CareerSave`), immutable open snapshots (`SaveSession`), the open/publish/compare/install workflow (`CareerWorkspace`), each Goodie's rule and evidence (`GoodieFacts`, `GoodieUnlockRequirementService`) and cheat names (`CheatCodeCatalog`, `CheatSaveNameComposer`) |
| [Files](Files/) | The protected OS file boundary (`ProtectedSaveFiles` on `SaveLabFileTransaction` and `FileMutationSafety`), its worker thread, and game-folder writes in `GameWrites.cs`: the running-game check (`GameProcess`), backup sets (`Backups`) and the verified write on Linux and elsewhere (`GameInstaller`) |
| [Game](Game/) | Steam library discovery, the game folder and its files, the companion's remembered choices and backup folder (`GameFolder`), and the game's own text read from the install (`GameText`, `GameTextCatalog`) |
| [Options](Options/) | The settings block's reader and editor (`OptionsFile`), for `defaultoptions.bea` and the copy each career stores, and the physical-key table (`KeyTable`) |
| [Media](Media/) | The game's music, voice lines and cutscene list (`GameAudio`) |
| [Assets](Assets/) | The game's models, textures and bank sounds: the `.aya` envelope (`AyaContainer`), the mesh reader (`CmshReader`), DDS decoding (`DdsTexture`), the sound banks (`XapBank`), what each Goodie holds (`GoodieResources`), the install's lists (`AssetLibrary`), glTF export (`GltfExport`) and new-file-only exports (`ExportFiles`) |
| [Lore](Lore/) | The embedded lore library, its Markdown renderer and the campaign's mission list (`CampaignLoreComposer`) |
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
window**; use it when the desktop is available. Each command stages the project and the lore into a unique canonical `local-data/companion/`
directory with isolated imports, profiles, scratch and logs, and prints that directory.
Worktrees use the [canonical lab rules](../../LOCAL_LAB_OVERLAY.md); no research corpus
is copied.

`npm test` runs `Tests/CompanionTestRunner.cs` against an owned copy of the one tracked
[real-save fixture](../../tests_shared/fixtures/README.md) and a game-shaped folder built
from tiny original bytes, then the development runner's own checks (`tools/companion_godot.py`,
which builds, tests, captures, runs and exports the companion). It covers the codec on the real
bytes, Goodie edits, settings edits and the key table, the protected adapter and six Linux
publication races, Steam discovery, the game's text on a synthetic language table,
backups, automatic backups and writes into the game on both the Linux and the portable
(Windows) path, including a file that takes the name just before the swap, a career the
game saved after it was opened and a game that starts while the backup is made, the
Onslaught CE process and folder rules, backups kept apart per game folder, a backup copy
changed after it was made, the game-written keys and the right-hand Shift and Control,
music and voice grouping, every lore article and link, and
the interface driving its real controls: saving into the game, putting files back,
catching up after the game closes, and asking before unsaved changes are dropped.

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
**Extras** (Music & voices, Lore, Art & sound); and **Advanced**, folded away
(Career bytes). The header names the page, shows **Game running** while the original game
or Onslaught CE is open, and switches careers (or opens a career file, Ctrl+O). While Edit career or Game
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
  be earned but never shown; they are listed apart and always kept as they are. **What it
  shows** reads the Goodie from your install, as
  reverse-engineering/asset-formats/goodie-resources.md describes:
  - a picture is shown;
  - a model is named;
  - both open in Art & sound, which saves copies;
  - a video names its cutscene file (Bink video: watch it in the game);
  - a race level names its level.

  A Goodie the open career has not earned stays hidden until you press **Show it anyway**.
- **Edit career**: kill counts (only the three count bytes; the fourth is kept) and Goodies
  (unlock every Goodie, or pick them). Your changes are listed in words; the exact bytes
  are shown on request. **Save changes…** offers a new career in your game (named by you),
  replacing this career in your game, or a copy somewhere else.
- **Cheats**: a byte-identical copy of the career whose name switches on the cheats seen
  working in the Steam game (`MALLOY`, `TURKEY`, `Maladim`), added to your game or saved
  elsewhere.
- **Game settings**: the game's default settings (`defaultoptions.bea`, which the game reads
  when it starts), or the copy of the settings each career stores. The game does not apply a
  career's copy when that career loads, and may overwrite it the next time it saves the
  career ([save-format.md](../../reverse-engineering/save-file/save-format.md#options-entries)).
  It edits sound and music volume; invert flight and walking, vibration and controller layout
  for each player; mouse sensitivity (the game's own slider steps) and screen shape; and
  keyboard keys captured from a key press, in the two binding slots each action has (Slot 1
  and Slot 2; which slot the game gives to which player has not been checked in the game).
  Controller and mouse bindings are kept unless replaced; language and display mode are kept.
- **Backups** (of the original game's careers and settings): automatic backups (when the
  companion opens and after the game closes while it is open, only when something changed), the folder (`Battle Engine Aquila Backups` in
  Documents unless you choose another), Back up now, and every backup set, newest first,
  with why it was made and **Put back** for each file.
- **Music & voices** plays the soundtrack and voice lines from your install, grouped by
  mission with the game's own transcripts. Only files with an Ogg Vorbis header reach the
  decoder. Cutscenes are Bink video and are listed, not played.
- **Lore** reads the repository's lore library offline: the front door's shelves and
  reading order, a section outline, search, Back, Forward and Home (Alt+Left, Alt+Right;
  Ctrl+F searches), the map of Allium from your game's manual, and the manual itself in
  your browser. The campaign's mission list is read from your game's text, never shipped.
- **Art & sound** lists the game's 213 model files, 847 textures and its sound effects (the
  164 samples of each language's sound bank) from your install,
  previews each (a model as it stands at its first frame, a texture over a checkerboard) and
  saves a copy into a folder you choose: a model as binary glTF (`.glb`, with its textures
  embedded; Blender and most 3D tools open it), a texture as PNG, a sound effect as WAV (16-bit
  mono at 44,100 Hz, decoded as reverse-engineering/asset-formats/xap-sample-bank.md describes);
  a sound can also be played. The readers follow the
  public format documents (`reverse-engineering/asset-formats/cmsh-fields.md` and
  `cmsh-animation-keys.md`); the game's left-handed, Z-down model space is converted to
  glTF's right-handed, Y-up one. Copies are new files only, never written into the game
  folder or the backups. A copy carries the model's animations, one per animation mode, with
  the mode's frames in each animation's `extras`, and its skeleton as a glTF skin. The game
  does not bend normals with the bones, while glTF viewers do, so lighting on a moving limb
  can differ slightly from the game. Between frames, glTF turns keys smoothly where the game
  blends them as matrices, so the two agree exactly only at each frame.
- **Advanced**: **Career bytes** shows, read-only, either the open career's stored values
  (including both players' god flags) or, after you choose another career, every byte that
  differs between the two, named by region.

When the original game closes while the companion is open, or you come back to the companion, it
notices careers and settings the game saved, reads them again, backs them up if automatic
backups are on (after the game closed), and shows the latest. Changes you have not saved
are never thrown away for this; the companion says so instead.

## Known limits

- Nothing has been run on Windows; the Windows package is cross-exported and inspected only.
- Nobody has clicked through the app by hand or listened to its music and voices.
- The model preview shows each model at its first frame; the app never plays an animation. On
  2026-10-16, playing the exported animations inside a headless Godot (a development check, not the
  app) aborted the engine with an internal error and then crashed its crash handler, so the
  development probe only counts the animations and skins Godot's importer reads, and the pose
  check runs outside Godot (`tools/gltf_pose_check.py`). Copies play in Blender.
- The handedness conversion follows the game's culling convention; no mirrored text on a model
  has been checked against it.
- Behavior after a power loss during a write is not proven (see below).
- The Onslaught CE running check has been seen against a running CE only on Linux (Onslaught
  CE 0.1, its `bea` started from the package folder); spotting CE on Windows is untested, and
  there the companion says so beside its promise. CE's folder locations come from the port's
  source and packaging; only `BEA_USER_DIR` has been seen in use.
- Which player each binding slot serves (Slot 1 or Slot 2) has not been checked in the game, and
  key classes no game-written row confirms (for example top-row digits, punctuation and the
  right-hand Shift and Control) are stored by the same convention but marked as not yet seen.
- A career or copy chosen through a symbolic link in its path is refused rather than resolved.

## How files stay safe

Home makes three promises about your original game (its Steam or retail install), and the
code keeps them:

- **Nothing in your game changes without a backup first.** Only a career in `savegames/`
  or `defaultoptions.bea` is ever written. First, every career and settings file the companion
  can read (a 10,004-byte career or settings file) is copied to a new backup set outside the
  game folder, each copy read back and verified and listed with its SHA-256 in a manifest; any
  other file there is left untouched, and the backup says how many were skipped. A file being
  replaced must be one of the backed-up files and still match its fresh backup, and a career
  or settings file you opened must still match what you opened: if the game saved it since,
  nothing is written. The new file is staged, verified, swapped in
  and reopened. On Linux the swap is `renameat2` with `RENAME_EXCHANGE`; if the file it
  displaced is not the one backed up, it is swapped back. A drive without that exchange
  cannot have the displaced file checked, so there a replacement is refused before anything
  changes; new careers are still added with a no-clobber link. If a step after the new file is
  in place fails (the flush, the read-back, the clean-up), the companion says the file may
  have changed and leaves it as it is, with the backup named; it never reports that as
  nothing written, and never deletes or retries it.
- **Nothing is written while the game is running.** A write is refused while the original
  game or Onslaught CE runs (CE reads the same install's careers). The check is made before
  the backup and again just before the new file is swapped in. On Linux a process counts as
  the original game when its name is `BEA.exe`, when the program it runs (its first argument)
  is `BEA.exe`, or when it is a Wine loader given `BEA.exe`; a tool that only names the file
  further along its command line does not count. It counts as Onslaught CE when the program
  it runs is CE's launcher (`onslaught-ce-launch`, or `onslaught-ce.exe` on Windows), or is
  named `bea` (`bea.exe`) and sits in a folder that also holds that launcher, as an Onslaught
  CE package lays it out; a program called `bea` anywhere else does not count. On Windows the
  check looks for processes named `BEA` (which includes CE's `bea.exe`) or `onslaught-ce`. A
  CE program replaced while it runs (`/proc/PID/exe` ending in ` (deleted)`) still counts. On
  2026-10-22 the check found a running Onslaught CE 0.1 on Linux (comm `bea`, its program in the
  extracted package beside `onslaught-ce-launch`), before and after its `bea` file was replaced,
  and stopped finding it once CE exited (`Development/RunningCheck.cs` output saved in the ignored
  `local-data/companion/evidence/ce-running-check-2026-10-22.log` beside the harness that ran it);
  it has not been tried on Windows. On
  2026-09-26, with the Steam game running under Proton, the check found exactly the game's own process (`BEA.exe`, argv[0] `S:\steamapps\common\Battle Engine
  Aquila\BEA.exe`) and not Steam's launcher shim, the Proton script or the runtime wrapper;
  `python tools/companion_godot.py test --script Development/RunningCheck.cs` prints what it sees.
- **Any earlier version can be put back from Backups.** Putting a file back is itself a
  write into the game, so it backs up the current files first. The file is put back only if
  its bytes still match the SHA-256 the backup's manifest recorded. A backup made from another
  game folder (an install that moved, or another copy of the game) is put back only after a
  confirmation that names both folders. Automatic backups compare against the newest backup of
  the same game folder.

Two rules sit under all three. A backup is only ever the file as it was found, copied, read
back and hashed: the companion never makes an "original" from a file that may already have
been changed, never edits or replaces a backup, and never deletes one. And it never writes
`BEA.exe`. It reads it only to say which game it is: an install counts as the unmodified Steam
release only when its `BEA.exe` is exactly 2,506,752 bytes with SHA-256
`74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`
(`ExecutableIdentity.RetailSha256` in [GameFolder](Game/GameFolder.cs)), the pristine retail
specimen's identity.

Everything else only reads. Careers and settings open read-only as verified snapshots. A
copy saved elsewhere is always a **new** file: publication re-checks the source's identity
and content, stages and verifies every byte, publishes without replacing any existing file,
and reopens the result to compare it with the plan. Malformed inputs, changed sources,
linked paths, existing destinations and unavailable protected access fail closed; neither
copies nor writes into the game have an ordinary write fallback. A copy is never saved inside a
game folder (one holding `BEA.exe` and `data/`) or inside Onslaught CE's own folder
(`BEA_USER_DIR` when set, else `$XDG_DATA_HOME/onslaught-ce`, else
`~/.local/share/onslaught-ce`; `%APPDATA%\Onslaught CE` on Windows). File dialogs cannot
delete files or create folders. An uncertain result says a file may exist; it is never deleted or reported as verified. File
work runs on one worker thread, and closing waits for it. Switching careers or closing the
companion while Edit career or Game settings holds unsaved changes asks first.

On Windows the same writes use portable .NET file calls: a new file is moved into place
without replacing anything, and a replaced file is swapped with `File.Replace`, which keeps
the displaced file so it can be compared with its backup and the swap undone. That path's
logic runs in the tests on Linux; it has not been executed on Windows.

The tests inject the two hard cases rather than meeting them for real: a switch makes the
exchange report itself unsupported, and a failure is raised just after the file is in place,
on both the Linux and the portable path. No drive that really lacks the exchange has been
tried.

A receipt concerns that operation, not later changes by another program or what the game
does with the file. These checks do not prove behavior after power loss.

## File-safety boundary

[ProtectedSaveFiles](Files/ProtectedSaveFiles.cs) is built on
[`SaveLabFileTransaction.cs`](Files/SaveLabFileTransaction.cs) and
[`FileMutationSafety.cs`](Files/FileMutationSafety.cs), the file-safety source the
retired WinUI application's AppCore library used, moved here unchanged (the date is in
[PROVENANCE.md](PROVENANCE.md); AppCore still compiles the same file).
`Files/SafetyCompatibility.cs` holds what that source still names from AppCore: one size
constant and two stubs that always refuse. On Linux it opens sources descriptor-relative
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
