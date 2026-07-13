# CMSH Profile V0 Geometry Preview Design

**Status:** Approved by the primary task on 2026-07-13

## Milestone

Deliver **local static Aquila geometry preview on procedural terrain**. A
public-safe generated fixture proves the pipeline first; optional retail input
uses only the ignored `local-lab/rebuild-godot/` workspace. The tracked result
contains no retail bytes, paths, hashes, names, screenshots, or derived assets.

This milestone does not add playable Aquila, textured fidelity, full CMSH
support, or parity. It does not use Visual Studio, Blender, legacy extractor
DLLs, FBX, DDS, textures, GLB, LNDS, animation, bones, or Core changes.

## Architecture And Data Flow

The implementation stays in the Python tooling lane, outside
`OnslaughtRebuild.Core` and `OnslaughtRebuild.Client`:

1. Reuse the archive framing, zlib inflation, top-level chunk parsing, and
   `MESH`/`PMSH`/`PMS2` to `CMSH` body-carve rules from
   `tools/aya_archive_inventory.py`, adding bounded APIs rather than invoking
   payload or native tools.
2. Parse one carved body with the new fail-closed **CMSH profile v0** parser.
   Its output is an immutable geometry model: ordered parts, transformed
   positions, and ordered triangle lists. It contains no material, texture,
   animation, or simulation data.
3. Emit one deterministic geometry-only OBJ accepted by the existing
   `LocalMeshSafety` and `LocalAssetMeshLoader` path.
4. Publish that OBJ through the existing ignored local player role. First
   Flight retains procedural terrain and all simulation truth from Core.

Ordinary rebuild tests and smoke remain synthetic and never discover or read a
local game install. The local retail route requires an explicit input and an
explicit ignored output root; it reads the source and writes only beneath the
validated local workspace.

## CMSH Profile V0

All integers and IEEE-754 floats are little-endian. Every offset, chunk length,
count, multiplication, and addition is checked before slicing or allocation.
Chunk lengths must cover exactly the bytes consumed by their declared profile;
trailing or overlapping data fails.

The accepted body has this exact order:

1. Fixed `CMSH` header: tag at `0x00`, texture count at `0x0c`, 300-byte name
   field at `0x2c`, part count at `0x164`, and `CMST` at `0x17c`.
2. The declared `CMST` payload is exactly `texture_count * 36` bytes, followed
   by exactly `texture_count` `MSHT` then `TEXB` records. Texture data is
   validated and skipped; it is never emitted.
3. Exactly `part_count` parts follow. Each is `MESP`, `CMSP`, an exact
   `0x13c`-byte static transform/count record, then `PMVB`, `CMVB`, and exactly
   the declared number of `MMPT` groups. Frame and bone counts and all
   child/parent/chain/reference counts must be zero; `PMVB` must immediately
   follow `CMSP`. Serialized pointer/reserved slots must be zero, part numbers
   must be contiguous, and the part vertex/triangle counts must equal the sums
   declared by its groups.
4. The `CMVB` payload is exactly `0x128` bytes: 264 opaque bytes, one u8 group
   count plus three zero padding bytes, eight opaque bytes, u32 stride, u32 FVF
   value, u32 primitive value, and eight trailing opaque bytes. The group count
   must be nonzero; all opaque/reserved bytes must be zero; stride is `36`;
   FVF is `0x152` (`XYZ | NORMAL | DIFFUSE | TEX1`); and primitive is Direct3D
   triangle strip value `5`.
5. Each `MMPT` group is its fixed six-u32 header followed by `IBUF`, exactly
   `index_count` unsigned 16-bit indices, `VBUF`, exactly
   `vertex_count * 36` bytes, then `TEXR` with exactly six u32 values. Only the
   geometry within that group supplies its indices and vertices; groups are
   concatenated in file order and never share inferred state.
6. The body ends exactly after the declared parts at the already-carved sibling
   boundary.

The only vertex stride is 36 bytes:

| Offset | Field |
| --- | --- |
| `0x00` | finite float32 position `x, y, z` |
| `0x0c` | finite float32 normal `x, y, z` (validated, not emitted) |
| `0x18` | u32 packed color (validated, not emitted) |
| `0x1c` | finite float32 `u, v` (validated, not emitted) |

Profile v0 accepts only static triangle-strip geometry. The generated fixture
records every required numeric constant as an assertion, not a permissive enum.
Any other stride, FVF value, tag, ordering, required field, primitive value,
hierarchy, bones, bone tag, `REFR` graph, truncated record, nonzero required
padding, or undeclared bytes fails the complete conversion. There is no
best-effort part skipping.

## Bounds And Geometry Policy

Hard limits apply before allocation: 64 MiB source AYA, 128 MiB total inflated
bytes, 32 MiB carved CMSH body, 256 parts, 100,000 aggregate vertices, 600,000
aggregate source indices, 400,000 emitted triangles, and 32 MiB OBJ. Per-record
counts must also fit their enclosing declared byte length. Positions, normals,
UVs, transforms, transformed positions, and computed bounds must be finite;
absolute coordinates above `1,000,000` fail. Every index must be below its
group's vertex count.

For source strip indices `s[0..n-1]`, triangle ordinal `k` uses
`(s[k], s[k+1], s[k+2])` when `k` is even and
`(s[k+1], s[k], s[k+2])` when `k` is odd. A triangle with any repeated index is
degenerate and is omitted; all other triangles retain order. Fewer than three
indices is an error. The declared primitive count must equal `index_count - 2`
before degenerate removal.

Source coordinates are treated as left-handed, Y-up, at source scale. Part
base orientation and position are applied in source space. Emission maps
`(x, y, z)` to Godot/OBJ `(x, y, -z)`, reverses each surviving triangle once to
preserve its front face across the handedness change, and performs no
centering, normalization, inferred unit conversion, or visual correction.
Existing manifest scale/yaw/offset remain presentation settings and cannot be
used as format evidence or fed back into fixture expectations.

## OBJ Contract

Output is UTF-8 without BOM, LF-only, invariant-culture decimal text, with one
canonical shortest round-trippable representation for each float and a final
newline. It contains only ordered `v x y z` statements followed by triangular
`f a b c` statements using positive one-based indices. It emits no comments,
names, `vn`, `vt`, `o`, `g`, `s`, `mtllib`, `usemtl`, external references, or
polygons. The emitter precomputes the exact byte count and refuses output above
the cap. The complete file must pass `LocalMeshSafety.ValidateObjBytes` before
publication.

## Errors

Errors are deterministic, path-free categories with the body-relative offset
and field/tag role: unsupported profile, invalid framing, limit exceeded,
unexpected tag/order, invalid declared length/count, unsupported topology,
unsupported bones/reference graph, non-finite numeric value, index out of
bounds, truncation, or OBJ rejection. Public tests assert categories and
offsets, not machine paths or private identifiers. Failure produces no partial
OBJ or active manifest generation.

## Verification And Acceptance

Parser and emitter work is test-driven with a generated fixture and an exact
golden OBJ SHA-256. The fixture oracle also asserts finite vertices, all index
bounds, post-degenerate triangle count, transformed bounding box, aspect-ratio
tolerances, exact OBJ grammar, and loader acceptance. Malformed cases cover
every cap plus bad compression framing, chunk overrun, count/length overflow,
wrong/missing/reordered tags, unknown stride, wrong primitive, NaN/Inf,
out-of-range index, short strip, bones, references, trailing bytes, and every
truncation boundary.

One end-to-end public fixture packs the accepted geometry through synthetic
AYA compression and the exact `MESH`/`PMSH`/`PMS2`/`CMSH` route, then compares
the emitted OBJ digest. No native process or retail input is needed for this
gate.

Local acceptance is a separate ignored one-player-role run. It confirms a
nonempty loader-accepted mesh on unchanged procedural terrain, exercises the
existing movement, fire, transform, and reset actions, and ends with zero owned
processes. Human visual inspection is secondary confirmation only; it cannot
override the objective oracle or expand the profile. Closeout also requires
focused parser/emitter and rebuild tests, payload safety, and independent
normal/adversarial review.

## Rejected Alternatives

- **Legacy extractor plus Blender:** requires the blocked native/legacy toolchain,
  FBX staging, and manual conversion, while inheriting known coverage and
  provenance ambiguity beyond this geometry slice.
- **OBJ with MTL/PNG sidecars:** adds texture decode, naming, path, material,
  and multi-file publication contracts that profile v0 neither needs nor proves.
- **Immediate GLB and textures:** couples mesh parsing to DDS/material/glTF work,
  weakens the objective geometry oracle, and blurs this milestone with later
  fidelity work.

## Provenance And Future Contracts

The implementation is original GPL rebuild tooling. It may use the pinned
legacy importer and Stuart source only as labeled hypotheses; it must not copy,
port, mechanically translate, link, or revive their implementation. Steam
static evidence bounds released-format claims, the generated fixture proves
only its exact profile, and an authorized ignored local run proves only the
selected bytes and observed loader result.

Later work requires separate contracts for: a selected-DDS observed-BC decoder
feeding a self-contained textured GLB; `LNDS` terrain; and measured movement,
camera, handling, or scale. None is part of this milestone's done bar.
