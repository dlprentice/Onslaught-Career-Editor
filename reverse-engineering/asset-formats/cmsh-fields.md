# CMSH mesh stream: complete grammar and record layouts (PC)

Status: active format contract — the PC loader's complete chunk grammar and every stored record layout
Date: 2026-10-16
Verdict: all 213 installed PC mesh files (228 meshes, counting 15 chained meshes) parse to their exact
final byte under the grammar below, with exactly one tag in every grammar slot. Every stored record is the
loader's in-memory object image: 372, 316, 296 and 184 bytes for the mesh, part, vertex-buffer and
collision-grid records, matching their declared layouts.
Evidence: SOURCE + MEASURED. The grammar follows the retail loaders as reconstructed and byte-matched in
the private decompilation; functions are cited by name and retail address. Record offsets come from the
decompilation's class declarations, laid out with the 32-bit MSVC rules and checked against the stored
record sizes. The installed corpus was walked with
[`tools/cmsh_grammar_walk.py`](../../tools/cmsh_grammar_walk.py).
Specimen: retail addresses cite `BEA.exe.original.backup`, SHA-256
`74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`; the corpus is the installed
`data/resources/meshes/*.aya`, 213 files, whose manifest digest (SHA-256 over sorted `name sha256` lines) is
`27ada81470ff8919cb832f63e78e24ac6d33625b26be54247b70b05a76690ae1`.

This document owns the PC mesh stream's field-level layout and its parse order: what a reader needs to
recover every part, vertex, index, texture binding, frame lane and collision grid exactly as the game
loads them. [cmsh-mesh.md](cmsh-mesh.md) keeps the corpus census and the PS2 material profile.
[cmsh-animation-usage.md](cmsh-animation-usage.md), [cmsh-matrix-palette-skinning.md](cmsh-matrix-palette-skinning.md)
and [cmsh-matrix-normal-deformation.md](cmsh-matrix-normal-deformation.md) keep how the frame lanes and bone
palettes are evaluated. A mesh file first passes the AYA envelope in [aya-container.md](aya-container.md).

## Corrections to earlier readings

The grammar walk settles several tags that [cmsh-mesh.md](cmsh-mesh.md) left open or named tentatively:

| Tag | Earlier reading | What the loader reads there |
| --- | --- | --- |
| `PMS2` | bone/skeletal lane | the header that opens a chained mesh: the mesh after it belongs to the same file (15 files) |
| `CAMD` | camera metadata | the mesh's animation-mode table (36-byte records) |
| `CEMT` | end metadata | the mesh's emitter table |
| `NMIC` | chain metadata | a part's next-part-in-chain index |
| `MMPT` | geometry/material array | one vertex-buffer piece's six counts |
| `PB*`, `CPBT`, `SIZS`, `PLQT` | opaque | the part's collision polygon grid, fully laid out below |
| 48-byte vertex | position, normal, colour, UV, then three palette offsets | position, then the three palette offsets, then normal, colour and UV |

The census in [cmsh-mesh.md](cmsh-mesh.md) counts each file's first mesh only. The counts below include the
15 chained meshes, which is why they are larger (for example 4,009 parts rather than 3,774).

## How the stream is read

The inflated stream is a flat run of eight-byte headers, each a four-character tag followed by a
little-endian `u32` payload size. Chunks nest when they are written, but the loader never uses that
nesting. It reads the next header and then reads exactly as many payload bytes as the grammar says, so:

- a **wrapper** chunk (for example `MESP`) is entered, not read: the very next header is the first one
  inside its payload;
- a **leaf** chunk's payload is consumed exactly. The only exception is `VBUF` for vertex-buffer pieces after
  the first, whose payload the loader skips by its size;
- the loader checks only two tags (`HORI` and `CORI`, below); every other tag is taken on trust. The names
  given here are the tags observed in every instance of each slot.

Records are memory images of the loader's objects, written by the original tools:

- **Pointer-typed fields** hold whatever the saving tool's memory held. The loader tests them only for zero:
  a non-zero pointer means the array or link it names follows in the stream. The loader then replaces it.
- **Other fields of a record the loader then ignores can hold stale memory.** In 2,210 parts with no
  vertex-buffer pieces, the `CMVB` record's stride, vertex format and primitive type are leftover bytes. A
  reader must take only the fields this document names, and only where it names them.

All integers are little-endian. `i32` is signed 32-bit, `f32` an IEEE single. A **vector** is 16 bytes:
`f32 x, y, z` and a fourth float that is padding. A **matrix** is 48 bytes: three vectors, its rows.

## Grammar

Indentation shows what belongs to what. `[if …]` is the condition the loader tests, using the named field of
the record just read. `×n` repeats.

```text
mesh:
    CMSH  mesh record (372 bytes)
    CMST  texture records, 36 bytes × mesh.texture_count          (always present, possibly empty)
    × mesh.texture_count:
        MSHT  (wrapper)
        TEXB  five f32 lanes × texture.frames each, then a 128-byte texture name
    × mesh.part_count:  part
    [if mesh.sequence_count > 0]
        sequence records, 12 bytes × mesh.sequence_count
        × each sequence whose camera field is non-zero:  one header, then i32 camera part index
    [if mesh.anim_mode_count > 0]
        CAMD  animation-mode records, 36 bytes × mesh.anim_mode_count
    BBOX (wrapper), BBOX  bounding box (40 bytes)
    [if mesh.emitter_count > 0]
        CEMT  i32 record_size, then × mesh.emitter_count:
                  emitter record (record_size bytes),
                  then i32 part index if the record's part field is non-zero
    [if mesh.next_in_chain is non-zero]
        PMS2  (header only), then another mesh, starting at its CMSH

part:
    MESP  (wrapper)
    CMSP  part record (the chunk's whole payload; 316 bytes)
    [if part.dvertex_count > 0]   i32 record_size, then dvertex records × part.dvertex_count
    [if part.triangle_count > 0]  i32 × 3 × part.triangle_count       (dvertex indices)
    [if part.pvertex_count > 0]   vectors × part.pvertex_count × part.aframe_count
    [if part.child_count > 0]     CHLD  i32 part indices × part.child_count
    [if part.parent is non-zero]  PRNT  i32 part index
    [if part.chain_next is non-zero]  NMIC  i32 part index
    BBOX (wrapper), BBOX  bounding box (40 bytes)
    [if part.vframe_count > 0]    VHFM  u8 × part.vframe_count     (virtual-frame map)
    [if part.hframe_count > 0]
        [if part.hframe_orientations is non-zero]  HORI  matrices × part.hframe_count
        [if part.hframe_positions is non-zero]     HPOS  vectors × part.hframe_count
        [if part.hframe_fovs is non-zero]          HFOV  f32 × part.hframe_count
    [if part.bone_count > 0]
        BONE  i32 part indices × part.bone_count
        [if part.bone_weights is non-zero]  f32 × part.bone_count × part.pvertex_count
        [if part.bone_slots is non-zero]    i32 × 3 × part.pvertex_count
    [if part.collision_grid is non-zero]  collision grid
    [if part.cached_positions is non-zero]     CPOS  vectors × part.cached_frame_count
    [if part.cached_orientations is non-zero]  CORI  matrices × part.cached_frame_count
    [if part.reference_to is non-zero]         REFR  i32 part index
    vertex buffer

vertex buffer:
    PMVB  (wrapper)
    CMVB  vertex-buffer record (296 bytes)
    × vb.piece_count:
        MMPT  six i32: vb_bytes, ib_bytes, index_count, vertex_count, primitive_count, built
        IBUF  u16 × index_count
        VBUF  first piece: vb.stride bytes × vertex_count; later pieces: skipped (they share the first's vertices)
        TEXR  six i32 texture slots (-1 = none, otherwise an index into the mesh's texture records)

collision grid:
    PBKT  (wrapper)
    CPBT  grid record (the chunk's whole payload; 184 bytes)
    SIZS  i32 list_count, i32 index_count
    × grid.width × grid.height cells:
        PBCS  i32 present
        [if present == 1]  PBET (wrapper), PBSQ  i32 n, then i16 triangle indices × n
    PLQT  i32 triangle_count
    PBFK  (header only)
    × triangle_count:  PBKE  i16 × 3 vertex indices, i16 search stamp, u32 height mask
    PBPN  i32 vertex_count
    × vertex_count:    PBPP  i16 × 3 packed position
```

Three loader details matter for an exact reader:

- **The two checked tags.** If the slot after a non-zero `hframe_orientations` is not `HORI`, or the slot after
  a non-zero `cached_orientations` is not `CORI`, the loader reads nothing there and the stream desynchronises.
  Every installed stream has the expected tag.
- **Collision triangles are stored with their fields in a different order from the memory record.** Each `PBKE`
  holds the u32 mask first, then the three vertex indices, then the stamp. The record in memory is indices,
  stamp, then mask.
- **The stored part record may in principle differ in size from 316 bytes.** The loader reads the `CMSP`
  payload whole, and only logs a size difference. Every installed part is exactly 316 bytes.

Cited loaders:
- `CMesh::Deserialize`, `0x004aab90`
- `CMeshPart::Deserialize`, `0x004b27a0`
- `CMeshPart::ReadBoundingBox`, `0x004b3180`
- `CDXMeshVB::Load`, `0x0054e160`
- the collision grid's loader, `0x004d59f0`
- the chunk reader's `GetNext`, `Read` and `Skip`, at `0x00423910`, `0x00423960` and `0x00423990`

## Records

### Mesh record (`CMSH`, 372 bytes)

| Offset | Type | Meaning |
| ---: | --- | --- |
| `+0x000` | ptr | textures (replaced) |
| `+0x004` | i32 | `texture_count` |
| `+0x008` | ptr | `next_in_chain`: non-zero when a chained mesh follows (`PMS2`) |
| `+0x00C` | i32 | `sequence_count` (cutscene camera sequences; 0 in every installed mesh) |
| `+0x010` | ptr | sequences (replaced) |
| `+0x014` | i32 | `anim_mode_count` |
| `+0x018` | ptr | animation modes (replaced) |
| `+0x01C` | i32 | `emitter_count` |
| `+0x020` | ptr | emitters (replaced) |
| `+0x024` | char[300] | mesh name, NUL-terminated |
| `+0x150` | ptr | bounding box (replaced) |
| `+0x154` | i32 | resource id (overwritten by the level's id at load) |
| `+0x158` | ptr | next mesh in the global list (replaced) |
| `+0x15C` | i32 | `part_count` |
| `+0x160` | ptr | parts (replaced) |
| `+0x164` | f32 | radius |
| `+0x168` | f32 | cue factor (level-of-detail scale; semantics open) |
| `+0x16C` | i32 | runtime collision-frame stamp |
| `+0x170` | i32 | reference count (reset to 0 at load) |

The `0x0000DEAD` value that [cmsh-mesh.md](cmsh-mesh.md) saw at `+0x00` sits in the textures pointer field,
which the loader replaces without reading: it means nothing to the game.

### Texture record (`CMST` entries, 36 bytes) and texture lanes (`TEXB`)

| Offset | Type | Meaning |
| ---: | --- | --- |
| `+0x00` | ptr | texture object (replaced; resolved from the `TEXB` name) |
| `+0x04` | ptr | runtime vertex buffer (replaced) |
| `+0x08` | i32 | `frames`: the length of each `TEXB` lane |
| `+0x0C`–`+0x1C` | ptr × 5 | the five lanes (replaced) |
| `+0x20` | f32 | maximum blend |

`TEXB` holds five `f32` lanes of `frames` values each, in this order, then the 128-byte texture name:
1. blend: an alpha multiplier
2. U offset
3. V offset
4. U scale
5. V scale

The name is looked up among the textures already loaded. At draw time the renderer picks a lane value as
follows (the renderer is `0x0054d530`):
1. Take the virtual frame: `floor(render_frame × mode.frame_scaler + mode.start)`, modulo the part's
   `vframe_count`. A part drawn without an animation uses frame 0.
2. Take each lane's value at that frame, modulo `frames`.
3. Multiply the layer's alpha by the blend lane, and pass the offsets and scales to the texture as its
   transform.

How the texture applies that transform depends on the texture's mode, which is open here.

### Part record (`CMSP`, 316 bytes)

| Offset | Type | Meaning |
| ---: | --- | --- |
| `+0x000` | matrix | orientation |
| `+0x030` | matrix | base orientation |
| `+0x060` | vector | offset position |
| `+0x070` | vector | base position |
| `+0x080` | ptr | triangles (replaced) |
| `+0x084` | ptr | pvertices (replaced) |
| `+0x088` | i32 | part number |
| `+0x08C` | i32 | `part_type` (named below) |
| `+0x090` | i32 | `child_count` |
| `+0x094` | ptr | children (replaced) |
| `+0x098` | ptr | `parent`: non-zero when `PRNT` follows |
| `+0x09C` | ptr | `chain_next`: non-zero when `NMIC` follows |
| `+0x0A0` | i32 | chained-part count |
| `+0x0A4` | i32 | is-chained flag |
| `+0x0A8` | i32 | `dvertex_count` |
| `+0x0AC` | i32 | `pvertex_count` |
| `+0x0B0` | i32 | `triangle_count` |
| `+0x0B4` | i32 | `aframe_count` |
| `+0x0B8` | i32 | `vframe_count` |
| `+0x0BC` | i32 | `hframe_count` |
| `+0x0C0` | i32 | `bone_count` |
| `+0x0C4` | ptr | virtual-frame map (replaced) |
| `+0x0C8` | ptr | `hframe_positions`: non-zero when `HPOS` follows |
| `+0x0CC` | ptr | `hframe_fovs`: non-zero when `HFOV` follows |
| `+0x0D0` | ptr | bones (replaced) |
| `+0x0D4` | ptr | `bone_weights`: non-zero when the weight array follows |
| `+0x0D8` | ptr | `bone_slots`: non-zero when the slot array follows |
| `+0x0DC` | char[32] | part name |
| `+0x0FC` | ptr | bounding box (replaced) |
| `+0x100` | ptr | `collision_grid`: non-zero when the grid follows |
| `+0x104` | ptr | `cached_positions`: non-zero when `CPOS` follows |
| `+0x108` | ptr | `cached_orientations`: non-zero when `CORI` follows |
| `+0x10C` | ptr | `hframe_orientations`: non-zero when `HORI` follows |
| `+0x110` | ptr | runtime only |
| `+0x114` | u8[4] | runtime only (meaning open) |
| `+0x118` | i32 | `cached_frame_count` |
| `+0x11C` | i32 | position-static flag |
| `+0x120` | i32 | orientation-static flag |
| `+0x124` | ptr | `reference_to`: non-zero when `REFR` follows |
| `+0x128` | ptr | owning mesh (replaced) |
| `+0x12C` | f32 | radius |
| `+0x130` | f32 | cue factor |
| `+0x134` | ptr | dvertices (replaced) |
| `+0x138` | ptr | vertex buffer object (replaced) |

The game's own part-type names, from the loading messages of its older mesh reader:

| `part_type` | Name | Installed parts | Notes |
| ---: | --- | ---: | --- |
| 1 | normal | 1,788 | |
| 2 | null | 417 | not drawn unless the caller asks |
| 3 | skeletal | 16 | the only parts with `BONE` and 48-byte vertices |
| 4 | camera | 17 | the only parts with `HFOV` |
| 5 | emitter | 1,383 | |
| 6 | reference | 388 | draws the part named by `REFR` |

The older-format "dvertex", triangle and "pvertex" arrays, and the bone weight and slot arrays, never occur
in the installed PC files: every count is zero or the pointer is null. Geometry lives only in the vertex
buffer.

### Bounding box (`BBOX`, 40 bytes)

| Offset | Type | Meaning |
| ---: | --- | --- |
| `+0x00` | vector | origin |
| `+0x10` | vector | axes (half extents) |
| `+0x20` | i32 | valid flag |
| `+0x24` | f32 | radius |

### Animation-mode record (`CAMD` entries, 36 bytes)

| Offset | Type | Meaning |
| ---: | --- | --- |
| `+0x00` | char[16] | mode name |
| `+0x10` | i32 | mode id |
| `+0x14` | i32 | start (virtual frame) |
| `+0x18` | i32 | last |
| `+0x1C` | i32 | frame scaler |
| `+0x20` | f32 | rate |

How modes drive frame selection is the subject of [cmsh-animation-usage.md](cmsh-animation-usage.md).

### Sequence record (12 bytes)

The fields are a camera part pointer (non-zero when a part index follows), then the start and end frames, as
`i32`. No installed mesh has sequences.

### Emitter record (`CEMT`, 336 bytes in all 136 installed tables)

| Offset | Type | Meaning |
| ---: | --- | --- |
| `+0x000` | vector | position |
| `+0x010` | matrix | orientation |
| `+0x040` | ptr | part (non-zero when an `i32` part index follows the record) |
| `+0x044` | i32 | tracking vertex |
| `+0x048` | i32 | sub-part emitter |
| `+0x04C` | char[256] | name |
| `+0x14C` | i32 | number |

The stored record size comes first in the chunk. The loader reads records of that size, even though the
in-memory record is 336 bytes.

### Vertex-buffer record (`CMVB`, 296 bytes)

| Offset | Type | Meaning |
| ---: | --- | --- |
| `+0x000` | — | runtime header (replaced) |
| `+0x008` | ptr × 64 | pieces (replaced) |
| `+0x108` | i32 | `piece_count` (0 to 12 installed) |
| `+0x10C` | ptr | part (replaced) |
| `+0x110` | ptr | vertex shader (replaced at render) |
| `+0x114` | u32 | `stride`: vertex size in bytes |
| `+0x118` | u32 | Direct3D vertex format (`0x152` for 36-byte vertices; 0 for 48-byte vertices, which use a shader) |
| `+0x11C` | i32 | primitive type, in the game's own numbering |
| `+0x120` | u32 | file position (replaced) |
| `+0x124` | ptr | file name (replaced) |

Stride, vertex format and primitive type are meaningful only when `piece_count > 0`. In every such installed
part they are `(36, 0x152, 4)` (1,783 parts) or `(48, 0, 4)` (16 skeletal parts).

The game maps its primitive numbering 0–5 to Direct3D's point list, line list, line strip, triangle list,
triangle strip and triangle fan. So the stored 4 is a **triangle strip**. The buffer-building code stores Direct3D's
triangle-list constant there, which is also 4, and the game draws strips.

Each piece's index buffer is one stitched strip: `primitive_count = index_count − 2` in all 2,661
installed pieces, and degenerate triangles join the runs (2,635 pieces contain some). A reader takes triangles from consecutive index triples, flips the winding of every
other one, and drops the degenerate ones. Every installed index is below the first piece's `vertex_count`.

### Vertex formats

36-byte vertex (`0x152`: position, normal, diffuse, one UV set):

| Offset | Type | Meaning |
| ---: | --- | --- |
| `+0x00` | f32 × 3 | position (part space) |
| `+0x0C` | f32 × 3 | normal |
| `+0x18` | u32 | diffuse colour, `0xAARRGGBB` |
| `+0x1C` | f32 × 2 | U, V |

48-byte vertex (skeletal parts):

| Offset | Type | Meaning |
| ---: | --- | --- |
| `+0x00` | f32 × 3 | position |
| `+0x0C` | f32 × 3 | three bone-palette offsets (each 3 × a `BONE` index; see [cmsh-matrix-palette-skinning.md](cmsh-matrix-palette-skinning.md)) |
| `+0x18` | f32 × 3 | normal |
| `+0x24` | u32 | diffuse colour |
| `+0x28` | f32 × 2 | U, V |

These are the vertex records the game builds before uploading (`CDXMeshVB::BuildStaticVB`, `0x0054c0a0`;
`CDXMeshVB::BuildSkinnedVB`, `0x0054c920`). A file's `VBUF` stores them as built.

### Texture slots (`TEXR`)

The six `i32` slots are the piece's texture layers 0–5, each drawn as its own pass with the texture in the
layer's mode. A value of `-1` means no layer. Installed pieces use these layer sets:

| Layers used | Pieces |
| --- | ---: |
| 0 only | 1,645 |
| 0 and 2 | 766 |
| 0 and 4 | 211 |
| 0, 1, 2 and 3 | 39 |

What each layer mode means is open.

### Collision grid (`CPBT`, 184 bytes, and its arrays)

Of the grid record, a reader needs these fields:

| Offset | Type | Meaning |
| ---: | --- | --- |
| `+0x30` | vector | origin |
| `+0x40` | vector, f32 | packing origin and scale, used to unpack `PBPP` positions |
| `+0x68` | i32 | `width` (cells) |
| `+0x6C` | i32 | `height` (cells) |
| `+0x70` | f32 | cell size across |
| `+0x74` | f32 | cell size in height |
| `+0x78` | i32 | triangle count |

The record's other fields are runtime search state, pointers or bytes whose meaning is open.

Each cell present in the grid lists triangle indices. The lists' indices are one shared array of
`index_count` values, which the loader gives each list a slice of. Positions are three signed 16-bit values,
unpacked through the packing origin and scale. The exact unpacking formula is open here; the grid is
collision data and not needed to export geometry.

## Corpus counts (grammar walk)

| Slot | Tag | Count |
| --- | --- | ---: |
| mesh | `CMSH` / `CMST` | 228 / 228 |
| texture | `MSHT` / `TEXB` | 1,014 / 1,014 |
| part | `MESP` / `CMSP` / `VHFM` / `HORI` / `HPOS` / `PMVB` / `CMVB` | 4,009 each |
| part children / parent / chain | `CHLD` / `PRNT` / `NMIC` | 1,456 / 3,781 / 2 |
| bounding boxes | `BBOX` (wrapper + record) | 2 × (4,009 + 228) |
| camera / skeletal / reference | `HFOV` / `BONE` / `REFR` | 17 / 16 / 388 |
| caches | `CPOS` / `CORI` | 3,971 / 2,746 |
| animation modes / emitters / chained meshes | `CAMD` / `CEMT` / `PMS2` | 70 / 136 / 15 |
| collision grids | `PBKT` / `CPBT` / `SIZS` / `PLQT` / `PBFK` / `PBPN` | 1,799 each |
| grid cells / lists / triangles / vertices | `PBCS` / `PBSQ` / `PBKE` / `PBPP` | 69,880 / 46,060 / 173,760 / 521,280 |
| vertex-buffer pieces | `MMPT` / `IBUF` / `VBUF` / `TEXR` | 2,661 each |

Every part has a virtual-frame map, an `HORI` and an `HPOS`. 2,205 parts have no animation frames
(`aframe_count` 0), 1,777 have one and 27 have two. Skeletal parts have 14 to 19 bones.

## Open questions

- **Texture layer modes.** What each of the six layer modes does when applied to a texture. Falsifier: the
  texture `Activate` path per mode, against a capture of a multi-layer piece.
- **Texture lanes.** How the U/V offset and scale lanes compose into the PC texture transform. The PS2 law is in
  [cmsh-mesh.md](cmsh-mesh.md). Falsifier: the PC texture `Activate` path for modes 0–5.
- **Collision positions.** The collision grid's position unpacking. Falsifier: the grid's unpack helper
  against a part's vertex-buffer positions.
- **Cue factors.** The mesh and part cue factors. Falsifier: the level-of-detail callers.
- **Runtime-only bytes.** The meaning of the part's runtime-only bytes at `+0x110` and `+0x114`, if any is
  ever stored meaningfully.
