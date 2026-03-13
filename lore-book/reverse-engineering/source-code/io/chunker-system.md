# Chunker System

## Chunker System (chunker.cpp/h)

> Analysis added December 2025

The Chunker system is the binary serialization framework for `.aya` resource files. It uses an IFF-style tagged chunk format for structured data storage.

**CRITICAL**: This is for **asset files (.aya)**, NOT for **.bes save files**. Save files use raw struct serialization, not chunking.

### Purpose

CChunker provides a hierarchical binary format for game resources - textures, meshes, level data, goodies, etc. The format allows tools to skip unknown chunks gracefully and supports nested structures.

### Chunk Format

Each chunk consists of a tag, size, and payload:

```
+0x00: DWORD - Tag (4 ASCII chars, little-endian via MKID macro)
+0x04: DWORD - Size (bytes after this field)
+0x08: ...   - Data payload
```

**Example**: A `LVLR` chunk containing 128 bytes of level resource data:
```
4C 56 4C 52  80 00 00 00  [128 bytes of data...]
'L''V''L''R' size=128
```

### MKID Macro

The tag encoding macro from `membuffer.h` converts 4 ASCII characters to a little-endian 32-bit integer:

```cpp
#define MKID(foo) UINT(((foo)[0]) + ((foo)[1]<<8) + ((foo)[2]<<16) + ((foo)[3]<<24))
```

**Examples**:
- `MKID("LVLR")` → `0x524C564C` (R=0x52, L=0x4C, V=0x56, L=0x4C)
- `MKID("NEKO")` → `0x4F4B454E` (O=0x4F, K=0x4B, E=0x45, N=0x4E)

### Known Chunk Tags

| Tag | Purpose | Typical Size |
|-----|---------|--------------|
| `LVLR` | Level resource header | Variable |
| `ENGN` | Engine resources | Large |
| `GDIE` | Goodie entry (gallery assets) | Variable |
| `GDAT` | Goodie data | Variable |
| `NEKO` | Xbox memory card magic (Japanese for "cat") | 4 bytes |
| `TEXT` | Texture data | Large |
| `MESH` | Mesh data | Large |

### Classes

**CChunker** - Writer class for resource compilation:
- Used by development tools to create .aya files
- Supports nested chunks via `BeginChunk()`/`EndChunk()`
- Writes to internal buffer then flushes to file

**CChunkReader** - Reader class for runtime loading:
- Parses .aya files at game startup
- Provides `GetChunk()` to locate specific tags
- Handles chunk nesting and size validation

### Constants

```cpp
#define CHUNKPOOLSIZE  (256*1024)  // 256KB internal buffer
#define LENGTHSMAX     256         // Max nesting depth
```

The 256KB buffer is allocated once and reused for chunk operations. Nesting is limited to 256 levels deep (more than sufficient for any game resource).

### AYA File Naming Convention

| Pattern | Purpose | Example |
|---------|---------|---------|
| `XXX_res_PC.aya` | Level resources | `101_res_PC.aya` |
| `goodie_XX_res_PC.aya` | Gallery assets | `goodie_01_res_PC.aya` |
| `base_res_PC.aya` | Common resources | Shared textures, UI |
| `frontend_res_PC.aya` | Frontend resources | Menus, HUD |

The `_PC` suffix indicates platform - console versions use `_PS2.aya` or `_XBOX.aya`.

### Relevance to Save Editing

**NONE for .bes files.** Save files are fixed-size raw binary (10,004 bytes) with NO chunk headers:

| Aspect | .bes Save Files | .aya Resource Files |
|--------|-----------------|---------------------|
| **Format** | Raw struct dump | IFF-style chunks |
| **Size** | Fixed 10,004 bytes | Variable |
| **Headers** | 16-bit version word (`0x4BD1`) + CCareer core copied at `file+2` (plus options/tail blocks in retail) | Tag+size per chunk |
| **Tool** | Save patcher | AYAResourceExtractor |
| **Editing** | Offset-based | Chunk-aware |

The chunker system is relevant ONLY for asset extraction (via Stuart's AYAResourceExtractor tool), not for save file editing.

### Files Analyzed for This Section

| File | Purpose |
|------|---------|
| `chunker.cpp` | CChunker writer implementation |
| `chunker.h` | Class definitions, constants |
| `membuffer.h` | MKID macro definition |

---

## Resource Accumulator (ResourceAccumulator.cpp/h)

AYA resource file system for game assets.

**AYA File Format:**
| Field | Value/Description |
|-------|-------------------|
| Signature | "AYADATA" |
| Version | 103 |

**Chunk IDs:**
| ID | Purpose |
|----|---------|
| `LVLR` | Level resource |
| `TARG` | Target data |
| `AYAD` | AYA data |
| `TEXT` | Text/strings |
| `MESH` | 3D meshes |
| `ERES` | Entity resources |
| `WRES` | World resources |
| `IMPS` | Imports |
| `LNDS` | Landscape |
| `VSDS` | Vertex shader data |
| `PLAT` | Platform-specific |
| `SURF` | Surface data |
| `SSHD` | Shadow shader |
| `PMIB` | Unknown |
| `DMKR` | Debug marker |
| `GDIE` | Goodie data |
| `PAGE` | Page/UI data |

**File Naming Conventions:**
| Pattern | Purpose |
|---------|---------|
| `base_res_PC.aya` | Base resources |
| `000_res_PC.aya` | Level 0 resources |
| `goodie_00_res_PC.aya` | Goodie 0 resources |

**Goodie Resource IDs:** Start at 10000 (goodie_00 = -1000, maps to ID 10000)

**Easter Egg:** "kempy cube" is the internal name for the skybox (likely named after a team member)

---
