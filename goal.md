# Active Goal Slice

Status: active
Last updated: 2026-06-25
Policy: `goal.policy.md`

## Current Slice

Add clearer Asset Library first-run catalog guidance so a new public checkout or
portable app user understands why the catalog is empty, how to point the app at
generated local catalog material, and what still requires a local game/assets
overlay. Do not bundle game assets or imply full 3D rendering/rebuild parity.
Continue bounded patch/mod UX and runtime-proof work from this checkout:

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
- The public app release `v1.0.7` is the latest published GitHub asset. It keeps
  the friendly wrapper layout, includes the generated short-path `lore-pack/`
  content pack, and avoids raw deep `lore-book/` paths that can hit Windows
  Explorer `0x80010135` path-too-long extraction failures.
- The source tree stages packaged public Lore library content through a
  generated short-path `lore-pack/` content pack. Package
  probes build and validate `lore-pack/onslaught-lore.v1.index.json` plus
  `lore-pack/onslaught-lore.v1.jsonl`, keep only short `lore-book/` entry files
  beside it, and reject raw deep `lore-book/` mirror leakage. The latest local
  package probe generated 943 public-safe offline Markdown/TXT Lore documents
  and passed launch/Home/Lore/Media smokes; external references may still open
  in the browser.
- The maintainer-local live Ghidra project path is
  `C:\Users\david\Ghidra\Projects\BEA.gpr` with store
  `C:\Users\david\Ghidra\Projects\BEA.rep\`. The repo tracks scripts, exports,
  ledgers, and docs instead of full binary project stores.
- Current WinUI Lore cleanup loads generated `lore-pack/` documents when present,
  falls back to `lore-book/BOOK.md` otherwise, keeps included document links
  inside the reader, and labels source/external links as browser actions.
- Windowed & Mods selected-state UX for safe-copy profiles and menu-background
  choices is accepted: visible selected button styling, plain selected-status
  text, UIA selected names, and focused runtime UIA/visual smoke coverage are in
  place. This did not change patch rows, byte patches, safe-copy launch
  behavior, online proof, music audible-output proof, rebuild proof, or
  installed-game mutation.
- Online multiplayer is still not player-ready. Host/Join remains disabled
  until distinct-endpoint command-source proof and source-bound copied-runtime
  causality proof both exist.
- Music audible output is still not proven. The previous rejected live bundle
  showed CDB decode instants at about 44-46 seconds but raw WAV data spanning
  only about 11-12 seconds, so the accepted 2026-06-25 helper/materializer
  hardening now preserves/verifies wall-clock WAV data span, helper-authored
  padding metadata, and canonical WAV header/data-frame consistency before any
  later private live materializer attempt.
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

1. Add clearer Asset Library first-run catalog guidance for empty catalog state,
   generated catalog selection, and local overlay expectations.
2. Keep the guidance plain and actionable; move technical catalog-generation and
   importer/rebuild details behind existing advanced/docs surfaces.
3. Defer another private music live-bundle attempt until the helper/materializer
   guard is present and no BEA/CDB process is already running.

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
