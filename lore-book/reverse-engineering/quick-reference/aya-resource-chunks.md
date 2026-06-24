Status: active quick reference
Last updated: 2026-04-29
Source: migrated from archived Codex Onslaught skills during the skill clean-slate pass.
Summary: Resource archive chunk IDs and top-level chunk lookup.
# AYA Chunk Reference

Complete list of chunk IDs found in Onslaught .aya resource files.

## Top-Level Resource Chunks

| ID | Hex | Description |
|----|-----|-------------|
| LVLR | 0x524C564C | Level resource header, contains version |
| TARG | 0x47524154 | Target platform identifier |
| AYAD | 0x44415941 | Engine struct size validation |
| TEXT | 0x54584554 | Texture resource |
| MESH | 0x4853454D | Mesh resource |
| ERES | 0x53455245 | Engine resources |
| WRES | 0x53455257 | World resources |
| IMPS | 0x53504D49 | Imposter/LOD resources |
| LNDS | 0x53444E4C | Landscape data |
| SURF | 0x46525553 | Surface/terrain data |
| SSHD | 0x44485353 | Static shadows |
| VSDS | 0x53445356 | Vertex shaders (Xbox) |
| PLAT | 0x54414C50 | Platform-specific data |
| PMIB | 0x42494D50 | Patch manager index buffers |
| DMKR | 0x524B4D44 | Damage markers |
| GDIE | 0x45494447 | Goodie data container |
| PAGE | 0x45474150 | Page file header (PS2) |
| ENGN | 0x4E474E45 | Engine state |

## Mesh Sub-Chunks

| ID | Parent | Description |
|----|--------|-------------|
| CMST | MESH | Mesh texture list header |
| MSHT | MESH | Material/shader definition |
| TEXB | MSHT | Texture binding (name + UV params) |
| MESP | MESH | Mesh part container |
| CMSP | MESP | Core mesh part (transforms) |
| CHLD | MESP | Child part indices (uint32 array) |
| PRNT | MESP | Parent part index |
| NMIC | MESP | Next mesh in chain index |
| BBOX | MESP | Bounding box (written twice) |
| VHFM | MESP | Vertex/hierarchy frame mapping |
| HORI | MESP | Hierarchy orientation frames |
| HPOS | MESP | Hierarchy position frames |
| HFOV | MESP | Hierarchy FOV frames |
| BONE | MESP | Bone indices |
| BONW | MESP | Bone weights per vertex |
| BONS | MESP | Bone scale/transform data |
| PBKT | MESP | Part bucket (skip by size) |
| CPOS | MESP | Current position (skip by size) |
| CORI | MESP | Current orientation (skip by size) |
| REFR | MESP | Reference to another part's geometry |
| PMVB | MESP | Part mesh vertex buffer |

## Vertex Buffer Sub-Chunks

| ID | Parent | Description |
|----|--------|-------------|
| CMVB | PMVB | Core vertex buffer header |
| MMPT | CMVB | Material primitive type (per material) |
| IBUF | MMPT | Index buffer (uint16 indices) |
| VBUF | MMPT | Vertex buffer (vertex data) |
| TEXR | MMPT | Texture reference IDs (6 x uint32) |

## Goodie Sub-Chunks

| ID | Parent | Description |
|----|--------|-------------|
| GDAT | GDIE | Goodie data container |
| IMAG | GDAT | Image/thumbnail data |
| MDAT | GDAT | Mesh data reference |
| TXTR | GDAT | Texture reference |

## Camera/Misc Chunks

| ID | Description |
|----|-------------|
| CAMD | Camera data |
| CCUS | Custom camera settings |

## Chunk Size Conventions

Most chunks store size excluding the 8-byte header:
```
Actual data size = size field value
Total chunk bytes = size + 8
```

The chunker writes size after chunk content is complete, filling in the size field retroactively.

## Reading Pattern

```csharp
uint chunkId = reader.ReadUInt32();   // 4 bytes: ID
uint chunkSize = reader.ReadUInt32(); // 4 bytes: size
byte[] data = reader.ReadBytes(chunkSize);
```

Or using the engine's CChunkReader:
```cpp
ULONG tag = reader.GetNext();  // reads ID + size
if (tag == MKID("MESH")) {
    // reader.GetSize() returns chunk size
    reader.Read(&data, sizeof(data), 1);
}
reader.Skip(); // skip remaining unread bytes
```
