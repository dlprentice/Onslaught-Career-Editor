# Tools

Status: active — the Onslaught Modding & Content Toolkit surface
Last updated: 2026-11-21 (repurposed into the Onslaught Modding & Content Toolkit; retired Companion build/codegen, rebuild parity probes and pre-decomp binary scanners removed)
Summary: what each tool in `tools/` does, Python prerequisites, how to run the JSON Content Catalogue and Content Inventory, and the safety and documentation gates.

`tools/` is the executable core of the **Onslaught Modding & Content Toolkit**: the `src/`-verified JSON Content Catalogue, byte-level Content Inventory, read-only format decoders, round-trip world and Mission Script Language tools, Onslaught CE mod stagers, and repository safety/documentation gates.

Root [`package.json`](../package.json) owns the npm shortcuts. Documentation and safety checks use the Python standard library and the pinned public reference submodules (`git submodule update --init --recursive`); authored tool suites need no retail game installation, Godot or .NET SDK.

```bash
npm run test:safety
npm run test:docs
npm run test:tools
```

`npm run test:tools` runs `tools/run_tool_tests.py --self-test` followed by every registered test suite. The self-test fails if any `*_tests.py` (or `test_*.py`) file in the repository is neither registered in `SUITES` nor listed with a reason in `NOT_IN_THIS_GATE`.

## Python prerequisites

Python 3.12 or newer (tested on Python 3.14). Required third-party packages depend on the suite you run:

| Scope | Additional Python packages or inputs |
| --- | --- |
| Documentation and safety gates (`test:docs`, `test:safety`) | Standard library only; full safety scan requires initialized `references/` submodules |
| Authored catalogue, world, mod-staging and MSL suites (`content_catalog_tests.py`, `world_resources_encode_tests.py`, `msl_compile_tests.py`, etc.) | Standard library; `jsonschema` enables JSON Schema assertions (without `jsonschema`, schema tests report `SKIP`) |
| DDS census (`dds_census.py`, `dds_census_tests.py`, `dds_metadata_tests.py`) | `numpy` |
| Content inventory gate (`content_inventory_gate.py`, `content_inventory_tests.py`) | `Pillow` (image checks) and `jsonschema` (row schema validation) |
| Full `npm run test:tools` | `numpy`, `Pillow` and `jsonschema`, plus `$BEA_GAME/data/worldheaders.dat` (or default Steam install) for `worldheaders_decode.py --self-test` |

In a virtual environment:

```bash
python3 -m venv local-data/venv
. local-data/venv/bin/activate
python -m pip install numpy Pillow jsonschema
```

## Documentation integrity

- [`md_link_check.py`](md_link_check.py): validates every local Markdown path and heading anchor across tracked files (`--self-test` and `--check-only`).
- [`md_reachability_check.py`](md_reachability_check.py): offline reachability diagnostic from `CLAUDE.md`, `AGENTS.md` and `README.MD` (optional; not part of `npm run test:docs`).
- [`doc_header_check.py`](doc_header_check.py): enforces the header contract in [`DOCUMENTATION.md`](../DOCUMENTATION.md) (`Status:`, `Last updated:` / `Date:`, `Summary:` / `Verdict:`, plus `Evidence:` and `Specimen:` on findings). [`doc_header_backlog.txt`](doc_header_backlog.txt) sits at zero entries and must remain empty.

## Payload and output safety

- [`public_allowlist_safety_check.py`](public_allowlist_safety_check.py): rejects tracked retail binaries/assets, generated catalogues (via the generated-retail-derived JSON marker), secrets, debugger transcripts, quoted retail byte runs, unreviewed long hex strings and private path markers across tracked files and `references/` submodules, while preserving the two reviewed SHA-256 fixtures (`tests_shared/fixtures/gold_career_save.bin` and `references/AYAResourceExtractor/BoxWithTextures.fbx`). Reviewed text exceptions fail as stale if their target text is removed.
- [`safe_generated_output.py`](safe_generated_output.py) ([tests](safe_generated_output_tests.py)): POSIX descriptor-relative no-follow publication helper behind Toolkit writers (`aya_archive_inventory.py`, `aya_cross_platform_compare.py`, `aya_texture_fidelity_census.py`, `cmsh_animation_usage_census.py`, `cmsh_static_preview.py`, `content_catalog.py`, `content_inventory.py`, `export_asset_catalog.py`, `export_language_corpus.py`, `export_video_manifest.py`, `world_mod_stage.py`). Refuses symlinks, hard links, existing targets and destinations overlapping a protected game installation. Note: directory-identity re-checks detect concurrent moves rather than locking the parent directory, so do not aim writers at directories another process can rename.

## Content catalogue

[`content_catalog.py`](content_catalog.py) builds a local JSON Content Catalogue from a selected PC installation (`manifest.json`, `survey.json`, `coverage.json`, `assets.jsonl`), conforming to [`content_catalog.schema.json`](content_catalog.schema.json). Its authored tests require no retail files; the generator and retail gate read your lawfully obtained game installation without modifying it:

```bash
python3 -B tools/content_catalog_tests.py
python3 -B tools/imposter_records_tests.py
python3 -B tools/content_catalog.py --game /path/to/game --out local-data/content-catalog
python3 -B tools/content_catalog_gate.py --game /path/to/game
```

Optional `--decomp /path/to/onslaught-decomp` adds literal string-lookup joins from a public [onslaught-decomp](https://github.com/dlprentice/onslaught-decomp) checkout. Output is accepted only under ignored `local-data/` and carries the generated-retail-derived JSON marker so `public_allowlist_safety_check.py` refuses any accidental commit.

Key catalogue capabilities:

- **Loose & packed textures:** records per-mip encoded-byte SHA-256 and raw DDS header fields (`dds_census.py`), plus packed archive `TEXT`, imposter, font and goodie texture descriptors (`aya_texture_fidelity_census.py`). Sets `upscale.premultipliedAlpha` per Direct3D DXT2/4 vs DXT3/5 specification without prescribing automatic conversion.
- **Meshes, animations & hierarchies:** reads loose and embedded CMSH meshes (`cmsh_static_preview.py`, `cmsh_animation_usage_census.py`, `model_transform_catalog.py`), preserving `CMSP`/`MESP` hashes, stored `BBOX` bounds, 128-byte `TEXB` texture-slot names (`utf8-decoded`, `empty`, `unterminated`, `invalid-utf8`), `CAMD` animation offsets and `nestedMeshDetails`.
- **Imposter records (`imposter_records.py`, [tests](imposter_records_tests.py)):** parses framed `IMPT` / `CIMP` / `IMPS` / `VIEW` imposter records, validates view rectangles and joins `imposter-of-mesh` and `uses-texture` relationships within the owning archive, keeping ambiguous duplicate mesh IDs unresolved.
- **Levels, world bodies & scripts:** decodes `WRES`, `ERES`, `SURF`, `SSHD`, `VSDS`, `PMIB` and `DMKR` (`world_resources_decode.py`), models `WORLD.mNamedThings` (`named_things.py`), joins `worldheaders.dat` (`worldheaders_decode.py`), `battle engine configurations.dat` and `sounds.sfx` (`game_tables_decode.py`), XAP sample banks (`xap_bank_walk.py`), particle sets (`particle_set_walk.py`), compiled physics scripts (`physics_values_decode.py`) and language tables (`language_dat_decode.py`).
- **Retail gate (`content_catalog_gate.py`):** independently verifies every level archive's `WRES`/`WDAT`, world bodies, named-thing lookup agreement (`find` vs `find_by_walk`), resource chunk exact consumption (`ERES`, `SURF`, `SSHD`, `VSDS`, `PMIB`, `DMKR`), configurations, `sounds.sfx`, physics joins and imposter records. Pass `--table` for a per-level summary (retail-derived; keep private).

### Catalogue source-file coverage

`coverage.json` separates parser availability from what the selected input actually yielded: `sourceFileCoverage` counts regular input files and stored byte sizes by family, files represented by at least one catalogue record and files targeted by at least one explicit resolved relationship. Whole stored file sizes are not decoded-byte counts; see [Content inventory](#content-inventory) for byte-level accounting.

## Content inventory

[`content_inventory.py`](content_inventory.py) accounts for every byte of a selected PC installation (`manifest.json`, `coverage.json`, `files.jsonl`, `items.jsonl`, `asset-metadata.jsonl`, `records.jsonl`) conforming to [`content_inventory.schema.json`](content_inventory.schema.json). Every byte is classified as **decoded** (consumed in loader/spec order with exact closure), **referenced** (framed by a record or header but unread) or **unknown** (any gap is unknown by construction).

```bash
python3 -B tools/content_inventory_tests.py
python3 -B tools/content_inventory.py --game /path/to/game [--decomp /path/to/onslaught-decomp] --out local-data/content-inventory
python3 -B tools/content_inventory_gate.py --game /path/to/game --inventory local-data/content-inventory
```

- Compressed media payloads (Ogg Vorbis audio packets, Bink 1 frames/audio tracks, JPEG scans) count as decoded only when an independent media decoder (FFmpeg on `PATH` or `--media-decoder`) decodes every stream with matching frame/sample counts; `coverage.json` always reports the headline decoded share both with and without FFmpeg.
- `asset-metadata.jsonl` emits one row per texture, image, model, animation, sound and film with exact container coordinates, SHA-256, dimensions, pixel formats, mip counts, alpha, audio channels/rates/durations and usage summaries as an offline batch input list.
- [`content_inventory_gate.py`](content_inventory_gate.py) independently walks and hashes the installation, re-inflates every AYA archive with zlib, walks archive chunks, validates images with Pillow, composes cached mesh frames (`cmsh_grammar_walk.py`), verifies every `asset-metadata.jsonl` field directly against asset bytes and checks every row against [`content_inventory.schema.json`](content_inventory.schema.json).

## World, terrain, MSL & mod-staging tools

All world and modding tools read local inputs without modifying the installation. Format specs live in [onslaught-preservation](https://github.com/dlprentice/onslaught-preservation/blob/main/formats/README.md).

- [`world_resources_decode.py`](world_resources_decode.py): pure decoder for level archive payloads (`WRES`, `ERES`, `SURF`, `SSHD`, `VSDS`, `PMIB`, `DMKR`) in PC loader order, refusing unread trailing bytes.
- [`world_resources_encode.py`](world_resources_encode.py) ([tests](world_resources_encode_tests.py)): byte-exact inverse encoder for `WRES` world bodies (`verify --game DIR`, `extract --stdout`, `encode MODEL.json --stdout`, `stage --stdout`, `stage --as-mod --out PARENT --id ID --name TEXT`).
- [`world_mod_stage.py`](world_mod_stage.py) ([tests](world_mod_stage_tests.py)): packages edited world bodies into an Onslaught CE mod folder (`PARENT/ID/mod.json` plus `data/worlds/worldNNN.wrd`) enforcing CE's loader bounds and publishing via `safe_generated_output.py`.
- [`world_thing_index.py`](world_thing_index.py) ([tests](world_thing_index_tests.py)): read-only paged listing of serialized thing ordinals, stored names, definitions, float32 positions and baseline SHA-256 from a `.wrd` body.
- [`world_edit_preview.py`](world_edit_preview.py) ([tests](world_edit_preview_tests.py)): read-only structural diff and compiled-script check comparing an edited world JSON model against its baseline `.wrd` body.
- [`world_edit_move.py`](world_edit_move.py) ([tests](world_edit_move_tests.py)): two-step hash-pinned CLI workflow to preview and emit a single existing thing's position edit to stdout.
- [`named_things.py`](named_things.py) ([tests](named_things_tests.py)): source-modelled predictor for `WORLD.mNamedThings` and `CWorld::FindThingByName` lookups across base and real worlds.
- [`heightfield_lookup.py`](heightfield_lookup.py) ([tests](heightfield_lookup_tests.py)): evaluates terrain height at `(X, Y)` from an archive's `ERES` chunk matching `CHeightField::Collide` (`0x0047eb80`) fixed-point bilinear math.
- [`msl_compile.py`](msl_compile.py) ([tests](msl_compile_tests.py)) and [`msl_gate.py`](msl_gate.py): reference Mission Script Language (`.msl`) compiler producing world-body compiled script records, plus its retail install comparison gate.
- [`mission_script_inspect.py`](mission_script_inspect.py) ([tests](mission_script_inspect_tests.py)): bounded read-only structural inspector for a single compiled mission-script record (never executes scripts).

## Assets and formats

Format documentation for these decoders lives in [onslaught-preservation/formats](https://github.com/dlprentice/onslaught-preservation/blob/main/formats/README.md).

- **AYA archives:** [`aya_archive_inventory.py`](aya_archive_inventory.py) ([tests](aya_archive_inventory_tests.py)), [`aya_corpus_chunk_inventory.py`](aya_corpus_chunk_inventory.py), [`aya_cross_platform_compare.py`](aya_cross_platform_compare.py), [`aya_texture_fidelity_census.py`](aya_texture_fidelity_census.py) ([tests](aya_texture_fidelity_census_tests.py)). All shared readers validate regular single-link files without following symlinks and enforce explicit byte/member bounds.
- **CMSH meshes & animations:** [`cmsh_static_preview.py`](cmsh_static_preview.py) ([tests](cmsh_static_preview_tests.py)) (bounded CMSH parser and OBJ preview emitter), [`cmsh_grammar_walk.py`](cmsh_grammar_walk.py) ([tests](cmsh_grammar_walk_tests.py)) (complete CMSH grammar walker and `--compose` animation key verification against [cmsh-fields.md](https://github.com/dlprentice/onslaught-preservation/blob/main/formats/cmsh-fields.md) and [cmsh-animation-keys.md](https://github.com/dlprentice/onslaught-preservation/blob/main/formats/cmsh-animation-keys.md)), [`cmsh_animation_usage_census.py`](cmsh_animation_usage_census.py) ([tests](cmsh_animation_usage_census_tests.py)), [`model_transform_catalog.py`](model_transform_catalog.py) ([schemas](model_transform_catalog.schema.json), [v2](model_transform_catalog.v2.schema.json), [tests](model_transform_catalog_tests.py)), [`level_asset_xref.py`](level_asset_xref.py) ([tests](level_asset_xref_tests.py)).
- **Textures, goodies & sound banks:** [`dds_census.py`](dds_census.py) ([tests](dds_census_tests.py), [metadata tests](dds_metadata_tests.py)), [`goodie_resource_walk.py`](goodie_resource_walk.py) ([tests](goodie_resource_walk_tests.py)), [`xap_bank_walk.py`](xap_bank_walk.py) ([tests](xap_bank_walk_tests.py)).
- **Game tables, physics, particles, media & saves:** [`battle_engine_config_decode.py`](battle_engine_config_decode.py) ([tests](battle_engine_config_decode_tests.py), layout pin in [`format_contracts/battle-engine-config-layout.tsv`](format_contracts/README.md)), [`game_tables_decode.py`](game_tables_decode.py) ([tests](game_tables_decode_tests.py)), [`worldheaders_decode.py`](worldheaders_decode.py) ([tests](worldheaders_decode_tests.py)), [`particle_set_walk.py`](particle_set_walk.py) ([tests](particle_set_walk_tests.py)), [`physics_values_decode.py`](physics_values_decode.py) ([tests](physics_values_decode_tests.py)), [`media_readers.py`](media_readers.py) ([tests](media_readers_tests.py)), [`language_dat_decode.py`](language_dat_decode.py), [`options_entries_decode.py`](options_entries_decode.py).
- **Local catalog & corpus exporters:** [`export_asset_catalog.py`](export_asset_catalog.py) ([tests](export_asset_catalog_tests.py)), [`export_language_corpus.py`](export_language_corpus.py), [`export_video_manifest.py`](export_video_manifest.py).
- **Reference fixtures:** [`godot_reader_fixtures/`](godot_reader_fixtures/README.md) holds five C# reader files mirrored from `onslaught-godot` and parsed as plain text by `particle_set_walk_tests.py` and `physics_values_decode_tests.py`; [`format_contracts/`](format_contracts/README.md) holds `battle-engine-config-layout.tsv` mirrored from `onslaught-preservation`.

Generated catalogues, inventories, conversions and reports remain private local outputs in ignored `local-data/` and must never be committed.
