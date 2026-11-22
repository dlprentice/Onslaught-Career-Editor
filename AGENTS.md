# Onslaught Modding & Content Toolkit: agent guide

Status: active — the single instruction file for this repository; `CLAUDE.md` only points here
Last updated: 2026-11-21 (updated for repurposing into the Onslaught Modding & Content Toolkit; retired Companion GUI and frozen reverse-engineering copy removed)
Summary: what this repository holds, which documents own its state, and the evidence, data, safety and licensing rules that apply here.

This repository (`Onslaught-Career-Editor`, called the Toolkit in its guides) holds the **Onslaught Modding & Content Toolkit**: the JSON Content Catalogue, Content Inventory, asset/format decoders, mod-staging tools, canonical lore library and project overview. If guide files exist above this checkout on your machine, follow them too. Contributors start with [CONTRIBUTING.md](CONTRIBUTING.md#where-to-contribute) and [README.MD](README.MD#setup-and-checks); no private checkout is required.

## What this is

A preservation and modding-tooling repository for *Battle Engine Aquila* (2003). Its active scope is:

- [`tools/`](tools/README.md): the `src/`-verified JSON Content Catalogue (`content_catalog.py`, `content_catalog.schema.json`, `content_catalog_gate.py`), Content Inventory (`content_inventory.py`, `content_inventory.schema.json`, `content_inventory_gate.py`), asset/format decoders and mod-staging utilities, plus repository doc/safety gates.
- [`lore/`](lore/_index.md) and [`lore-book/`](lore-book/BOOK.md): canonical public lore and development history.
- Project overview and coordination guides: [`GOAL.md`](GOAL.md), [`PROGRAM.md`](PROGRAM.md), [`CURRENT_CAPABILITIES.md`](CURRENT_CAPABILITIES.md), [`PROJECT-INDEX.md`](PROJECT-INDEX.md) and [`VALIDATION.md`](VALIDATION.md).

Where related work lives:

- Native Windows/Linux game port (with built-in Career, Backups, Mods and Editor screens that replaced the retired standalone Companion app): [Onslaught CE](https://github.com/dlprentice/onslaught-ce).
- Byte-matching decompilation (reverse-engineering authority): [onslaught-decomp](https://github.com/dlprentice/onslaught-decomp).
- Maintained game documentation (formats, saves, mechanics, levels, engine): [onslaught-preservation](https://github.com/dlprentice/onslaught-preservation).
- Proof-of-concept Godot 4 C# rebuild: [onslaught-godot](https://github.com/dlprentice/onslaught-godot).

## Checkouts and branches

- Public contributions use fork and pull request per [CONTRIBUTING.md](CONTRIBUTING.md). Contributor checks need no private lab inputs or retail game files ([README.MD](README.MD#setup-and-checks)).
- `main` is the integration branch; topic branches merge when their focused gates pass. Never merge pre-flatten history branches.
- Worktrees never receive a copied retail corpus; keep generated catalogues, inventories and scratch outputs in ignored `local-data/` ([LOCAL_LAB_OVERLAY.md](LOCAL_LAB_OVERLAY.md)).

## Ground rules

- **Read-only on game installs:** Toolkit inspection, catalogue, inventory and mod-staging tools must never write into a game installation. Outputs go to explicit directories outside the game tree via `tools/safe_generated_output.py` (or stdout).
- **Save preservation:** Do not synthesize `.bes` saves from scratch; start from a real baseline and preserve length, reserved fields and unknown bytes. [`tests_shared/fixtures/gold_career_save.bin`](tests_shared/fixtures/README.md) is the one tracked save fixture.
- **Public-repo boundary:** Never track retail binaries or assets, converted retail material, generated catalogues/inventories, arbitrary saves, raw debugger logs, bulky captures, Ghidra databases or backups, decompiler output, decomp source, credentials or `.env*`. Never quote original-game bytes or private machine paths in tracked text. `npm run test:safety` enforces both; reviewed exceptions live in `tools/public_allowlist_safety_check.py`.
- **Evidence rules:** Every behaviour or format claim cites a controlled measurement, byte comparison, focused test or pinned function in [onslaught-decomp](https://github.com/dlprentice/onslaught-decomp) (cited by function, never quoted). `references/Onslaught` is a source reference, not proof of retail behaviour. Write unknowns explicitly as open questions with a falsifier.
- **No `git clean` at root:** `local-data/` and `local-lab/` are ignored directories that may hold local inputs on a maintainer machine. Never run root `git clean -x`/`-X`; stage explicit paths only.
- **No telemetry:** Nothing in this repository collects or sends usage data.
- **Licensing:** Code and schemas in `tools/` and root config files are GPL-3.0-only (`LICENSE`); documentation, format-contract tables and `lore/` are CC BY-SA 4.0; `tests_shared/fixtures/gold_career_save.bin` is `LicenseRef-Retail-Save-Fixture` (`REUSE.toml`). Contributions follow inbound = outbound ([CONTRIBUTING.md](CONTRIBUTING.md#licensing-of-contributions)).
- **No hosted CI:** Do not add GitHub Actions workflows or hosted release automation unless explicitly directed; run the local validation gates instead.

## Reference routing

- Source layout and ownership: [PROJECT-INDEX.md](PROJECT-INDEX.md)
- Setup and commands: [README.MD](README.MD#setup-and-checks) and [package.json](package.json)
- Gate selection: [VALIDATION.md](VALIDATION.md)
- Tools catalogue and Python prerequisites: [tools/README.md](tools/README.md)
- Documentation header standard: [DOCUMENTATION.md](DOCUMENTATION.md)
- Ignored local data boundary: [LOCAL_LAB_OVERLAY.md](LOCAL_LAB_OVERLAY.md)
- Security and private reporting: [SECURITY.md](SECURITY.md)

## Definition of done

1. Run the narrowest gate that could falsify the change:
   - Docs or deletions: `git diff --check` and `npm run test:docs`
   - Added/edited tracked files: `npm run test:safety`
   - Tool changes: the affected `python3 -B tools/<name>_tests.py` and `npm run test:tools`
   - Catalogue/inventory changes: `python3 -B tools/content_catalog_tests.py`, `python3 -B tools/content_inventory_tests.py`, and (when retail data is available locally) `content_catalog_gate.py` / `content_inventory_gate.py`
2. Every new or edited tracked `.md` carries `Status:`, `Last updated:` (or `Date:`) and `Summary:` (or `Verdict:`) in its header block (`DOCUMENTATION.md`). `tools/doc_header_backlog.txt` stays at zero entries.
3. Stage only scoped paths and write plain, public-neutral commit messages describing the change itself (no session links, private paths or internal tooling chatter).
