# Onslaught Toolkit changelog

Status: active — app-release record only
Last updated: 2026-08-24
Evidence: MEASURED — published entries name the released ZIP/tag they
describe. A version cut prepared before publication is labeled as a candidate
and does not invent a tag or GitHub Release. RE generations are NOT recorded
here — they live in `developer_state.json` and the campaign ledgers.
Summary: per-version record of shipped WinUI releases, for downloaders who
arrive from the Releases page.

## Unreleased

## 1.0.12 — 2026-08-24 (candidate; not a GitHub Release)

Source-tree version cut for the next unsigned portable ZIP. No git tag or
GitHub Release is authorized by this entry.

- Save Lab now shows what the opened save already has for campaign links,
  listed Goodies, mission grades, and a focused Goodie, so a write replaces a
  named mix rather than a blind table.
- Cheats shows which offered cheats the source save already switches on, and
  can copy live-trainer readings into the Set and Hold boxes. Life, energy,
  and shields can be held together. It is still a top-up, not a freeze:
  walker mode still needs energy held for shields to last, jet mode still
  zeros shields, and one hit big enough to kill still will.
- Windowed & Mods names which listed catalog patches a safe copy already has
  by reading that copy's `BEA.exe`. The installed game is not opened.
- Settings and Home say whether the chosen `BEA.exe` is the known Steam
  retail file. A changed file is not called an original; a copy made from it
  is disclosed as carrying those changes. Auto-detect failure is shown on
  Settings. Save Lab, Game Options, and Cheats name whether the file sits in
  the installed game, a playable copy, or a folder the player chose.
- Player-facing pages name files and folders, not full paths, and no longer
  dump raw exceptions. Writes into the installed game stay refused except
  for the existing backup-gated installed-game path.
- The portable ZIP wraps the payload in one `Onslaught-Toolkit/` folder.
  Extracted launch, Home, Lore, generated-synthetic Safe Copy, and Media
  smokes remain the candidate gate. The package is still unsigned and is not
  an installer, MSIX, or Store build.

Publication (tag, GitHub Release, upload) remains maintainer-owned.

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
