# ibuffer.cpp - Index Buffer System

**Source File:** `C:\dev\ONSLAUGHT2\ibuffer.cpp`
**Debug String Address:** `0x0062d390`
**RTTI Type:** `.?AVCIBuffer@@` at `0x0062d380`
**VTable Address:** `0x005dbec4`

## Overview

CIBuffer is an index buffer wrapper class used for DirectX rendering. It manages GPU index buffers for efficient triangle rendering, supporting both static and dynamic buffer types. The class works alongside CVBuffer (vertex buffer) as part of the rendering pipeline.

## Class Structure

Based on member access patterns in decompiled code:

| Offset | Type | Member | Notes |
|--------|------|--------|-------|
| 0x00 | void* | vtable | Points to 0x005dbec4 |
| 0x08 | IDirect3DIndexBuffer8* | m_pBuffer | D3D index buffer interface |
| 0x0C | int | m_size | Buffer size in bytes |
| 0x10 | DWORD | m_flags | Usage/creation flags |
| 0x14 | int | m_format | Index format (0x65 = D3DFMT_INDEX16) |
| 0x18 | int | m_type | 0=static, 1=dynamic |
| 0x1C | void* | m_pSystemCopy | System memory copy (for shadow buffers) |
| 0x20 | bool | m_bLocked | Lock state flag |

## VTable Layout (0x005dbec4)

| Index | Address | Function |
|-------|---------|----------|
| 0 | 0x00488270 | CIBuffer__ScalarDeletingDestructor |
| 1 | 0x00488460 | CIBuffer__CreateDynamic (not a function in Ghidra) |
| 2 | 0x004884f0 | CIBuffer__CreateStatic (not a function in Ghidra) |
| 3 | 0x00488520 | CIBuffer__ReleaseStatic |
| 4 | 0x00488550 | CIBuffer__ReleaseDynamic |
| 5 | 0x006142f8 | purecall (placeholder) |
| 6 | 0x004886a0 | CImageLoader__ScalarDeletingDestructor (wrong class - shared vtable?) |

## Functions (11 total)

### CIBuffer__Constructor
- **Address:** `0x00488210`
- **Signature:** `void __thiscall CIBuffer__Constructor(CIBuffer* this)`
- **Purpose:** Initializes a new CIBuffer instance
- **Details:**
  - Sets vtable pointer to 0x005dbec4
  - Clears m_pBuffer (offset 0x08)
  - Initializes m_pSystemCopy to NULL
  - Sets m_bLocked to false

### CIBuffer__ScalarDeletingDestructor
- **Address:** `0x00488270`
- **Signature:** `void __thiscall CIBuffer__ScalarDeletingDestructor(CIBuffer* this, byte flags)`
- **Purpose:** VTable destructor for delete operator
- **Details:**
  - Calls CIBuffer__Destructor
  - If flags & 1, frees object memory via operator delete

### CIBuffer__Destructor
- **Address:** `0x00488290`
- **Signature:** `void __thiscall CIBuffer__Destructor(CIBuffer* this)`
- **Purpose:** Clean up index buffer resources
- **Details:**
  - Sets vtable pointer (defensive)
  - Releases D3D index buffer via COM Release()
  - Frees system memory copy if allocated
  - Handles both static (type 0) and dynamic (type 1) buffers

### CIBuffer__Destructor_thunk
- **Address:** `0x0048e350`
- **Signature:** `void __thiscall CIBuffer__Destructor_thunk(CIBuffer* this)`
- **Purpose:** Thunk function that jumps to CIBuffer__Destructor
- **Details:**
  - Simple JMP to 0x00488290
  - Likely used for different calling contexts

### CIBuffer__Create
- **Address:** `0x00488380`
- **Signature:** `int __thiscall CIBuffer__Create(CIBuffer* this, int numIndices)`
- **Purpose:** Create and initialize an index buffer
- **Debug Reference:** Uses `ibuffer.cpp` debug string at line 0x36 (54)
- **Details:**
  - Allocates system memory copy (numIndices * 2 bytes for 16-bit indices)
  - Stores buffer size at offset 0x0C
  - Sets format to 0x65 (D3DFMT_INDEX16)
  - Sets type to 1 (dynamic)
  - Calls D3D device CreateIndexBuffer via vtable
  - Uses assertion check for success (line 0xd2 = 210)

### CIBuffer__CreateConfigured
- **Address:** `0x00488330`
- **Signature:** `int __thiscall CIBuffer__CreateConfigured(void* this, void* pBuffer, int flags, int format, int type, int callerLine)`
- **Purpose:** Generic configured create path used by non-default callers.
- **Details:**
  - Writes caller-provided buffer pointer/flags/format/type into CIBuffer fields.
  - Dispatches to vtable create routine:
    - `type == 1` -> dynamic create slot
    - otherwise -> static create slot
  - Performs localized fatal check on HRESULT (same assert line used by Create path).

### CIBuffer__GetEntryHeightByOwnerSlot
- **Address:** `0x00488aa0`
- **Signature:** `double __thiscall CIBuffer__GetEntryHeightByOwnerSlot(void* this, int owner, int unused)`
- **Purpose:** Read per-entry height scalar from CIBuffer-owned entry table by owner slot index.
- **Details:**
  - Resolves slot index from `owner` via virtual call at `owner->vtable[0x6c/4]`.
  - Returns float at `this->entry_table[slot].height` (`entry stride = 0x18`).
  - Used by `CDXTrees__BuildTreeGeometry` for billboard/tree geometry placement.

### CIBuffer__Unlock
- **Address:** `0x004883f0`
- **Signature:** `int __thiscall CIBuffer__Unlock(CIBuffer* this)`
- **Purpose:** Unlock index buffer after CPU modification
- **Details:**
  - If buffer is NULL, returns 0
  - If m_bLocked is false, calls D3D Unlock directly
  - If using shadow buffer (m_bLocked true):
    - Clears m_bLocked flag
    - Locks D3D buffer
    - Copies from system memory to GPU buffer
    - Unlocks D3D buffer
  - Returns HRESULT from D3D operations

### CIBuffer__ReleaseStatic
- **Address:** `0x00488520`
- **Signature:** `int __thiscall CIBuffer__ReleaseStatic(CIBuffer* this)`
- **Purpose:** Release static index buffer resources
- **Details:**
  - Only acts if m_type == 0 (static)
  - Calls COM Release on D3D buffer
  - Clears buffer pointer

### CIBuffer__ReleaseDynamic
- **Address:** `0x00488550`
- **Signature:** `int __thiscall CIBuffer__ReleaseDynamic(CIBuffer* this)`
- **Purpose:** Release dynamic index buffer resources
- **Details:**
  - Only acts if m_type == 1 (dynamic)
  - Calls COM Release on D3D buffer
  - Clears buffer pointer

### CIBuffer__Lock
- **Address:** `0x00488580`
- **Signature:** `int __thiscall CIBuffer__Lock(CIBuffer* this, void** ppData)`
- **Purpose:** Lock index buffer for CPU access
- **Details:**
  - If system copy exists (shadow buffer mode):
    - Returns pointer to system copy
    - Sets m_bLocked to true
    - Returns S_OK (0)
  - Otherwise locks D3D buffer directly:
    - Uses D3DLOCK_NOOVERWRITE (0x800) normally
    - Uses D3DLOCK_DISCARD | D3DLOCK_NOOVERWRITE (0x2800) if flag 0x200 set

## Usage Pattern

Index buffers are used in conjunction with vertex buffers for rendering. Example from CFastVB__Render:

```cpp
// Create index buffer for quad rendering
CIBuffer__Create(ibuffer, 0x1d4c);  // 7500 indices

// Lock and fill with quad indices
CIBuffer__Lock(ibuffer, &pData);
for (int i = 0; i < numQuads; i++) {
    // Triangle 1: 0, 1, 2
    *pData++ = i*4 + 0;
    *pData++ = i*4 + 1;
    *pData++ = i*4 + 2;
    // Triangle 2: 2, 3, 0
    *pData++ = i*4 + 2;
    *pData++ = i*4 + 3;
    *pData++ = i*4 + 0;
}
CIBuffer__Unlock(ibuffer);
```

## Related Systems

- **CVBuffer** (`vbuffer.cpp`) - Vertex buffer counterpart
- **CFastVB** (`FastVB.cpp`) - Fast vertex buffer system that uses CIBuffer
- **Rendering Pipeline** - Uses index buffers for DrawIndexedPrimitive calls

## Technical Notes

1. **Shadow Buffer Pattern**: CIBuffer supports a shadow buffer mode where index data is kept in system memory. This allows faster CPU access for frequently updated buffers.

2. **Index Format**: Uses D3DFMT_INDEX16 (0x65) - 16-bit indices supporting up to 65535 vertices per draw call.

3. **Lock Flags**:
   - D3DLOCK_NOOVERWRITE (0x800) - Promise not to overwrite existing data
   - D3DLOCK_DISCARD (0x2000) - Discard entire buffer contents

4. **Static vs Dynamic**: Type 0 (static) for infrequently changed data, Type 1 (dynamic) for per-frame updates.

## Cross-References

Functions calling CIBuffer methods:
- `CFastVB__Render` (0x0051a510) - Creates and fills index buffer for quad rendering
- `FUN_0053a5e0` (0x0053a5e0) - Unknown renderer function
- `CVBufTexture__ResizeIndexBuffer` (0x005007f0) - Uses `CIBuffer__CreateConfigured` for runtime-resized IB allocation
- `CDXLandscape__Init` (0x00544af0) - Uses `CIBuffer__CreateConfigured` for landscape index buffer setup
- `CDXTrees__BuildTreeGeometry` (0x0055a420) - Uses `CIBuffer__GetEntryHeightByOwnerSlot` for tree-card placement

## Analysis Status

- [x] All functions identified (9 total)
- [x] Functions renamed in Ghidra
- [x] VTable documented
- [x] Class structure inferred
- [ ] Complete parameter types (partial)
- [ ] Member variable names verified against source
