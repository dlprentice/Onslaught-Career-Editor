# landscapeib.cpp Functions

> Source File: landscapeib.cpp | Binary: BEA.exe
> Debug Path: 0x0062d824

## Overview
Landscape index buffer system for terrain rendering grid. CLandscapeIB manages DirectX index buffers used to render the terrain mesh as triangulated grids. The system supports edge stitching via bitmask flags to handle LOD transitions between adjacent terrain patches.

## Functions
| Address | Name | Purpose | Size |
|---------|------|---------|------|
| 0x0048df20 | CLandscapeIB__CreateIndexBuffer | Creates/populates index buffer for landscape mesh | ~0x1F0 |

## Function Details

### CLandscapeIB__CreateIndexBuffer (0x0048df20)

**Signature:** `void __thiscall CLandscapeIB::CreateIndexBuffer(void)`

**Description:**
Generates triangle indices for a grid-based landscape mesh and creates a DirectX index buffer resource. Handles edge case adjustments for LOD stitching.

**Algorithm:**
1. Allocates temporary buffer: `gridSize * gridSize * 12` bytes (6 shorts per cell)
2. Generates two triangles per grid cell using the pattern:
   - Triangle 1: (v, v+stride, v+stride+1)
   - Triangle 2: (v+stride+1, v, v+1)
3. Applies edge modifications based on flags at offset 0x28:
   - Bit 0 (0x1): Modifies first edge triangles
   - Bit 1 (0x2): Modifies second edge triangles
   - Bit 2 (0x4): Modifies third edge triangles
   - Bit 3 (0x8): Modifies fourth edge triangles
4. Compacts buffer by removing degenerate (all-zero) triangles
5. Creates DirectX index buffer via D3D resource creation
6. Copies index data to GPU buffer

**Global Cache:**
- `DAT_009c64e0` - If non-zero, uses cached index data instead of regenerating
- `DAT_009c64e4` - Base pointer to cached index data
- `DAT_009c64e8` / `DAT_009c64ec` - Index range lookup tables

**Called Functions:**
- `OID__AllocObject` - Memory allocation (receives debug path + line number)
- `FUN_0056eb60/70/80/50/90` - D3D setup functions
- `FUN_005137d0` - D3D index buffer creation
- `OID__FreeObject` - Memory deallocation
- `FUN_004883f0` - Buffer unlock

## Class Layout (CLandscapeIB)

| Offset | Type | Member | Notes |
|--------|------|--------|-------|
| 0x00 | void** | vtable | Virtual function table |
| 0x08 | IDirect3DIndexBuffer* | m_pIndexBuffer | D3D index buffer resource |
| 0x18 | int | m_bDirty | Rebuild needed flag |
| 0x24 | int | m_nLODLevel | Level of detail index |
| 0x28 | uint | m_nEdgeFlags | Bitmask for edge stitching |
| 0x2C | int | m_nGridSize | Grid dimension (NxN) |
| 0x30 | int | m_nIndexCount | Number of indices in buffer |

## Related Functions (Not in this source file)

These functions appear to be CLandscapeIB methods but lack debug path references:

| Address | Likely Name | Purpose |
|---------|-------------|---------|
| 0x0048e310 | CLandscapeIB__ReleaseBuffer | Releases index buffer resource |
| 0x0048e360 | CLandscapeIB__SetParameters | Sets LOD level and edge flags, triggers rebuild |

## Key Observations

- **Single function per source file**: Only one function has the debug path reference, suggesting a small utility class
- **Edge stitching system**: The 4-bit flag system at offset 0x28 handles terrain LOD transitions (common in terrain engines)
- **Global caching**: Index buffers can be cached globally to avoid regeneration (optimization for static terrain)
- **Grid-based terrain**: Uses standard triangle strip generation pattern for heightfield terrain
- **Memory allocation tracking**: Debug path passed to allocator for leak detection in dev builds
- **Virtual function dispatch**: CreateIndexBuffer is called via vtable (offset 0x04), indicating polymorphic design

---
*Discovered via Phase 1 xref analysis (Dec 2025)*
