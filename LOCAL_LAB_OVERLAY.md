# Local lab overlay

Status: active — the ignored-directory boundary
Last updated: 2026-11-21 (updated for the repurposed Onslaught Modding & Content Toolkit)
Summary: which ignored local paths own retail inputs and generated catalogue/inventory outputs, and what may be promoted into tracked source.

This page records the ignored local-directory boundary. Public contributors do not need or receive maintainer lab inputs; [CONTRIBUTING.md](CONTRIBUTING.md) owns public setup. Use your own licensed game files only when a tool needs them, and keep all game inputs and generated outputs ignored.

## Ignored local directories

- **`local-data/`** (Git-ignored inside this checkout): default local home for Python virtual environments (`local-data/venv`), generated JSON Content Catalogues (`local-data/content-catalog`), Content Inventories (`local-data/content-inventory`), staged mod previews and other private local outputs.
- **`local-lab/`** (Git-ignored, maintainer workstation only; absent in public clones and fresh worktrees): retained read-only retail specimens and historical evidence corpus. Fresh clones and child worktrees never copy this directory; pass explicit `--game` paths when running retail gates.
- **`.artifacts/`** (Git-ignored): optional output directory for offline diagnostic reports such as `md_link_check.py` (without `--check-only`).

## Safety rules

- Git ignore is a publication boundary, not a backup. Never run root-level `git clean -x` or `git clean -X`, and never bulk-stage ignored folders.
- Do not store secrets or credentials inside ignored folders; use the system secret store.
- Treat retail game installations and pristine specimens as read-only inputs; every Toolkit writer requires an explicit output directory outside the game tree.
- Before committing any new fixture or metadata, retain only small authored or public-safe structures and verify with `npm run test:safety`. Retail binaries/assets, real saves, generated catalogues/inventories, raw captures and Ghidra databases stay local and untracked.
