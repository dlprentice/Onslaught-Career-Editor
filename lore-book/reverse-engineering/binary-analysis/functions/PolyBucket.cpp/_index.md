# PolyBucket.cpp Functions

**Source file:** `C:\dev\ONSLAUGHT2\PolyBucket.cpp`

**Debug path string:** `0x006316bc`

## Overview

CPolyBucket is a spatial partitioning system for polygon rendering optimization. It divides 3D space into a 2D grid of "buckets" to enable efficient spatial queries for collision detection and rendering. Triangles are sorted into buckets based on their XY position, with height (Z) stored as a bitmask for vertical filtering.

## Class Structure

The CPolyBucket class (size 0xB8 bytes) contains:
- Bounding box and origin offset (offsets 0x30-0x4C)
- Maximum radius/scale (offset 0x50)
- 2D bucket grid pointer (offset 0x60) - array of bucket pointers
- Grid dimensions: width (0x68), height (0x6C)
- Cell size (0x70) - bucket size in world units
- Height scale (0x74) - for Z-axis bitmask calculation
- Triangle data array (offset 0x64) - 12-byte triangle records
- Vertex array (offset 0x98) - compressed 6-byte vertices
- Search state (offsets 0x88-0xB4) - iteration variables

## Vertex Compression

Vertices are stored in compressed 6-byte format (3 x int16):
- Each coordinate = `(worldPos - origin) / scale * 32767.0`
- Decompression: `origin + (compressed * scale * 3.051851e-05)`
- The constant `3.051851e-05` is approximately `1/32767`

## Height Bitmask

Triangles store a 32-bit bitmask indicating which Z-layers they occupy:
- Each bit represents a vertical slice
- Enables fast rejection of triangles outside query height range
- Calculated from triangle min/max Z divided by height scale

## Functions (16 total)

| Address | Name | Purpose |
|---------|------|---------|
| 0x004d40d0 | CPolyBucket__Build | Build bucket structure from mesh triangles |
| 0x004d59f0 | CPolyBucket__Load | Load/deserialize bucket from file stream |
| 0x004d3ce0 | CPolyBucket__TriangleInBucket | Test if triangle overlaps a bucket cell |
| 0x004d4aa0 | CPolyBucket__VertexToCompressed | Convert world vertex to compressed int16 format |
| 0x004d4b30 | CPolyBucket__CompressedToVertex | Convert compressed int16 to world vertex |
| 0x004d4b90 | CPolyBucket__NormalizeVector | Divide vector by scale factor |
| 0x004d4bc0 | CPolyBucket__VertexEquals | Compare two vertices for equality |
| 0x004d4c00 | CPolyBucket__StartSearch | Begin point-radius search in buckets |
| 0x004d4f00 | CPolyBucket__GetNextTriangle | Get next triangle from point search |
| 0x004d50d0 | CPolyBucket__StartLineSearch | Begin line segment search (Bresenham-style) |
| 0x004d5650 | CPolyBucket__AdvanceLineSearch | Step to next cell along line |
| 0x004d57c0 | CPolyBucket__GetNextLineTriangle | Get next triangle from line search |
| 0x004d5930 | CPolyBucket__GetRandomTriangle | Get random triangle (for effects/spawning) |
| 0x004d5e30 | CPolyBucket__DebugRender | Debug visualization - render all triangles |
| 0x004d61b0 | CPolyBucket__AddVertex | Add vertex to vertex array (with resize) |
| 0x004d6210 | CPolyBucket__ResizeVertexBuffer | Reallocate vertex buffer |

## Function Details

### CPolyBucket__Build (0x004d40d0)

**Signature:** `int CPolyBucket::Build(CMesh* mesh)`

Main construction function that processes mesh triangles:
1. Allocates bucket grid based on mesh bounding box
2. Iterates all mesh triangles
3. Compresses vertices and checks for degenerates
4. Calculates height bitmask for each triangle
5. Places triangle indices into overlapping bucket cells
6. Warns if triangle doesn't fit in any bucket

**Key behaviors:**
- Uses `OID__AllocObject` for memory allocation
- Calls `CConsole__Printf` (`FUN_00441740`) to log warning for unplaced triangles
- Returns 1 on success, 0 on failure

### CPolyBucket__Load (0x004d59f0)

**Signature:** `CPolyBucket* CPolyBucket::Load(int* sizePtr)`

Deserializes a CPolyBucket from file:
1. Allocates 0xB8 byte structure
2. Reads bucket grid dimensions and data
3. Reads triangle records (12 bytes each)
4. Reads compressed vertex array (6 bytes each)
5. Reconstructs bucket cell pointers

**File format:**
- Header with grid dimensions
- Per-cell: flag (1=has data), triangle count, triangle indices
- Triangle array: 3 vertex indices + height bitmask
- Vertex array: compressed xyz coordinates

### CPolyBucket__StartSearch (0x004d4c00)

**Signature:** `int CPolyBucket::StartSearch(float* position, float radius)`

Initiates a spatial query for triangles near a point:
1. Transforms position to bucket-local coordinates
2. Calculates height bitmask from Z +/- radius
3. Determines bucket cell range to search
4. Sets up iteration state for GetNextTriangle

### CPolyBucket__StartLineSearch (0x004d50d0)

**Signature:** `int CPolyBucket::StartLineSearch(float* start, float* end)`

Initiates a ray/line segment query:
1. Transforms endpoints to bucket coordinates
2. Calculates Bresenham-style stepping parameters
3. Determines height bitmask for line segment
4. Validates line intersects bucket bounds

Uses global variables for line stepping:
- `DAT_006316b4` - X step direction
- `DAT_006316b8` - Y step direction
- `DAT_0082b688/8c` - current position
- `DAT_0082b690` - step count

### CPolyBucket__GetRandomTriangle (0x004d5930)

**Signature:** `int CPolyBucket::GetRandomTriangle(int* vertexPtrs)`

Returns pointers to 3 vertices of a random triangle:
1. Tries up to 1000 random bucket lookups
2. Uses `Random__NextLCGAbs` (0x004de8d0 random number generator)
3. Outputs vertex pointers to caller's array
4. Returns 1 on success, 0 if no triangles found

Used for: effect spawning, particle placement, random sampling

### CPolyBucket__DebugRender (0x004d5e30)

**Signature:** `void CPolyBucket::DebugRender()`

Debug visualization that renders all bucket triangles:
1. Sets up render states (depth, blend)
2. Loads default debug texture (`meshtex_default.tga`)
3. Iterates all bucket cells
4. Decompresses and renders each triangle
5. Controlled by `cg_drawpolybuckets` console variable

## Related Strings

| Address | String |
|---------|--------|
| 0x006316bc | `C:\dev\ONSLAUGHT2\PolyBucket.cpp` |
| 0x006316e0 | `Warning: Triangle wasn't placed in polybucket (part_num %d)` |
| 0x0063171c | `WARNING: search in invalid poly bucket` |
| 0x0063174c | `WARNING: diff outside poly bucket` |
| 0x00628b60 | `cg_drawpolybuckets` |
| 0x00628b74 | `Should polybucket volumes be rendered` |

## Global Variables

| Address | Purpose |
|---------|---------|
| 0x0082b688 | Line search current X position (float) |
| 0x0082b68c | Line search current Y position (float) |
| 0x0082b690 | Line search remaining steps (int) |
| 0x0082b694 | Line search diagonal flag (int) |
| 0x0082b698 | Line search step counter (int) |
| 0x0082b69c | Current triangle index in bucket iteration |
| 0x006316b4 | Line search X step direction (float) |
| 0x006316b8 | Line search Y step direction (float) |
| 0x0089ce84 | Debug render texture handle |

## Usage Pattern

```cpp
// Typical collision query:
CPolyBucket* bucket = terrain->GetPolyBucket();
if (bucket->StartSearch(&position, radius)) {
    int* tri;
    while ((tri = bucket->GetNextTriangle()) != NULL) {
        // Test collision with triangle vertices
        // tri points to 12-byte record with vertex indices
    }
}

// Ray cast query:
if (bucket->StartLineSearch(&start, &end)) {
    int* tri;
    while ((tri = bucket->GetNextLineTriangle(0)) != NULL) {
        // Test ray intersection with triangle
    }
}
```

## Notes

- The poly bucket system is used for terrain collision detection
- Console variable `cg_drawpolybuckets` enables debug visualization
- The 32-bit height bitmask limits vertical resolution to 32 slices
- Bucket cell size affects query performance vs memory tradeoff
