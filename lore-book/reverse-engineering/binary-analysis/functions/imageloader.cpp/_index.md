# imageloader.cpp Functions

> Source File: imageloader.cpp | Binary: BEA.exe
> Debug Path: 0x0062d3cc (`C:\dev\ONSLAUGHT2\imageloader.cpp`)
> RTTI: 0x0062d3b8 (`.?AVCImageLoader@@`)

## Overview

CImageLoader is an **abstract base class** for image loading. It provides a common interface for loading image dimensions and pixel data, with derived classes (like CTGALoader) implementing format-specific loading.

The class manages two data buffers (width/height) and stores the source filename. Memory allocation uses a global allocator at 0x009c3df0.

## Class Layout

```cpp
class CImageLoader {
    /* +0x00 */ void* vtable;           // Virtual function table
    /* +0x04 */ int   unknown_04;       // Unknown, zeroed in constructor
    /* +0x08 */ int   width;            // Image width
    /* +0x0C */ int   height;           // Image height
    /* +0x10 */ void* widthBuffer;      // Allocated buffer for width data
    /* +0x14 */ void* heightBuffer;     // Allocated buffer for height data
    /* +0x18 */ char  filename[...];    // Source filename (variable length)
};
```

## Virtual Table (0x005dbedc)

| Offset | Address | Method |
|--------|---------|--------|
| 0x00 | 0x004886a0 | ScalarDeletingDestructor |
| 0x04 | 0x0055df1f | (inherited) |
| 0x08 | 0x00488670 | GetFilenamePtr (inline) |
| 0x0C | 0x0052f540 | (inherited) |
| 0x10 | 0x00488680 | GetWidth (inline) |
| 0x14 | 0x00488690 | GetHeight (inline) |
| 0x18 | 0x00453a60 | (inherited) |
| 0x1C | 0x004de070 | (inherited) |
| 0x20 | 0x00405930 | (inherited) |
| 0x24 | 0x00488740 | FreeWidthBuffer |
| 0x28 | 0x00488760 | FreeHeightBuffer |
| 0x2C | 0x00488780 | LoadWidthBuffer |
| 0x30 | 0x004887c0 | LoadHeightBuffer |

## Functions

| Address | Name | Size | Purpose |
|---------|------|------|---------|
| 0x00488620 | CImageLoader__Constructor | ~68 bytes | Initialize instance, copy filename |
| 0x004886a0 | CImageLoader__ScalarDeletingDestructor | ~96 bytes | Destructor with optional heap free |
| 0x00488700 | CImageLoader__Destructor | ~60 bytes | Base destructor, frees buffers |
| 0x00488740 | CImageLoader__FreeWidthBuffer | ~32 bytes | Free width buffer (vtable[0x24]) |
| 0x00488760 | CImageLoader__FreeHeightBuffer | ~32 bytes | Free height buffer (vtable[0x28]) |
| 0x00488780 | CImageLoader__LoadWidthBuffer | ~52 bytes | Allocate and load width data |
| 0x004887c0 | CImageLoader__LoadHeightBuffer | ~52 bytes | Allocate and load height data |

### Inline Getters (Labels, not functions)

| Address | Purpose | Code |
|---------|---------|------|
| 0x00488670 | GetFilenamePtr | `LEA EAX, [ECX+0x18]; RET` |
| 0x00488680 | GetWidth | `MOV EAX, [ECX+0x08]; RET` |
| 0x00488690 | GetHeight | `MOV EAX, [ECX+0x0C]; RET` |

## Function Details

### CImageLoader__Constructor (0x00488620)

**Signature:** `void __thiscall CImageLoader::CImageLoader(const char* filename)`

Initializes a new CImageLoader instance:
1. Zeros member fields (offsets 0x04-0x14)
2. Sets vtable pointer to 0x005dbedc
3. Copies filename string to offset 0x18 using `rep movsd/movsb`

### CImageLoader__LoadWidthBuffer / LoadHeightBuffer

**Pattern:**
1. Call virtual method to free existing buffer (vtable[0x24] or [0x28])
2. Allocate 0x80 (128) bytes via global allocator
3. Store pointer in this+0x10 or this+0x14
4. Return true if allocation succeeded

The line numbers in assert calls (0x2b=43, 0x32=50) indicate original source locations.

## Inheritance Hierarchy

```
CImageLoader (base)
    |
    +-- CTGALoader (TGA format support)
        Constructor: 0x004f2c60
        Destructor:  0x004f2cb0
```

## Memory Allocator

Both Load methods use a global memory allocator:
- **Allocator instance:** 0x009c3df0
- **Alloc function:** 0x005490e0 (size, debug_file, debug_line)
- **Free function:** 0x00549220

## Key Observations

1. **Abstract base class** - Designed for polymorphism, used by CTGALoader and likely other format loaders
2. **Debug asserts preserved** - Line numbers 43 and 50 from original source are embedded
3. **Fixed buffer size** - Both buffers are 128 bytes regardless of image dimensions
4. **thiscall convention** - All methods use ECX as `this` pointer
5. **RAII pattern** - Constructor zeros buffers, destructor frees them

## Related Files

- `CTGALoader` - TGA format implementation (tgaloader.cpp)
- Likely `CBMPLoader` or similar for other formats

---
*Discovered via Phase 1 xref analysis (Dec 2025)*
*7 functions identified and renamed in Ghidra*
