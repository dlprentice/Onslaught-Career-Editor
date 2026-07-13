# CMSH Static-Preview Profile V0 Design

**Status:** approved direction, revised from sanitized corpus evidence

**Supersession:** This document supersedes the design committed as `3f6c41c4`.
That version described a synthetic-only profile as though it could be the retail
Aquila route. A read-only, path/name/hash-redacted inventory of all 213 ignored
loose mesh archives showed that zero observed bodies matched its strict
topology, record-order, zero-field, or independent-VBUF assumptions.

## Milestone And Identity Boundary

Deliver an original-code, geometry-only **CMSH static-preview profile v0** with
a generated public-safe fixture, exact fail-closed parser, deterministic OBJ
emitter, and bounded ignored local preview route. Profile support and asset
identity are separate claims:

- the generated fixture proves only this parser/emitter contract;
- an ignored local conversion proves only that selected local bytes match the
  profile and produce pure-validator-accepted OBJ geometry;
- separately leased native Godot acceptance proves only that the selected OBJ
  is accepted by the runtime loader in that run;
- a local human contact sheet may identify an Aquila candidate visually;
- neither structure nor a successful conversion establishes Aquila identity.

No candidate has been selected. Tracked Steam-static and source-crosswalk docs
establish mesh loading/name fields and corpus coverage, but do not publish a
deterministic player-Aquila asset identity. Reference-source behavior remains a
hypothesis, not format or identity authority.

This milestone does not add playable Aquila, textures, GLB, LNDS terrain,
animation playback, bone skinning, reference-part instancing, measured scale,
camera or movement behavior, parity, Visual Studio, Blender, legacy DLLs, or
Core changes.

## Sanitized Observed-Corpus Decision

The authorized ignored inventory parsed 213 of 213 loose archives without
publishing paths, names, hashes, bytes, screenshots, or identity claims:

- 3,774 `MESP` parts: 1,782 populated `PMVB`, 1,992 empty `PMVB`;
- 2,593 `MMPT` groups, all with bounded `IBUF`, in-range indices, `active=1`,
  and `primitive_count = index_count - 2`;
- 206 bodies use only stride `36`, FVF `0x152`, and topology field `4`;
- among those 206, 104 use first-VBUF ownership plus zero-payload secondary
  VBUF reuse and 102 use only first-owned VBUF;
- all 811 secondary groups repeat the first group's vertex count and declared
  vertex-byte size while their own `VBUF` payload length is zero;
- seven bodies include the separate stride-48/FVF-0 family;
- all bodies contain frame records; 155 contain child hierarchy, 44 contain
  `REFR`, and seven contain bones;
- the 213 post-part sibling streams have six exact tag orders using `BBOX`,
  `CEMT`, `CAMD`, and `PMS2`;
- physical per-body vertices are 17..14,862, groups 1..122, indices
  24..23,407, and declared primitives 22..23,327;
- positions and normals are finite; one owned buffer has non-finite UV data;
  maximum observed absolute source position is below 78.

Profile v0 deliberately selects the common stride-36, no-bone, no-`REFR`,
finite-UV structural subset. It currently matches 162 anonymous local bodies.
That count is a breadth check only; none is labeled Aquila.
These local-corpus aggregates are design inputs, not a public-clone acceptance
gate. The generated fixture is the profile authority. The later bounded local
enumerator reproduces the aggregate match count from an explicitly supplied
corpus while keeping its path-to-anonymous-label mapping ignored.

## Architecture And Data Flow

The implementation stays in GPL Python tooling under `rebuild/tools/`, outside
`OnslaughtRebuild.Core` and the Godot client. This keeps ownership consistent
with `rebuild/PROVENANCE.md`; root `tools/` remains the existing MIT lane.

1. Add original bounded archive inflation and CMSH-envelope APIs in
   `rebuild/tools/cmsh_static_preview.py`; do not invoke native or payload
   tools. Root `tools/aya_archive_inventory.py` is an inventory cross-check,
   not an imported implementation dependency.
2. Parse one inflated loose CMSH stream into immutable ordered parts, each with
   one optional owned vertex pool and ordered triangle-strip groups.
3. Emit one deterministic geometry-only OBJ accepted by the pure
   `LocalMeshSafety` contract. `LocalAssetMeshLoader` acceptance is deferred to
   the separately leased native Godot step and is not part of ordinary or
   generated verification.
4. For an explicit ignored local input root, enumerate only matching bodies to
   an ignored output workspace using anonymous local labels.
5. Generate ignored thumbnails/contact sheets for human identity selection in
   a later separately leased local presentation step. Publication activates
   only the explicitly human-selected candidate OBJ as the local player role;
   procedural terrain remains intact.

Ordinary tests and smoke use generated fixtures and never discover a game
install. The local route requires explicit input and output roots, reads only
the supplied archives, and writes only beneath a validated child of
`local-lab/rebuild-godot/`. It reuses the secured generated-output and local
asset workspace contracts: source/output must be disjoint; source and output
components must use non-reparse directories and regular single-link files;
game, source-tree, and installed-game output targets are rejected; publication
uses held handles plus same-directory temporary files and atomic replacement.

## Archive And CMSH Envelope

All integers and IEEE-754 floats are little-endian. Every offset, length, count,
multiplication, addition, decompression result, and allocation is checked
before use.

The AYA input is exactly a contiguous sequence of
`[u32 compressed_length][zlib member]` records with no trailing bytes. Each
compressed member must fit its record, independently reach zlib EOF without
unused or unconsumed data, and inflate below the remaining cap. Member outputs
concatenate in record order into one CMSH stream.

The inflated loose stream has this exact envelope:

1. `CMSH` with payload length `372`. CMSH body offsets are always relative to
   the chunk start at byte zero, including its eight-byte tag/length header.
   Its u32 texture count is at body offset `0x0c`, 300-byte opaque name field at
   `0x2c`, u32 part count at `0x164`, and the next chunk begins at `0x17c`.
2. `CMST` payload length is exactly `texture_count * 36`.
3. Exactly `texture_count` `MSHT` containers follow. Each has payload length
   `156` and contains exactly one `TEXB` chunk of payload length `148`.
   Texture metadata and names are validated as bounded bytes and not emitted.
4. Exactly `part_count` declared `MESP` containers follow.
5. The CMSH body ends after the last declared `MESP`, not at inflated EOF.
6. A zero-length remainder is accepted. A nonempty remainder must be one of
   the six observed exact sibling orders:
   `BBOX`; `BBOX,CEMT`; `CAMD,BBOX`; `CAMD,BBOX,CEMT`;
   `BBOX,PMS2`; or `CAMD,BBOX,CEMT,PMS2`. These siblings remain outside the
   CMSH model. Each is an eight-byte ASCII-tag/u32-length header plus exactly
   that many payload bytes. Every payload must fit the remaining stream and
   opaque-chunk cap, the final chunk must end at inflated EOF, and any unknown,
   repeated, or out-of-order tag is `unexpected tag/order`. Payloads are
   otherwise opaque; nested interpretation is out of profile.

This derived body boundary replaces the old `CMSH`-to-EOF carve rule.

## Part Profile

Each `MESP` payload contains exactly one `CMSP` chunk of payload length `316`,
then exactly one of these 16 complete observed no-bone/no-reference tag orders:

```text
PRNT BBOX VHFM HORI HPOS CPOS CORI PMVB
CHLD PRNT BBOX VHFM HORI HPOS PBKT CPOS PMVB
PRNT BBOX VHFM HORI HPOS PBKT CPOS PMVB
PRNT BBOX VHFM HORI HPOS CPOS PMVB
PRNT BBOX VHFM HORI HPOS PBKT CPOS CORI PMVB
CHLD PRNT BBOX VHFM HORI HPOS PBKT CPOS CORI PMVB
CHLD BBOX VHFM HORI HPOS PBKT CPOS CORI PMVB
BBOX VHFM HORI HPOS PBKT CPOS CORI PMVB
CHLD BBOX VHFM HORI HPOS CPOS CORI PMVB
CHLD PRNT BBOX VHFM HORI HPOS PBKT PMVB
PRNT BBOX VHFM HORI HPOS PBKT PMVB
PRNT BBOX VHFM HORI HPOS HFOV CPOS CORI PMVB
PRNT BBOX VHFM HORI HPOS PMVB
PRNT NMIC BBOX VHFM HORI HPOS PBKT CPOS PMVB
CHLD PRNT BBOX VHFM HORI HPOS CPOS CORI PMVB
CHLD PRNT BBOX VHFM HORI HPOS CPOS PMVB
```

The parser matches the complete sequence, not an independently optional
superset. Missing required, repeated, reordered, or unknown tags fail. `BONE`,
`BONW`, `BONS`, or `REFR` fail as unsupported-profile categories rather than
being skipped.

The `CMSP` payload has this normative little-endian layout; other ranges are
bounded opaque bytes:

| Payload offset | Field |
| --- | --- |
| `0x00` | current orientation, 3 x vec4 float32 |
| `0x30` | base orientation, 3 x vec4 float32 |
| `0x60` | offset position, vec4 float32 |
| `0x70` | base position, vec4 float32 |
| `0x88` | u32 `partNum` |
| `0x8c` | u32 `partType` |
| `0x90` | u32 `numChildren` |
| `0xa8` | u32 `numDVert` |
| `0xac` | u32 `numPVert` |
| `0xb0` | u32 `numTris` |
| `0xb4` | u32 `numAFrames` |
| `0xb8` | u32 `numVFrames` |
| `0xbc` | u32 `numHFrames` |
| `0xc0` | u32 `numBones` |
| `0xdc` | 32-byte opaque part-name field |

This agrees with the tracked hypothesis in
`reverse-engineering/game-assets/aya-asset-format.md`. Profile v0 requires:

- finite XYZ components for current/base orientations and offset/base
  positions; vec4 W components and other unknown blocks are bounded opaque
  fields, not required-zero padding;
- each `partNum` equals its zero-based `MESP` ordinal, yielding unique
  contiguous values `0..part_count-1`; hierarchy u32 indices address that same
  MESP ordinal/part-number domain;
- observed `partType` values `1..6` only;
- `numChildren <= 256`, `numAFrames <= 2`, `numVFrames <= 512`, and
  `numHFrames <= 256` before any dependent multiplication;
- `numDVert`, `numPVert`, and `numTris` equal zero; geometry counts come only
  from `MMPT`, so they are not compared with invented sums;
- `numBones` equal zero;
- `CHLD` is present if and only if `numChildren > 0`; its length is exactly
  `numChildren * 4`, with every child index in range. Absence requires
  `numChildren = 0`;
- `PRNT` and `NMIC` length exactly four with an in-range part index;
- outer `BBOX` payload length exactly `48`, containing exactly one inner
  `BBOX` header with payload length `40`; the inner payload is opaque and ends
  exactly at the outer boundary, with no recursive nesting;
- `numVFrames` and `numHFrames` are nonzero because their required chunks are
  present;
- `VHFM` length equals `numVFrames`, `HORI` length equals
  `numHFrames * 48`, `HPOS` length equals `numHFrames * 16`, and optional
  `HFOV` length equals `numHFrames * 4`;
- `PBKT`, `CPOS`, and `CORI` are recognized bounded opaque chunks whose
  declared payload must fit the enclosing `MESP` exactly.

The arbitrary byte content and `0..16 MiB` declared lengths of `PBKT`, `CPOS`,
and `CORI` are an intentional original profile policy because the bytes are
never interpreted or emitted. The parser makes no claim that every accepted
opaque value occurred in retail. Tests cover zero, nonzero, cap, and cap-plus-
one lengths while rejecting every unlisted tag order and every leftover byte.

Hierarchy validation is structural only: indices and count/presence
relationships are checked, but cycles, duplicate children, and inverse
parent/child consistency are not interpreted because hierarchy is not used for
geometry. Frame chunks are likewise validated and skipped. Profile v0 applies
only the part's serialized base orientation and base position; it does not
compose parent transforms or play frames. A visually displaced local result is
"no selectable preview candidate," not evidence that an identity is absent.

## Vertex Buffer And Reuse Profile

`PMVB` is an exact container. Its first child is `CMVB` with payload length
`296`. The payload contains 264 opaque bytes, one u8 group count plus three
opaque bytes, eight opaque bytes, u32 stride, u32 FVF, u32 topology, and eight
trailing opaque bytes. Opaque bytes are not required to be zero.

An empty `PMVB` has group count zero, contains no `MMPT`, and emits no geometry;
its stride/FVF/topology slots are opaque and not validated. Its `CMVB` must end
exactly at the `PMVB` boundary; any trailing byte or child header fails. A
populated `PMVB` requires stride `36`, FVF `0x152`, topology field `4`, and
`1..12` groups.
Field `4` is the observed selector; this design does not relabel it as a
Direct3D enum. Profile v0 interprets it as ordered triangle strips because the
observed count relation is `primitive_count=index_count-2` and the tracked
legacy source labels its index lists as strips. That interpretation is an
independently specified preview policy, not proven retail semantics.

Each group is exactly:

1. `MMPT` payload length `24`: six u32 fields in this exact order: declared
   VBUF bytes, declared IBUF bytes, index count, vertex count, primitive count,
   and active flag;
2. `IBUF` payload length `declared_ibuf_bytes = index_count * 2`;
3. `VBUF`;
4. `TEXR` payload length `24`, validated and ignored.

For the first group, `VBUF` payload length and declared VBUF bytes both equal
`vertex_count * 36`; this is the PMVB's single owned vertex pool. For every
secondary group, vertex count and declared VBUF bytes must equal the first
group's values while the actual `VBUF` payload length is exactly zero. All
groups index the first owned pool. Independent or duplicate secondary vertex
payloads fail; the parser never infers reuse from proximity.

Every group requires `active=1`, at least three indices,
`primitive_count=index_count-2`, and every u16 index below the owned vertex
count. After degenerate removal, every populated group must retain at least one
triangle. The complete `PMVB` must end after its declared groups with no
trailing bytes.

The stride-36 vertex record is:

| Offset | Field |
| --- | --- |
| `0x00` | finite float32 position `x, y, z` |
| `0x0c` | finite float32 normal `x, y, z` (validated, not emitted) |
| `0x18` | u32 packed color (validated, not emitted) |
| `0x1c` | finite float32 `u, v` (validated, not emitted) |

Stride 48, bones, references, and other vertex/topology families require later
contracts.

## Geometry And OBJ Policy

Let source position be `(x,y,z)`, the serialized base-orientation XYZ rows be
`(r00,r01,r02)`, `(r10,r11,r12)`, `(r20,r21,r22)`, and base-position XYZ be
`(bx,by,bz)`. Profile v0 evaluates these exact left-associated expressions:

```text
tx = (((r00 * x) + (r01 * y)) + (r02 * z)) + bx
ty = (((r10 * x) + (r11 * y)) + (r12 * z)) + by
tz = (((r20 * x) + (r21 * y)) + (r22 * z)) + bz
```

The OBJ position is `(tx,ty,-tz)`. This is the sole position handedness change;
no later emission step negates Z again. The pinned importer suggests the same
base operation, but is labeled source hypothesis rather than authority.
Parent/frame transforms are not applied.

For strip indices `s[0..n-1]`, triangle ordinal `k` is
`(s[k], s[k+1], s[k+2])` when even and `(s[k+1], s[k], s[k+2])` when odd.
Repeated-index triangles are degenerate and omitted; all others retain order.
The handedness reversal is exactly `(a,b,c) -> (a,c,b)` for each surviving
strip triangle.

Each populated part's owned vertex pool is transformed and emitted exactly
once in ascending part order, with no vertex deduplication. That pool's checked
global one-based OBJ base index is reused by all of the part's groups. After all
vertices, face rows are emitted in ascending part order, then group order, then
surviving strip-triangle order. Every emitted face index must be within
`1..emitted_vertex_count`. A body with no owned vertices or no surviving faces
fails before emission.

Source coordinates are treated as left-handed Y-up at source scale. The single
Z negation in the transform rule and exact `(a,b,c) -> (a,c,b)` face
permutation form the independently specified preview mapping, informed by the
tracked source hypothesis. It is not measured retail scale, orientation, or
parity evidence. No centering, normalization, inferred unit conversion, or
visual correction is allowed. Manifest scale/yaw/offset remain
presentation-only settings.

Float32 source values are decoded by CPython 3 to binary64. Each multiply and
add in the explicitly ordered transform expression uses normal Python binary64
semantics. Output uses CPython's shortest round-trippable binary64 `repr` for
finite nonzero values; both positive and negative zero serialize as `0`.

OBJ output is UTF-8 without BOM, LF-only and final-newline terminated. It
contains only ordered `v x y z` rows followed by triangular `f a b c` rows with
positive one-based indices. It emits no comments, names, normals, UVs, objects,
groups, materials, smoothing, external references, or polygons. The exact byte
count is checked before write, and the result must pass the stricter test-local
semantic contract whose literal golden output is also accepted by
`LocalMeshSafety.ValidateObjBytes`.

## Bounds And Errors

Limits are checked before allocation: 64 MiB source AYA, 128 MiB total inflate,
32 MiB CMSH body, 256 textures, 256 parts, 1,024 aggregate MMPT groups, 100,000
owned vertices, 600,000 indices, 200,000 emitted triangles, 16 MiB per opaque
chunk, and 32 MiB OBJ. Absolute transformed coordinates above 1,000,000 fail.
All parsed and transformed numeric values used by the profile must be finite.
The 200,000-triangle cap is the existing `LocalMeshSafety.MaxObjFaces` limit,
not a looser format claim.

Errors are deterministic and path-free. AYA framing and decompression failures
use archive-relative record/header offsets; parsed CMSH failures use
body-relative offsets. Each also names the field/tag role and one category:
unsupported profile, invalid framing, limit exceeded,
unexpected tag/order, invalid declared length/count, unsupported topology,
unsupported bones/reference graph, non-finite numeric value, index out of
bounds, truncation, or OBJ rejection. No partial OBJ, thumbnail, contact sheet,
or active manifest is published on failure.

## Generated Verification

Implementation is test-driven. Test fixture builders are independent of the
production parser/emitter: they duplicate the required tag, length, offset,
stride, FVF, and topology values as test-local literals and direct byte packing,
without importing production serializers, constant tables, or transform
helpers. Expected transformed vertices, complete OBJ text, and OBJ SHA-256 are
literal independently calculated oracles. Malformed fixtures mutate literal
byte offsets directly rather than asking production code to serialize the
invalid case. Review verifies that construction remains test-local rather than
"drying" the duplicated literals back into the production module.

One generated chunked-zlib AYA fixture inflates to a CMSH stream containing:

- texture metadata;
- a parent part with child/frame/opaque optional records and an empty PMVB;
- a child part with a nonidentity base transform, one owned VBUF, two MMPT
  groups, and exact zero-payload secondary reuse;
- a post-body sibling chunk proving the derived CMSH boundary.

The oracle asserts every constant, tag boundary, finite vertex, index bound,
strip/degenerate triangle, transformed bounding box, exact OBJ grammar, exact
OBJ SHA-256, and a stricter test-local Python OBJ semantic validator. A focused
test in the non-engine `OnslaughtRebuild.Client.Tests` host, which directly
links `LocalMeshSafety.cs` without referencing the Godot project, feeds the
same literal golden OBJ bytes to `LocalMeshSafety.ValidateObjBytes`. Neither
gate constructs Godot `SurfaceTool`, `ArrayMesh`, or `LocalAssetMeshLoader`.
Generated positive variants cover a first-owned single-group PMVB, all accepted
optional tags, all 16 complete part orders, zero and all six allowed sibling
remainders, and the primary first-VBUF-reuse path. Actual loader acceptance
remains under a later exclusive native Godot lease.

Malformed cases cover every cap plus bad compression framing, incomplete zlib,
chunk overrun, header/count overflow, missing/reordered/repeated tags, invalid
hierarchy index, mismatched frame length, bones, `REFR`, stride 48, wrong FVF or
topology, nonzero secondary VBUF payload, mismatched reuse declaration, NaN/Inf,
out-of-range index, short strip, wrong primitive count, trailing bytes, OBJ
rejection, every truncation boundary, every unlisted part/sibling transition,
and residual bytes after empty and populated containers. A table-driven grammar
test enumerates all accepted complete sequences and rejects all single-tag
insertions, deletions, duplications, and swaps. Opaque bytes are the only
deliberately value-open region; topology, reuse, transform, counts, and framing
cannot broaden without changing a positive or negative fixture expectation.

## Local-Only Candidate Selection

After generated acceptance and a separate path lease, a bounded local command
may nonrecursively scan at most 256 regular, non-reparse, single-link files
whose final extension is case-insensitively `.aya`. The input directory must be
a validated child of the checkout's ignored `game/` copied-payload root or
`local-lab/rebuild-godot/input/`; installed-game, source-managed, arbitrary
external, and output-tree inputs fail before enumeration. Aggregate source
bytes are capped at 256 MiB and each file retains the 64 MiB source cap.
Enumeration is sorted only for stable anonymous
local labels; those labels and their path mapping remain ignored. The input
directory and every candidate are held/revalidated through the read, and output
is confined to a disjoint guarded child of `local-lab/rebuild-godot/`. Only
complete profile matches receive atomic OBJ publication; failures produce an
aggregate path-free category count stored only in the ignored local workspace.

A separately leased rendering step then produces anonymous ignored
thumbnails/contact sheets and asks the user to identify the Aquila visually;
using Godot for that step requires the exclusive native Godot lease. Local
mappings, names, paths, bytes, hashes, OBJ files, images, and selection
manifests remain ignored and untracked.

If the Aquila is not present among the profile matches, selection stops. A
separate reviewed profile expansion may then add `REFR`, stride 48, or bones;
the tool must not guess an ordinal or silently broaden v0. Before human
selection, outputs are anonymous candidates and are never called player assets.
After human selection, only the ignored player-role manifest is activated.
Procedural terrain remains unchanged unless a separate terrain requirement is
proven.

Native Godot acceptance requires an explicit exclusive lease. It confirms a
nonempty loader-accepted selected mesh on procedural terrain, exercises the
existing movement, fire, transform, and reset actions, and ends with zero owned
processes. Visual recognition establishes only the local identity choice; the
generated fixture remains the format oracle.

## Provenance And Deferred Work

The implementation is original GPL rebuild tooling. The pinned legacy importer
and Onslaught source may suggest vocabulary or hypotheses but are not copied,
ported, linked, revived, or treated as released-format authority. See
`reverse-engineering/source-code/reference-submodule-audit-2026-07-12.md` and
`reverse-engineering/game-assets/aya-asset-format.md` for the current boundary.

Selected DDS/textured GLB, `LNDS`, reference instancing, stride 48, bones,
animation, measured scale/camera/movement, and parity are separately bounded
future contracts.
