# CMSH tagged mesh-stream contract

Status: active format contract — complete corpus framing and bounded field
semantics; animation/skinning/general scene import remain partial
Date: 2026-08-22
Verdict: all 213 mesh streams frame and their complete tag population is
counted; selected geometry is bounded while PB*, animation, and skinning remain
partial.
Evidence: MEASURED — all 213 mirror-index mesh rows were re-aggregated on
2026-08-22. Field names below are either measured by repository parsers or
explicitly attributed to Stuart's AYAResourceExtractor lineage.
Specimen: `G:\bea-asset-mirror\INDEX.jsonl`, SHA-256
`c45722aeed52e77788c7886cb30b813900d3516b1c387983c442d2b02d4fe4b9`;
retail VAs cite `BEA.exe.original.backup`, SHA-256
`74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`.

## Population and envelope

All **213** files are `resources/meshes/*.msh.aya`. Each first passes the PC
AYA envelope in [aya-container.md](aya-container.md), and the concatenated
inflated bytes begin `CMSH`.

A CMSH stream uses repeated eight-byte chunk headers:

```text
char tag[4]
u32le payload_size
byte payload[payload_size]
```

The 2026-07-31 mirror index reports 194 rows `ok` and 19 `unsupported`. All 19
still passed AYA inflation and bounded tag walking, and that decoder label is
now historical rather than the current capability boundary. The tracked
`cmsh_static_preview_tests.py` gate parses and emits all 213 loose meshes; its
larger stream census parses 213 loose + 15 loose-nested + 139 embedded = 367
streams, emits OBJ for 366 (one is an explicit empty-geometry placeholder), and
round-trips all 367 CMSH streams byte-identically. The mirror status is retained
as a dated decoder result, not as a claim that 19 current inputs remain blocked.

## Measured tag census

The 2026-08-22 aggregate counts nested observed tags, so its large PB-family
numbers are not comparable to the older 5,494-chunk shallow summary:

| Tag | Occurrences | Files containing tag | Current interpretation |
| --- | ---: | ---: | --- |
| `CMSH` | 213 | 213 | mesh stream owner |
| `CMST` | 213 | 213 | texture-list/root metadata |
| `MESP` | 3,774 | 213 | mesh-part wrapper |
| `PMVB` | 3,774 | 213 | per-part vertex-buffer container; child geometry schema is profile-bounded |
| `MSHT` | 887 | 213 | material/texture block |
| `TEXB` | 887 | 213 | texture binding; fixed 128-byte name decoded, remaining fields partial |
| `BBOX` | 7,974 | 213 | part bounds records |
| `CMSP` / `CMVB` | 3,774 each | 213 | part state / vertex-buffer owner |
| `IBUF` / `MMPT` / `TEXR` / `VBUF` | 2,593 each | 213 | geometry/material arrays |
| `CHLD` / `PRNT` | 1,296 / 3,561 | 155 each | hierarchy relations |
| `REFR` | 388 | 44 | part instancing/reference |
| `VHFM` / `HORI` / `HPOS` | 3,774 each | 213 | vertex/orientation/position frame lanes |
| `CPOS` | 3,736 | 213 | derived model-space position cache, indexed by virtual frame |
| `CORI` | 2,514 | 213 | derived model-space orientation cache, indexed by virtual frame |
| `HFOV` | 17 | 17 | camera field-of-view frames |
| `BONE` / `PMS2` | 7 each | 7 | bone/skeletal lane |
| `CAMD` / `CEMT` | 61 / 126 | 61 / 126 | camera/end metadata |
| `NMIC` | 2 | 1 | chain metadata |
| `PBPP` | 515,988 | 213 | opaque PB-family element stream |
| `PBKE` | 171,996 | 213 | opaque PB-family element stream |
| `PBCS` | 69,863 | 213 | opaque PB-family element stream |
| `PBET` / `PBSQ` | 46,043 each | 213 | opaque PB-family element streams |
| `CPBT` / `PBFK` / `PBKT` / `PBPN` / `PLQT` / `SIZS` | 1,782 each | 213 | bounded vocabulary; semantics incomplete |

The `CPOS` / `CORI` cache interpretation comes from the exhaustive 213-mesh
composition check in
[`cmsh-cpos-cori-identity-2026-07-25.md`](../binary-analysis/cmsh-cpos-cori-identity-2026-07-25.md);
the occurrence and file counts above come from the current aggregate census.
PB* recognition is not a decoded schema. The cheapest next artifact is a
per-instance geometry ledger with offset, length, parent tag, consumer, and
opaque-byte disposition.

## Bounded field contracts

The following are tool/source contracts from
[`game-assets/aya-asset-format.md`](../game-assets/aya-asset-format.md), retained
with that provenance rather than promoted to released-runtime behavior:

- The `CMSH` root payload is 372 bytes. The tracked parser reads texture count
  at payload `+0x04`, a NUL-padded mesh name beginning at `+0x24`, and part
  count at `+0x15C`; all other header bytes remain opaque/carried. Every shipped
  stream has nonzero opaque header data, beginning with a `0x0000DEAD` guard at
  `+0x00`, so those bytes must not be called reserved-zero.
- Exactly `part_count` `MESP` records follow; the first child `CMSP` payload is
  316 bytes. Re-emission keeps opaque bytes rather than manufacturing meaning.
- `CMSP` carries current/base orientation matrices, offset/base positions,
  part number/type, child and geometry counts, animation-frame counts, bone
  count, and a 32-byte part name. Several offsets remain unnamed.
- `CHLD` is a `u32` child-index array; `PRNT` is one `u32` parent index;
  `REFR` is one referenced-part index used by repeated geometry.
- `IBUF` is a `u16` index array. The common vertex form is 36 bytes:
  `float3 position`, `float3 normal`, packed ARGB, `float u`, `float v`.
  A 48-byte form adds twelve bytes whose exact bone-weight interpretation is
  not fully established.
- `TEXR` stores six texture IDs. `TEXB` includes a fixed 128-byte texture name.
- Triangle strips and 16-bit indices are supported by the extractor path;
  not every topology is proved supported by the retail runtime or rebuild.

## Animation and skinning boundary

There is no standalone `.anim` file family in the 5,464-file mirror. Animation
is embedded in CMSH: `VHFM`, `HORI`, `HPOS`, `HFOV`, `BONE`, and related tags.
The dedicated
[animation, skeleton, and authored-usage contract](cmsh-animation-usage.md)
hash-verifies the 213 loose meshes, 66 numeric LVLR archives, and 733 MSL files.
It measures 64 meshes / 659 parts with non-trivial `VHFM` maps, seven one-part
`BONE` carriers, 17 one-value camera `HFOV` lanes, 3,432 named numeric-LVLR
membership joins, and 56 authored `PlayAnimation*` calls. Those are storage and
reference contracts, not universal scheduling or render proof.
The retail image has no `HFOV` fourcc literal because
`CMeshPart__LoadFromStream @ 0x004B27A0` consumes the keyframe sequence largely
positionally. The measured note
[`player-camera-attach-and-mesh-hfov-2026-07-26.md`](../binary-analysis/player-camera-attach-and-mesh-hfov-2026-07-26.md)
bounds that one path; it does not close general animation.

The seven `BONE` arrays are now bounded as same-mesh part indices: exactly part
1 carries 14, 18, or 19 indices, and the indexed CMSP part names form either a
`Bip01` humanoid skeleton or the Sentinel arm's `Bone01`…`Bone14` chain. In the
48-byte vertex form, the three words at `+0x0C` are exact `BONE index × 3`
matrix-palette slots. Their blending/weight semantics and bind matrices remain
open.

Retail static routes include:

| VA | Identity | Boundary |
| --- | --- | --- |
| `0x004B27A0` | `CMeshPart__LoadFromStream` | Positional mesh-part/keyframe consumer with selected tag checks. |
| `0x0054E160` | `CDXMeshVB__Load` | Reads ten fields through `CChunkReader__Read` and six tags through `GetNext`. |
| `0x0054C0A0` | `CDXMeshVB__BuildStaticVB` | Static vertex-buffer construction. |
| `0x0054C920` | `CDXMeshVB__BuildSkeletalVB` | Skeletal vertex-buffer construction. |

The address summary is in
[`coordinate-long-tail.md`](../binary-analysis/functions/coordinate-long-tail.md).

## Decoder/tool entry points

- [`tools/BeaAssetExportHarness/Program.cs`](../../tools/BeaAssetExportHarness/Program.cs)
  loads the pinned AYAResourceExtractor assemblies and enumerates all loose mesh
  AYA files.
- [`tools/aya_archive_inventory.py`](../../tools/aya_archive_inventory.py)
  performs fail-closed AYA/tag framing and labels carved embedded CMSH bodies
  candidate-only.
- [`rebuild/tools/cmsh_static_preview.py`](../../rebuild/tools/cmsh_static_preview.py)
  and its focused tests parse, emit OBJ for the supported geometry surface, and
  byte-round-trip all 367 measured streams. The byte-accounting gate attributes
  32.05% of 100,813,615 stream bytes to typed model state and 67.95% to honest
  opaque carry-through; byte identity is not semantic completeness.
- [`tools/cmsh_animation_usage_census.py`](../../tools/cmsh_animation_usage_census.py)
  joins the loose frame/skeleton lanes to numeric-LVLR `MESH` membership and
  authored MSL animation calls, with synthetic can-fail tests and an optional
  hash-pinned full-corpus gate.
- The dedicated rebuild Aquila consumer is exact and specimen-bounded; it is not
  a general CMSH importer.

## Open questions and falsifiers

- Name every PB* payload field by joining one exact part to its retail consumer;
  tag frequency alone is insufficient.
- Recover the three-slot blend/weight rule, bind pose, animation interpolation,
  and malformed hierarchy behavior for the seven bone-bearing files. Bone and
  palette-slot indices themselves are now bounded by the dedicated contract.
- Establish every remaining topology/FVF combination with a cross-check between
  bytes, static loader branches, and rendered output.
- Trace the population of the runtime named-animation table at
  `CMesh+0x14/+0x18`; MSL requests and `VHFM` pose maps are separate evidence
  until their exact frame-range records are joined.
- Resolve the apparent repeated `BBOX` writer behavior without assuming it is a
  harmless exporter bug.
- Test a non-Level-100 static mesh and one skeletal mesh in a disposable copied
  profile before claiming general runtime parity.

## Claim boundary

The container walk, corpus population, tag counts, hierarchy/reference shapes,
selected geometry fields, pose-map dimensions, bone-to-part names, palette-slot
indices, and numeric-LVLR membership are bounded. Named clips, weights/blending,
general scheduling/rendering, complete scene dependencies, collision,
malformed-input behavior, pixels, and parity are open.
