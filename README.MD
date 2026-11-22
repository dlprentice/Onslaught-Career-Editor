# Onslaught Modding & Content Toolkit

Status: active — the project overview
Last updated: 2026-11-21 (repurposed into the Onslaught Modding & Content Toolkit; standalone Companion GUI and frozen reverse-engineering copy retired)
Summary: what this repository holds (the JSON Content Catalogue, Content Inventory, live asset/format decoders, mod-staging tools and lore), how to run checks on a public clone, and where the rest of the Onslaught ecosystem lives.

The **Onslaught Modding & Content Toolkit** (repository name `Onslaught-Career-Editor`) is the public modding, content-cataloguing, format-inspection and lore repository for *Battle Engine Aquila* (2003, Lost Toys).

The former standalone Godot/.NET **Onslaught Companion** career-editor GUI was retired on 2026-11-21 now that player-facing career management, Service Record, backups, Goodies, audio/lore browsing, mods and map authoring live natively in [Onslaught CE](https://github.com/dlprentice/onslaught-ce). The frozen local copy of `reverse-engineering/` was removed in the same pass: the maintained game documentation lives in [onslaught-preservation](https://github.com/dlprentice/onslaught-preservation), the byte-matching decompilation in [onslaught-decomp](https://github.com/dlprentice/onslaught-decomp), and historical records in Git history and the private maintainer archive.

To contribute to any part of the project, start with [Where to contribute](CONTRIBUTING.md#where-to-contribute): it states which public repository takes which kind of work, and everyone contributes by fork and pull request.

| I want to | Start at |
| --- | --- |
| Play the game (including built-in Career, Backups, Mods & Editor) | [Onslaught CE](https://github.com/dlprentice/onslaught-ce) (you need your own copy of the game) |
| Build the local JSON Content Catalogue or Content Inventory | [Tools guide](tools/README.md#content-catalogue) |
| Scaffold, discover targets for, and validate an Onslaught CE mod | [Mod Author Quickstart](docs/MOD-AUTHOR-QUICKSTART.md) |
| Inspect assets, decode formats or stage a CE world mod | [Tools guide](tools/README.md#assets-and-formats) |
| Read the game's lore and development history | [lore/_index.md](lore/_index.md) and [lore-book/BOOK.md](lore-book/BOOK.md) |
| Read game format specs, saves and mechanics | [onslaught-preservation](https://github.com/dlprentice/onslaught-preservation) |
| Explore the byte-matching decompilation | [onslaught-decomp](https://github.com/dlprentice/onslaught-decomp) |
| Ask a question or share an idea | [Onslaught CE Discussions](https://github.com/dlprentice/onslaught-ce/discussions) |
| Contribute a change | [CONTRIBUTING.md](CONTRIBUTING.md) and [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md) |
| Choose the checks for a change | [VALIDATION.md](VALIDATION.md) |
| Find where code and documents live | [PROJECT-INDEX.md](PROJECT-INDEX.md) |
| See the direction, work queue and demonstrated capabilities | [GOAL.md](GOAL.md), [PROGRAM.md](PROGRAM.md) and [CURRENT_CAPABILITIES.md](CURRENT_CAPABILITIES.md) |

## What this repository holds

- **JSON Content Catalogue (`tools/content_catalog.py`, `content_catalog.schema.json`, `content_catalog_gate.py`).** Surveys every file of a user-supplied PC installation and builds a verified JSON catalogue of textures, meshes, animations, imposters, levels, placed things, waypoint paths, compiled mission scripts, physics definitions, goodies, particles, audio banks, films, archives and text tables, with cross-asset relationships derived from loader rules in [onslaught-decomp](https://github.com/dlprentice/onslaught-decomp).
- **Byte-Level Content Inventory (`tools/content_inventory.py`, `content_inventory.schema.json`, `content_inventory_gate.py`).** Accounts for every byte of a selected PC installation (decoded, referenced or unknown) and emits `asset-metadata.jsonl` for offline asset pipelines such as HD texture/model inspection or upscaling.
- **Modding, Format & World Tools (`tools/`).** Pure-Python decoders, round-trip encoders, inspectors and mod stagers for AYA archives, CMSH meshes and animations, DDS textures, XAP sample banks, Goodie archives, particle sets, physics scripts, language tables, battle engine configurations, world headers, world bodies (`world_resources_decode.py` / `world_resources_encode.py` / `world_mod_stage.py` / `world_edit_move.py` / `world_edit_preview.py` / `world_thing_index.py`), terrain heightfields (`heightfield_lookup.py`) and the Mission Script Language compiler (`msl_compile.py` / `msl_gate.py`).
- **Canonical Lore Library (`lore/`, `lore-book/`).** Offline narrative, characters, factions, weapons, worlds and development history of *Battle Engine Aquila*.
- **Repository Safety & Documentation Gates (`tools/`).** Payload/secret/retail-byte guard (`public_allowlist_safety_check.py`), Markdown link and reachability checks (`md_link_check.py`, `md_reachability_check.py`), documentation header gate (`doc_header_check.py`) and tool test runner (`run_tool_tests.py`).

This repository holds no game files, Ghidra database, decompiler output or decomp source.

This is an unofficial community project. It is not affiliated with or endorsed by the game's publishers or rights holders. Repository licenses cover their respective project code and documentation; they grant no rights in the retail game, its assets, names, or trademarks.

## Related repositories

| Repository | What it holds |
| --- | --- |
| This repository | The Modding & Content Toolkit: JSON Content Catalogue, Content Inventory, format decoders, mod-staging tools, lore and project overview |
| [Onslaught CE](https://github.com/dlprentice/onslaught-ce) | Native Linux and Windows port built from the decompilation, with built-in Career, Backups, Mods and Editor UI; GPL-3.0-only |
| [onslaught-decomp](https://github.com/dlprentice/onslaught-decomp) | Byte-matching decompilation of the retail executable (5,482/5,482 mapped functions match purely from source in the maintainer tree; 5,449/5,482 in the public export excluding DirectX SDK sample files); GPL-3.0-only |
| [onslaught-preservation](https://github.com/dlprentice/onslaught-preservation) | Maintained home of *Battle Engine Aquila* game documentation: file formats, saves, mechanics, levels and engine; CC BY-SA 4.0 |
| [onslaught-godot](https://github.com/dlprentice/onslaught-godot) | Proof-of-concept Godot 4 C# rebuild compared Present by Present with recorded runs; GPL-3.0-only |
| [`stuart73/Onslaught`](https://github.com/stuart73/Onslaught) | Stuart Gillam's GPL Onslaught source release; pinned as [`references/Onslaught`](references/Onslaught) |
| [`stuart73/AYAResourceExtractor`](https://github.com/stuart73/AYAResourceExtractor) | Stuart Gillam's resource extractor; pinned as [`references/AYAResourceExtractor`](references/AYAResourceExtractor) |

The two forks under `references/` are pinned references, not contribution targets.

## Report a problem

- Playing the game (Onslaught CE): [Onslaught CE's issues](https://github.com/dlprentice/onslaught-ce/issues).
- The byte-matching decompilation: [onslaught-decomp's issues](https://github.com/dlprentice/onslaught-decomp/issues).
- The Content Catalogue, format/mod tools, lore or this repository's documents: [this repository's issues](https://github.com/dlprentice/Onslaught-Career-Editor/issues).
- Game documentation (formats, saves, mechanics, levels, engine): [onslaught-preservation's issues](https://github.com/dlprentice/onslaught-preservation/issues).
- The Godot rebuild: [onslaught-godot's issues](https://github.com/dlprentice/onslaught-godot/issues).
- General questions and ideas across the project: [Onslaught CE Discussions](https://github.com/dlprentice/onslaught-ce/discussions).

## Where things live

| Path | Owner |
| --- | --- |
| [`tools/`](tools/README.md) | JSON Content Catalogue, Content Inventory, format decoders/encoders, mod-staging tools, reader fixtures, format contract tables and repository checks |
| [`lore/`](lore/_index.md) and [`lore-book/`](lore-book/BOOK.md) | Canonical public lore and development history library |
| [`tests_shared/`](tests_shared/fixtures/README.md) | Narrow reviewed save regression fixture (`gold_career_save.bin`) used by inventory tests |
| [`references/`](references/) | Pinned public `Onslaught` and `AYAResourceExtractor` submodules (source references, not proof of retail behavior) |

[`PROJECT-INDEX.md`](PROJECT-INDEX.md) maps source ownership and dependencies; [`CURRENT_CAPABILITIES.md`](CURRENT_CAPABILITIES.md) states what is demonstrated today and what is not. Retired surfaces (the Godot/.NET Companion GUI, WinUI v1.0.11, AppCore, CLI, Electron, Python GUI, WPF and the frozen copies of `rebuild/` and `reverse-engineering/`) remain in Git history; WinUI v1.0.11 release notes remain in [`CHANGELOG.md`](CHANGELOG.md).

## Setup and checks

All authored Toolkit tests and documentation/safety checks run on Linux (or WSL2 on Windows) with no game installation, Godot or .NET required. Tools that inspect an actual retail installation require your own lawfully obtained copy of *Battle Engine Aquila*.

### Public setup

Prerequisites:

- Git, including the pinned public reference submodules for the full safety scan (`git submodule update --init --recursive`)
- Python 3.12 or newer (tested on Python 3.14) with `numpy`, `Pillow` and `jsonschema` for the full tool and schema suites (documentation and safety checks use the standard library only; see [Python prerequisites](tools/README.md#python-prerequisites))
- Optionally, Node.js/npm for the convenience scripts in [`package.json`](package.json); equivalent `python3` commands work without Node

```bash
git clone --recurse-submodules https://github.com/dlprentice/Onslaught-Career-Editor.git
cd Onslaught-Career-Editor
python3 -m venv local-data/venv
. local-data/venv/bin/activate
python -m pip install numpy Pillow jsonschema
npm run test:safety
npm run test:docs
npm run test:tools
```

Without Node/npm:

```bash
python3 -B tools/public_allowlist_safety_check.py --self-test
python3 -B tools/public_allowlist_safety_check.py --include-submodules
python3 -B tools/md_link_check.py --self-test
python3 -B tools/md_link_check.py --check-only
python3 -B tools/doc_header_check.py --self-test
python3 -B tools/doc_header_check.py
python3 -B tools/run_tool_tests.py --self-test
python3 -B tools/run_tool_tests.py
```

For a local retail installation, build and validate the Content Catalogue or Content Inventory into ignored `local-data/`:

```bash
python3 -B tools/content_catalog.py --game /path/to/game --out local-data/content-catalog
python3 -B tools/content_catalog_gate.py --game /path/to/game
python3 -B tools/content_inventory.py --game /path/to/game --out local-data/content-inventory
python3 -B tools/content_inventory_gate.py --game /path/to/game --inventory local-data/content-inventory
```

Root [`package.json`](package.json) is the command authority; [`VALIDATION.md`](VALIDATION.md) selects the smallest gate for each change.

## Data and mutation safety

- All Toolkit inspection, catalogue, inventory and decoding commands are read-only on your game installation and write only to explicit output directories outside the game tree (or stdout).
- Mod staging (`world_mod_stage.py`, `world_resources_encode.py stage --as-mod`) publishes only to a fresh output folder outside the game tree via `safe_generated_output.py` and never modifies an installed game.
- Never synthesize `.bes` saves from scratch: start from a real baseline and preserve file length, reserved fields and unknown bytes.
- Keep retail binaries, assets, generated catalogues/inventories, real saves, Ghidra databases, decompiler output, raw captures and secrets out of Git; `npm run test:safety` enforces the boundary.
- No telemetry: nothing in this repository collects or sends usage data.

The tracked regression fixture [`tests_shared/fixtures/gold_career_save.bin`](tests_shared/fixtures/README.md) is the reviewed exception to the no-save rule. See [`SECURITY.md`](SECURITY.md) and [`LOCAL_LAB_OVERLAY.md`](LOCAL_LAB_OVERLAY.md) for handling local inputs.

## Licenses

| Path | Licence |
| --- | --- |
| Code, schemas and configuration: `tools/` scripts, `package.json`, build/config files | GPL-3.0-only ([`LICENSE`](LICENSE)) |
| Documentation (`*.md`, `*.MD`, `.github/`), `tools/format_contracts/*.tsv`, `lore/` and `lore-book/` | CC BY-SA 4.0 ([`LICENSES/CC-BY-SA-4.0.txt`](LICENSES/CC-BY-SA-4.0.txt)) |
| `tests_shared/fixtures/gold_career_save.bin` | `LicenseRef-Retail-Save-Fixture` ([`LICENSES/LicenseRef-Retail-Save-Fixture.txt`](LICENSES/LicenseRef-Retail-Save-Fixture.txt)) |
| `references/` submodules | Their own licences |

[`REUSE.toml`](REUSE.toml) maps every path to its licence; quotations in `lore/` stay with their authors. Credits and attribution are maintained in [onslaught-preservation's `history/attribution.md`](https://github.com/dlprentice/onslaught-preservation/blob/main/history/attribution.md).
