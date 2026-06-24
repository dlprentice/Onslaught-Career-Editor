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
    int gridOriginX;               // +0x2C: Wave807 observed rebuild origin X
    int gridOriginZ;               // +0x30: Wave807 observed rebuild origin Z
    int gridStep;                  // +0x34: Wave807 observed height-sample step
    short slotIndex;               // +0x3C: Allocation slot (-1 = free)
    int rebuildDirtyOrReady;       // +0x40
    int gridVertexStep;            // +0x44: Wave422 grid size/source step (2, 4, or 8)
    int tileMetadata;              // +0x4C: Wave807 observed tile-record metadata copy
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

## Functions (13 documented rows)

| Address | Name | Size | Notes |
|---------|------|------|-------|
| 0x0048f1e0 | CDXPatch__CreateGridVertexBuffer | 0x30 | Wave422 owner/signature correction; creates a grid vertex buffer from one `grid_step` argument |
| 0x0048f210 | CDXPatch__RebuildHeightGridVertexBuffer | 0x110 | Wave422 owner/signature correction; rebuilds height-sampled grid vertices |
| 0x0048f2f0 | CDXPatch__SetGridOriginStepAndRebuild | 0x30 | Wave807 owner/signature correction; sets patch grid origin/step fields and rebuilds vertices from `CDXLandscape__UpdateLOD` callsite `0x00546fe6` |
| 0x0048f320 | CDXPatch__RestoreAndRebuildIfDirty | 0x30 | Wave422 owner/signature correction; vtable slot restore/rebuild wrapper |
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

## Wave807 Landscape Patch Raw Head Note (2026-05-24)

Wave807 landscape patch raw head (`landscape-patch-raw-head-wave807`, `wave807-readback-verified`) corrected stale `0x0048f2f0 CDXLandscape__SetUpdateBoundsAndRebuildVB` to `0x0048f2f0 CDXPatch__SetGridOriginStepAndRebuild` with saved signature `void __thiscall CDXPatch__SetGridOriginStepAndRebuild(void * this, int grid_origin_x, int grid_origin_z, int grid_step, int tile_metadata)`.

Static evidence: `RET 0x10` proves four stack arguments after `ECX=this`; `CDXLandscape__UpdateLOD` callsite `0x00546fe6` calls this immediately after `CDXPatchManager__AllocatePatchSlot` returns a patch pointer, then passes two tile coordinates scaled by `8`, `grid_step` derived as `4 >> lod_slot`, and a tile-record metadata value from `[ESI+0x0b]`. The body stores the args into CDXPatch fields `+0x2c`, `+0x30`, `+0x34`, and `+0x4c`, then calls `CDXPatch__RebuildHeightGridVertexBuffer(this)`.

Post-Wave807 queue telemetry is `6098` total, `5582` commented, `516` commentless, `0` exact-undefined signatures, `0` `param_N`, strict proxy `5582/6098 = 91.54%`, and next raw head `0x0048f620 CDXEngine__RenderPostMissionOverlayAndMenu`. Verified backup: `G:\GhidraBackups\BEA_20260524-105819_post_wave807_landscape_patch_raw_head_verified`.

This is static Ghidra read-back evidence only. Exact source-body identity, exact CDXPatch field names, tile-record layout, runtime terrain rendering/GPU behavior, BEA patching, and rebuild parity remain deferred.

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
+0x00: 0x00550320  (Wave613: no Ghidra function at pointer yet; deferred boundary)
+0x04: 0x0048f320  (CDXPatch__RestoreAndRebuildIfDirty)
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

## Wave613 Static Re-Audit Note (2026-05-20)

Wave613 saved nine CDXPatch/CDXPatchManager signatures, comments, and tags from fresh retail Ghidra read-back. The pass made no renames and did not recover any missing boundaries.

| Address | Saved signature | Static evidence |
| --- | --- | --- |
| `0x00550380` | `void * __thiscall CDXPatch__Constructor(void * this)` | Vector-constructor callsites `0x005504ab`, `0x0055052a`, and `0x005505ad` pass this ECX-only constructor for each `0x50`-byte patch-pool entry. The body calls `CVBuffer__ctor_base`, installs vtable `0x005e5114`, and returns `this`. |
| `0x005503a0` | `void __thiscall CDXPatch__Destructor_thunk(void * this)` | Vector-destructor callsites `0x005504a6`, `0x00550525`, and `0x005505a8` pass this thunk beside the constructor. The body tail-jumps to `CVBuffer__dtor_base`. |
| `0x005503b0` | `void __fastcall CDXPatchManager__ReleasePatches(void * patch_pool_entry)` | `CDXPatchManager__Destroy` passes this helper as a callback at `0x005506f0` over 8-byte patch-pool entries. It releases the array through vtable slot 0 with delete flag `3` and clears the pointer. |
| `0x005503d0` | `void __fastcall CDXPatchManager__ResetPatchSlots(void * patch_pool)` | `CDXLandscape__Reset` (`0x00545392`) and `CDXEngine__InvalidateLandscapeTilesAndPatchSlots` (`0x005473d5`) pass a patch-pool pointer in ECX. The body walks count entries with `0x50` stride and writes `0xffff` at patch `+0x3c`. |
| `0x00550400` | `void * __thiscall CDXPatchManager__AllocatePatchSlot(void * this, short slot_id)` | `CDXLandscape__UpdateLOD` callsite `0x00546fa6` passes one `RET 0x4` stack slot id. The helper scans for `+0x3c == -1`, stores the slot id, returns the patch pointer, or returns null if the pool is exhausted. |
| `0x00550430` | `void __thiscall CDXPatchManager__Init(void * this, int lod2_patch_count, int lod4_patch_count, int lod8_patch_count)` | `CDXEngine__Init` callsite `0x0053d6c3` passes counts `800`, `300`, and `90`. The body allocates a pool table, allocates three `0x50`-byte patch arrays, constructs patch entries, creates grid vertex buffers for LOD steps `2`, `4`, and `8`, allocates 48 `CLandscapeTexture` entries, and initializes three 16-texture mip groups. |
| `0x005506e0` | `void __thiscall CDXPatchManager__Destroy(void * this)` | `CDXEngine__Shutdown` callsite `0x0053d467` passes the engine-owned manager fields in ECX. The body destroys the pool table through `CDXLandscape__DestroyArrayWithCallback`, frees the count header, clears the pool pointer, releases the landscape-texture vector, and clears the texture pointer. |
| `0x00550730` | `void __thiscall CDXPatch__FreeData(void * this)` | Unbounded callsite `0x005120cb` reaches this ECX-only cleanup helper. It frees the data pointer at patch `+0x0c` through `CDXMemoryManager__Free` when non-null, then clears it. |
| `0x00550750` | `void __thiscall CDXPatch__LoadFromFile(void * this, void * chunk_reader)` | `CResourceAccumulator__ReadResourceFile` callsite `0x004d7875` passes a CDXPatch in ECX and one chunk-reader argument. The body reads `3x16` dwords into `+0x10`, reads a data count into `+0xd0`, allocates `count*2` bytes from DXPatchManager.cpp line `0x94`, reads 16-bit data into `+0x0c`, and marks `+0x08` loaded. |

Read-back verified `9` metadata rows, `9` tag rows, `16` xref rows, `2349` instruction rows, `9` decompile rows, `464` callsite instruction rows, and `10` vtable-slot rows. Queue telemetry after Wave613 is `6093` functions, `3156` commented, `2937` commentless, `1275` exact-undefined signatures, `1056` `param_N`, comment-backed proxy `3156/6093 = 51.80%`, strict clean-signature proxy `3111/6093 = 51.06%`, and next head `0x00552060 CDXShadows__Destructor`. Verified backup: `G:\GhidraBackups\BEA_20260520-001229_post_wave613_cdxpatch_manager_verified`.

CDXPatch vtable `0x005e5114` remains partial. Slot 0 points to `0x00550320`, where no Ghidra function exists yet; the nearby unbounded region calls `CDXPatch__Destructor_thunk` at `0x0055035c`, but Wave613 deliberately deferred boundary recovery. Exact CDXPatch, CDXPatchManager, patch-pool, CLandscapeTexture, and serialized patch-data layouts, runtime terrain rendering/LOD behavior, BEA patching, and rebuild parity remain unproven.

## Wave422 Static Re-Audit Note (2026-05-14)

Wave422 corrected three patch/vertex-buffer helpers and one adjacent texture invalidation helper from fresh saved Ghidra read-back:

| Address | Saved signature | Static evidence |
| --- | --- | --- |
| `0x0048f1e0` | `void __thiscall CDXPatch__CreateGridVertexBuffer(void * this, int grid_step)` | `RET 0x4` proves one stack argument. The body stores `grid_step` at `+0x44`, computes `(grid_step+1)^2` at `+0x38`, clears patch fields, writes slot marker `+0x3c = 0xffff`, and calls `CVBuffer__Create` with `0x14`-byte vertices and flags `0x102`. |
| `0x0048f210` | `void __thiscall CDXPatch__RebuildHeightGridVertexBuffer(void * this)` | Calls `CVBuffer__Lock`, walks a square grid from start X/Z fields `+0x2c/+0x30` with step `+0x34`, samples `CWorld__GetHeightSamplePacked16`, writes `0x14`-byte vertex rows, calls `CVBuffer__Unlock`, and marks `+0x40`. |
| `0x0048f320` | `int __thiscall CDXPatch__RestoreAndRebuildIfDirty(void * this)` | Vtable `0x005e5114` slot 1 dispatches here; calls `CVBuffer__Restore`, rebuilds when `+0x40` is nonzero, and returns the restore result. |

The same wave corrected adjacent `0x0048f180` to `CLandscapeTexture__InvalidateTileMaskOrRefreshAll`; see `LandscapeTexture.cpp/_index.md`. The Wave422 apply/read-back verified `4` metadata rows, `4` tag rows, `7` xref rows, `484` instruction rows, `4` decompile exports, and `32` vtable-adjacent rows. Runtime terrain rendering, GPU upload/restore behavior, concrete layouts, complete vtable recovery, BEA launch, game patching, and rebuild parity remain unproven.
