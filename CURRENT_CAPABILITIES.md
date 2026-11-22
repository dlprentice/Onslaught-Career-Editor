# Current Capabilities

Status: active — what the Onslaught Modding & Content Toolkit demonstrates today, and what it does not
Last updated: 2026-11-21 (repurposed into the Onslaught Modding & Content Toolkit; retired standalone Companion GUI and frozen reverse-engineering copy removed)
Summary: the demonstrated capabilities and measured boundaries of this repository's JSON Content Catalogue, Content Inventory, format/modding tools and lore library.

This repository (`Onslaught-Career-Editor`) is the **Onslaught Modding & Content Toolkit**. Its player-facing Companion GUI (`companion/`) was retired on 2026-11-21 in favour of [Onslaught CE](https://github.com/dlprentice/onslaught-ce)'s native Career, Service Record, Backups, Goodies, Audio/Lore, Mods and 3D Editor screens. The frozen `reverse-engineering/` copy was removed in the same pass: live game documentation is owned by [onslaught-preservation](https://github.com/dlprentice/onslaught-preservation), the byte-matching decompilation (5,482/5,482 mapped functions matched purely from source, 0 concessions, 0 aliases; 5,449/5,482 in the public export excluding DirectX SDK sample files) by [onslaught-decomp](https://github.com/dlprentice/onslaught-decomp), and the Godot rebuild by [onslaught-godot](https://github.com/dlprentice/onslaught-godot). Prior standalone Companion, WinUI, AppCore and frozen-rebuild snapshots remain in Git history.

## JSON Content Catalogue

[`tools/content_catalog.py`](tools/README.md#content-catalogue) surveys every file of a selected PC retail installation and emits a structured JSON catalogue (`manifest.json`, `survey.json`, `coverage.json`, `assets.jsonl`) validated against [`tools/content_catalog.schema.json`](tools/content_catalog.schema.json).

- **Covered asset families:** loose DDS textures (including per-mip encoded-byte SHA-256 and raw header fields), packed archive `TEXT` / imposter / font / goodie texture records, loose and embedded CMSH meshes (including part hierarchies, `CMSP`/`MESP` hashes, bounding boxes, animation modes and `nestedMeshDetails`), framed `IMPT` imposter records and view rectangles (`tools/imposter_records.py`), levels and world bodies (`WRES`, `ERES`, `SURF`, `SSHD`, `VSDS`, `PMIB`, `DMKR`), placed things and waypoint paths, compiled mission scripts and `.msl` sources, physics definitions, battle engine configurations, sound effects and XAP bank samples, music/voice Ogg streams, Bink films, Goodie archives, particle sets and language tables.
- **Relationships and provenance:** cross-asset links (mesh-to-texture, texture-record-to-DDS, imposter-to-mesh/atlas, placement-to-definition/mesh, script-to-unit/path/sample/text/named-thing, level-to-sky/water/configuration, configuration-to-weapons/cockpit, effect-to-sample, goodie-to-asset, voice-to-text, and optional `--decomp` literal lookups) follow loader rules from [onslaught-decomp](https://github.com/dlprentice/onslaught-decomp). Unresolved and ambiguous links stay explicit.
- **Gates:** [`tools/content_catalog_tests.py`](tools/content_catalog_tests.py) and [`tools/imposter_records_tests.py`](tools/imposter_records_tests.py) validate authored installs without retail bytes (including JSON Schema validation when `jsonschema` is installed). [`tools/content_catalog_gate.py`](tools/content_catalog_gate.py) verifies all level archives, resource payloads, named-thing registries (`named_things.py`), configurations, sound effects and imposter joins against a selected retail install without modifying it.
- **Limits:** generated outputs are retail-derived and stay in ignored `local-data/` (enforced by `npm run test:safety`). Catalogue relationships reflect loader rules and static data, not runtime observation, rendered appearance or an automated HD conversion.

## Byte-Level Content Inventory

[`tools/content_inventory.py`](tools/README.md#content-inventory) builds a complete byte-level accounting of a selected PC installation (`manifest.json`, `coverage.json`, `files.jsonl`, `items.jsonl`, `asset-metadata.jsonl`, `records.jsonl`) conforming to [`tools/content_inventory.schema.json`](tools/content_inventory.schema.json).

- Every byte of every file is classified as **decoded** (consumed in loader/spec order with exact closure), **referenced** (framed by a record or header but unread) or **unknown**.
- Emits `asset-metadata.jsonl` with per-asset identities, hashes, dimensions, pixel formats, mip counts, alpha, audio channels/rates/durations and catalogue usage summaries as an offline batch input list.
- Uses dedicated pure-Python walkers (`media_readers.py` for Ogg Vorbis, Bink 1, PNG, JPEG, TGA, PE, ActiveMime, HTML, XML; `particle_set_walk.py`; `physics_values_decode.py`; `cmsh_grammar_walk.py`; `goodie_resource_walk.py`; `xap_bank_walk.py`; `msl_compile.py` / `msl_gate.py`) with optional FFmpeg cross-checking for compressed media streams (headline coverage always reports both with and without FFmpeg).
- **Gates:** [`tools/content_inventory_tests.py`](tools/content_inventory_tests.py) tests the pipeline and gate on an authored install; [`tools/content_inventory_gate.py`](tools/content_inventory_gate.py) independently re-walks archives, hashes assets, verifies images with Pillow and validates JSON Schema rows against a selected retail install.
- **Limits:** tested on Linux against a read-only PC Steam installation; Windows host behaviour and downstream HD batch processing are not validated here.

## Format Decoders, World Tools & Mod Staging

All format and modding tools under [`tools/`](tools/README.md) operate read-only on user-supplied installations and publish any generated files through [`tools/safe_generated_output.py`](tools/safe_generated_output.py) (descriptor-relative no-follow creation, atomic rename, refusal of destinations overlapping the game tree) or to stdout:

- **AYA & CMSH inspection:** `aya_archive_inventory.py`, `aya_corpus_chunk_inventory.py`, `aya_cross_platform_compare.py`, `aya_texture_fidelity_census.py`, `cmsh_static_preview.py`, `cmsh_grammar_walk.py`, `cmsh_animation_usage_census.py`, `model_transform_catalog.py`, `level_asset_xref.py`, `dds_census.py`, `export_asset_catalog.py`.
- **World & CE mod pipeline:** `world_resources_decode.py`, `world_resources_encode.py` (byte-exact world body round-trip and `stage --as-mod`), `world_mod_stage.py` (CE `mod.json` + `data/worlds/worldNNN.wrd` packaging), `world_thing_index.py`, `world_edit_preview.py`, `world_edit_move.py`, `named_things.py`, `heightfield_lookup.py`, `worldheaders_decode.py`.
- **Mission Script Language (`.msl`):** `msl_compile.py` (reference `.msl` compiler producing world-body script records), `msl_gate.py` (retail install comparison gate), `mission_script_inspect.py` (read-only compiled-script structural inspector).
- **Game tables, media & localization:** `battle_engine_config_decode.py`, `game_tables_decode.py`, `goodie_resource_walk.py`, `xap_bank_walk.py`, `language_dat_decode.py`, `export_language_corpus.py`, `export_video_manifest.py`, `options_entries_decode.py`, `particle_set_walk.py`, `physics_values_decode.py`.
- **Limits:** `world_mod_stage.py` packages world overrides according to Onslaught CE's mod loader contract but does not validate runtime gameplay, physics placement or career compatibility. Descriptor-relative CLI guards (`O_PATH`/`renameat2`) are validated on Linux; native Windows CLI behaviour is unvalidated.

## Lore & Repository Gates

- **Canonical Lore (`lore/`, `lore-book/`):** 17 narrative/reference articles and reading guide covering Allium, factions, characters, weapons, units, worlds and development history, with technical citations pointing to [onslaught-preservation](https://github.com/dlprentice/onslaught-preservation).
- **Safety & Documentation Gates:** `npm run test:safety` enforces payload, secret, retail-byte and private-path boundaries across the repository and pinned reference submodules; `npm run test:docs` checks every local Markdown link, heading anchor and documentation header (zero backlog entries); `npm run test:tools` runs all registered tool test suites.

## Retired Surfaces (Historical Reference)

- **Standalone Godot/.NET Companion GUI (`companion/`):** removed on 2026-11-21 as its player workflows moved natively into Onslaught CE. Preserved in Git history.
- **Frozen `reverse-engineering/` copy:** removed on 2026-11-21; all live game documentation lives in [onslaught-preservation](https://github.com/dlprentice/onslaught-preservation) and historical snapshots remain in Git history and the private archive.
- **Frozen `rebuild/` copy:** removed on 2026-11-11 (tag `archive/20261111-rebuild-frozen-copy`); active rebuild development lives in [onslaught-godot](https://github.com/dlprentice/onslaught-godot).
- **WinUI v1.0.11 & AppCore:** retired in October 2026; release notes remain in [`CHANGELOG.md`](CHANGELOG.md).
