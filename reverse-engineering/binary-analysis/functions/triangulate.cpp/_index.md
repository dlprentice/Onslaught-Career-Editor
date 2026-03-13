# triangulate.cpp - Mesh Triangulation

**Source file:** `C:\dev\ONSLAUGHT2\triangulate.cpp`
**Debug string address:** `0x00633ab8`

## Overview

This source file contains functions for triangulating rectangular regions into triangle meshes. Used for rendering quad surfaces that need to be converted to triangles for the GPU.

## Functions (1 found)

| Address | Name | Purpose |
|---------|------|---------|
| `0x004f7170` | `Triangulate__CreateQuadMesh` | Creates triangulated quad mesh from bounds |

## Function Details

### Triangulate__CreateQuadMesh (0x004f7170)

**Signature:** `void __thiscall CreateQuadMesh(void* this, int maxVerts, float minX, float minY, float maxX, float maxY, int subdivisionMode)`

**Purpose:** Allocates and initializes a triangulated quad mesh from rectangular bounds. Supports two modes:
- Mode 0: Simple quad (4 vertices, 2 triangles)
- Mode 1: Subdivided quad (8 vertices, 6 triangles with edge midpoints)

**Parameters:**
- `this` (ECX): Pointer to mesh structure to initialize
- `maxVerts`: Maximum vertex count for allocation
- `minX, minY`: Bottom-left corner coordinates
- `maxX, maxY`: Top-right corner coordinates
- `subdivisionMode`: 0 = simple quad, 1 = subdivided quad

**Mesh Structure Layout:**
```c
struct TriangulatedMesh {
    float* vertices;      // [0] - Pointer to vertex array (x,y pairs)
    uint16_t* indices;    // [4] - Pointer to triangle index array
    int vertexCount;      // [8] - Number of vertices
    int triangleCount;    // [12] - Number of triangles
    int maxVertices;      // [16] - Allocated capacity
};
```

**Mode 0 - Simple Quad (2 triangles):**
```
Vertices (4):
  0: (minX, minY)  - bottom-left
  1: (maxX, minY)  - bottom-right
  2: (minX, maxY)  - top-left
  3: (maxX, maxY)  - top-right

Triangles (2):
  [0, 1, 2]  - lower-left triangle
  [1, 3, 2]  - upper-right triangle
```

**Mode 1 - Subdivided Quad (6 triangles):**
```
Vertices (8):
  0: (minX, minY)           - bottom-left corner
  1: (midX, minY)           - bottom edge midpoint
  2: (minX, midY)           - left edge midpoint
  3: (midX, midY)           - center (computed)
  4: (maxX, minY)           - bottom-right corner
  5: (maxX, midY)           - right edge midpoint
  6: (minX, maxY)           - top-left corner
  7: (maxX, maxY)           - top-right corner

Triangles (6):
  [0, 1, 3], [1, 5, 3], [1, 6, 5],
  [1, 7, 6], [1, 4, 7], [1, 2, 4]
```

**Memory Allocation:**
- Calls `OID__AllocObject` (memory allocator) with alignment 0x80 (128 bytes)
- Vertex buffer: `maxVerts * 8` bytes (2 floats per vertex)
- Index buffer: `maxVerts * 12` bytes (6 uint16 indices per triangle pair)

**Calling Convention:** `__thiscall` (mesh pointer in ECX)

## Cross-References

The debug path string at `0x00633ab8` is referenced twice within `CreateQuadMesh`:
1. At `0x004f717a` - Vertex buffer allocation (line 6)
2. At `0x004f71aa` - Index buffer allocation (line 7)

## Technical Notes

1. **Subdivision Mode 1** computes edge midpoints using linear interpolation: `mid = (a + b) * 0.5`

2. The triangle indices are stored as `uint16_t` (2 bytes each), allowing up to 65535 vertices per mesh.

3. The allocator function `OID__AllocObject` appears to be a debug memory allocator that records source file and line number for leak tracking.

## Related Files

- Likely called by terrain/water rendering code
- May be used for UI quad rendering with texture subdivision
