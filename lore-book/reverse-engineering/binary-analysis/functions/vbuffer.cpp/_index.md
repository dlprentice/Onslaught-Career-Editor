# vbuffer.cpp - Vertex Buffer Management

**Source File:** `C:\dev\ONSLAUGHT2\vbuffer.cpp`
**Debug String Address:** `0x00633d08`
**RTTI Class Name:** `.?AVCVBuffer@@` at `0x00633cf8`

> **Queue status (2026-05-26):** Ghidra export-contract closure **6113/6113** (Wave900: every function commented; clean-signature proxy; not evidence-grade semantics). Lines below that reference a "next raw commentless" row are **archival wave progress**, not open work.

## Overview

CVBuffer (Vertex Buffer) manages GPU vertex data for 3D rendering. This is a core component of the rendering system that wraps Direct3D vertex buffer interfaces. The class handles creation, locking/unlocking, and streaming of vertex data to the GPU.

Wave529 is the current saved Ghidra state for the `0x004fff00..0x00500390` CVBuffer tail. It corrected stale ctor/dtor labels, hardened signatures/comments/tags for the lifecycle/create/lock/release/stream helpers, and recovered `CVBuffer__CreateDefaultPoolVertexBuffer` at `0x00500250` from CVBuffer vtable slot 2 (`0x005dfb94`) plus the derived DXPatch-style slot (`0x005e511c`). This remains static retail evidence only; runtime rendering/device-loss behavior and rebuild parity are not proven by the wave.

Wave904 (`texture-render-static-review-wave904`) includes CVBuffer/CIBuffer in the `static-coherent texture/resource/decode/render core` after export-contract queue closure `6113/6113 = 100.00%` (static review slice only). The reviewed slice covers `1289` rows across `25` selected families, including `CDXTexture` `366`, `CFastVB` `347`, `CTexture` `233`, and `CVBufTexture` `40`; buffer/render anchors include `CVBuffer__Create`, `CIBuffer__CreateConfigured`, `CDXTexture__LoadTextureFromFile_Core`, `CDXTexture__DecodeMemoryToTextureObject`, `CDXTexture__ValidateJpegFrameAndComputeMcuLayout`, `CFastVB__RenderTriangleStripImmediate`, and `CVBufTexture__DrawSpriteEx`. Asset bridge counts include `847/847` loose textures and `352/352` model material/texture-binding rows. Verified backup: `G:\GhidraBackups\BEA_20260526-101300_post_wave904_texture_render_static_review_verified`.

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

## Functions (16 current Wave529 targets)

| Address | Name | Description |
|---------|------|-------------|
| `0x004fff00` | CVBuffer__ctor_base | Constructor/base initializer; installs CVBuffer vtable and clears D3D/backing/dirty state |
| `0x004fff60` | CVBuffer__scalar_deleting_dtor | Scalar-deleting destructor wrapper in vtable slot 0 |
| `0x004fff80` | CVBuffer__dtor_base | Destructor body; releases D3D buffer and backing storage before base teardown |
| `0x005000c0` | CVBuffer__Create | Create vertex buffer with system memory allocation |
| `0x00500020` | CVBuffer__CreateInternal | Internal creation helper, calls D3D CreateVertexBuffer |
| `0x00500080` | CVBuffer__CreateDynamic | Create dynamic vertex buffer (D3DUSAGE_DYNAMIC) |
| `0x00500120` | CVBuffer__Restore | Restore buffer after device reset |
| `0x005001b0` | CVBuffer__Lock | Lock buffer for CPU write access |
| `0x005001e0` | CVBuffer__Unlock | Unlock buffer, sync to GPU if dirty |
| `0x00500250` | CVBuffer__CreateDefaultPoolVertexBuffer | Recovered default-pool vtable slot 2 boundary |
| `0x00500280` | CVBuffer__Release | Release non-managed buffer resources |
| `0x005002b0` | CVBuffer__ReleaseManaged | Release managed buffer resources |
| `0x005002e0` | CVBuffer__EnsureLock | Ensure buffer is locked, handles D3DLOCK flags |
| `0x00500320` | CVBuffer__SetStreamSource | Set as active vertex stream (updates globals) |
| `0x00500360` | CVBuffer__SetStreamSourceSimple | Set as active vertex stream (simple version) |
| `0x00500390` | CVBuffer__LockRange | Lock a specific range of the buffer |

## Function Details

### CVBuffer__ctor_base (0x004fff00)
```c
void *CVBuffer__ctor_base(void *this)
```
Installs the CVBuffer vtable at `0x005dfb8c`, clears the D3D vertex-buffer pointer at `+0x08`, initializes the shader/device-object base path through `CShaderBase__Init`, and clears backing storage `+0x24` plus dirty byte `+0x28`.

### CVBuffer__scalar_deleting_dtor (0x004fff60)
```c
void *CVBuffer__scalar_deleting_dtor(void *this, byte flags)
```
Vtable slot 0 wrapper. Calls `CVBuffer__dtor_base` and frees the object through `CDXMemoryManager__Free` when `flags & 1` is set.

### CVBuffer__dtor_base (0x004fff80)
```c
void CVBuffer__dtor_base(void *this)
```
Restores the CVBuffer vtable, runs the base unlink/destruction helper, releases D3D vertex-buffer state for mode `0` or `1`, clears `+0x08` and `+0x28`, frees backing storage `+0x24`, and runs the base device-object teardown path.

### CVBuffer__Create (0x005000c0)
```c
bool CVBuffer__Create(void *this, int vertex_count, int vertex_stride, int fvf_format)
```
Creates a vertex buffer with system memory allocation for backup. Allocates `numVertices * stride` bytes via memory manager. Sets `m_bManaged = 1` and creates buffer in managed pool.

**Parameters:**
- `numVertices`: Number of vertices to allocate
- `stride`: Bytes per vertex
- `fvf`: Flexible Vertex Format flags

**Returns:** true on success, false on failure

### CVBuffer__CreateInternal (0x00500020)
```c
int CVBuffer__CreateInternal(void *this, int total_bytes, int usage_flags, int fvf_format, int pool_mode)
```
Internal helper that calls Direct3D `CreateVertexBuffer`. Chooses between managed pool (vtable+4) or default pool (vtable+8) based on pool parameter.

### CVBuffer__CreateDynamic (0x00500080)
```c
bool CVBuffer__CreateDynamic(void *this, int vertex_count, int vertex_stride, int fvf_format)
```
Creates a dynamic vertex buffer using `D3DUSAGE_DYNAMIC` (0x208). Dynamic buffers are faster for frequently-updated vertex data. Uses default pool (non-managed).

### CVBuffer__Restore (0x00500120)
```c
int CVBuffer__Restore(void *this)
```
Restores the vertex buffer after a device reset (e.g., alt-tab, resolution change). Only acts if `m_bManaged == 1`. Recreates the D3D buffer and copies data from system memory backup.

### CVBuffer__Lock (0x005001b0)
```c
int CVBuffer__Lock(void *this, void **out_data)
```
Locks the buffer for CPU write access. If system memory copy exists, returns that pointer directly and sets dirty flag. Otherwise calls D3D Lock with `D3DLOCK_NOSYSLOCK` (0x800).

### CVBuffer__Unlock (0x005001e0)
```c
int CVBuffer__Unlock(void *this)
```
Unlocks the buffer. If dirty flag is set, copies system memory to GPU buffer first. Handles the memcpy with optimized 4-byte copies.

### CVBuffer__CreateDefaultPoolVertexBuffer (0x00500250)
```c
int CVBuffer__CreateDefaultPoolVertexBuffer(void *this)
```
Recovered by Wave529 from CVBuffer vtable slot 2 and a derived DXPatch-style vtable slot. Returns `0` when `m_bManaged`/pool mode is nonzero; otherwise calls the Direct3D create wrapper with pool token `0`, stores the interface at `+0x08`, and returns `0x80004005` on failure or `0` on success.

### CVBuffer__Release (0x00500280)
```c
int CVBuffer__Release(void *this)
```
Releases resources for non-managed buffers (`m_bManaged == 0`). Calls helper function to release D3D interface and clears pointers.

### CVBuffer__ReleaseManaged (0x005002b0)
```c
int CVBuffer__ReleaseManaged(void *this)
```
Releases resources for managed buffers (`m_bManaged == 1`). Same cleanup as Release but checks managed flag.

### CVBuffer__EnsureLock (0x005002e0)
```c
int CVBuffer__EnsureLock(void *this, void **out_data)
```
Ensures buffer is locked, with appropriate D3DLOCK flags. Checks usage flags for `D3DUSAGE_WRITEONLY` (0x200) and uses `D3DLOCK_DISCARD` (0x2000) for dynamic buffers.

### CVBuffer__SetStreamSource (0x00500320)
```c
void CVBuffer__SetStreamSource(void *this, int stream_index)
```
Sets this buffer as the active vertex stream source. Updates global state:
- `DAT_009c73d4` = FVF format
- `DAT_009c741c` = 1 (stream active flag)

Calls D3D `SetStreamSource` via device vtable offset 400.

### CVBuffer__SetStreamSourceSimple (0x00500360)
```c
void CVBuffer__SetStreamSourceSimple(void *this, int stream_index)
```
Simplified version of SetStreamSource without updating global FVF state.

### CVBuffer__LockRange (0x00500390)
```c
int CVBuffer__LockRange(void *this, int offset_bytes, int size_bytes, void **out_data, int lock_flags)
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
