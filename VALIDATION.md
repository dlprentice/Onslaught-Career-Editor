# Validation

Status: active — the gate-selection table
Last updated: 2026-11-21 (updated for the repurposed Onslaught Modding & Content Toolkit; retired Companion and rebuild gates removed)
Summary: choosing the smallest local check that proves the contract you changed. Root [`package.json`](package.json) owns the npm shortcuts.

Validation is proportional to the contract changed. The commands below are options, not a required sequence.

Documentation, safety and authored tool tests use the [public prerequisites](README.MD#setup-and-checks) (Git, Python 3.12+ with `numpy`, `Pillow` and `jsonschema`, and initialized reference submodules for the full safety scan). No retail game installation, Godot or .NET SDK is required for authored tests. Retail verification gates require your own lawfully obtained installation of *Battle Engine Aquila*.

| Change | Focused evidence |
| --- | --- |
| Documentation or deletion only | `git diff --check`, `npm run test:docs` (link check with self-test, then doc header check with self-test), and optionally `python3 -B tools/md_reachability_check.py` when adding or removing document routes |
| A new or edited tracked `.md` header | `npm run test:doc-headers` (also inside `npm run test:docs`). Contract: [`DOCUMENTATION.md`](DOCUMENTATION.md). `tools/doc_header_backlog.txt` holds 0 entries and must stay empty |
| Public payload, secret, retail-byte or private-path boundary | `npm run test:safety` (`public_allowlist_safety_check.py --self-test` and `--include-submodules`). Rejects tracked retail payloads, generated catalogues, secrets, quoted retail byte runs, long hex strings and private path markers. Reviewed exceptions live in `tools/public_allowlist_safety_check.py`, and stale allowances fail |
| Content Catalogue (`content_catalog*`, `imposter_records*` and decoders) | `npm run test:catalog` (`python3 -B tools/content_catalog_tests.py`) and `python3 -B tools/imposter_records_tests.py` (authored install, no game files). Retail verification: `python3 -B tools/content_catalog_gate.py --game /path/to/game` (read-only) |
| Content Inventory (`content_inventory*`, `media_readers*`, walkers) | `npm run test:inventory` (`python3 -B tools/content_inventory_tests.py`, authored install). Retail verification: `python3 -B tools/content_inventory.py --game /path/to/game --out local-data/content-inventory` followed by `python3 -B tools/content_inventory_gate.py --game /path/to/game --inventory local-data/content-inventory` |
| World codec, mod stager, MSL compiler or format decoders | The affected `python3 -B tools/<name>_tests.py`, plus `npm run test:tools` (`run_tool_tests.py --self-test` and every registered suite). `particle_set_walk_tests.py` and `physics_values_decode_tests.py` verify their tables against `tools/godot_reader_fixtures/`; `battle_engine_config_decode_tests.py` pins `tools/format_contracts/battle-engine-config-layout.tsv`. Retail verification for MSL: `python3 -B tools/msl_gate.py --game /path/to/game` |
| Full Toolkit verification | `npm test` (`npm run test:safety && npm run test:docs && npm run test:tools`) |

Notes on `npm run test:tools`:

- `run_tool_tests.py --self-test` fails if any `*_tests.py` (or `test_*.py`) file in the repository is neither registered in `SUITES` nor listed with a reason in `NOT_IN_THIS_GATE`, so a new test suite cannot silently fall outside the gate.
- `worldheaders_decode.py --self-test` reads `$BEA_GAME/data/worldheaders.dat` (or the default Steam install path); without a local install, run individual authored `*_tests.py` suites (such as `worldheaders_decode_tests.py`, `content_catalog_tests.py` and `content_inventory_tests.py`) instead.
- Check individual suite output for any `SKIP` lines (for example when `jsonschema` is not installed); never cite a skipped check as a pass.
- Game documentation changes belong in [onslaught-preservation](https://github.com/dlprentice/onslaught-preservation); native port changes belong in [Onslaught CE](https://github.com/dlprentice/onslaught-ce); Godot rebuild changes belong in [onslaught-godot](https://github.com/dlprentice/onslaught-godot).
