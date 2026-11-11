# Current Capabilities

Status: active — what is demonstrated today, and what is not
Last updated: 2026-11-11 (the earlier rebuild's dated narrative removed; 2026-11-06: standalone Companion is current implementation; unified CE migration is required, not delivered)
Summary: the demonstrated capability of each part of the project with the measured gap stated beside it. Every
figure here is the value at the commit that wrote it; re-measure before relying on one. Superseded narratives remain
in Git and the private historical maintainer archive; they are not current operating instructions.

The current standalone Onslaught Companion ([built from source](README.MD#build-and-run); no packaged release yet) lets players choose the original game or Onslaught CE. It supports finding
CE's launcher, protected career writes, two launcher settings and the steps for updating CE (the running companion
contacts nothing; its build setup downloads pinned tools, see [README](README.MD#build-and-run); CE checks its own signed feed and installs an update only when the player chooses Update).
See its [README](companion/OnslaughtToolkit.Godot/README.md) for the contract and platform limits.
The map/mission authoring capabilities described here currently run in Companion. They are reusable work toward the
required native CE experience, not completed in-game editors. Continuous 3D RTS Commander and an explorable museum
through CE's menus also remain incomplete; the map/preview controls and separate gallery/construction test retain
their narrower evidence. [GOAL.md](GOAL.md) and [PROGRAM.md](PROGRAM.md#order-after-0113) own the new requirements
and the hold on 0.2 until its agreed player workflows are internally complete and tested.
The latest product decision also moves Companion's lore, content exploration, career/save editing, backups,
settings and installation-management workflows into CE, eventually retiring the separate app. The present tools
and evidence remain until that replacement is verified. This is a migration requirement; no completed in-process
career editor or unified frontend is claimed here. Integrated career editing still needs verified recovery and
coordination with CE's loaded profile state, not just removal of the current running-game refusal.
The byte-matching decompilation is the reverse-engineering authority. Its private function check matches every mapped
game function with a guarded one-byte correction to a compiled object; without that correction, one function remains
unmatched. Its public export, [onslaught-decomp](https://github.com/dlprentice/onslaught-decomp), records its own
coverage and the third-party sample files it leaves out. Function matches do not by themselves establish complete
behavioural equivalence or a byte-identical linked executable. Its native port is published separately as
[Onslaught CE](https://github.com/dlprentice/onslaught-ce), and this document does not measure it. The Godot rebuild,
a scoped proof of concept (level 100, startup to exit), is developed
in [onslaught-godot](https://github.com/dlprentice/onslaught-godot), which records its measured parity; `rebuild/` here is a frozen copy. Executable patching and copied-install
safe launch are retired and not planned; their code (the AppCore library and the `patches/` catalog) was removed on
2026-10-22, and Git keeps it.

## Retail behaviour findings — save, settings and startup

The [current compatibility recheck](reverse-engineering/binary-analysis/save-options-static-review-2026-05-26.md)
executes selected unchanged retail bodies with preserved inputs and explicit
OS/heap/device boundaries. It establishes startup read versus write filenames,
campaign reset after settings load, menu-load forwarding to the next startup,
binding/preset serialization effects and the active language field written by the serializer.

Later extensions of the same method cover the language files and text lookups, the audio volume, reset and language-bank
controls, sample decoding and bank loading, audio-device initialisation and the outer sound-manager setup. Each is
recorded, with its contract and its limits, in that note and in the dated entries of
[`VALIDATION-HISTORY.md`](VALIDATION-HISTORY.md#original-load-save-and-reload-controls--september-20). They are
controlled-memory observations with supplied file, heap, device and COM boundaries. They do not establish full startup,
audible playback, localized rendering, durable save round trips, an installed-game or Proton failure, or reconstruction
acceptance. The figures that this page once quoted for them are in Git (`git show e64df96d9:CURRENT_CAPABILITIES.md`).

## Godot companion — careers, settings, backups, music and lore

The GPL-3.0-only [companion](companion/OnslaughtToolkit.Godot/README.md) is a C# application
built entirely in code on **Godot 4.8.beta1.mono.official.4d10419ca** and .NET 10 (`net10.0`,
runtime 10.0.13, SDK 10.0.402). Its one scene only
attaches the root script; the build refuses GDScript, saved resources and multi-node
scenes. David approved its feature set and Flight-deck look on 2026-09-25; on 2026-09-26
he asked for it to be built around players: easy to find your way, easy on the eyes, and
safe for their game and saves.

**Which game it works with:** Home selects the original game or Onslaught CE. The original game uses its
installation's careers and `defaultoptions.bea`. With CE selected, the companion lists its user-folder careers
and original-install files for browsing and backups, preferring the user file for a duplicate name regardless of case.
Original-install careers are labeled read-only; edits can become a new named
CE copy, and CE writes go to its user folder. The companion offers Play through the selected CE launcher, shows the steps
for updating CE on Home (it contacts nothing and displays no release version), and edits only the launcher's
`update_check` and `record_sessions` switches. Original data also supplies music, voices and art. CE settings backups are separate verified files; the career Backups page does
not restore `ce.ini`.
CE 0.1.4 merges both lists on Linux and Windows; the older Linux listing defect described in earlier records
was corrected in that CE release. See the linked current source in the companion README.
CE's original data folder is admitted by its two data-file hashes, using its environment/configuration/Steam
search order; the companion's separate pictures-and-music choice does not override that.

**CE evidence and gaps:** [CE career tests](companion/OnslaughtToolkit.Godot/Tests/CeTargetTests.cs) and
[original-career browsing tests](companion/OnslaughtToolkit.Godot/Tests/CeOverlayTests.cs) use owned copies
of the tracked real-save fixture in isolated folders. [Launcher and settings tests](companion/OnslaughtToolkit.Godot/Tests/CeSettingsTests.cs)
check the launch request and capture a tiny fixture script's version reply. In addition, the
[November 3 Linux acceptance](VALIDATION-HISTORY.md#companion-with-real-onslaught-ce-0113--november-3) read CE 0.1.13's version,
started its actual launcher, edited and backed up a copy of a game-created career, saved the two supported CE settings,
and loaded the edited Unicode-named career through CE's own menu. The loaded options file equals the edited career
byte for byte; the selected level-selection frame was inspected. The check also refused career/settings writes while
the game ran, refused stale writes, and restored the original career from its verified backup. It is an automated
Linux workflow driven through programmatic production-page actions, not human UI input, an update hand-off,
complete campaign play or native Windows acceptance. The [October 24 CE 0.1.4 run](VALIDATION-HISTORY.md#companion-with-real-onslaught-ce--october-24)
remains a separate dated record.

The initial November 4 Linux checkpoint check used the same pinned production pages with the unreleased CE 0.1.99 package.
Discovery read its actual launcher version; copied-career backup/edit/restore and the two supported settings controls
passed. Fresh Home/version, settings and restored-backup images, plus authored 3D project/map-link/source views,
were inspected. Both capture processes exited normally and the pinned source/runtime inputs read back unchanged.
The retained checkpoint acceptance receipt has SHA-256
`2f267eb8df39c78028729fddeaf468307c1f74d56464229dfabb3f7fc25ff367`.
This adds bounded automated workflow and image acceptance, not human input, audible output, an update hand-off or
native Windows acceptance. This first local snapshot remains preserved; neither it nor the separate 0.1.99 refresh
is a public release. The earlier CE 0.1.13 career-load result remains the dated acceptance described above.

The refreshed November 4 Companion stage uses the accepted installed-model editor source described below and the
newer unreleased CE 0.1.99 package. Fresh scripted production-page checks passed actual launcher-version discovery,
copied-career backup/edit/restore, settings writes and refusal to overwrite a changed settings snapshot. The process
exited normally; package and preserved baseline read back unchanged. Home/version, settings, restored-career and
static installed-model images were inspected. The retained combined receipt has SHA-256
`60ce7544b472c5380e58a3c813abecf4bf179aba61e510b0595943642c052009`.
This is bounded Linux workflow/image acceptance, with no new human-input, audio, game-load, update hand-off or
native Windows claim. The checkpoint status and remaining work are tracked in [PROGRAM.md](PROGRAM.md#order-after-0113).
David's subsequent November 4 manual CE playtest did not include Companion. Human use of its workflow and 3D editor
therefore remains unverified; the CE and museum feedback is recorded in [PROGRAM.md](PROGRAM.md#onslaught-ce-player-experience-and-online-play).

[Data-folder tests](companion/OnslaughtToolkit.Godot/Tests/CeGameDataTests.cs) exercise the two-file validation and
folder selection using owned tiny inputs; these are not a game-content or launch acceptance test.
[Update tests](companion/OnslaughtToolkit.Godot/Tests/CeUpdateFeedTests.cs) check signature verification and refused
responses. [Native Windows checks](companion/OnslaughtToolkit.NativeChecks/README.md) now exercise production
process detection, protected career/settings writes and actual-game running refusals. CE also loads the edited
Unicode career and writes exactly its bytes as options. A separate [native Windows development UI workflow](VALIDATION-HISTORY.md#companion-native-windows-development-ui--october-25)
exercised selected production-page actions and its screenshots were inspected; ordinary release invocation,
physical input, file dialogs, hardware rendering and broader UI acceptance remain open. Version
queries still intermittently time out while Windows opens SDL3.dll during loader startup. Separate native
launcher checks reproduced CE 0.1.4 sending redirected output to an attached console; Onslaught CE 0.1.5
publishes that correction, which does not resolve the distinct startup wait. See the
[companion README](companion/OnslaughtToolkit.Godot/README.md#which-game-it-works-with).

Its sidebar:

- **Home**, with the original game selected, finds the game through Steam (native, Flatpak or Snap on Linux; the registry
  on Windows) or a chosen folder, checks `BEA.exe` against the Steam release by SHA-256,
  shows the banner art from the player's own manual, offers Play through Steam, lists the
  careers with their progress and opens the most recent one read-only.
- **Your career**: a Summary with a map of the career's path through the campaign (each
  mission's rank, the routes taken and those the game recorded as not taken, read from the
  links the career stores), then missions, Goodies and kills; the 230 Goodies the game's
  gallery shows, row by row as on its wall, with titles from the player's text, unlock
  rules and how each rule is known (071–073 are stored but never shown); Edit career for
  kill counts and Goodies; Cheats for a byte-identical copy named to switch on the three
  cheats seen working in the Steam game.
- **Your game**: for the original game, Game settings edits the defaults read at start, or the copy each career
  stores, which the game does not apply when that career loads: sound, invert, vibration,
  controller layout, mouse sensitivity, screen shape and keys captured from a key press, in
  the two binding slots each action has. CE offers its two launcher settings described above.
  Backups offers automatic backups when the companion opens and after the game closes, only
  when something changed; Back up now; and every set, with Put back for each file.
- **Extras**: Music & voices plays the soundtrack and voice lines from the install with
  the game's transcripts (Bink cutscenes are listed only); Lore reads the repository's lore
  offline with search, the map of Allium from the player's manual and the manual itself;
  Art & sound lists the install's models, textures and bank sound effects, previews them and
  saves copies (models as glTF, textures as PNG, sounds as WAV). The Level editor shows placed objects and a map,
  lets the player move objects (by typing, dragging on the map or the arrow keys, with undo and a list of only the moved ones), copy a unit (appended after every row so existing row, path and target indices do not shift; the copy retains its script and target; only units, only as copies, undoable) and save the changed world as a new CE mod, and shows mission scripts. For a script of the
  level's own with an installed source it can also edit the source, compile it and make the open level use the result (undoable,
  with a warning when an edit adds calls to `Damage`); Save as mod then writes the world file with the replaced script, and a Play button starts Onslaught CE (Linux, CE 0.1.11 or later) at the open level
  with the changes as they are, in a temporary CE folder of its own. One offscreen run through the released 0.1.12 launcher left the scratch player's CE folder, settings, stand-in career and tape unchanged (section 17 of the mission editor design). The page is
  covered by event-driven tests and offscreen captures on Linux, and one edit of one script (a tutorial message of level 100) was staged by
  it and run in CE on Linux, offscreen and live, with the edited subtitle on screen beside control runs (the [mission editor design](roadmap/companion-mission-editor.md)'s
  section 16, which also says what that does not show); one copy of one Target Tank of level 100 was staged by it and run in CE on Linux, offscreen, through the Play button, and a second tank stood at the crosshair
  (the [level editor plan](roadmap/companion-level-editor.md)'s M5 acceptance). Two moved Target Tanks were also run in CE on level 100. Nobody has used the page or its Play button by hand; beyond those moves, the copy and the script edit, no other kind of edit has been run (nothing is added from nothing and nothing is deleted). The mod holds the world file only (the
  edited source is not kept beside it), and there has been no native Windows run. The documented CE world-mod loader is Linux-only. See the [level editor description](companion/OnslaughtToolkit.Godot/README.md#what-it-does),
  [level editor plan](roadmap/companion-level-editor.md) and [mission editor design](roadmap/companion-mission-editor.md).
  Parsed-object source offsets describe positions in the original input buffer; they do not automatically
  follow later edits. To use offsets with edited or serialized bytes, parse those bytes again or use an independently
  verified mapping. This metadata does not establish catalogue-to-model identity, a complete 3D editor, or a completed museum.
- **Mission project** creates an authored document without an installed level, career or catalogue. Its 3D view
  starts as a flat placement plane of object markers with orbit, zoom, selection, dragging and undo/redo; a drag
  changes X/Y while preserving stored Z. Objects keep stable IDs and definition-reference names. Preserved mission
  source can be edited, attached to objects and selected as the mission entry source. Save as writes a new
  `.ceproject` JSON file; Open restores placements, source, links and installed-map bindings with a fresh undo
  history. Existing project files are not replaced.
  [Document tests](companion/OnslaughtToolkit.Godot/Tests/CeMissionProjectTests.cs),
  [file tests](companion/OnslaughtToolkit.Godot/Tests/CeMissionProjectFilesTests.cs) and
  [page-input tests](companion/OnslaughtToolkit.Godot/Tests/CeMissionProjectPageTests.cs) cover those authored paths,
  invalid inputs, stale edits and delayed I/O. Focused authored checks and the composed full `npm test` passed on
  Linux on 2026-11-02 against [integrated source](https://github.com/dlprentice/Onslaught-Career-Editor/tree/f4f832c7d2b63f42b9837d96e4a3912808f770c4).
  An installed-map link binds a placement's definition to one named object of the selected level; Load linked map
  reads that level into a read-only preview of sampled terrain and static, untextured models, which drag like
  markers. Base-world objects stay where the map puts them. A name only the base world has, or that two objects of
  the level share, refuses the preview and keeps the project; a binding no placement uses is ignored. Only regular
  files are read, each within a byte limit; a link, named pipe or other special file is refused before any read.
  [Linked-scene](companion/OnslaughtToolkit.Godot/Tests/CeLinkedSceneTests.cs),
  [selected-file](companion/OnslaughtToolkit.Godot/Tests/CeLinkedSceneInputTests.cs) and
  [runtime-link](companion/OnslaughtToolkit.Godot/Tests/CeMissionRuntimeLinkTests.cs) tests cover these rules with
  authored data, and the full `npm test` passed on Linux on 2026-11-03 against the
  [source merged into main](https://github.com/dlprentice/Onslaught-Career-Editor/tree/2d0bfd308e9553d45d54e21d7aafef951eea49e3).
  Offscreen captures at two window sizes, loading through the folder dialog's selection signal and reloading with the
  Reload control, were inspected: an authored scene's models on its sampled terrain, a base-world copy left at its
  installed place and the bound model at the drop. The earlier read-only survey found no world listing models of its
  own, so that version showed installed terrain and project markers only. Development on November 4 now resolves
  unambiguous object definitions to meshes in the same resource archive. Fresh offscreen Linux captures of level 221
  were inspected: 16 static, untextured meshes supplied 35 model instances over sampled terrain, while geometry for
  27 unsupported object references was omitted and reported. Duplicate definitions and missing model-definition
  tables refuse that geometry instead
  of selecting an unrelated model. Move, Undo/Redo and Save/Open retain the project and source identities. Authored
  reader and scene checks and independent review cover those paths; textures, animation, complete-scene rendering,
  human input and native Windows remain unverified. This source was added after the initial 0.1.99 Companion stage
  and is included in the refreshed stage, whose fresh installed-model images were also inspected; the initial stage
  remains preserved.
  A separate 2026-11-03 controlled run and independent review exercised the production
  [Save as path](https://github.com/dlprentice/Onslaught-Career-Editor/blob/443b2b3d921775767a87404d9c6842fc1b275294/companion/OnslaughtToolkit.Godot/Ui/Pages/CeMissionProjectPage.cs)
  through its file-selection signal, then loaded the saved documents in a clean, default Linux CE development build.
  One existing boat on level 221 reached each authored X/Y placement at its first update. Its own initialization
  replaced stored Z; runtime height therefore remains object-dependent. A same-position control matched ordinary
  play. One moved case kept changes confined to that object through the observed window; another later caused
  mission and AI reactions, so the result does not promise that moving an object leaves the rest of a mission
  unchanged. Deliberately broken writer and coordinate-reader variants were refused by the check. The controlled
  career-write case left the protected save unchanged; it does not establish every save path. The retained independent
  review receipt has SHA-256 `9b9871ca08f689f63c2e8a1aa0c678a0ba36f13a0c7671f0027bbd68abcb6525`.
  On November 4, the initial unreleased 0.1.99 Linux package, built with networking enabled, also loaded one of those
  page-saved level-221 projects locally. Its placement log entry and gameplay image were inspected; no network session
  was active. The retained exact-package smoke receipt has SHA-256
  `e4a7f4daf13dd8e442f52a894452870880aeeb45ea4a50d2ea2614b279070e81`.
  The refreshed November 4 package also loaded the saved project locally, rendered gameplay and exited cleanly;
  the project and package read back unchanged. Its gameplay frame was inspected. The retained smoke receipt has
  SHA-256 `f03720cef8d15f9e09f7d75661beaabccd4fb08d2d87e07cfb4ea76ebe2c1370`.
  This is page-to-runtime evidence for an existing-object placement in CE development source. No publicly released CE
  reads these projects. No person operated the Save as dialog or 3D drag for these checks, and they do not establish
  multiplayer project loading/replication, native Windows, mission completion or additional object kinds. The Windows
  branch of the regular-file open is compiled but has never run. The page edits no terrain, compiles or runs no source
  and exports no new playable level. The [workflow and limits](companion/OnslaughtToolkit.Godot/README.md#mission-project) distinguish this
  bounded runtime path from source compilation and complete mission authoring. Human use and native Windows
  acceptance remain open.
- **Advanced**, folded away: Career bytes (the open career's stored values, or the bytes that
  differ from another career).

The authored Mission project page uses the integrated shared viewport foundation. Older installed-level development
candidates remain separate and unreleased. The
[3D drag candidate](https://github.com/dlprentice/Onslaught-Career-Editor/tree/8aacbb23577ce57397a5319282bf33cd5f742494)
binds a drag to the current edit session and object; authored page-input and offscreen capture assertions cover
motion without changing the world or undo history, one undoable move on release, preserved height and an unchanged camera. The
[spherical-trigger radius backend](https://github.com/dlprentice/Onslaught-Career-Editor/tree/6d2c3e4f949f3f4885ec7cb74e5654dfed4d6a33)
adds undo/redo, validation and change summaries, with a passing authored-data fixture; that branch has no inspector
control. A separate inspector component candidate remains unwired.
The [level editor owner](roadmap/companion-level-editor.md#unreleased-editor-candidates) records their scope.
Those older candidate checks do not establish their full Companion-suite acceptance, human use, new-edit acceptance
in CE or native Windows acceptance. In the installed-level editor, world/terrain project Save/Open and script-draft
restoration remain unwired. Derived terrain/snapshot save and play remain disabled, and the unsaved terrain draft
remains a preview rather than published content. The authored `.ceproject` document does not add those installed-level
snapshot or CE export capabilities.

A career change reaches the game through a dialog that offers a new career, replacement where allowed,
or a copy elsewhere. Before a career write, the readable careers for the selected game are copied to a
verified backup set, along with `defaultoptions.bea` for the original game. CE settings use their separate
verified backups described above. Nothing is written while it finds
`BEA.exe` or Onslaught CE running, checked before the backup and again just before the swap (on
Linux, the `BEA.exe` rule was seen on 2026-09-26 to find the Steam game's own process under
Proton and nothing else; the CE rule was seen on 2026-10-22 to find a running Onslaught CE 0.1
on Linux, recorded in the maintainer's ignored local evidence,
and the native Windows backend checks on 2026-10-24 also refused writes while the selected CE game
process was running; general Windows Godot UI acceptance remains pending); a
file the game saved since it was opened is not replaced; the new file is swapped in (on Linux
an atomic exchange that swaps back if the displaced file is not the one backed up; elsewhere
`File.Replace` with the same comparison) and verified. A file is put back from Backups only if it
still matches the SHA-256 its backup recorded; a backup from another game folder goes back only
after a confirmation naming both games and folders; new manifests record the game, and older manifests that lack
that information are identified as unknown. Switching careers or closing with unsaved changes asks first. When the
game closes, or the player comes back to the companion, it reads what the game saved and shows the latest, keeping any
unsaved changes; while changes are unsaved, a bar under the page keeps Save in reach. Every label style outside the banner measures at least 4.5:1 against the
surfaces it sits on.

The in-process [ProtectedSaveFiles](companion/OnslaughtToolkit.Godot/Files/ProtectedSaveFiles.cs)
adapter uses the companion's own `SaveLabFileTransaction` and `FileMutationSafety` (moved from the retired
AppCore library and since cut down to what the companion uses; see the companion's
[PROVENANCE](companion/OnslaughtToolkit.Godot/PROVENANCE.md)). Linux publication retains
no-follow handles, physical identities, unnamed staging and no-clobber linking.
Malformed or changed inputs and conflicting outputs are refused; uncertain publication
never becomes a success receipt or an automatic deletion. There is no helper process or
unchecked write fallback, and normal Godot .NET exports bundle their runtime.

A replacement in the game is refused on a drive without an atomic exchange (renameat2 RENAME_EXCHANGE); a failure
after a file is in place is reported as a possible change and the file is left as it is. Both are checked by fault
injection in the tests, not on a real drive lacking the exchange. Backups cover the careers and settings file the
companion can read; other files are skipped and counted.

**Evidence:** the lane's commit messages from 2026-09-26 record each check: `npm test`
(one C# contract suite inside headless Godot, including the portable write path run on
Linux, and the development runner's own cases), renders of every screen at 1280×800 and 1920×1080
reviewed first-hand, the problems that review found fixed, covered by tests, re-rendered and
reviewed again, and Linux and Windows packages exported, with the Linux package started and
quit cleanly under an isolated home. The earlier approved-workflow receipts are
in [their validation section](VALIDATION-HISTORY.md#companion-approved-workflows--september-26) and
the migration's in [its section](VALIDATION-HISTORY.md#companion-c-migration--september-25).
Art & sound and the Goodies page's "What it shows" are covered by the contract suite on
synthetic models, textures, a sound bank and Goodie archives; no dated receipt for them is
recorded here. **Ordinary Windows release UI acceptance, a human click-through and listening to the audio remain pending.**
The selected Windows development UI workflow and native backend and CE career-load checks described above are narrower executed evidence.
The companion does not patch
`BEA.exe` and that is not planned; mission, rank and link edits are not offered; no legacy
feature parity or retail gameplay acceptance is implied.

The [content and model/transform catalogue tools](tools/README.md) cover the families their current readers support.
On November 4, the catalogue gained individual framed imposter identities, source hashes and coordinates, bounded
labels and view rectangles, and unambiguous links to meshes and texture atlases in the same resource archive.
A read-only installed-data run produced 1,999 identities; authored checks and independent review cover truncation,
invalid views, ambiguity and the existing metadata consumers. Unread fields remain labelled unread. These are
metadata relationships, not new decoded-byte coverage, rendered-image acceptance or a tested HD conversion.
The [content inventory](tools/README.md#content-inventory) puts every byte of one selected PC install in a class
(decoded by a reader, framed by a record but unread, or unknown) and lists every model, texture, image, animation,
sound, film and text asset with what names it; on the read-only retail view its gate checked that account against the
folder by independent paths. Its headline gives the decoded share of the content twice, with FFmpeg reading the audio
packets, video frames and JPEG scans and without it, because those payloads count as decoded only on that decoder's
word; the Vorbis setup header (its codebooks, floors, residues, mappings and modes) and the JPEG tables are read by this
repository's own readers and count either way. Beside
the account it writes a per-asset metadata file (identity, format, size, mip levels, alpha, channels, sample rate,
duration and what names each texture, image, model, animation, sound and film) as the input list for an offline batch
such as an upscale. The gate takes each row's form, place and readability from the file and the run's own items, not from
the row (a row relabelled to another form, or called unparsed, fails), reads every field of that file again from the
asset's own bytes (for the mesh chains and terrain mixer mips that no reader places, from their details) and checks every
row the run writes against its item, its catalogue record and its schema; what the run copies from the catalogue's
relationships is not recomputed there. Nobody has fed the file to a batch yet. Its coverage lists what stays framed: the font records, part of each imposter
record, the HUD dial's later frames, the career block, the language pool strings no entry reaches, the mission scripts
whose compile reproduces no shipped copy, the words a particle set's reader skips, the document a manual's Word file
compresses and the executables' code and data; a few bytes after that document stay unknown. Sources no loader reads
(mission scripts and text, symbol tables, the manual's pages) count as decoded only when their own grammar holds to
the end. "Used" means a record, physics value, page link or loader rule names the asset; it is not a runtime
observation. A second install, Windows and an HD conversion are not covered; the
[programme](PROGRAM.md#content-catalogue) owns the remaining catalogue work.

## Retired WinUI toolkit

The Windows-only WinUI 3 shell, its UI tests, the maintainer CLI and the portable ZIP
packaging were removed on 2026-10-15; the Godot companion replaced them. Their source,
demonstrated features and receipts remain in Git history.

The WinUI app's core library, AppCore (executable patch plans, guarded application, copied-install
"safe launch" profiles and their save and options services), and the `patches/` catalog it read
were removed on 2026-10-22; Git keeps them. Executable patching and safe launch are not planned
for the companion: Onslaught CE replaces them; it reads the install and keeps its own files in its own folder. AppCore's save-layout
and file-safety test facts were carried into the companion's own tests first. On Windows, Home
lists every `.bes` left in the old toolkit's safe copies
(`%APPDATA%\OnslaughtCareerEditor\GameProfiles\*`, in each copy's `savegames`, `saves` and `Save`
folders and its top folder, as AppCore's rescue searched) and saves each career-sized one as a
protected copy elsewhere; a file of another size is listed as one that cannot be copied. That listing
and copy are tested on a scratch folder on Linux (the button and save picker driven by the interface
test) and have not run on Windows; nobody has looked at the panel on screen.

## Reconstruction

**Current: the parity-core proof of concept.** The rebuild is developed in
[onslaught-godot](https://github.com/dlprentice/onslaught-godot), not in this repository's frozen `rebuild/` copy.
`OnslaughtRebuild.Parity` owns the simulation and `OnslaughtRebuild.Host` the presentation. The live
[parity record](https://github.com/dlprentice/onslaught-godot/blob/main/rebuild/PARITY.md) owns the measured bounds;
its numerical model and portability are not claimed exact beyond those checks. Test success does not establish
audible audio, visual equality, physical input, whole-game parity or a completed tutorial.

**The earlier fixed-point rebuild.** The frozen [`rebuild/`](rebuild/README.md) copy still holds the earlier fixed-point
rebuild (`OnslaughtRebuild.Core`, `Client`, `Godot` and `Headless`, with their tests) as a reference. Its dated account of what
it demonstrated, as it stood at the end of September 2026, was removed from this page on 2026-11-11; it describes no
current capability. Git keeps it: `git show e64df96d9:CURRENT_CAPABILITIES.md`.

The current source tree and release packages do not include retail game assets
or their conversions. The source tree tracks no screenshots: the screenshot register in
[`reverse-engineering/project-meta/attribution.md`](reverse-engineering/project-meta/attribution.md)
is empty (its two former entries left with the retired WinUI shell on 2026-10-15), and the screenshot allowance is
stated in [`AGENTS.md`](AGENTS.md). Pictures of the game running are not files
copied out of it.
In onslaught-godot (the live rebuild), the materializer takes the exact currently consumed slice
from a user-provided supported retail installation into ignored local paths.
The remaining asset gap is technical integration and format fidelity.
Read that repository's [`rebuild/PROVENANCE.md`](https://github.com/dlprentice/onslaught-godot/blob/main/rebuild/PROVENANCE.md) before changing this lane.

## Reverse engineering

The [content catalogue coverage report](tools/README.md#catalogue-source-file-coverage) distinguishes represented logical paths, relationship targets and unrecorded parse status. Its checks use authored fixtures; those counts do not establish a complete asset inventory, unique file contents or mappings to placeable objects.

The byte-matching decompilation is the reverse-engineering authority. The [overview above](#current-capabilities)
states the compiled-object concession and the limits of function matching. Its public export,
[onslaught-decomp](https://github.com/dlprentice/onslaught-decomp), owns the current score, matched list, sample-file
exclusions and remaining divergences.
Findings are written as prose and specs in [onslaught-preservation](https://github.com/dlprentice/onslaught-preservation),
citing functions rather than quoting code; [`reverse-engineering/`](reverse-engineering/RE-INDEX.md) here is a frozen copy.

The Ghidra-era campaign (generations, contract grades, promotion cohorts, the tracked Ghidra checkpoint and
`developer_state.json`) ended with that work. Its records moved on 2026-10-15 to the private historical maintainer archive, byte-exact at their old paths; its figures are history, not current capability.

## Evidence boundary

[`reverse-engineering/RE-INDEX.md`](reverse-engineering/RE-INDEX.md) is the front door to the frozen copy of the game
documentation, which is maintained in [onslaught-preservation](https://github.com/dlprentice/onslaught-preservation).
The decompilation and the retail executable own static released-binary facts; controlled copied-runtime
observations own measured behaviour. Stuart's GPL source owns architecture and implementation evidence; retail
static and runtime differences decide where the Steam release diverged.

## Distribution

The companion has no published release yet; `npm run export:companion-godot -- --platform both` builds Linux and
Windows packages that bundle their .NET runtime. The retired WinUI app's last release, the unsigned portable
Windows ZIP `v1.0.11` (tag `winui-v1.0.11`), is still on the Releases page and is no longer maintained; its
executable patching and safe launch are not in the current companion and are replaced by Onslaught CE. No package includes the retail
executable, the original assets, saves, a Ghidra database or the rebuild client. Repository licenses do not cover
retail game data; future releases keep that user-supplied boundary.

Use `npm run` for the current command surface: `npm test` checks the companion.
