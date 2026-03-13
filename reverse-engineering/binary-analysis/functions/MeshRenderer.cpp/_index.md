# MeshRenderer.cpp Functions

> Source File: MeshRenderer.cpp | Binary: BEA.exe
> Debug Path: 0x00630178 (`C:\dev\ONSLAUGHT2\MeshRenderer.cpp`)

## Overview

MeshRenderer handles the actual rendering of 3D mesh objects to the screen. This system manages:
- Mesh type classification and render state handling
- Particle effect attachment for special mesh types
- Material/texture lookup and application
- Position transforms and matrix operations
- Debug/wireframe rendering modes

## Functions

| Address | Name | Purpose | Size |
|---------|------|---------|------|
| 0x004b6350 | CMeshRenderer__RenderMesh | Main mesh rendering dispatch function | ~1848 bytes |

## Function Details

### CMeshRenderer__RenderMesh (0x004b6350)

**Signature:** `void CMeshRenderer__RenderMesh(int* position, undefined4* matrix, int* meshData, int* material, int* particleSystem, undefined4 param6, uint flags)`

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
   - Debug/wireframe path: Calls `FUN_0053d760()` with color 0xff7f7f7f (gray)
   - Alternative path: Calls `FUN_004d5e30()` when meshData[0x40] is set

**Flag Bits (param_7):**
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
- `FUN_004cb040()` - Particle system initialization
- `Transform__Unk_00403650()` - Position/matrix update helper
- `FUN_00550ca0()` - Transform setup (x, y, z components)
- `CMeshRenderer__RenderMeshCore()` - Main mesh draw call
- `FUN_0053d760()` - Debug/wireframe mesh draw
- `FUN_004d5e30()` - Alternative mesh rendering

### Exception Handler (0x005d3ac0)

**Note:** This is an SEH (Structured Exception Handling) unwind handler for the RenderMesh function, not a standalone function. It references line 0x207 (519) in the source file for cleanup during stack unwinding.

## Key Observations

1. **Mesh Type System:** The renderer uses a type discriminator at offset 0x23 (0x8C bytes into the mesh structure) to determine rendering behavior. Types 5 and 6 have special handling.

2. **Particle Integration:** Type 5 meshes can have attached particle systems, with the renderer managing their positions. The magic value 10000.0f (0x461c4000) appears to mark uninitialized positions.

3. **LOD System:** When flag bit 4 is set, the renderer checks material LOD levels via virtual calls at offsets 0x1c, potentially skipping render based on `meshData[0x2f]` and `meshData[0x2d]` thresholds.

4. **Debug Rendering:** Global flag `DAT_0089ce54` bit 2 enables a debug render path that uses a gray color (0xff7f7f7f) and reads material properties from `meshData[0x3f]`.

5. **Default Texture Fallback:** When materials lack proper textures, the system falls back to "meshtex_default.tga" with default specular values (0.1f, 0.1f, 0.1f = 0x3dcccccd).

## Related Systems

- **ParticleManager.cpp** - Particle effect creation and management
- **texture.cpp** - Texture loading and caching
- **mesh.cpp** - Mesh data structures and loading

---
*Discovered via Phase 1 xref analysis (Dec 2025)*
