# Onslaught Toolkit changelog

Status: active — app-release record only
Last updated: 2026-08-18
Evidence: MEASURED — each entry names the released ZIP/tag it describes and
was written from the release probe report and release notes of that tag.
Summary: per-version record of shipped WinUI releases, for downloaders who
arrive from the Releases page. RE generations are NOT recorded here — they
live in `developer_state.json` and the campaign ledgers.

## Unreleased

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
  without dumping the full path. Save Lab and Game Options also keep the write
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
  without the exception. An Asset Library search with no hits now says to try
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
  music-swap note names the backup file the same way. A live-trainer attach
  refusal names why the copy was not opened, without the Win32
  dump or a path. A live-trainer write that cannot open the copy
  names that refusal the same way, without the Win32 dump.

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
