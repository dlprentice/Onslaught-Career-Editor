# tgaloader.cpp Functions

> Source File: tgaloader.cpp | Binary: BEA.exe
> Debug Path: 0x0063314c (`[maintainer-local-source-export-root]\tgaloader.cpp`)

> **Queue status (2026-05-26):** Ghidra export-contract closure **6113/6113** (Wave900: every function commented; clean-signature proxy; not evidence-grade semantics). Lines below that reference a "next raw commentless" row are **archival wave progress**, not open work.

## Overview

TGA (Truevision Graphics Adapter) texture file loader. The `CTGALoader` class handles `.tga` image files, supporting uncompressed and RLE-compressed formats in 24-bit and 32-bit color depths under the current static evidence. It inherits from the `CImageLoader` base class and installs vtable `0x005df518`.

Wave513 refreshed this page on 2026-05-17 after saved Ghidra read-back for all four CTGALoader methods plus the adjacent 24-bit writer at `0x004f3110`. Wave1079 recovered the adjacent compact CTGALoader vtable slot-8 status-output helper at `0x004f2cc0`.

## Functions

| Address | Name | Purpose | Size |
|---------|------|---------|------|
| 0x004f2c60 | CTGALoader__CTGALoader | Constructor: calls `CImageLoader__Constructor`, installs vtable, stores caller `status_out` at `this+0x118` | ~35 bytes |
| 0x004f2c90 | CTGALoader__ScalarDeletingDestructor | MSVC scalar deleting destructor wrapper | ~30 bytes |
| 0x004f2cb0 | CTGALoader__Destructor | Destructor body: restores CTGALoader vtable and chains to `CImageLoader__Destructor` | ~11 bytes |
| 0x004f2cc0 | CTGALoader__HasNonzeroStatusOut_004f2cc0 | Compact vtable slot-8 helper: checks the constructor-stored `status_out` pointer at `this+0x118` and returns whether the pointed dword is nonzero | ~24 bytes |
| 0x004f2ce0 | CTGALoader__Load | Main TGA loading function: parses header, handles raw/RLE data, and splits alpha for 32-bit images | ~560 bytes |
| 0x004f3110 | ImageIO__WriteTGA24 | Shared 24-bit TGA writer used by screenshot and texture-dump callsites | ~140 bytes |

**Total: 6 functions documented in this page**

## Class Structure

```cpp
class CTGALoader : public CImageLoader {  // Base constructor at 0x00488620
    // Vtable at 0x005df518
    // Object size: at least 0x11c bytes based on constructor offset 0x118

    // Inherited/loader fields under current static evidence:
    // +0x00: vtable pointer
    // +0x04/+0x08/+0x0C: header-derived scalar fields; Wave414 getter evidence names +0x08/+0x0C as width/height,
    //                   but CTGALoader::Load field semantics are still not fully reconciled.
    // +0x10: RGB/width-buffer pointer under current ImageLoader evidence
    // +0x14: alpha/height-buffer pointer, used by CTGALoader for 32-bit alpha separation
    // ...
    // +0x118: caller status/output pointer; CTGALoader__Load writes 4 on the alpha path,
    //         and Wave1079 recovered a slot-8 helper that returns whether the pointed dword is nonzero.
};
```

## Vtable Layout (0x005df518)

| Offset | Address | Method |
|--------|---------|--------|
| +0x00 | 0x004f2c90 | scalar_deleting_destructor (virtual) |
| +0x04 | 0x004f2ce0 | Load (virtual) |
| +0x08 | 0x00488670 | CImageLoader__GetFilenamePtr (inherited) |
| +0x0C | 0x0052f540 | SharedVFunc__ReturnField04_0052f540 (shared inherited getter) |
| +0x10 | 0x00488680 | CImageLoader__GetWidth (inherited) |
| +0x14 | 0x00488690 | CImageLoader__GetHeight (inherited) |
| +0x18 | 0x00453a60 | (inherited) |
| +0x1C | 0x004de070 | SharedVFunc__ReturnField14_004de070 (shared inherited getter) |
| +0x20 | 0x004f2cc0 | CTGALoader__HasNonzeroStatusOut_004f2cc0 (Wave1079 boundary recovery) |
| +0x24 | 0x00488740 | CImageLoader__FreeWidthBuffer (inherited) |
| +0x28 | 0x00488760 | CImageLoader__FreeHeightBuffer (inherited) |
| +0x2C | 0x00488780 | CImageLoader__LoadWidthBuffer (inherited) |
| +0x30 | 0x004887c0 | CImageLoader__LoadHeightBuffer (inherited) |

Wave414 created the missing inherited getter function boundaries at `0x00488670`, `0x00488680`, `0x00488690`, `0x0052f540`, and `0x004de070` while auditing the ImageLoader vtable. This updates the inherited-vtable evidence only; CTGALoader runtime image decoding behavior remains bounded by the existing static Load evidence.

Wave513 then renamed the CTGALoader destructor entries to `CTGALoader__ScalarDeletingDestructor` and `CTGALoader__Destructor`, saved the constructor as `void * __thiscall CTGALoader__CTGALoader(void * this, char * filename, void * status_out)`, and saved the loader as `bool __thiscall CTGALoader__Load(void * this)`.

Wave1079 (`texture-tga-table-review-wave1079`, `wave1079-readback-verified`) recovered `0x004f2cc0 CTGALoader__HasNonzeroStatusOut_004f2cc0` as a saved `bool __thiscall` function. Fresh static evidence ties CTGALoader vtable `0x005df518` slot `8` at slot address `0x005df538` to the body; pre-read recorded it as `NO_FUNCTION_AT_POINTER`, and post-read verified a 9-instruction function that reads `this+0x118`, returns false for null or zero pointed status, returns true for nonzero pointed status, and stops before `0x004f2ce0 CTGALoader__Load`. Adjacent TerrainGuide slot `0x005df514` points at `0x00616dd0`, which dumps as an empty string/table-boundary context rather than a CTGALoader function. Queue closure after Wave1079 is `6262/6262 = 100.00%`; Wave911 focused progress remains `812/1408 = 57.67%`; expanded static surface advances to `1373/1560 = 88.01%`; top-500 coverage remains `500/500 = 100.00%`. Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260602-085858_post_wave1079_texture_tga_table_review_verified`. Exact source virtual name, exact status-output field semantics, runtime TGA/image-loading behavior, BEA patching, gameplay outcomes, and rebuild parity remain separate proof. Probe token anchor: Wave1079; texture-tga-table-review-wave1079; 0x004f2cc0 CTGALoader__HasNonzeroStatusOut_004f2cc0; 0x005df518; 0x005df538; 0x004f2ce0 CTGALoader__Load; 0x00616dd0; 812/1408 = 57.67%; 1373/1560 = 88.01%; 500/500 = 100.00%; 6262/6262 = 100.00%; [maintainer-local-ghidra-backup-root]\BEA_20260602-085858_post_wave1079_texture_tga_table_review_verified; boundary recovery.

## TGA Format Support

### Image Types
- **Type 2 (0x02)**: Uncompressed RGB/RGBA
- **Type 10 (0x0A)**: RLE compressed RGB/RGBA

### Color Depths
- **24-bit (0x18)**: RGB format, 3 bytes per pixel
- **32-bit (0x20)**: RGBA format, 4 bytes per pixel (alpha channel separated)

### TGA Header (18 bytes at offset 0x12)
```cpp
struct TGAHeader {
    uint8_t  idLength;        // +0x00
    uint8_t  colorMapType;    // +0x01
    uint8_t  imageType;       // +0x02 (2=uncompressed, 10=RLE)
    uint16_t colorMapStart;   // +0x03
    uint16_t colorMapLength;  // +0x05
    uint8_t  colorMapDepth;   // +0x07
    uint16_t xOrigin;         // +0x08
    uint16_t yOrigin;         // +0x0A
    uint16_t width;           // +0x0C
    uint16_t height;          // +0x0E
    uint8_t  bitsPerPixel;    // +0x10 (24 or 32)
    uint8_t  imageDescriptor; // +0x11 (bit 5 = top-to-bottom)
};
```

## Key Algorithms

### RLE Decompression
The Load function implements standard TGA RLE decompression:
- Read packet header byte
- Bit 7 (0x80): Run-length packet (1) vs raw packet (0)
- Bits 0-6 (0x7F): Pixel count minus 1 (1-128 pixels)

```cpp
// Pseudocode for RLE decompression
while (pixelsRemaining > 0) {
    byte header = ReadByte();
    int count = (header & 0x7F) + 1;
    pixelsRemaining -= count;

    if (header & 0x80) {
        // Run-length packet: read one pixel, repeat 'count' times
        pixel = ReadPixel();
        for (int i = 0; i < count; i++)
            WritePixel(pixel);
    } else {
        // Raw packet: read 'count' pixels
        for (int i = 0; i < count; i++)
            WritePixel(ReadPixel());
    }
}
```

### 32-bit Alpha Separation
For 32-bit TGA files, the alpha channel is separated from RGB:
- RGB data stored at inherited buffer pointer `this+0x10`
- Alpha data stored at inherited buffer pointer `this+0x14`
- This allows independent access to color and transparency

### Image Orientation
The `imageDescriptor` field bit 5 controls vertical orientation:
- 0: Bottom-to-top (standard TGA)
- 1: Top-to-bottom
The loader handles both orientations by adjusting write pointers.

## Cross-References

### Callers (who loads TGA files)
| Address | Function | Context |
|---------|----------|---------|
| 0x00440cb8 | CDamage__LoadDamageTexture | Loading damage overlay textures |
| 0x00491203 | CMapTex__LoadTexture | Map texture loading |

### Called Functions / Slots
| Address | Name | Purpose |
|---------|------|---------|
| 0x00488620 | CImageLoader__Constructor | Parent constructor |
| 0x00488700 | CImageLoader__Destructor | Parent destructor |
| 0x00547d70 | (stream init) | Initialize file stream |
| 0x00547d90 | (stream cleanup) | Cleanup file stream |
| 0x00547ec0 | (stream seek/validate) | Validate file access |
| 0x00548570 | (stream read) | Read bytes from stream |
| 0x00548c00 | (stream close) | Close file stream |
| 0x005490e0 | (memory alloc) | Allocate memory with debug info |
| 0x00549220 | (memory free) | Free allocated memory |

## Memory Allocation

The Load function allocates temporary buffer for 32-bit images:
```cpp
// Allocation at line 0x77 (119) in tgaloader.cpp
buffer = Alloc(width * height * 4, 0x80, "[maintainer-local-source-export-root]\\tgaloader.cpp", 0x77);
```

This suggests the game uses a debug memory allocator that tracks source file and line number.

## 24-bit Writer

`ImageIO__WriteTGA24` at `0x004f3110` is saved as:

```cpp
bool __cdecl ImageIO__WriteTGA24(char * path, void * pixels32, int width, int height, int pitch_bytes)
```

It writes an uncompressed 18-byte TGA header, walks a 32-bit source buffer bottom-up using `pitch_bytes`, emits three bytes per pixel, closes the file, and returns success/failure. Stuart's `ltshell.cpp` calls the analogous `CTGALoader::Save24BitWithPitch(name, pixels, width, height, pitch)` from screenshot capture, and retail xrefs also include `CDXTexture__DumpTextureToRGBA`.

## Key Observations

1. **Inheritance Pattern**: CTGALoader inherits from a base texture loader class, following a common polymorphic loader pattern for different image formats.

2. **Alpha Channel Handling**: 32-bit TGA files have their alpha channel extracted and stored separately, likely for engine-specific blending operations.

3. **Debug Memory Tracking**: Memory allocations include source file and line number, indicating debug build features preserved in release.

4. **RLE Support**: Static evidence shows RLE decompression support for both 24-bit and 32-bit images.

5. **Orientation Handling**: Proper handling of TGA image orientation flag, ensuring correct display regardless of how the TGA was saved.

6. **Error Handling**: Function returns 0 on failure (invalid format, allocation failure) or 1 on success.

---
Read-back evidence: `release/readiness/ghidra_texture_tga_wave513_2026-05-17.md`. Runtime image loading, malformed-file behavior, exact source-body identity, complete class layouts, and rebuild parity remain unproven.
