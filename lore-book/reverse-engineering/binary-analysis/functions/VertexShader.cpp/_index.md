# VertexShader.cpp Function Analysis

**Source File:** `C:\dev\ONSLAUGHT2\VertexShader.cpp`
**Debug String Address:** `0x0063cf78`
**Analysis Date:** December 2025

## Overview

VertexShader.cpp implements the `CVertexShader` class, which manages GPU vertex shader programs for hardware-accelerated 3D rendering in Battle Engine Aquila. The class handles shader creation, compilation, caching, and cloning operations using DirectX 8 shader assembly.

## Functions Found (13 mapped; no weak helpers remain)

| Address | Name | Purpose |
|---------|------|---------|
| `0x00501800` | `CVertexShader__CVertexShader` | Constructor - initializes shader object |
| `0x00502060` | `CVertexShader__Create` | Factory method - creates or retrieves cached shader |
| `0x005022a0` | `CVertexShader__LoadFromFile` | Loads shader code from file or compiled blob |
| `0x00502420` | `CVertexShader__CompileShader` | Compiles shader assembly via D3DXAssembleShader |
| `0x00503f90` | `CVertexShader__Clone` | Deep copies a shader object with all resources |
| `0x005019d0` | `CVertexShader__QueryDeviceCapsAndSetGlobalSupportFlag` | Reads device caps and updates global VS-enabled support flag (`DAT_00854e6c`) |
| `0x00502290` | `CVertexShader__DecrementLiveReferenceCount` | Release helper that decrements shader live-reference counter at `+0x30` |
| `0x005027f0` | `CVertexShader__LoadCompiledShaderBlobFromVSOFile` | Opens `Shaders/%s.vso`, loads bytecode blob, and issues device create-shader call |
| `0x00503ac0` | `CVertexShader__BuildAndCreateRenderInfoShader` | Builds dynamic render-state declaration/token stream and creates active render-info shader |
| `0x00503dd0` | `CVertexShader__AppendDeclarationNamesToDebugString` | Debug formatter for declaration-token names during shader declaration dumps |
| `0x00501ba0` | `CVertexShader__GetVertexDeclarationToken` | Maps shader-type field (`+0x2C`) to the device vertex-declaration token used by `CEngine__SetShaderObject` |
| `0x00501cd0` | `CVertexShader__ApplyRenderStateShaderConstants` | Uploads projection/view and render-state constant blocks for the active render-state shader path |
| `0x00502920` | `CVertexShader__ApplyCustomRenderStateShaderConstants` | Expanded/custom constant-upload path used when shader custom-state flag (`+0x34`) is enabled |

## Detailed Function Analysis

### CVertexShader__CVertexShader (0x00501800)

**Purpose:** Constructor that initializes a new CVertexShader object.

**Key Operations:**
- Sets vtable pointer to `0x005dfbc4`
- Zeroes out member fields (offsets 0x08-0x24)
- Calls `CShaderBase__Init` (base class initialization)
- Links shader into global shader list via `DAT_00854e68` (linked list head)
- Initializes shader version to 9 (offset 0x2C = `in_ECX[0xb]`)

**Global Data:**
- `DAT_00854e68` - Head of global shader linked list

**Object Layout (partial):**
```
+0x00: vtable pointer
+0x04: unknown (saved/restored in Clone)
+0x08-0x24: zeroed fields (8 dwords)
+0x28: ref count (offset 0x0A)
+0x2C: shader version (0x0B) - initialized to 9
+0x30: ref count 2 (offset 0x0C)
+0x34: is_compiled flag (offset 0x0D)
+0x38: compiled_data (offset 0x0E)
+0x3C: compiled_size (offset 0x0F)
+0x40: constant_table_ptrs (offset 0x10)
+0x44: constant_counts (offset 0x11)
+0x48: source_code (offset 0x12)
+0x4C: source_size (offset 0x13)
+0x50: shader_bytecode (offset 0x14)
+0x54: bytecode_size (offset 0x15)
+0x58: next_shader (offset 0x16) - linked list pointer
```

---

### CVertexShader__Create (0x00502060)

**Purpose:** Factory method that creates a new shader or returns a cached existing one.

**Parameters:**
- `param_1` (char*): Shader name/path
- `param_2` (int): Shader ID/handle
- `param_3` (int): Shader version/type
- `param_4` (char*): Pre-compiled shader data (optional)
- `param_5` (uint): Pre-compiled data size
- `param_6` (undefined4): Additional flags

**Key Operations:**
1. Checks `DAT_0063c108` (shaders enabled flag) - returns NULL if disabled
2. Searches global shader list for existing matching shader
3. If pre-compiled data provided (`param_4 != NULL`):
   - Matches by data content and size
4. If loading from file:
   - Matches by name (via `stricmp` (0x00568390, was `FUN_00568390`)) and ID
5. If no match found:
   - Allocates 0x5C bytes for new CVertexShader object
   - Calls constructor at `0x00501800`
   - Calls `LoadFromFile` or sets up pre-compiled data
6. Increments reference count on success

**Return:** Pointer to CVertexShader object or NULL on failure

**Error Code:** Returns `0x80004005` (E_FAIL) on failure

---

### CVertexShader__LoadFromFile (0x005022a0)

**Purpose:** Loads shader source code from a file and prepares it for compilation.

**Parameters:**
- `param_1` (char*): Shader name (copied to object)
- `param_2` (char*): File path or pre-compiled data
- `param_3` (int): Shader version
- `param_4` (uint): Data size (-1 means load from file)

**Key Operations:**
1. Calls virtual method at vtable+0x0C (likely `Lock`)
2. Copies shader name to object (offset 0x08, up to 72 bytes)
3. Sets `is_compiled` flag to 0 (offset 0x34)
4. Sets shader version (offset 0x2C)
5. If `param_4 == 0xFFFFFFFF`:
   - Loads from file using `FUN_00579a9a` (D3DXAssembleShaderFromFile wrapper)
   - On failure, logs error via `DebugTrace` and `FatalError_LocalizedStringId`
6. Otherwise:
   - Allocates memory and copies pre-compiled data
7. Calls virtual method at vtable+0x08 (likely `Unlock`)

**Return:** 0 on success, `0x80004005` on failure

---

### CVertexShader__CompileShader (0x00502420)

**Purpose:** Compiles shader assembly source into GPU bytecode using D3DXAssembleShader.

**Key Operations:**
1. Frees existing compiled shader (offset 0x50) if present
2. Detects shader version by searching for "vs.1.1" or "vs.1.0" strings
3. Builds vertex declaration string based on input semantics found:
   - `dcl_position v0` - always added
   - `dcl_blendweight0 v11` - if blend weights used
   - `dcl_normal v3` - if normals used
   - `dcl_color v5` - if vertex colors used
   - `dcl_texcoord v7` - if texture coordinates used
4. Patches shader source to insert declarations after version string
5. Removes fog output references (`oFog.x` replaced with spaces)
6. Calls `FUN_00579a9a` (D3DXAssembleShader wrapper)
7. On failure, logs detailed error via:
   - `HResultToString` (`0x005be628`) - HRESULT to string conversion
   - Error message: "D3DXAssembleShader failed for %s"
8. Copies compiled bytecode to object (offset 0x50)
9. Frees source code buffer

**Shader Version Strings:**
- `0x0063d038`: "vs.1.0"
- `0x0063d040`: "vs.1.1"

**Vertex Declaration Strings:**
- `0x0063d020`: "vs.1.1\ndcl_position v0\n"
- `0x0063d004`: "dcl_blendweight0 v11\n"
- `0x0063cff0`: "dcl_normal v3\n"
- `0x0063cfdc`: "dcl_color v5\n"
- `0x0063cfc8`: "dcl_texcoord v7\n"

**Error String:**
- `0x0063cf9c`: "D3DXAssembleShader failed for %s"

---

### CVertexShader__Clone (0x00503f90)

**Purpose:** Creates a deep copy of a shader object, duplicating all resources.

**Parameters:**
- `param_1`: Unknown
- `param_2`: Shader index (used for debug file naming)

**Key Operations:**
1. Allocates new 0x5C byte object
2. Calls constructor
3. Preserves vtable, field[1], and linked list pointer
4. Copies object data via `FUN_00423960` (memcpy wrapper)
5. Deep copies each resource if present:
   - Compiled data (offset 0x38/0x3C)
   - Constant counts array (offset 0x44) - size from `DAT_00854e74`
   - Constant table pointers (offset 0x40)
   - Shader bytecode (offset 0x50/0x54)
   - Source code (offset 0x48/0x4C)
6. If `DAT_00662f35` is set (debug mode):
   - Loads shader from file "shader%03d.i" using `param_2` as index
7. Calls `CompileShader` to rebuild
8. Cleans up temporary source buffer
9. Calls virtual method vtable+0x08 (Unlock)

**Global Data:**
- `DAT_00854e74` - Number of shader constants
- `DAT_00662f35` - Debug/development mode flag

## Global Variables

| Address | Name | Purpose |
|---------|------|---------|
| `0x00854e68` | g_pShaderList | Head of global CVertexShader linked list |
| `0x00854e74` | g_nShaderConstants | Number of shader constant slots |
| `0x0063c108` | g_bShadersEnabled | Flag to enable/disable vertex shaders |
| `0x00662f35` | g_bDebugMode | Debug mode flag for shader reloading |

## Related Functions (Called)

| Address | Likely Name | Purpose |
|---------|-------------|---------|
| `0x005490e0` | MemAlloc | Memory allocation with debug info |
| `0x00549220` | MemFree | Memory deallocation |
| `0x00579a9a` | D3DXAssembleShader | DirectX shader assembly wrapper |
| `0x00568390` | strcmp | String comparison |
| `0x00512ca0` | CShaderBase__Init | Base class initialization |
| `0x00423960` | memcpy_wrapper | Memory copy with size/count |
| `0x0042d080` | Assert | Debug assertion |
| `0x0040c640` | DebugPrint | Debug output logging |
| `0x005be628` | HResultToString | Convert HRESULT to error string |

## Technical Notes

1. **Shader Caching:** Shaders are cached in a global linked list (`0x00854e68`) to avoid recompilation. The `Create` function searches this list before creating new shaders.

2. **DirectX 8 Shaders:** The code targets DirectX 8 vertex shader assembly (vs.1.0/vs.1.1), not the later HLSL format.

3. **Vertex Declaration Patching:** The compiler automatically inserts vertex input declarations based on which registers are referenced in the shader source.

4. **Fog Output Removal:** The `.oFog.x` output is explicitly disabled by replacing it with spaces - possibly due to hardware compatibility issues.

5. **Reference Counting:** Shaders use reference counting (offset 0x30) to manage lifetime. The `Create` function increments this on each use.

6. **Debug Shader Loading:** When `DAT_00662f35` is set, `Clone` can reload shader source from numbered files (shader000.i, shader001.i, etc.) for runtime modification.

## Cross-References Summary

The VertexShader.cpp debug string at `0x0063cf78` is referenced 15 times:
- 2 refs from `CVertexShader__Create` (allocation)
- 1 ref from `CVertexShader__LoadFromFile` (allocation)
- 2 refs from `CVertexShader__CompileShader` (allocations)
- 8 refs from `CVertexShader__Clone` (multiple allocations)
- 2 refs from unwind handlers (exception handling)
