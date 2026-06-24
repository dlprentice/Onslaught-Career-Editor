# PolyBucket.cpp Functions

**Source file:** `C:\dev\ONSLAUGHT2\PolyBucket.cpp`

**Debug path string:** `0x006316bc`

> **Queue status (2026-05-26):** Ghidra export-contract closure **6113/6113** (Wave900: every function commented; clean-signature proxy; not evidence-grade semantics). Lines below that reference a "next raw commentless" row are **archival wave progress**, not open work.

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

## Functions (18 tracked entries)

| Address | Name | Purpose |
|---------|------|---------|
| 0x004d39d0 | CPolyBucket__InitFields | Wave455 owner/name correction; initializes CPolyBucket-style fields and seeds scale field `+0x50` to `1.0` |
| 0x004d3a00 | CPolyBucket__FreeBuffers | Wave455 owner/name correction; frees grid/storage buffers and optional callback-owned object state |
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

## Wave487 Saved Signature/Comment Hardening

Wave487 hardened the full top-of-queue CPolyBucket cluster plus the directly supporting AABB/segment helper. This was a static retail-binary pass only: no function objects were created, no names were changed, and runtime collision/render/debug behavior remains unproven.

| Address | Saved signature | Bounded evidence |
|---------|-----------------|------------------|
| 0x004d3b10 | `int __cdecl CPolyBucket__AABBIntersectsSegment2D(float rect_x, float rect_y, float rect_w, float rect_h, float * seg_p0, float * seg_p1)` | Preserved Wave217 signature; called by `CPolyBucket__AdvanceLineSearch`; rejects or accepts a 2D segment/AABB candidate. |
| 0x004d3ce0 | `int __thiscall CPolyBucket__TriangleInBucket(void * this, float * triangle_vertices, int bucket_x, int bucket_y)` | Tests triangle overlap against a bucket cell from `CPolyBucket__Build`. |
| 0x004d40d0 | `int __thiscall CPolyBucket__Build(void * this, void * mesh_part)` | Builds grid, triangle records, compressed vertex store, height masks, and per-cell triangle lists from mesh-part/static-shadow callers. |
| 0x004d4aa0 | `void __thiscall CPolyBucket__VertexToCompressed(void * this, float * world_vertex, float * bucket_context)` | Helper-shaped saved `this`/ECX is the output compressed vertex; exact typed receiver is documented in the comment rather than forced into the signature. |
| 0x004d4b30 | `void __thiscall CPolyBucket__CompressedToVertex(void * this, float * out_world_vertex, float * bucket_context)` | Helper-shaped saved `this`/ECX is the compressed vertex pointer; expands three signed-short coordinates into world space. |
| 0x004d4b90 | `void __thiscall CPolyBucket__NormalizeVector(void * this, float * out_vec3, float scale)` | Helper-shaped saved `this`/ECX is the input vec3; divides by the supplied scale. |
| 0x004d4bc0 | `int __thiscall CPolyBucket__VertexEquals(void * this, float * vec_b)` | Helper-shaped saved `this`/ECX is the first vec3; exact xyz equality test for vertex deduplication. |
| 0x004d4c00 | `void * __thiscall CPolyBucket__StartSearch(void * this, float * position, float radius)` | Seeds point/radius query state and returns the first matching triangle record through `CPolyBucket__GetNextTriangle`. |
| 0x004d4f00 | `void * __fastcall CPolyBucket__GetNextTriangle(void * this)` | Iterates point-search cell lists, generation filters, and height masks; returns a triangle record pointer or `0`. |
| 0x004d50d0 | `void * __thiscall CPolyBucket__StartLineSearch(void * this, float * start, float * end)` | Clips and seeds segment query state, including global line stepping state, then returns the first line-search triangle record. |
| 0x004d5650 | `int __fastcall CPolyBucket__AdvanceLineSearch(void * this)` | Advances line-search cells and uses the AABB/segment helper for diagonal-cell decisions. |
| 0x004d57c0 | `void * __thiscall CPolyBucket__GetNextLineTriangle(void * this, int stop_after_current_cell)` | Iterates line-search triangle lists and advances cells unless the stop flag halts iteration. |
| 0x004d5930 | `int __thiscall CPolyBucket__GetRandomTriangle(void * this, int * out_vertex_triplet)` | Samples random nonempty bucket cells and returns three compressed-vertex pointers through the output triplet. |
| 0x004d59f0 | `void * __cdecl CPolyBucket__Load(int * chunk_reader)` | Deserializes the 0xB8 object, grid cells, triangle records, callback/owner arrays, and 6-byte compressed vertices. |
| 0x004d5e30 | `void __fastcall CPolyBucket__DebugRender(void * this)` | Debug-renders bucket triangles through decompression and render-state setup using `meshtex_default.tga`. |
| 0x004d61b0 | `int __thiscall CPolyBucket__AddVertex(void * this, void * compressed_vertex)` | Helper-shaped saved `this`/ECX is the vertex-store record; appends one 6-byte compressed vertex and returns its index. |
| 0x004d6210 | `void __thiscall CPolyBucket__ResizeVertexBuffer(void * this, int new_capacity)` | Helper-shaped saved `this`/ECX is the vertex-store record; reallocates backing storage for `new_capacity * 6` bytes. |

Read-back evidence:

- `ApplyPolyBucketWave487.java` final apply: `updated=17 skipped=0 created=0 would_create=0 renamed=0 would_rename=0 missing=0 bad=0`.
- Post exports: `17` metadata rows, `17` tag rows, `27` xref rows, `3757` instruction rows, and `17` decompile files.
- Focused probe: `tools/ghidra_polybucket_wave487_probe.py --check` reported `PASS`.
- Queue refresh: `6057` functions, `2189` commented, `3868` commentless, `1685` undefined signatures, and `1541` `param_N` signatures.

Wave607 follow-up:

- `0x005491b0` is now corrected to `CDXMemoryManager__ReAlloc`, not CPolyBucket-owned. The CPolyBucket and FlexArray rows are caller evidence for the global realloc helper, not ownership evidence for this address.
- Concrete layouts, exact source-body identity, runtime collision/render/debug behavior, BEA launch, patching, and rebuild parity are not proven by Wave487 or by the later allocator correction.

## Wave455 Owner Corrections

Wave455 corrected two older InfluenceMap-labeled entries into CPolyBucket context using caller evidence from `CMeshPart__CreatePolyBucket`, `CMesh__Deserialize`, `CMeshPart__FreeOwnedResourcePointers_004ae640`, and `CStaticShadows` paths. This pass saved names/signatures/comments/tags only; concrete field names, complete CPolyBucket layout, and runtime render/collision behavior remain deferred.

| Address | Current saved state | Notes |
|---------|---------------------|-------|
| 0x004d39d0 | `void __fastcall CPolyBucket__InitFields(void * this)` | Clears fields around `+0x40/+0x60/+0x78/+0x98/+0x9c` and initializes `+0x50` to `1.0`; called by mesh-part creation and static-shadow build paths. |
| 0x004d3a00 | `void __fastcall CPolyBucket__FreeBuffers(void * this)` | Frees the `+0x60` grid, optional `+0x80/+0x84` arrays, `+0x64` storage, and `+0x98` callback/free path; called by mesh, mesh-part, and static-shadow cleanup/build paths. |

## Wave764 PolyBucket.cpp Unwind Continuation

Wave764 static read-back (`unwind-continuation-wave764`, `wave764-readback-verified`) saved comments/tags/signatures for PolyBucket.cpp-adjacent compiler-generated SEH unwind cleanup callbacks at `0x005d4800 Unwind@005d4800`, `0x005d4840 Unwind@005d4840`, and `0x005d4859 Unwind@005d4859` as `void __cdecl Unwind@...(void)` rows. Evidence includes PolyBucket.cpp debug path `0x006316bc`, DATA scope-table xrefs `0x0061d074`, `0x0061d0a4`, and `0x0061d0ac`, and `OID__FreeObject_Callback` calls with line/allocation tokens `0x14c/0x46`, `0x499/0x46`, and `0x4da/0x46`. The adjacent `0x005d481c Unwind@005d481c` row uses array.h debug path `0x0062d590`. Verified backup: `G:\GhidraBackups\BEA_20260523-152957_post_wave764_unwind_continuation_verified`. This is saved static retail Ghidra evidence only; exact parent source-body identity, runtime polybucket cleanup behavior, runtime exception behavior, BEA patching, and rebuild parity remain deferred.

## Function Details

### CPolyBucket__Build (0x004d40d0)

**Current saved signature:** `int __thiscall CPolyBucket__Build(void * this, void * mesh_part)`

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

**Current saved signature:** `void * __cdecl CPolyBucket__Load(int * chunk_reader)`

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

**Current saved signature:** `void * __thiscall CPolyBucket__StartSearch(void * this, float * position, float radius)`

Initiates a spatial query for triangles near a point:
1. Transforms position to bucket-local coordinates
2. Calculates height bitmask from Z +/- radius
3. Determines bucket cell range to search
4. Sets up iteration state for GetNextTriangle

### CPolyBucket__StartLineSearch (0x004d50d0)

**Current saved signature:** `void * __thiscall CPolyBucket__StartLineSearch(void * this, float * start, float * end)`

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

**Current saved signature:** `int __thiscall CPolyBucket__GetRandomTriangle(void * this, int * out_vertex_triplet)`

Returns pointers to 3 vertices of a random triangle:
1. Tries up to 1000 random bucket lookups
2. Uses `Random__NextLCGAbs` (0x004de8d0 random number generator)
3. Outputs vertex pointers to caller's array
4. Returns 1 on success, 0 if no triangles found

Used for: effect spawning, particle placement, random sampling

### CPolyBucket__DebugRender (0x004d5e30)

**Current saved signature:** `void __fastcall CPolyBucket__DebugRender(void * this)`

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
