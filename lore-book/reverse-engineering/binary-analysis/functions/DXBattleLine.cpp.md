# DXBattleLine.cpp Function Mappings

<!-- ghidra-full-reaudit-20260713:start -->
> **2026-07-13 semantic revalidation:** `0x0053a140` comment correction. Older conflicting text below is superseded for these rows. Use the [closeout](../ghidra-full-reaudit-closeout-2026-07-13.md); exact records are in `reverse-engineering/binary-analysis/ghidra-full-reaudit-corrections-2026-07-13.json` and `reverse-engineering/binary-analysis/ghidra-targeted-revalidation-corrections-2026-07-13.json`.
<!-- ghidra-full-reaudit-20260713:end -->

> Debug path: `[maintainer-local-source-export-root]\DXBattleLine.cpp` (0x00650324)
> Functions found: 13
> Last updated: 2026-05-28

## Overview

CDXBattleLine is a DirectX rendering class that visualizes the "battle line" on the HUD - the tactical map showing territory control and unit positions. It inherits from CTexture and manages heightmap sampling, BattleLine mesh construction, marker vertex updates, and multi-pass rendering.

Wave521 corrected the adjacent mesh-topology helper ownership: `CDXBattleLine__BuildMesh` allocates and uses a separate 0x18-byte Triangulate work object, so the helper island at `0x004f7170..0x004f7940` is documented under [`triangulate.cpp`](triangulate.cpp/_index.md), not as CDXBattleLine methods.

Wave934 (`battleline-triangulate-mesh-review-wave934`) re-reviewed that boundary read-only. Fresh exports confirmed `0x004f7170 Triangulate__CreateQuadMesh`, `0x004f7460 Triangulate__InsertPointOrAppendVertex`, `0x004f74b0 Triangulate__SplitTriangleAtPointAndLegalizeEdges`, `0x004f7660 Triangulate__TryFlipSharedEdgeForQuality`, `0x004f78c0 Triangulate__FindTriangleByDirectedEdge`, and `0x004f7940 Triangulate__RelaxMeshByEdgeFlips` still belong to the Triangulate work object, with context anchors `0x0053a5e0 CDXBattleLine__BuildMesh`, `0x0053b470 CDXBattleLine__RenderTriOverlayPass`, and `0x00487d10 CHud__RenderBattleline`. Wave934 made no mutation. Wave911 focused re-audit progress after Wave934 is `146/1408 = 10.37%`; static export-contract closure remains `6113/6113 = 100.00%`. Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260528-005650_post_wave934_battleline_triangulate_mesh_review_verified`.

Wave990 (`hud-battleline-objective-overlay-review-wave990`) saved comment/tag normalization for `0x00414cb0 CDXBattleLine__PopulateBattleLineAndInfluenceOverlayVertices`. Fresh xrefs verify `0x00487d10 CHud__RenderBattleline -> 0x00414cb0` at `0x00488071`, `0x00414cb0 -> 0x004e6610 SharedState__IsTimer88PendingAndState7CZero` at `0x00414d1c`, and `0x00414cb0 -> 0x0053b5f0 CDXBattleLine__AppendOverlayVertex` at `0x00414ce2` / `0x00414d35`. The body walks battle-line list `DAT_00855140` and influence/deferred list `DAT_008550a0`, appending yellow/red overlay vertices. Wave911 focused re-audit progress is `441/1408 = 31.32%`; expanded static surface progress is `517/1478 = 34.98%`; export-contract closure remains `6222/6222 = 100.00%`. Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260531-041618_post_wave990_hud_battleline_objective_overlay_verified`. Runtime battleline rendering, exact `CDXBattleLine` list/vertex layouts, source-body identity, and rebuild parity remain separate proof.

Probe token anchor: Wave990; hud-battleline-objective-overlay-review-wave990; 0x0040dda0 CUnitAI__RefreshGridCooldownFromOccupiedCells; 0x00414cb0 CDXBattleLine__PopulateBattleLineAndInfluenceOverlayVertices; 0x0044c720 CFearGrid__GetOccupancyAtWorldVector; 0x00485d50 CHud__RenderObjectiveStatusPanel; 0x00487d10 CHud__RenderBattleline; 441/1408 = 31.32%; 517/1478 = 34.98%; 6222/6222 = 100.00%; [maintainer-local-ghidra-backup-root]\BEA_20260531-041618_post_wave990_hud_battleline_objective_overlay_verified.

Wave589 hardened the core CDXBattleLine constructor/render slice from `0x0053a050` through `0x0053b5f0`. It saved 13 signatures/comments/tags, renamed the stale duplicate `CDXSurf__dtor` label at `0x0053a140` to `CDXBattleLine__DestructorThunk`, and corrected the overlay append helper to the observed `RET 0xc` three-stack-argument shape. This is static retail Ghidra evidence only; exact source identity/layout, runtime rendering behavior, BEA patching, and rebuild parity remain unproven.

Wave1213 (`wave1213-render-resource-lifecycle-tail-current-risk-review`) re-read `0x0053a140 CDXBattleLine__DestructorThunk` as a current-risk denominator row inside the mesh/resource/render static contract. Fresh instruction export is still a one-instruction `JMP 0x00556d90` thunk, while the decompiler follows the jump and shows the `CDXSurf__dtor` body. That decompiler behavior is a reason to preserve the thunk name and not re-collapse the row into the base destructor owner. The wave made no mutation. Active current-risk progress moved to `1125/1179 = 95.42%`; verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260607-074242_post_wave1213_render_resource_lifecycle_tail_current_risk_review_verified`. Runtime HUD battleline teardown/render behavior, exact CDXBattleLine/CDXSurf layouts, exact source identity, BEA patching behavior, rebuild parity, and no-noticeable-difference parity remain separate proof.

## Class Structure

### Vtable at 0x005e4f64

| Offset | Address | Function | Notes |
|--------|---------|----------|-------|
| 0x00 | 0x0053a120 | CDXBattleLine__scalar_deleting_dtor | Proven slot 0 only |
| 0x04 | 0x0053a010 | (raw target - no function at pointer) | Calls InitMipLevels / UpdateHeightmap via raw trampoline; boundary remains deferred |
| 0x08 | 0x0053a040 | (raw target - no function at pointer) | JMP to `0x00557060`; boundary remains deferred |
| 0x0C | 0x005572c0 | CTextureSequence__ReleaseIfLoaded | Inherited-looking |
| 0x10 | 0x00558600 | (CTexture method) | Inherited |
| 0x14 | 0x00556e90 | (CTexture method) | Inherited |
| 0x18 | 0x00556fc0 | CDXSurf__SetupSurface | Virtual call in Constructor |
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
| 0x58 | int | m_overlayPulseBoost | Computed in AppendOverlayVertex |
| 0x5C | int | m_overlayBufferLocked | Set/cleared around dynamic overlay VB lock |
| 0x60 | int | m_overlayVertexCount | Reset by Populate helper; capped at 500 |
| 0x64 | int | param_1 | Constructor param |
| 0x68 | int | param_2 | Constructor param |
| 0x70 | CVBuffer* | m_pVertexBuffer | Vertex buffer for markers |
| 0x74 | ? | m_pRenderTarget | Render target reference |
| 0x78 | CVBuffer* | m_pDynamicVB | 500-vertex dynamic buffer |
| 0x7C | void* | m_dynamicVBWriteCursor | Current write cursor after lock |
| 0x1C (obj) | int | m_nVertexCount | Vertex count from mesh |
| 0x1D (obj) | CIBuffer* | m_pMeshIB | Mesh index buffer |

## Functions

### CDXBattleLine__Constructor (0x0053a050)

**Signature:** `void __thiscall CDXBattleLine__Constructor(void * this, int origin_x, int origin_y)`

Initializes the HUD battleline field block. `CHud__Init` passes ECX as the newly allocated field block, then stack constants `-7` and `14`; the function stores those values at `this+0x64/+0x68`, allocates the 0x158 texture-backed CDXBattleLine/CDXSurf object, installs vtable `0x005e4f64`, and creates the line texture as 128x1 or 128x128 based on hardware flags.

**Key Operations:**
1. Stores `origin_x` at offset 0x64 and `origin_y` at offset 0x68
2. Allocates CTexture via OID__AllocObject (0x158 bytes)
3. Calls CTexture__ctor to initialize base class
4. Sets vtable to PTR_FUN_005e4f64
5. Creates texture: 128x128 if (DAT_00888a90 & 0x20) || DAT_0089c924, else 128x1
6. Calls InitMipLevels to initialize texture mip levels

**Called from:** CHud__Init (0x00481450)

---

### CDXBattleLine__scalar_deleting_dtor (0x0053a120)

**Signature:** `void * __thiscall CDXBattleLine__scalar_deleting_dtor(void * this, byte delete_flags)`

Scalar deleting destructor at vtable slot `0x005e4f64[0]`. `RET 0x4` proves one stack flag after ECX; the body calls `CDXBattleLine__DestructorThunk`, frees `this` when `delete_flags & 1`, and returns `this`.

**Called from:** Vtable slot 0

---

### CDXBattleLine__DestructorThunk (0x0053a140)

**Signature:** `void __fastcall CDXBattleLine__DestructorThunk(void * this)`

One-instruction `JMP 0x00556d90` thunk to the real `CDXSurf__dtor`. Wave589 renamed this away from the stale duplicate `CDXSurf__dtor` label at `0x0053a140`; the actual base destructor remains documented at `0x00556d90` in [`DXSurf.cpp.md`](DXSurf.cpp.md).

**Called from:** CDXBattleLine__scalar_deleting_dtor (0x0053a120)

---

### CDXBattleLine__LoadTextures (0x0053a150)

**Signature:** `void __fastcall CDXBattleLine__LoadTextures(void * this)`

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

**Signature:** `int __fastcall CDXBattleLine__Setup(void * this)`

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

**Signature:** `void __fastcall CDXBattleLine__UpdateHeightmap(void * this)`

Updates the heightmap data by sampling terrain at grid positions. Uses circular mask (radius 0x844 = 2116) to limit area.

**Key Operations:**
1. Gets battle bounds from `CHeightField__RecomputeGridExtentsAndHeightRange`
2. Calculates center and extent with 1.21x padding
3. Iterates over grid (-0x30 to +0x30 in both axes)
4. For each point in circular mask:
   - Samples terrain height via FUN_0047eb80
   - Calculates intensity value (0-3 range)
   - Writes to heightmap buffer as short values

**Called from:** BuildMesh (0x0053a5e0)

---

### CDXBattleLine__BuildMesh (0x0053a5e0)

**Signature:** `void __fastcall CDXBattleLine__BuildMesh(void * this)`

Builds the mesh for battle line rendering using triangulation and height data.

**Key Operations:**
1. Gets battle bounds and calculates mesh extents
2. Calls UpdateHeightmap to sample terrain
3. Allocates triangulation mesh via OID__AllocObject (0x18 bytes)
4. Creates a Triangulate work mesh via `Triangulate__CreateQuadMesh` (0x400 capacity)
5. Calculates scale/offset for coordinate mapping (offsets 0x48-0x54)
6. Iterates through units at DAT_0067a748, transforms positions
7. Stores triangle/vertex counts (offsets 0x1C/0x20)
8. Creates dynamic vertex buffer if needed (offset 0x1C obj)
9. Allocates vertex position array (8 bytes per vertex)
10. Creates index buffer via CIBuffer__Constructor
11. Copies indices with triangle reordering

Wave521 BattleLine/Triangulate context:

- `0x0053a712` calls `Triangulate__CreateQuadMesh`.
- `0x0053a7a4` calls `Triangulate__InsertPointOrAppendVertex`.
- `0x0053a7c0` calls `Triangulate__RelaxMeshByEdgeFlips`.
- These calls operate on the Triangulate work object returned by `Triangulate__CreateQuadMesh`; runtime overlay mesh behavior and rebuild parity remain unproven.

**Called from:** CDXBattleLine__Setup (0x0053a280)

**Line references in debug:** 0x145, 0x161, 0x165, 0x170

---

### CDXBattleLine__InitMipLevels (0x0053a930)

**Signature:** `void __fastcall CDXBattleLine__InitMipLevels(void * this)`

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

**Signature:** `void __thiscall CDXBattleLine__UpdateVertexBuffer(void * this, float hud_y, int use_unit_marker_offsets)`

Updates the vertex buffer with marker positions for rendering.

**Key Operations:**
1. Locks vertex buffer from offset 0x70
2. Iterates 8 times with base offset, calls SetupVertex
3. Iterates through unit list at DAT_0067a748
4. For each unit, calculates position and calls SetupVertex with intensity value
5. Unlocks vertex buffer

`RET 0x8` and the two `CDXBattleLine__Render` callsites prove the `hud_y` / mode-flag stack pair.

**Called from:** CDXBattleLine__Render (0x0053abe0)

---

### CDXBattleLine__SetupVertex (0x0053ab40)

**Signature:** `void __cdecl CDXBattleLine__SetupVertex(float * out_vertex, float screen_base_y, float screen_offset_x, float screen_offset_y, float * source_xy, float intensity, char mode)`

Sets up a single 0x20-byte marker vertex with position, texture coordinates, and intensity. Two `UpdateVertexBuffer` callsites push seven arguments and then add `ESP,0x1c`, confirming the cdecl shape.

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

**Signature:** `void __fastcall CDXBattleLine__Render(void * this)`

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

**Called from:** CHud__RenderBattleline (0x00487d10)

---

### CDXBattleLine__RenderTriOverlayPass (0x0053b470)

**Signature:** `void __fastcall CDXBattleLine__RenderTriOverlayPass(void * this)`

Render helper called from `CDXBattleLine__Render` after the base battleline passes. The body unlocks the dynamic overlay buffer if `this+0x5c` says it is still locked, binds the marker texture at `this+0x0c`, configures two overlay draw passes, and submits `this+0x60` vertices from the buffer at `this+0x78` when the count is nonzero.

**Called from:** CDXBattleLine__Render (0x0053abe0)

---

### CDXBattleLine__AppendOverlayVertex (0x0053b5f0)

**Signature:** `void __thiscall CDXBattleLine__AppendOverlayVertex(void * this, float world_x, float world_y, uint color_rgb)`

Appends one dynamic overlay marker vertex. `RET 0xc` and the two `CDXBattleLine__PopulateBattleLineAndInfluenceOverlayVertices` callsites prove ECX plus three stack arguments: `world_x`, `world_y`, and the color constants `0xffff00` / `0xff0808`. The body lazily locks the dynamic buffer, computes a pulsing color boost at `this+0x58`, projects the point into HUD space, writes a 0x14-byte overlay vertex, and increments the count at `this+0x60` up to 500.

**Called from:** CDXBattleLine__PopulateBattleLineAndInfluenceOverlayVertices (0x00414cb0)

---

### CDXBattleLine__PopulateBattleLineAndInfluenceOverlayVertices (0x00414cb0)

**Signature:** `void __thiscall CDXBattleLine__PopulateBattleLineAndInfluenceOverlayVertices(void * this)`

Wave 310 corrected this saved owner label from the older `CExplosionInitThing` interpretation to a CDXBattleLine overlay helper.

**Key Operations:**
1. Resets the dynamic overlay vertex count at offset `+0x60`
2. Walks the battle-line source list at `DAT_00855140`
3. Appends yellow overlay vertices through `CDXBattleLine__AppendOverlayVertex`
4. Walks the influence/source list at `DAT_008550a0`
5. Filters the second list through `CExplosionInitThing__HasSpawnDelayElapsedAndNotTriggered`
6. Appends red overlay vertices through `CDXBattleLine__AppendOverlayVertex`

**Called from:** `CHud__RenderBattleline` (0x00487d10)

**Boundary:** This is static saved-Ghidra refinement only. Runtime overlay rendering, concrete list layouts, tag/local/type recovery, and source identity beyond the checked caller/body evidence remain unproven.

---

## Related Strings

| Address | String | Usage |
|---------|--------|-------|
| 0x00650324 | "[maintainer-local-source-export-root]\DXBattleLine.cpp" | Debug path |
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
| 0x0047ef20 | CHeightField__RecomputeGridExtentsAndHeightRange | Heightfield-owned grid extent / height range helper consumed by battle-line mesh and heightmap updates; Wave396 corrected the older CDXBattleLine owner label. |
| 0x0047eb80 | FUN_0047eb80 | Sample terrain height |
| 0x0047ec60 | FUN_0047ec60 | Unknown terrain function |
| 0x004f7170 | Triangulate__CreateQuadMesh | Allocates and seeds the BattleLine Triangulate work mesh. |
| 0x004f7460 | Triangulate__InsertPointOrAppendVertex | Inserts/appends BattleLine mesh points into the Triangulate work object. |
| 0x004f74b0 | Triangulate__SplitTriangleAtPointAndLegalizeEdges | Splits a containing triangle and legalizes new shared edges. |
| 0x004f7660 | Triangulate__TryFlipSharedEdgeForQuality | Flips shared edges when static geometric quality tests improve. |
| 0x004f78c0 | Triangulate__FindTriangleByDirectedEdge | Finds or rotates triangle triplets by directed edge. |
| 0x004f7940 | Triangulate__RelaxMeshByEdgeFlips | Performs dirty-flagged edge-flip relaxation passes. |
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
