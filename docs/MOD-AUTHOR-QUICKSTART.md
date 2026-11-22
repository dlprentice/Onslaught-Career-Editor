# Mod Author Quickstart

Status: active — mod-authoring guide for the Onslaught Modding & Content Toolkit
Last updated: 2026-11-22
Summary: end-to-end guide for discovering replaceable game targets with the JSON Content Catalogue, scaffolding a schema-1 Onslaught CE mod with `tools/mod_starter.py`, validating it against `bea --check-mods`, and extending engine behavior via Onslaught CE's `ce_hooks.h` v2.0.
Evidence: SOURCE — verified against `tools/mod_starter.py`, `tools/mod_starter_tests.py`, `tools/world_mod_stage.py`, `tools/content_catalog.py`, and Onslaught CE's `mods.cpp` schema-1 loader contract.

This guide walks through creating, validating, and enabling an **Onslaught CE** schema-1 mod using your own lawfully obtained PC copy of *Battle Engine Aquila* and the Toolkit's stdlib-only Python tools.

> **Never modify your retail installation.** All Toolkit tools treat `--game` / `--game-dir` as read-only and refuse to write into a game directory or overwrite an existing mod folder. Never commit retail game files or generated catalogues into Git.

## 1. Build Your Local JSON Content Catalogue

First, survey your local PC installation into the ignored `local-data/` directory using [`tools/content_catalog.py`](../tools/content_catalog.py):

```bash
python3 -B tools/content_catalog.py --game /path/to/game --out local-data/content-catalog
```

This emits `manifest.json`, `survey.json`, `coverage.json`, and `assets.jsonl` under `local-data/content-catalog/` covering textures, meshes, levels, world bodies, audio banks, language tables, and archives.

## 2. Discover Valid Replaceable Targets

Query your local catalogue with [`tools/mod_starter.py`](../tools/mod_starter.py) to list valid game-relative `data/...` target paths and level world IDs (`data/worlds/worldNNN.wrd`):

```bash
# List replaceable texture targets matching "be_texa"
python3 -B tools/mod_starter.py \
  --catalog local-data/content-catalog \
  --list-targets --type texture --filter be_texa

# List catalogued levels and their added-world paths (data/worlds/worldNNN.wrd)
python3 -B tools/mod_starter.py \
  --catalog local-data/content-catalog \
  --list-targets --type world
```

Supported `--type` filters are `all`, `texture`, `mesh`, `world`, `archive`, `audio`, `video`, and `table`. Non-`data/` install entries (executables, manuals, saves) are automatically excluded because Onslaught CE's loader admits only game-relative `data/...` paths.

## 3. Scaffold a Schema-1 Starter Mod

An Onslaught CE schema-1 mod lives in `<user-dir>/mods/<mod-id>/` and contains:

- `mod.json` — strict ASCII JSON (`schema: 1`, `id`, `name`, `version`, optional `author`, `description`, `ce_min`, `ce_max`, and `files` listing each file's `path`, exact byte `size`, and lowercase SHA-256 digest).
- `data/...` — the replacement files (or added `data/worlds/worldNNN.wrd` world bodies).

Use `tools/mod_starter.py` to generate a verified starter folder:

```bash
# Option A: scaffold from a safe replaceable file in your own game folder
python3 -B tools/mod_starter.py \
  --out local-data/starter-mods \
  --id ce-example-starter \
  --name "CE Example Starter" \
  --author "Your Name" \
  --description "Starter mod verified with Onslaught CE." \
  --game-dir /path/to/game \
  --target data/language/english.dat

# Option B: extract a level's RLWD world body (from WRES/WRLD) into an editable worldNNN.wrd mod
python3 -B tools/mod_starter.py \
  --out local-data/starter-mods \
  --id my-level-100 \
  --name "Level 100 Starter" \
  --game-dir /path/to/game \
  --world-level 100

# Option C: self-contained world fixture (no retail install needed; for schema testing)
python3 -B tools/mod_starter.py \
  --out local-data/starter-mods \
  --id ce-fixture-starter \
  --world-level 100 \
  --world-fixture
```

For structured world-body edits (moving units, updating mission scripts, and byte-exact re-encoding), pair [`tools/world_resources_encode.py`](../tools/world_resources_encode.py) and [`tools/world_mod_stage.py`](../tools/world_mod_stage.py) with [`tools/msl_compile.py`](../tools/msl_compile.py).

## 4. Validate Against Onslaught CE (`bea --check-mods`)

Before launching the game, validate your mod directly with Onslaught CE's built binary. `mod_starter.py --validate-with` runs `bea --check-mods <mod-id>` in an isolated headless environment and requires exit status `0` and `result: 1 passed, 0 refused`:

```bash
python3 -B tools/mod_starter.py \
  --out local-data/starter-mods \
  --id ce-example-starter \
  --game-dir /path/to/game \
  --validate-with /path/to/onslaught-ce/bea
```

You can also invoke Onslaught CE directly after copying `<mod-id>/` into your CE user folder's `mods/` directory:

```bash
bea --check-mods ce-example-starter
```

Every time you edit a payload file inside `data/...`, regenerate `mod.json` so its `size` and `sha256` entries match the updated bytes; Onslaught CE refuses any mod whose on-disk file diverges from `mod.json`.

## 5. Enable in Onslaught CE

1. Copy `<out>/<mod-id>/` into `<CE user folder>/mods/<mod-id>/`.
2. Either enable the in-game **Mods** menu (`mods_menu=1` in `ce.ini`, then open **Onslaught CE > Mods** to toggle and order mods) or add `mods=ce-example-starter` directly in `ce.ini`.
3. Restart Onslaught CE so the active mod list takes effect at start-up.

Note that Onslaught CE automatically disables mods during faithful replays, session recordings, probes, virtual-clock runs, and network sessions so deterministic verification stays unperturbed.

## 6. Going Deeper: Engine Extensions (`ce_hooks.h` v2.0)

Asset and world mods run through the schema-1 mod folder without recompiling the engine. If you want to add new C++ gameplay mechanics, HUD overlays, camera overrides, or custom spawn logic inside Onslaught CE itself, see the [Onslaught CE repository](https://github.com/dlprentice/onslaught-ce) (`docs/mod-author-quickstart.md` and `docs/ce-hooks-api.md`) for the 21-point `ce_hooks.h` v2.0 extension API, `SIM` vs `RENDER` write-fences, and `CE_GATE_LAYER` neutrality rules.
