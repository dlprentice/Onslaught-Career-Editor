# Execution Program

Status: active — cross-project work queue and Toolkit backlog
Last updated: 2026-11-21 (repurposed repository into the Onslaught Modding & Content Toolkit; standalone Companion GUI retired into Onslaught CE; frozen reverse-engineering copy removed in favour of onslaught-preservation)
Summary: the cross-project work queue across Onslaught CE, the byte-matching decompilation, the Godot rebuild, game documentation and this Modding & Content Toolkit.

[`GOAL.md`](GOAL.md) sets the direction. Toolkit capability claims belong in [`CURRENT_CAPABILITIES.md`](CURRENT_CAPABILITIES.md) and checks in [`VALIDATION.md`](VALIDATION.md); Onslaught CE, `onslaught-decomp`, `onslaught-godot` and `onslaught-preservation` each own their detailed release and evidence records.

## Cross-project progress and priorities

| Area | Current state and remaining outcome | Detailed owner |
| --- | --- | --- |
| Onslaught CE releases & player experience | Latest public release: 0.1.13. CE follows an incremental release cadence (`0.1.14` through `0.1.19`) leading to `0.2.0` for the full milestone. Physical Windows validation of fixes, controls, high-resolution UI readability and device recovery remain gated per release. | [Onslaught CE releases](https://github.com/dlprentice/onslaught-ce/releases/latest) |
| Native CE Career, Backups, Mods & Editor UI | Player-facing Career/Service Record, Goodies, Cheats, Settings, Backups, Music/Lore, Mods and 3D `.ceproject` Map Editor workflows live natively in Onslaught CE; the former standalone Companion GUI in this repository was retired on 2026-11-21. Remaining CE work includes Windows parity/backup custody, full in-game career edit coordination, persistent terrain authoring and complete edit–play–return loops. | [Onslaught CE](https://github.com/dlprentice/onslaught-ce) |
| Online multiplayer, Commander & direct unit play | Required for CE 0.2.0: cross-platform Linux/Windows co-op and versus/skirmish play with lobby browser and voice/text chat; continuous real-time 3D RTS Commander; and direct control of eligible infantry, vehicles, guns and structures with safe AI hand-back. | [Onslaught CE](https://github.com/dlprentice/onslaught-ce) and [`GOAL.md`](GOAL.md) |
| Explorable 3D museum | Required for CE 0.2.0: an explorable 3D museum reached through CE's menus, distinct from the Goodies gallery. | [Onslaught CE](https://github.com/dlprentice/onslaught-ce) |
| Modding & Content Toolkit (this repository) | Active home of the `src/`-verified JSON Content Catalogue (`tools/content_catalog.py`, `content_catalog.schema.json`, `content_catalog_gate.py`), byte-level Content Inventory (`tools/content_inventory.py`, `content_inventory_gate.py`), format decoders/encoders, CE world-mod stagers (`world_mod_stage.py`, `world_resources_encode.py`), MSL compiler (`msl_compile.py`) and canonical lore (`lore/`). | [`CURRENT_CAPABILITIES.md`](CURRENT_CAPABILITIES.md) and [`tools/README.md`](tools/README.md) |
| Decompilation baseline | All 5,482 of 5,482 mapped game functions match purely from source in the maintainer tree, with 0 object-byte concessions and 0 link aliases (5,449/5,482 in the public export, excluding 33 functions in third-party DirectX SDK sample files). Ongoing work: public export maintenance and source/layout stand-in cleanup. | [onslaught-decomp](https://github.com/dlprentice/onslaught-decomp) |
| Game documentation | Maintained in `onslaught-preservation` (file formats, saves, mechanics, levels, engine, platforms, history). The frozen `reverse-engineering/` copy in this repository was removed on 2026-11-21 after verifying full archive/preservation parity. | [onslaught-preservation](https://github.com/dlprentice/onslaught-preservation) |
| Godot 4 C# rebuild | Proof-of-concept simulation (`OnslaughtRebuild.Parity`) and presentation (`OnslaughtRebuild.Host`) measured Present by Present against recorded runs. | [onslaught-godot parity](https://github.com/dlprentice/onslaught-godot/blob/main/rebuild/PARITY.md) |

## Toolkit backlog

### Content catalogue & inventory

- Keep [`tools/content_catalog.py`](tools/content_catalog.py), [`tools/content_catalog.schema.json`](tools/content_catalog.schema.json) and [`tools/content_catalog_gate.py`](tools/content_catalog_gate.py) synchronized with loader findings in [onslaught-decomp](https://github.com/dlprentice/onslaught-decomp) and format documentation in [onslaught-preservation](https://github.com/dlprentice/onslaught-preservation).
- Expand decoded-byte coverage in [`tools/content_inventory.py`](tools/content_inventory.py) where new loader rules are verified (for example font records `FGEN`/`DXFT`, unread `CIMP`/`DATA` fields and terrain mixer pixel metadata), keeping every unread span explicitly classified as referenced rather than guessed.
- Keep `asset-metadata.jsonl` accurate and schema-validated as a clean offline batch input for future HD texture/model/audio tooling without distributing proprietary game files.

### Modding, world & script tools

- Maintain byte-exact world decoding/encoding (`world_resources_decode.py`, `world_resources_encode.py`), read-only previews (`world_edit_preview.py`, `world_thing_index.py`), single-object edits (`world_edit_move.py`) and CE mod packaging (`world_mod_stage.py`) aligned with Onslaught CE's mod loader contract.
- Keep the Mission Script Language reference compiler (`msl_compile.py`, `msl_gate.py`) and structural inspector (`mission_script_inspect.py`) tested against authored fixtures and retail verification gates.
- Validate Windows CLI paths for tools that currently rely on Linux `O_PATH`/`renameat2` descriptor-relative safeguards before claiming Windows CLI support.

### Lore & repository hygiene

- Maintain [`lore/`](lore/_index.md) and [`lore-book/BOOK.md`](lore-book/BOOK.md) with accurate citations into [onslaught-preservation](https://github.com/dlprentice/onslaught-preservation).
- Keep `npm run test:safety`, `npm run test:docs` (zero backlog entries) and `npm run test:tools` green on every change.
