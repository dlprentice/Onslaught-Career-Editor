# AYA Asset Format

## Overview

From deep analysis of `AYAResourceExtractor` (Stuart's extraction tool):

**Key Insight**: NO shift-16 encoding in asset files. Also note: the historical “shift-16” appearance in retail `.bes` saves is a **misaligned view** caused by the 16-bit version word and the CCareer dump beginning at `file+2` (true dword boundaries are `file_offset % 4 == 2`).

**Pipeline provenance note (desimbr, February 15, 2026):** parts of `.aya` content were used as a runtime performance path where many `.msh`-derived C++ structures (and related texture data) were dumped from memory and loaded back, instead of always loading large loose `.msh`/`.tga` sets during startup.

**Pipeline corroboration note (Glenn, February 23, 2026):** dev builds reportedly included generation/precompute code (coastline mesh, some landscape LOD tables, and normal-mapped distance sprites rendered via D3D scenes), while console/release builds loaded saved outputs and had generation paths conditionally compiled out.

---

## Compression Architecture

```
AYA File Structure:
+-------------------------------------+
| [4 bytes] Compressed chunk size     |  <- Little-endian uint32
+-------------------------------------+
| [N bytes] zlib compressed data      |  <- Standard zlib (RFC 1950)
+-------------------------------------+
| [4 bytes] Next chunk size (if any)  |
+-------------------------------------+
| [N bytes] zlib compressed data      |
+-------------------------------------+
(Repeat until EOF - 1MB decompression limit per chunk)
```

- **Compression**: zlib 1.2.x with default window bits (15)
- **Chunk limit**: 1MB uncompressed **(AYAResourceExtractor buffer limit; not confirmed as a format rule)**
- **Total buffer**: 4MB maximum **(extractor output buffer limit)**
- **Format**: Standard zlib wrapper (not raw deflate, not gzip)

---

## Model Binary Structure (Post-Decompression)

### Header (starts at offset 0x08)

| Offset | Size | Content |
|--------|------|---------|
| 0x08 | 4 | Unknown |
| 0x0C | 4 | numTextures (uint32) |
| 0x10 | 28 | 7 x uint32 (unknown) |
| 0x2C | 300 | meshName (fixed-length UTF-8, null-padded) |
| 0x158 | 12 | Unknown |
| 0x164 | 4 | numParts (uint32) |
| 0x168 | 20 | 5 x uint32 (unknown) |

---

## Tagged Chunk System

All data sections use 8-byte headers:
```
[4 bytes] ASCII tag name (e.g., "CMST", "MESP")
[4 bytes] chunk size (uint32)
[N bytes] chunk data
```

### Complete Tag Catalog

| Tag | Purpose | Data Structure |
|-----|---------|----------------|
| `CMST` | Texture list header | `numTextures x 36 bytes` metadata |
| `MSHT` | Material/texture block | Container for TEXB |
| `TEXB` | Texture binding | 20 bytes + 128-byte texture name |
| `MESP` | Mesh part header | Container for CMSP and subchunks |
| `CMSP` | Mesh part data | Transform matrices + metadata |
| `CHLD` | Child parts list | `numChildren x 4 bytes` (uint32 array) |
| `PRNT` | Parent part reference | 4 bytes (uint32) |
| `NMIC` | Next part in chain | 4 bytes (uint32) |
| `BBOX` | Bounding box | Origin + axis + valid + radius (**appears TWICE - bug!**) |
| `VHFM` | Vertex frame data | Animation data |
| `HORI` | Orientation frames | `numHFrames x 48 bytes` (3 vectors/frame) |
| `HPOS` | Position frames | `numHFrames x 16 bytes` (1 vector/frame) |
| `HFOV` | FOV frames | `numHFrames x 4 bytes` (floats) |
| `BONE` | Bone indices | `numBones x 4 bytes` |
| `BONW` | Bone weights | `numPVert x 4 x numBones bytes` |
| `BONS` | Bone skinning | `numPVert x 12 x numBones bytes` |
| `PBKT` | Unknown (skipped) | Variable size |
| `CPOS` | Unknown (skipped) | Variable size |
| `CORI` | Unknown (skipped) | Variable size |
| `REFR` | Part reference | 4 bytes - enables mesh instancing |
| `PMVB` | Part mesh vertex buffer | Container for CMVB |
| `CMVB` | Vertex buffer header | Texture counts, FVF flags, primitive type |
| `MMPT` | Material/mesh part | Per-material geometry section |
| `IBUF` | Index buffer | `numIndices x 2 bytes` (ushort array) |
| `VBUF` | Vertex buffer | `numVertices x vertexChunkSize bytes` |
| `TEXR` | Texture reference | 6 x uint32 texture IDs |
| `CCUS` | Custom/end marker | Variable |
| `CAMD` | Camera data | Variable |

**BBOX Bug Note**: Stuart marked this in code as "bug? BBOX tag stored twice!" - the tag appears consecutively, likely a bug in original export tool that was never fixed.

---

## Vertex Data Formats

### Standard Vertex (36 bytes)

| Offset | Size | Type | Field |
|--------|------|------|-------|
| 0x00 | 12 | float3 | position (x, y, z) |
| 0x0C | 12 | float3 | normal (x, y, z) |
| 0x18 | 4 | uint32 | colour (ARGB packed) |
| 0x1C | 4 | float | U (texture coord) |
| 0x20 | 4 | float | V (texture coord) |

### Extended Vertex (48 bytes)

Same but with 12 extra bytes at 0x0C (bone weights - Stuart's comment: "not sure what this is. Bone weighting or something maybe....")

---

## Mesh Part Structure (CMSP)

| Offset | Size | Content |
|--------|------|---------|
| +0x00 | 48 | currentOrientation (3 x vec4 matrix) |
| +0x30 | 48 | baseOrientation (3 x vec4 matrix) |
| +0x60 | 16 | offsetPosition (vec4) |
| +0x70 | 16 | basePosition (vec4) |
| +0x80 | 8 | Pointers (null in file) |
| +0x88 | 4 | partNum |
| +0x8C | 4 | partType |
| +0x90 | 4 | numChildren |
| +0xA8 | 4 | numDVert |
| +0xAC | 4 | numPVert |
| +0xB0 | 4 | numTris |
| +0xB4 | 4 | numAFrames |
| +0xB8 | 4 | numVFrames |
| +0xBC | 4 | numHFrames |
| +0xC0 | 4 | numBones |
| +0xDC | 32 | partName (fixed-length string) |

---

## Part Instancing (REFR Tag)

Memory optimization via mesh instancing:
```csharp
// Copy vertices/indices from a different part but using different pos/ori.
// Used on guncrab mesh with repeating 'same' legs.
uint refpart = ReadUint(fileBytes, ref index);
```

---

## Coordinate System

- **Convention**: Left-handed Y-up (DirectX standard)
- **FBX Export**: Z and V coordinates are negated for right-handed conversion
- This matches DirectX conventions used throughout BEA

---

## Fixed-Length String Buffers

| Buffer | Size | Usage |
|--------|------|-------|
| Mesh name | 300 bytes | Model identifier |
| Texture name | 128 bytes | Material reference |
| Part name | 32 bytes | Part identifier |

This pattern parallels save file structures (CCareerNode = 64 bytes fixed).

---

## Texture Format

### Path Convention

```
dxtntextures\meshtex%{name}(0){format}.aya
```

Where `{format}` is `A1R5G5B5` (16-bit) or `A8R8G8B8` (32-bit).

### DDS Compression

| Format | FourCC | Block Size | Notes |
|--------|--------|------------|-------|
| DXT1 | 0x31545844 | 8 bytes | RGB + optional 1-bit alpha |
| DXT2/DXT3 | 0x32545844/0x33545844 | 16 bytes | Explicit 4-bit alpha |
| DXT5 | 0x35545844 | 16 bytes | Interpolated 8-level alpha |

The README claims DXT2, but the extractor selects decoding based on the DDS header and supports DXT1/3/5 as well. Treat DXT2 as **possible**, not exclusive.

---

## Data Type Encoding (Contrast with Save Files)

| Type | AYA Files | BES Save Files |
|------|-----------|----------------|
| Integers | Raw uint32/int32 | Raw uint32/int32 (true view; legacy aligned view can look like `value << 16`) |
| Floats | Raw IEEE-754 | Raw IEEE-754 |
| Booleans | Raw 0/1 | Raw 0/1 (true view; legacy aligned view can look like `0x00010000`) |
| Byte Order | Little-endian | Little-endian |
| Compression | zlib | None |
| Structure | Tagged chunks | Fixed offsets |

This helps avoid a common pitfall: the retail `.bes` “shift-16” look is primarily a **misaligned view** problem (CCareer begins at `file+2` after a 16-bit version word), not a universal fixed-point convention.

---

## Known Bugs in Extractor

1. **Memory leak**: Native zlib wrapper allocates 2MB per call, never freed
2. **Non-square texture bug**: `height x height x 4` instead of `width x height x 4` in DDSTextureUncompress.cpp

---

## Additional Constants

| Constant | Value | Purpose |
|----------|-------|---------|
| Part VB bookmarks | 1000 | Max parts for REFR instancing |
| Max textures per mesh | 24 | FBX template limit (not BEA limit) |
| Uncompressed buffer | 4MB | Max model output size |

---

## BEA Game Directory Structure

Expected layout for extraction tool:
```
<BEA_ROOT>/
  data/
    resources/
      meshes/           <- All .aya model files
      dxtntextures/     <- DDS textures as .aya files
        meshtex%<name>(0)A1R5G5B5.aya  (16-bit tried first)
        meshtex%<name>(0)A8R8G8B8.aya  (32-bit fallback)
```

---

## Rendering Details

- **Native primitive**: Triangle strips (converted to triangle lists for FBX)
- **Index format**: 16-bit (ushort)
- **Winding order**: Alternates per triangle in strip
- **No scale normalization**: Models export at original game scale
