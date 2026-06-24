# MeshRenderer.cpp Functions

> Source File: MeshRenderer.cpp | Binary: BEA.exe
> Debug Path: 0x00630178 (`C:\dev\ONSLAUGHT2\MeshRenderer.cpp`)

## Overview

> **Queue status (2026-05-26):** Ghidra export-contract closure **6113/6113** (Wave900: every function commented; clean-signature proxy; not evidence-grade semantics). Lines below that reference a "next raw commentless" row are **archival wave progress**, not open work.

MeshRenderer handles the actual rendering of 3D mesh objects to the screen. This system manages:
- Mesh type classification and render state handling
- Particle effect attachment for special mesh types
- Material/texture lookup and application
- Position transforms and matrix operations
- Debug/wireframe rendering modes

## Wave758 MeshRenderer.cpp Unwind Read-Back

Wave758 static read-back (`unwind-continuation-wave758`, `wave758-readback-verified`) hardened `0x005d3ac0 Unwind@005d3ac0` as a compiler-generated SEH unwind allocation-cleanup callback. DATA scope-table xref `0x0061c6ec` points at the body; instruction/decompile evidence calls `OID__FreeObject_Callback` on `*(EBP+0x14)` with MeshRenderer.cpp debug path `0x00630178`, line token `0x10`, and allocation/type value `0x207`. Verified backup: `G:\GhidraBackups\BEA_20260523-123821_post_wave758_unwind_continuation_verified`. Exact parent source-body identity, runtime exception behavior, runtime cleanup behavior, BEA patching, and rebuild parity remain deferred.

## Functions

| Address | Name | Purpose | Size |
|---------|------|---------|------|
| 0x004b6350 | CMeshRenderer__RenderMesh | Main mesh rendering dispatch function | ~1848 bytes |
| 0x00549570 | CMeshRenderer__RenderMeshCore | Central caller-cleaned mesh draw core hardened by Wave866 | ~2093 instructions |
| 0x0054d530 | CMeshRenderer__RenderMeshWithLayerPasses | CDXMeshVB-style group/layer render pass helper called by `CMeshRenderer__RenderMeshCore` | ~2936 bytes |

## Function Details

### CMeshRenderer__RenderMesh (0x004b6350)

**Signature:** `void __cdecl CMeshRenderer__RenderMesh(void * world_position_vec4, void * transform_matrix12, void * mesh_part, void * render_context, void * effect_owner, int render_slot_or_mode, byte render_flags)`

**Purpose:** Main entry point for rendering a mesh object. Handles multiple mesh types and render states.

**Key Behaviors:**

1. **Early Exit Conditions:**
   - Returns immediately if mesh type is 2 or 4 and flag bit 2 is not set
   - Returns if flag bit 0 is set (visibility culled?)

2. **Mesh Type Handling (meshData[0x23]):**
   - Type 2, 4: Early exit under certain flag conditions
   - Type 5: Special particle-attached mesh rendering
   - Type 6: Redirects to sub-mesh at meshData[0x49]

3. **Particle Effect Integration:**
   - For type 5 meshes, creates particle effects via `CParticleManager__CreateEffect()`
   - Manages particle position updates at offsets 0x10-0x13 and 0x20-0x23
   - Special handling for position value 0x461c4000 (10000.0f - likely "uninitialized" marker)

4. **Material/Texture Handling:**
   - References default texture "meshtex_default.tga" at 0x00625498
   - Uses `CTexture__FindTexture()` for texture lookup
   - Caches default texture in global `DAT_0089ce84`

5. **Render Paths:**
   - Normal path: Calls `CMeshRenderer__RenderMeshCore()` for standard mesh rendering
   - Debug/wireframe path: Calls `CThing__RenderDebugVolumeOverlay()` with color 0xff7f7f7f (gray)
   - Alternative path: Calls `FUN_004d5e30()` when meshData[0x40] is set

**Flag Bits (`render_flags`):**
- Bit 0 (0x01): Skip rendering (culled/invisible)
- Bit 2 (0x04): Force render regardless of mesh type
- Bit 4 (0x10): Check material LOD levels
- Bit 5 (0x20): Has environment map (set based on material query)

**Global State:**
- `DAT_0089ce54`: Global render flags (bit 2 = debug mode?)
- `DAT_0089ce5c`: Alternative render mode flag
- `DAT_0089ce84`: Cached default texture pointer
- `DAT_00704e64`: Environment map index
- `DAT_00704df8`: Default transform matrix (48 bytes)

**Called Functions:**
- `CParticleManager__CreateEffect()` - Creates attached particle effects
- `CTexture__FindTexture()` - Texture lookup
- `OID__AllocObject()` - Memory allocation (8 bytes, alignment 16)
- `ParticleEffectLink__PushGlobalList()` - Wave822-corrected effect-owner link global registration helper at `0x004cb040`
- `Transform__Unk_00403650()` - Position/matrix update helper
- `FUN_00550ca0()` - Transform setup (x, y, z components)
- `CMeshRenderer__RenderMeshCore()` - Main mesh draw call
- `CThing__RenderDebugVolumeOverlay()` - Wave593-saved debug-volume overlay helper
- `FUN_004d5e30()` - Alternative mesh rendering

### Exception Handler (0x005d3ac0)

**Note:** This is an SEH (Structured Exception Handling) unwind handler for the RenderMesh function, not a standalone function. It references line 0x207 (519) in the source file for cleanup during stack unwinding.

### Wave866 mesh renderer core (0x00549570)

Wave866 static read-back (`meshrenderer-core-wave866`, `wave866-readback-verified`) hardened `0x00549570 CMeshRenderer__RenderMeshCore` as `void __cdecl CMeshRenderer__RenderMeshCore(float world_position_x, float world_position_y, float world_position_z, float world_position_w, float * transform_matrix12, void * mesh_part, void * render_context, void * effect_owner, int render_slot_or_mode, int render_flags, int reserved_zero, void * world_position_vec4)`. The observed caller is `0x004b6a82 CMeshRenderer__RenderMesh`: it copies four world-position dwords by value, pushes the transform pointer and render context payload, and cleans `0x30` bytes after return.

Static evidence ties this high-importance connective renderer infrastructure to a `0x1e54-byte stack frame`, mesh-type dispatch from `mesh_part+0x8c`, animated pose/interpolation through `CMCMech__BuildInterpolatedPoseAndAnchor`, `CVBufTexture` vertex/index/batch rendering, and `CMeshRenderer__RenderMeshWithLayerPasses` handoffs at `0x0054a4b6` and `0x0054b265`. Verified backup: `G:\GhidraBackups\BEA_20260525-162911_post_wave866_meshrenderer_core_verified`. Post-Wave866 strict proxy is `5820/6105 = 95.33%`; next raw commentless row is `0x005501d0 CVBufTexture__GetVertexWriteCursorPlusOne`. Exact renderer/mesh/pose layouts, exact source identity, visual/runtime rendering behavior, BEA patching, and rebuild parity remain deferred.

## Key Observations

1. **Mesh Type System:** The renderer uses a type discriminator at offset 0x23 (0x8C bytes into the mesh structure) to determine rendering behavior. Types 5 and 6 have special handling.

2. **Particle Integration:** Type 5 meshes can have attached particle systems, with the renderer managing their positions. The magic value 10000.0f (0x461c4000) appears to mark uninitialized positions.

3. **LOD System:** When flag bit 4 is set, the renderer checks material LOD levels via virtual calls at offsets 0x1c, potentially skipping render based on `meshData[0x2f]` and `meshData[0x2d]` thresholds.

4. **Debug Rendering:** Global flag `DAT_0089ce54` bit 2 enables a debug render path that uses a gray color (0xff7f7f7f) and reads material properties from `meshData[0x3f]`.

5. **Default Texture Fallback:** When materials lack proper textures, the system falls back to "meshtex_default.tga" with default specular values (0.1f, 0.1f, 0.1f = 0x3dcccccd).

## 2026-05-08 Read-Back Guard

`tools/mesh_renderer_readback_probe.py --check` consumes the existing ignored `CMeshRenderer__RenderMesh` decompile export and verifies the current index row, normal dispatch to `CMeshRenderer__RenderMeshCore`, particle attachment context, debug render context, and default texture fallback tokens. This is public-safe renderer dispatch evidence only. Exact full source parity remains unavailable because `MeshRenderer.cpp` is not present in this checkout, and this does not prove Goodies model-viewer runtime playback or WinUI textured/material rendering.

## Wave822 Particle Owner-Link Update

Wave822 particle manager owner links (`particle-manager-owner-links-wave822`) corrected `0x004cb040` from old `CWorldPhysicsManager__PushNodeGlobalList` to `0x004cb040 ParticleEffectLink__PushGlobalList`, matching the ECX-node body that pushes an effect/owner-link node into `DAT_0082b3e8`. The same wave hardened `0x004caf30 CParticleManager__ClearParticleOwnerBacklinks`, `0x004cb080 CParticleManager__PruneDeadOwnerLinks`, and `0x004cbc60 CParticleManager__UpdateRenderNodesAndResetState`. Queue after Wave822 is `5626/6098 = 92.26%`; next raw commentless row is `0x004cd7a0 CWorldPhysicsManager__FindNodeByNameGE`; verified backup `G:\GhidraBackups\BEA_20260524-180249_post_wave822_particle_manager_owner_links_verified`. Exact effect-handle/link-node/render-node/owner layouts, exact source-body identity, runtime particle shutdown behavior, runtime particle/effect behavior, runtime render behavior, BEA patching, and rebuild parity remain deferred.

## Wave452 Render / Sort Hardening

Wave452 saved the seven-stack-argument `CMeshRenderer__RenderMesh` signature above after callsite review from `CMeshPart__RenderAnimatedRecursive` and `CSphere__RenderPartsWithOrientation`. The same pass recorded comment/tag evidence for the particle/effect setup branch, `CDXEngine__SetWorldMatrixElements`, `CMeshRenderer__RenderMeshCore`, and `CThing__RenderDebugVolumeOverlay`. This is static retail evidence only; exact matrix/vector types, concrete renderer/mesh-part layouts, runtime render behavior, and rebuild parity remain unproven.

## Wave593 Debug Volume Overlay Callsite Update

Wave593 saved `0x0053d760 CThing__RenderDebugVolumeOverlay` as a 16-stack-argument, `RET 0x40` debug-volume draw helper. The `CMeshRenderer__RenderMesh` callsite at `0x004b6b8e` copies twelve transform dwords with `MOVSD.REP`, pushes the default texture/material pointer, half-extents/center vectors, and the debug color before calling the helper. Queue telemetry after Wave593 is `6093` functions, `3033` commented, `3060` commentless, `1347` exact-undefined signatures, `1100` `param_N` signatures, comment-backed proxy `3033/6093 = 49.78%`, strict clean-signature proxy `2987/6093 = 49.02%`, and next head `0x0053f040 CVBufTexture__SetStateCacheModeByFlag`. Evidence lives in `release/readiness/ghidra_debug_volume_overlay_wave593_2026-05-19.md` and backup `G:\GhidraBackups\BEA_20260519-140648_post_wave593_debug_volume_overlay_verified`. Runtime debug-render behavior, exact source identity, concrete renderer/mesh-part/debug-volume layouts, BEA patching, and rebuild parity remain unproven.

## Wave610 Layer-Pass Helper Update

Wave610 saved `0x0054d530 CMeshRenderer__RenderMeshWithLayerPasses` as `void __thiscall CMeshRenderer__RenderMeshWithLayerPasses(void * this, void * frame_provider, uint render_flags, void * unused_render_context, void * unused_transform_payload)` with no rename. `RET 0x10` and the two `CMeshRenderer__RenderMeshCore` callsites at `0x0054a4b6` and `0x0054b265` prove four stack arguments after ECX. The receiver is loaded from the caller's `+0x138` field and uses the adjacent CDXMeshVB-style fields for group count, source mesh, shader pointer, stride, FVF/shader state, and primitive selector.

The helper uses `frame_provider` vtable slots `+0x1c` and `+0x18` when present, consumes `render_flags` bits `0x10`, `0x20`, and `0x40`, loops up to six texture layer passes, handles water/reflection paths through `DAT_0089c9c0` and `DAT_0089c9c4`, restores `DAT_0063012c`, disables vertex shaders when required, and restores render state `0xb`. Post-Wave610 queue telemetry is `6093` functions, `3125` commented, `2968` commentless, `1301` exact-undefined signatures, `1059` `param_N` signatures, comment-backed proxy `3125/6093 = 51.29%`, strict clean-signature proxy `3080/6093 = 50.55%`, and next head `0x0054e500 DXPalletizer__InsertColor`. Evidence lives in `release/readiness/ghidra_meshrenderer_layer_passes_wave610_2026-05-20.md` and backup `G:\GhidraBackups\BEA_20260519-224655_post_wave610_meshrenderer_layer_passes_verified`. Runtime rendering, exact source identity, concrete CDXMeshVB/mesh/texture/render-state layouts, BEA patching, and rebuild parity remain unproven.

## Related Systems

- **ParticleManager.cpp** - Particle effect creation and management
- **texture.cpp** - Texture loading and caching
- **mesh.cpp** - Mesh data structures and loading

---
*Discovered via Phase 1 xref analysis (Dec 2025)*
