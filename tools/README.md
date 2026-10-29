# Tools

Status: active — the reusable support surface, not a product lane
Last updated: 2026-10-29 (the tool-test gate's coverage and skips; TEXB texture-slot name identity; census v4 wording: the outer MESH name and the internal CMSH name are separate; earlier: read-only world-edit preview; stream-only world body and stage-bundle exports; per-part mesh bounds and identities; per-mip DDS identities; earlier: content catalogue phase 3: world things, paths, compiled scripts, terrain payloads; earlier: content catalogue, single-archive texture catalog, bounded level, texture and mission-script metadata)
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
cannot run here (one that needs a Windows host, none registered now, or the extractor source audit when a submodule it
compares with its pin is not initialised) is a named SKIP in the summary, never a pass and never a failure. The runner's
self-test fails for any `*_tests.py` file that is neither registered nor listed with a reason as run elsewhere or out of scope.

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
- `safe_generated_output.py` is the publication helper behind the Python writers `aya_archive_inventory.py`,
  `aya_cross_platform_compare.py`, `aya_texture_fidelity_census.py`, `cmsh_animation_usage_census.py`,
  `cmsh_skinning_contract.py`, `cmsh_matrix_normal_contract.py`, `content_catalog.py`, `export_asset_catalog.py`,
  `export_game_assets.py`, `export_language_corpus.py` and `export_video_manifest.py` (the frozen rebuild's
  `cmsh_static_preview.py` uses it too). On POSIX it creates and opens every output directory relative to a directory
  descriptor it already holds, so a symlink or directory put at the output path during a run cannot redirect a write;
  it writes an exclusive temporary name, publishes with a rename that follows no link, and refuses a destination that
  is a symlink, a hard link or not a regular file. It re-checks that every held directory is still named where it was
  found before each write, again just before the rename and once after publishing. That is detection, not a lock.
  **Moved-destination limit:** a directory renamed while a file is being published still receives that file, wherever
  the directory now is, and the writer refuses only afterwards; later writes are refused before anything is created.
  The check that the output root does not overlap a protected source (the game folder) is made once, when the root is
  opened, so the helper does not guarantee that a destination moved by another process during a run stays outside the
  game folder. Do not point a writer at an output root that another process can rename. The Windows path holds the
  directories with share modes meant to block a rename; no native Windows run has validated it here.

## Assets and formats

- `aya_archive_inventory.py`, `aya_cross_platform_compare.py`, and
  `aya_texture_fidelity_census.py` provide fail-closed AYA inventory,
  cross-platform pairing, and stored-texture geometry/block comparison. The
  texture census also exposes a bounded `serialized_texture_metadata` API for
  selected held TEXT payloads; external PC mip contents and runtime selection
  remain unknown.
  Their shared `read_held_archive` opens each input without blocking and without following a final symlink,
  accepts only a regular single-link file within the size cap, and compares the file's identity before and
  after the read. A name replaced by a FIFO, device or symlink between its check and its open is refused
  (`not_regular_input` or `reparse_input`) instead of waited on. It takes no lock: it detects replacement and
  metadata-visible change, not a rewrite that keeps the size and modification time.
  These writers publish through `safe_generated_output.py` and have its moved-destination limit (see `safe_generated_output.py` above).
- `mission_script_inspect.py` inspects one explicitly selected, hash-bound
  compiled-script record or range. Its bounded output describes stored
  structure and unknowns; it does not execute scripts or edit missions.
- `cmsh_animation_usage_census.py` performs a read-only, optionally
  mirror-hash-verified join across loose CMSH pose/skeleton lanes, numeric-LVLR
  `MESH` membership, and authored MSL animation calls. Census v4 reads mesh and
  part names from their bounded fields: an empty stored name stays empty, and
  an invalid or unterminated mesh name is null with a status. The shared parser
  instead refuses the whole mesh if a part name is invalid or unterminated.
  Name byte hashes describe terminated field contents; UTF-8 decoding does not
  establish the game's original display encoding. The anonymous embedded rows are
  the `MESH` chunks whose outer wrapper name is empty; each row's internal CMSH
  name is read from its own field and reported with its own status, so an empty
  outer name does not by itself mean an empty internal name. A malformed anonymous
  embedded mesh, such as one with an invalid part name, stops the whole census,
  because that path has no per-row refusal. A malformed loose mesh is recorded as
  unparsed in `modelMetadataCoverage` and has no part, frame-map, bone or camera rows
  at all, so those counts in `meshSummary` (`parts`, `meshesWithNontrivialFrameMaps`,
  `partsWithNontrivialFrameMaps`, `boneMeshes`, `boneCarriers`, `hfovMeshes`, `hfovParts`)
  cover parsed meshes only; its `meshes` count still includes every selected file.
  The model-metadata v1 record keeps its field names; its texture rows gain `nameStatus` and `nameBytesSha256`, and `name`
  is null where the 128-byte TEXB name field is unterminated or not UTF-8 (it was the parser's lossy decode). Census v4
  is an output format identifier; there is no separate machine-readable schema for the
  census. Its JSON output is restricted to ignored `local-lab` or `.artifacts` paths and is published with its moved-destination limit (see `safe_generated_output.py` above).
  It distinguishes
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
  `texture.ddsHeader` also retains the raw DDS flags, pitch or linear size, depth, declared mip count, caps, pixel-format
  flags, four stored FourCC bytes, bit count and RGBA masks. A non-null header on a malformed or unsupported record is
  only a readable declaration, not an admitted payload; `status` and `problems` remain the validation outcome. These
  values describe stored bytes and do not establish original art properties or rendered appearance. The loader builds
  expected filename suffixes from requested formats; a matching filename alone does not prove loading or the original
  art's bit depth, and its suffix need not match the stored format.
  `upscale.premultipliedAlpha` records the admitted DXT format's specified convention: DXT2/4 true, DXT3/5 false,
  DXT1 and RGB null; unsupported and malformed records also use null and get no treatment suggestions. This does not
  establish pixel association or render behavior, and no automatic un-premultiplication is prescribed. The format
  conventions are documented by [Microsoft](https://learn.microsoft.com/en-us/windows/win32/direct3d9/using-compressed-textures).
  Existing v1 catalogs may contain the older false values or treatment text; regenerate them to get these corrections.
  The legacy `repeats-beyond-0-1` label reports raw mesh UVs outside a 0.01 tolerance before transforms; it does not
  establish the sampler mode or visible repetition.
  A mesh's texture slots keep the stored 128-byte `TEXB` name as `name` with a `nameStatus` (`utf8-decoded`, `empty`,
  `unterminated` or `invalid-utf8`) and the SHA-256 of its bytes before the first NUL. An unterminated or non-UTF-8 field is
  an unknown name: its `name` is null, which is not the same as empty, and bytes after the first NUL are not part of the name.
  `requestedFormat` is inferred only for a terminated, readable name longer than 8 bytes, by `CMesh::FindTexture`'s rule (the
  suffix from byte 8: `A8` gives 4, `A4` gives 2, anything else 1; an empty suffix is a null texture name and nothing is looked
  up), and only such a name is joined to a descriptor. Every other slot's `uses-texture` relationship has no target and the
  status `unknown-name` (unreadable field), `empty-name` (known empty) or `unresolved` (a readable name shorter than 9 bytes),
  so it adds nothing to a texture's usage or tiling roll-up; `coverage.json` counts the statuses in `meshTextureNameStatus`.
  Existing v1 catalogs may hold a lossy name and an inferred format for such slots; regenerate them.
  Mesh hierarchy rows also retain each part's CMSP and MESP payload hashes and its stored BBOX center, half-extents,
  flag and radius, without exporting geometry. The flag is the stored value, not a validity check; non-finite numbers
  are `null`. These are part records before transforms, not world-space or animated bounds. The source is
  `CMeshPart::ReadBoundingBox` (`0x004b3180`); the record layout is in
  [cmsh-fields.md](../reverse-engineering/asset-formats/cmsh-fields.md#bounding-box-bbox-40-bytes).
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
  `public_allowlist_safety_check.py` refuses, as it refuses any tracked `local-data/` path. The catalogue is published with
  its moved-destination limit (see `safe_generated_output.py` above).
  `world_resources_encode.py` is the decoder's inverse for world bodies: `read_world_model` keeps every field
  `CWorld::LoadWorld` reads (the regions it only skips as base64 blobs). The tested PC installation's bodies round-trip
  byte for byte; `verify --game DIR` checks the level archives in the selected installation. This does not establish
  coverage of other builds or a playable editor. `extract --stdout` emits a JSON bundle containing a level's world
  bodies and editable models; `encode MODEL.json --stdout` emits raw world-body bytes; `stage --stdout` emits a JSON
  bundle containing the loose-world files and shadow archive that would be needed for a separate CE user folder.
  The bundle's `onslaught.world-bundle.v1` format maps relative names to byte counts, SHA-256 values and base64 data;
  those hashes describe the bundled bytes and do not verify any downstream file write.
  The name `stage` describes the bundle's purpose: this command does not create or stage those files.
  All three commands require the selected game folder (`--game DIR`, or `BEA_GAME`) and an explicit `--stdout`
  (`stage --as-mod`, below, is the exception). Legacy `--out`, positional output and `--user` paths are now refused
  before input reads: tool-managed publication cannot yet guarantee that a concurrently moved destination stays outside
  the selected game. This is a compatibility change. The caller controls stdout and any redirection; do not redirect it into a game installation or live user
  folder. The streams can contain material derived from the selected game and should be kept private. Windows stdout
  and archive-reading behavior have not been validated. Each input archive is limited to 64 MiB compressed, 128 MiB
  inflated and 4096 members; each inflated
  member is limited to 1 MiB, matching the PC writer and default read buffer. These total limits are tool resource
  ceilings, not established maxima for the game format. Encoding checks binary layout but is not a mission, placement
  or gameplay safety validator.
  `stage --as-mod --out PARENT --id ID --name TEXT [--world MODEL.json] [--base-world MODEL.json]` is the one command that
  writes files. It packages the edited world(s) as a CE mod folder `PARENT/ID` (`mod.json` plus `data/worlds/worldNNN.wrd`,
  the one kind of file a CE mod may add) through `world_mod_stage.py`, held to the loader's own limits (the id, the text
  lengths, the version format, at most 4 MiB per world file), so CE loads it with no hand editing. It is the step after
  `world_edit_move.py --emit-model`: pass that preview's `--baseline-sha256` and `--model-sha256` (and the `--base-*`
  pair for a base world) to pin the same two identities. It refuses a no-op edit, an edited world that names a base world
  the archive does not hold unless `--base-world` supplies it, a destination inside the selected game folder (or any game
  tree), a `--ce-min` that is later than `--ce-max` (compared number by number, so 1.10 is after 1.9; no released CE
  could load such a mod) and a folder that already holds anything. It writes through `safe_generated_output.py`: each file is published
  without replacing anything, the world files first and `mod.json` last, and the helper detects replacement rather than
  locking, so a folder moved by another process during the run is not guaranteed to stay outside the game folder (the
  limit every writer through that helper has). It does not validate placement, slots, scripts or saves, and it needs a CE
  build whose Mods section lists world files. CE loads mods on Linux only for now: Windows refuses them, and mods
  are off in replays, recordings, probes, virtual clocks, pilots and network sessions, so a staged mod cannot change
  any of those runs. `world_mod_stage_tests.py` checks the staged folder against an independent
  restatement of the loader's start-up rules on authored data only.
  `world_edit_preview.py BASELINE.wrd EDITED.json` is a read-only step before encoding or preparing a stage bundle. It reports input
  hashes, byte and field changes, changes to opaque groups and slot-sensitive structures, and bounded compiled-script
  inspection findings. It also identifies model fields the encoder would silently omit. An omitted field, truncated
  change list, changed opaque/compiled data, incomplete script inspection or structural script finding makes the command
  exit 1, including a pre-existing finding in an unchanged script. Thing count, an exact record-value permutation, per-ordinal
  non-position fields, target fields, waypoints, base level, map number and placement changes also require review;
  placement is reported separately as unvalidated, not as a detected invalid position. Ordinal comparisons cannot
  prove identity or detect every mixed move/reorder. Every changed encoded body also receives a general unvalidated
  change reason, and a zero exit is not a safety or playability certification.
  Field paths can include user-supplied JSON keys verbatim: inspect reports before sharing them. Optional
  `--baseline-sha256` and `--model-sha256` pin the selected snapshots. The CLI rejects `..` path components and
  symlinks. It writes no files; later encoding or bundle preparation is a separate command and is not automatically
  bound to this preview. Inspect the reported
  hashes before using its inputs. It does not check terrain placement, runtime slots, save compatibility or mission
  behavior, and does not execute a game or script. The CLI requires descriptor-relative no-follow file support;
  `preview_bytes` accepts immutable snapshots for integrations on other platforms. Windows CLI and physical play have
  not been validated.
  `world_thing_index.py WORLD.wrd --stdout` lists a page of serialized thing ordinals, stored names, definitions,
  positions and the exact baseline SHA-256, without exposing the world or script bodies. Use `--start` and `--limit`
  for later pages (at most 128 rows each). A position shows its float32 bytes and finite value; a non-finite value is
  null with its bits retained. The source must decode and round-trip exactly. A row's ordinal is local to that
  selected body, not a runtime slot, a stable identity or proof the thing will spawn. Names use a byte-preserving
  Latin-1 mapping; the game's display encoding for non-ASCII bytes is not established. The selected-file CLI needs
  Linux `O_PATH` and `/proc/self/fd`, while `report_bytes` accepts already-owned bytes on other platforms. The
  report is private game/user-derived metadata. The tool opens no output files; shell redirection and its destination
  are the caller's responsibility. It does not identify the level, validate placement or check gameplay.
  `world_edit_move.py` adds a narrow, two-step editing workflow for **one existing thing's position**. First run
  `python tools/world_edit_move.py WORLD.wrd --thing ORDINAL --position X Y Z`; this reads one selected body and prints
  a structural preview without creating files. Use the index above to choose `ORDINAL` and pass its baseline hash as
  `--baseline-sha256` to pin this exact body. The `extract` command also provides a model whose `things` array can
  be inspected privately. That ordinal is a zero-based serialized record index, not a proven runtime slot
  or stable identity. Review the coordinates, input/model hashes and all preview findings. A zero exit means the
  operation completed, not that the edit is safe; every move is marked `reviewRequired`. The tool
  accepts finite float32 positions; a decimal that needs rounding is refused unless `--allow-rounding` is given, in
  which case the report shows the requested decimal, stored value and float32 bits. The existing position must also
  be finite. To emit the edited JSON model, repeat the same command with `--baseline-sha256 SHA`, `--model-sha256 SHA`,
  `--emit-model` and `--acknowledge-unvalidated`, using the hashes from the preview. This emits the model to stdout;
  the tool has no output-file option and does not create files. **Redirection and subsequent file handling are outside
  its protections:** a shell can overwrite files, and no redirection may target the game installation. Check any saved
  model against the preview's model hash before further use. These models can contain retail data: keep them private
  and out of Git, and do not emit them into a shared terminal or transcript.
  The move checks that byte differences are confined to the selected twelve serialized position bytes and that other
  model fields, opaque groups and inspected scripts are unchanged; it does not stage or run anything. It cannot determine ground height,
  collision, runtime slots, script consequences, career compatibility or playability. Later encoding and bundle
  preparation remain separate, and must use the same reviewed identities. No no-overwrite or atomic-write guarantee applies to a
  redirected stream. This CLI has only authored-fixture tests, requires the
  same descriptor-safe input support as the preview, and has no validated Windows workflow.
- `level_editor_vectors.py` writes `companion/OnslaughtToolkit.Godot/Tests/LevelVectors.g.cs`, the authored vectors the
  Companion's level data layer (`Levels/`: `WorldBody` and `LevelArchive`, which read and write a world body and read a
  level archive) is tested against: world bodies of every version the loader accepts and every kind of thing record it
  reads, bodies the reference refuses (each valid but for one field), edits with the bytes the reference writes after
  them, and authored level archives, each with the reference's dump of the fields it read. No game bytes enter it.
  `python tools/level_editor_vectors.py --check` fails when the committed file is not what `--write` writes; it compares
  what each compressed blob inflates to, so it does not depend on the zlib that compressed it.
  `level_editor_vectors_tests.py` adds the reference's own round trips and the refusal of every proper prefix of a body.
  `gate-table --game GAME --stdout` lists the size, SHA-256 and dump hash of each world body of an installed game (hashes
  only) for the Companion's local retail gate, `Development/LevelsGate.cs`, whose header gives its command; the table is
  derived from a game, so keep it private.
- `export_game_assets.py`, `export_asset_catalog.py`,
  `export_language_corpus.py`, and `export_video_manifest.py` operate on
  user-supplied local inputs and write to a separate local output root. The
  asset catalogue's exact-content mesh variants contain payload-relative
  metadata; selected source paths and occurrence identities stay on occurrence
  rows rather than changing the shared variant. All four publish with its moved-destination limit (see `safe_generated_output.py` above).
- `level_asset_xref.py --archive LEVEL_res_PC.aya [--mesh m_NAME.msh.aya ...] --stdout`
  reports metadata from one selected PC archive and up to 16 selected loose
  meshes. It retains each top-level `MESH` and `TEXT` occurrence and lists
  same-archive `TEXT` candidates for each selected root mesh's stored `TEXB`
  names, qualified by the stored requested format and mip-level fields. The
  archive-to-selected-mesh association is by ASCII case-insensitive filename
  only: it is a candidate, not proof of the file's ownership or runtime use.
  A selected mesh's internal name is shown only for a NUL-terminated, nonempty
  printable ASCII value within its 300-byte name field; other names are null.
  A slot's name status is `readable`, `empty` (known empty: its candidates are not evaluated, `candidateStatus`
  `empty-name-not-evaluated`), `unterminated` or `unsupported-name`; the last two are unknown names.
  Duplicate, absent, unparsed and unsupported-name candidates remain separate
  or unknown. Unsupported `TEXT` names make comparison coverage partial;
  uncomparable or embedded `MESH` names likewise make reverse filename
  comparisons partial. WDAT
  values and a filename-derived level hint are reported separately.
  Embedded meshes, chained meshes, non-`TEXT` descriptors, other/base archives,
  optional-mesh conditions and script spawns are outside its coverage; it is
  not a complete dependency inventory or a visual test. The selected-file CLI
  requires Linux `O_PATH` and `/proc/self/fd`. The CLI emits private
  retail-derived metadata to stdout and opens no report file. If the caller
  redirects or saves the result, the destination and overwrite safety are the
  caller's responsibility; never redirect it into a game or user folder.
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
  and normal contracts (`cmsh_matrix_normal_contract.py` and `cmsh_skinning_contract.py` write their JSON with its moved-destination limit (see `safe_generated_output.py` above));
  `world_mesh_normal_probe.py` carries static-world OBJ bytes through both lighting chains.
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
