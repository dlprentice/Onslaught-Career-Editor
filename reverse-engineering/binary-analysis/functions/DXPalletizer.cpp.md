# DXPalletizer.cpp - Function Mappings

> Color palette quantization system for 8-bit indexed textures
> Source file: `C:\dev\ONSLAUGHT2\DXPalletizer.cpp`
> Debug path address: `0x00651d60`

## Overview

DXPalletizer implements an **octree-based color quantization** system for converting 32-bit RGBA textures to 8-bit indexed (palettized) textures. This is a common technique in game engines for reducing texture memory while maintaining visual quality.

The system uses:
- **Octree data structure** - 16-entry child nodes (2^4 for RGBA bit levels)
- **Color frequency tracking** - Counts pixels per color region
- **Manhattan distance** - For nearest-color matching in palette lookup
- **Console texture swizzling** - Morton order reordering for GPU cache efficiency

## Functions (9 total)

| Address | Name | Size | Purpose |
|---------|------|------|---------|
| 0x0054e9d0 | DXPalletizer__Palletize | ~610 | Main entry point - converts RGBA to indexed |
| 0x0054e500 | DXPalletizer__InsertColor | ~432 | Insert color into octree, creating nodes as needed |
| 0x0054e6e0 | DXPalletizer__AssignPaletteIndices | ~176 | Recursively assign palette indices to leaf nodes |
| 0x0054e790 | DXPalletizer__CollapseOctreeNode | ~448 | Collapse octree nodes to reduce colors |
| 0x0054e670 | DXPalletizer__BuildPalette | ~112 | Extract final palette from octree |
| 0x0054e950 | DXPalletizer__FreeOctreeNode | ~128 | Recursively free octree node memory |
| 0x0054ef70 | DXPalletizer__FindNearestColor | ~256 | Find closest palette entry using Manhattan distance |
| 0x0054f380 | DXPalletizer__SwizzleTexture | ~528 | Swizzle texture for console GPU (Morton order) |
| 0x0054f090 | DXPalletizer__SwizzleBlock | ~560 | Swizzle individual texture block (16x16 or smaller) |

---

## Function Details

### DXPalletizer__Palletize (0x0054e9d0)

**Main quantization entry point**

```c
void DXPalletizer__Palletize(
    int sourcePixels,      // RGBA pixel data
    int width,             // Texture width
    int height,            // Texture height
    uint paletteSize,      // Target palette size (usually 256)
    uint* outIndices,      // Output: indexed pixel data
    uint* outPalette,      // Output: RGBA palette entries
    int hasAlpha,          // Source has alpha channel
    int allocBuffers,      // Allocate output buffers internally
    int useSwizzle,        // Apply console swizzling
    int preserveAlpha,     // Keep alpha in output
    int param_11,          // Unknown flag
    int param_12           // Unknown flag
);
```

**Algorithm:**
1. Allocates octree root node (0x54 bytes)
2. Iterates all source pixels, inserting into octree
3. Collapses octree to fit target palette size
4. Builds final palette from remaining nodes
5. Maps each pixel to nearest palette entry
6. Optionally swizzles output for console GPU

**Memory allocations:**
- Line 0xee (238): Octree root node - 0x54 bytes
- Line 0xf4 (244): Palette buffer - paletteSize * 4 bytes
- Line 0x136 (310): Index buffer - width * height bytes
- Line 0x147 (327): Temp index buffer - width * height bytes

---

### DXPalletizer__InsertColor (0x0054e500)

**Insert color into octree**

```c
int DXPalletizer__InsertColor(
    byte r,        // Red component
    byte g,        // Green component
    byte b,        // Blue component
    byte a,        // Alpha component
    byte depth     // Current bit depth (starts at 7)
);
```

**Octree Node Structure (0x54 bytes):**
```c
struct OctreeNode {
    byte r, g, b, a;           // 0x00: Color values (center of region)
    byte maxR, maxG, maxB, maxA; // 0x04: Max bounds (0xFF initially)
    uint pixelCount;           // 0x08: Number of pixels in this region
    uint isLeaf;               // 0x0C: 1 if leaf node, 0 if branch
    uint flags;                // 0x10: Node flags
    uint children[16];         // 0x14: Child node pointers (2^4 for RGBA bits)
};
```

**Algorithm:**
- Walks down octree from MSB to LSB of each color channel
- Creates child nodes as needed (16 children per level for 4-bit index)
- At depth 0 (leaf), stores exact color and increments pixel count
- At higher depths, stores region center color

---

### DXPalletizer__AssignPaletteIndices (0x0054e6e0)

**Assign palette indices to leaf nodes**

```c
int DXPalletizer__AssignPaletteIndices(
    int* paletteCounter,   // Current palette index counter
    uint threshold         // Minimum pixel count to include
);
```

**Algorithm:**
- Recursively traverses octree
- Leaf nodes with pixelCount >= threshold get assigned a palette index
- Non-leaf nodes recurse into all 16 children
- Returns total pixels assigned

---

### DXPalletizer__CollapseOctreeNode (0x0054e790)

**Collapse octree to reduce palette size**

```c
void DXPalletizer__CollapseOctreeNode(void);
```

**Algorithm:**
- Checks if all children are leaves
- If so, merges children into parent:
  - Sums pixel counts
  - Sets isLeaf = 1
  - Frees child nodes
- If not, recursively collapses children first
- Called repeatedly until palette fits target size

---

### DXPalletizer__BuildPalette (0x0054e670)

**Extract palette from octree**

```c
void DXPalletizer__BuildPalette(int paletteBuffer);
```

**Algorithm:**
- Recursively walks octree
- For each node with assigned index (index >= 0):
  - Writes RGBA color to `paletteBuffer[index * 4]`
- Iterates all 16 children recursively

---

### DXPalletizer__FreeOctreeNode (0x0054e950)

**Free octree node and children**

```c
int DXPalletizer__FreeOctreeNode(byte shouldFree);
```

**Algorithm:**
- Recursively frees all 16 children
- If shouldFree & 1, frees self via OID__FreeObject (OID_Free)
- Returns node pointer

---

### DXPalletizer__FindNearestColor (0x0054ef70)

**Find nearest palette entry**

```c
byte DXPalletizer__FindNearestColor(
    uint r,    // Red component
    uint g,    // Green component
    uint b,    // Blue component
    uint a     // Alpha component
);
```

**Algorithm:**
- Uses **Manhattan distance** (sum of absolute differences)
- Distance = |r1-r2| + |g1-g2| + |b1-b2| + |a1-a2|
- Iterates palette entries from ECX pointer
- Palette count at offset 0x400 from palette base
- Returns index of closest match

---

### DXPalletizer__SwizzleTexture (0x0054f380)

**Swizzle texture for console GPU**

```c
int DXPalletizer__SwizzleTexture(
    int width,         // Texture width
    int height,        // Texture height
    void* srcIndices,  // Source indexed pixels
    void* dstSwizzled  // Output swizzled data
);
```

**Algorithm:**
- Validates dimensions are powers of 2 (up to 1024)
- Divides texture into 128x64 blocks (or smaller for small textures)
- Calls SwizzleBlock for each block
- Uses lookup tables at:
  - 0x00651760: Small texture swizzle table
  - 0x00651960: Large texture swizzle table
  - 0x00651c60: Block index table
  - 0x00651ce0: Morton order table

---

### DXPalletizer__SwizzleBlock (0x0054f090)

**Swizzle individual texture block**

```c
int DXPalletizer__SwizzleBlock(
    int blockWidth,     // Block width (up to 128)
    int blockHeight,    // Block height (up to 64)
    void* srcBlock,     // Source block data
    void* dstSwizzled   // Output swizzled block
);
```

**Morton Order Tables:**
- 0x00651ce0: 4x8 lookup table for Morton indices
- Used to reorder pixels for GPU texture cache coherency

---

## Data References

| Address | Type | Purpose |
|---------|------|---------|
| 0x00651d60 | string | Debug path "C:\dev\ONSLAUGHT2\DXPalletizer.cpp" |
| 0x00651760 | int[128] | Small texture swizzle table |
| 0x00651960 | int[128] | Large texture swizzle table |
| 0x00651c60 | int[] | Block index lookup table |
| 0x00651ce0 | int[32] | Morton order lookup (4x8) |
| 0x006fbe44 | uint | Global: DAT_006fbe44 (palette scaling factor 1) |
| 0x006fbe54 | uint | Global: DAT_006fbe54 (palette scaling factor 2) |

---

## Technical Notes

### Octree Color Quantization

The octree structure efficiently represents the color space:
- 8 bits per channel = 8 levels of tree depth
- Each node can have up to 16 children (2^4 for RGBA)
- Leaf nodes represent actual colors used
- Branch nodes represent color regions

### Console Swizzling (Morton Order)

Console GPUs (PS2/Xbox) use different texture memory layouts than PC:
- **Linear**: Row-by-row (PC standard)
- **Morton/Z-order**: Interleaved bits for better cache locality

The swizzle functions convert linear indexed textures to Morton order for console GPU compatibility.

### Memory Allocation Pattern

All allocations use `OID__AllocObject`:
```c
OID__AllocObject(size, type, debugFile, debugLine);
```
- type 0x5f: Octree nodes
- type 0x61: Pixel/palette buffers

---

## Call Graph

```
DXPalletizer__Palletize
    |
    +-> OID__AllocObject (octree root)
    +-> DXPalletizer__InsertColor (for each pixel)
    |       +-> OID__AllocObject (child nodes)
    |
    +-> DXPalletizer__AssignPaletteIndices
    +-> DXPalletizer__CollapseOctreeNode
    |       +-> DXPalletizer__FreeOctreeNode
    |
    +-> DXPalletizer__BuildPalette
    +-> DXPalletizer__FindNearestColor (for each pixel)
    +-> DXPalletizer__SwizzleTexture (optional)
            +-> DXPalletizer__SwizzleBlock
    +-> DXPalletizer__FreeOctreeNode (cleanup)
```

---

## Related Files

- **DXTexture.cpp** - Texture loading, uses palletizer for 8-bit textures
- **tgaloader.cpp** - TGA image loading, may feed into palletizer
- **imageloader.cpp** - Base image loading class

---

## Discovery Method

Found via xref search to debug path string at 0x00651d60:
- 5 xrefs from 2 functions
- FUN_0054e500: 1 xref (InsertColor)
- FUN_0054e9d0: 4 xrefs (Palletize - multiple allocations)

Helper functions discovered by analyzing call targets within the main functions.

---

## Status

- [x] All 9 functions identified
- [x] All functions renamed in Ghidra
- [x] Data structures documented
- [x] Algorithm analysis complete
- [ ] Swizzle table values not fully decoded

Last updated: 2025-12-16
