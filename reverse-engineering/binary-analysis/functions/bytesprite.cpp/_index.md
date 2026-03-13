# bytesprite.cpp - Byte Sprite System

**Source File:** `C:\dev\ONSLAUGHT2\bytesprite.cpp`
**Debug String Address:** `0x00623c18`

## Overview

The CByteSprite class implements a lightweight sprite rendering system using 8-bit (byte) pixel data with RLE (Run-Length Encoding) compression. This system is used for HUD elements and UI sprites that need efficient storage and fast rendering.

## Class Structure

Based on decompiled code analysis, the CByteSprite class has the following layout:

```cpp
class CByteSprite {
    void*    m_pSpriteData;      // +0x00: Compressed sprite data
    void*    m_pFrameOffsets;    // +0x04: Array of frame offsets
    int      m_nFrameCount;      // +0x08: Number of frames loaded
    void*    m_pTargetBuffer;    // +0x0C: Render target buffer
    int      m_nTargetPitch;     // +0x10: Target buffer pitch (bytes per row)
    int      m_nTargetWidth;     // +0x14: Target buffer width
    int      m_nTargetHeight;    // +0x18: Target buffer height
    byte     m_bTransparentVal;  // +0x1C: Transparency threshold value
    // ... additional fields including wrap flag at offset 0x1C (in int form)
};
```

## Functions (11 total)

| Address | Name | Description |
|---------|------|-------------|
| `0x004183d0` | `CByteSprite__dtor_base` | Base destructor - sets up vtable pointers |
| `0x00418430` | `CByteSprite__scalar_deleting_dtor` | Scalar deleting destructor |
| `0x00418450` | `CByteSprite__vfunc_stub` | Virtual function stub |
| `0x00418470` | `CByteSprite__Init` | Initialize sprite object (zeros members) |
| `0x00418480` | `CByteSprite__Free` | Free allocated sprite data |
| `0x004184c0` | `CByteSprite__Load` | Load sprite from .raw file |
| `0x00418720` | `CByteSprite__SetTarget` | Set render target buffer |
| `0x00418750` | `CByteSprite__DrawRLE_NoClip` | Draw RLE sprite (no clipping) |
| `0x004187e0` | `CByteSprite__DrawRLE_ClipLeft` | Draw RLE sprite with left edge clipping |
| `0x00418880` | `CByteSprite__DrawRLE_ClipRight` | Draw RLE sprite with right edge clipping |
| `0x00418920` | `CByteSprite__DrawFrame` | Draw a frame at position (dispatches to appropriate draw function) |
| `0x004189f0` | `CByteSprite__EncodeFrame` | Encode raw frame data to RLE format |

## Function Details

### CByteSprite__Init (0x00418470)

Initializes a CByteSprite object by zeroing the first three members:
- `m_pSpriteData = NULL`
- `m_pFrameOffsets = NULL`
- `m_nFrameCount = 0`

### CByteSprite__Free (0x00418480)

Frees allocated memory for sprite data and frame offsets:
```cpp
if (m_pSpriteData) { free(m_pSpriteData); m_pSpriteData = NULL; }
if (m_pFrameOffsets) { free(m_pFrameOffsets); m_pFrameOffsets = NULL; }
```

### CByteSprite__Load (0x004184c0)

**Signature:** `int Load(const char* name, int width, int height, int frameCount, byte transparentThreshold)`

Loads sprite data from a raw file:
1. Constructs filename as `"data_%s.raw"` from the name parameter
2. Opens file for reading
3. Allocates temporary buffers for raw frame data
4. Reads each frame (width * height bytes)
5. Calls `EncodeFrame()` to compress each frame to RLE
6. Copies compressed data to final sprite storage
7. Frees temporary buffers
8. Returns number of frames loaded

Memory allocations use debug tags with source file and line numbers (0x1d = 29, 0xbd = 189, 0xbe = 190, 0xbf = 191).

### CByteSprite__SetTarget (0x00418720)

**Signature:** `void SetTarget(void* buffer, int pitch, int width, int height, byte wrapFlag)`

Sets the render target for drawing operations:
- `m_pTargetBuffer = buffer`
- `m_nTargetPitch = pitch`
- `m_nTargetWidth = width`
- `m_nTargetHeight = height`
- `m_bTransparentVal = wrapFlag` (stored at +0x1C)

### CByteSprite__DrawFrame (0x00418920)

**Signature:** `void DrawFrame(int frameIndex, int x, int y)`

Main entry point for drawing a sprite frame:
1. Validates frame index against `m_nFrameCount`
2. Gets frame data pointer from offset table
3. Reads frame header (x offset, y offset, width, height as signed bytes)
4. Adjusts x/y by sprite's center offset
5. Performs bounds checking
6. Dispatches to appropriate draw function based on clipping needs:
   - `DrawRLE_NoClip` - sprite fully within bounds
   - `DrawRLE_ClipLeft` - sprite extends past left edge
   - `DrawRLE_ClipRight` - sprite extends past right edge
7. Handles wrap-around rendering if wrap flag is set

### CByteSprite__EncodeFrame (0x004189f0)

Encodes raw pixel data to RLE format:

1. Scans raw frame to find bounding box of non-transparent pixels
2. Writes frame header (4 bytes): x offset, y offset, width, height (relative to center)
3. For each scanline, writes RLE packets:
   - Positive byte N followed by N pixel values (run of opaque pixels)
   - Negative byte -N means skip N transparent pixels
   - Zero byte marks end of scanline
4. Updates frame offset table
5. Returns 1 on success, 0 if no visible pixels

### RLE Drawing Functions

All three RLE drawing functions share similar logic:
- `DrawRLE_NoClip` (0x00418750): Fastest path, no bounds checking
- `DrawRLE_ClipLeft` (0x004187e0): Clips pixels with x < 0
- `DrawRLE_ClipRight` (0x00418880): Clips pixels with x >= targetWidth

**RLE Format:**
- Byte > 0: Copy next N bytes to output
- Byte < 0: Skip |N| pixels (transparent)
- Byte == 0: End of scanline

## Usage Context

CByteSprite is used by the compass HUD (DXCompass.cpp) for rendering animated indicators. The caller at `0x0053be40` shows:
```cpp
// Load compass sprites: 16x16 pixels, 20 frames, transparency threshold 4
sprite->Load("compass", 16, 16, 20, 4);
```

## Memory Allocation Tags

Memory allocations use tag `0x61` ('a') for temporary loading buffers and `0x4d` ('M') for final sprite storage.

## Technical Notes

1. **Transparency**: Pixels with value < `m_bTransparentVal` are considered transparent
2. **Center-relative**: Frame positions are stored relative to sprite center (width/2, height/2)
3. **Wrap rendering**: Optional horizontal wrap-around for compass-like displays
4. **8-bit palette**: Sprites use 8-bit indexed color (palette lookup happens elsewhere)
