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
