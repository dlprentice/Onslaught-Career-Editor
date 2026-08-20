# Onslaught Toolkit changelog

Status: active — app-release record only
Last updated: 2026-08-18
Evidence: MEASURED — each entry names the released ZIP/tag it describes and
was written from the release probe report and release notes of that tag.
Summary: per-version record of shipped WinUI releases, for downloaders who
arrive from the Releases page. RE generations are NOT recorded here — they
live in `developer_state.json` and the campaign ledgers.

## Unreleased

- Cheats now says which offered cheats the save you start from already switches on.
  Those live in the file name, so a new name needs them ticked if you want to keep them.
  The source file is still only copied.
- Your safe copies now says which listed catalog patches this copy already has,
  by reading that copy's `BEA.exe`. Original, already-patched, and unmatched
  bytes are named without a dump or a path. The installed game is not opened.
- Cheats live trainer can hold life, energy, and shields together. One switch
  turns on the three existing holds at the values in the boxes. It is still a
  top-up, not a freeze: walker mode still needs energy held for shields to last,
  jet mode still zeros shields, and one hit big enough to kill still will.
- Save Lab focused Goodie now shows what the opened save already has for that
  ID, so a write is replacing a named state rather than a blind dword.
- Settings and Home now say whether the chosen `BEA.exe` is the known Steam
  retail file. A changed file is not called an original; a copy made from it
  is disclosed as carrying those changes. If the file cannot be read, the app
  says so instead of pretending it was changed. Windowed & Mods uses the same
  distinction: a locked executable is not described as already patched. Auto-Detect
  failure is shown on Settings, not only in the status bar. Save Lab names whether
  the opened career save sits in the installed game, a playable copy, or a folder
  the player chose. Game Options does the same for the opened defaultoptions.bea.
  Cheats names the same three places for the career it is about to copy.
  A Lore search with no hits now says to try another word or clear the search,
  instead of calling the empty tree filtered results. Cheats will not offer to
  write into a folder inside the installed game. Media load and playback
  failures stay on the page without dumping the raw exception. The dedicated
  video player says it could not start, without the exception. Dedicated video
  windows now use the public product name, Onslaught Toolkit. Media names the
  source folder and the selected file by their last segment, not the full path.
  A Media search with no hits now says to try another word or clear the search. Asset
  Library names the catalog and export by their last segments, not the full path. The
  footer tooltip names the game folder the same way. Settings names the
  settings file and the chosen install folder by their last segments, not the full path. Windowed & Mods
  Last operation and the safe-copy list do the same: a failure names the action
  and that nothing was changed, without the exception. Home setup failures
  keep the same sentence and drop the exception. Save Lab comparison/analysis
  and Game Options browse/patch failures do the same. Save Lab will not keep a
  rescued career in a folder inside the installed game, and it names that folder
  without dumping the full path. If that folder cannot be created, it says so
  without the path or the exception. Save Lab and Game Options also keep the write
  button off when the chosen output file sits inside the installed game. Game
  Options overwrite confirmation names the file, not the full path, and leaves
  the existing file alone if the player cancels. Save Lab overwrite
  confirmation names the file, not the folder. Windowed & Mods create-copy
  and launch confirmations name the folder, not the full path. A Cheats write
  that fails no longer dumps the exception, and an unreadable career path is
  named the same way. Game Options patch refusals name the missing or invalid
  file without the full path. Save Editor patch refusals do the same for a
  missing career save. Save Editor advanced read refusals name the action
  without the exception. A locked Save Editor write names the action
  without the exception. A successful Save Editor write names the file,
  not the path. An Asset Library search with no hits now says to try
  another word or clear the search. Settings names a folder that could not
  be kept and puts the previous folder back, instead of leaving the new path
  looking saved. A look or media choice that cannot be kept is named the
  same way and the previous value is put back. Home uses that same folder
  sentence when a chosen install cannot be kept, including after auto-detect.
  A failed playable-copy setup stays on the same "nothing was changed"
  note instead of the prepare message. Save Lab overwrite cancel
  says the file was left as it is. Putting a career into a safe copy, or
  bringing one out, asks the same overwrite question. A missing or unreadable
  analysis or compare file uses that same sentence instead of the exception, and
  a failed compare is not called identical. A failed stop of a
  copied game names the action and that nothing was changed, without the
  exception. A failed backup of the installed game does the same, and an
  unreadable install path is named without the exception. The
  installed-game status line names the folder, not the path. A restored
  music backup names the track and that the install was not changed,
  without the internal restore sentence. Staging a copied track names the
  two files the same way, not the Music folder path. A prepared copy's
  music-swap note names the backup file the same way. An unusable patch
  target is named without the exception. A live-trainer attach
  refusal names why the copy was not opened, without the Win32
  dump or a path. A live-trainer write that cannot open the copy
  names that refusal the same way, without the Win32 dump. The launch
  plan names BEA.exe, not the copy folder path. Putting a career into a
  safe copy names a failed write without the writer sentence. A Cheats
  write names the new file, not a path, if the writer sentence is not
  already public-safe. A failed apply or restore of a copied game no
  longer dumps the exception. A live-trainer read or hold stop names the
  status, not the internal read sentence. Installed-game patch and restore
  questions name the folder, not the path. A Save Analyzer report that
  cannot decode keybinds names that, without the exception. A Lore document
  tooltip names the file, not the lore-book folder. A failed career rescue
  with a path or Win32 dump uses the shared keep-failed sentence. A missing
  patch or profile catalog no longer dumps the exception. Save Lab names
  the output file, not a path, when the destination is not a career save.
  Game Options does the same for an options file that is not .bea.
  A failed Save Editor write that still looks like a dump uses that same
  kind of sentence. After that write, the journey names Put it in my
  safe copy instead of telling the player to copy by hand. An empty Lore
  library says to refresh, instead of describing the emptiness. A missing
  Windowed & Mods quick-pick row names the refusal, not the catalog key.
  A Save Editor kill-count read that fails names the action, not the
  analyzer sentence. A missing Save Editor career save names that the
  file could not be found, not a path. A patch-target filesystem-safety
  refusal uses the unusable-target sentence, without the exception. A
  loaded patch or profile catalog is named without the file path. Home
  names a missing folder, an empty save list, or a failed save count as a
  next step, not a dash. The game line on that card uses the same folder
  sentence. An incomplete install on that card names BEA.exe and data,
  not just "the full install." Choosing an incomplete folder on Home uses
  that same sentence. Home setup uses it when the folder is not set, not
  "the full Battle Engine Aquila folder." The footer tooltip names BEA.exe
  and data the same way. The Review setup tooltip uses that sentence
  too. An empty safe-copy list says to create one above, not that there
  are none yet. An empty Save Analyzer tree uses the same choose-a-file
  sentence, not "No analysis yet." Settings incomplete-folder lines
  name BEA.exe and data, not "the full install." An empty Save Editor
  patch summary says to select a change first, not that none are
  selected yet. An empty Game Options patch summary uses that same
  sentence. A kill-count summary with no save loaded names that,
  not "loaded yet." A failed Game Options write that still looks
  like a dump uses the shared nothing-was-changed sentence. A failed
  focused Goodie write that still looks like a dump uses that same
  sentence. Save Editor refusals that used to say paths now name the
  files. Save Lab names a missing analysis file, not a path. An inline
  video that fails mid-play uses the same could-not-be-played sentence
  as the other Media failures. An audio track that cannot play uses that
  same kind of sentence. Game Options refusals that used to say
  paths now name the files. A focused Goodie patcher refusal does the
  same. A Media library with no tracks or cutscenes says to check the
  game folder, instead of describing the emptiness. Windowed & Mods
  apply and restore name BEA.exe and BEA.exe.original.backup, not the
  full paths. A failed Save Analyzer compare names the action, not the
  compare error, on the status line. A failed compare or analysis no
  longer titles the banner complete. A failed compare no longer calls
  the files identical on the metric card. A failed analysis no longer
  dumps the analyzer sentence on the Missions card. An empty Save Lab
  or Game Options file list says to set the game folder or browse,
  instead of describing the emptiness. Refreshing that list names the
  game folder, not a
  directory. Keeping careers and then deleting a
  copy names a dumped removal without the path. A media-only install
  names the data folder, not media/data. A Cheats refresh
  that still finds no copies names the next step, not the emptiness. A
  write inside a Battle Engine Aquila game folder names the files, not
  the output paths. A missing restore backup names
  BEA.exe.original.backup, not the path. A dumped installed-game patch
  or restore uses the shared nothing-was-changed sentence. Career-save
  and Game Options patcher refusals that used to say an input or output
  path now name the files. Choosing BEA.exe on Windowed & Mods names
  the file, not a path. A Settings save list with no files names the
  game folder, not a path. Save Lab ready-state names the file, not a
  path. A Save Editor mission-grade read
  that fails names the action, not the file size. Empty Save Lab, Save
  Editor, and Game Options lists name the game folder, not a directory.
  Settings with no game folder set names the folder, not a directory.
  Settings status lines name the folder the same way. A Windowed & Mods
  install that has not been chosen names the next step, not the emptiness.
  A missing Asset Library export names the file, not a recorded path.
  A valid or partial install names the game folder, not a directory.
  A Windowed & Mods custom-selection receipt names the patch rows, not
  the catalog keys. A Windowed & Mods Last operation that still looks
  like a dump names BEA.exe, not the path. A workspace backup refusal
  names BEA.exe.original.backup, not a path. Home setup names a ready
  game folder, not a directory. Copying an Asset Library
  export names the file, not a path. A safe copy with no
  careers names the next step, not the emptiness. Asset Library file cards say
  File details and Export file, not Path details. Media with no
  game folder set names the folder, not a directory. An installed-game
  refusal that already says nothing was changed is not said twice.
  Media folder cards say Folder details, not Path details. A
  live-trainer write block before the first reading names the next
  step, not the emptiness. The Asset Library copy
  button names the file, not a path. Registering a
  managed copy names the app-owned profile folder, not a root. An empty
  Lore library names the next step, not the emptiness.
  Putting a career in a safe copy when none
  exists names the next step, not the emptiness. A missing
  managed copy names the folder, not a directory. The Asset Library
  catalog picker names catalog.json, not a path. Windowed & Mods
  source cards say Source file details, not a path. The replacement
  picker names the .ogg file. A device, drive-relative,
  or network location refusal names the location, not a path. A
  Windowed & Mods verify hint names the file, not a path. Save Editor
  advanced overrides with none chosen name the next step, not the emptiness.
  An empty Asset Library catalog status names the next step, not the emptiness.
  A Goodie with no preview names the next step, not the emptiness.
  A Windowed & Mods launch plan that is not ready names the next step,
  not the emptiness. A missing playable copy names the folder, not a path.
  Staging music in a missing copy names the folder, not a path. A
  resolved network or non-local drive refusal names the location,
  not a path. A music replacement manifest names the files, not a path.
  A Windowed & Mods create that cannot see the source game folder names
  the next step, not the emptiness. A missing copy used to launch names
  the folder, not a path. A blank app-owned profile folder names the
  folder, not a root. Preparing, copying, or deleting with a blank
  app-owned folder names that folder, not a root. A missing Asset
  Library sidecar preview names the next step, not the emptiness. A
  missing inline video names the file, not a path. A missing Lore
  document reuses the could-not-be-opened sentence, not a key.
  A missing copied english.dat, its backup, or 100_res_PC.aya
  names the file, not a path. A missing copied music replacement
  or its backup names the file, not a path. A missing copied
  defaultoptions.bea or its backup names the file, not a path.
  Windowed & Mods preset details name restore steps, not a path.
  A BEA.exe-only copy names the file, not a path.

## 1.0.11 — 2026-08-07

- **No debug symbols in the ZIP.** Previously two PDBs shipped inside the
  package, embedding the build machine's absolute path and submodule names.
  Now excluded and enforced by the package probe (which denies `.pdb` and
  `.lib` entries).
- **Public identity fixed.** The executable now reports "Onslaught Toolkit"
  as its file description and product name (previously the internal project
  name), with a clean `1.0.11` version and no git hash in the About page.
- Friendly user-facing copy replaces raw exception text on the Media and
  Binary Patches pages.
- Release probe green on this exact tree: 93/93 checks (launch, Home, Lore,
  and Media smokes against the extracted app), ZIP + SHA-256 sidecar.

Download: `OnslaughtToolkit-winui-v1.0.11-win-x64.zip` (+ `.sha256` sidecar).

## 1.0.10 — 2026-08-05

- Save rescue: deleting a safe copy no longer takes the careers inside it.
- Backup-gated direct patching of the installed game (backup first, verified
  hash, no opt-out).
- Safe-copy manager in the GUI with sizes and careers shown.
- Live trainer phase 1 (read-only vitals; ammo/timescale refused for lack of
  address evidence); god-mode read-only discovery.
- Lore reader renders natively (WebView2 dropped from the page).
- 33 invented cutscene titles removed; media failures made visible.
- CLI v2 with verbs, `--json`, exit codes 0/1/2.

## 1.0.9 and earlier

See the GitHub Releases page for prior releases.
