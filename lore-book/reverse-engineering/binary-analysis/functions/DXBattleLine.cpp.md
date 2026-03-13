# DXBattleLine.cpp Function Mappings

> Debug path: `C:\dev\ONSLAUGHT2\DXBattleLine.cpp` (0x00650324)
> Functions found: 10
> Last updated: 2025-12-16

## Overview

CDXBattleLine is a DirectX rendering class that visualizes the "battle line" on the HUD - the tactical map showing territory control and unit positions. It inherits from CTexture and manages mesh generation, heightmap sampling, and multi-pass rendering.

## Class Structure

### Vtable at 0x005e4f64

| Offset | Address | Function | Notes |
|--------|---------|----------|-------|
| 0x00 | 0x0053a120 | scalar_deleting_dtor | Destructor |
| 0x04 | 0x0053a010 | (unknown - not defined) | Possibly base class method |
| 0x08 | 0x0053a040 | (unknown - not defined) | Possibly base class method |
| 0x0C | 0x005572c0 | (CTexture method) | Inherited |
| 0x10 | 0x00558600 | (CTexture method) | Inherited |
| 0x14 | 0x00556e90 | (CTexture method) | Inherited |
| 0x18 | 0x00556fc0 | (CTexture method) | Virtual call in Constructor |
| 0x1C | 0x00405930 | (unknown) | - |
| 0x20 | 0x005593a0 | (unknown) | - |

### Object Size

- Size: 0x158 bytes (344 bytes)
- Allocated via OID__AllocObject with alignment 2

### Member Offsets (Partial)

| Offset | Type | Name | Notes |
|--------|------|------|-------|
| 0x00 | vtable* | vtable | Points to 0x005e4f64 |
| 0x04 | CTexture* | m_pBaseTexture | Line/gradient texture |
| 0x08 | CTexture* | m_pOverlayTexture | Created in LoadTextures |
| 0x0C | CTexture* | m_pMarkerTexture | "hud\marker.tga" |
| 0x14 | CTexture* | m_pBEMarkerTexture | "hud\V2\BattleEngineMarker.tga" |
| 0x18 | int | m_nBaseOffset | Base offset for vertex data |
| 0x1C | CIBuffer* | m_pIndexBuffer | Index buffer for mesh |
| 0x20 | int | m_nTriCount | Triangle count from mesh |
| 0x24 | byte | m_nState | State (2 = ready for rendering) |
| 0x48 | float | m_fScaleX | X scale for marker positioning |
| 0x4C | float | m_fScaleY | Y scale for marker positioning |
| 0x50 | float | m_fOffsetX | X offset for marker positioning |
| 0x54 | float | m_fOffsetY | Y offset for marker positioning |
| 0x5C | int | m_nUnknown5C | Set to 0 in LoadTextures |
| 0x64 | int | param_1 | Constructor param |
| 0x68 | int | param_2 | Constructor param |
| 0x70 | CVBuffer* | m_pVertexBuffer | Vertex buffer for markers |
| 0x74 | ? | m_pRenderTarget | Render target reference |
| 0x78 | CVBuffer* | m_pDynamicVB | 500-vertex dynamic buffer |
| 0x1C (obj) | int | m_nVertexCount | Vertex count from mesh |
| 0x1D (obj) | CIBuffer* | m_pMeshIB | Mesh index buffer |

## Functions

### CDXBattleLine__Constructor (0x0053a050)

**Signature:** `void __thiscall CDXBattleLine__Constructor(int param_1, int param_2)`

Constructor that initializes the battle line object. Creates a CTexture for the line rendering (128x128 or 128x1 based on hardware flags).

**Key Operations:**
1. Stores param_1 at offset 0x64, param_2 at offset 0x68
2. Allocates CTexture via OID__AllocObject (0x158 bytes)
3. Calls CTexture__ctor to initialize base class
4. Sets vtable to PTR_FUN_005e4f64
5. Creates texture: 128x128 if (DAT_00888a90 & 0x20) || DAT_0089c924, else 128x1
6. Calls InitMipLevels to initialize texture mip levels

**Called from:** CHud__Init (0x00481450)

---

### CDXBattleLine__scalar_deleting_dtor (0x0053a120)

**Signature:** `void __thiscall CDXBattleLine__scalar_deleting_dtor(byte flags)`

Scalar deleting destructor. Calls base destructor then optionally frees memory.

**Called from:** Vtable slot 0

---

### CDXBattleLine__LoadTextures (0x0053a150)

**Signature:** `void __thiscall CDXBattleLine__LoadTextures(void)`

Loads marker textures and creates vertex/index buffers for battle line rendering.

**Key Operations:**
1. Finds "hud\marker.tga" texture (offset 0x0C)
2. Allocates CVBuffer (0x2c bytes) for markers (offset 0x78)
3. Creates dynamic vertex buffer (500 vertices, stride 0x14, flags 0x44)
4. Finds "hud\V2\BattleEngineMarker.tga" texture (offset 0x14)
5. Allocates overlay CTexture (0x158 bytes, offset 0x08)
6. Creates 128x128 texture with mipmaps

**Called from:** CHud__LoadTextures (0x00481650)

---

### CDXBattleLine__Setup (0x0053a280)

**Signature:** `int __thiscall CDXBattleLine__Setup(void)`

Sets up the battle line for rendering by setting state to 2 and rebuilding the mesh.

**Key Operations:**
1. Saves DAT_00889010, sets it to 1
2. Sets state byte at offset 0x24 to 2
3. Calls BuildMesh to generate terrain mesh
4. Restores DAT_00889010
5. Returns 1

**Called from:** FUN_00481af0 (via JMP)

---

### CDXBattleLine__UpdateHeightmap (0x0053a390)

**Signature:** `void __thiscall CDXBattleLine__UpdateHeightmap(void)`

Updates the heightmap data by sampling terrain at grid positions. Uses circular mask (radius 0x844 = 2116) to limit area.

**Key Operations:**
1. Gets battle bounds from FUN_0047ef20
2. Calculates center and extent with 1.21x padding
3. Iterates over grid (-0x30 to +0x30 in both axes)
4. For each point in circular mask:
   - Samples terrain height via FUN_0047eb80
   - Calculates intensity value (0-3 range)
   - Writes to heightmap buffer as short values

**Called from:** BuildMesh (0x0053a5e0)

---

### CDXBattleLine__BuildMesh (0x0053a5e0)

**Signature:** `void __thiscall CDXBattleLine__BuildMesh(void)`

Builds the mesh for battle line rendering using triangulation and height data.

**Key Operations:**
1. Gets battle bounds and calculates mesh extents
2. Calls UpdateHeightmap to sample terrain
3. Allocates triangulation mesh via OID__AllocObject (0x18 bytes)
4. Creates quad mesh via Triangulate__CreateQuadMesh (0x400 = 1024 quads)
5. Calculates scale/offset for coordinate mapping (offsets 0x48-0x54)
6. Iterates through units at DAT_0067a748, transforms positions
7. Stores triangle/vertex counts (offsets 0x1C/0x20)
8. Creates dynamic vertex buffer if needed (offset 0x1C obj)
9. Allocates vertex position array (8 bytes per vertex)
10. Creates index buffer via CIBuffer__Constructor
11. Copies indices with triangle reordering

**Called from:** CDXBattleLine__Setup (0x0053a280)

**Line references in debug:** 0x145, 0x161, 0x165, 0x170

---

### CDXBattleLine__InitMipLevels (0x0053a930)

**Signature:** `void __thiscall CDXBattleLine__InitMipLevels(void)`

Initializes mip levels for the battle line texture with gradient data.

**Key Operations:**
1. Gets mip level count from FUN_00558690
2. For each mip level:
   - Locks texture surface
   - Fills with gradient values (-0x400 to -0xf70 range)
   - Left half: -0x400 (darker)
   - Right half: varies based on position
3. Unlocks texture

**Called from:** CDXBattleLine__Constructor (0x0053a050)

---

### CDXBattleLine__UpdateVertexBuffer (0x0053aa40)

**Signature:** `void __thiscall CDXBattleLine__UpdateVertexBuffer(void)`

Updates the vertex buffer with marker positions for rendering.

**Key Operations:**
1. Locks vertex buffer from offset 0x70
2. Iterates 8 times with base offset, calls SetupVertex
3. Iterates through unit list at DAT_0067a748
4. For each unit, calculates position and calls SetupVertex with intensity value
5. Unlocks vertex buffer

**Called from:** CDXBattleLine__Render (0x0053abe0)

---

### CDXBattleLine__SetupVertex (0x0053ab40)

**Signature:** `void CDXBattleLine__SetupVertex(float* outVertex, float baseY, float offsetX, float offsetY, float* inPosition, float intensity, char mode)`

Sets up a single vertex with position, texture coordinates, and intensity.

**Key Operations:**
1. Calculates world position from input position and offsets
2. Sets Z=0.9, W=0.5 for clip space
3. If mode == 0:
   - Calculates texture coordinates from position (×0.0078125)
   - Sets intensity value
4. If mode != 0:
   - Sets alternate UV mapping

**Called from:** CDXBattleLine__UpdateVertexBuffer (0x0053aa40)

---

### CDXBattleLine__Render (0x0053abe0)

**Signature:** `void __thiscall CDXBattleLine__Render(void)`

Main render function that draws the battle line with multiple passes.

**Key Operations:**
1. Checks DAT_0067a748 (unit list) exists
2. Sets render states (DAT_009c68ac=0, DAT_009c690d=1)
3. Calculates Y position based on split-screen mode
4. Calls UpdateVertexBuffer
5. Renders in 3 passes (indices 0, 1, 2 via FUN_00527cc0):
   - Pass 0: Full battle line with stencil
   - Pass 1: Masked area rendering
   - Pass 2: Battle engine markers
6. Each pass configures:
   - Texture stages (`RenderState_Set`/`0x00513bc0`, `FUN_00513820`)
   - Sampler states (FUN_00513930)
   - Alpha blending
7. Renders markers for units at DAT_008a9a98+0x2a4 range
8. Uses FUN_00555be0 for marker sprite rendering with rotation

**Called from:** FUN_00487d10 (CHud render function)

---

## Related Strings

| Address | String | Usage |
|---------|--------|-------|
| 0x00650324 | "C:\dev\ONSLAUGHT2\DXBattleLine.cpp" | Debug path |
| 0x00650348 | "hud\V2\BattleEngineMarker.tga" | BE marker texture |
| 0x00650368 | "hud\marker.tga" | Generic marker texture |
| 0x00650378 | "battleline_method" | CVar name (?) |
| 0x0062d1b8 | "hud\v2\BattleLineOutline.tga" | Outline texture (used in CHud) |

## Related Globals

| Address | Type | Name | Notes |
|---------|------|------|-------|
| 0x0067a748 | void* | g_pUnitList | Unit list for markers |
| 0x00889010 | int | DAT_00889010 | Render state flag |
| 0x00888a90 | int | DAT_00888a90 | Hardware capability flags |
| 0x0089c924 | int | DAT_0089c924 | Unknown render flag |
| 0x008a9d84 | void* | DAT_008a9d84 | Render target/device |
| 0x008a9a98 | int[] | DAT_008a9a98 | Unit array base |
| 0x009c68ac | int | DAT_009c68ac | Z-buffer write flag |
| 0x009c690d | byte | DAT_009c690d | Alpha blend flag |

## Related Functions (External)

| Address | Name | Purpose |
|---------|------|---------|
| 0x0047ef20 | FUN_0047ef20 | Get battle bounds (returns int[4]) |
| 0x0047eb80 | FUN_0047eb80 | Sample terrain height |
| 0x0047ec60 | FUN_0047ec60 | Unknown terrain function |
| 0x004f7460 | FUN_004f7460 | Transform position |
| 0x004f7940 | FUN_004f7940 | Finalize transformation |
| 0x00558690 | FUN_00558690 | Get texture/surface manager |
| 0x00555be0 | FUN_00555be0 | Render sprite with rotation |
| 0x00513bc0 | RenderState_Set | Cached render-state setter |
| 0x00513820 | FUN_00513820 | Set texture stage state |
| 0x00513930 | FUN_00513930 | Set sampler state |
| 0x00513a50 | FUN_00513a50 | Set texture |
| 0x00513c70 | FUN_00513c70 | Draw indexed primitives |
| 0x00527cc0 | FUN_00527cc0 | Check render pass enabled |
| 0x00527d20 | FUN_00527d20 | Check stencil enabled |
| 0x00527da0 | CVBufTexture__MarkAccepted | Apply/mark accepted stencil pass |

## Inheritance

```
CTexture (0x158 bytes)
  |
  +-- CDXBattleLine
```

## Notes

1. The battle line is a tactical HUD element showing territorial control
2. Uses triangulated mesh for terrain-following visualization
3. Multiple render passes for different effects (outline, fill, markers)
4. Supports split-screen multiplayer (position calculations)
5. Unit markers rendered with rotation based on facing direction
6. Hardware capability flags affect texture resolution (128x128 vs 128x1)
