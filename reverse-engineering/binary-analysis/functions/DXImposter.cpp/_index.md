# DXImposter.cpp - DirectX Imposter Rendering System

**Source File:** `C:\dev\ONSLAUGHT2\DXImposter.cpp`
**Debug String Address:** `0x006508cc`
**Analysis Date:** December 2025

## Overview

DXImposter is the DirectX rendering component for imposters - billboard sprites used as a Level of Detail (LOD) technique to render distant objects cheaply. Instead of rendering full 3D models at long distances, the game renders pre-computed 2D images that face the camera.

This file handles the DirectX-specific rendering infrastructure for imposters:
- Deserializing imposter data from resource files
- Managing vertex/index buffers for batch rendering
- Allocating imposter texture objects

The imposter system works in conjunction with:
- **imposter.cpp** - Core imposter logic (CImposter class) at address range `0x00488xxx`
- **rtmesh.cpp** - Real-time mesh rendering with imposter fallback

## Functions Found (2 total)

| Address | Name | Size | Purpose |
|---------|------|------|---------|
| `0x00543d90` | `CDXImposter__Deserialize` | ~432 bytes | Load imposter data from resource file |
| `0x00543f50` | `CDXImposter__Create` | ~232 bytes | Create single imposter instance |

## Global Variables

| Address | Name | Purpose |
|---------|------|---------|
| `0x008aa8b4` | `g_pImposterVBuf1` | CVBufTexture* - Primary vertex buffer texture |
| `0x008aa8b8` | `g_pImposterTexture` | CDXTexture* - Imposter texture atlas |
| `0x008aa8bc` | `g_nImposterCount` | int - Total imposter count |
| `0x008aa8c0` | `g_nImposterWidth` | int - Imposter texture width |
| `0x008aa8c4` | `g_nImposterHeight` | int - Imposter texture height |
| `0x008aa8cc` | `g_pImposterVBuf2` | CVBufTexture* - Secondary vertex buffer texture |
| `0x0067a678` | `g_pImposterList` | CImposter* - Linked list head |
| `0x0067a67c` | `g_bImpostersInitialized` | bool - Initialization flag |

## Function Details

### CDXImposter__Deserialize (0x00543d90)

Main deserialization function that loads imposter data from a resource file during level loading.

**Signature (reconstructed):**
```cpp
void CDXImposter::Deserialize(CResourceAccumulator* resourceFile);
```

**Key Operations:**
1. Reads two unknown values via `FUN_00423910()` (stream read)
2. Reads width and height into globals at `0x008aa8c0` and `0x008aa8c4`
3. Reads another value (likely flags)
4. Destroys existing imposter texture if present via `FUN_004f27e0()` (destructor)
5. Calls `CDXTexture__Deserialize()` to load new texture atlas
6. Increments texture reference count at offset `0xa4`
7. Reads imposter count and creates individual imposters in a loop
8. Allocates two `CVBufTexture` objects (0x68 bytes each, OID type 0x1f):
   - Line 0x741: Primary buffer stored at `0x008aa8b4`
   - Line 0x742: Secondary buffer stored at `0x008aa8cc`
9. Configures vertex buffer format via `CVBufTexture__SetVBFormat()`:
   - FVF: 0x152 (D3DFVF_XYZ | D3DFVF_DIFFUSE | D3DFVF_TEX1)
   - Buffer count: 8
   - Vertex size: 0x24 (36 bytes)
   - Primitive type: 4 (triangle list)
10. Configures index buffer format via `CVBufTexture__SetIBFormat()`:
    - Format: 0x65
    - Buffer count: 8
    - Index size: 2 bytes (16-bit indices)
11. Sets initialization flag at `0x0067a67c` to 1

**Called By:**
- `CResourceAccumulator__ReadResourceFile` at `0x004d7706`

**Memory Allocations:**
- Allocates 0x68 bytes for each CVBufTexture via OID system
- Uses debug markers for lines 0x741 and 0x742

### CDXImposter__Create (0x00543f50)

Creates a single imposter instance and adds it to the global imposter list.

**Signature (reconstructed):**
```cpp
CImposter* CDXImposter::Create(CResourceAccumulator* resourceFile);
```

**Key Operations:**
1. Allocates imposter object (0x4c bytes, OID type 0x39) via `OID__AllocObject()`
2. Initializes object fields:
   - Offset 0x30: 0 (linked list next pointer)
   - Offset 0x38: 0 (unknown)
   - Offset 0x3c: 0 (frame data pointer)
3. Increments global imposter count at `0x008aa8bc`
4. Saves first dword of object (likely vtable/type ID)
5. Deserializes object data (0x4c bytes) from resource file
6. Reads additional value and looks up resource via `FUN_004ab330()`
7. Stores lookup result at offset 0x24 (texture/mesh reference)
8. Clears first dword temporarily
9. Allocates frame data buffer (size = `[0x40] * [0x44] * 0x18`)
   - Product of two dimension values times 24 bytes per frame
   - Stored at offset 0x3c
10. Deserializes frame data from resource file
11. Restores first dword
12. Calls `CImposter__AddToList()` to add to global linked list

**Returned Object Structure (0x4c bytes):**
```cpp
struct CImposter {
    /* 0x00 */ CImposter* pNext;      // Linked list next
    /* 0x04 */ char name[32];          // Imposter name (estimated)
    /* 0x24 */ void* pTextureRef;      // Texture/mesh reference
    /* 0x30 */ void* pUnknown1;        // Unknown
    /* 0x38 */ void* pUnknown2;        // Unknown
    /* 0x3c */ void* pFrameData;       // Per-frame animation data
    /* 0x40 */ int nFrameCountX;       // Frame count X dimension
    /* 0x44 */ int nFrameCountY;       // Frame count Y dimension
    /* 0x48 */ int unknown;            // Unknown
};
```

**Memory Allocations:**
- 0x4c bytes for imposter object (OID type 0x39)
- Frame data: `[0x40] * [0x44] * 0x18` bytes (variable size)
- Uses debug markers for lines 0x7e3 and 0x807

## Exception Handlers

Two compiler-generated exception unwinding functions exist for cleanup:

| Address | Name | Triggered By |
|---------|------|--------------|
| `0x005d78e0` | `Unwind@005d78e0` | CVBufTexture allocation at line 0x741 |
| `0x005d78f9` | `Unwind@005d78f9` | CVBufTexture allocation at line 0x742 |

Both call `OID__FreeObject_Callback()` (wrapper around `OID__FreeObject`) to clean up on allocation failure.

## Related Functions (in other files)

These functions use DXImposter globals but are defined in other source files:

| Address | Name | Source File | Purpose |
|---------|------|-------------|---------|
| `0x005428d0` | `CDXImposter__InitGlobals` | imposter.cpp? | Initialize all imposter globals to zero |
| `0x00542990` | `CDXImposter__ShutdownAll` | imposter.cpp? | Destroy all imposters, free vertex buffers |
| `0x00542a30` | `CDXImposter__InitEntry` | imposter.cpp? | Initialize imposter object fields |
| `0x005438c0` | `CDXImposter__RenderAll` | imposter.cpp? | Render imposters (complex rendering setup) |
| `0x00542f90` | `CDXImposter__BuildQuadGeometry` | imposter.cpp? | Build imposter quad vertices |
| `0x004888f0` | `CImposter__FindOrCreate` | imposter.cpp | Find existing or create new imposter |
| `0x00488a70` | `CImposter__AddToList` | imposter.cpp | Add imposter to global linked list |

## Imposter Rendering Pipeline

```
1. Level Load
   |
   v
2. CResourceAccumulator__ReadResourceFile()
   |
   v
3. CDXImposter__Deserialize()
   - Load texture atlas
   - Create vertex buffers
   - Loop: CDXImposter__Create() for each imposter
   |
   v
4. Runtime Rendering (`CDXImposter__RenderAll`)
   - Check if initialized (g_bImpostersInitialized)
   - Check if list has entries (g_pImposterList)
   - Set render states
   - Build vertex data for visible imposters
   - CVBufTexture__RenderIndexed()
```

## Vertex Format

Imposters use a standard textured vertex format (FVF 0x152):

```cpp
struct ImposterVertex {
    float x, y, z;      // Position (12 bytes)
    DWORD color;        // Diffuse color (4 bytes)
    float u, v;         // Texture coordinates (8 bytes)
    // Total: 36 bytes (0x24)
};
```

Quad rendering uses 4 vertices and 6 indices per imposter (2 triangles).

## Console Variables

From the strings dump, these cvars relate to imposters:

| CVar | Address | Purpose |
|------|---------|---------|
| `cg_renderimposters` | `0x0062c8cc` | Enable/disable imposter rendering |
| `cg_imposterfadestart` | `0x0063211c` | Distance to start fading in |
| `cg_imposterfadeend` | `0x006320dc` | Distance to stop fading in |
| `cg_forceobjectimposters` | `0x00632164` | Force imposter mode for all objects |

## Technical Notes

1. **Texture Atlas**: All imposter images are packed into a single texture atlas loaded via `CDXTexture__Deserialize()`
2. **Reference Counting**: Texture has reference count at offset 0xa4, incremented on load
3. **Dual Vertex Buffers**: Two CVBufTexture objects are allocated, possibly for double-buffering or LOD separation
4. **Dynamic Sizing**: Frame data allocation is based on imposter dimensions from resource file
5. **Linked List**: Imposters form a singly-linked list via first dword for iteration
6. **OID System**: Uses game's object ID system for memory tracking:
   - Type 0x1f: CVBufTexture
   - Type 0x39: CImposter

## String References

| Address | String | Context |
|---------|--------|---------|
| `0x006508cc` | `"C:\dev\ONSLAUGHT2\DXImposter.cpp"` | Debug path, 6 references |

## Data Following Debug String

At `0x006508f0`, there is vertex data (400 bytes = 100 floats) that appears to be static mesh data for cube rendering, likely used for debug visualization or a related system (DXKempyCube.cpp).
