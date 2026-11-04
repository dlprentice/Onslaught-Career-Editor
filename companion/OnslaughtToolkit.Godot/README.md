# Onslaught Companion

Status: active — companion for the original game and Onslaught CE
Last updated: 2026-11-04 (Mission project Save as reaches Linux CE development source, with object-dependent height; CE 0.1.13 acceptance limits)
Summary: Onslaught Companion manages original-game and Onslaught CE careers, verified backups and supported settings; it starts only CE packages it identifies as 0.1.7 or later and explains how CE updates.

Onslaught Companion is for players. It opens on their game and careers, and everything it
changes in the game is backed up first and can be put back. Retail reverse engineering, the
faithful game (the native source port, published separately as
[Onslaught CE](https://github.com/dlprentice/onslaught-ce)) and the GPL Godot rebuild ([onslaught-godot](https://github.com/dlprentice/onslaught-godot)) have separate owners; this project neither launches nor
depends on the rebuild. Tools for looking at raw bytes are kept, folded away under Advanced.

## Which game it works with

Choose **Original Battle Engine Aquila** or **Onslaught CE** on Home. The original game uses
its installation's careers and `defaultoptions.bea`; its Play button starts Steam. With CE selected,
the companion shows CE's own careers and additional original-game files for browsing and backups.
When both folders have the same filename, ignoring letter case, the companion shows CE's own copy.
It labels careers from the original installation as read-only:
changes can be saved as a new named CE copy, but cannot replace the original through the CE choice.
CE 0.1.4 merges these sources on Linux and Windows; older Linux CE releases could omit the original
folder once a CE savegames folder existed. Original files also supply music, voices and art.
For careers, the companion checks the two game data files required by CE, tries `BEA_GAME_DIR`
then `ce.ini`'s `gamedir`, and finally searches CE's Steam locations. Choosing a different original
folder for pictures and music does not change that CE career source.

**CE launcher safety.** Released Onslaught CE launchers 0.1.0–0.1.6 can delete neighbouring
`<program folder>.old-*` files and folders when they start, even with update checks off; CE's
[manual migration](https://github.com/dlprentice/onslaught-ce#manual-migration-from-affected-launchers)
says not to start them at all. Before executing a launcher, the companion reads the version on the first
line of the package's `README.txt` and refuses Play and the version query for 0.1.0–0.1.6, for a missing or
unreadable header, and for a launcher whose `--version` answer disagrees with that header. The one accepted
difference is a 0.1.8 or later package whose launcher reports a newer version: CE's updater installed that version
under the package's own `versions` folder and the launcher hands off to it. Install 0.1.8 or later by hand into a
new empty folder.

CE's Play button uses `onslaught-ce` (Linux) or `onslaught-ce.exe` (Windows). The companion looks
for a launcher among installed commands and remembers a launcher you choose; portable CE packages
can live elsewhere. For a package that passes the safety check it asks that launcher for its version
with `--version`, without starting the game. An isolated Linux acceptance run read CE 0.1.4's actual
version and launched its real package (before this safety check existed).
It edited a copy of a game-created career through the companion's controls, made and verified backups,
and loaded the edited Unicode-named career through CE's own keyboard-driven Load menu. The game reached
level selection and wrote the exact edited career bytes through its successful-load path. This is an
automated offscreen check, not a human click-through or a full mission playthrough; see
[the acceptance record](../../VALIDATION.md#companion-with-real-onslaught-ce--october-24).

CE's writable user folder is chosen in this order: `BEA_USER_DIR`, then Linux
`$XDG_DATA_HOME/onslaught-ce` or `~/.local/share/onslaught-ce`; Windows uses
`%APPDATA%\Onslaught CE`. Relative paths, drive roots and the home folder itself are refused.
The launcher creates its user folder; the companion does not invent an installation. CE career
writes go to that user folder.
Both the user folder and backups must be outside CE's package folder, which updates can replace,
and its selected original game-data folder, including data-only installs without `BEA.exe`. For custom folders,
use separate, ordinary directories; do not use a link, junction or bind mount into either game folder. The current
checks do not detect every folder alias, so the player must make sure these locations are separate.

The companion reads and writes CE's `.bes` careers with the same verified backups and saved-file
checks used for original-game careers. It refuses a write if it detects the game running, if a file has
changed since it was opened, or if the path uses a symbolic link. CE settings edits are limited to
**Check for updates** (`update_check`) and **Record sessions** (`record_sessions`) in `ce.ini`.
Unknown lines stay intact; invalid text encoding is refused. Saving makes a verified settings copy
outside CE's user folder, holds and checks the copy through publication, prepares the new file beside the existing one,
replaces it in one step and checks the saved bytes. These settings backups are named `onslaught-ce-settings-*` and are kept
separately from career backup sets; automatic backups and the Backups page manage careers, not
these settings copies. Backup binding and its race controls have run on Linux's native and portable writer paths;
the new settings-backup binding has not been exercised on Windows. Close CE and the original game before saving and
wait for the save to finish before starting either. The process checks do not lock out a start immediately after the
last check; CE's own settings writer can
replace a successful companion change with an older snapshot. A shared cross-process writer protocol remains open.

**Updates** on Home contacts nothing. CE 0.1.8 and later check CE's signed update feed when they start and
install a new version only when the player chooses Update; 0.1.7 has no update code, so players on 0.1.7 or
older download 0.1.8 or later once and extract it by hand into a new empty folder. The button shows those steps.
The **Check for updates** setting (`update_check`) is the `ce.ini` switch CE 0.1.8 and later read
(`update_check=0` turns checking off); turning it off does not make a 0.1.0–0.1.6 launcher safe to start. The
signed-feed verifier (`CeUpdateFeed`: CE's update feed v2, `ce-update-v2.json`, with CE's pinned Ed25519 key over
the feed's domain prefix and exact bytes, and the MIT-licensed BouncyCastle.Cryptography package, whose notice is
included in exports) stays in the source for its tests; the companion does not call the verifier's signed-feed methods and
never reads the old `latest.json`.

The source contract was read at
[CE 0.1.4](https://github.com/dlprentice/onslaught-ce/tree/93ea9145d6d4d9f36f7cd9a800506ebf5bcbd788):
`port/updater/ce_launch.c`, `port/updater/ce_report.h`, `port/tools/package.py` and
`port/tools/sign_release.py`. Both
[Linux files.cpp](https://github.com/dlprentice/onslaught-ce/blob/93ea9145d6d4d9f36f7cd9a800506ebf5bcbd788/port/platform/linux/files.cpp)
and [Windows files.cpp](https://github.com/dlprentice/onslaught-ce/blob/93ea9145d6d4d9f36f7cd9a800506ebf5bcbd788/port/platform/windows/files.cpp)
merge careers from the user and original-data folders. The original-install rows remain read-only in the
companion's CE mode. Its data-folder selection follows
[the launcher's validation and search](https://github.com/dlprentice/onslaught-ce/blob/93ea9145d6d4d9f36f7cd9a800506ebf5bcbd788/port/updater/ce_launch.c).

On 2026-10-29 part of that contract was read again at CE 0.1.10
([d6aafb7](https://github.com/dlprentice/onslaught-ce/commit/d6aafb7)). Still true there: the two data-file hashes the
launcher admits an install by (`install_problem` in `ce_launch.c`) are the ones the companion pins; the search order for the
data folder is unchanged (`BEA_GAME_DIR`, then `ce.ini`'s `gamedir`, then Steam, then the launcher asks); the published
Linux launcher, run with a private home folder, prints `Onslaught CE V0.1.10, build d6aafb7d04b2`, which the companion's
version pattern reads; and the first line of the published packages' `README.txt` is `Onslaught CE V0.1.10`, which the
package-header check accepts. **Not read again:** the Windows `files.cpp` career merge, and `package.py` beyond that header
line. Between 0.1.4 and 0.1.10 `ce_launch.c`, `package.py` and the Windows `files.cpp` changed a good deal, so what this
README says about those files is as of 0.1.4 until they are read again.

**Acceptance of these flows (careers, backups and settings, with the companion starting the real CE launcher) against a
real CE 0.1.7 or later package: one Linux run, on CE 0.1.13.** On 2026-11-03 the opt-in `CeLiveCheck` ran its prepare,
settings, launch and restore phases against the released CE 0.1.13 Linux package, checked against the release's signed
feed first. On a copy of a game-created career in an isolated folder, the production controls edited the career with a
verified backup, saved both CE settings with verified backups and refused stale writes; the companion refused career and
settings writes while the real CE launcher and game ran offscreen; CE's own keyboard-driven Load menu loaded the edited
career byte for byte; and the Backups page put the exact original bytes back. It is an automated Linux check driven by
programmatic page actions, not a human click-through; see
[the dated acceptance record](../../VALIDATION.md#companion-with-real-onslaught-ce-0113--november-3). The earlier
real-package runs are CE 0.1.4 on Linux and a `0.1.6-dev` package on Windows (below), and no run of these flows on
Windows is newer than that one. The 0.1.8 hand-off to a package's `versions` folder is covered by tests with fixture
launchers only, and the 0.1.10 reading above is a reading of files and of one `--version` line, not a launch, a
user-interface session or a career edit. The Level editor's Play button, which starts a real CE package, is a different
path: its runs are described under "What it does", and they do not stand in for these flows.

Native Windows checks exercised production process detection and protected file/settings writes;
CE also loaded the edited Unicode career through its own menu. Those backend/load experiments used the
then-admitted CE development builds; they are not companion UI acceptance of the final 0.1.5 package.
In the pinned 0.1.4 source, the launcher uses
[`AttachConsole(ATTACH_PARENT_PROCESS)` and `CONOUT$`](https://github.com/dlprentice/onslaught-ce/blob/93ea9145d6d4d9f36f7cd9a800506ebf5bcbd788/port/updater/ce_launch.c).
Separate native Windows launcher checks reproduced CE 0.1.4 sending redirected version output to
an attached console instead of its pipe. Onslaught CE 0.1.5 publishes that launcher correction
([the 0.1.5 source](https://github.com/dlprentice/onslaught-ce/blob/52c8c1f91e98cd2ff3573978ce608987c2ab170e/port/updater/ce_launch.c)).
Earlier standalone version queries also captured an intermittent Windows loader wait opening SDL3.dll.
The later selected development workflow below read its actual version successfully; it does not establish
a general resolution of those earlier startup waits. See
[NativeChecks](../OnslaughtToolkit.NativeChecks/README.md) for the executed paths and limits.

A native Windows development package at companion source `b4b32d0f` passed the `CeLiveCheck` workflow with
the selected CE `0.1.6-dev` package, source `9ed8c56e81d3`. Production discovery read the actual launcher
version, then programmatic production-page actions edited, backed up and reopened a copied real career,
published a Unicode-named copy, refused stale inputs, saved both supported settings and restored the exact
baseline. Home, Settings and restored Backups screenshots were inspected first-hand and their selected
controls and text were readable. Godot used its embedded ANGLE fallback with Microsoft Basic Render Driver
over D3D11 software. This was a development invocation under `DEBUG_PROCESS` and a private Windows job;
ordinary release invocation, physical mouse/keyboard input, file dialogs, Windows ACL failures, hardware
GPU rendering and audio remain unvalidated. The gate never starts a game or requests updates. See
[the dated acceptance record](../../VALIDATION.md#companion-native-windows-development-ui--october-25) and
[the opt-in workflow contract](../OnslaughtToolkit.NativeChecks/README.md#godot-ui-workflow-gate).

## Layout

Everything is C# on Godot 4.8 beta1 .NET, targeting .NET 10 (`net10.0`). [Main.tscn](Main.tscn) is a one-node wrapper
that attaches [CompanionApp](Ui/CompanionApp.cs); every control, container, dialog
and style below it is constructed in code. There is no GDScript, saved resource or
editor-authored scene, and `npm run build` refuses to stage one.

| Folder | Owner of |
| --- | --- |
| [Careers](Careers/) | The career reader and writer (`CareerSave`), immutable open snapshots (`SaveSession`), the open/publish/compare/install workflow (`CareerWorkspace`), each Goodie's rule and evidence (`GoodieFacts`, `GoodieUnlockRequirementService`) and cheat names (`CheatCodeCatalog`, `CheatSaveNameComposer`) |
| [Files](Files/) | The protected OS file boundary (`ProtectedSaveFiles` on `SaveLabFileTransaction` and `FileMutationSafety`), its worker thread, and game-folder writes in `GameWrites.cs`: the running-game check (`GameProcess`), backup sets (`Backups`) and the verified write on Linux and elsewhere (`GameInstaller`) |
| [Game](Game/) | Steam library discovery, the game folder and its files, careers left in the retired Windows toolkit's copied installs (`OldSafeCopies`), the companion's remembered choices and backup folder (`GameFolder`), the game's text (`GameText`, `GameTextCatalog`), CE package discovery (`CeInstallation`) and temporary level play (`CePlay`, `CePlayFolder`) |
| [Options](Options/) | The settings block's reader and editor (`OptionsFile`), for `defaultoptions.bea` and the copy each career stores, and the physical-key table (`KeyTable`) |
| [Media](Media/) | The game's music, voice lines and cutscene list (`GameAudio`) |
| [Assets](Assets/) | The game's models, textures and bank sounds: the `.aya` envelope (`AyaContainer`), the mesh reader (`CmshReader`), DDS decoding (`DdsTexture`), the sound banks (`XapBank`), what each Goodie holds (`GoodieResources`), the install's lists (`AssetLibrary`), glTF export (`GltfExport`) and new-file-only exports (`ExportFiles`) |
| [Lore](Lore/) | The embedded lore library, its Markdown renderer and the campaign's mission list (`CampaignLoreComposer`) |
| [Levels](Levels/) | World-body reading/writing and level-archive reading, undoable changes (`EditSession`), the editor's application model (`LevelEditorModel`), terrain lookup and map (`Heightfield`, `MapView`), script/source/name readers and structural checks, and separate CE mod publication (`ModStager`) |
| [Ui](Ui/) | The Flight-deck theme and icons, the shell, career cards, the save-choice dialog, the game's art read from the install (`GameArt`) and one class per page |
| [Tests](Tests/) | Every behavioral contract, run headlessly inside Godot |
| [Missions](Missions/) | The mission script compiler (`ScriptCompiler`), used by the installed-level Scripts view and checked against the Toolkit's reference compiler, with documented missing-header and stale-source cases. Separately, authored project documents (`CeMissionProject`), undoable edits (`CeMissionProjectEditor`) and JSON (`CeMissionProjectJson`); their page is `Ui/Pages/CeMissionProjectPage.cs` and protected file publication is `Files/CeMissionProjectFiles.cs` |
| [Development](Development/) | Development-only entries: screen captures, the local retail gates (`LevelsGate`, `ScriptsGate`), export license metadata and the Windows program icon (`IconWriter`) |

`Tests/` and `Development/` compile only into development builds; release exports
exclude them from both the assembly and the package.

Start editor changes at [LevelEditorPage](Ui/Pages/LevelEditorPage.cs), which passes actions to
[LevelEditorModel](Levels/LevelEditorModel.cs). The compiler starts at [ScriptCompiler](Missions/ScriptCompiler.cs);
the [source map](../../PROJECT-INDEX.md#level-and-mission-editor) connects world edits, script checks, mod publication
and temporary CE launch to their owners. [Python references and generators](../../tools/README.md#editor-references-and-generators)
provide authored vectors separately from the optional retail comparisons. The [content catalogue](../../tools/README.md#content-catalogue)
is a separate Python analysis tool; this application does not load its generated output.

## Build, test, capture, run and export

Use Linux x86-64 with Git and Python 3.12 or newer. The repo-local setup installs the exact Godot .NET and .NET SDK
versions pinned in [toolchain.json](toolchain.json). The public [download manifest](../../tools/companion_toolchain.json)
names official URLs, sizes, checksums and licences. No private repository or installer is required.

The host still needs the native libraries required by [.NET on your distribution](https://learn.microsoft.com/en-us/dotnet/core/install/linux-scripted-manual#dependencies),
including ICU and OpenSSL, and a working graphics driver for the interactive application. The Companion uses Godot's
[Compatibility renderer](https://docs.godotengine.org/en/stable/about/system_requirements.html), requiring OpenGL 3.3.
Headless tests need no display. The setup never runs a system package manager or elevates privileges.

From a public clone on an internal disk:

```bash
python tools/companion_toolchain.py setup
python tools/companion_toolchain.py verify
```

The default installs below ignored `local-data/toolchains/companion/` in the canonical checkout. Engine and SDK
downloads total about 318 MiB; allow about 1.2 GiB for the retained archives and installation, plus build outputs.
The setup reuses matching downloads and refuses changed installations instead of overwriting them. It does not
modify system tools, PATH or shell startup files. Build commands select the verified local SDK themselves. For a
separate installation beneath this checkout's `local-data/`, use `setup --root DIR` and pass the same
`--toolchain-root DIR` to `companion_godot.py`.

Export templates are optional for development. Before exporting either platform, run:

```bash
python tools/companion_toolchain.py setup --with-templates
```

That adds approximately 1.1 GiB of downloads plus extracted templates. The whole installation remains private,
ignored build data; only the setup code and pins belong in Git. Setup contacts the official Godot GitHub releases
and Microsoft SDK download service; restore contacts nuget.org for pinned packages. No game data or usage data is sent.

A maintainer can still explicitly select an existing shared installation with `--shared-lock FILE` or
`ONSLAUGHT_SHARED_LOCK`. That optional legacy route retains its provenance checks. `--toolchain-root DIR` explicitly
selects the public installation even if a shared-lock environment variable is set. Neither route silently falls
back to a different engine. `--engine PATH`, if provided, must match the selected verified executable.

A game installation is unnecessary for the authored Companion gate. The [documentation and Python checks](../../README.MD#build-and-run)
also work without Godot. With public setup complete, use the commands in [package.json](../../package.json):

```bash
npm run build:companion-godot
npm test
npm run capture:companion-godot
npm run run:companion-godot
npm run export:companion-godot -- --platform both
python tools/companion_godot.py audit
```

`audit` restores outside locked mode with
NuGet's vulnerability audit over direct and transitive packages (it needs nuget.org); the
build's own restore stays locked and does not audit, so a new advisory never changes a build.
Each check, build, test, run and audit leaves an output folder; the runner keeps the newest five
of each per worktree and removes older ones. Export and capture folders are never removed.

Build, test, capture and export never open a window on the desktop. **Run opens a
window**; use it when the desktop is available. Each command stages the project and the lore into a unique canonical `local-data/companion/`
directory with isolated imports, profiles, scratch and logs, and prints that directory.
Worktrees use the [canonical lab rules](../../LOCAL_LAB_OVERLAY.md); no research corpus
is copied.

On machines with the shared wrapper, `ONSLAUGHT_GODOT_HEADLESS=godot-headless npm test` routes engine checks
through it. Tests and captures use a private HOME and clear inherited CE user-folder overrides.

`npm test` runs `Tests/CompanionTestRunner.cs` against an owned copy of the one tracked
[real-save fixture](../../tests_shared/fixtures/README.md) and a game-shaped folder built
from tiny authored bytes, then the development runner's own fake-tool checks (`tools/companion_godot_tests.py`).
The runtime suite checks the career reader and writer
against the real bytes, Goodie edits, settings edits and the key table, the protected adapter and six Linux
publication races, Steam discovery, the game's text on a synthetic language table,
backups, automatic backups and writes into the game on both the Linux and the portable
(Windows) path, including a file that takes the name just before the swap, a career the
game saved after it was opened and a game that starts while the backup is made, the
Onslaught CE process and folder rules, backups kept apart per game folder, a backup copy
changed after it was made, the game-written keys and the right-hand Shift and Control,
music and voice grouping, every lore article and link, and
the interface driving its real controls: saving into the game, putting files back,
catching up after the game closes, and asking before unsaved changes are dropped.

The automatic capture route is an optional maintainer workflow, separate from public build/test setup. It requires
a compatible hidden-output wrapper selected with `--offscreen PATH`; the bootstrap does not install a desktop
compositor or this machine-specific wrapper. Contributors can inspect the application through `npm run dev` on their
own desktop. Automated agents must follow their user's rules before opening a window.

With that wrapper available, `npm run capture:companion-godot` renders every page and state at 1280×800 and
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
**Extras** (Music & voices, Lore, Art & sound, Level editor); and **Advanced**, folded away
(Career bytes). The header names the page, shows **Game running** while the original game
or Onslaught CE is open, and switches careers (or opens a career file, Ctrl+O). While Edit career or Game
settings has unsaved changes, a bar under the page counts them and offers Save (Ctrl+S)
and Undo.

**Home**, with the original game selected, finds the game through Steam (native, Flatpak and Snap
on Linux; the registry and Program Files on Windows) or a folder you choose, and checks `BEA.exe` against the Steam
release by SHA-256. It shows the render from the game's manual as its banner when the
install has it, a Play button for a Steam install (`steam://rungameid/1346400`), your
careers as cards with their progress, adding a career file to the game, the safety net
(automatic backups, Back up now, and the three promises below), and ways into Goodies,
Lore, Music & voices and the game's own manual. The career saved most recently opens by
itself, read-only. On Windows, if the retired WinUI toolkit (v1.0.11) left copied installs
in `%APPDATA%\OnslaughtCareerEditor\GameProfiles` (its "safe launch"), Home lists every `.bes`
in each copy's `savegames`, `saves` and `Save` folders and its top folder (the folders the old
toolkit's own rescue searched) and saves any career-sized one as a checked copy elsewhere; a file
of another size is listed as one that cannot be copied, so no career disappears without a word. It
never changes or deletes those copies. That listing and the copy are tested on a scratch folder on
Linux; neither has run on Windows, and nobody has looked at the panel on screen.

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
  replacing this career where allowed, or a copy somewhere else. An original-install career
  opened with CE selected can only be saved as a new copy.
- **Cheats**: a byte-identical copy of the career whose name switches on the cheats seen
  working in the Steam game (`MALLOY`, `TURKEY`, `Maladim`), added to your game or saved
  elsewhere.
- **Game settings**, with the original game selected: the game's default settings
  (`defaultoptions.bea`, which the game reads when it starts), or the copy of the settings each career stores. The game does not apply a
  career's copy when that career loads, and may overwrite it the next time it saves the
  career ([save-format.md](../../reverse-engineering/save-file/save-format.md#options-entries)).
  It edits sound and music volume; invert flight and walking, vibration and controller layout
  for each player; mouse sensitivity (the game's own slider steps) and screen shape; and
  keyboard keys captured from a key press, in the two binding slots each action has (Slot 1
  and Slot 2; which slot the game gives to which player has not been checked in the game).
  Controller and mouse bindings are kept unless replaced; language and display mode are kept.
- **Backups**: careers for the selected game, plus `defaultoptions.bea` for the original game.
  CE career backups include original-install careers in its combined list; `ce.ini` backups
  are separate, as described above. Automatic backups run when the companion opens and after the
  game closes while it is open, only when something changed. The page shows the folder
  (`Battle Engine Aquila Backups` in Documents unless you choose another; on Windows in `%LOCALAPPDATA%\Onslaught Companion`, which
  Windows does not sync, because Documents is often a OneDrive folder), Back up now, and every backup set, newest first,
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
- **Level editor** opens one of the game's levels from its `data/resources` folder and lists what the level's own
  world places (the player's start, units, waypoints, triggers and the rest) with each row's kind, name (or the definition
  it names) and X, Y and Z. Choose an object, type new coordinates and press Enter: they are read as the Toolkit's
  move tool reads a coordinate and stored as the 32-bit float the world stores, and the page says when that is a slightly
  different number than you typed. A stored -0, which ground units have, is shown as -0 and kept unless you type another value.
  A move can be undone, redone and reset; a position outside the 0 to 512 square the terrain covers is warned about, for a moved object and for a copy; and the
  result is saved as an Onslaught CE mod, a new folder holding `mod.json` and the level's world file, never inside the game
  folder or the backups (even one that does not exist yet) and never over an existing folder. A move you have not saved as a mod
  is asked about before it is dropped when you close the Companion, open another level or choose another game folder, and
  switching games is refused, with a message, until the move is saved or undone. Only a level's own world is changed: the base
  world a level also loads is mentioned, not edited. Onslaught CE loads a world file from a mod on Linux only for now, from 0.1.11 on, and only from a version
  whose README's Mods section lists world files. The page's reader and writer are checked against the Toolkit's Python reference
  (`tools/level_editor_vectors.py`) and, on a game install, against every world body in it; the file it saves for a move of one
  Target Tank is byte for byte the one the Toolkit's pipeline stages for the same move, whether the move was typed or made by
  dragging its mark on the map.

  The page also draws a **map** of the open level, beside the table (below it in a narrow window; the Map switch beside the
  search hides it). Its terrain is hill-shaded relief with the water tinted, built from the level's terrain with the game's own
  height lookup (the Toolkit's `tools/heightfield_lookup.py` is the reference the Companion's version is checked against, on
  generated vectors and, on a game install, on every level's terrain); no game texture is used. Every placed thing is a mark
  by kind: the start, units, waypoints, sphere triggers at their radius, buildings and features, and the rest as dots; X runs
  right and Y runs up. The wheel zooms about the pointer, dragging the background pans, Home shows the whole square (and so does a new window size, until you have zoomed or panned), a click
  on a mark selects it in the table and the fields, and dragging a mark moves it: the mark follows the pointer, Esc puts it
  back, and letting go moves X and Y to the place under the pointer (to a hundredth) and keeps Z as it was, a stored -0
  included, as one move that can be undone. With a mark selected and the map focused, the arrow keys nudge it, 0.5 a press (Shift 5, Ctrl 0.05; up is +Y), each press one
  move that can be undone (a held key's repeats count as presses; nobody has tried a real held key). Only the pressed axis changes, and it lands on the hundredth as a drop does; the other axis and Z stay as they were, bit for bit. **Copy this unit** (for a selected unit; a start, trigger, path point, spawner or building cannot be copied yet) adds a copy at the end of the level's list, 10 units to its right under the name `<name> copy`, selects it so it can be moved at once, and counts as one change that Undo takes back; it keeps the original's script and target (a unit whose script ends the level does so for the copy), and it is appended after every row so no path, target or career index changes, the saved world holds one more thing, and a base world is never given one. **List only the moved objects** in the changes box makes the table show just the objects that have been moved or copied, to look a long session over. A moved object is amber on the map with a line from where the level has it, and a
  readout gives the world position and the ground's height under the pointer. The map's mouse paths are tested with events
  pushed into the window; how a drag feels has been tried only by scripted events. The map's orientation was checked in Onslaught CE
  on level 100: two Target Tanks were dragged on the map, one straight ahead of the player's start and one 25 degrees to the
  map's left of that, and in a private CE build that loads world files from mods (offscreen, frames looked at) the first stands
  at the crosshair and the second well to its left, so the map is not mirrored. That is one level and one heading, a mod this
  page saved, not played by anyone; there has been no Windows run.

  The **Scripts** switch beside the Map switch shows the level's mission scripts in place of the table and the map (their source is read only until Edit source is turned on, below). The
  list gives each compiled script with what names it (how many objects of the level) and the events it handles, then the base
  world's scripts, dimmed; the selected script's installed source, the `.msl` file it was compiled from, is shown beside it with line numbers
  and the keywords coloured, and a card in the right-hand column says what the script handles, which game functions it calls, and
  which objects name it (each a button that shows the object on the table and the map). Selecting an object that names a script
  offers a button for it in the same way. The game never reads these source files (it runs the compiled scripts in the level's world),
  so the page says so, says which file is missing when one is, and says when an object names a script the level does not have; a source
  may differ from what was compiled, which the Toolkit's `tools/msl_gate.py` checks per script. A click in a quoted text of the
  source says what in the level has that name, with a button for each that goes to it: an object by its own name, a waypoint
  path, a script, or the scripts that handle an event of that name. An object of the level's base world is named too, without a
  button, because this page does not list that world's objects. The scripts take names as quoted texts and nothing says which
  call reads which text as what, so this goes by the name alone; about three quarters of the quoted texts in the shipped sources
  name something in their level or its base world. The **Paths** switch under the map draws every waypoint path faintly through
  the objects it names, and a path button, from the source or from an object that is a point of the path, highlights that path on
  the map, numbered and with an arrow on each leg, and brings it into view. A path names objects by their place in the world's
  thing list, which is the reading under which the shipped paths run from point to point (measured against shifts of one and
  two). The game keeps a slot as a point of the path only if it names a waypoint (`CWaypointPath::Load` in the decompilation), so
  the page draws, numbers and counts only those: about one slot in five names a unit, a spawner or another kind of object and is
  dropped, and an object that only such a slot names is on no path. The game searches the first matching waypoint path in a list
  with the base world's paths before the level's own (`CWaypointManager::FindNearest`). For a quoted first argument of
  `FollowWaypoint` or `FollowWaypointWait`, the page models the C-locale byte comparison: ASCII letters match in either case,
  other bytes match exactly, and a NUL ends the name. The level's own path gets a button (which says when the compared case differs);
  a base world's path is named with nothing to go to. A matched path with no usable waypoints gives the game no waypoint. Other
  process locales and native Windows comparison are not verified. Empty quoted names are not resolved by the page. Every other name is matched as written. The list,
  the links and the names are read from the compiled code, the level's objects and the sources, and
  checked against the Toolkit's reference (`tools/level_editor_vectors.py gate-table`, its SCRIPTS, NAMES and PATHS rows) on a game
  install, with the native names generated from the Toolkit's table (`tools/script_tables.py`). Reading writes nothing.

  The Scripts view can also **edit a script's source**. **Edit source** makes the source view typeable for one of the level's own
  scripts that has an installed source file (a base world's script is shown and not edited, and a script whose file is missing says so
  on the button). **Compile and use** compiles the text with the compiler in `Missions/` (headers from the game folder; the compile
  session's two counters start where the shipped script's do, so what the edit does not touch keeps its names) and, if it compiles,
  makes the open level use the new script as one edit: **Undo** takes it back, Redo brings it back, and **Put the shipped script back**
  is an edit too. A source that does not compile changes nothing, says "line N: ..." and puts the caret on that line. The compiler's
  notes (how a mixed chain of operators was grouped, a handler the game never calls, a variable declared twice) are shown with the
  result, and so is one warning about the script the level now uses: a call to `Damage` beyond the shipped script's can crash a level in
  the game as it is, when the damaged unit has a script of its own and the call is inside a running handler, because the game's script
  machine cannot be entered twice (the design document's section 8 has what is and is not known; Undo takes the warning away with the
  script). "Your changes" says "1 script replaced: NAME (what differs)" beside the
  objects moved. Text that was typed and is not in use (the level's script is not what it compiled to) stays with its script while
  another is chosen, counts as a change when the companion, the level or the game is left (the page asks first), is named in "Your
  changes" and is written nowhere. **Save as mod** writes the world
  file with the replaced script, and only when every replaced script passes the structural check (`ScriptChecker`: the opcodes,
  operands, jump targets, game functions and their argument counts, entry points, handlers, symbol tables and stack balance the game's
  loader and script machine assume); the mod holds the world file only, so the edited source is not kept beside it. **Play this level with the changes** starts Onslaught CE at the
  open level with the changes as they are (nothing is saved), in a temporary CE folder of its own: a copy of your ce.ini with only this mod switched on and recording and the update check off,
  your options file (never a career) and the mod. It is designed to leave your own CE folder, ce.ini and careers untouched. In one offscreen run the scratch player's settings, stand-in career and tape were unchanged and the temporary folder was removed. The Play feature needs Linux and CE 0.1.11 or later,
  and a recorded session switches mods off, which the copy of ce.ini avoids. The page was driven
  by events in tests and looked at in offscreen captures, and its `scriptmod` capture staged one edit (a tutorial message of level 100) as a mod that Onslaught CE ran on
  Linux, offscreen and live, with the edited subtitle on screen beside control runs (the mission editor design's section 16 says how and what it does not show); nobody has used
  it or the Play button by hand (the button ran once offscreen through the released 0.1.12 launcher, section 17 of the design), no other script edit has been run, and there has been no native Windows run. Onslaught CE switches mods off under a deterministic clock, a tape, probes, a
  recording, a pilot or a network session, so a run that should load a mod is a live one.

  The page is laid out for a window of about 1366 by 800 or more. In a smaller one, down to the Companion's 1024 by 700
  minimum, the map is a small overview, the table is narrower, the right-hand column scrolls and the notice a save leaves is
  scrolled into view there; the Map switch gives the table the whole column back. The design and what is still planned
  (adding and deleting things) are in
  [`roadmap/companion-level-editor.md`](../../roadmap/companion-level-editor.md). The [mission-editor roadmap](../../roadmap/companion-mission-editor.md) describes current limitations and planned work.
- **Mission project** creates authored placements and source independently of an installed level. Its
  [workflow and limits](#mission-project) describe 3D placement, the linked-map preview, project Save/Open and the
  bounded placement path into CE development source.
- **Advanced**: **Career bytes** shows, read-only, either the open career's stored values
  (including both players' god flags) or, after you choose another career, every byte that
  differs between the two, named by region.

When the selected game closes while the companion is open, or you come back to the companion, it
notices careers and settings the game saved, reads them again, backs them up if automatic
backups are on (after the game closed), and shows the latest. Changes you have not saved
are never thrown away for this; the companion says so instead.

### Mission project

Open **Mission project** in the sidebar to start a new authored project without a game installation, career or
catalogue. Add objects with a name and definition reference, add mission source, attach a source to an object and
choose the mission entry source. The project preserves source text and stable object/source IDs together.

The 3D view starts as a flat placement plane with object markers. Drag empty space to orbit, use the wheel to zoom,
or choose **Frame all**. Drag a marker to change X/Y while preserving its stored Z; Z is separately editable and
positive down. Coordinate, name and source drafts can be applied together and undone/redone. **Save as…** writes
a new `.ceproject` JSON file and verifies it; existing files are not replaced. **Open…** restores the placements,
source text, links and map bindings with a fresh undo history, after confirmation when current work would be discarded.

**Installed-map link** ties a placement's definition to one existing named object of an installed level, so a
project-enabled CE can apply the authored placement before the object initializes. The object's initialization can
replace its height: stored Z is not a guarantee of runtime height. **Load linked map…** asks for a game folder and
reads that level's terrain and the models its objects reference into a read-only preview: sampled terrain and static,
untextured models at their installed orientation, which drag like markers. Tree groups, animation, models chosen by
game code and models the folder lacks are not shown, and the page reports what it left out. The folder stays out of
the project file. **Reload map** reads it again and **Close map preview** releases it.

The preview finds a model only through the world's own model list. In the installed levels checked, that list is empty
while objects still carry model numbers, so an installed map shows its terrain and object markers but no models yet.

The preview binds as CE's project loader does. A placement moves the one object of the selected level with the bound
name. Base-world objects are shown where the map puts them and never move, even when one shares that name. A name only
the base world has, or that two objects of the level share, refuses the preview and keeps the project; a binding no
placement uses is ignored. Only regular files are read, each within a byte limit: a link, a named pipe or another
special file where a map file should be is refused at once.

Definition references are names, not resolved game models. This page edits no terrain, compiles or runs no source and
exports no new playable level. CE development source now reads linked projects: a 2026-11-03 controlled run and
independent review saved projects through this page's production Save as path and ran those files in default Linux
CE on level 221. One existing boat reached the authored X/Y; its own initialization set its height. A moved placement
can change later mission and AI behavior. The page was driven programmatically, not by a person operating its dialog
or dragging a marker. No released CE reads these projects, and complete mission authoring, physical-input use,
network-build behavior and native Windows acceptance remain open. The [document](Tests/CeMissionProjectTests.cs),
[file](Tests/CeMissionProjectFilesTests.cs), [page-input](Tests/CeMissionProjectPageTests.cs),
[linked-scene](Tests/CeLinkedSceneTests.cs) and [selected-file](Tests/CeLinkedSceneInputTests.cs) tests cover authored
data and programmatic controls. This command renders the page offscreen from an authored scene:

```sh
npm run capture:companion-godot -- --capture-script Development/CeMissionProjectCapture.cs --sizes 1280x900,760x800
```

The [capability record](../../CURRENT_CAPABILITIES.md#godot-companion--careers-settings-backups-music-and-lore) owns the executed evidence.

## Known limits

- Linux CE 0.1.13 launch, version reading, copied-career edits and loading, settings, running-game refusals and
  backup restoration passed the automated isolated check above. This does not establish human use, update hand-off,
  complete campaign play or every save variant.
- The selected Windows development UI workflow above passed with inspected screenshots. Ordinary release
  invocation, physical input and file dialogs remain open. The production file/settings backend also ran
  natively on Windows 11 using [NativeChecks](../OnslaughtToolkit.NativeChecks/README.md): real-career backup,
  edit, reopen, restore, Unicode publication, stale-source and sharing refusals, and refusal while
  CE runs passed. Separate CE replays loaded both the restored baseline and the edited Unicode
  career, with the loaded options container matching each selected career exactly. Earlier standalone
  launcher queries intermittently hit their five-second deadline, even with the launcher output correction.
  The selected `9ed8c56e81d3` launcher passed its production version query in the rendered development gate;
  that observation does not resolve the earlier intermittent loader wait for other builds or invocations.
- Nobody has clicked through the app by hand or listened to its music and voices.
- The model preview shows each model at its first frame; the app never plays an animation. On
  2026-10-16, playing the exported animations inside a headless Godot (a development check, not the
  app) aborted the engine with an internal error and then crashed its crash handler, so the
  development probe only counts the animations and skins Godot's importer reads, and the pose
  check runs outside Godot (`tools/gltf_pose_check.py`). Copies play in Blender.
- The handedness conversion follows the game's culling convention; no mirrored text on a model
  has been checked against it.
- Behavior after a power loss during a write is not proven (see below).
- The Onslaught CE running check has been exercised against actual CE processes on Linux and
  Windows. Native Windows backend checks required the exact running-game refusal and verified
  unchanged careers, settings and backup directories. CE's folder locations come from the port's
  source and packaging; only `BEA_USER_DIR` has been seen in use.
- Which player each binding slot serves (Slot 1 or Slot 2) has not been checked in the game, and
  key classes no game-written row confirms (for example top-row digits, punctuation and the
  right-hand Shift and Control) are stored by the same convention but marked as not yet seen.
- A career or copy chosen through a symbolic link in its path is refused rather than resolved.
- Two Windows folder rules are untested on Windows. Backups default to
  `%LOCALAPPDATA%\Onslaught Companion\Battle Engine Aquila Backups` because a OneDrive Documents
  folder can hold online-only placeholders, which are reparse points the backup refuses (and with it
  every write); a backup folder chosen inside OneDrive would still be refused. For a game in a Program
  Files folder, Windows may keep what the game saves in `%LOCALAPPDATA%\VirtualStore\...\savegames`;
  Home names careers found there, but the companion does not read, back up or write them.

## How files stay safe

Home describes three safeguards for your original game (its Steam or retail install); their limits are below:

- **Nothing in your game changes without a backup first.** Only a career in `savegames/`
  or `defaultoptions.bea` is ever written. First, every career and settings file the companion
  can read (a 10,004-byte career or settings file) is copied to a new backup set outside the
  game folder, each copy read back and verified and listed with its SHA-256 in a manifest; any
  other file there is left untouched, and the backup says how many were skipped. The new backup
  directory, its recovery copies and its manifest remain held through the game-file operation.
  Linux creates and publishes them relative to protected directory handles; Windows reuses its
  ancestor and file sharing locks. Directory or recovery-file changes refuse a write before the
  swap; a change detected afterwards reports that the career may have changed and that the backup
  needs inspection. These race controls ran on Linux through both writer paths; this new binding
  has not run on Windows. A file being
  replaced must be one of the backed-up files and still match its fresh backup, and a career
  or settings file you opened must still match what you opened: if the game saved it since,
  nothing is written. The new file is staged, verified, swapped in
  and reopened. On Linux the swap is `renameat2` with `RENAME_EXCHANGE`; if the file it
  displaced is not the one backed up, it is swapped back. A drive without that exchange
  cannot have the displaced file checked, so there a replacement is refused before anything
  changes; new careers are still added with a no-clobber link. If a step after the new file is
  in place fails (saving to disk, checking the saved file or removing temporary files), the
  companion says the file may have changed and leaves it as it is, with the backup named; it never reports that as
  nothing written, and never deletes or retries it.
- **Check whether the game is running.** The companion refuses a write when it detects the original
  game or Onslaught CE (CE reads the same install's careers). It checks before the backup and again just before the
  new file is swapped in; these checks do not prevent a new process from starting between a check and a write.
  Close both games and do not start either until saving finishes. On Linux a process counts as
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
  native Windows checks on 2026-10-24 also detected the selected package's actual `bea.exe` and
  refused both career and CE-settings writes with the running-game reason, without changing files
  or creating backups ([NativeChecks](../OnslaughtToolkit.NativeChecks/README.md)). On 2026-09-26, with the Steam
  game running under Proton, the check found exactly the game's own process (`BEA.exe`, argv[0]
  `S:\steamapps\common\Battle Engine Aquila\BEA.exe`) and not Steam's launcher shim, the Proton script or the runtime wrapper;
  `python tools/companion_godot.py test --script Development/RunningCheck.cs` prints what it sees.
- **Career backup sets can be put back from Backups.** Putting a file back is itself a
  write into the game, so it backs up the current files first. The file is put back only if
  its bytes still match the SHA-256 the backup's manifest recorded. A backup made from another
  game folder (an install that moved, or another copy of the game) is put back only after a
  confirmation that names both games and folders. New backup manifests record which game was selected;
  older manifests without that information are identified as unknown. Automatic backups compare against
  the newest backup of the same game and folder.

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
logic runs in the tests on Linux and in the native Windows backend workflow described above.
The Windows workflow exercised actual replacement, verified backup, reopen and restore; it does
not establish every failure path or behavior after power loss.

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
retired WinUI application's AppCore library used, moved here (see [PROVENANCE.md](PROVENANCE.md))
and cut down on 2026-10-22, when AppCore was removed, to what the companion calls: link and
Windows path-form refusals, ancestor-locked folders, no-follow opens, the game-folder output
refusal and the new-file-only guarded publication. On Linux it opens sources descriptor-relative
without following links, compares physical identity and link count, stages into an unnamed
file, flushes it, and publishes with a no-clobber link. [GameWrites](Files/GameWrites.cs)
builds backups and game-folder writes on the same primitives, with the portable path
described above for other systems. The Windows copy path locks ancestors and verifies
identity, but releases its staging quarantine and closes the handle before a path-based
move, then verifies the published identity. Native Windows checks exercised protected reads,
Unicode publication/discovery and stale-source refusal. An adversarial race at every publication
boundary remains untested; neither these backend checks nor a cross-export validate the Windows UI.

The level data layer adds one writer of folders: [ModStager](Levels/ModStager.cs) writes an Onslaught CE mod folder
(`mod.json` and `data/worlds/worldNNN.wrd`) through the same guarded publication, one new file at a time, the world files
first and `mod.json` last. It refuses a folder inside a game folder or one of the protected folders, a link anywhere on the
way, and a folder that already holds anything; when it fails, it removes what it made. It detects replacement; it does not
lock, as the Toolkit's Python stager does not: a directory swapped for a link, or moved into a game folder, by another
process after its early checks and before it creates the folders is not caught by those checks, and a folder moved by another
process during the run is not guaranteed to stay outside the game folder (the limit every writer through the publication has).

## Exact toolchain and rollback

[toolchain.json](toolchain.json) records the measured engine, SDK and template hashes and
the shared lock revision; `tools/companion_godot.py` verifies the installation and refuses
mismatches. `global.json` pins .NET SDK 10.0.402 (latest patch of that band; the runner accepts only
10.0.402); the Godot SDK is `4.8.0-beta.1`, the target `net10.0` and the runtime 10.0.13, the
one that SDK ships. The runtime packs Godot's export bundles
(`microsoft.netcore.app.runtime.linux-x64` and `win-x64` 10.0.13) are pinned by nuget.org's
SHA-512 and their SHA-256, and an export whose restored pack differs is refused. Export presets target Linux x86_64 and Windows x86_64, and Godot's normal
.NET export bundles the runtime, so packages need no installed .NET. The Windows package
carries the companion's name and its emblem as the program icon, drawn by
[Emblem](Ui/Emblem.cs) at export time; the project itself stores no icon file. Adopt a later engine
only in an isolated worktree with updated pins, matching templates and a full rerun of the
suite, exports and captures; roll back with the preceding commit and its preserved engine.

See [PROVENANCE.md](PROVENANCE.md) for licensing and data boundaries.
