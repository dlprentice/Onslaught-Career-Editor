# Active Goal Slice

Status: active
Last updated: 2026-06-24
Policy: `goal.policy.md`

## Current Slice

Close the Windowed & Mods patch/mod UX/testability cleanup plus the Lore package
truth and Ghidra path documentation follow-up from this checkout:

`C:\Users\david\source\Onslaught-Career-Editor`

This repo is the normal day-to-day working repo. The former private checkout is
an archived comparison/source snapshot, not required for normal public
contributor work.

## Current Truth

- Static Ghidra closure remains complete: `6411/6411 = 100.00%`, static debt
  `0 / 0 / 0`, active current-risk re-audit `1179/1179 = 100.00%`.
- Public source is primary and is not a sparse export. Track useful source,
  tools, tests, RE notes, wave notes, state batons, agent reports, readiness
  notes, compact proof summaries, and non-secret/non-payload scratch text.
- Hard payloads remain local/ignored overlays: actual game executables/DLLs/
  archives/media, copied runtime profiles, arbitrary save/options payloads,
  raw screenshots/frame dumps, raw CDB logs, bulky generated proof captures,
  full Ghidra databases/backups, secrets, local config, caches, and build/test/
  package outputs.
- `game/`, `save-attempts/`, `local-rom-input/`, `mcps/`, `local-proofs/`, and
  `local-ghidra/` are maintainer-local ignored overlays in this checkout. They
  are useful locally but are not public clone requirements.
- `local-proofs/OnslaughtRuntimeProofArchive` and
  `local-ghidra/GhidraBackups` are ignored junctions to `G:` archives rather
  than duplicated on `C:`.
- The public app release `v1.0.5` remains the latest published GitHub asset
  until `v1.0.6` is tagged and published. The validated `v1.0.6` candidate
  keeps the same safe wrapper layout and adds clearer Lore source-link copy.
  It supersedes `v1.0.3`/`v1.0.4`/`v1.0.5`: v1.0.3 included deep
  `lore-book/` mirror paths that can hit Windows Explorer `0x80010135`
  path-too-long extraction failures under normal Downloads paths, and v1.0.4
  did not rewrite deeper unbundled Lore links, while v1.0.5 did not yet surface
  the source-link boundary clearly inside the app. The v1.0.6 package keeps the
  friendly wrapper layout, includes the `lore-book/BOOK.md`-linked offline Lore
  reader set, rewrites deeper unbundled source links to GitHub source/search
  pages, labels source links in-app, auto-detects common Steam installs where
  possible, and makes Asset Library catalog requirements clear instead of
  implying raw game browsing.
- The current app ZIP should not raw-copy the full `lore-book/` mirror because
  the full tree has long RE/proof filenames that can exceed Windows Explorer
  Extract All path budgets. Full offline Lore remains a planned WinUI feature
  via a generated short-path content pack; see
  `roadmap/winui-lore-offline-pack-plan.md`.
- The maintainer-local live Ghidra project path is
  `C:\Users\david\Ghidra\Projects\BEA.gpr` with store
  `C:\Users\david\Ghidra\Projects\BEA.rep\`. The repo tracks scripts, exports,
  ledgers, and docs instead of full binary project stores.
- Current Windowed & Mods cleanup adds patch-key-derived AutomationIds for
  dynamic patch rows, checkboxes, and Details expanders; it also keeps CDB,
  proof-boundary, key-census, raw-offset, and evidence jargon out of the normal
  debug-camera, online-unavailable, music-staging, and preset-detail path.
- Online multiplayer is still not player-ready. Host/Join remains disabled
  until distinct-endpoint command-source proof and source-bound copied-runtime
  causality proof both exist.
- Installed Steam game files and original `BEA.exe` remain read-only.

## Public Reproducible Gates

These are normal public source/release checks:

```powershell
git submodule update --init --recursive
node --version # v24.x
npm --version  # >=11.12 <12; npm@11.12.1 is the packageManager target
npm run test:hard-payload-safety
npm install
npm run build:winui
npm run build:cli
npm run build:host
npm run test:appcore
npm run test:winui
npm run test:winui-primary-lane
npm run test:winui-safe-copy-preflight
npm run test:winui-patch-engine-safety
npm run test:doc-commands
npm run test:md-links
npm run test:public-allowlist
npm run test:repo-hygiene
npm run test:winui-notices
npm run release:profile-check
npm run release:curated-check
npm run test:winui-zip-release-candidate-probe
```

## Maintainer-Local Evidence

These are useful only when the local archive/material exists; they are not
public clone setup requirements:

```powershell
py -3 tools\public_primary_migration_inventory.py --check --private-root C:\Users\david\source\Onslaught-Career-Editor-private --require-private-root
py -3 tools\winui_safe_copy_music_decode_window_correlation_diagnostic.py --check G:\OnslaughtRuntimeProofArchive\winui-safe-copy-live-runtime\music-audible-live-20260624-144834\raw\decode-window-correlation-diagnostic.json
Get-Process BEA,cdb -ErrorAction SilentlyContinue
```

## Next Executable Work

1. Commit and push the validated Windowed & Mods patch-row UX/testability plus
   Lore/Ghidra package-truth cleanup after docs/state/hygiene gates are green.
2. Continue bounded patch/mod/runtime proof work from public `main`, likely
   Asset Library first-run catalog guidance or the next safe-copy/mod runtime
   proof that does not require external endpoint material.

## Stop Conditions

- Any step would mutate the installed Steam game folder or original `BEA.exe`.
- Any tracked file would add actual game executable/DLL/archive/media payload,
  arbitrary save/options payload, full Ghidra database/backup, raw CDB log,
  screenshot/frame dump, secret, `.env*`, copied runtime output, or build
  artifact.
- Online wording or UI implies player-ready online multiplayer before required
  distinct-endpoint and source-bound runtime proofs exist.
- A runtime proof requires unavailable operator hardware/endpoints and no other
  bounded progress remains.
- A static RE contradiction appears; stop product/runtime work and correct the
  static claim with bounded evidence first.
