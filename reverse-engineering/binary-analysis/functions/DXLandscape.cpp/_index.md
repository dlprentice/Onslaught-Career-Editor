# DXLandscape.cpp Function Mappings

> Functions from DXLandscape.cpp mapped to BEA.exe binary
> Debug path: `C:\dev\ONSLAUGHT2\DXLandscape.cpp` at 0x00650bdc

## Overview
- **Functions Mapped:** 20
- **Status:** COMPLETE (Dec 2025)
- **Classes:** CDXLandscape (derives from CLandscape)
- **RTTI:** `.?AVCDXLandscape@@` at 0x00650c28
- **VTable:** 0x005e50d0

## Class Description

CDXLandscape is the DirectX implementation of the landscape/terrain rendering system. It manages:
- **Terrain Grid:** 64x64 tile grid (512x512 world units at 8 units per tile)
- **Vertex Buffer:** 65x65 vertex grid (0x41 x 0x41) for terrain mesh
- **Mipmapped Textures:** Multiple LOD levels for terrain textures
- **Shadow Mapping:** Dynamic shadow rendering for terrain
- **LOD System:** Distance-based level-of-detail for terrain tiles

## Key Technical Details

### Terrain Grid
- 64x64 tiles (0x40 x 0x40)
- Each tile is 8 world units
- Total terrain size: 512x512 world units
- Tile data stored in 0x14 (20) byte structures

### LOD System
- Distance-based LOD selection in UpdateLOD
- LOD levels: 0-8 (higher = more detail)
- Thresholds: 4096, 1024, 256 for LOD transitions
- Calls CLandscapeTexture__QueueTileUpdate for texture streaming

### Vertex Shader
- Name: "LandscapeShader"
- Shader Model: vs.1.1
- Uses position (v0) and texcoord (v7) inputs

### Console Variables
- `BuildLandscapeCache` - Console command to rebuild texture cache
- `xx_coastcalc` - Coast calculation debug variable

## Function List

| Address | Name | Status | Description |
|---------|------|--------|-------------|
| 0x00544a00 | CDXLandscape__Constructor | NAMED | Initializes vtable, zeroes members |
| 0x00544a40 | CDXLandscape__ScalarDeletingDestructor | NAMED | MSVC scalar deleting destructor |
| 0x00544a60 | CDXLandscape__Destructor | NAMED | Cleanup, releases shader and buffers |
| 0x00544af0 | CDXLandscape__Init | NAMED | Main init, creates buffers, registers console cmds |
| 0x00544eb0 | CDXLandscape__ReleaseBuffers | NAMED | Releases vertex/index/texture buffers |
| 0x00544f10 | CDXLandscape__Shutdown | NAMED | Full shutdown, releases all resources |
| 0x00544fc0 | CDXLandscape__BuildVertexBuffer | NAMED | Builds 65x65 vertex grid with height data |
| 0x005447e0 | CDXLandscape__CreateMipLevels | NAMED | Creates mipmapped texture hierarchy |
| 0x00545070 | CDXLandscape__Reset | NAMED | Resets terrain data, calculates min/max heights |
| 0x005453d0 | CDXLandscape__LoadCloudShadowTexture | NAMED | Loads "clouds_shadow.tga" |
| 0x005453f0 | CDXLandscape__SetTileData | NAMED | Sets data for specific terrain tile |
| 0x00545410 | CDXLandscape__Render | NAMED | Main render entry point |
| 0x00545590 | CDXLandscape__RenderTerrain | NAMED | Complex terrain rendering with multi-texturing |
| 0x00546220 | CDXLandscape__SetRenderTarget | NAMED | D3D render target setup for shadow mapping |
| 0x005463f0 | CDXLandscape__ReleaseRenderTarget | NAMED | Releases D3D render targets |
| 0x00546460 | CDXLandscape__ReleaseSurfaces | NAMED | Releases two D3D surfaces |
| 0x00546490 | CDXLandscape__RenderShadowMap | NAMED | Renders terrain to shadow map |
| 0x00546900 | CDXLandscape__RenderTileRange | NAMED | Renders tiles within bounding box |
| 0x00546b10 | CDXLandscape__ResetCameraPosition | NAMED | Forces camera position update (magic: 0x4996b438) |
| 0x00546b40 | CDXLandscape__UpdateLOD | NAMED | Main LOD calculation for all 64x64 tiles |

## VTable Layout (0x005e50d0)

| Offset | Address | Function |
|--------|---------|----------|
| 0x00 | 0x00544a40 | ScalarDeletingDestructor |
| 0x04 | 0x00544cc0 | Virtual method (inherited) |
| 0x08 | 0x00405930 | Virtual method (inherited) |
| 0x0C | 0x00405930 | Virtual method (inherited) |
| 0x10 | 0x00544eb0 | ReleaseBuffers |

## Class Hierarchy
```
CLandscape (base)
  |
  +-- CDXLandscape (DirectX implementation)
```

## Related Files
- **Header:** DXLandscape.h (debug path at 0x00650bbc)
- **Texture System:** CLandscapeTexture functions at 0x0048e310+
- **Index Buffer:** CLandscapeIB__CreateIndexBuffer at 0x0048df20

## Related Classes
- CLandscapeTexture - Terrain texture management
- CLandscapeIB - Terrain index buffer management
- CVBuffer - Vertex buffer wrapper
- CIBuffer - Index buffer wrapper
- CVertexShader - Shader management

## Parent
- [../README.md](../README.md)
