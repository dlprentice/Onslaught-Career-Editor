# Tools

Status: active — the reusable support surface, not a product lane
Last updated: 2026-11-11 (link-check note for the moved validation entries)
Summary: what each tool in `tools/` is for.

`tools/` supports the companion, the game documentation and the frozen rebuild copy in `rebuild/` through guarded extraction,
format inspection, capture analysis and focused checks. The Ghidra scripts, cohort specs, campaign/authority tools
and the Windows TTD/cdb/PowerShell runtime-probe lab moved on 2026-10-15 to the private historical maintainer archive; the WinUI packaging tools were removed.
The active rebuild lives in [onslaught-godot](https://github.com/dlprentice/onslaught-godot).

Root [`package.json`](../package.json) is the command authority. Documentation and safety checks use Python and
the pinned public source-reference submodules, with optional Node/npm shortcuts; they need no retail installation or Godot.
Run `git submodule update --init --recursive` from the repository root first ([README.MD, Public setup](../README.MD#public-setup));
without it, the link check in `npm run test:docs` fails with broken links into `references/`. The commands are:

```bash
npm run test:docs
npm run test:safety
```

`npm test` runs the Companion's contract and tooling checks without opening a window after public toolchain setup.
See the [Companion build guide](../companion/OnslaughtToolkit.Godot/README.md#build-test-capture-run-and-export).
`companion_toolchain.py` installs and verifies the pinned official development tools locally;
`companion_godot.py` stages, builds and tests the application using that installation.
Current root commands and reusable examples use `python` and forward-slash paths. The Companion development
runner targets Linux, including WSL2; other tools state their own platform limits. Dated receipts and historical evidence may
retain the literal Windows commands and drive letters that produced them; a
tool can also have an explicitly documented Windows evidence dependency.

`npm run test:tools` runs every registered suite; prefer an affected suite for a focused change. A suite that
cannot run here (one that needs a Windows host, none registered now, or the extractor source audit when a submodule it
compares with its pin is not initialised) is a named SKIP in the summary, never a pass and never a failure. The runner's
self-test fails for any `*_tests.py` file that is neither registered nor listed with a reason as run elsewhere or out of scope.

## Python prerequisites

Python 3.12 or newer, with `venv`, for the setup, build and runtime checks; the repository's wider Python tools are tested on Python 3.14 ([README.MD, Public setup](../README.MD#public-setup)). The modules needed depend on the selected check:

| Scope | Additional Python packages or inputs |
| --- | --- |
| Documentation and safety gates | Standard library only; full scans require the pinned public reference submodules initialized, including the documentation links into those sources |
| Authored catalogue, world/editor and mission-compiler checks | Standard library; catalogue schema assertions additionally need `jsonschema` and report SKIP without it |
| glTF pose checks and numerical frame/terrain probes | NumPy; probes that read images also need Pillow |
| Capture comparison, frontend scoring and region-overlap tests | Pillow |
| Content inventory gate (`content_inventory_gate.py`) | Pillow (image checks); `jsonschema` (row schema; the gate reports a skip without it) |
| DDS census (`dds_census.py`) | NumPy |
| Full `npm run test:tools` | NumPy and Pillow, plus the inputs required by its selected retail checks. In particular, `worldheaders_decode.py --self-test` reads `$BEA_GAME/data/worldheaders.dat` (or the tool's default install location); without that file it exits 1 with `not found`, so the aggregate reports a failure there, not a SKIP. This aggregate is not a game-free contribution gate |

Install NumPy (`numpy`), Pillow (`Pillow`) and, when checking catalogue schemas, `jsonschema` in the Python environment
used by the command. In an activated venv, `python -m pip install numpy Pillow jsonschema` installs all three;
`jsonschema` enables the schema checks, which report SKIP without it. This repository does not yet pin their versions or provide a Python dependency lock file;
these dependency names do not establish a tested standalone environment. Prefer the affected authored suite for a
change that needs no retail data. For example, `python tools/content_catalog_tests.py` uses an authored install;
`python tools/msl_compile_tests.py` uses authored script sources. Read each suite's SKIP lines when reporting results.

## Product and release

- `godot_host.py` supplies installed-engine discovery, locked bundled-SDK restore/build and owned-process cleanup;
  `companion_godot.py` builds and runs the companion through the verified public setup; an explicitly selected
  shared installation remains an optional maintainer route.
- `rebuild/` is a frozen reference. Some current format tools import its `cmsh_static_preview.py` parser;
  `test:tools` retains that parser's tests and `materialize_retail_assets_tests.py`. `test:godot-host` also checks
  the retained `first_flight.py` launcher with fake tools. These are support-code checks, not builds or parity
  acceptance of the frozen rebuild application. Current rebuild setup, runtime commands and gates belong to
  [onslaught-godot](https://github.com/dlprentice/onslaught-godot).
- `ce_museum_stage.py` turns an authored exhibition description into two loose-world overrides in a CE mod folder, using an existing level's terrain and resources from a game you own. It is experimental: [the museum project note](../docs/ce-museum-project.md) gives its scope and limits. Its authored tests are registered in `run_tool_tests.py`.

Use [`VALIDATION.md`](../VALIDATION.md) to select checks. These tools do not
publish, sign, or install anything by themselves.

## Documentation integrity

- `md_link_check.py` validates local link **targets** and heading anchors; `md_reachability_check.py`
  answers the different question of whether a document is linked from anywhere. The frozen copies cannot be edited, so
  the link check accepts their links into sections that moved from `VALIDATION.md` to `VALIDATION-HISTORY.md`; live
  documents must link to the new file.
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
  is a symlink, a hard link or not a regular file. It re-checks that every held directory (one it keeps open as a descriptor) is still named where it was
  found before each write, again just before the rename and once after publishing. That is detection, not a lock.
  **Moved-destination limit:** a directory renamed while a file is being published still receives that file, wherever
  the directory now is, and the writer refuses only afterwards; later writes are refused before anything is created.
  The check that the output root does not overlap a protected source (the game folder) is made once, when the root is
  opened, so the helper does not guarantee that a destination moved by another process during a run stays outside the
  game folder. Do not point a writer at an output root that another process can rename. The Windows path holds the
  directories with share modes meant to block a rename; no native Windows run has validated it here.

## Content catalogue

[`content_catalog.py`](content_catalog.py) builds a local content catalogue from a selected game installation.
Its [authored tests](content_catalog_tests.py) require no retail files; `jsonschema` enables the schema assertions.
The generator and separate read-only retail gate need your own lawfully obtained game:

```bash
python tools/content_catalog_tests.py
python tools/imposter_records_tests.py
python tools/content_catalog.py --game /path/to/game --out local-data/content-catalog
python tools/content_catalog_gate.py --game /path/to/game
```

Optional `--decomp /path/to/onslaught-decomp` adds literal code lookups from a public
[onslaught-decomp](https://github.com/dlprentice/onslaught-decomp) checkout; no private decompilation or lab is required.
The generator writes `manifest.json`, `survey.json`, `coverage.json` and `assets.jsonl` below this checkout's
ignored `local-data/`. They contain retail-derived metadata and stay private. The Companion does not read these output files; its C# implements the `catalog_world` contract of `content_catalog.py` as a static preview ([its provenance note](../companion/OnslaughtToolkit.Godot/PROVENANCE.md)). [The asset schema](content_catalog.schema.json), the detailed format descriptions below and
[source-file coverage](#catalogue-source-file-coverage) explain the records and their limits.

### Imposter models and atlas references

The catalogue records each framed imposter separately as `type: imposter`. Its ID uses the owning archive,
top-level chunk and record ordinal; its source coordinates and SHA-256 bind the whole framed `IMPT` record.
Existing mesh IDs are unchanged. `imposter-of-mesh` resolves its stored mesh resource ID in that same archive,
`uses-texture` names the enclosing set's atlas descriptor, and `loaded-by-archive` and `has-imposter` connect it
to its owner. An unresolved mesh or atlas stays unresolved; duplicate mesh IDs in one archive are ambiguous, so no
first- or last-record precedence is assumed. The stored label is display text, never a path to open.
The descriptor's existing atlas-to-mesh relationships remain available.

[`imposter_records.py`](imposter_records.py) walks the nested chunk lengths and refuses truncated, contradictory
or duplicate identity fields. It reads each stored `VIEW` rectangle's normalized atlas edges and positive dimensions,
rejecting non-finite values, empty or reversed rectangles and invalid sizes. A malformed view array retains the
imposter's identity but publishes no valid-looking prefix of view metadata. Missing, truncated or unterminated labels
are explicit, and bytes outside the fixed label are not treated as part of its name. The reader never searches opaque
fields for tags. [Authored controls](imposter_records_tests.py) exercise these cases without game files; catalogue
tests cover the actual identity, coordinate/hash and mesh/atlas relationships.

Full metadata and relationships are available in the catalogue's `assets.jsonl` for editor or renderer consumers.
The inventory's `records.jsonl` retains only their ID, type, source and hash, as it does for other catalogue assets.
They are not extra pixel assets or new `asset-metadata.jsonl` processing rows. The overall
record stays partial: the other `CIMP` fields and set-level `DATA` remain uninterpreted. The number of complete
view rectangles does not establish runtime angle selection, a mesh's live rendering, or whether a mission uses it.
Stored dimensions are not relabelled as pixels or world units. This adds usable identities and relationships;
it does not increase the inventory's decoded-byte coverage or mean the Companion already renders these imposters.

## Content inventory

[`content_inventory.py`](content_inventory.py) accounts for every byte of a selected install and lists every model,
texture, image, animation, sound, film and text asset in it, used or not. It runs the catalogue, then walks each file
with the reader that follows its loader, or with its format's published layout, and puts each byte of the file's stream
in one class: decoded (a reader consumed it in the loader's order and its walk closed exactly), referenced (a record or
reader establishes what the bytes are and how long they are, but nothing has read their contents) or unknown. A gap in a
walk is unknown by construction, so a reader cannot lose bytes silently. Used means that a catalogue record, a physics
value, a manual page's link or a loader rule names the file or asset; it is not a runtime observation.

```bash
python tools/content_inventory_tests.py
python tools/content_inventory.py --game /path/to/game [--decomp /path/to/onslaught-decomp] --out local-data/content-inventory
python tools/content_inventory_gate.py --game /path/to/game --inventory local-data/content-inventory
```

Vorbis audio packets, Bink frames and audio track descriptors and JPEG scans count as decoded only when an independent
decoder (FFmpeg, found on `PATH` or named with `--media-decoder`) reads every stream without an error and its frame and
sample counts equal the walk's own. Without one (`--no-media-decoder`) those payloads stay referenced, and the coverage
says so. Those payloads are a large share of the content, so the coverage's `headline` (and the run's last summary line)
gives the content families' decoded share twice, with that decoder and without it; quote both. The Vorbis setup
header, the JPEG tables and headers and a Bink file's header and frame index are read by this repository's readers and
count as decoded either way (a Bink header's version letter and flags are reported, not constrained, and its second
frame count is skipped); a JPEG's application, comment and other segments and a PNG's ancillary chunks count on their
lengths and checksums alone, and a Vorbis comment header's strings must be UTF-8 but its comments are not read
further. A particle set counts as
decoded only when `particle_set_walk.py` reads every value to the last descriptor; the words the game's reader skips
after a direct number stay referenced. With `--decomp`, a film, particle set or splash image whose name a source string
literal holds counts as used. An archive's `LVLR`, `TARG` and `AYAD` words count as decoded only when they are the
documented PC build's ([the archive contract](../reverse-engineering/asset-formats/lvlr-archive.md), which defines all three), `WDAT` only when
its level numbers fit the archive's world layout, and a mesh, goodie texture or goodie mesh reference's name or an
imposter's stored label only when it ends inside its buffer; a language table's strings only when each entry points
inside its pool and each string ends there. Anything else stays referenced and is reported as a problem. A texture
whose envelope does not inflate stays unknown, as does any file whose reader cannot run, and an install holding a link
or special file, or a folder the walk cannot list, is refused.

No loader reads the sources, so each is held to its own grammar to its end. A mission script counts as decoded when
`msl_compile.py`'s compile reproduces every shipped script compiled from it (`msl_gate.py`'s exact verdict, or exact,
assisted: an `#include` the install lacks is read as empty and the names it would define come from the shipped
constants) or, when no level ships it, when it compiles with every include present; a stale source (it compiles to a
known older revision), one that compiles only with a missing include read as empty and one that does not compile stay
referenced, and a shipped copy it does not reproduce is a problem even beside one it does. When the judge cannot read a
level archive's worlds, which scripts that archive ships, and for which level folders, is unknown: no source in a level
folder is then judged, each is referenced with a problem, and the gate fails. Mission
text counts when every line is an `[ID]` line with its quoted string on the next, a `;` comment or blank; a symbol
table or `textlist.h` when every line is a `#define` of a number, a `//` comment or blank; a manual page when it
tokenizes as one html element, and its file list when it parses as XML. Plain text with no grammar (the install's
readme and log, which are not content) counts when every byte is a character of its encoding. An empty file counts as
decoded; the coverage counts empty files by family.

The run writes `manifest.json`; `coverage.json` (per family, files and stored and logical bytes by class; the unknown
total; the proofs each reader produced; the installer's log compared with the folder; the physics joins; the assets by
kind, used and unused, with the texture records an archive loads but nothing names counted apart); `files.jsonl` (each
file's account, with the spans that are not decoded); `items.jsonl` (one row per asset, including every link of a mesh
chain and its animations, and its texture slots joined as the parent's are); `asset-metadata.jsonl` (below); and
`records.jsonl` (the catalogue records' coordinates, for the gate). [The row schema](content_inventory.schema.json)
describes them. All of it is retail-derived and stays in ignored `local-data/`.

`asset-metadata.jsonl` is the input list for an offline processing batch, such as an AI upscale: one row per texture,
image, model, animation, sound and film, with its identity (the file, how its bytes are wrapped there, the archive
chunk, bank sample or resource, the coordinates and the SHA-256 of the asset's own bytes), the format, width, height,
mip levels, alpha, channels, sample rate, duration and frames its reader established, the records that name it and the
archives that load it, and the catalogue's usage summary and upscale notes where the catalogue has them. A field no
reader established is null; nothing is taken from a name. A DDS file's row gives the format its header says it stores,
with that file's mips and alpha. A texture record's row gives the format the record itself names (the same field names
its pixel files); the PC build loads the record's pixels from DDS files (the catalogue's `pixels-from` evidence, which
the row lists), and those can store another format, with another channel count, which their own rows give. One
texture-record row stands for every byte-identical copy of the record: `details.occurrences` counts the copies, the
identity places the first, and the catalogue's record lists every copy. An animation's frames are its virtual frames
from its start to its last frame inclusive, whichever way it runs (a negative frame scaler plays from start down to
last). That is the span the record states: the animation keys document's frame formula places a frame from the phase,
the scaler and the start and does not use the last frame, and the count is one more than the scaler's magnitude in a
mode whose last frame is the start plus the scaler. Its duration is the time its phase takes from 0 to 1 at its stored
rate, 1 / (20 × rate) seconds with a rate up to 0.0001 played at 1, the game's rule as
[the animation keys document](../reverse-engineering/asset-formats/cmsh-animation-keys.md#from-time-to-a-virtual-frame)
gives it; a looping mode repeats at that period, and a script can choose another speed. No pixel format is established
for the terrain mixer textures or the static shadow cells. The coverage counts, per kind, the rows that establish each
field.

[`content_inventory_gate.py`](content_inventory_gate.py) combines independent checks of the selected install with
consistency checks of the run: an independent walk and hash of the folder (any link, special file,
folder it cannot list or search, or file it cannot read fails the gate), every AYA re-inflated with zlib alone, every
archive's chunks walked again, every catalogue record that an archive stream places hashed at its coordinates, Pillow
opening every image, every cached mesh frame composed from its keys, and the independent decoder's agreement on every
Ogg and Bink file. Every row the run wrote must meet [the row schema](content_inventory.schema.json); the gate checks it
with `jsonschema`, and says so when it skips the check without it. PE resource-tree lookup reuses the inventory's PE
walker, and decoder agreement is the result recorded by the inventory. These parts are consistency checks, not
separate decoder implementations or repeat decoder runs.

A row of `asset-metadata.jsonl` claims nothing the rest of the run, or the file, does not bear out. It must say what its
`items.jsonl` row says (kind, form, name, status, use, owner and identity) and, where the catalogue lists the asset,
what that record says (envelope, chunk path, coordinates, hash and container). Its form is then held to the file:
the gate states, apart from the inventory, which kind each form is, which file families hold it, which envelope its
identity names, whether its coordinates address the stored file or the stream inflated here, which top-level archive
chunk its bytes lie in (read from its own chunk walk), whether its coordinates are the whole stream, and what its bytes
open with; a PE resource is an icon or a bitmap as the executable's resource tree says. A row relabelled to another form
therefore fails, and so does a row and its item relabelled together, because the file does not hold what the new label
needs. Every row but a mesh chain's links, their animations and the terrain mixer mips (whose readers give no
coordinates, and whose item must lie in an `ERES` (engine-resources) chunk) is placed, and its bytes, cut from the stored file or from the
stream inflated here, must hash to its SHA-256. Whether a DDS, texture record, Ogg or Bink is readable is the gate's
reading of its bytes, never the row's status: a row that calls readable bytes unparsed fails, as does one that calls
unreadable bytes parsed or claims fields for them. Each metadata field must equal what the gate reads from the bytes
itself: a DDS header and mip chain, each mip hashed, and with Pillow the top mip's alpha (DXT2 is decoded as DXT3, whose
alpha layout it shares); a texture record's own fields; a PNG, TGA, JPEG, icon, Ogg, Bink or bank sample header; an
animation record; a damage texture's levels. So must the details those bytes show: a PNG's bit depth, colour type,
interlacing and transparency chunk, a TGA's bits per pixel and alpha bits, a JPEG's precision and process, an animation's
mode, an Ogg's samples and nominal bitrate, a Bink's frame rate and audio tracks, an icon's bit count and the
Dial.raw byte sprite's frames. An unplaced row's fields must follow its details. What the run copies from the
catalogue's records is not recomputed: a texture record's occurrence count and pixel files, a mesh's structure counts,
a sound's role, a bank sample's details, the usage summaries and upscale notes, and the records that name an asset are
checked against the item and the record's coordinates, not against the relationships that gave them, which the
catalogue's own gate owns; and a chained animation's rate and duration follow its details because no coordinate places
it. For some placed rows the gate's reading adds little beyond the chunk the bytes lie in: the terrain, surface and
shadow payloads and the byte sprite have constant fields, and a mesh is read only for its magic. The gate also fails
when the mission-script judge could not read a level archive's worlds. It exits 0 only when all of them pass.

A decoded byte belongs to a reader; that does not give every field a meaning or establish what the game does with it.
The font records (`FGEN`, `DXFT`), part of each imposter record, a save's career block, the bytes of `Dial.raw` after its
first frame, the language tables' pool strings no entry reaches, the mission scripts that reproduce no shipped copy,
the words a particle set's reader skips, the document a Word ActiveMime file compresses and everything in the
executables but their headers, resource tree, icon images and icon groups stay referenced, and the coverage lists each
such part. Bytes after an ActiveMime file's compressed stream stay unknown: no published layout says what they are.

## Editor references and generators

The Companion's [level and mission editor owners](../PROJECT-INDEX.md#level-and-mission-editor) use these Python references:

- `world_resources_decode.py` and `world_resources_encode.py` for world formats, `world_edit_move.py` for coordinates
  and moves, `world_mod_stage.py` for separate mod folders, and `heightfield_lookup.py` for terrain lookup.
- `msl_compile.py` for mission-source compilation, with authored cases in `msl_compile_tests.py`.
- `level_editor_vectors.py`, `msl_vectors.py` and `script_tables.py` generate the committed C# vectors and tables.
  Their `--check` mode compares generated content with the tracked file without rewriting it.

These authored checks are separate from retail comparisons: `level_editor_vectors.py gate-table` feeds
`Development/LevelsGate.cs`, and `msl_gate.py --table` feeds `Development/ScriptsGate.cs`. Those comparisons need
selected retail inputs and the Companion's shared-toolchain runtime; their detailed commands and limitations are
documented below and in the development entry headers. Keep retail-derived tables in ignored local output.

## Assets and formats

- `media_readers.py` walks the install's public container formats with their published layouts and refuses, with a
  reason, whatever does not hold: Ogg (every page checksum, sequence and flag, the identification and comment headers,
  and the setup header read field by field as the Vorbis I specification gives it: codebooks, floors, residues,
  mappings and modes, with each rule the specification calls an error, and libvorbis's rules for a codebook's lone
  entry, a residue classbook's entries and a vector book's lookup refused too; the audio packets are only framed), Bink 1
  (the header, the frame index and each frame's audio packet sizes, as libavformat's demuxer reads them; the audio
  track descriptors and the packets are framed), PNG (chunk checksums and the inflated image data's size and row
  filters), JPEG (markers, the quantization and Huffman tables, the restart interval, the frame header's components,
  each scan header and the extent of each scan; application, comment and any other segment are framed by their lengths),
  uncompressed TGA, PE (the headers, the section table and the resource tree with its icon images; section contents,
  the DOS stub, header padding, unreached resource bytes and COFF symbol tables are only framed), Word's saved-web-page
  ActiveMime container (its header and compressed stream; the compound document inside is not walked), HTML pages
  (tokenized to their end as one html element) and XML documents (parsed by expat).
  `media_readers_tests.py` reaches every refusal reason the module has.
- `particle_set_walk.py` reads a particle set (`*.par`) value by value in `CParticleSet::ReadData`'s order, with the
  token grammar of the rebuild's reader (`rebuild/OnslaughtRebuild.Parity/Particles/`), and refuses what that reader
  would take otherwise than as written. `particle_set_walk_tests.py` checks its tables against that C#.
- `physics_values_decode.py` reads the compiled physics script value by value with the value classes of the rebuild's
  typed reader (`rebuild/OnslaughtRebuild.Parity/Physics/`) and says which values name a mesh, particle effect, sound
  effect or icon. `physics_values_decode_tests.py` checks its tables against that C#, so the two cannot drift apart.
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
  mirror-hash-verified join across loose CMSH (the tagged mesh-stream format, see its [format contract](../reverse-engineering/asset-formats/cmsh-mesh.md)) pose/skeleton lanes, numeric-LVLR
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
  timings, occupancy), `ERES` (mixer mips, heightfield settings and samples, mixer map), `SURF`, `SSHD`, `VSDS` (the
  vertex shaders `CVertexShader::Load` reads: each one's declaration, constants, compiled code and assembly text as sizes
  and hashes, read only where the stored object's pointer to it is set; `CVertexShader::Create` finds a declaration
  shader by its type and declaration bytes, never by name), `PMIB` (the landscape patches' index strips per level and
  edge mask, each checked against its patch's vertices) and `DMKR` (the damage texture's mip levels; the base archive's,
  read at start-up, means `data\textures\mixers\damage0.tga` is never read); `LNDS` is skipped by the PC loader.
  Relationships (archive to mesh, texture record to its DDS file, mesh slot to texture
  record, imposter to mesh, placement to definition and mesh, thing to its compiled script and `.msl` source, path to
  its waypoints, script to the units, paths, scripts, text ids, thing names and bank samples its literal call arguments
  name, level to the sky-cube, water and detail textures its map numbers build with `sprintf` and to the battle engine
  configurations it offers, configuration to its weapons, explosion, cockpit mesh and description text, sound effect to
  its bank samples and its chain, effect to texture, goodie to texture/mesh/film, voice file to its text line, code
  lookups of textures, meshes and sound effects with `--decomp`) are emitted only from a loader rule in
  the public decompilation or from the data, and each names that evidence; unresolved links stay explicit. Sample joins
  consider only direct `data/sounds/sounds_<language>_pc.xap` banks for the five names `CText::GetLanguageName` returns;
  other banks are catalogued without
  asserting they load. Duplicate sample names within a bank make the join incomplete and list candidates: the last
  successful initial creation would be found first, but the catalogue does not observe loading or reload outcomes.
  A script's
  literal thing name (`GetThingRef`, `Teleport`, `PlayCutscene`), and a cutscene's link-to name (`CCutscene::Start`), is
  joined using a source-modelled prediction of `CWorld::FindThingByName` just after a successful load (`named_things.py`, below): the record predicted to be found in every
  career (`resolved`, with the records of that name it hides), the base-world records of the name in the order the
  career's keeping decides (`career-dependent`), a name a script's literal `SetName` call could give its own thing
  (`runtime-name`), or nothing (`unresolved`). Each named placement and marker says whether and how it joins the list
  and whether its own name finds it, and each level record lists the modelled registry in joining order. These are
  predictions, not observations of runtime names or later changes. Missing, misordered or undecodable world parts mark
  the registry and its lookups incomplete; a partial list never claims a target. A registry requiring over 10,000 entries is
  refused explicitly before the catalogue is written; the limit is the tool's, not the game's. The
  loose-mesh reader uses the bounded archive decoder: at most 64 MiB compressed, 128 MiB expanded and 4,096 members.
  These are tool limits, not claims about the game format. A refused mesh or ambiguous duplicate world container stops
  the catalogue before publication. The optional `--decomp` source must contain `src/` and stay disjoint from the output;
  a reported Git HEAD belongs to the selected repository root, while its working tree remains unverified. Language and
  symbol tables are selected from the file inventory and parsed from a bounded, identity-checked read; final symlinks
  and detected file changes are refused. The
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
  writes files. Its `--out` is the writing form for this command only; the legacy `--out` of the `--stdout` commands is refused (see above). It packages the edited world(s) as a CE mod folder `PARENT/ID` (`mod.json` plus `data/worlds/worldNNN.wrd`,
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
  behavior, and does not execute a game or script. The CLI requires descriptor-relative no-follow file support (each path component is opened relative to a held directory, and links are not followed);
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
- `named_things.py` predicts the registry of named things a level loads (`WORLD.mNamedThings`) from its decoded world
  bodies by source-derived loader rules, assuming initialization succeeds; it is not a runtime measurement. The rules
  are cited by function in the module: a thing joins when `CWorld::LoadWorld`
  initialises its slot (the base world's slots before the real world's, and a base-world one only if the career keeps
  it) and its class's `Init` reaches `CComplexThing::Init` with a name. Trees and waypoints never do (their classes
  derive from `CThing`); a unit whose behaviour has a squad, and a squad, hand the name to their member units or keep
  it as `CSquad::Init` decides. Each thing joins at the front, and `CWorld::FindThingByName` returns the first exact
  (`strcmp`) match from there: the thing named most recently. `find` predicts a name's answer right after loading
  (`resolved`, `career-dependent` when only base-world things have it, or `unresolved`) with every candidate in lookup
  order; `find_by_walk` computes the same answer using a second source model, as a cross-check, not an independent game
  run. Names given at run time
  (`SetName`), things spawned in play and things that leave the list are listed, not followed, and which base-world
  things a career keeps is the career's (each base-world entry carries its career bit and dies-on world).
  `named_things_tests.py` checks each rule on authored world bodies, and the gate below on authored game folders
  (`content_catalog_tests.py` checks the payload decoders and the gate's payload checks); no game bytes.
- `game_tables_decode.py` reads `data/battle engine configurations.dat` in `CBattleEngineData::Load`'s order for each
  record version (`UPhysicsManager::Reload` -> `UBattleEngineDataManager::Load`; each record joins the front of the
  list, so a name finds the last record of that name and a world header's unknown name gets the last record). It
  preserves stored scalar fields and reports separately the effective values after initialization and the loader's
  version-specific defaults or overwrites. A catalogue configuration's `values` and `stores` are effective; when
  defaults occur, `storedValues` and `storedStores` preserve the stored values (null means absent or non-finite for
  stored scalars, absent for stores). Existing catalogue v1 outputs for versions before 8 can contain incorrect
  effective values and should be regenerated. It also reads
  `data/sounds/sounds.sfx` as `CEffect::LoadSFXFile` reads its lines (`CDXMemBuffer::ReadString` and `CEffect::ReadLine`:
  `#` lines skipped, a CR in the penultimate byte replaced even without a LF, each line's last character stripped; a later effect of an earlier one's
  name, by `stricmp`, joins that effect's chain, of which `PlayEffect` plays one at random). It refuses what the loaders
  would misread (a name past the 256-byte buffer or the 64-byte effect fields, an SFX version above 103, bytes left over
  in the configurations). The catalogue adds a record per configuration and per effect: a configuration's weapons
  and explosion join the physics definitions of that kind (`strcmp`, the first definition of a name), its cockpit the
  loose mesh, its description number the text `CFEPBEConfig::GetConfigDescription` shows; a level's configuration
  names join from `worldheaders.dat` (the configuration page, by name) and from its world header (in game, by the slot
  chosen, with the fallback); an effect's sample and low-pass sample join the samples of the same name in each
  language's XAP bank, as a script's `PlaySample` argument does (it names a bank sample, not an effect).
  `game_tables_decode_tests.py` checks both readers on authored files.
- `content_catalog_gate.py --game GAME [--table] [--level N]` is the content catalogue's retail gate. Over every level
  archive of an installed game it checks that exactly one WRES/WRLD is present and that WDAT and its required world bodies are complete, in loader order, and
  name the selected level; case-colliding resource folders or level archives are refused. It checks that the world
  bodies decode with the loader's slots, that every registry
  entry is a slotted record of a class that names itself, under its own name, with the base world's first and every
  base-world slot inside the career's bits, that no unit takes a slot with nothing made for it, and that `find` and
  `find_by_walk` agree on every literal thing name of every script, and every cutscene's link-to name, with every, no
  and every other base-world thing kept. Over every resource archive it decodes every payload a PC loader decodes
  (`ERES`, `SURF`, `SSHD`, `VSDS`, `PMIB`, `DMKR`) and checks that each consumes exactly its chunk and that every patch
  strip stays inside its patch. It decodes the configurations and `sounds.sfx` and counts what they name that the
  install lacks, and the levels whose world header lists other configurations than `worldheaders.dat`. It reads the
  game folder, writes nothing and prints counts; it checks the archives present, so the counts alone do not prove an
  installation is complete. `--table` adds a row per level (derived from a game: keep it private).
- `heightfield_lookup.py ARCHIVE.aya X Y` prints the height under a position of a level archive's terrain, as the game's
  terrain lookup computes it: the archive's `ERES` chunk holds 64 x 64 tiles of 9 x 9 signed 16-bit samples (one per world
  unit; a tile's ninth row and column repeat its neighbour's first) and a height scale, and heights are world units with Z
  down, so ground above the origin plane has a negative height. The rule is `CHeightField::Collide` (`0x0047eb80`)
  and the bilinear read it calls (`0x0047eb00`), cited by function as the decompilation describes them and written here
  without copying its source: a bias and a large constant are added to each coordinate in 32-bit floats, the bits are read as
  8.8 fixed point, a position outside 0 to 512 on either axis answers 0, and the four samples around it are blended with 8-bit
  fractions (arithmetic shifts, so a step down rounds down) and multiplied by the scale. A position that is not finite answers
  0 here, which is not claimed to be the game's answer. `read_heightfield` reads the chunk in the order the loader reads it
  and refuses a payload with bytes left over or missing. `heightfield_lookup_tests.py` runs on authored terrains only (no
  game bytes): the bias, whole and fractional positions, steps down, the order of the tiles and the ninth sample, the edge of
  the square, and damaged payloads. It is the reference the Companion's C# port (`Levels/Heightfield.cs`) is checked against.
- `level_editor_vectors.py` writes `companion/OnslaughtToolkit.Godot/Tests/LevelVectors.g.cs`, the authored vectors the
  Companion's level data layer (`Levels/`: `WorldBody` and `LevelArchive`, which read and write a world body and read a
  level archive; `ModStager`, which writes the mod folder `world_mod_stage.py` writes; `EditSession`, which moves things
  and undoes it) is tested against: world bodies of every version the loader accepts and every kind of thing record it
  reads, bodies the reference refuses (each valid but for one field), edits with the bytes the reference writes after
  them, authored level archives, each with the reference's dump of the fields it read, and the `mod.json` bytes and
  files the reference stager writes for a set of inputs (and the inputs it refuses), and coordinate texts with what the move tool
  (`world_edit_move.py`) stores for each, which the page's coordinate reader (`CoordinateInput`, used by the Level editor page) must
  match: the float32 as four bytes, whether it is not exactly the decimal typed, and its exact value, with the texts the tool reads
  and the page does not (digit separators, other digits, other whitespace) marked as narrower, never wider; and, for the map,
  an authored terrain in an archive whose `ERES` chunk is split over members, with the heights `heightfield_lookup.py` gives
  at a large set of edge positions (the edges of the square, the bias's flooring, tile borders, the ninth sample, positions
  that are not finite), as the float32 bits the C# lookup must equal. No game bytes enter it.
  `python tools/level_editor_vectors.py --check` fails when the committed file is not what `--write` writes; it compares
  what each compressed blob inflates to, so it does not depend on the zlib that compressed it.
  `level_editor_vectors_tests.py` adds the reference's own round trips and the refusal of every proper prefix of a body.
  `gate-table --game GAME --stdout` lists the size, SHA-256 and dump hash of each world body of an installed game, for
  each level archive a SCRIPTS row (how many scripts its own world and its base world hold, a hash of the lines the Level editor's script
  catalog reads from them, how many of their sources the finder reads and a hash of those sources' text), a NAMES row (every quoted text of
  the level's own sources, found outside comments and resolved against the level's objects and its base world's, its paths, scripts and event handlers, hashed;
  the nonempty first argument of a `FollowWaypoint` or `FollowWaypointWait` call uses the first matching base or level path under the modeled C-locale byte comparison: ASCII case-insensitive, other bytes exact, NUL-terminated; other locales and native Windows remain unverified), a PATHS row (each waypoint
  path of the level's own world with the rows of the points the game keeps, the slots that name a waypoint, hashed, and how many points are kept of how many slots)
  and for
  each level archive with a terrain the digest of its samples, the bits of its scale and water level, and a digest of the
  heights `heightfield_lookup.py` gives on a fixed grid and at every thing's position (hashes only) for the Companion's local
  retail gate, `Development/LevelsGate.cs`, whose header gives its command; the table is derived from a game, so keep it
  private.
- `msl_compile.py` compiles a mission script source (`.msl`) to the record a level's world file ships for it. The `.msl` sources are the original compiler's input. The game runs the compiled scripts inside each world body
  (`CWorld::LoadScripts`, `0x0050ac70`, and `CMissionScriptObjectCode`'s file constructor, `0x00538ec0`); no runtime
  trace has checked whether it opens an `.msl` file. The compiler is written from the decompilation's description of the script VM and its loader (cited by function, no source
  copied) and checked against what the game shipped. The output is the record `world_resources_encode.read_world_model` gives for a
  script (instructions, the 13 event entry points, the symbol table with each symbol's source line, the named handlers, two
  trailing words), ready for `write_world_body`. The module's docstring lists the dialect as the shipped scripts show it: a call's
  attribute has a result-used bit, an assignment is an expression, a `for` step is read before the body, `do_once` blocks add boolean
  symbols after every other symbol, floats are float32. Two counters belong to the compile session and are the caller's to start
  (`const dataN` and `do-once-N`). Operator grouping is only partly proven by the shipped scripts, so the compiler accepts repeats
  of one operator, `&&` with `==` (one rank, left to right, unlike C) and arithmetic inside comparisons, and refuses any other
  mix without parentheses, naming both operators. It refuses, with a line and a reason, statements nested more than 100 deep, a
  script that grows past a million tokens when its `#define` names are replaced, a number that does not fit 32 bits or float32, and
  an `#include` that is a link or passes through one below the selected game folder. It reads at most 128 included headers per script,
  with at most 1,048,576 characters per header and 2,097,152 characters in total, including repeated headers; the file reader also caps
  a header's bytes. For game-relative headers and the gate's primary source, the Python reader opens each path component relative to
  a held directory, refuses symbolic links below the selected root and checks identities around the bounded read. The selected root
  itself may be reached through a link; regular hard links remain accepted. Detected file changes are refused, but these checks do
  not create an immutable snapshot and remote-filesystem behavior has not been validated. This Python file reader currently requires
  Linux descriptor-relative, no-follow support and refuses on other systems, including Windows; the in-memory compiler is unaffected.
  Its separate `read_source` for an explicitly selected standalone file permits parent links and does not establish a game-root boundary.
  Besides the record it returns notes (how a mixed chain was grouped, a handler the
  game never calls) for an editor to show.
- `msl_gate.py --game GAME [--table] [--level N]` is its retail gate: for every compiled script of every world body of an
  installed game it compiles `data/MissionScripts/level<NNN>/<name>.msl` and compares the record field by field and as the bytes
  the world encoder writes. A script is exact; exact with an `#include` the install lacks (a few sources name files only the
  developers had, so the gate treats the header as empty and takes each name it would have defined from the shipped constants);
  or one of a pinned list of installed sources that differs from the compiled world-file script. Each pinned entry has a description and a
  SHA-256 identity of the complete ordered shipped/compiled record pair; a different pair, a missing entry or an entry that has become exact
  fails. The fingerprint pins the observed pair, not the explanation for its difference; a legitimate different installation may need its
  own independently verified baseline. It reads the game folder, writes nothing,
  and needs an installed game; `--table` lists one row per script (private, derived from a game).
  `msl_compile_tests.py` runs on authored sources only (the shape of every statement, the call flag, the counters, the grouping
  rules and the refusals, the header search, a record's round trip through the world encoder, and the gate's verdicts on an
  authored game folder).
- `script_tables.py` writes `companion/OnslaughtToolkit.Godot/Levels/ScriptTables.g.cs`: the 13 event names a compiled mission
  script's entry points are indexed by and every native a script can call (name and argument letters, in the order a CALL
  instruction's low byte indexes them), from `world_resources_decode.py`'s tables, for the Level editor's Scripts view.
  `--check` fails when the committed file is not what `--write` writes; `script_tables_tests.py` reads the file itself back against
  the tables. No game bytes are in it. The file also holds the VM's opcode names, in the order an instruction's opcode number
  indexes them, which the compiler in the Companion writes.
- `msl_vectors.py` writes `companion/OnslaughtToolkit.Godot/Tests/ScriptVectors.g.cs`: authored mission scripts (none is a game
  script) and what `msl_compile.py` makes of each, as lines (the instructions by opcode name, the entry points, the symbols with their
  values, the named handlers, the two trailing words), as the notes it gives, or as the message it refuses with, plus the reference's
  `repr` of some texts (its messages quote tokens with it) and its answer for every pair of operators. The Companion's C# compiler
  (`Missions/`, which ports `msl_compile.py`) must give the same lines, notes and messages word for word. `--check` fails when the
  committed file is not what `--write` writes; `msl_vectors_tests.py` works a few vectors out by hand and checks that the set writes
  every instruction the compiler can and uses every operator. The Companion's local retail gate for that compiler,
  `Development/ScriptsGate.cs`, takes `msl_gate.py --table` and requires the same status for every script of an installed game.
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
- `rebuild/tools/materialize_retail_assets.py` is the frozen rebuild's materialization reference; its retained
  focused tests still run under `test:tools`. Current rebuild input preparation and build/run commands belong to
  [onslaught-godot](https://github.com/dlprentice/onslaught-godot).
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

## Catalogue source-file coverage

The counts describe logical source-file paths. Different paths can count separately even when their file contents are identical.
For byte counts by what a reader decoded, see [the content inventory](#content-inventory).

The `coverage.json` produced by `content_catalog.py` separates a family’s advertised parser support from what the
selected input actually yielded. `sourceFileCoverage` counts regular input files and their stored sizes by family,
then counts files represented by at least one catalogue record and files targeted by at least one explicit resolved
relationship. Each file is counted once per measure, even when it contains many records. The relationship count reflects
catalogue evidence, not an observation that the game used the file. Whole stored file sizes are not decoded-byte counts:
a record may describe only a header or a portion of an archive. An input list that was unavailable is reported as
`not-recorded`, not as an empty install; invalid, non-regular, duplicate or ambiguous inputs are reported separately.

`assetStatusByType` reports `not-recorded` when a record has no explicit parser status. Family labels such as
`catalogued` describe available readers, not proof of a complete per-file or per-byte decode. These counts cover only the
selected local input and the current readers; they are not a percentage of every asset in every version of the game.
The catalogue and its detailed outputs contain game-derived data and stay in ignored `local-data/`.

## Parity measurement

- `compare_capture.py` compares one reconstruction frame against one retail
  frame per region. It refuses mismatched sizes rather than resampling.
- `score_frontend_capture.py` pairs whole capture runs against the retail reference by offset. In the retained
  `rebuild/tools/first_flight.py` launcher, capture folds its verdict into the capture's `status`, so a frontend
  regression fails that capture. This describes the frozen route; current capture commands and parity gates belong to
  [onslaught-godot](https://github.com/dlprentice/onslaught-godot). The retained thresholds live in
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
writes at all, to ignored local paths. New game findings belong in
[onslaught-preservation](https://github.com/dlprentice/onslaught-preservation);
[`reverse-engineering/`](../reverse-engineering/RE-INDEX.md) retains the frozen reference notes.

- Formats and corpora: `aya_corpus_chunk_inventory.py` (corpus-wide AYA chunk inventory),
  `aya_extractor_source_audit.py` (source/history audit of the pinned AYAResourceExtractor fork),
  `battle_engine_config_decode.py` (reads and re-encodes `battle engine configurations.dat` in memory; by
  `CBattleEngineData::Load` its UNKNOWN spans are the explosion, the walker and jet weapon lists, the aug and primary
  weapons, the cockpit and the description number, which `game_tables_decode.py` reads by name),
  `worldheaders_decode.py` (decodes `data/worldheaders.dat` byte-exactly; its
  `--metadata-json` option projects bounded level modes and optional
  configuration-name membership, not proof of playable multiplayer),
  `heightfield_node_array_probe.py` (checks whether any shipped heightfield header fills the per-node array).
- Meshes: `cmsh_grammar_walk.py` walks PC CMSH streams with the grammar in
  [`asset-formats/cmsh-fields.md`](../reverse-engineering/asset-formats/cmsh-fields.md) and proves it accounts for
  every byte (with `--compose`, it also checks every cached frame against the composed keys). A loose mesh's chained
  mesh is a direct `PMS2` child; a resource archive's wraps it in `PMSH`, `PMS2` and the 309-byte reference, and the
  walk follows both;
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
- Model transforms: `model_transform_catalog.py` produces, for selected loose PC meshes, a private per-part report that
  identifies the reflected local keys (a stored parent-relative key whose basis has determinant -1) and the virtual-frame
  ranges whose `VHFM` entries refer to them. It reports stored keys, distinct referenced keys and frame references
  separately, and classifies bases that are not orthonormal within its stated tolerance separately. The report is metadata
  and hashes, with no matrix or geometry payload; its [v2 schema](model_transform_catalog.v2.schema.json) marks it as
  retail-derived, and the older [v1 schema](model_transform_catalog.schema.json) remains available for existing reports. The
  format facts and the finding are in
  [`asset-formats/cmsh-animation-keys.md`](../reverse-engineering/asset-formats/cmsh-animation-keys.md).
  Names are read from their bounded stored fields: the 300-byte `CMesh::mName` at CMSH payload `+0x24` and the 32-byte
  `CMeshPart::mName` at CMSP payload `+0xdc` (the declarations in onslaught-decomp `src/mesh.h`). An empty part name stays
  empty; it is not replaced by the preview parser's generated `part-N` label. For a terminated name the report hashes the
  bytes before the NUL and emits a text value only when those bytes decode as UTF-8, which is a lossless interpretation of the
  bytes, not proof of the game's display encoding. An invalid-UTF-8 or unterminated mesh name has a null text value and an
  explicit status, and an unterminated field has no name-byte hash. The underlying parser can refuse an invalid part name
  before a report is produced. Older v1 reports may contain a generated empty-part label or a replacement-decoded mesh name
  and should be regenerated before names are used as identifiers.
  `python tools/model_transform_catalog.py --mesh /path/to/selected.msh.aya --stdout` prints the private report to stdout
  and opens no report file; repeat `--mesh` to select more files. The `report_bytes` API returns deterministic UTF-8 JSON
  bytes, and the caller is responsible for privacy and any persistence: a shell opens a redirected destination before the
  tool runs, so the tool cannot protect the destination or prevent overwriting source data. Keep retail-derived reports
  private and out of Git. The selected-file reader requires Linux descriptor-relative `O_PATH` and `/proc/self/fd`, refuses
  `..`, symlinks in any source path component and files with multiple hard links, performs a bounded read of each and
  rechecks the file identities before it returns or emits the report. Those checks detect many changes but are not an atomic
  filesystem snapshot or a lock, so compare the recorded archive hash when using the result. `analyse_stream` accepts
  already-owned bytes on other platforms, the caller being responsible for source identity. The v2 schema checks the
  name/status/hash combinations but cannot verify a digest without the original bytes, and it checks structure and basic
  field limits, not semantic consistency among counts, parent/key ordinals or frame ranges. The report covers only the root
  stream's parent-relative keys: it counts nested mesh siblings without analysing them, and it does not establish that a game
  animation selects a frame, a reflected world transform or an export's fidelity.
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
