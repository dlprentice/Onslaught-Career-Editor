# DXPatchManager.cpp

> DirectX terrain patch manager for LOD (Level of Detail) rendering
> Debug path: `C:\dev\ONSLAUGHT2\DXPatchManager.cpp` (0x0065211c)

## Overview

DXPatchManager manages terrain patches for the landscape LOD system. It allocates pools of `CDXPatch` objects at different detail levels (likely near/medium/far) and manages landscape textures with mipmap levels.

The system uses three patch pools with different vertex buffer configurations:
- Pool 1: 800 patches, vertex size 2 (low detail)
- Pool 2: 300 patches, vertex size 4 (medium detail)
- Pool 3: 90 patches, vertex size 8 (high detail)

Each patch contains vertex buffer data for terrain geometry rendering.

## Classes

### CDXPatchManager
Main manager class that owns patch pools and landscape textures.

**Structure (inferred):**
```cpp
struct CDXPatchManager {
    CDXPatchPool* patchPool1;      // +0x00: Pool for detail level 1
    void* landscapeTextures;       // +0x04: Array of CLandscapeTexture[48]
    CDXPatchPool* patchPool2;      // +0x08: Pool for detail level 2
    int numPatches2;               // +0x0C: Count for pool 2
    CDXPatchPool* patchPool3;      // +0x10: Pool for detail level 3
    int numPatches3;               // +0x14: Count for pool 3
};
```

### CDXPatch
Individual terrain patch with vertex buffer data.

**Structure (inferred):**
```cpp
struct CDXPatch : CVBuffer {
    // CVBuffer base class
    void* vtable;                  // +0x00: Points to 0x005e5114
    // ... CVBuffer members ...
    short slotIndex;               // +0x3C: Allocation slot (-1 = free)
    int unknown40;                 // +0x40
    int lodLevel;                  // +0x44: LOD level (2, 4, or 8)
    // Total size: 0x50 (80 bytes)
};
```

### CDXPatchPool (helper struct)
Pool of patches at a specific detail level.

**Structure (inferred):**
```cpp
struct CDXPatchPool {
    CDXPatch* patches;             // +0x00: Array of patches
    int maxPatches;                // +0x04: Pool capacity
};
```

## Functions (8 total)

| Address | Name | Size | Notes |
|---------|------|------|-------|
| 0x00550380 | CDXPatch__Constructor | 0x20 | Sets vtable to 0x005e5114 |
| 0x005503a0 | CDXPatch__Destructor_thunk | 0x10 | Thunk to CVBuffer destructor |
| 0x005503b0 | CDXPatchManager__ReleasePatches | 0x20 | Releases patch pool via vtable call |
| 0x005503d0 | CDXPatchManager__ResetPatchSlots | 0x30 | Resets all slot indices to -1 (0xFFFF) |
| 0x00550400 | CDXPatchManager__AllocatePatchSlot | 0x30 | Finds free slot, returns patch pointer |
| 0x00550430 | CDXPatchManager__Init | 0x250 | Main initialization, creates 3 pools |
| 0x005506e0 | CDXPatchManager__Destroy | 0x50 | Frees all pools and textures |
| 0x00550730 | CDXPatch__FreeData | 0x20 | Frees patch data buffer at +0x0C |
| 0x00550750 | CDXPatch__LoadFromFile | 0x98 | Loads patch data from resource file |

## Function Details

### CDXPatchManager__Init (0x00550430)

**Signature:** `void __thiscall CDXPatchManager__Init(CDXPatchManager* this, int pool1Count, int pool2Count, int pool3Count)`

**Called from:** DXEngine initialization (0x0053d5f0) with parameters (800, 300, 90)

**Purpose:** Initializes the patch manager with three pools of terrain patches at different LOD levels.

**Key Operations:**
1. Allocates CDXPatchManager structure (0x1C bytes)
2. Creates patch pool 1 with `pool1Count` patches, LOD level 2
3. Creates patch pool 2 with `pool2Count` patches, LOD level 4
4. Creates patch pool 3 with `pool3Count` patches, LOD level 8
5. Allocates 48 CLandscapeTexture objects (0x9C4 bytes total, 0x34 each)
6. Calls CLandscapeTexture__SetupMipLevel for 3 LOD levels x 16 textures

**Memory allocations:**
- Pool 1: `800 * 0x50 + 4 = 64,004 bytes`
- Pool 2: `300 * 0x50 + 4 = 24,004 bytes`
- Pool 3: `90 * 0x50 + 4 = 7,204 bytes`
- Textures: `0x9C4 = 2,500 bytes`

### CDXPatch__LoadFromFile (0x00550750)

**Signature:** `void __thiscall CDXPatch__LoadFromFile(CDXPatch* this, CResourceFile* file)`

**Called from:** CResourceAccumulator__ReadResourceFile (0x004d7200)

**Purpose:** Loads patch vertex data from a resource file during level loading.

**Key Operations:**
1. Reads 3 rows x 16 columns of 4-byte values (mip data) from file
2. Reads count value for vertex data
3. Allocates vertex buffer (`count * 2` bytes)
4. Reads vertex data from file
5. Sets loaded flag at offset +0x08

### CDXPatchManager__AllocatePatchSlot (0x00550400)

**Signature:** `CDXPatch* __thiscall CDXPatchManager__AllocatePatchSlot(CDXPatchPool* pool, short slotId)`

**Purpose:** Finds a free patch slot and marks it as allocated.

**Returns:** Pointer to allocated patch, or NULL if pool is full.

**Algorithm:**
```cpp
for each patch in pool:
    if patch.slotIndex == -1:  // Free slot
        patch.slotIndex = slotId
        return &patch
return NULL  // Pool exhausted
```

### CDXPatchManager__ResetPatchSlots (0x005503d0)

**Signature:** `void __thiscall CDXPatchManager__ResetPatchSlots(CDXPatchPool* pool)`

**Purpose:** Marks all patches in pool as free by setting slot index to -1.

**Used for:** Level unload/reload, freeing all terrain patches.

## Vtables

### CDXPatch vtable at 0x005e5114
```
+0x00: 0x00550320  (inherited from CVBuffer - destructor?)
+0x04: 0x0048f320  (CVBuffer__Restore wrapper)
+0x08: 0x00500250  (CVBuffer method)
+0x0C: 0x00500280  (CVBuffer__Release)
+0x10: 0x005002b0  (CVBuffer__ReleaseManaged)
+0x14: 0x00619c40  (unknown)
+0x18: 0x00551fb0  (destructor with free)
+0x1C: 0x00405930  (unknown)
+0x20: 0x00552410  (unknown)
+0x24: 0x00552470  (release resource at +0x6C0)
```

## Related Classes

- **CVBuffer** - Base class for DirectX vertex buffers (vbuffer.cpp)
- **CLandscapeTexture** - Landscape texture with mipmap levels (LandscapeTexture.cpp)
- **CResourceAccumulator** - Resource file loader (ResourceAccumulator.cpp)

## Constants

| Value | Meaning |
|-------|---------|
| 0x50 | CDXPatch structure size (80 bytes) |
| 0x34 | CLandscapeTexture structure size (52 bytes) |
| 0x1C | CDXPatchManager structure size (28 bytes) |
| 0xFFFF | Free slot marker |
| 0x30 | Number of landscape textures (48) |
| 0x10 | Textures per LOD level (16) |

## LOD System

The patch manager implements a terrain LOD system:

| LOD Level | Patch Count | Vertex Grid | Use Case |
|-----------|-------------|-------------|----------|
| 2 | 800 | 3x3 | Distant terrain |
| 4 | 300 | 5x5 | Medium distance |
| 8 | 90 | 9x9 | Near terrain |

Vertex count per patch: `(level + 1)^2`
- LOD 2: 9 vertices
- LOD 4: 25 vertices
- LOD 8: 81 vertices

## Xrefs to Debug Path (0x0065211c)

| Address | Function | Line# | Context |
|---------|----------|-------|---------|
| 0x0055044d | CDXPatchManager__Init | 0x54 | OID__AllocObject call |
| 0x00550479 | CDXPatchManager__Init | 0x11 | Patch pool allocation |
| 0x005504f4 | CDXPatchManager__Init | 0x11 | Patch pool allocation |
| 0x0055057d | CDXPatchManager__Init | 0x11 | Patch pool allocation |
| 0x005505f1 | CDXPatchManager__Init | 0x5b | Texture array allocation |
| 0x005507b5 | CDXPatch__LoadFromFile | 0x94 | Vertex buffer allocation |

## Notes

1. **Not in Stuart's source:** DXPatchManager.cpp is likely a PC port addition or DirectX-specific implementation not present in the original console source.

2. **Memory management:** Uses OID__AllocObject (0x005490e0) with allocation type 0x35 for all allocations.

3. **Exception handling:** Multiple Unwind@* functions in exception handler chain for cleanup on allocation failure.

4. **Relationship to DXLandscape:** Works closely with CDXLandscape for terrain rendering, providing the patch geometry that gets textured and rendered.
