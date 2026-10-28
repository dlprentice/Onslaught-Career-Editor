# Tools

Status: active — the reusable support surface, not a product lane
Last updated: 2026-10-28 (per-mip DDS identities; world body encoder and loose-world staging; earlier: content catalogue phase 3: world things, paths, compiled scripts, terrain payloads; earlier: content catalogue, single-archive texture catalog, bounded level, texture and mission-script metadata)
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
  builds and runs the companion, and `rebuild/tools/first_flight.py` adds retail
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
  cross-platform pairing, and stored-texture geometry/block comparison. The
  texture census also exposes a bounded `serialized_texture_metadata` API for
  selected held TEXT payloads; external PC mip contents and runtime selection
  remain unknown.
- `mission_script_inspect.py` inspects one explicitly selected, hash-bound
  compiled-script record or range. Its bounded output describes stored
  structure and unknowns; it does not execute scripts or edit missions.
- `cmsh_animation_usage_census.py` performs a read-only, optionally
  mirror-hash-verified join across loose CMSH pose/skeleton lanes, numeric-LVLR
  `MESH` membership, and authored MSL animation calls. Its JSON output is
  restricted to ignored `local-lab` or `.artifacts` paths. It distinguishes
  the loose mesh's direct `PMS2` child from the embedded resource's
  `PMSH`/`PMS2` plus 309-byte header, and keeps a mismatched or unknown reader
  context unresolved. A recognized child is a serialized next-in-chain; it is
  not proof that a particular resource record loads it at runtime. The renderer
  can follow at most two links from a root; deeper links are labelled a chain,
  without a claim that the renderer selects them.
- `content_catalog.py` surveys every file of a selected retail install (family, count, size, the game function that
  reads it, and whether a repository parser already reads it) and writes the content catalogue: one JSON record per
  texture file, texture record (level, imposter, font and goodie), mesh, animation mode, level, world thing
  (placements of units, squads and features; markers for waypoints, spawners, triggers, starts, spawn points and the
  other kinds), waypoint path, compiled mission script, definition, goodie, particle effect, sample, music and voice
  file, film, resource archive and script/text file, with container coordinates, SHA-256, format metadata, an upscale
  section, provenance and, for meshes and textures, a usage summary ([schema](content_catalog.schema.json)). Each
  admitted loose texture mip records the encoded bytes' SHA-256 and offset in the inflated DDS, so individual levels
  can be compared without exporting their pixels; unsupported or malformed textures have no admitted mip entries.
  `nestedMeshDetails` reports each immediate child's relationship, parse status, count and hash; an unknown count is
  `null` there and in `lodChildParts`, and nested descendants are available in the CMSH census. No relationship
  asserts runtime loading. If a root mesh is unparsed, its counts are `null` and its bounded refusal is reported;
  an unparsed emitter section likewise has an unknown emitter count. Animation source offsets identify their own
  36-byte `CAMD` records in the inflated container. An embedded mesh's `chunkPath` anchors the owning top-level
  `MESH` chunk rather than listing every wrapper; its offset comes from walking those wrappers, not searching bytes.
  `world_resources_decode.py` decodes the level payloads in their loaders' read order and refuses unread bytes: the
  `WRES` world bodies (`CWorld::LoadWorld`: header, compiled scripts, things, trees, influence map, waypoint paths,
  timings, occupancy), `ERES` (mixer mips, heightfield settings and samples, mixer map), `SURF` and `SSHD`; `LNDS`
  is skipped by the PC loader. Relationships (archive to mesh, texture record to its DDS file, mesh slot to texture
  record, imposter to mesh, placement to definition and mesh, thing to its compiled script and `.msl` source, path to
  its waypoints, script to the units, paths, scripts, text ids and thing names its literal call arguments name, level
  to the sky-cube, water and detail textures its map numbers build with `sprintf`, effect to texture, goodie to
  texture/mesh/film, voice file to its text line, code lookups with `--decomp`) are emitted only from a loader rule in
  the public decompilation or from the data, and each names that evidence; unresolved links stay explicit. The
  single-record `mission_script_inspect.py` is the independent check of the compiled-script reader. Output is accepted
  only below the ignored `local-data/`, and every generated file carries a marker that
  `public_allowlist_safety_check.py` refuses, as it refuses any tracked `local-data/` path.
  `world_resources_encode.py` is the decoder's inverse for world bodies: `read_world_model` keeps every field
  `CWorld::LoadWorld` reads (the regions it only skips as base64 blobs) and `write_world_body` writes them back, byte
  for byte on every retail body (`verify --game DIR`). `extract` writes a level's bodies as `worldNNN.wrd` plus an
  editable JSON model, `encode` turns an edited model back into a body, and `stage` builds an Onslaught CE user folder
  that loads a level's worlds from loose `data\worlds\worldNNN.wrd` files (`CWorld::Load`'s fallback) through a
  shadow copy of the level archive whose `WDAT` names no level. All writing commands require the selected game folder
  (`--game DIR`, or `BEA_GAME`) and a separate output location, and will not replace existing files or follow output
  symlinks. Multi-file operations can leave earlier new outputs when a later write fails: inspect those and choose a
  fresh output folder. Atomic no-replace publication currently fails closed on Windows; native Windows support needs
  validation. Each input archive is limited to 64 MiB compressed, 128 MiB inflated and 4096 members; each inflated
  member is limited to 1 MiB, matching the PC writer and default read buffer. These total limits are tool resource
  ceilings, not established maxima for the game format. Encoding checks binary layout but is not a mission, placement
  or gameplay safety validator.
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

The asset catalog can also inspect **one explicitly selected PC archive**. In
addition to the usual catalog manifest and output arguments, pass
`--archive-source-root <directory> --inspect-pc-text-archive <file>`; a relative
file path is relative to that directory. The options must appear together and
only once. This separate opt-in reads the selected regular, single-link file
under the explicit root, rejects path or parent replacement, and does no
discovery. When manifest-source inspection is also enabled, the archive cannot
be selected there as well. The caller selects the PC chunked-zlib profile; a name
alone does not establish the archive's platform.

The optional `pc_archive_texture_inspection` in `catalog.json` records the held
archive and inflated-stream hashes, then the ordinal, inflated payload offset,
length, hash and bounded metadata for each admitted top-level `TEXT` occurrence.
Repeated names and payloads remain separate occurrences; same-name groups include
only successfully parsed admitted records. Archive, record and aggregate mip
budgets can yield an explicit refusal or partial result, with omitted counts.
The report contains no raw archive, payload or pixel bytes. It does not join
these occurrences to loose DDS files, models or the manifest catalog, and does
not establish runtime selection or appearance. Generated reports remain private
local material. Archive inspection requires fresh catalog output filenames; its
atomic no-replace publication preserves any existing file, including a source
moved into an output name during the run. A concurrent collision can leave a
partial set of newly created reports; use a fresh output location to retry. This
path requires Linux `renameat2` no-replace support and fails closed without it.
Omitting the archive options leaves the existing catalog publication unchanged.

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
  `worldheaders_decode.py` (decodes `data/worldheaders.dat` byte-exactly; its
  `--metadata-json` option projects bounded level modes and optional
  configuration-name membership, not proof of playable multiplayer),
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
