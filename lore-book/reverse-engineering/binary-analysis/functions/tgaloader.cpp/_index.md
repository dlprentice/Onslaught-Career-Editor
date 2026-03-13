# tgaloader.cpp Functions

> Source File: tgaloader.cpp | Binary: BEA.exe
> Debug Path: 0x0063314c (`C:\dev\ONSLAUGHT2\tgaloader.cpp`)

## Overview

TGA (Truevision Graphics Adapter) texture file loader. The `CTGALoader` class handles loading .tga image files, supporting both uncompressed and RLE-compressed formats in 24-bit and 32-bit color depths. Inherits from a base texture loader class (vtable at 0x005df518).

## Functions

| Address | Name | Purpose | Size |
|---------|------|---------|------|
| 0x004f2c60 | CTGALoader__CTGALoader | Constructor - initializes vtable and parent class | ~35 bytes |
| 0x004f2c90 | CTGALoader__scalar_deleting_destructor | MSVC scalar deleting destructor wrapper | ~30 bytes |
| 0x004f2cb0 | CTGALoader__destructor | Base destructor - resets vtable, calls parent destructor | ~11 bytes |
| 0x004f2ce0 | CTGALoader__Load | Main TGA loading function - parses header, handles RLE decompression | ~560 bytes |

**Total: 4 functions identified**

## Class Structure

```cpp
class CTGALoader : public CTextureLoader {  // Base class at 0x00488620
    // Vtable at 0x005df518
    // Object size: 0x118+ bytes (based on constructor offset 0x118)

    // Inherited members from CTextureLoader:
    // +0x00: vtable pointer
    // +0x04: width
    // +0x08: height
    // +0x0C: bits per pixel
    // +0x10: pixel data pointer
    // +0x14: alpha data pointer (for 32-bit)
    // ...
    // +0x118: unknown member (set by constructor param_2)
};
```

## Vtable Layout (0x005df518)

| Offset | Address | Method |
|--------|---------|--------|
| +0x00 | 0x004f2c90 | scalar_deleting_destructor (virtual) |
| +0x04 | 0x004f2ce0 | Load (virtual) |
| +0x08 | 0x00488670 | (inherited) |
| +0x0C | 0x0052f540 | (inherited) |
| +0x10 | 0x00488680 | (inherited) |
| +0x14 | 0x00488690 | (inherited) |
| +0x18 | 0x00453a60 | (inherited) |
| +0x1C | 0x004de070 | (inherited) |

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
- RGB data stored at object+0x10
- Alpha data stored at object+0x14
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
| 0x00491203 | FUN_004911c0 | General texture loading |

### Called Functions
| Address | Name | Purpose |
|---------|------|---------|
| 0x00488620 | CTextureLoader::CTextureLoader | Parent constructor |
| 0x00488700 | CTextureLoader::~CTextureLoader | Parent destructor |
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
buffer = Alloc(width * height * 4, 0x80, "C:\\dev\\ONSLAUGHT2\\tgaloader.cpp", 0x77);
```

This suggests the game uses a debug memory allocator that tracks source file and line number.

## Key Observations

1. **Inheritance Pattern**: CTGALoader inherits from a base texture loader class, following a common polymorphic loader pattern for different image formats.

2. **Alpha Channel Handling**: 32-bit TGA files have their alpha channel extracted and stored separately, likely for engine-specific blending operations.

3. **Debug Memory Tracking**: Memory allocations include source file and line number, indicating debug build features preserved in release.

4. **RLE Support**: Full RLE decompression support for both 24-bit and 32-bit images, reducing texture file sizes.

5. **Orientation Handling**: Proper handling of TGA image orientation flag, ensuring correct display regardless of how the TGA was saved.

6. **Error Handling**: Function returns 0 on failure (invalid format, allocation failure) or 1 on success.

---
*Discovered via Phase 1 xref analysis (Dec 2025)*
