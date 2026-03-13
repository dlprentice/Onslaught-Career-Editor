# maptex.cpp - Map Texture System

**Source File:** `C:\dev\ONSLAUGHT2\maptex.cpp`
**Debug String Address:** `0x0062db04`
**Functions Found:** 6

## Overview

The CMapTex class manages terrain mixer textures used for blending between different terrain types (grass, rock, sand, snow, road, concrete). The system loads TGA texture files and stores them in RGBA format with height/displacement information in the alpha channel.

## Class Structure (Reconstructed)

```cpp
class CMapTex {
    void*   m_pTextureData;     // +0x00: Main texture buffer
    int     m_field_04;         // +0x04: Unknown (possibly flags)
    void*   m_pSecondaryData;   // +0x08: Secondary texture buffer
    short   m_nTextureSet;      // +0x0C: Current texture set ID (-1 = unloaded)
    int     m_nTexelSize;       // +0x10: Size per texel (width*width*4)
    int     m_nTextureCount;    // +0x14: Number of textures loaded
    int     m_nTextureWidth;    // +0x18: Texture dimension (e.g., 64, 128)
    int     m_minHeights[6];    // +0x1C: Min height per texture
    int     m_maxHeights[6];    // +0x34: Max height per texture
};
```

## Texture Types

The system supports 6 terrain texture types, loaded from `data\textures\mixers\`:

| Index | Name     | File Pattern              |
|-------|----------|---------------------------|
| 0     | grass    | grass##.tga               |
| 1     | rock     | rock##.tga                |
| 2     | sand     | sand##.tga                |
| 3     | snow     | snow##.tga                |
| 4     | road     | road##.tga                |
| 5     | concrete | concrete##.tga            |

Full path format: `data\textures\mixers\%s%.2d.tga` (e.g., `data\textures\mixers\grass00.tga`)

## Functions

### CMapTex__Reset
| Property | Value |
|----------|-------|
| Address | `0x00491180` |
| Returns | `void` |
| Calling Convention | thiscall (ECX = this) |

**Purpose:** Resets the CMapTex object and frees allocated memory.

**Behavior:**
- Sets texture set ID to -1 (0xFFFF)
- Frees main texture buffer if allocated
- Frees secondary buffer if allocated

```cpp
void CMapTex::Reset() {
    m_nTextureSet = -1;
    if (m_pTextureData) {
        free(m_pTextureData);
        m_pTextureData = NULL;
    }
    if (m_pSecondaryData) {
        free(m_pSecondaryData);
        m_pSecondaryData = NULL;
    }
}
```

---

### CMapTex__LoadTexture
| Property | Value |
|----------|-------|
| Address | `0x004911c0` |
| Returns | `int` (1 = success, 0 = failure) |
| Parameters | `const char* filename, int width, int textureIndex` |
| Calling Convention | thiscall (ECX = this) |

**Purpose:** Loads a single TGA texture into the texture array.

**Behavior:**
- Uses CTGALoader to load the TGA file
- Copies RGB data to texture buffer (BGR -> RGBA conversion)
- If alpha channel exists: converts to signed height value (alpha >> 2) - 32
- Tracks min/max height values per texture (stored at offsets +0x1C and +0x34)
- Height range: -32 to +31 (6-bit signed from 8-bit alpha)

**Memory Layout per texel:** 4 bytes (R, G, B, Height)

---

### CMapTex__DownsampleTexture
| Property | Value |
|----------|-------|
| Address | `0x00491340` |
| Returns | `void` |
| Parameters | `byte* destBuffer, byte* srcBuffer` |
| Calling Convention | thiscall (ECX = this) |

**Purpose:** Downsamples a texture by 2x in each dimension using box filter averaging.

**Algorithm:**
- 2x2 box filter: averages 4 source pixels to produce 1 destination pixel
- Processes RGBA separately
- Height channel (alpha) uses signed arithmetic for correct averaging

---

### CMapTex__LoadMixerTextureSet
| Property | Value |
|----------|-------|
| Address | `0x004914b0` |
| Returns | `int` (1 = success, 0 = failure) |
| Parameters | `int setID, int textureCount, int textureWidth` |
| Calling Convention | thiscall (ECX = this) |
| Source Line | 0x97 (151) |

**Purpose:** Loads a complete set of mixer textures for a given terrain set.

**Behavior:**
- Prints warning if loading manually: "Warning : Loading mixer texture set %d manually!"
- Skips if set already loaded (checks m_nTextureSet)
- Frees existing buffers
- Allocates new buffer: `textureWidth * textureWidth * 4 * textureCount` bytes
- Iterates through 6 texture types (grass, rock, sand, snow, road, concrete)
- Loads each via `CMapTex__LoadTexture()`

**Memory Allocation:**
- Uses custom allocator at `0x005490e0` with source tracking (file, line)
- Allocation ID: 0x30

---

### CMapTex__CopyFromOther
| Property | Value |
|----------|-------|
| Address | `0x004915d0` |
| Returns | `void` |
| Parameters | `CMapTex* pSource` |
| Calling Convention | thiscall (ECX = this) |
| Source Line | 0xAF (175) |

**Purpose:** Creates a half-resolution copy from another CMapTex object.

**Behavior:**
- Skips if texture sets match
- Frees existing buffers
- Copies texture set ID and count from source
- Sets width to half of source width (source->width >> 1)
- Allocates new buffer at half resolution
- Copies min/max height values from source
- Downsamples each texture using `CMapTex__DownsampleTexture()`

**Use Case:** Creating LOD (level-of-detail) versions of terrain textures.

---

### CMapTex__Deserialize
| Property | Value |
|----------|-------|
| Address | `0x004916c0` |
| Returns | `void` |
| Calling Convention | thiscall (ECX = this) |
| Source Lines | 0x17C (380), 0x19A (410) |

**Purpose:** Loads CMapTex data from a serialized stream (save file or level data).

**Behavior:**
- Calls stream read functions (`FUN_00423910`, `FUN_00423960`)
- Reads 0x4C (76) bytes of object header data
- If main texture buffer exists:
  - Allocates new buffer: `textureCount * texelSize` bytes
  - Reads texture data from stream
- If secondary buffer exists:
  - Allocates new buffer: `textureCount << 12` bytes (textureCount * 4096)
  - Reads `textureCount << 10` bytes (textureCount * 1024)

**Stream Format:**
1. 76-byte header
2. Main texture data (if present)
3. Secondary texture data (if present)

---

## Related Functions (Not in maptex.cpp)

| Address | Name | Notes |
|---------|------|-------|
| `0x00491060` | Map loader | Calls CHeightField__Load, CMixerMap__Init |
| `0x00549220` | Memory free | Used by Reset() |
| `0x005490e0` | Memory alloc | Custom allocator with source tracking |
| `0x00423910` | Stream read header | Deserialization helper |
| `0x00423960` | Stream read data | Deserialization helper |

## Technical Notes

1. **Texture Set Caching:** Functions check if the requested texture set is already loaded before reloading, using m_nTextureSet as a cache key.

2. **Memory Management:** Uses a custom allocator (0x005490e0) that tracks allocation source (file path and line number) for debugging.

3. **Height Encoding:** Alpha channel encodes height as: `(alpha >> 2) - 32`, giving a signed 6-bit range (-32 to +31).

4. **LOD System:** The CopyFromOther function creates half-resolution copies, suggesting a mipmapping or LOD system for terrain rendering.

5. **Texture Format:** All textures stored as RGBA with 4 bytes per texel, even though source TGAs appear to be RGB with optional alpha.

## String References

| Address | String |
|---------|--------|
| `0x0062da84` | "Deserializing map" |
| `0x0062dae4` | "data\\textures\\mixers\\%s%.2d.tga" |
| `0x0062db04` | "C:\\dev\\ONSLAUGHT2\\maptex.cpp" |
| `0x0062db24` | "Warning : Loading mixer texture set %d manually!" |

## Texture Name Pointers

Array at `0x0062da98`:
- `0x0062dadc` -> "grass"
- `0x0062dad4` -> "rock"
- `0x0062dacc` -> "sand"
- `0x0062dac4` -> "snow"
- `0x0062dabc` -> "road"
- `0x0062dab0` -> "concrete"
