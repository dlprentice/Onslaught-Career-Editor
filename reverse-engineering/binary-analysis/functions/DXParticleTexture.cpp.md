# DXParticleTexture.cpp Function Mappings

> Debug path: `[maintainer-local-source-export-root]\DXParticleTexture.cpp` (0x00651dcc)
> Functions found: 8
> Last updated: 2026-05-20

## Overview

DXParticleTexture is a DirectX rendering class that manages particle system textures and their associated vertex/index buffers. It maintains a global linked list of particle texture objects for efficient batch rendering and resource management.

## Wave612 Read-Back Status

Wave612 saved Ghidra signatures/comments/tags for the four engine-side particle texture helpers and the nine DXParticleTexture global/object helpers:

| Address | Saved Ghidra state | Evidence summary |
| --- | --- | --- |
| `0x0054f6e0` | `void __fastcall CDXEngine__ShutdownParticleSystemBundle(void * particle_bundle)` | Callsite `0x0054f6d5` jumps here with ECX set to particle bundle `0x009c63e8`; body destroys particles, clears particle-manager owner links, shuts down manager storage, and frees the manager. |
| `0x0054f740` | `void __fastcall CDXEngine__ResetParticleSystemBundle(void * particle_bundle)` | Callsite `0x0054f6b5` reaches the reset helper; body clears bundle fields at `+0x00/+0x04/+0x08/+0x0c/+0x18`. |
| `0x0054f760` | `void __cdecl CDXEngine__SetParticleRenderStatePreset(void)` | Callsite `0x004c8fba` invokes this no-argument render-state preset before particle texture drawing. |
| `0x0054f7e0` | `void __fastcall CDXEngine__RenderParticleTexturePass(void * particle_bundle)` | `CDXEngine__Render` callsite `0x0053ebe3` and frontend matrix setup callsite `0x00540f55` set ECX to bundle `0x009c63e8`; body calls `DXParticleTexture__RenderAll` at `0x0054f9ec`. |
| `0x0054fbc0` | `void * __cdecl DXParticleTexture__GetOrCreate(char * texture_path, int texture_type)` | `CParticleDescriptor__Load` callsite `0x004c57b9` pushes path/type, calls, cleans `0x8`, and stores the returned node pointer. The body scans `DAT_009c64d0`, allocates `0x1a4` bytes when absent, configures CTexture/CVBufTexture, and links the node. |
| `0x0054fd80` | `void __cdecl DXParticleTexture__ReleaseAll(void)` | Device/reset callsite `0x00512c1d`; body walks `DAT_009c64d0`, releases node resources at `+0x194/+0x198`, and releases/nulls `DAT_009c6468`. |
| `0x0054fde0` | `void __cdecl DXParticleTexture__RestoreAll(void)` | Device-restore callsite `0x0051290e`; body recreates CTexture/CVBufTexture resources and conditionally creates particle shaders including `s_particleshader_00651ed0`. |
| `0x0054fee0` | `void __cdecl DXParticleTexture__DestroyAll(void)` | Teardown callsites `0x0046923c` and `0x0046c9c5`; body walks `DAT_009c64d0`, calls `DXParticleTexture__Release`, frees nodes, and clears the global list. |
| `0x0054ff20` | `void __cdecl DXParticleTexture__RenderAll(void)` | Called by `CDXEngine__RenderParticleTexturePass` at `0x0054f9ec` and the particle render path at `0x004c8cb3`; body sets render/shader state and calls `DXParticleTexture__Render` for every list node. |
| `0x00550110` | `void __thiscall DXParticleTexture__Release(void * this)` | `DXParticleTexture__DestroyAll` callsite `0x0054fefd` passes the current node in ECX before freeing it. |
| `0x00550180` | `void __thiscall DXParticleTexture__AddTriangleIndices(void * this, ushort index0, ushort index1, ushort index2)` | Six particle sprite/descriptor callsites prove ECX plus three 16-bit indices and `RET 0x0c`; body writes three index words from `CVBufTexture__GetIndexPtr(this+0x198, 3)`. |
| `0x005501b0` | `void * __thiscall DXParticleTexture__GetIndexBuffer(void * this, int index_count)` | `CPDSimpleSprite__ProcessAndRenderSpriteList` callsite `0x004c782c` uses EAX as the writable index-buffer pointer returned from `CVBufTexture__GetIndexPtr`. |
| `0x00550220` | `void __thiscall DXParticleTexture__Render(void * this)` | `DXParticleTexture__RenderAll` callsite `0x00550082` passes each global-list node in ECX; body resolves texture frame, sets blend mode from node type `+0x190`, resets batch index `+0x19c`, and renders the CVBufTexture. |

Read-back evidence: `ApplyParticleTextureBundleWave612.java` dry/apply/final dry reported `updated=0 skipped=13 renamed=0 would_rename=0 missing=0 bad=0`, then `updated=13 skipped=0 renamed=0 would_rename=0 missing=0 bad=0`, then `updated=0 skipped=13 renamed=0 would_rename=0 missing=0 bad=0`, with `REPORT: Save succeeded`. Post exports verified `13` metadata rows, `13` tag rows, `23` xref rows, `3393` instruction rows, `13` decompile rows, and `667` callsite instruction rows.

Queue telemetry after the pass: `6093` total, `3147` commented, `2946` commentless, `1283` exact-undefined signatures, `1056` `param_N`, comment-backed proxy `3147/6093 = 51.65%`, strict clean-signature proxy `3102/6093 = 50.91%`. Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260519-234626_post_wave612_particle_texture_verified`, `19` files, `161581959` bytes, `DiffCount=0`. Next queue head: `0x00550380 CDXPatch__Constructor`.

This is static saved-Ghidra evidence only. Exact particle bundle, DXParticleTexture, CParticleDescriptor, CTexture, CVBufTexture, shader/global, and render-state layouts, runtime particle output, BEA patching, and rebuild parity remain unproven.

## Class Structure

### Object Size

- Size: 0x1a4 bytes (420 bytes)
- Allocated via OID__AllocObject with object type 0x23

### Global Linked List

- Head pointer: `DAT_009c64d0` (0x009c64d0)
- Objects linked via offset 0x1a0 (next pointer)

### Member Offsets

| Offset | Type | Name | Notes |
|--------|------|------|-------|
| 0x00 | char[200] | m_szFullPath | Full texture path (copied from param) |
| 0xC8 (200) | char[200] | m_szShortName | Short name (filename after last backslash) |
| 0x190 (400) | int | m_nType | Texture type (param_2: 1=?, 2=?, 3=?) |
| 0x194 | CTexture* | m_pTexture | Texture object from CTexture__FindTexture |
| 0x198 | CVBufTexture* | m_pVBufTexture | Vertex buffer texture from CVBufTexture__GetOrCreate |
| 0x19C | int | m_nLastBatchIndex | Last batch index (reset to -1 each render) |
| 0x1a0 | DXParticleTexture* | m_pNext | Next in global linked list |

## Functions

### DXParticleTexture__GetOrCreate (0x0054fbc0)

**Signature:** `DXParticleTexture* DXParticleTexture__GetOrCreate(char* texturePath, int textureType)`

Factory function that retrieves an existing particle texture or creates a new one. Implements a cache pattern using a global linked list.

**Key Operations:**
1. Iterates through linked list at DAT_009c64d0
2. For each node, compares texturePath (case-insensitive) and textureType
3. If found, returns existing object
4. If not found:
   - Allocates 0x1a4 bytes via OID__AllocObject
   - Initializes all fields to 0
   - Sets m_nLastBatchIndex to -1 (0xFFFFFFFF)
   - Copies full path to offset 0x00
   - Copies short name (after last '\\') to offset 0xC8
   - Determines texture format based on type (2 or 5)
   - Calls CTexture__FindTexture to get texture
   - Calls CVBufTexture__GetOrCreate for vertex buffer
   - Sets VB format: 0x142, 8 entries, stride 0x18, 4 components
   - Sets IB format: 0x65, 8 entries, stride 2
   - Adds to head of linked list
5. Returns pointer to object

**Called by:**
- CParticleDescriptor (0x004c0682, 0x004c3185)
- CParticleDescriptor__Load (0x004c57b9)

---

### DXParticleTexture__ReleaseAll (0x0054fd80)

**Signature:** `void DXParticleTexture__ReleaseAll(void)`

Releases GPU resources for all particle textures without destroying the objects. Called during device lost scenarios.

**Key Operations:**
1. Iterates through linked list at DAT_009c64d0
2. For each object:
   - If m_pTexture (0x194) exists, releases it via CTexture__DecrementRefCountFromNameField, sets to NULL
   - If m_pVBufTexture (0x198) exists, releases it via FUN_00501310, sets to NULL
3. Cleans up pixel shader at DAT_009c6468 via FUN_00514010

**Called from:** Device reset handler (0x00512c1d)

---

### DXParticleTexture__RestoreAll (0x0054fde0)

**Signature:** `void DXParticleTexture__RestoreAll(void)`

Restores GPU resources for all particle textures after device reset. Recreates textures and shaders.

**Key Operations:**
1. Logs "CPT__RAS__" marker via `CConsole__Printf` (`FUN_00441740`)
2. Iterates through linked list at DAT_009c64d0
3. For each object:
   - Determines texture format (2 or 5) based on type
   - Calls CTexture__FindTexture with path at this+0x20
   - Calls CVBufTexture__GetOrCreate
   - Sets VB format: 0x142, 0x208 entries, stride 0x18, 4 components
   - Sets IB format: 0x65, 0x208 entries, stride 2
4. If DAT_009c648c and hardware supports (DAT_00888b20 > 0xffff01ff):
   - Creates vertex shader "particleshader" at DAT_009c646c
   - Creates pixel shader with ps_2_0 code at DAT_009c6468
5. Logs "CPT__RAS___end" marker

**Called from:** Device restore handler (0x0051290e)

---

### DXParticleTexture__DestroyAll (0x0054fee0)

**Signature:** `void DXParticleTexture__DestroyAll(void)`

Destroys all particle texture objects and frees memory. Called during shutdown.

**Key Operations:**
1. While linked list head (DAT_009c64d0) is not NULL:
   - Gets current head
   - Gets next pointer from offset 0x1a0
   - Calls DXParticleTexture__Release to release GPU resources
   - Frees object memory via OID__FreeObject
   - Updates head to next
2. Sets DAT_009c64d0 to NULL

**Called from:**
- Shutdown handler (0x0046923c)
- Level unload (0x0046c9c5)

---

### DXParticleTexture__RenderAll (0x0054ff20)

**Signature:** `void DXParticleTexture__RenderAll(void)`

Main render function that draws all particle textures with optional shader support.

**Key Operations:**
1. Saves linked list head
2. Sets render state `0x1b` to `1` via `RenderState_Set` (`0x00513bc0`)
3. Clears DAT_009c64d4 flag
4. Checks various conditions (`CGame__IsMultiplayer`, FUN_00515970)
5. If shader rendering enabled:
   - Sets pixel shader (DAT_009c6468) via D3D call (vtable+0x1ac)
   - Sets vertex shader (DAT_009c646c) via FUN_00513e20
   - Configures texture sampler state at slot 1
   - Sets various render states (6, 5, 7, 10)
   - Sets DAT_009c64d4 flag to 1
6. Iterates through all particle textures:
   - Calls DXParticleTexture__Render for each
7. Restores render states
8. Clears pixel shader (sets to 0)
9. Sets render state 0x1b to 0

**Called from:**
- Particle system render (0x004c8cb3)
- Alternative particle render (0x0054f9ec)

---

### DXParticleTexture__Release (0x00550110)

**Signature:** `void __thiscall DXParticleTexture__Release(void)`

Instance method that releases GPU resources for a single particle texture.

**Key Operations:**
1. Sets up exception handler
2. If m_pTexture (0x194) exists:
   - Releases via CTexture__DecrementRefCountFromNameField
   - Sets to NULL
3. If m_pVBufTexture (0x198) exists:
   - Releases via FUN_00501310
   - Sets to NULL

**Called from:** DXParticleTexture__DestroyAll (0x0054fee0)

---

### DXParticleTexture__AddTriangleIndices (0x00550180)

**Signature:** `void __thiscall DXParticleTexture__AddTriangleIndices(short i0, short i1, short i2)`

Adds three indices for a triangle to the index buffer.

**Key Operations:**
1. Gets CVBufTexture from this+0x198
2. Calls CVBufTexture__GetIndexPtr(3) to get pointer for 3 indices
3. Writes indices i0, i1, i2 as shorts

**Called from:** Multiple particle rendering locations (0x004c8bec, 0x004c8c05, 0x004ca201, etc.)

---

### DXParticleTexture__GetIndexBuffer (0x005501b0)

**Signature:** `void* __thiscall DXParticleTexture__GetIndexBuffer(int count)`

Gets a pointer to index buffer space for the specified number of indices.

**Key Operations:**
1. Gets CVBufTexture from this+0x198
2. Calls CVBufTexture__GetIndexPtr(count)
3. Returns pointer (result discarded in wrapper, likely inlined)

**Called from:** Particle batch rendering (0x004c782c)

---

### DXParticleTexture__Render (0x00550220)

**Signature:** `void __thiscall DXParticleTexture__Render(void)`

Instance method that renders this particle texture's geometry.

**Key Operations:**
1. Returns early if m_pVBufTexture (0x198) is NULL
2. Gets texture surface via FUN_00558690
3. Sets texture at slot 0 via FUN_00513a50
4. Based on texture type (m_nType at offset 400):
   - Type 1: Sets blend mode (0x13=2, 0x14=2)
   - Type 2: Sets blend mode (0x13=5, 0x14=6)
   - Type 3: Sets blend mode (0x13=2, 0x14=6)
5. Resets m_nLastBatchIndex to -1
6. Renders indexed geometry:
   - If DAT_009c64d4 (shader mode): CVBufTexture__RenderIndexedNoValidate
   - Otherwise: CVBufTexture__RenderIndexed

**Called from:** DXParticleTexture__RenderAll (0x0054ff20) loop

## Related Strings

| Address | String | Usage |
|---------|--------|-------|
| 0x00651dcc | "[maintainer-local-source-export-root]\DXParticleTexture.cpp" | Debug path |
| 0x00651ed0 | "particleshader" | Vertex shader name |
| 0x00651ee0 | "vs_1_1 dcl_position v0 dcl_texco..." | Vertex shader source |
| 0x00651e04 | "ps_2_0 dcl_2d s0 dcl_2d s1 dcl_v..." | Pixel shader source |
| 0x00652110 | "CPT__RAS__" | RestoreAll start marker |
| 0x00651df4 | "CPT__RAS___end" | RestoreAll end marker |
| 0x00651db4 | "GEFORCE_PARTICLE_FOG" | Hardware capability string |

## Related Globals

| Address | Type | Name | Notes |
|---------|------|------|-------|
| 0x009c64d0 | DXParticleTexture* | g_pParticleTextureList | Linked list head |
| 0x009c64d4 | char | g_bShaderMode | Shader rendering enabled flag |
| 0x009c6468 | void* | g_pPixelShader | Pixel shader handle |
| 0x009c646c | void* | g_pVertexShader | Vertex shader handle |
| 0x009c648c | int | g_bUseShaders | Shader support flag |
| 0x009c647c | int | DAT_009c647c | Unknown render flag |
| 0x00888b20 | int | DAT_00888b20 | Hardware capability bits |
| 0x00854dec | int | DAT_00854dec | Unknown hardware flag |
| 0x0089c9b0 | void* | DAT_0089c9b0 | Texture manager/device |
| 0x00888a50 | void* | DAT_00888a50 | D3D device pointer |

## Related Functions (External)

| Address | Name | Purpose |
|---------|------|---------|
| 0x004f27e0 | CTexture__DecrementRefCountFromNameField | Release CTexture refcount helper |
| 0x00501310 | FUN_00501310 | Release CVBufTexture |
| 0x00514010 | FUN_00514010 | Release pixel shader |
| 0x00513f20 | FUN_00513f20 | Create pixel shader |
| 0x00513e20 | FUN_00513e20 | Set vertex shader |
| 0x00513bc0 | RenderState_Set | Cached render-state setter |
| 0x00513930 | FUN_00513930 | Set sampler state |
| 0x00513a50 | FUN_00513a50 | Set texture |
| 0x00549220 | OID__FreeObject | Free object memory |
| 0x00558690 | FUN_00558690 | Get texture surface |
| 0x00568390 | stricmp (`FUN_00568390`) | Case-insensitive string compare |
| 0x00441740 | CConsole__Printf (`FUN_00441740`) | Debug log marker |
| 0x004725d0 | CGame__IsMultiplayer | Check multiplayer/current-level render condition |
| 0x00515970 | FUN_00515970 | Check render pass |

## Texture Type Meanings

| Type | Blend Source | Blend Dest | Usage |
|------|-------------|------------|-------|
| 1 | 2 (SRC_ALPHA) | 2 (ONE) | Additive particles |
| 2 | 5 (SRC_ALPHA) | 6 (INV_SRC_ALPHA) | Standard alpha blend |
| 3 | 2 (SRC_ALPHA) | 6 (INV_SRC_ALPHA) | Mixed blend mode |

## Architecture Notes

1. **Factory Pattern**: GetOrCreate implements a factory with caching via linked list
2. **Device Lost Handling**: ReleaseAll/RestoreAll pattern for D3D device reset
3. **Batch Rendering**: Multiple particles share textures, rendered in batches
4. **Shader Support**: Optional pixel/vertex shaders for enhanced effects (ps_2_0, vs_1_1)
5. **Memory Management**: Uses OID__AllocObject/OID__FreeObject for allocation
6. **String Storage**: Full path and short name stored for texture lookup

## Relationship to Other Classes

```
CParticleManager
  |
  +-- CParticleDescriptor
        |
        +-- DXParticleTexture (via GetOrCreate)
              |
              +-- CTexture (m_pTexture)
              +-- CVBufTexture (m_pVBufTexture)
```
