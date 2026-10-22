# Tools

Status: active — the reusable support surface, not a product lane
Last updated: 2026-10-21 (the rebuild is active, not parked)
Summary: what each tool in `tools/` is for, and which of them are gates.

`tools/` supports the companion, the game documentation and the active rebuild through guarded extraction,
format inspection, capture analysis and focused checks. The Ghidra scripts, cohort specs, campaign/authority tools
and the Windows TTD/cdb/PowerShell runtime-probe lab moved on 2026-10-15 to the private repository
`dlprentice/onslaught-re-archive`; the WinUI packaging tools were removed.

Root [`package.json`](../package.json) is the command authority. On Omarchy,
start with:

```bash
npm run test:docs
npm run test:safety
```

`npm test` runs the companion's contract and tooling checks without opening a window.
Current root commands and reusable examples use `python` and
forward-slash paths on both hosts. Dated receipts and historical evidence may
retain the literal Windows commands and drive letters that produced them; a
tool can also have an explicitly documented Windows evidence dependency.

`npm run test:tools` runs every registered suite; prefer an affected suite for a focused change. A suite that
needs a Windows host would be reported as skipped on Linux, never as a pass; none is registered now.

## Product and release

- `godot_host.py` supplies pinned installed-engine discovery, locked bundled-SDK
  restore/build and owned-process cleanup for both Godot lanes; `companion_godot.py`
  builds and runs the MIT companion, and `rebuild/tools/first_flight.py` adds retail
  preparation and rebuild runtime modes. The shared helper imports no GPL or retail code.
Use [`VALIDATION.md`](../VALIDATION.md) to select checks. These tools do not
publish, sign, or install anything by themselves.

## Documentation integrity

- `md_link_check.py` validates local link **targets**; `md_reachability_check.py`
  answers the different question of whether a document is linked from anywhere.
- `doc_header_check.py` enforces the header contract in
  [`DOCUMENTATION.md`](../DOCUMENTATION.md) — Status, Date, Verdict/Summary
  everywhere, plus Evidence and Specimen on findings. It rejects a byte claim
  that names no specimen, and a specimen that cites an installed Steam path instead
  of the preserved measurement input. `doc_header_backlog.txt` holds the pre-standard documents and
  may only shrink; `--self-test` exercises the rules without a repository, and
  exit `2` means the check could not run rather than that it found nothing.

## Payload and output safety

- `public_allowlist_safety_check.py` rejects tracked game/runtime payloads,
  build output, raw debugger scripts, common secret patterns, and unsafe
  submodule payloads while preserving the two reviewed fixture exceptions.
- `safe_generated_output.py` provides guarded local publication for Python
  exporters.

## Assets and formats

- `aya_archive_inventory.py`, `aya_cross_platform_compare.py`, and
  `aya_texture_fidelity_census.py` provide fail-closed AYA inventory,
  cross-platform pairing, and stored-texture geometry/block comparison.
- `cmsh_animation_usage_census.py` performs a read-only, optionally
  mirror-hash-verified join across loose CMSH pose/skeleton lanes, numeric-LVLR
  `MESH` membership, and authored MSL animation calls. Its JSON output is
  restricted to ignored `local-lab` or `.artifacts` paths.
- `export_game_assets.py`, `export_asset_catalog.py`,
  `export_language_corpus.py`, and `export_video_manifest.py` operate on
  user-supplied local inputs and write to a separate local output root.
- `rebuild/tools/materialize_retail_assets.py` verifies one supported retail
  installation and reproduces the exact current rebuild inputs at ignored
  runtime paths. Existing rebuild build/run/smoke commands invoke it directly.
- `BeaAssetExportHarness/` is the bounded C# AYA/FBX export bridge.
- `language_dat_decode.py`, `options_entries_decode.py`,
  `cheat_table_decode.py`, and `cardid_preset_manager.py` are focused format
  inspection utilities.

Generated catalogs, retail assets, conversions, and bulk exports remain ignored
local material. Source retains only the bounded recipe and implementation.
Passing an output safety test proves neither format completeness nor visual
fidelity.

## Parity measurement

- `compare_capture.py` compares one reconstruction frame against one retail
  frame per region. It refuses mismatched sizes rather than resampling.
- `score_frontend_capture.py` pairs whole capture runs against the retail reference by offset. It is a
  **gate**: `rebuild/tools/first_flight.py capture` folds its verdict into the
  capture's `status`, so a frontend regression fails the capture. Its thresholds live in
  `rebuild/tools/frontend-parity-plan.json` and are regression ceilings, not
  parity claims. The plan stores each measured value plus the single
  `marginPp: 2.0` regression allowance used to derive its ceiling.

A run that can score nothing reports `UNSCORED`, never `PASS`. Reference frames
are retail-derived and live under ignored local paths, so a fresh clone scores
nothing and must say so.

Review is optional and question-driven under
[REVIEW-PROTOCOL.md](../reverse-engineering/REVIEW-PROTOCOL.md).

## Format and analysis instruments

Each reads only local inputs the user supplies (an installation, a capture, a pinned specimen) and writes, when it
writes at all, to ignored local paths. Their findings are documented under
[`reverse-engineering/`](../reverse-engineering/RE-INDEX.md).

- Formats and corpora: `aya_corpus_chunk_inventory.py` (corpus-wide AYA chunk inventory),
  `aya_extractor_source_audit.py` (source/history audit of the pinned AYAResourceExtractor fork),
  `battle_engine_config_decode.py` (reads and re-encodes `battle engine configurations.dat` in memory),
  `worldheaders_decode.py` (decodes `data/worldheaders.dat` byte-exactly; its self-test needs the retail file),
  `heightfield_node_array_probe.py` (checks whether any shipped heightfield header fills the per-node array).
- Meshes: `cmsh_grammar_walk.py` walks PC CMSH streams with the grammar in
  [`asset-formats/cmsh-fields.md`](../reverse-engineering/asset-formats/cmsh-fields.md) and proves it accounts for
  every byte (with `--compose`, it also checks every cached frame against the composed keys);
  `dds_census.py` checks every installed texture's DDS header against its stored mip chain, classifies its alpha and, with `--mips`, checks every lower level
  (see [`asset-formats/dds-texture.md`](../reverse-engineering/asset-formats/dds-texture.md));
  `goodie_resource_walk.py` walks the Goodie archives and resolves what each Goodie shows (see
  [`asset-formats/goodie-resources.md`](../reverse-engineering/asset-formats/goodie-resources.md));
  `xap_bank_walk.py` walks and decodes the sound banks (see
  [`asset-formats/xap-sample-bank.md`](../reverse-engineering/asset-formats/xap-sample-bank.md));
  `gltf_pose_check.py` evaluates the companion's glTF exports by the glTF rules and compares every node of every
  animation at every sample with the game's composition (it needs numpy and the exports a
  `Development/AssetCheck.cs` run keeps with `ASSET_KEEP=all`); `cmsh_cpos_cori_verify.py`, `cmsh_track_probe.py`, `cmsh_matrix_normal_contract.py` and
  `cmsh_skinning_contract.py` settle position/orientation tracks, per-part tracks and the matrix-palette skinning
  and normal contracts; `world_mesh_normal_probe.py` carries static-world OBJ bytes through both lighting chains.
- Executable reading: `pe_read_va.py` reads a PE virtual address; `call_xref_scan.py` finds every direct
  CALL/JMP rel32 reference to a VA (verify each hit by disassembling it).
- Capture analysis (retail frame against a reconstruction frame): `frame_alignment_probe.py`,
  `region_rgb_probe.py`, `cockpit_edge_profile.py`, `cockpit_intersection_mask_probe.py`,
  `cockpit_light_state_probe.py`, `sky_source_gain_probe.py`, `frontend_arc_bracket_fit.py` and the terrain
  probes (`terrain_ambient_light_factor_probe.py`, `terrain_gain_dispersion_probe.py`,
  `terrain_macro_inversion_probe.py`, `terrain_shade_interpolation_probe.py`,
  `terrain_spatial_structure_probe.py`, `terrain_sun_colour_candidates.py`, `terrain_transfer_probe.py`).
- Repository checks: `check_installed_game_claims.py` bans standing promises about the installed game;
  `check_registered_screenshots.py` bounds tracked pictures of the game; `check_region_overlap.py` checks capture
  region plans; `run_tool_tests.py` runs the registered suites.
