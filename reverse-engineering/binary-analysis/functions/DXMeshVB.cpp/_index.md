# DXMeshVB.cpp - DirectX Mesh Vertex Buffer Management

**Source File:** `C:\dev\ONSLAUGHT2\DXMeshVB.cpp`
**Debug String Address:** `0x00651244`
**Total Functions Found:** 3

## Overview

This source file implements DirectX vertex buffer management for 3D mesh rendering. It handles both static geometry and skeletal (animated) meshes, creating and managing Direct3D vertex and index buffers.

The CDXMeshVB class appears to be part of the rendering subsystem, responsible for:
- Building vertex buffers from mesh data
- Creating index buffers for triangle strips
- Supporting both static and skeletal mesh rendering
- Loading/streaming vertex buffer data from files

## Functions

| Address | Name | Size | Description |
|---------|------|------|-------------|
| `0x0054c0a0` | `CDXMeshVB__BuildStaticVB` | ~2176 bytes | Builds vertex/index buffers for static meshes |
| `0x0054c920` | `CDXMeshVB__BuildSkeletalVB` | ~2112 bytes | Builds vertex/index buffers for skeletal meshes |
| `0x0054e160` | `CDXMeshVB__Load` | ~600 bytes | Loads vertex buffer data from stream |

## Function Details

### CDXMeshVB__BuildStaticVB (0x0054c0a0)

**Purpose:** Builds DirectX vertex and index buffers for static (non-animated) mesh geometry.

**Key Characteristics:**
- Uses `thiscall` convention (ECX = this pointer)
- Allocates vertex buffer of size `numVerts * 0x24` (36 bytes per vertex)
- Allocates index buffer data of size `numVerts * 0x300` (768 bytes per vertex for indices)
- Creates up to 64 material/texture groups
- Each vertex contains: position (12 bytes), normal (12 bytes), UV (8 bytes), color (4 bytes)
- Returns HRESULT-style value: `S_OK` on success, `E_FAIL` on failure

**Vertex Format (0x24 = 36 bytes):**
```
Offset 0x00: float3 position (12 bytes)
Offset 0x0C: float3 normal (12 bytes)
Offset 0x18: float2 texcoord (8 bytes)
Offset 0x20: DWORD color (4 bytes)
```

**Memory Allocations (via OID__AllocObject):**
- Line 0x51: Vertex data buffer (`numVerts * 0x24`)
- Line 0x52: Index data buffer (`numVerts * 0x300`)
- Line 0x84: Material group structure (0x3C = 60 bytes each)
- Line 0xBA: Triangle index arrays (`numFaces * 6` bytes)

**DirectX Calls:**
- `FUN_00513770` - Creates D3D vertex buffer (FVF 0x152 = position|normal|tex1)
- `FUN_005137d0` - Creates D3D index buffer (format 0x65 = 16-bit indices)
- Uses vtable calls at offset 0x2C (Lock) and 0x30 (Unlock)

**Final State:**
- Sets `this+0x114 = 0x24` (vertex stride)
- Sets `this+0x118 = 0x152` (FVF flags)
- Sets `this+0x11C = 4` (primitive type - triangle list)

---

### CDXMeshVB__BuildSkeletalVB (0x0054c920)

**Purpose:** Builds DirectX vertex and index buffers for skeletal (bone-animated) mesh geometry.

**Key Characteristics:**
- Uses `thiscall` convention (ECX = this pointer)
- Debug message: "Building skeletal VB" at 0x00651290
- Allocates larger vertex buffer: `numVerts * 0xC00` (3072 bytes per vertex batch)
- Vertex stride is 0x30 (48 bytes) vs 0x24 for static meshes
- Includes bone weight data multiplied by 3.0 for blending
- Checks `DAT_00854e6c` flag for hardware vs software vertex processing

**Skeletal Vertex Format (0x30 = 48 bytes):**
```
Offset 0x00: float3 position (12 bytes)
Offset 0x0C: float3 blendWeights (12 bytes) - bone weights * 3.0
Offset 0x18: float3 normal (12 bytes)
Offset 0x24: float2 texcoord (8 bytes)
Offset 0x2C: DWORD color (4 bytes)
```

**Memory Allocations (via OID__AllocObject):**
- Line 0x1A9: Vertex data buffer (`numVerts * 0xC00`)
- Line 0x1AA: Index data buffer (`numVerts * 0x180`)
- Line 0x1AB: Weight data buffer (`numVerts * 2`)
- Line 0x1D8: Material group structure (0x3C bytes)
- Line 0x216: Triangle index arrays

**Bone Weight Processing:**
```c
// Converts integer bone weights to floats with 3.0 multiplier
for (int i = 0; i < 3; i++) {
    weights[i] = (float)intWeights[i] * 3.0f;
}
```

**Hardware Detection:**
- If `DAT_00854e6c != 0`: Uses hardware vertex shaders (flag 0x18, type 2)
- Otherwise: Uses software processing (flag 0x8, type 1)

**Final State:**
- Sets `this+0x114 = 0x30` (vertex stride)
- Sets `this+0x118 = 0` (custom FVF/shader)
- Sets `this+0x11C = 4` (primitive type)

---

### CDXMeshVB__Load (0x0054e160)

**Purpose:** Loads/deserializes vertex buffer data from a file stream.

**Parameters:**
- `param_1` (int): Source data pointer/stream
- `param_2` (int): Boolean flag for hardware shader support

**Key Operations:**
1. Saves and restores class state during load
2. Frees existing vertex buffer resources (up to 64 groups)
3. Reads mesh name string from stream (offset +0x2C in source)
4. Allocates and copies name to `this+0x124` (member 0x49)
5. Iterates through material groups (up to `this+0x108` count)
6. Reads per-group data: buffer sizes, vertex counts, etc.
7. Creates D3D vertex and index buffers
8. Reads texture/material references (indices 0x20-0x38)

**Memory Allocations (via OID__AllocObject):**
- Line 0x6CE: Mesh name string (strlen + 1)
- Line 0x6DC: Material group structure (0x3C bytes)

**Stream Reading (via FUN_00423960):**
- Reads vertex buffer size at offset +0x08
- Reads index buffer size at offset +0x0C
- Reads vertex count at offset +0x10
- Reads primitive count at offset +0x14
- Reads triangle count at offset +0x18
- Reads flags at offset +0x1C
- Reads 6 texture indices at offsets 0x20-0x34

**Hardware Detection:**
- Same as BuildSkeletalVB: checks `DAT_00854e6c` and `param_2`

---

## Class Structure (CDXMeshVB)

Based on decompilation analysis:

```cpp
class CDXMeshVB {
    /* 0x000 */ IDirect3DVertexBuffer* m_pVB;      // Vertex buffer pointer
    /* 0x004 */ IDirect3DIndexBuffer* m_pIB;       // Index buffer pointer
    /* 0x008 */ CMaterialGroup* m_pGroups[64];     // Material groups (0x40 entries)
    /* 0x108 */ int m_nGroupCount;                 // Number of active groups
    /* 0x10C */ CMesh* m_pSourceMesh;              // Source mesh data
    /* 0x110 */ int m_unknown110;
    /* 0x114 */ int m_nVertexStride;               // Bytes per vertex (0x24 or 0x30)
    /* 0x118 */ DWORD m_dwFVF;                     // Flexible vertex format flags
    /* 0x11C */ int m_nPrimitiveType;              // D3D primitive type
    /* 0x120 */ int m_unknown120;
    /* 0x124 */ char* m_szMeshName;                // Mesh name string
};
```

## Related Systems

- **OID__AllocObject**: Memory allocation with debug tracking (file/line)
- **FUN_00513770**: D3D vertex buffer creation wrapper
- **FUN_005137d0**: D3D index buffer creation wrapper
- **FUN_0056eb60/70/80/50**: Render state setup functions
- **FUN_0056eb90**: Triangle strip optimizer
- **CLandscapeTexture__FreeTexture**: Texture cleanup callback
- **DAT_00854e6c**: Hardware vertex shader capability flag
- **DAT_009c3df0**: D3D device critical section/lock

## Technical Notes

1. **FVF 0x152 Breakdown:**
   - `D3DFVF_XYZ` (0x002) - Position
   - `D3DFVF_NORMAL` (0x010) - Normal vector
   - `D3DFVF_TEX1` (0x100) - One texture coordinate set
   - `D3DFVF_DIFFUSE` (0x040) - Diffuse color

2. **Index Format 0x65:**
   - 16-bit indices (D3DFMT_INDEX16)
   - Used for triangle lists/strips

3. **Memory Pool:**
   - Allocation type 0x3A likely corresponds to D3DPOOL_MANAGED

4. **Error Handling:**
   - Returns `(success ? 0 : 0x80004005)` - S_OK or E_FAIL

## Cross-References

Functions called by DXMeshVB:
- `OID__AllocObject` - Memory allocation
- `OID__FreeObject` - Memory deallocation
- `FUN_00513770` - VB creation
- `FUN_005137d0` - IB creation
- `DebugTrace` - Debug trace output (ret stub in retail build; was `FUN_0040c640`)
- `CConsole__Status` - Begin status/logging section ("Building skeletal VB")
- `CConsole__StatusDone` - End status/logging section
- `FUN_0056eb90` - Strip optimization

## Version History

| Date | Change |
|------|--------|
| 2025-12-16 | Initial documentation - 3 functions identified and named |
