# DXLandscape.cpp Function Mappings

> Functions from DXLandscape.cpp mapped to BEA.exe binary
> Debug path: `[maintainer-local-source-export-root]\DXLandscape.cpp` at 0x00650bdc

## Overview

> **Queue status (2026-05-26):** Ghidra export-contract closure **6113/6113** (Wave900: every function commented; clean-signature proxy; not evidence-grade semantics). Lines below that reference a "next raw commentless" row are **archival wave progress**, not open work.

- **Functions Mapped:** 20 primary DXLandscape entries, plus Wave806 mixer-detail texture helper read-back and Wave807 adjacent patch-helper correction; Wave982 superseded the older `0x00403ff0` DXLandscape owner label as resource-descriptor-table cleanup evidence
- **Status:** Active re-audit in progress; earlier "complete" wording was provisional
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
| 0x0048de90 | CDXLandscape__ClearMixerDetailTextureHandle | WAVE806 | Clears global mixer-detail texture handle `0x0067a7d0`; supersedes older Wave420 HUD-marker wording |
| 0x0048dea0 | CDXLandscape__ReleaseMixerDetailTextureRef | WAVE806 | Releases non-null global mixer-detail texture handle through `CTexture__DecrementRefCountFromNameField(handle+0x08)` and clears it |
| 0x00544770 | CDXLandscape__ReleaseOwnedResources | WAVE601 | Releases one landscape resource record, its 0xc-entry callback vector, and scratch buffer |
| 0x005447d0 | CDXLandscape__FreeObjectCallback | WAVE601 | Frees the pointer at one 0xc-byte vector record |
| 0x005447e0 | CDXLandscape__CreateMipLevels | WAVE601 | Creates mip texture hierarchy and per-level update buffers |
| 0x00544a00 | CDXLandscape__Constructor | WAVE601 | Initializes vtable, HUD marker handle, and resource fields |
| 0x00544a40 | CDXLandscape__ScalarDeletingDestructor | WAVE601 | MSVC scalar deleting destructor with `flags` bit 0 free gate |
| 0x00544a60 | CDXLandscape__Destructor | WAVE601 | Unlinks shader lists, releases shader/interface fields, and clears pending HUD marker |
| 0x00544af0 | CDXLandscape__Init | WAVE601 | Main init, creates buffers, registers console cmds, and stores `engine+0x49c` init context |
| 0x00544eb0 | CDXLandscape__ReleaseBuffers | WAVE601 | Releases vertex/index/texture buffers and interface pointer |
| 0x00544f10 | CDXLandscape__Shutdown | WAVE601 | Full shutdown, releases arrays, device resources, surfaces, and texture/HUD pointer |
| 0x00544fb0 | CDXLandscape__ResetWrapper | WAVE865 | Wrapper reached from `CEngine__ResetPos`; ignores forwarded stack coordinates and calls `CDXLandscape__Reset(this)` |
| 0x00403ff0 | CResourceDescriptorTable__DestroyEmbeddedDescriptor_Thunk | WAVE982 | Supersedes older `CDXLandscape__DestroyResourceDescriptorArray_Thunk`; owner-neutral resource-descriptor cleanup thunk |
| 0x00544fc0 | CDXLandscape__BuildVertexBuffer | WAVE602 | Builds 65x65 vertex grid with height data |
| 0x00545070 | CDXLandscape__Reset | WAVE602 | Resets terrain resources and 64x64 tile records |
| 0x005453d0 | CDXLandscape__LoadCloudShadowTexture | WAVE602 | Loads "clouds_shadow.tga" into `+0x38` |
| 0x005453f0 | CDXLandscape__SetTileData | WAVE602 | Stores a tile/context pointer into one resource record |
| 0x00545410 | CDXLandscape__Render | WAVE603 | Main render wrapper, LOD forwarder, world-matrix setup, and cached-light terrain draw entry |
| 0x00545590 | CDXLandscape__RenderTerrain | WAVE603 | Terrain draw path with resource-record, texture-stage, buffer-binding, LOD tile, and shadow-map handling |
| 0x00546220 | CDXLandscape__SetRenderTarget | WAVE604 | D3D render-target save/switch helper for shadow mapping |
| 0x005463f0 | CDXLandscape__ReleaseRenderTarget | WAVE604 | Restores and releases saved D3D target/depth surfaces |
| 0x00546460 | CDXLandscape__ReleaseSurfaces | WAVE604 | Releases and nulls two saved D3D surfaces without restore |
| 0x00546490 | CDXLandscape__RenderShadowMap | WAVE604 | Shadow-map pass over terrain/resource-record tile ranges |
| 0x00546900 | CDXLandscape__RenderTileRange | WAVE604 | Renders clamped 64x64 tile ranges from coordinate bounds |
| 0x00546b10 | CDXLandscape__ResetCameraPosition | WAVE605 | Invalidates cached resource-record camera position sentinels |
| 0x00546b40 | CDXLandscape__UpdateLOD | WAVE605 | Main LOD calculation and texture/patch update path for 64x64 tiles |

## Wave865 Reset Wrapper Read-Back

## Wave1213 Render-Resource Lifecycle Tail Read-Back

Wave1213 (`wave1213-render-resource-lifecycle-tail-current-risk-review`) re-read `0x00544a60 CDXLandscape__Destructor` and `0x00544eb0 CDXLandscape__ReleaseBuffers` as current-risk denominator rows inside the mesh/resource/render static contract. Fresh xrefs verify `CDXLandscape__ScalarDeletingDestructor -> CDXLandscape__Destructor` at `0x00544a43`, and vtable DATA xref `0x005e50e0` points at `CDXLandscape__ReleaseBuffers` for slot `+0x10`. Context rows also re-read `CDXLandscape__Constructor`, `CDXLandscape__ScalarDeletingDestructor`, `CDXLandscape__Init`, `CDXLandscape__Shutdown`, and `CDXLandscape__UpdateLOD`.

The wave made no mutation. Active current-risk progress moved to `1125/1179 = 95.42%`; verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260607-074242_post_wave1213_render_resource_lifecycle_tail_current_risk_review_verified`. Runtime Direct3D behavior, runtime terrain/HUD output, runtime lost-device behavior, exact CDXLandscape/CLandscape/resource layouts, exact source identity, BEA patching behavior, rebuild parity, and no-noticeable-difference parity remain separate proof.

Wave865 render tail static read-back (`render-tail-wave865`, `wave865-readback-verified`) hardened `0x00544fb0 CDXLandscape__ResetWrapper` as `void __thiscall CDXLandscape__ResetWrapper(void * this, int reset_x, int reset_y)`. `CEngine__ResetPos` forwards two stack values and the engine landscape pointer at `engine+0x10` into the wrapper; the wrapper ignores the stack values and calls `CDXLandscape__Reset(this)`. Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260525-160100_post_wave865_render_tail_verified`. Exact reset coordinate semantics, `CDXLandscape` layout, runtime reset behavior, source identity, BEA patching, and rebuild parity remain deferred.

## Wave982 Resource Descriptor Cleanup Owner Correction

Wave982 resource descriptor cleanup correction (`resource-descriptor-cleanup-wave982`, `wave982-readback-verified`) re-reviewed `0x00403ff0` and corrected the saved name from `CDXLandscape__DestroyResourceDescriptorArray_Thunk` to `CResourceDescriptorTable__DestroyEmbeddedDescriptor_Thunk`.

The row is retained here only as superseded DXLandscape-owner history. Current static evidence is generic descriptor cleanup: the body advances `ECX` by `8`, pushes `CResourceDescriptor__dtor`, element size `0x41c`, and count `1`, then calls `CRT__EhVectorDestructorIterator_WithUnwind`. Representative unwind xrefs include `0x005d0fb0`, `0x005d196b`, `0x005d2070`, `0x005d4900`, and `0x005d52e0`, plus DATA refs `0x00515f30` and `0x00515f90`.

Post-Wave982 queue telemetry remains `6222/6222 = 100.00%`. Wave911 focused re-audit progress is `376/1408 = 26.70%`; expanded static surface progress is `435/1478 = 29.43%`. Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260530-232843_post_wave982_resource_descriptor_cleanup_verified`.

This is static Ghidra evidence only. Exact source identity, concrete descriptor-table layout, runtime unwind/cleanup behavior, BEA patching, and rebuild parity remain separate proof.

## Wave807 Adjacent Patch Helper Correction

Wave807 landscape patch raw head (`landscape-patch-raw-head-wave807`, `wave807-readback-verified`) corrected adjacent stale `0x0048f2f0 CDXLandscape__SetUpdateBoundsAndRebuildVB` to `0x0048f2f0 CDXPatch__SetGridOriginStepAndRebuild` in [`DXPatchManager.cpp`](../DXPatchManager.cpp.md). The saved signature is `void __thiscall CDXPatch__SetGridOriginStepAndRebuild(void * this, int grid_origin_x, int grid_origin_z, int grid_step, int tile_metadata)`.

The DXLandscape evidence remains the caller: `CDXLandscape__UpdateLOD` callsite `0x00546fe6` calls the helper immediately after `CDXPatchManager__AllocatePatchSlot`, with two tile coordinates scaled by `8`, `grid_step` derived as `4 >> lod_slot`, and tile-record metadata copied from `[ESI+0x0b]`. Post-caller decompile read-back shows `CDXPatch__SetGridOriginStepAndRebuild(pvVar12, iStack_c8 * 8, iStack_c4 * 8, 4 >> ..., *(pbVar16 + 0xb))`.

Post-Wave807 queue telemetry is `6098` total, `5582` commented, `516` commentless, `0` exact-undefined signatures, `0` `param_N`, strict proxy `5582/6098 = 91.54%`, and next raw head `0x0048f620 CDXEngine__RenderPostMissionOverlayAndMenu`. Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260524-105819_post_wave807_landscape_patch_raw_head_verified`.

This is static Ghidra read-back evidence only. Exact CDXPatch field names, tile-record layout, runtime terrain rendering/GPU behavior, BEA patching, and rebuild parity remain deferred.

## Wave806 Mixer-Detail Texture Helper Correction

Wave806 raw commentless head (`raw-commentless-head-wave806`, `wave806-readback-verified`) corrected the earlier active wording for the `0x0067a7d0` global. `0x0048de90 CDXLandscape__ClearMixerDetailTextureHandle` now carries `void * __thiscall CDXLandscape__ClearMixerDetailTextureHandle(void * this)` and returns the incoming subobject pointer after clearing the global. `0x0048dea0 CDXLandscape__ReleaseMixerDetailTextureRef` now carries `void __cdecl CDXLandscape__ReleaseMixerDetailTextureRef(void)` and releases a non-null global by calling `0x004f27e0 CTexture__DecrementRefCountFromNameField(handle+0x08)` before clearing it.

The old `CDXLandscape__ClearPendingHudMarkerHandle` / `CDXLandscape__ReleasePendingHudMarker` labels are superseded for these rows. The correction is based on adjacent `0x0048dec0 CResourceAccumulator__LoadMixerDetailTexture`, which formats `mixers\detail%.2d.tga` and stores `CTexture__FindTexture(...)` into the same global, plus xrefs from `CDXLandscape__Constructor`, `CDXLandscape__Destructor`, and `Unwind@005d7980`.

Post-Wave806 queue telemetry is `6098` total, `5581` commented, `517` commentless, `0` exact-undefined signatures, `0` `param_N`, strict proxy `5581/6098 = 91.52%`, and next raw head `0x0048f2f0 CDXLandscape__SetUpdateBoundsAndRebuildVB`, later corrected by Wave807. Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260524-102416_post_wave806_raw_commentless_head_verified`.

This is static Ghidra read-back evidence only. Exact CDXLandscape field ownership, runtime terrain rendering behavior, runtime texture lifetime, BEA patching, and rebuild parity remain deferred.

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

## Superseded Wave420 Static Re-Audit Note (2026-05-14)

Wave420 originally hardened `CDXLandscape__ClearPendingHudMarkerHandle` at `0x0048de90` to:

```text
void * __thiscall CDXLandscape__ClearPendingHudMarkerHandle(void * this)
```

Wave806 supersedes the HUD-marker interpretation for this row. The saved name is now `CDXLandscape__ClearMixerDetailTextureHandle`, and adjacent loader/release evidence ties global `0x0067a7d0` to the mixer-detail texture path. This is static retail-binary evidence only; complete `CDXLandscape` layout recovery and runtime texture/terrain behavior remain unproven.

## Wave748 Unwind Continuation Read-Back

Wave748 unwind continuation saved a `void __cdecl Unwind@005d2070(void)` signature, comment, and tags for `0x005d2070 Unwind@005d2070`. Scope-table DATA xref `0x0061af0c` points at the cleanup body, and decompile/instruction evidence calls `CDXLandscape__DestroyResourceDescriptorArray_Thunk` on the stack-local descriptor array at `EBP-0x434`.

The same `unwind-continuation-wave748` tranche spans `0x005d1fc8 Unwind@005d1fc8` through `0x005d222b Unwind@005d222b`, with verified backup `[maintainer-local-ghidra-backup-root]\BEA_20260522-183258_post_wave748_unwind_continuation_verified`. Next high-signal queue head is `0x005d2250 Unwind@005d2250`; earliest raw commentless row remains `0x0042f220 CSPtrSet__Clear`.

This is saved static retail Ghidra evidence only. Exact parent source body, runtime exception behavior, runtime cleanup behavior, BEA patching, and rebuild parity remain unproven.

## Wave601 Head Lifecycle / Resource Note (2026-05-19)

Wave601 hardened the first nine live queue rows in this file:

```text
void __fastcall CDXLandscape__ReleaseOwnedResources(void * resource_record)
void __fastcall CDXLandscape__FreeObjectCallback(void * object_record)
void __thiscall CDXLandscape__CreateMipLevels(void * this, int mip_level_count)
void * __fastcall CDXLandscape__Constructor(void * this)
void * __thiscall CDXLandscape__ScalarDeletingDestructor(void * this, byte flags)
void __fastcall CDXLandscape__Destructor(void * this)
int __thiscall CDXLandscape__Init(void * this, void * init_context)
int __fastcall CDXLandscape__ReleaseBuffers(void * this)
void __fastcall CDXLandscape__Shutdown(void * this)
```

Evidence:

- `CEngine__Init` allocates a `0x40`-byte object, calls `CDXLandscape__Constructor`, stores it at `engine+0x10`, pushes `engine+0x49c`, moves the object into ECX, and calls `CDXLandscape__Init`; `RET 0x4` proves the one-stack-argument shape.
- `CDXLandscape__Constructor` installs vtable `0x005e50d0`, clears the pending HUD marker owner at `this+0x08`, and zeroes resource fields including `+0x24/+0x28/+0x2c/+0x30/+0x38` and byte `+0x3c`.
- `CDXLandscape__CreateMipLevels` has `RET 0x4`, stores `mip_level_count` at `+0x0c`, allocates CLandscapeTexture records from `DXLandscape.cpp` line `0x5f`, allocates per-level buffers from `DXLandscape.h` line `0xaa`, and initializes non-root mip buffers to `0xff`.
- Vtable slot `0` at `0x005e50d0` points to `CDXLandscape__ScalarDeletingDestructor`; vtable slot `4` at `0x005e50e0` points to `CDXLandscape__ReleaseBuffers`.
- `CEngine__Shutdown` calls `CDXLandscape__Shutdown` for `engine+0x10`; shutdown destroys the `+0x24` array of `0x34`-byte resource records through `CDXLandscape__ReleaseOwnedResources`, releases `+0x28/+0x2c/+0x30`, destroys CDXSurf state, and clears the `+0x38` texture/HUD-linked pointer.

Post-Wave601 queue telemetry is `6093` total, `3088` commented, `3005` commentless, `1324` exact-undefined signatures, and `1073` `param_N`; comment-backed proxy `3088/6093 = 50.68%`; strict clean-signature proxy `3043/6093 = 49.94%`. Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260519-181626_post_wave601_cdxlandscape_head_verified`. The next queue head is `0x00544fc0 CDXLandscape__BuildVertexBuffer`.

Static retail evidence only: runtime terrain rendering, exact CDXLandscape/CLandscape/CLandscapeTexture/CVBuffer/CIBuffer/CDXSurf layouts, exact source-body identity, BEA patching, and rebuild parity remain unproven.

## Wave602 Core Terrain-Data Note (2026-05-19)

Wave602 hardened the next four live queue rows in this file:

```text
void __fastcall CDXLandscape__BuildVertexBuffer(void * this)
void __fastcall CDXLandscape__Reset(void * this)
void __fastcall CDXLandscape__LoadCloudShadowTexture(void * this)
void __thiscall CDXLandscape__SetTileData(void * this, void * tile_context, int record_index)
```

Evidence:

- `CDXLandscape__BuildVertexBuffer` locks the vertex buffer at `this+0x28`, emits a `0x41` by `0x41` grid of `0x14`-byte vertices, samples `CHeightField__GetHeightSamplePacked16(&DAT_006fadc8, x, y)` every 8 units, scales heights through `DAT_006fbdf4`, and unlocks before plain `RET`.
- `CDXLandscape__Reset` destroys/rebuilds the `+0x24` resource-record array, resets the `CLandscapeTexture` update queue, allocates one resource record for non-multiplayer or two for multiplayer, calls `CDXLandscape__CreateMipLevels`, rebuilds the vertex buffer, fills `64x64` tile records with clamped shadow-height and complexity data, resets patch slots, invalidates the landscape texture cache, and calls `CDXSurf__LoadWavesTexture`.
- `CEngine__InitResources` calls `CDXLandscape__LoadCloudShadowTexture`, which invokes `CTexture__FindTexture("clouds_shadow.tga", 4, 0, -1, 1, 1)` and stores the returned pointer at `this+0x38`.
- `CEngine__UpdatePos` checks `engine+0x4a8`, loads the landscape object from `engine+0x10`, pushes its stack camera/context argument and `engine+0x4ac`, then calls `CDXLandscape__SetTileData`; `RET 0x8` proves the two-stack-argument shape, and the helper stores `tile_context` at `resource_record+0x10` for `record_index * 0x34`.

Post-Wave602 queue telemetry is `6093` total, `3092` commented, `3001` commentless, `1320` exact-undefined signatures, and `1073` `param_N`; comment-backed proxy `3092/6093 = 50.75%`; strict clean-signature proxy `3047/6093 = 50.01%`. Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260519-184356_post_wave602_cdxlandscape_core_verified`. The next queue head is `0x00545410 CDXLandscape__Render`.

Static retail evidence only: runtime terrain rendering, runtime cloud-shadow/waves behavior, resource ownership under lost-device/reset conditions, exact CDXLandscape/CLandscape/CLandscapeTexture/CVBuffer/CIBuffer/CDXSurf layouts, exact source-body identity, BEA patching, and rebuild parity remain unproven.

## Wave603 Render Note (2026-05-19)

Wave603 hardened the next two live queue rows in this file:

```text
void __thiscall CDXLandscape__Render(void * this, void * engine_context_470, int record_index)
void __thiscall CDXLandscape__RenderTerrain(void * this, int record_index)
```

Evidence:

- `CDXEngine__Render` calls `CDXLandscape__Render` only when `engine+0x4a8` is enabled, passes `ECX=engine+0x10`, pushes the value at `engine+0x470`, and pushes the active view/resource record index; `RET 0x8` proves the two-stack-argument shape.
- `CDXLandscape__Render` resets terrain resources when `DAT_0089ce44` changes, forwards both stack arguments to `CDXLandscape__UpdateLOD`, builds the world matrix from `DAT_008c0280..DAT_008c028c` plus the 12 dwords at `DAT_008aa9c0`, changes render-state/cache flags, applies cached lights with flag `1`, calls `CDXLandscape__RenderTerrain(record_index)`, then restores cached-light state with flag `0`.
- `CDXLandscape__RenderTerrain` computes `this+0x24 + record_index*0x34`, updates cloud-shadow scroll offsets only for record `0`, runs validation passes through `CWaterRenderSystem__ValidateVBufferAndMarkReady`, configures texture stages for `this+0x30`, `DAT_0067a7d0`, and `this+0x38`, binds `this+0x2c` as the index buffer and `this+0x28` as the vertex buffer, draws base/LOD tile ranges, and conditionally calls `CDXLandscape__RenderShadowMap(0)`.

Post-Wave603 queue telemetry is `6093` total, `3094` commented, `2999` commentless, `1318` exact-undefined signatures, and `1073` `param_N`; comment-backed proxy `3094/6093 = 50.78%`; strict clean-signature proxy `3049/6093 = 50.04%`. Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260519-191021_post_wave603_cdxlandscape_render_verified`. The next queue head is `0x00546220 CDXLandscape__SetRenderTarget`.

Static retail evidence only: exact `engine_context_470` class semantics, matrix/light-state semantics, texture-stage/resource-record layouts, runtime terrain/shadow rendering, exact source-body identity, BEA patching, and rebuild parity remain unproven.

## Wave604 Target / Shadow Note (2026-05-19)

Wave604 hardened the next five live queue rows in this file:

```text
bool __thiscall CDXLandscape__SetRenderTarget(void * this, void * target_surface)
void __thiscall CDXLandscape__ReleaseRenderTarget(void * this)
void __thiscall CDXLandscape__ReleaseSurfaces(void * this)
bool __thiscall CDXLandscape__RenderShadowMap(void * this, int record_index)
void __thiscall CDXLandscape__RenderTileRange(void * this, int x_min, int x_max, int z_min, int z_max)
```

Evidence:

- `CGame__Render` and `CDXLandscape__RenderShadowMap` call `CDXLandscape__SetRenderTarget` with a stack/local two-surface save pair in implicit `this`/ECX and one pushed `target_surface`; `RET 0x4` proves the one-stack-argument shape.
- `CDXLandscape__SetRenderTarget` captures current target/depth surfaces into the save pair, queries an auxiliary surface/pointer from `target_surface` through vtable slot `0x48`, updates device target/depth state through slots `0x94/0x9c`, logs `Failed SRT` / `Failed SDSS`, disables `DAT_009c6480` on failures, releases the auxiliary surface on success, and returns `AL` as the success flag.
- `CDXLandscape__ReleaseRenderTarget` is ECX-only and restores device target/depth state from the local surface pair before releasing/nulling both entries.
- `CDXLandscape__ReleaseSurfaces` is ECX-only and releases/nulls the same two-surface pair without issuing restore calls; xrefs include `CGame__Render` final/unwind paths.
- `CDXLandscape__RenderShadowMap` is called from `CDXLandscape__RenderTerrain` with `record_index 0`, guards `DAT_009c648c`, non-multiplayer state, and required `this+0x08/0x0c/0x18/0x1c` resources, switches to the shadow target at `this+0x08`, draws base/LOD terrain, calls `CWaterRenderSystem__RenderShadowPass(DAT_0089c9b4)`, restores target/depth surfaces and render states, and returns `AL`.
- `CDXLandscape__RenderTileRange` is called by `CDXEngine__RenderMultipassLayerA` with four coordinate bounds and `ECX=DAT_0089c9b0`; `RET 0x10` proves the four-stack-argument shape. The body averages `x_min/x_max` and `z_min/z_max`, samples `CStaticShadows__SampleShadowHeightBilinear`, clamps to `0..0x3f` tile indices, binds tile CVBuffers at `+0x0c`, selects `DAT_009c64dc` material records from tile bytes `+0x10/+0x11`, validates through `DAT_009c7c58`, and draws indexed primitives.

Post-Wave604 queue telemetry is `6093` total, `3099` commented, `2994` commentless, `1313` exact-undefined signatures, and `1073` `param_N`; comment-backed proxy `3099/6093 = 50.86%`; strict clean-signature proxy `3054/6093 = 50.12%`. Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260519-194745_post_wave604_cdxlandscape_target_shadow_verified`. The next queue head is `0x00546b10 CDXLandscape__ResetCameraPosition`.

Static retail evidence only: exact D3D interface semantics, COM/surface ownership lifetime, CDXLandscape/resource/tile-record layouts, runtime terrain/shadow rendering, exact source-body identity, BEA patching, and rebuild parity remain unproven.

## Wave605 LOD / Damage Note (2026-05-19)

Wave605 hardened the next four live queue rows tied to CDXLandscape LOD and landscape damage:

```text
void __fastcall CDXLandscape__ResetCameraPosition(void * this)
void __thiscall CDXLandscape__UpdateLOD(void * this, void * engine_context_470, int record_index)
void __stdcall CDXEngine__ApplyLandscapeDamageStamp(float world_x, float world_z, int stamp_value)
double __stdcall CDXEngine__ComputeLandscapeTileComplexityScore(uint tile_index)
```

Evidence:

- `CDXLandscape__ResetCameraPosition` is an ECX-only helper; all five fresh callsites load `ECX` from `DAT_0089c9b0`, and the plain `RET` body writes the `0x4996b438` / `1234567.0f` sentinel into resource-record camera/cache slots at `+0x14` and, for multiplayer, `+0x48`.
- `CDXLandscape__UpdateLOD` has `RET 0x8`; `CDXEngine__Render` pushes the active viewpoint/record index and `engine+0x470` before calling with `ECX=engine+0x10`, while `CDXLandscape__Render` forwards its `engine_context_470` and `record_index` stack arguments after reset.
- `CDXLandscape__UpdateLOD` computes `this+0x24 + record_index*0x34`, iterates the `64x64` tile records, invalidates stale patch slots, allocates patch slots through `CDXPatchManager__AllocatePatchSlot`, queues `CLandscapeTexture` updates, writes LOD ranges into the index buffer, and flushes the texture update queue.
- `CDXEngine__ApplyLandscapeDamageStamp` has `RET 0xc`, consumes `world_x/world_z` plus `stamp_value`, derives a stamp width from `1 << abs(stamp_value)`, calls `CDamage__RemoveCellEntryByCoords` or `CDamage__InsertCellEntry`, and marks affected landscape texture/patch records under `DAT_0089c9b0`; the orphan `0x004da4fd` callsite is supplemental call evidence only.
- Wave996 (`cdamage-residual-review-wave996`) re-read the adjacent CDamage helpers read-only: `0x00440eb0 CDamage__InsertCellEntry` and `0x00440f80 CDamage__RemoveCellEntryByCoords` remain the saved Wave346 cell-entry signatures called from `CDXEngine__ApplyLandscapeDamageStamp`. Runtime terrain damage/decal behavior remains separate proof.
- `CDXEngine__ComputeLandscapeTileComplexityScore` has `RET 0x4`; `CDXLandscape__Reset` passes `tile_index`, the body uses global heightfield pointers/scales rather than `ECX`, samples a `0x9 by 0x9` height window through `DAT_006fbdf0`, evaluates three subdivision levels, multiplies by `DAT_006fbdf4`, returns double, and the caller casts the result to float.

Post-Wave605 queue telemetry is `6093` total, `3103` commented, `2990` commentless, `1311` exact-undefined signatures, and `1071` `param_N`; comment-backed proxy `3103/6093 = 50.93%`; strict clean-signature proxy `3058/6093 = 50.19%`. Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260519-201654_post_wave605_cdxlandscape_lod_damage_verified`. The next queue head is `0x00547d40 DXMemBuffer__SetBufferSize`.

Static retail evidence only: exact `engine_context_470` class semantics, CDXLandscape resource/tile/patch layouts, damage-entry layout, terrain deformation behavior, runtime LOD rendering, exact source-body identity, BEA patching, and rebuild parity remain unproven.

## Wave570 Render Validation Tail Note (2026-05-19)

Wave570 hardened `CDXLandscape__ValidateDeviceAndUpdateValidSoFar` at `0x00527d20` to `bool __thiscall CDXLandscape__ValidateDeviceAndUpdateValidSoFar(void * this)`. Plain `RET` read-back proves the helper is ECX-only. The body checks the render validation record accepted flag at `this+0x10`, calls `CEngine__DeviceCall118_WithZeroOut(&DAT_00855bb0)` when validation is still pending, logs `RM: Failed ValidSoFar...` on failure, and decrements `this+0x0c` only on the nonzero failure path that returns false.

Static retail evidence only: the current `CDXLandscape` owner prefix is retained as the saved entry name, but xrefs also come from battle-line, mesh, surf, and water render paths. Runtime D3D validation behavior, exact render-record class/layout, exact source identity, BEA patching, and rebuild parity remain unproven.

## Parent
- [../README.md](../README.md)

## Wave1151 Current-Risk Tag Normalization

Wave1151 tag-only normalization also covers `0x00403ff0 CResourceDescriptorTable__DestroyEmbeddedDescriptor_Thunk` as a score21 current-risk row. It confirms the Wave982 resource-descriptor cleanup-thunk boundary and adds Wave1151/current-risk tags only; no rename, signature, comment, boundary, or byte change was made. Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260605-201419_post_wave1151_mixed_score21_current_risk_review_verified`. Runtime behavior, exact layouts, exact source-body identity, BEA patching behavior, gameplay outcomes, visual QA, and rebuild parity remain separate proof.
