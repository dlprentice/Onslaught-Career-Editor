# bytesprite.cpp - Byte Sprite System

**Source File:** `[maintainer-local-source-export-root]\bytesprite.cpp`
**Debug String Address:** `0x00623c18`

> **Queue status (2026-05-26):** Ghidra export-contract closure **6113/6113** (Wave900: every function commented; clean-signature proxy; not evidence-grade semantics). Lines below that reference a "next raw commentless" row are **archival wave progress**, not open work.

## Overview

The CByteSprite class implements a lightweight sprite rendering system using 8-bit byte pixel data with RLE (Run-Length Encoding) compression. Current saved Ghidra evidence ties the true CByteSprite helper cluster to `0x00418470` through `0x004189f0` and a `CDXCompass__Init` caller.

Wave743 unwind continuation added saved static metadata around the bytesprite.cpp debug path. `0x005d1540 Unwind@005d1540` cleans up a `CResourceDescriptor` stack local at `EBP-0x5b8`, `0x005d1560 Unwind@005d1560` removes a `CParticleManager` stack local at `EBP-0x404` from its global list, `0x005d1580 Unwind@005d1580` calls `CDXMemBuffer__dtor_base` on stack local `EBP-0x140`, and `0x005d158b Unwind@005d158b` frees the pointer at `EBP-0x164` through `OID__FreeObject_Callback` with bytesprite.cpp debug path `0x00623c18`, line `0x1d`, and memtype `0x61`. These rows use `unwind-continuation-wave743` and `wave743-readback-verified`, with verified backup `[maintainer-local-ghidra-backup-root]\BEA_20260522-160155_post_wave743_unwind_continuation_verified`; next high-signal queue head after the wave is `0x005d1610 Unwind@005d1610`, while the raw commentless head remains `0x0042f220 CSPtrSet__Clear`. Runtime byte-sprite/resource/buffer cleanup behavior, exact source identity, and rebuild parity remain unproven.

Wave 314 corrected three adjacent older ByteSprite labels out of this owner group:

- `0x004183d0` is now `CBuildingNamedMesh__dtor_base`.
- `0x00418430` is now `CBuildingNamedMesh__scalar_deleting_dtor`.
- `0x00418450` is now `CBuildingNamedMesh__VFuncSlot_02_RemoveFromWorldAndForwardNamedMesh`.

Those addresses are documented with Building/CBuildingNamedMesh evidence, not CByteSprite evidence.

## Field Evidence

Current saved signatures and decompile comments support the following field-role evidence. This is not a concrete source layout proof:

```cpp
class CByteSprite {
    void*    m_pSpriteData;      // +0x00: Compressed sprite data
    void*    m_pFrameOffsets;    // +0x04: Array of frame offsets
    int      m_nFrameCount;      // +0x08: Number of frames loaded
    void*    m_pTargetBuffer;    // +0x0C: Render target buffer
    int      m_nTargetPitch;     // +0x10: Target buffer pitch (bytes per row)
    int      m_nTargetWidth;     // +0x14: Target buffer width
    int      m_nTargetHeight;    // +0x18: Target buffer height
    byte     m_bWrapFlag;        // +0x1C: horizontal wrap flag in SetTarget context
};
```

The load-time `transparentThreshold` argument is part of the raw-frame/RLE encode path; it should not be conflated with the target wrap flag.

## Functions (9 current CByteSprite targets)

| Address | Name | Description |
|---------|------|-------------|
| `0x00418470` | `CByteSprite__Init` | Initialize sprite object (zeros members) |
| `0x00418480` | `CByteSprite__Free` | Free allocated sprite data |
| `0x004184c0` | `CByteSprite__Load` | Load sprite from `.raw` file; saved `this`, name, dimensions, frame count, and threshold arguments |
| `0x00418720` | `CByteSprite__SetTarget` | Set render target buffer, pitch, width, height, and wrap flag |
| `0x00418750` | `CByteSprite__DrawRLE_NoClip` | Draw RLE sprite span group without horizontal clipping |
| `0x004187e0` | `CByteSprite__DrawRLE_ClipLeft` | Draw RLE sprite span group with left-edge clipping |
| `0x00418880` | `CByteSprite__DrawRLE_ClipRight` | Draw RLE sprite span group with right-edge clipping |
| `0x00418920` | `CByteSprite__DrawFrame` | Draw a frame at position and dispatch to the appropriate RLE draw helper |
| `0x004189f0` | `CByteSprite__EncodeFrame` | Encode raw frame data to compact RLE format |

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

**Saved signature:** `int __thiscall CByteSprite__Load(void * this, char * rawName, int width, int height, int frameCount, byte transparentThreshold)`

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

**Saved signature:** `void __thiscall CByteSprite__SetTarget(void * this, void * targetBuffer, int pitch, int width, int height, byte wrapFlag)`

Sets the render target for drawing operations:
- `m_pTargetBuffer = buffer`
- `m_nTargetPitch = pitch`
- `m_nTargetWidth = width`
- `m_nTargetHeight = height`
- `m_bWrapFlag = wrapFlag` (stored at `+0x1C`)

### CByteSprite__DrawFrame (0x00418920)

**Saved signature:** `void __thiscall CByteSprite__DrawFrame(void * this, int frameIndex, int x, int y)`

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

1. **Transparency**: The load/encode path takes a `transparentThreshold` byte; exact runtime palette/transparency semantics remain bounded to static read-back.
2. **Center-relative**: Frame positions are stored relative to sprite center (width/2, height/2)
3. **Wrap rendering**: Optional horizontal wrap-around for compass-like displays
4. **8-bit palette**: Sprites use 8-bit indexed color (palette lookup happens elsewhere)
5. **Proof boundary**: This note records saved Ghidra signatures/comments and caller evidence only. It does not prove concrete class layout, local names, Ghidra tags, runtime compass rendering, or rebuild parity.
