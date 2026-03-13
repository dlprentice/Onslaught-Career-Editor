# StaticShadows.cpp Functions

> Source File: StaticShadows.cpp | Binary: BEA.exe
> Debug Path: 0x006329f8 (`C:\dev\ONSLAUGHT2\StaticShadows.cpp`)

## Overview

CStaticShadows handles pre-computed shadow rendering for static objects (buildings, terrain features) in the game world. The system uses a grid-based shadow map approach where each cell contains a bitmap representing shadow coverage. Shadows are computed by ray-tracing from light sources through scene geometry.

## Functions

| Address | Name | Purpose | Size |
|---------|------|---------|------|
| 0x004ec2f0 | CStaticShadows__BuildShadowMaps | Main shadow map generation - iterates objects, builds 64x64 shadow grids | ~7680 bytes |
| 0x004ee0f0 | CStaticShadows__ApplyShadowsToGrid | Applies individual shadow maps to global shadow grid | ~512 bytes |
| 0x004ee8f0 | CStaticShadows__Load | Loads/deserializes shadow data from save file | ~720 bytes |
| 0x004ee8a0 | CStaticShadows__LoadAll | Loads multiple shadow objects, calls Load() in loop | ~80 bytes |
| 0x004ebc00 | CStaticShadows__Reattach | Rebinds shadow entries to live things by stored IDs and refreshes visibility | ~352 bytes |
| 0x004ebd10 | CStaticShadows__ClearAllShadowEntries | Drains linked shadow-entry list and frees cached tile shadow grids | ~352 bytes |
| 0x004ebe40 | CStaticShadows__UpdateLightVectorAndRebuild | Normalizes light vector and rebuilds static shadow maps for eligible objects | ~624 bytes |
| 0x004ec250 | CStaticShadows__DestroyShadowMapNode | Frees one shadow-map node and owned bitmap allocations (deleting-dtor path) | ~208 bytes |
| 0x004ebfb0 | CStaticShadows__UpdateVisibility | Updates shadow visibility when objects change state | ~384 bytes |
| 0x004ebdf0 | CStaticShadows__Destructor | Frees shadow map memory allocations | ~96 bytes |
| 0x004ee0d0 | CStaticShadows__CleanupHelper | Helper for cleanup operations | ~32 bytes |
| 0x004ee410 | CStaticShadows__RayTriangleIntersect | Ray-triangle intersection test for shadow casting | ~448 bytes |

## Key Observations

### Shadow Grid System
- Uses a 64x64 grid system (0x40 cells per axis)
- Each grid cell contains a 512-byte (0x200) shadow bitmap
- Grid bounds clamped to 0-63 range (0x3f max)
- Shadow data stored at global address `DAT_009c8028`

### Shadow Map Structure (0x1c bytes per entry)
```
+0x00: int minX          - Grid X start
+0x04: int minY          - Grid Y start
+0x08: int width         - Grid width
+0x0C: int height        - Grid height
+0x10: int* shadowData   - Pointer to shadow bitmap array
+0x14: int isActive      - Shadow enabled flag
+0x18: int isVisible     - Visibility state
```

### BuildShadowMaps Algorithm
1. Iterates through all static objects in scene
2. For each object with shadow type 1 or 6:
   - Computes 8 bounding box corners in world space
   - Projects corners to shadow grid coordinates
   - Allocates shadow bitmap for grid region
   - Ray-traces from light direction through geometry
   - Sets shadow bits where rays intersect triangles

### Ray-Triangle Intersection
- Uses standard Moller-Trumbore algorithm
- Computes plane normal from triangle vertices
- Tests ray against triangle plane
- Uses angle sum test (2*PI) for point-in-triangle

### Debug Output
- "Building shadow map for %d, %d, %d" at 0x00632a30
- "Thing at 0x%x has no RTMesh when..." at 0x00632a58
- "Warning - unattached static shadow..." path used by `CStaticShadows__Reattach`

### Memory Management
- Uses OID__AllocObject for allocation (custom allocator)
- Uses OID__FreeObject for deallocation
- Shadow linked list head at DAT_009c8010

### Additional Lifecycle Helpers (Wave51)
- `CStaticShadows__ClearAllShadowEntries` (`0x004ebd10`)
  - Walks the linked entry list, updates visibility state, frees entry-owned nodes, and clears 64x64 cached shadow cells.
- `CStaticShadows__UpdateLightVectorAndRebuild` (`0x004ebe40`)
  - Refreshes light vector from globals, normalizes it, then enumerates eligible world objects and rebuilds maps.
- `CStaticShadows__DestroyShadowMapNode` (`0x004ec250`)
  - Releases per-node bitmap arrays and supports deleting-dtor flag behavior.

### Related Systems
- RTMesh (runtime mesh) at object+0x30
- Scene graph traversal via virtual calls
- Coordinate transformation matrices

---
*Discovered via Phase 1 xref analysis (Dec 2025)*
