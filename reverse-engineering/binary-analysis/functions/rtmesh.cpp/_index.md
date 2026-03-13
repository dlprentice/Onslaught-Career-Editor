# rtmesh.cpp Function Mappings

> Functions from rtmesh.cpp mapped to BEA.exe binary
> Debug Path: `C:\dev\ONSLAUGHT2\rtmesh.cpp` (0x00631f28)
> RTTI: `.?AVCRTMesh@@` (0x00631db8)

## Overview
- **Functions Mapped:** 7
- **Status:** Phase 1 xref analysis complete
- **Classes:** CRTMesh
- **Purpose:** Real-Time Mesh rendering system with LOD, imposters, and effects

## Function List

| Address | Name | Status | Purpose |
|---------|------|--------|---------|
| 0x004dc370 | CRTMesh__Init | NAMED | Constructor - initializes mesh, pose data, imposters, and console vars |
| 0x004dc950 | CRTMesh__Destructor | NAMED | Destructor - frees all allocated resources and unlinks from list |
| 0x004dcb00 | CRTMesh__FreePoseData | NAMED | Helper to free pose data arrays |
| 0x004dcb70 | CRTMesh__ScalarDeletingDestructor | NAMED | MSVC scalar deleting destructor |
| 0x004dd0c0 | CRTMesh__CleanupAllEffects | NAMED | Static - iterates all RTMesh instances and cleans up effects |
| 0x004dd6b0 | CRTMesh__SetQualityLevel | NAMED | Static - sets LOD/quality parameters (0=low, 1=med, 2=high) |
| 0x004dd770 | CRTMesh__GetQualityLevel | NAMED | Static - returns current quality level based on threshold |

## Console Variables (registered in Init)

| Variable | Description | Type | Global |
|----------|-------------|------|--------|
| cg_forceobjectimposters | Force use of object imposters | bool | 0x0083cd58 |
| cg_imposterfadestart | Distance at which imposters start | float | 0x00631e94 |
| cg_imposterfadeend | Distance at which imposters stop | float | 0x00631e98 |
| cg_meshlodbias | Mesh LOD bias (use <1 to increase) | float | 0x00631e88 |
| cg_meshlodmedthreshold | Mesh LOD high<->medium threshold | float | 0x00631e8c |
| cg_meshlodlowthreshold | Mesh LOD medium<->low threshold | float | 0x00631e90 |
| cg_meshlodignorezoom | Ignore zoom factor for LOD | bool | 0x0083cd5a |
| cg_snowlayerenable | Enable/disable snow layer | bool | 0x0083cd5b |
| cg_meshtexturelodbias | Mesh texture LOD bias | float | 0x00631e9c |
| cg_meshsurfacelodbias | Mesh surface LOD bias | float | 0x00631ea0 |

## Class Layout (partial)

```
CRTMesh (size ~0x4C+ bytes)
+0x00: vtable*
+0x04: float (from mesh +0x168)
+0x08: CAnimation* (animation pointer)
+0x0c: CMeshPose* (pose data)
+0x14: CMesh* (mesh pointer)
+0x18: CImposter* (imposter for distant rendering)
+0x1c: byte* (imposter state)
+0x20: unknown (from mesh +0x164)
+0x24: unknown (from param +0x404)
+0x28: int effectCount (number of effects with '_' prefix)
+0x2c: byte* effectFlags
+0x30: int* effectIndices
+0x34: int* effectTypes
+0x38: int* effectBoneIndices
+0x3c: int* effectStartFrames
+0x40: int* effectDurations
+0x44: unknown
+0x48: CRTMesh* next (linked list)
```

## Vtable (at 0x005deb1c)

| Offset | Address | Function |
|--------|---------|----------|
| +0x00 | 0x004dcb70 | CRTMesh__ScalarDeletingDestructor |
| +0x04 | 0x004dc370 | CRTMesh__Init |
| +0x08 | 0x004dcba0 | (not analyzed) |
| +0x0c | 0x004dcea0 | (not analyzed) |
| +0x10 | 0x004de060 | (not analyzed) |
| +0x14 | 0x004db8a0 | (not analyzed) |
| +0x18 | 0x004dcaf0 | (not analyzed) |
| +0x1c | 0x004dd160 | (not analyzed) |
| +0x20 | 0x004dd400 | (not analyzed) |
| +0x24 | 0x004de070 | (not analyzed) |
| +0x28 | 0x00405930 | (inherited/shared) |
| +0x2c | 0x004dcb90 | (not analyzed) |

## Key Observations

1. **Imposter System**: RTMesh uses imposters (billboard sprites) for distant objects to reduce polygon count. Console vars control fade distances.

2. **LOD System**: Three-tier LOD system (low/medium/high) with configurable thresholds and bias values.

3. **Effect System**: Effects are named with '_' prefix in bone names. The system tracks effect indices, types, bone associations, start frames, and durations.

4. **Linked List**: All CRTMesh instances are maintained in a global linked list (head at DAT_0083cd5c, tail at DAT_0083cd60) for batch operations like cleanup.

5. **Memory Allocation**: Uses game's heap allocator (OID__AllocObject) with allocation tags 0x7d (rtmesh) and 0x3b (effects). Also allocates from meshpose.h structures.

6. **Snow Layer**: Has a dedicated enable/disable for snow rendering on meshes.

## Related Strings

| Address | String |
|---------|--------|
| 0x00631db8 | `.?AVCRTMesh@@` (RTTI type info) |
| 0x00631ea3 | `Warning : not enough thing heap for RTMesh effects` |
| 0x00631ef8 | `Warning : not enough thing heap for RTMesh` |
| 0x00631f28 | `C:\dev\ONSLAUGHT2\rtmesh.cpp` (debug path) |
| 0x00632a58 | `Thing at 0x%x has no RTMesh when trying to statically shadow!` |

## Related Files
- meshpose.h - Referenced for pose data allocation
- CMesh - Base mesh system (`CMesh__FindOrCreate`)
- CImposter - Imposter/billboard system (`CImposter__FindOrCreate`)

## Parent
- [../README.md](../README.md)

---
*Discovered via Phase 1 xref analysis (Dec 2025)*
