# LandscapeTexture.cpp - Function Analysis

**Source File:** `C:\dev\ONSLAUGHT2\LandscapeTexture.cpp`
**Debug Path Address:** `0x0062d8e0`
**RTTI Class:** `CLandscapeTexture` (type descriptor at `0x0062d8c8`)

## Overview

The `CLandscapeTexture` class manages terrain/landscape texturing in Battle Engine Aquila. It handles texture tile updates, mip-level management, and texture caching for the game's landscape rendering system.

## Class Structure

### VTables

Two vtables were identified:

1. **Base CLandscapeTexture vtable:** `0x005dc1d8`
   - Used by `CLandscapeTexture__Constructor` (sets `*this = &PTR_LAB_005dc1d8`)

2. **Mip-level variant vtable:** `0x005dc1f0`
   - Used by `CLandscapeTexture__ConstructorMip` and `CLandscapeTexture__Destructor`

### Key Member Offsets (from `this` pointer)

| Offset | Type | Purpose |
|--------|------|---------|
| 0x00 | ptr | vtable pointer |
| 0x08 | ptr | Texture surface pointer |
| 0x18 | int | Shared texture flag |
| 0x2c | int | Dirty flag (needs update) |
| 0x30 | int | Tile set index |
| 0x34 | int | Mip level |
| 0x3c | uint | Mask for coordinate calculation |
| 0x40 | ptr | Update buffer pointer |
| 0x44 | int | Update buffer size |
| 0x48 | short | U mask |
| 0x4a | short | V mask |

## Functions (14 total)

| Address | Name | Description |
|---------|------|-------------|
| `0x0048e310` | `CLandscapeTexture__FreeTexture` | Releases texture memory if allocated |
| `0x0048e330` | `CLandscapeTexture__Constructor` | Base constructor, sets vtable |
| `0x0048e360` | `CLandscapeTexture__SetupMipLevel` | Configures mip level and calculates buffer sizes |
| `0x0048e430` | `CLandscapeTexture__ConstructorMip` | Constructor for mip-level textures |
| `0x0048e450` | `CLandscapeTexture__Destructor` | Destructor with reference counting |
| `0x0048e4d0` | `CLandscapeTexture__Init` | Main initialization with mip level setup |
| `0x0048e610` | `CLandscapeTexture__Reset` | Resets texture state, clears update buffer |
| `0x0048e7b0` | `CLandscapeTexture__ResetUpdateQueue` | Resets the tile update queue pointer |
| `0x0048e7c0` | `CLandscapeTexture__FlushUpdateQueue` | Processes pending tile updates |
| `0x0048e880` | `CLandscapeTexture__QueueTileUpdate` | Queues a tile for texture update |
| `0x0048e950` | `CLandscapeTexture__CopyTileToTexture` | Copies tile data to GPU texture |
| `0x0048ea80` | `CLandscapeTexture__UpdateTile` | Main tile update function |
| `0x0048ee00` | `CLandscapeTexture__BlendAlpha` | Alpha blending for texture compositing |
| `0x0048ef00` | `CLandscapeTexture__UpdateTileRange` | Updates a range of tiles |

## Detailed Function Analysis

### CLandscapeTexture__Constructor (0x0048e330)

```cpp
void CLandscapeTexture__Constructor(void) {
    // thiscall - ECX = this
    FUN_00488210();  // Parent constructor
    *this = &PTR_LAB_005dc1d8;  // Set vtable
    this[0xb] = 0;  // Clear member
}
```

### CLandscapeTexture__ConstructorMip (0x0048e430)

```cpp
void CLandscapeTexture__ConstructorMip(void) {
    FUN_004f79d0();  // Parent constructor (different from base)
    *this = &PTR_LAB_005dc1f0;  // Mip variant vtable
    this[0xb] = 0;
    this[0x10] = 0;  // Clear update buffer pointer
}
```

### CLandscapeTexture__Init (0x0048e4d0)

Main initialization function referenced by debug path at line 0x5b (91).

```cpp
undefined4 CLandscapeTexture__Init(int mipLevel, int param_2) {
    this[0xd] = mipLevel;

    // Set UV masks based on mip level
    switch(mipLevel) {
        case 0: uMask = 0x3f;  vMask = 0xfc0;  break;
        case 1: uMask = 0x1f;  vMask = 0x7c0;  break;
        case 2: uMask = 0x0f;  vMask = 0x3c0;  break;
        case 3: uMask = 0x07;  vMask = 0x1c0;  break;
        case 4: uMask = 0x03;  vMask = 0x0c0;  break;
    }

    // Calculate texture dimensions: 512 / (1 << mipLevel)
    int size = 0x200 / (1 << mipLevel);
    this[0xe] = size;
    this[0xf] = size - 1;
    this[0xc] = param_2;

    // Call virtual function (likely parent init)
    (**(this->vtable + 4))();

    // Increment global texture count
    DAT_006fabf8++;

    // Allocate update buffer for non-zero mip levels
    if (mipLevel != 0) {
        int bufSize = (512 / (8 << mipLevel))^2;
        this[0x11] = bufSize;
        this[0x10] = OID__AllocObject(bufSize * 2, 0x35,
                      "C:\\dev\\ONSLAUGHT2\\LandscapeTexture.cpp", 0x5b);
        // Initialize buffer to 0xFFFFFFFF
        memset(this[0x10], 0xFF, bufSize * 2);
    }

    // Create texture and setup rendering
    ...
}
```

### CLandscapeTexture__Destructor (0x0048e450)

```cpp
void CLandscapeTexture__Destructor(void) {
    *this = &PTR_LAB_005dc1f0;  // Restore vtable

    // Free update buffer
    if (this[0x10] != 0) {
        OID__FreeObject(this[0x10]);
    }

    // Decrement global texture count
    DAT_006fabf8--;

    // If last texture, cleanup shared resources
    if (DAT_006fabf8 == 0) {
        (*DAT_006fabf4->vtable[8])(DAT_006fabf4);
        DAT_006fabf4 = NULL;
    }

    FUN_004f7a40();  // Parent destructor
}
```

### CLandscapeTexture__QueueTileUpdate (0x0048e880)

Queues a tile for texture update using coordinate encoding.

```cpp
void CLandscapeTexture__QueueTileUpdate(uint tileCoord, undefined4 param_2) {
    byte mipShift = this[0x34];
    uint mask = this[0x3c];

    // Calculate texture coordinates
    int texY = ((tileCoord & 0xFFFF) >> 3 & mask & 0xFFFFFFF8) << mipShift;
    int texX = ((tileCoord & 0x3F) << 3 & mask) << mipShift;

    // Search existing queue for duplicate
    int* queue = &DAT_006fa7d8;
    while (queue < PTR_DAT_0062d868) {
        if (queue[3] == texX && queue[4] == texY && *queue == this) {
            // Found existing entry - update it
            ...
        }
        queue += 5;
    }

    // Check queue overflow
    if (PTR_DAT_0062d868 > 0x6fabbf) {
        CLandscapeTexture__FlushUpdateQueue();
    }

    // Add new entry to queue (20 bytes per entry)
    *(PTR_DAT_0062d868 + 0) = this;
    *(PTR_DAT_0062d868 + 4) = tileCoord & 0xFFFF;
    *(PTR_DAT_0062d868 + 8) = param_2;
    *(PTR_DAT_0062d868 + 12) = texX;
    *(PTR_DAT_0062d868 + 16) = texY;
    PTR_DAT_0062d868 += 0x14;
}
```

### CLandscapeTexture__BlendAlpha (0x0048ee00)

Alpha blending function for compositing textures. Uses 5-6-5 RGB565 format.

```cpp
void CLandscapeTexture__BlendAlpha(short* dest, int pitch, byte* alpha,
                                    int x, int y, byte level, int size) {
    int dim = 1 << level;

    // Handle clipping
    if (x < 0) { dim += x; alpha -= x; }
    else { dest += x; if (size < dim + x) dim = size - x; }

    if (y < 0) { ... similar y clipping ... }

    // Blend loop
    for (int row = 0; row < rowCount; row++) {
        for (int col = 0; col < colCount; col++) {
            if (*alpha < 0x20) {
                // RGB565 alpha blend: (pixel & 0x7e0f81f) * alpha >> 5
                uint blended = (CONCAT22(*dest, *dest) & 0x7e0f81f) * (*alpha) >> 5 & 0x7e0f81f;
                *dest = (short)(blended >> 16) + (short)blended;
            }
            dest++; alpha++;
        }
        alpha += dim;
        dest += pitch;
    }
}
```

## Global Variables

| Address | Name | Purpose |
|---------|------|---------|
| `0x006fabf8` | Texture count | Global count of CLandscapeTexture instances |
| `0x006fabf4` | Shared texture surface | Shared DirectX texture surface |
| `0x006fabf0` | Global mip level | Current rendering mip level |
| `0x006fabcc` | Per-instance flag | Controls shared vs per-instance textures |
| `0x0062d868` | Update queue pointer | Points to current position in tile update queue |
| `0x006fa7d8` | Update queue base | Base address of tile update queue |
| `0x0067a7d8` | Texture data buffer | Main texture data storage |

## Related Files

- **DXLandscape.cpp** - Calls `CLandscapeTexture__Init` and `CLandscapeTexture__ConstructorMip`
- **Landscape system** - Part of the terrain rendering pipeline

## Technical Notes

1. **Mip Level System**: Texture sizes are 512 / (1 << mipLevel):
   - Level 0: 512x512
   - Level 1: 256x256
   - Level 2: 128x128
   - Level 3: 64x64
   - Level 4: 32x32

2. **Tile Update Queue**: Uses a static queue at `0x006fa7d8` with 20-byte entries containing:
   - Object pointer (4 bytes)
   - Tile coordinate (2 bytes + 2 padding)
   - Update parameter (4 bytes)
   - Texture X coordinate (4 bytes)
   - Texture Y coordinate (4 bytes)

3. **RGB565 Blending**: The `BlendAlpha` function uses a clever bit manipulation trick for RGB565 alpha blending that processes R, G, B channels in parallel.

4. **Reference Counting**: The destructor implements reference counting for shared texture surfaces via `DAT_006fabf8`.

## Cross-References

Functions called from:
- `FUN_005447e0` (DXLandscape.cpp) - Creates mip texture array
- `FUN_00544af0` (DXLandscape.cpp) - Initializes landscape system

Functions that call landscape functions:
- `FUN_0047eff0` - Tile rendering helper (called by UpdateTile)
