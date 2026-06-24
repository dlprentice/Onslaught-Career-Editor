# Public-Primary Full Migration Inventory

Status: accepted public-primary source migration inventory
Date: 2026-06-24

## Summary

The public repo at `C:\Users\david\source\Onslaught-Career-Editor` is the
primary working repo. This inventory compares the public repo against the former
private repo tracked index and accepts public-primary migration when the only
remaining private-only tracked files are hard payloads or volatile scratch
outputs.

Validated command:

```powershell
py -3 tools\public_primary_migration_inventory.py --self-test
py -3 tools\public_primary_migration_inventory.py --check --private-root C:\Users\david\source\Onslaught-Career-Editor-private --require-private-root
```

Accepted output:

```text
Public-primary migration inventory: PASS
Private tracked paths: 24839
Public tracked paths: 19264
Allowed private-only hard-payload/scratch paths: 5584
```

## Material Added To Public

- Restored `references/Onslaught` and `references/AYAResourceExtractor` as
  tracked submodule gitlinks pinned to the same commits as the former private
  repo.
- Restored archived Electron media source files:
  - `archive/electron-workbench/packages/ui/src/components/media/MediaDetails.tsx`
  - `archive/electron-workbench/packages/ui/src/components/media/MediaSection.tsx`
- Restored the narrow public-primary save regression fixture:
  - `tests_shared/fixtures/gold_career_save.bin`
  - SHA-256:
    `0c17e47db9d666e9b26ef88d43d0a25e7cbfbf4f88c8005cc748965050e506fb`
- Anchored local overlay `.gitignore` entries so source directories named
  `media` are no longer accidentally ignored.
- Added `tools/public_primary_migration_inventory.py` and npm script
  `test:public-primary-migration-inventory`.

## Remaining Private-Only Classes

The accepted remaining private-only tracked delta is limited to:

- `game/**`
- `media/**`
- `save-attempts/**`
- temporary save/options payload folders such as `.tmp_cs_*`
- top-level historical executable/archive payloads such as `BEA_Widescreen.exe`
  and `BEA.exe.gzf`
- volatile RE scratch outputs under
  `reverse-engineering/binary-analysis/scratch/**`

Those classes remain local/ignored or historical-private because they are actual
game/runtime payloads, save/options payloads, raw generated proof material, or
old scratch exports. They are represented publicly by tracked source, scripts,
contracts, hashes, docs, compact proof summaries, and reproducible checkers.

## Non-Claims

- This does not publish Battle Engine Aquila executables, DLLs, archives, media,
  extracted assets, raw screenshots, raw CDB logs, full Ghidra databases, or
  copied runtime proof bundles.
- This does not make online multiplayer player-ready.
- This does not change the installed-game read-only rule.
- This does not replace the WinUI release ZIP boundary; release ZIPs remain
  intentional app artifacts rather than the whole source repo.
