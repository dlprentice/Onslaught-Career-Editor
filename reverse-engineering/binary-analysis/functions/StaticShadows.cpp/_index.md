# StaticShadows.cpp Functions

> Source File: StaticShadows.cpp | Binary: BEA.exe
> Debug Path: 0x006329f8 (`[maintainer-local-source-export-root]\StaticShadows.cpp`)

> **Queue status (2026-05-26):** Ghidra export-contract closure **6113/6113** (Wave900: every function commented; clean-signature proxy; not evidence-grade semantics). Lines below that reference a "next raw commentless" row are **archival wave progress**, not open work.

## Overview

CStaticShadows handles pre-computed shadow rendering for static objects (buildings, terrain features) in the game world. The system uses a grid-based shadow map approach where each cell contains a bitmap representing shadow coverage. Shadows are computed by ray-tracing from light sources through scene geometry.

Wave767 static read-back (`unwind-continuation-wave767`, `wave767-readback-verified`) saved comments/tags/signatures for StaticShadows.cpp-adjacent compiler-generated unwind cleanup callbacks from `0x005d4ef0 Unwind@005d4ef0` through `0x005d4f90 Unwind@005d4f90`. Evidence includes StaticShadows.cpp debug path `0x006329f8`, DATA scope-table xrefs `0x0061d7a4` through `0x0061d814`, allocation-free callbacks, and eight `CLine__SetBaseVtable_00426360` stack-local line cleanup rows beginning at `0x005d4f28 Unwind@005d4f28`. Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260523-164622_post_wave767_unwind_continuation_verified`. Exact parent source-body identity, runtime exception behavior, runtime cleanup behavior, BEA patching, and rebuild parity remain deferred.

Wave1009 (`geometry-guide-heightfield-spine-review-wave1009`) re-reviewed `0x0047eb80 CStaticShadows__SampleShadowHeightBilinear` as the central static-shadow height sampler and recovered DATA-backed caller boundaries including `0x00534ac0 ScriptCommand__SampleStaticShadowHeight_00534ac0`. Queue closure is `6233/6233 = 100.00%`; verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260531-155648_post_wave1009_geometry_guide_heightfield_spine_review_verified`. Runtime static-shadow, terrain, or MissionScript behavior, exact source method identity, concrete layouts, BEA patching, and rebuild parity remain separate proof.

## Functions

| Address | Name | Purpose | Size |
|---------|------|---------|------|
| 0x004ec2f0 | CStaticShadows__BuildShadowMaps | Main shadow map generation - iterates objects, builds 64x64 shadow grids | ~7680 bytes |
| 0x004ee0f0 | CStaticShadows__ApplyShadowsToGrid | Applies individual shadow maps to global shadow grid | ~512 bytes |
| 0x004ee8f0 | CStaticShadows__Load | Loads/deserializes one static-shadow entry from a chunk stream | ~720 bytes |
| 0x004ee8a0 | CStaticShadows__LoadAll | Loads multiple shadow objects, calls Load() in loop | ~80 bytes |
| 0x004ebbc0 | CStaticShadows__Initialise | Registers BuildStaticShadows, clears the 64x64 grid, and initializes manager list/tail fields | ~64 bytes |
| 0x004ebc00 | CStaticShadows__Reattach | Rebinds shadow entries to live things by stored IDs and refreshes visibility | ~352 bytes |
| 0x004ebd10 | CStaticShadows__ClearAllShadowEntries | Drains linked shadow-entry list and frees cached tile shadow grids | ~352 bytes |
| 0x004ebe40 | CStaticShadows__UpdateLightVectorAndRebuild | Normalizes light vector and rebuilds static shadow maps for eligible objects | ~624 bytes |
| 0x004ec250 | CStaticShadows__ShadowMapEntryDeletingDestructor | Shadow-map entry scalar/vector deleting destructor wrapper | ~208 bytes |
| 0x004ebfb0 | CStaticShadows__UpdateVisibility | Updates shadow visibility when objects change state | ~384 bytes |
| 0x004ebdf0 | CStaticShadows__ShadowMapEntryDestructor | Per-shadow-map-entry destructor callback for owned bitmap allocations | ~96 bytes |
| 0x004ee0d0 | CPolyBucket__ScalarDeletingDestructor | CPolyBucket scalar-deleting destructor reached during static-shadow build cleanup | ~32 bytes |
| 0x004ee410 | CStaticShadows__RayTriangleIntersect | Ray-triangle intersection test for shadow casting | ~448 bytes |
| 0x0047eb80 | CStaticShadows__SampleShadowHeightBilinear | Wave394 corrected the saved calling convention to `__fastcall` and records the EDX/world-position terrain-height sampler evidence | ~224 bytes |

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
- Computes a plane normal from triangle vertices
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

### Additional Lifecycle Helpers (Wave511)
- `CStaticShadows__Initialise` (`0x004ebbc0`)
  - `CGame::Init` calls this with `ECX=0x009c8010`, matching the source-level `STATICSHADOWS.Initialise()` call; the body registers `BuildStaticShadows`, clears the 64x64 shadow grid, and initializes list/tail fields.
- `CStaticShadows__ClearAllShadowEntries` (`0x004ebd10`)
  - Walks the linked entry list, updates visibility state, frees entry-owned nodes, and clears 64x64 cached shadow cells.
- `CStaticShadows__UpdateLightVectorAndRebuild` (`0x004ebe40`)
  - Refreshes light vector from globals, normalizes it, then enumerates eligible world objects and rebuilds maps.
- `CStaticShadows__ShadowMapEntryDestructor` (`0x004ebdf0`)
  - Corrects the stale manager-destructor label; this is the per-entry destructor callback passed to vector construction/destruction helpers for 0x1c-byte shadow-map entries.
- `CStaticShadows__ShadowMapEntryDeletingDestructor` (`0x004ec250`)
  - Corrects the stale destroy-node label; this is the scalar/vector deleting destructor wrapper for shadow-map entries and supports the observed flag behavior.
- `CPolyBucket__ScalarDeletingDestructor` (`0x004ee0d0`)
  - Corrects the stale static-shadow cleanup-owner label; this wrapper calls `CPolyBucket__FreeBuffers` and optionally frees the bucket.

Wave511 is static retail Ghidra evidence only. It does not prove exact static-shadow, entry, render-mesh, terrain, resource chunk, or CPolyBucket layouts, runtime shadow behavior, BEA launch behavior, patching behavior, or rebuild parity.

### Wave767 StaticShadows.cpp Unwind Continuation

Wave767 hardened eleven StaticShadows.cpp-adjacent unwind callbacks as `void __cdecl Unwind@...(void)` without renames, function-boundary changes, or executable-byte changes.

| Address | Evidence |
| --- | --- |
| 0x005d4ef0 | DATA xref `0x0061d7a4`; `OID__FreeObject_Callback(*(EBP-0x614))` with StaticShadows.cpp line token `0x18a` and allocation/type value `0x70`. |
| 0x005d4f0c | DATA xref `0x0061d7ac`; `OID__FreeObject_Callback(*(EBP-0x684))` with StaticShadows.cpp line token `0x1a7` and allocation/type value `0x61`. |
| 0x005d4f28 | DATA xref `0x0061d7b4`; `CLine__SetBaseVtable_00426360(EBP-0x31c)`. |
| 0x005d4f33 | DATA xref `0x0061d7bc`; `CLine__SetBaseVtable_00426360(EBP-0x24c)`. |
| 0x005d4f3e | DATA xref `0x0061d7c4`; `CLine__SetBaseVtable_00426360(EBP-0x2b4)`. |
| 0x005d4f49 | DATA xref `0x0061d7cc`; `CLine__SetBaseVtable_00426360(EBP-0x2e8)`. |
| 0x005d4f54 | DATA xref `0x0061d7d4`; `CLine__SetBaseVtable_00426360(EBP-0x280)`. |
| 0x005d4f5f | DATA xref `0x0061d7dc`; `CLine__SetBaseVtable_00426360(EBP-0x218)`. |
| 0x005d4f6a | DATA xref `0x0061d7e4`; `CLine__SetBaseVtable_00426360(EBP-0x1b0)`. |
| 0x005d4f75 | DATA xref `0x0061d7ec`; `CLine__SetBaseVtable_00426360(EBP-0x1e4)`. |
| 0x005d4f90 | DATA xref `0x0061d814`; `OID__FreeObject_Callback(*(EBP-0x10))` with StaticShadows.cpp line token `0x43d` and allocation/type value `0x70`. |

This is static saved-Ghidra metadata/decompile/xref evidence only. Runtime static-shadow behavior, exact line/local layout, exact source-body identity, BEA patching, and rebuild parity remain unproven.

### Wave426 Owner Boundary Note

Wave426 supersedes the older `CStaticShadows__TraceSegmentAgainstHeightfield` owner label at `0x00490a40`; current saved Ghidra evidence classifies that target as `CHeightField__TraceLineAgainstHeightfield`. Static shadows can call into heightfield/terrain helpers, but the checked line-trace body belongs to the MAP/heightfield context, not a `CStaticShadows` method. This is static Ghidra evidence only and does not prove runtime shadow or terrain behavior.

### Related Systems
- RTMesh (runtime mesh) at object+0x30
- Scene graph traversal via virtual calls
- Coordinate transformation matrices
- Terrain/heightfield sampling through `CStaticShadows__SampleShadowHeightBilinear`; Wave394 is static read-back only and does not prove runtime shadow behavior.

---
*Discovered via Phase 1 xref analysis (Dec 2025)*
