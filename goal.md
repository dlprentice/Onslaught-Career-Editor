# Active Goal Slice

Status: active
Last updated: 2026-06-24
Policy: `goal.policy.md`

## Current Slice

Close the public-primary migration so normal work happens from
`C:\Users\david\source\Onslaught-Career-Editor` with the former private repo no
longer acting as the day-to-day source of truth.

This slice is bounded to source/docs/tools/repo-readiness work:

- keep public as the primary collaboration and working repo;
- track useful project material broadly: source, tests, tools, patch catalogs,
  RE docs, wave notes, state batons, agent reports, readiness notes, and compact
  proof summaries;
- restore missing non-payload private surfaces that public still needs;
- keep hard payloads local/ignored: game files, copied executables, private
  media/input payloads, arbitrary saves/options, full Ghidra databases/backups,
  raw screenshots/frame dumps, raw CDB logs, secrets, and generated build/proof
  output;
- validate the migration with local gates and commit/push the green slice.

## Current Truth

- Static Ghidra closure remains complete: `6411/6411 = 100.00%`, static debt
  `0 / 0 / 0`, active current-risk re-audit `1179/1179 = 100.00%`.
- `v1.0.2` app release remains published at
  `https://github.com/dlprentice/Onslaught-Career-Editor/releases/tag/v1.0.2`.
- The previous runtime/music slice remains unresolved:
  `runtimeAudibleOutputProof=false`; the likely next proof step is an attach
  timing diagnostic for the missing `CGame__PlayMusicForCurrentLevel level=100`
  row.
- Online multiplayer is still not player-ready. Host/Join remains disabled until
  distinct-endpoint command-source proof and source-bound copied-runtime
  causality proof exist.
- WinUI 3 remains the current shipped app lane. Blazor/Tauri/Godot remain future
  evaluations, not active replacements for this slice.

## Migration Evidence

This slice adds or updates:

- `tools/public_primary_migration_inventory.py`
- npm script `test:public-primary-migration-inventory`
- `release/readiness/public_primary_full_migration_inventory_2026-06-24.md`
- `roadmap/public-primary-working-repo.md`
- `roadmap/repo-structure-and-archive-map.md`
- public contributor/overlay docs and state batons
- `references/Onslaught` and `references/AYAResourceExtractor` submodule
  gitlinks
- two archived Electron media source files previously hidden by an unanchored
  ignore rule
- the narrow tracked `tests_shared/fixtures/gold_career_save.bin` regression
  fixture

Accepted migration inventory:

- former private tracked paths: `24839`
- public tracked paths after this migration pass: `19264`
- accepted private-only hard-payload/scratch paths: `5584`

## Validation For This Slice

Required before closeout:

- `py -3 tools\public_primary_migration_inventory.py --self-test`
- `py -3 tools\public_primary_migration_inventory.py --check --private-root C:\Users\david\source\Onslaught-Career-Editor-private --require-private-root`
- `npm run test:hard-payload-safety`
- `npm run test:doc-commands`
- `npm run test:repo-hygiene`
- `git diff --cached --check`
- state JSON parse

## Next Executable Work After Closeout

1. Return to the music-runtime proof ladder and investigate whether the missing
   `CGame__PlayMusicForCurrentLevel level=100` row is an attach timing miss.
2. Continue patch/mod/runtime work from the public repo only.
3. Keep `runtimeAudibleOutputProof=false` unless the final checker accepts a
   complete live bundle.

## Stop Conditions

- A proposed tracked file is an actual BEA executable/DLL/game archive/media
  payload, full Ghidra database/backup, secret, `.env*`, copied runtime output,
  screenshot/frame dump, raw CDB log, or build artifact.
- A proposed runtime or patch step mutates the installed Steam game folder or
  original `BEA.exe`.
- Online wording or UI implies player-ready online multiplayer before required
  proofs exist.
- A static RE contradiction appears; stop product/runtime work and correct the
  static claim with bounded evidence first.
