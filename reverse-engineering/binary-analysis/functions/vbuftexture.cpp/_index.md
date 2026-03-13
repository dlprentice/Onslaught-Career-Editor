# vbuftexture.cpp - Vertex Buffer Texture System

**Source File:** `C:\dev\ONSLAUGHT2\vbuftexture.cpp`
**Debug Path Address:** `0x00633d5c`
**Function Range:** `0x005003f0` - `0x00501280`

## Overview

The CVBufTexture class combines vertex buffers with texture data for efficient rendering. It wraps D3D vertex/index buffers and associates them with textures for batched rendering operations. This is a higher-level abstraction over the raw CVBuffer class (from vbuffer.cpp).

## Class Architecture

CVBufTexture maintains:
- **Dual vertex buffers** - For double-buffering (mSlots[0x48] toggles between them)
- **Index buffer** - For indexed primitive rendering
- **Texture association** - Links vertex data to textures
- **Global linked list** - All instances tracked via `DAT_00854e00` for bulk operations

### Key Member Offsets

| Offset | Type | Purpose |
|--------|------|---------|
| 0x00 | int* | Texture pointer |
| 0x04 | int | FVF format / shader |
| 0x08 | uint | VB usage flags |
| 0x0C | int | VB pool type |
| 0x10 | bool | VB locked flag |
| 0x14 | int[2] | VB sizes (double-buffered) |
| 0x1C | int | Current VB data size |
| 0x20 | int | IB format |
| 0x24 | uint | IB usage flags |
| 0x28 | int | IB pool type |
| 0x2C | bool | IB locked flag |
| 0x30 | int | IB size |
| 0x34 | int | Current IB data size |
| 0x38 | void* | VB lock pointer |
| 0x3C | void* | IB lock pointer |
| 0x40 | int[2] | VB D3D objects (double-buffered) |
| 0x48 | int | Current buffer index (0 or 1) |
| 0x4C | int | IB D3D object |
| 0x50 | int | Primitive type (D3DPRIMITIVETYPE) |
| 0x54 | int | Vertex stride |
| 0x58 | int* | Next in linked list |
| 0x5C | bool | Persist flag |
| 0x60 | int | Reference count |
| 0x64 | int | Last vertex count |

### Primitive Type Values (D3DPRIMITIVETYPE)

Used in GetIndexPrimitiveCount/GetVertexPrimitiveCount:
- 1 = D3DPT_POINTLIST
- 2 = D3DPT_LINELIST
- 3 = D3DPT_LINESTRIP
- 4 = D3DPT_TRIANGLELIST
- 5 = D3DPT_TRIANGLESTRIP
- 6 = D3DPT_TRIANGLEFAN

## Functions (18 total)

### Construction / Destruction

| Address | Name | Purpose |
|---------|------|---------|
| `0x005003f0` | `CVBufTexture__CVBufTexture` | Constructor - initializes members, adds to global list |
| `0x00500460` | `CVBufTexture__dtor` | Destructor - releases buffers, removes from global list |

### Configuration

| Address | Name | Purpose |
|---------|------|---------|
| `0x00500540` | `CVBufTexture__SetVBFormat` | Set vertex buffer format (FVF, usage, pool, stride) |
| `0x00500590` | `CVBufTexture__SetIBFormat` | Set index buffer format (format, usage, pool) |
| `0x005005d0` | `CVBufTexture__SetPersist` | Mark buffer as persistent (won't be released) |

### Buffer Management

| Address | Name | Purpose |
|---------|------|---------|
| `0x005005e0` | `CVBufTexture__ResizeVertexBuffer` | Resize/recreate vertex buffer, preserves existing data |
| `0x005007f0` | `CVBufTexture__ResizeIndexBuffer` | Resize/recreate index buffer, preserves existing data |
| `0x005009c0` | `CVBufTexture__UnlockVB` | Unlock vertex buffer after writing |
| `0x005009f0` | `CVBufTexture__UnlockIB` | Unlock index buffer after writing |

### Data Writing

| Address | Name | Purpose |
|---------|------|---------|
| `0x00500a10` | `CVBufTexture__AddVertices` | Copy vertex data to buffer, auto-resize if needed |
| `0x00500ac0` | `CVBufTexture__AddIndices` | Copy index data to buffer, auto-resize if needed |
| `0x00500b40` | `CVBufTexture__GetIndexPtr` | Get raw pointer to index buffer for direct writes |
| `0x00500bb0` | `CVBufTexture__GetVertexPtr` | Get raw pointer to vertex buffer for direct writes |

### Primitive Counting

| Address | Name | Purpose |
|---------|------|---------|
| `0x00500c50` | `CVBufTexture__GetIndexPrimitiveCount` | Calculate primitive count from index data |
| `0x00500cb0` | `CVBufTexture__GetVertexPrimitiveCount` | Calculate primitive count from vertex data |

### Rendering

| Address | Name | Purpose |
|---------|------|---------|
| `0x00500d10` | `CVBufTexture__RenderBatchList` | Render a batch list sorted by texture priority |
| `0x00500e70` | `CVBufTexture__Render` | Main render - sets texture, calls DrawIndexedPrimitive |
| `0x00500f80` | `CVBufTexture__Reset` | Reset buffer cursors, toggle double-buffer |
| `0x00500fa0` | `CVBufTexture__RenderIndexed` | Render with indexed primitives (with validation) |
| `0x005010e0` | `CVBufTexture__RenderIndexedNoValidate` | Render indexed without ValidateDevice check |
| `0x005011c0` | `CVBufTexture__RenderNonIndexed` | Render without index buffer (DrawPrimitive) |

### Factory

| Address | Name | Purpose |
|---------|------|---------|
| `0x00501280` | `CVBufTexture__GetOrCreate` | Get existing or create new CVBufTexture for a texture |

## Global Variables

| Address | Name | Purpose |
|---------|------|---------|
| `0x00854e00` | `g_CVBufTextureList` | Head of linked list of all CVBufTexture instances |
| `0x00854e04` | `g_bDoubleBuffering` | Enable double-buffering (toggle buffer index each frame) |
| `0x00854dec` | `g_bHardwareVP` | Hardware vertex processing enabled flag |
| `0x00854dd8` | `g_bValidateFailed` | ValidateDevice failure flag |
| `0x00854dd9` | `g_bValidateEnabled` | Enable ValidateDevice checks |

## Related Strings

| Address | String | Usage |
|---------|--------|-------|
| `0x00633d40` | `"EnsureLockV failed for %s"` | VB lock failure error |
| `0x00633d80` | `"WARNING: CVBufTexture: no texture, has %d verts left over"` | Orphaned vertices warning |
| `0x00633dbc` | `"WARNING: CVBufTexture %s has %d verts left over"` | Vertices not rendered warning |
| `0x00633df0` | `"WARNING: CVBufTexture: no texture, has %d indices left over"` | Orphaned indices warning |
| `0x00633e2c` | `"WARNING: CVBufTexture %s has %d indices left over"` | Indices not rendered warning |
| `0x00633e60` | `"CVBT: DWATS ValidateDevice failed %s"` | D3D validation error |

## Double-Buffering System

The class supports double-buffering of vertex buffers to allow CPU writes while GPU reads:

1. `mSlots[0x48]` tracks current buffer (0 or 1)
2. `mSlots[0x14]` and `mSlots[0x40]` are arrays of size 2
3. After rendering, `Reset()` toggles the buffer index via XOR: `index ^= 1`
4. Controlled by global `g_bDoubleBuffering` at `0x00854e04`

## Rendering Pipeline

1. **Setup:** `SetVBFormat()` / `SetIBFormat()` configure buffer parameters
2. **Fill:** `AddVertices()` / `AddIndices()` copy geometry data
3. **Render:** `RenderIndexed()` or `RenderNonIndexed()` draw primitives
4. **Reset:** `Reset()` clears cursors and toggles double-buffer

## Dependencies

- **CVBuffer** (vbuffer.cpp) - Low-level D3D vertex buffer wrapper
- **CIBuffer** (likely ibuffer.cpp) - Low-level D3D index buffer wrapper
- **IDirect3DDevice8** - D3D device at `DAT_00888a50`

## Notes

- Buffer sizes grow in powers of 2, starting at 0x400 (1024)
- Hardware VP mode affects buffer creation flags (strips certain usage flags)
- ReleaseAllUnlocked() iterates global list to free unused buffers (for device lost recovery)
- Reference counting prevents premature destruction when texture is reused
