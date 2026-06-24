Status: active quick reference
Last updated: 2026-04-29
Source: migrated from archived Codex Onslaught skills during the skill clean-slate pass.
Summary: AYA tag IDs and mesh/texture marker lookup.
# AYA Tag Reference

Complete reference for all known AYA binary format tags.

## Contents

- [Texture Tags](#texture-tags)
- [Mesh Part Tags](#mesh-part-tags)
- [Hierarchy Tags](#hierarchy-tags)
- [Bounding Tags](#bounding-tags)
- [Animation Tags](#animation-tags)
- [Bone Tags](#bone-tags)
- [Vertex Buffer Tags](#vertex-buffer-tags)
- [Special Tags](#special-tags)

---

## Texture Tags

### CMST - Compiled Material Set
Container for texture/material definitions.

| Field | Size | Description |
|-------|------|-------------|
| Material data | numTextures * 36 | Per-texture material properties |

Followed by numTextures MSHT blocks.

### MSHT - Mesh Texture
Individual texture definition block.

Always contains a TEXB child tag.

### TEXB - Texture Binding
Texture file reference and UV properties.

| Field | Size | Description |
|-------|------|-------------|
| UV region/scale | 20 | Texture mapping parameters |
| Texture name | 128 | Filename (null-terminated) |

---

## Mesh Part Tags

### MESP - Mesh Part
Top-level container for a mesh part. Each model has numParts MESP blocks.

Always contains a CMSP child tag.

### CMSP - Compiled Mesh Part
Core mesh part data.

| Field | Size | Description |
|-------|------|-------------|
| Current orientation | 48 | 3x4 matrix (current transform) |
| Base orientation | 48 | 3x4 matrix (bind pose) |
| Offset position | 16 | float4 (current offset) |
| Base position | 16 | float4 (bind offset) |
| Pointers | 8 | Runtime pointers (skip) |
| Part number | 4 | uint32 |
| Part type | 4 | uint32 |
| Num children | 4 | uint32 |
| Reserved | 20 | 5 x uint32 |
| Num DVert | 4 | Display vertices |
| Num PVert | 4 | Physics vertices |
| Num tris | 4 | Triangle count |
| Num AFrames | 4 | Animation frames |
| Num VFrames | 4 | Vertex frames |
| Num HFrames | 4 | Hierarchy frames |
| Num bones | 4 | Bone count |
| Pointers | 24 | Runtime pointers (skip) |
| Part name | 32 | Name (null-terminated) |
| Reserved | 64 | 16 x uint32 |

---

## Hierarchy Tags

### CHLD - Children
List of child part indices.

| Field | Size | Description |
|-------|------|-------------|
| Child indices | numChildren * 4 | uint32 array |

### PRNT - Parent
Parent part reference.

| Field | Size | Description |
|-------|------|-------------|
| Parent index | 4 | uint32 |

### NMIC - Next in Chain
Links to next part in a chain (for segmented meshes).

| Field | Size | Description |
|-------|------|-------------|
| Next part index | 4 | uint32 |

---

## Bounding Tags

### BBOX - Bounding Box
Axis-aligned bounding box for culling.

**Note**: This tag appears twice in sequence (possible format bug).

| Field | Size | Description |
|-------|------|-------------|
| Origin | 16 | float4 (center point) |
| Axis | 16 | float4 (extents) |
| Valid | 4 | uint32 (1 = valid) |
| Radius | 4 | float (bounding sphere) |

---

## Animation Tags

### VHFM - Vertex Frame Mask
Frame visibility flags.

| Field | Size | Description |
|-------|------|-------------|
| Frame flags | numVFrames | byte array |

### HORI - Hierarchy Orientation
Per-frame orientation matrices.

| Field | Size | Description |
|-------|------|-------------|
| Orientations | numHFrames * 48 | 3x4 matrix per frame |

### HPOS - Hierarchy Position
Per-frame position data.

| Field | Size | Description |
|-------|------|-------------|
| Positions | numHFrames * 16 | float4 per frame |

### HFOV - Hierarchy Field of View
Per-frame FOV (for camera parts).

| Field | Size | Description |
|-------|------|-------------|
| FOV values | numHFrames * 4 | float per frame |

### CPOS - Current Position
Animation position keyframes.

| Field | Size | Description |
|-------|------|-------------|
| Size | 4 | Data size (read from tag header) |
| Position data | size | Keyframe data |

### CORI - Current Orientation
Animation orientation keyframes.

| Field | Size | Description |
|-------|------|-------------|
| Size | 4 | Data size (read from tag header) |
| Orientation data | size | Keyframe data |

---

## Bone Tags

### BONE - Bone Indices
Bone index array for skinning.

| Field | Size | Description |
|-------|------|-------------|
| Bone indices | numBones * 4 | uint32 array |

### BONW - Bone Weights
Per-vertex bone weights.

| Field | Size | Description |
|-------|------|-------------|
| Weights | numPVert * numBones * 4 | float array |

### BONS - Bone Skin
Per-vertex bone skin matrices (position offsets per bone).

| Field | Size | Description |
|-------|------|-------------|
| Skin data | numPVert * numBones * 12 | float3 per vertex per bone |

---

## Vertex Buffer Tags

### PMVB - Part Mesh Vertex Buffer
Container for vertex/index data. Contains CMVB.

### CMVB - Compiled Mesh Vertex Buffer
Vertex buffer header.

| Field | Size | Description |
|-------|------|-------------|
| Pointers | 8 | Runtime pointers (skip) |
| Reserved | 256 | 64 x uint32 |
| Num textures | 4 | Material count (byte at offset) |
| Pointers | 8 | Runtime pointers |
| Vertex chunk size | 4 | 36 (standard) or 48 (skinned) |
| FVF flags | 4 | D3D flexible vertex format |
| Primitive type | 4 | 5 = triangle strip |
| Reserved | 8 | Unknown |

Followed by numTextures MMPT blocks.

### MMPT - Mesh Material Part
Per-material vertex/index buffer section.

| Field | Size | Description |
|-------|------|-------------|
| VB size | 4 | Vertex buffer byte size |
| IB size | 4 | Index buffer byte size |
| Num indices | 4 | Index count |
| Num vertices | 4 | Vertex count |
| Num primitives | 4 | Primitive count |
| Active | 4 | uint32 (1 = enabled) |

Followed by IBUF, VBUF, TEXR.

### IBUF - Index Buffer
Triangle strip indices.

| Field | Size | Description |
|-------|------|-------------|
| Indices | numIndices * 2 | uint16 array |

### VBUF - Vertex Buffer
Vertex data array.

| Field | Size | Description |
|-------|------|-------------|
| Vertices | numVertices * vertexChunkSize | Vertex array |

For secondary materials (materialIndex > 0), VBUF references the same vertices:
- Read 4-byte size from tag header
- Skip that many bytes

### TEXR - Texture Reference
Material texture binding.

| Field | Size | Description |
|-------|------|-------------|
| Texture IDs | 24 | 6 x uint32 (multi-texture slots) |

Slot 0 is the primary diffuse texture. Other slots for multi-texturing (rarely used).

---

## Special Tags

### REFR - Reference Part
Shares geometry from another part (memory optimization for symmetric models).

| Field | Size | Description |
|-------|------|-------------|
| Reference part | 4 | uint32 (source part index) |

When encountered, copy vertex/index data from referenced part using current part's transform.

### PBKT - Part Bucket
Collision/physics bucket data (skip).

| Field | Size | Description |
|-------|------|-------------|
| Size | 4 | Data size |
| Data | size | Bucket data |

### CCUS - Custom Camera
Camera customization data (terminates part parsing).

### CAMD - Camera Data
Camera definition data (terminates part parsing).

---

## Tag Parsing Order

Tags within MESP appear in this order (all optional except CMSP):

1. CMSP (required)
2. CHLD
3. PRNT
4. NMIC
5. BBOX (appears twice)
6. VHFM
7. HORI
8. HPOS
9. HFOV
10. BONE
11. BONW
12. BONS
13. PBKT
14. CPOS
15. CORI
16. REFR
17. PMVB (contains CMVB, MMPT, IBUF, VBUF, TEXR)

Parsing terminates on MESP (next part), BBOX, CCUS, or CAMD.

---

## Implementation Notes

1. **Tag header**: Always 8 bytes (4-char name + 4-byte length)
2. **Alignment**: No padding between tags
3. **Optional tags**: Check tag name before reading; if unexpected, rewind 8 bytes
4. **Material loop**: MMPT/IBUF/VBUF/TEXR repeat for each material in CMVB
5. **REFR handling**: Must have already parsed the referenced part
