# vbuffer.cpp - Vertex Buffer Management

**Source File:** `C:\dev\ONSLAUGHT2\vbuffer.cpp`
**Debug String Address:** `0x00633d08`
**RTTI Class Name:** `.?AVCVBuffer@@` at `0x00633cf8`

## Overview

CVBuffer (Vertex Buffer) manages GPU vertex data for 3D rendering. This is a core component of the rendering system that wraps Direct3D vertex buffer interfaces. The class handles creation, locking/unlocking, and streaming of vertex data to the GPU.

## Class Structure

The CVBuffer class uses a thiscall convention with `this` pointer in ECX. Based on decompilation analysis:

| Offset | Type | Field | Description |
|--------|------|-------|-------------|
| 0x00 | void* | vtable | Virtual function table pointer |
| 0x08 | IDirect3DVertexBuffer* | m_pVB | Direct3D vertex buffer interface |
| 0x10 | int | m_nSize | Total buffer size in bytes |
| 0x14 | int | m_nUsage | D3D usage flags |
| 0x18 | int | m_nFVF | Flexible Vertex Format |
| 0x1C | int | m_nStride | Vertex stride (bytes per vertex) |
| 0x20 | int | m_bManaged | 1=managed pool, 0=default pool |
| 0x24 | void* | m_pSysMemCopy | System memory backup (for managed buffers) |
| 0x28 | bool | m_bDirty | Needs sync to GPU |

## Functions (11 total)

| Address | Name | Description |
|---------|------|-------------|
| `0x005000c0` | CVBuffer__Create | Create vertex buffer with system memory allocation |
| `0x00500020` | CVBuffer__CreateInternal | Internal creation helper, calls D3D CreateVertexBuffer |
| `0x00500080` | CVBuffer__CreateDynamic | Create dynamic vertex buffer (D3DUSAGE_DYNAMIC) |
| `0x00500120` | CVBuffer__Restore | Restore buffer after device reset |
| `0x005001b0` | CVBuffer__Lock | Lock buffer for CPU write access |
| `0x005001e0` | CVBuffer__Unlock | Unlock buffer, sync to GPU if dirty |
| `0x00500280` | CVBuffer__Release | Release non-managed buffer resources |
| `0x005002b0` | CVBuffer__ReleaseManaged | Release managed buffer resources |
| `0x005002e0` | CVBuffer__EnsureLock | Ensure buffer is locked, handles D3DLOCK flags |
| `0x00500320` | CVBuffer__SetStreamSource | Set as active vertex stream (updates globals) |
| `0x00500360` | CVBuffer__SetStreamSourceSimple | Set as active vertex stream (simple version) |
| `0x00500390` | CVBuffer__LockRange | Lock a specific range of the buffer |

## Function Details

### CVBuffer__Create (0x005000c0)
```c
bool CVBuffer__Create(int numVertices, int stride, int fvf)
```
Creates a vertex buffer with system memory allocation for backup. Allocates `numVertices * stride` bytes via memory manager. Sets `m_bManaged = 1` and creates buffer in managed pool.

**Parameters:**
- `numVertices`: Number of vertices to allocate
- `stride`: Bytes per vertex
- `fvf`: Flexible Vertex Format flags

**Returns:** true on success, false on failure

### CVBuffer__CreateInternal (0x00500020)
```c
int CVBuffer__CreateInternal(int size, int usage, int fvf, int pool)
```
Internal helper that calls Direct3D `CreateVertexBuffer`. Chooses between managed pool (vtable+4) or default pool (vtable+8) based on pool parameter.

### CVBuffer__CreateDynamic (0x00500080)
```c
bool CVBuffer__CreateDynamic(int numVertices, int stride, int fvf)
```
Creates a dynamic vertex buffer using `D3DUSAGE_DYNAMIC` (0x208). Dynamic buffers are faster for frequently-updated vertex data. Uses default pool (non-managed).

### CVBuffer__Restore (0x00500120)
```c
int CVBuffer__Restore(void)
```
Restores the vertex buffer after a device reset (e.g., alt-tab, resolution change). Only acts if `m_bManaged == 1`. Recreates the D3D buffer and copies data from system memory backup.

### CVBuffer__Lock (0x005001b0)
```c
HRESULT CVBuffer__Lock(void** ppData)
```
Locks the buffer for CPU write access. If system memory copy exists, returns that pointer directly and sets dirty flag. Otherwise calls D3D Lock with `D3DLOCK_NOSYSLOCK` (0x800).

### CVBuffer__Unlock (0x005001e0)
```c
int CVBuffer__Unlock(void)
```
Unlocks the buffer. If dirty flag is set, copies system memory to GPU buffer first. Handles the memcpy with optimized 4-byte copies.

### CVBuffer__Release (0x00500280)
```c
void CVBuffer__Release(void)
```
Releases resources for non-managed buffers (`m_bManaged == 0`). Calls helper function to release D3D interface and clears pointers.

### CVBuffer__ReleaseManaged (0x005002b0)
```c
void CVBuffer__ReleaseManaged(void)
```
Releases resources for managed buffers (`m_bManaged == 1`). Same cleanup as Release but checks managed flag.

### CVBuffer__EnsureLock (0x005002e0)
```c
void CVBuffer__EnsureLock(void** ppData)
```
Ensures buffer is locked, with appropriate D3DLOCK flags. Checks usage flags for `D3DUSAGE_WRITEONLY` (0x200) and uses `D3DLOCK_DISCARD` (0x2000) for dynamic buffers.

### CVBuffer__SetStreamSource (0x00500320)
```c
void CVBuffer__SetStreamSource(int streamNumber)
```
Sets this buffer as the active vertex stream source. Updates global state:
- `DAT_009c73d4` = FVF format
- `DAT_009c741c` = 1 (stream active flag)

Calls D3D `SetStreamSource` via device vtable offset 400.

### CVBuffer__SetStreamSourceSimple (0x00500360)
```c
void CVBuffer__SetStreamSourceSimple(int streamNumber)
```
Simplified version of SetStreamSource without updating global FVF state.

### CVBuffer__LockRange (0x00500390)
```c
HRESULT CVBuffer__LockRange(int offset, int size, void** ppData, DWORD flags)
```
Locks a specific range of the buffer. Returns `E_FAIL` (0x80004005) if buffer is null.

## Related Components

- **vbuftexture.cpp** - Texture buffer management (starts at 0x00500540)
- **D3D Device** - Global at `DAT_00888a50`
- **Memory Manager** - `OID__AllocObject` wraps `CMemoryManager__Alloc`

## D3D Constants Used

| Constant | Value | Usage |
|----------|-------|-------|
| D3DUSAGE_DYNAMIC | 0x0200 | Dynamic vertex buffer |
| D3DUSAGE_WRITEONLY | 0x0008 | Write-only access |
| D3DLOCK_NOSYSLOCK | 0x0800 | Don't take system-wide lock |
| D3DLOCK_DISCARD | 0x2000 | Discard entire buffer on lock |
| E_FAIL | 0x80004005 | Generic failure HRESULT |

## Global Variables

| Address | Type | Description |
|---------|------|-------------|
| `0x00888a50` | IDirect3DDevice* | D3D device pointer |
| `0x00854e00` | CVBuffer* | Linked list head of all VBuffers |
| `0x009c73d4` | DWORD | Current stream FVF format |
| `0x009c741c` | DWORD | Stream active flag |

## Notes

1. The CVBuffer class maintains a linked list of all instances via offset 0x58 (next pointer) and global head at `0x00854e00`. This allows bulk operations like device reset handling.

2. Managed buffers keep a system memory copy for restoration after device loss. Non-managed (dynamic) buffers must be refilled by the application.

3. The memory allocation at line 0x53 (83 decimal) in vbuffer.cpp uses memory pool 0x2d (45 decimal) which corresponds to "VBuffer" or "VBufferData" allocations.
