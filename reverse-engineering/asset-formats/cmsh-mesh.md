# CMSH tagged mesh-stream contract

Status: active format contract — complete PC corpus framing, bounded PC fields,
and complete released PS2 material-binding population; position and
linked-shader normal skinning laws are closed while animation/general scene
import remain partial
Date: 2026-08-28
Verdict: all 213 PC mesh streams frame and their complete tag population is
counted; the PS2 shelf closes 3,547 meshes and 14,028 material bindings across
307 unique AYA identities, while PB* and animation scheduling remain partial.
Evidence: MEASURED — all 213 mirror-index PC mesh rows were re-aggregated on
2026-08-22; the complete named PS2 demo/Europe/USA package population was
streamed and independently replayed on 2026-08-28. Field names below are
either measured by repository parsers or explicitly attributed to Stuart's
AYAResourceExtractor lineage.
Specimen: `G:\bea-asset-mirror\INDEX.jsonl`, SHA-256
`c45722aeed52e77788c7886cb30b813900d3516b1c387983c442d2b02d4fe4b9`;
retail VAs cite `BEA.exe.original.backup`, SHA-256
`74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`;
PS2 package specimens are the demo `DATA0.NYO`, SHA-256
`6d503ca251a4b00a5ebcfa447036075f6b1d563c9f55ea7ab784e7db4b6f3d3c`,
and the byte-identical Europe/USA retail `DATA0.NYO`, SHA-256
`dc02e657cb6e405c7228c54191d2ca37419c63b4d442a22a9a52b8ef0ab34f99`.

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
  A 48-byte form adds three float matrix-palette offsets. Each is exactly
  `3 *` an in-range index in that part's `BONE` array. The released position
  blend is owned by the focused
  [matrix-palette contract](cmsh-matrix-palette-skinning.md).
- In the PC profile, `TEXR` stores six texture IDs and `TEXB` includes a fixed
  128-byte texture name. The released PS2 profile below is materially different.
- Triangle strips and 16-bit indices are supported by the extractor path;
  not every topology is proved supported by the retail runtime or rebuild.

## Released PS2 material-binding profile

The PS2 `CMST` payload contains one 36-byte runtime binding record per texture.
Each following `MSHT` contains exactly one `TEXB`; unlike PC, the `TEXB` ends in
a numeric key rather than a fixed texture name:

```text
TEXB = lane0[n] || lane1[n] || lane2[n] || lane3[n] || lane4[n]
       || texture_key:u32
payload_size = 20*n + 4
```

All lane elements are serialized little-endian dwords and consumed as floats.
The corresponding binding record is:

| Offset | Released PS2 role |
| ---: | --- |
| `+0x00` | resolved texture-object pointer |
| `+0x04` | cleared runtime state |
| `+0x08` | sample count `n` |
| `+0x0C` | pointer to lane 0: opacity multiplier |
| `+0x10` | pointer to lane 1: axis-0 translation input |
| `+0x14` | pointer to lane 2: axis-1 translation input |
| `+0x18` | pointer to lane 3: axis-0 diagonal scale |
| `+0x1C` | pointer to lane 4: axis-1 diagonal scale |
| `+0x20` | cached `max(0, lane0[0..n-1])` active-binding gate |

The loader resolves `texture_key` against the current `TEXT` list by comparing
`CTEXTURE+0x94`, following `+0x98`, storing the winning pointer, and incrementing
its `+0x9C` reference count. List insertion makes a duplicate key's newest
texture win. The released load path dereferences the result without a missing-key
guard; an unresolved key is not a supported null/default binding.

The renderer selects one sample across all five lanes with `j = phase % n`.
It has an explicit divide-by-zero break rather than an `n == 0` default. Its
material equations are:

```text
alpha' = cvt.w.s(float(alpha) * lane0[j])

x  = lane1[j]
y  = lane2[j]
sx = lane3[j]
sy = lane4[j]
tx = x + (1 - sx) / 2
ty = y + (sy - 1) / 2
```

The texture matrix has `M00=sx`, `M11=sy`, `M20=tx`, `M21=ty`, `M22=1`, and
`M33=1`; all other cells are zero. The non-identity helper writes `tx` and `ty`
back through the lane-1/lane-2 pointers. Whether an outer owner refreshes those
arrays before a later render remains open. Axis 0/1 is deliberate conservative
naming: the instructions do not recover the authoring tool's U/V or S/T terms.

The independently reproduced executable identity is:

| Build | ELF SHA-256 | loader/cache subsection | renderer-lane subsection | transform helper |
| --- | --- | --- | --- | --- |
| PS2 demo | `5700b5d0b39554e49afe65e079ad8109fe6688c2aa5e6f0e0ed5afcefd034584` | `[0x21A180,0x21A2C0)` / `0c52d25e9a3a4590d9deb81e417285e1d774f925365332e1c0a17d2a54e527fd` | `[0x30FC20,0x30FE34)` / `ae976ad7dde8689cb7d35ac630600e16d7823b6a0ab5aacbbeba77400880073e` | `[0x3127D0,0x313528)` / `48486a65c625cf567508a24d206b3a1ee7532926876b6b6af681a825a1aac91e` |
| Europe | `87cb89b020cf107b3ba4612ac6bc86ed3fcbd6dd985e2cd3978bf897be96b655` | `[0x21A240,0x21A380)` / `447eb61022fbb81455bad434ed9dedde943300b41f70647e84d5659f8b4d07e2` | `[0x30FBF0,0x30FE04)` / `b171962ff8f80c4ab41356db57f6a0cf9a2aee72a6591b6bb5fd037b9f37aa6c` | `[0x3127A0,0x3134F8)` / `1624d0604b684543b0b87fb6153bd74833a86e63f35e87d9ec6c7ecef704edb2` |
| USA | `4cfed76f0b0cdf84377a4d5b1613fd197c27be9a3814743590fecba22ba4e166` | `[0x21A9A8,0x21AAE8)` / `9c32c8ef19493fb11d1ec80be01f74388bc7182aae40c37ecb54d29fa7adbf3b` | `[0x310530,0x310744)` / `c7d36e737654a077989be0363de24a514701e4d73622c54af88750f72e1ba9b3` | `[0x3130E0,0x313E38)` / `88f56b08fb12b43a7a42026fc690ff201ff188f9782d9b94719700ddd1bca780` |

After zeroing relocated MIPS jump targets and non-special immediates, the three
builds have identical normalized hashes for the loader/cache subsection
(`67090a14eeeb4ebdadcedbd815bc731308864a8b3375514f4eb3120d598e870f`),
renderer-lane subsection
(`7b18548d0e5e3c797ac1fcaa195fe1faea1e1f9596848d0636bbd8b179922fa9`),
and transform helper
(`1571b6abd76465f6608a2fdf83895a2867694de3ece168abfb9e720c01c3a363`).
A streamed demo `base_res_PS2.aya` sample has one binding with `n=1`, lanes
`[1,0,0,1,1]`, key `0`, cache `1`, and a matching `TEXT` key `0`; it
demonstrates the identity material, not the full authored population. The
larger demo `201_res_PS2.aya`
(`b187cab2b7866cd23a6e443908c357fca93d729fa9fcb9853768464417ad282e`)
independently exercises the new probe across 56 mesh bodies and 222 binding
records without a framing failure.

The complete named package shelf closes the sample boundary:

| Corpus | AYA identities/instances | `TEXT` | `MESH` / `CMST` | Bindings / `MSHT` / `TEXB` |
| --- | ---: | ---: | ---: | ---: |
| PS2 demo | 5 | 370 | 57 | 223 |
| shared Europe/USA retail bytes, counted once | 302 | 18,597 | 3,490 | 13,805 |
| unique-byte total | 307 | 18,967 | 3,547 | 14,028 |
| demo + Europe + USA regional instances | 609 | 37,564 | 7,037 | 27,833 |

Every one of the 14,028 unique binding records has `n=1`; no shipped `n=0`
or `n>1` row occurs. Consequently every `CMST` is exactly `36 * bindings`,
every `MSHT` is 32 bytes, and every `TEXB` is 24 bytes. The unique-byte
declared totals are 505,008 `CMST` bytes, 448,896 `MSHT` bytes, and 336,672
`TEXB` bytes. All 18,967 `TEXT/P2TX/TEXD` records have a 160-byte `TEXD`,
numeric keys are unique within each AYA, and all 14,028 material keys resolve
inside their owning AYA. Malformed streams, wrapper residue, size-law failures,
duplicate keys, and unresolved joins are all zero. The 232 retail Goodie AYAs
legitimately contain neither `TEXT` nor `MESH`; they are not dropped rows.

The exact demo split is 271/56/222 for `201`, 8/1/1 for `base`, and 91/0/0
for `Frontend` (`TEXT`/`MESH`/binding), reproduced by direct framing of the
exact package members.

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
matrix-palette slots. The
[focused position-skinning contract](cmsh-matrix-palette-skinning.md) proves
GPU-side c10 palette addressing, frame-zero/current pose roles, one-third
palette scale, and the released asymmetric slot weights `(0, 2/3, 1/3)`. Its
[typed-order/normal successor](cmsh-matrix-normal-deformation.md) proves the
row-vector bind/current product and that the normal-bearing linked shader uses
serialized `v3` directly with no c10 palette deformation.

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
  candidate-only. Its explicit `--embedded-mesh-profile ps2` probe validates
  the 36-byte `CMST` records, exact `MSHT`/`TEXB` framing, `20*n+4` payload law,
  five raw dword lanes, numeric texture key, and cached-gate bits without
  silently applying the incompatible PC fixed-name profile.
- [`rebuild/tools/cmsh_static_preview.py`](../../rebuild/tools/cmsh_static_preview.py)
  and its focused tests parse, emit OBJ for the supported geometry surface, and
  byte-round-trip all 367 measured streams. The byte-accounting gate attributes
  32.05% of 100,813,615 stream bytes to typed model state and 67.95% to honest
  opaque carry-through; byte identity is not semantic completeness.
- [`tools/cmsh_animation_usage_census.py`](../../tools/cmsh_animation_usage_census.py)
  joins the loose frame/skeleton lanes to numeric-LVLR `MESH` membership,
  definition-bearing WRES placements through physics mesh fields, and bounded
  authored MSL animation calls. The hash-pinned full-corpus gate also parses the
  53 anonymous direct embedded bodies without assigning guessed loose names.
- The dedicated rebuild Aquila consumer is exact and specimen-bounded; it is not
  a general CMSH importer.

## Open questions and falsifiers

- Name every PB* payload field by joining one exact part to its retail consumer;
  tag frequency alone is insufficient.
- Observe one infantry draw and preserve malformed hierarchy behavior for
  disposable copied-profile tests. Position blend, slot indices, typed palette
  order, and linked-shader normal dataflow are closed by the two dedicated
  skinning contracts.
- Establish every remaining topology/FVF combination with a cross-check between
  bytes, static loader branches, and rendered output.
- Trace the population of the runtime named-animation table at
  `CMesh+0x14/+0x18`; MSL requests and `VHFM` pose maps are separate evidence
  until their exact frame-range records are joined.
- Resolve the apparent repeated `BBOX` writer behavior without assuming it is a
  harmless exporter bug.
- Exercise a controlled two-sample PS2 binding to observe dormant phase
  stepping, and determine whether the transform helper's lane-1/lane-2 writeback
  accumulates across reachable renders.
- Test a non-Level-100 static mesh and one skeletal mesh in a disposable copied
  profile before claiming general runtime parity.

## Claim boundary

The container walk, corpus population, tag counts, hierarchy/reference shapes,
selected geometry fields, pose-map dimensions, bone-to-part names, palette-slot
indices, the seven-file position blend, typed bind/current order, released
normal dataflow, PS2 `CMST`/`MSHT`/`TEXB` framing and five-lane renderer
dataflow, numeric-LVLR membership, 4,090 WRES definition joins, and 53 anonymous
embedded bodies are bounded. PS2 axis authoring names and multi-sample authored
usage, named clips, other WRES/spawn owners, general scheduling/rendering,
complete scene dependencies, collision, malformed-input behavior, pixels, and
parity are open.
