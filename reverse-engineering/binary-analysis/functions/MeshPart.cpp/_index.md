# MeshPart.cpp Functions

> Source File: MeshPart.cpp | Binary: BEA.exe
> Debug Path: 0x0062fe70 (`C:\dev\ONSLAUGHT2\MeshPart.cpp`)

## Overview

CMeshPart represents a sub-component of a 3D mesh in the Battle Engine Aquila rendering system. Each mesh part contains geometry data (vertices, triangles) for a specific material or region, along with bone weights for skeletal animation support.

## Functions

| Address | Name | Purpose | Size |
|---------|------|---------|------|
| 0x004adff0 | CMeshPart__SetVertexCount | Allocates vertex arrays (positions, UVs, colors, normals) | ~176 bytes |
| 0x004ae2b0 | CMeshPart__CreatePolyBucket | Creates polygon bucket for rendering optimization | ~256 bytes |
| 0x004ae4b0 | CMeshPart__Init | Initializes mesh part with default values and matrices | ~400 bytes |
| 0x004ae860 | CMeshPart__AllocateGeometry | Allocates DVertices, PVertices, and Triangles arrays | ~480 bytes |
| 0x004af470 | CMeshPart__LoadVerticesAndTriangles | Loads vertex/triangle data from file stream | ~1856 bytes |
| 0x004afbb0 | CMeshPart__LoadVerticesWithBones | Loads vertices with bone weights for skinned meshes | ~2720 bytes |
| 0x004b1a40 | CMeshPart__CacheFrameData | Caches position and orientation data per frame | ~464 bytes |
| 0x004b27a0 | CMeshPart__LoadFromStream | Main deserialization - loads entire mesh part from stream | ~2560 bytes |
| 0x004b3180 | CMeshPart__LoadMaterial | Loads material/shader data (40 bytes struct) | ~112 bytes |
| 0x004b31f0 | CMeshPart__OptimizePolygons | Removes redundant vertices and degenerate triangles | ~2400 bytes |
| 0x004b3b70 | CMeshPart__Clone | Deep copies mesh part including all geometry data | ~1760 bytes |
| 0x004b4250 | CMeshPart__Merge | Merges another mesh part into this one | ~768 bytes |
| 0x00495030 | CMeshPart__PassesBuggyCoreStateForStrictOptimize | Buggy-specific optimize gate used by strict mesh-part optimize checks | ~96 bytes |
| 0x00495090 | CMeshPart__PassesBuggyCoreStateForMergeOptimize | Buggy-specific optimize gate used by merge optimize checks | ~96 bytes |

## Recent Headless Semantic Promotions (2026-02-26)

| Address | Symbol | Description |
|---------|--------|-------------|
| `0x004ae110` | `CMeshPart__StartTriangleBucketSearch` | Starts triangle polybucket search and maps local triangle indices to mesh triangle pointers |
| `0x004ae1a0` | `CMeshPart__GetNextTriangleFromBucketSearch` | Advances active triangle search and maps next local indices to mesh triangle pointers |
| `0x004ae220` | `CMeshPart__StartLineTriangleBucketSearch` | Starts line-triangle polybucket search and maps first local indices to mesh triangle pointers |
| `0x004ae430` | `CMeshPart__GetNextLineTriangleFromBucketSearch` | Advances line-triangle search and maps next local indices to mesh triangle pointers |
| `0x004ae640` | `CMeshPart__FreeOwnedResourcePointers_004ae640` | Bulk frees OID-owned resource pointers/arrays including influence-map runtime buffers |

## CMeshPart Structure (Size: 0x13C = 316 bytes)

Key offsets discovered from decompilation:

| Offset | Type | Field | Notes |
|--------|------|-------|-------|
| 0x00-0x2F | float[12] | Transform matrix | 4x3 matrix copied from global data |
| 0x30-0x5F | float[12] | Additional matrix | Copied during clone |
| 0x70-0x7F | float[4] | Bounding data | Copied during clone |
| 0x80 | int* | mTriangles | Triangle index array (12 bytes per tri) |
| 0x84 | int** | mPVertices | Per-frame vertex positions array |
| 0x88 | int | mPartIndex | Part identifier |
| 0x8c | int | mMeshType | 1=static, 3=skinned (triggers bone loading) |
| 0x90 | int | mNumMaterials | Count of material references |
| 0x94 | int* | mMaterials | Material pointer array |
| 0x98 | int* | mNextPart | Linked list - next part |
| 0x9c | int* | mPrevPart | Linked list - previous part |
| 0xa4 | int | Unknown | Copied during clone |
| 0xa8 | int | mNumDVertices | Dynamic vertex count |
| 0xac | int | mNumPVertices | Per-frame vertex count |
| 0xb0 | int | mNumTriangles | Triangle count |
| 0xb4 | int | mNumFrames | Animation frame count |
| 0xb8 | int | mNumTexCoords | Texture coordinate count |
| 0xbc | int | mNumKeyframes | Keyframe count for animation |
| 0xc0 | int | mNumBones | Bone count (skinned meshes only) |
| 0xc4 | byte* | mTexCoordData | Texture coordinate array |
| 0xc8 | float* | mPositionData | Position keyframe data |
| 0xcc | int* | mFOVData | Field-of-view keyframe data |
| 0xd0 | int* | mBoneIndices | Bone index mapping |
| 0xd4 | float** | mBoneWeights | Per-vertex bone weights |
| 0xd8 | int** | mBoneSlots | Bone slot assignments (3 per vertex) |
| 0xdc | char[60] | mName | Part name string (debug) |
| 0xfc | void* | mMaterial | Material structure pointer (40 bytes) |
| 0x100 | void* | mPolyBucket | Polygon bucket for rendering |
| 0x104 | float* | mPositionCache | Cached positions per frame |
| 0x108 | float* | mOrientationCache | Cached orientations per frame (0x30 bytes each) |
| 0x10c | void* | mKeyframeMatrix | Keyframe transformation matrices |
| 0x118 | int | mCachedFrameCount | Number of cached frames |
| 0x11c | int | mHasZeroPosition | Optimization flag |
| 0x120 | int | mHasIdentityMatrix | Optimization flag |
| 0x124 | int* | mSomePointer | Unknown reference |
| 0x128 | int* | mParentMesh | Pointer to parent CMesh |
| 0x12c | int | Unknown | |
| 0x130 | int | mFlags | Various flags |
| 0x134 | void* | mDVertices | Dynamic vertex array (0x60 bytes each) |
| 0x138 | int | mSomeValue | Preserved during load |

## Vertex Structures

### DVertex (Dynamic Vertex) - 0x60 bytes (96 bytes)
| Offset | Type | Field |
|--------|------|-------|
| 0x00-0x0F | float[4] | Position (x, y, z, w) |
| 0x20 | float | Normal X |
| 0x24 | float | Normal Y |
| 0x28 | float | Normal Z (negated on load) |
| 0x2c | uint | Color (ARGB, byte-swapped) |
| 0x30-0x47 | int[6] | Material/texture references (-1 = none) |

### PVertex (Per-frame Vertex) - 0x10 bytes (16 bytes)
| Offset | Type | Field |
|--------|------|-------|
| 0x00 | float | X position |
| 0x04 | float | Y position |
| 0x08 | float | Z position |
| 0x0c | float | W (usually 1.0) |

### Triangle - 0x0C bytes (12 bytes)
| Offset | Type | Field |
|--------|------|-------|
| 0x00 | int* | Vertex 0 pointer (into DVertices) |
| 0x04 | int* | Vertex 1 pointer |
| 0x08 | int* | Vertex 2 pointer |

## Key Observations

### Memory Allocation
- Uses custom allocator at `OID__AllocObject(size, type, filename, line)` for tracking
- Type 1 = general allocation, Type 0x24/0x46/0x74 = specific pools

### Coordinate System
- Z-coordinate is negated during load (`-z`) - indicates right-hand to left-hand conversion
- Color bytes are swapped (BGRA to ARGB conversion)

### Mesh Types
- Type 1: Static mesh (simple vertex loading)
- Type 3: Skinned mesh (includes bone weights and indices)

### Polygon Optimization
- `OptimizePolygons` removes vertices with similar normals (threshold 0.2-0.3)
- Removes degenerate triangles (where two vertices share the same index)
- Reports "Part %s removed %d of %d verts" and "Removed %d of %d polys"

### String References Found
- `"boss_fenrir.msh"` - Used in CreatePolyBucket for testing
- `"tempbuilding3.msh"` - Secondary test mesh
- `"Ignoring mesh '%s' for poly bucket"` - Debug message
- `"Merging %s into %s"` - Merge operation debug
- `"Got %d bones"` - Bone loading debug
- `"Meshes/%s/Part/%d/DVertices"` - Memory tracking label
- `"Meshes/%s/Part/%d/PVertices"` - Memory tracking label
- `"Meshes/%s/Part/%d/Triangles"` - Memory tracking label
- `"CORE"` / `"x1"` - Buggy optimize-state tags used by strict/merge gate helpers (`0x00495030` / `0x00495090`)

### Bone Weight System
- Up to 3 bones can influence each vertex (stored in mBoneSlots)
- Weights are normalized to sum to 1.0
- Uses 1/3 subtraction trick to find top 3 contributing bones

---
*Discovered via Phase 1 xref analysis (Dec 2025)*
