# texture.cpp Function Mappings

> Functions from texture.cpp mapped to BEA.exe binary
> Debug path: "C:\dev\ONSLAUGHT2\texture.cpp" at 0x00632ef0

## Overview
- **Functions Mapped:** 5
- **Status:** NEW (Dec 2025)
- **Classes:** CTexture, CTextureBase

## Function List

| Address | Name | Status | Description | Link |
|---------|------|--------|-------------|------|
| 0x004f27f0 | CTexture__FindTexture | NAMED | Finds or loads a texture by name | [View](CTexture__FindTexture.md) |
| 0x005d5120 | CTexture__FindTexture_Unwind | NAMED | Exception unwind handler for FindTexture | [View](CTexture__FindTexture_Unwind.md) |
| 0x00556cc0 | CTexture__ctor | NAMED | CTexture constructor - initializes vtable and fields | - |
| 0x004f2710 | CTextureBase__Init | NAMED | Base class initialization | - |
| 0x00556f50 | CTexture__Release | NAMED | Texture cleanup/release | - |

## Recent Headless Semantic Promotions (2026-02-26)

| Address | Name | Status | Description | Link |
|---------|------|--------|-------------|------|
| 0x005894a9 | CTexture__OpenIncludeSourceAndInitBuffer | NAMED | Opens include source (file/provider), allocates buffers, initializes parse span fields | - |
| 0x00589650 | CTexture__InitBufferFromMemorySpan | NAMED | Initializes decode parse span from memory pointer + length and validates bounds | - |
| 0x00598749 | CTexture__HasSameFormatClassId | NAMED | Predicate for texture-comparator helpers; checks format/class-id equality | - |
| 0x00582a99 | CTexture__PackTexels_Dither_Bits332 | NAMED | Dithered texel packer for 8-bit 3-3-2 packed output | - |
| 0x00582bbe | CTexture__PackTexels_Dither_Bits8 | NAMED | Dithered texel packer for 8-bit single-channel output | - |
| 0x00582c8a | CTexture__PackTexels_Dither_Bits565 | NAMED | Dithered texel packer for 16-bit 5-6-5 packed output | - |
| 0x00582dd3 | CTexture__PackTexels_Dither_Bits444 | NAMED | Dithered texel packer for 16-bit 4-4-4 packed output | - |
| 0x00583a94 | CTexture__PackTexels_Dither_A4L4 | NAMED | Dithered texel packer for 4-bit alpha + 4-bit luminance output | - |
| 0x00583ba4 | CTexture__PackTexels_Dither_L16 | NAMED | Dithered texel packer for 16-bit luminance output | - |
| 0x00583c8e | CTexture__PackTexels_Dither_Bits8_8 | NAMED | Dithered texel packer for dual-channel 8-8 packed output | - |
| 0x00583d89 | CTexture__PackTexels_Dither_Bits5_5_5 | NAMED | Dithered texel packer for 5-5-5 packed output | - |
| 0x00583eb3 | CTexture__PackTexels_Dither_Bits8_8_8_Alt | NAMED | Dithered texel packer for alternate-order 8-8-8 packed output | - |
| 0x00583fe5 | CTexture__PackTexels_Dither_Bits8_8_8_8_Alt | NAMED | Dithered texel packer for alternate-order 8-8-8-8 packed output | - |
| 0x00584535 | CTexture__PackTexels_Dither_Bits8_8_FromAuxLookup | NAMED | Dithered 8-8 output path using auxiliary lookup helper per texel | - |
| 0x0058463a | CTexture__PackTexels_Dither_L16_Alt | NAMED | Alternate table-slot variant of dithered 16-bit luminance output | - |
| 0x00584a4c | CTexture__PackTexels_NoDither_Bits16_16_16 | NAMED | Non-dither texel packer writing three 16-bit color channels per texel | - |
| 0x00584b5f | CTexture__UnpackTexels_Bgr8ToFloat4 | NAMED | Unpacks BGR8 source texels into float4 RGBA (alpha forced to 1.0) before optional post-normalization | - |
| 0x00584c04 | CTexture__UnpackTexels_Bgra8ToFloat4 | NAMED | Unpacks BGRA8 source texels into normalized float4 RGBA channels | - |
| 0x00584cc3 | CTexture__UnpackTexels_Bgr8ToFloat4_AlphaOne | NAMED | Unpacks BGR8 source texels into float4 RGBA with forced alpha = 1.0 | - |
| 0x0058579b | CTexture__UnpackTexels_Bits444ToFloat4_AlphaOne | NAMED | Unpacks 4-4-4 packed texels into float4 RGB with alpha forced to 1.0 | - |
| 0x0058586b | CTexture__UnpackTexels_PaletteIndexA8ToFloat4 | NAMED | Expands palette-indexed texels through lookup table and applies 8-bit alpha | - |
| 0x00585cb0 | CTexture__UnpackTexels_Signed8_8_ToFloat4_RG | NAMED | Unpacks signed 8-8 texels into float4 RG lanes with Z/A initialized | - |
| 0x005860ba | CTexture__UnpackTexels_Signed16_16_ToFloat4_RG | NAMED | Unpacks signed 16-16 texels into float4 RG lanes with Z/A initialized | - |
| 0x00586438 | CTexture__UnpackTexels_NormalXY_Signed8_8_ReconstructZ | NAMED | Unpacks signed XY normals and reconstructs Z from unit-length constraint | - |
| 0x0058686f | CTexture__UnpackTexels_CopyRaw128 | NAMED | Raw-copy unpack path copying 128-bit texel records directly | - |
| 0x005869b0 | CTexture__UnpackTexels_Bits16_16_16_ToFloat4 | NAMED | Unpacks 16-16-16 packed texels into float4 RGB with alpha forced to 1.0 | - |
| 0x005876ab | CTexture__WriteTexelBlockWithQuadCache | NAMED | Writes texel blocks through quad cache and flushes completed rows | - |
| 0x00587af0 | CTexture__ReadTexelBlockWithQuadCache | NAMED | Reads texel blocks through quad cache with optional postfilter zeroing | - |

## Key Strings Referenced

| Address | String | Used By |
|---------|--------|---------|
| 0x00632ef0 | "C:\dev\ONSLAUGHT2\texture.cpp" | Debug path |
| 0x00632f10 | "Warning : loading texture %s manually!\n" | CTexture__FindTexture |
| 0x00632ec0 | "Texture '%s' not found in level resource file" | CTexture__FindTexture |
| 0x00632f38 | "Found possible match for texture %s, but mipmaps=%d, wanted %d\n" | CTexture__FindTexture |

## Global Variables

| Address | Type | Purpose |
|---------|------|---------|
| 0x0083d9b0 | CTexture* | Head of texture linked list |
| 0x0083d9b4 | CTexture* | Default/fallback texture |
| 0x0083d9b8 | int | Debug output flag |
| 0x0083d99c | int | Texture count |
| 0x00662f3c | char | Texture loading mode flag |
| 0x00662dd4 | int | Another texture mode flag |

## Analysis Notes

### CTexture__FindTexture (0x004f27f0)

This is the main texture lookup function. It:

1. **Iterates through texture linked list** starting at `DAT_0083d9b0`
2. **Matches by name** using `stricmp` (0x00568390, was `FUN_00568390`)
3. **Validates mipmap count** if param_4 != -1
4. **On cache miss**:
   - Logs warning "Warning : loading texture %s manually!"
   - Allocates 0x158 bytes (344 bytes) for new CTexture
   - Calls constructor via `FUN_00556cc0`
   - Calls virtual load method at vtable offset 0x14
5. **Ref counting**: Increments `texture[0x29]` on success
6. **Fallback**: Returns `DAT_0083d9b4` (default texture) if loading fails and param_5 is set

### CTexture Structure (inferred from constructor)

```
Offset  Size  Purpose
0x00    4     vtable pointer (PTR_FUN_005e59a0)
0x08    128   Name buffer (32 chars via loop init)
0x88    4     Unknown (set to 0)
0x8C    4     Unknown (set to 0)
0x90    4     Unknown (set to 0)
0x94    4     Scale X (0x3f800000 = 1.0f)
0x98    4     Scale Y (0x3f800000 = 1.0f)
0x9C-0xF8  64  Cleared in loop (16 dwords per iteration)
0xA0    4     Next texture in list
0xA4    4     Reference count
0xA8    4     Texture type/format
0x138   4     Unknown (set to 1)
0x148   4     Mipmap count (piVar3[0x52])
0x150   4     Unknown (set to 0)
0x154   4     Unknown (set to 1)
0x155   1     Unknown byte (set to 0)
0x156   2     Unknown word (set to 0xFFFF)
Total: 0x158 (344 bytes)
```

### Call Graph

```
CTexture__FindTexture (004f27f0)
  +-> stricmp (string compare)
  +-> FUN_0042c750 (unknown - texture mode related)
  +-> sprintf (sprintf-like)
  +-> DebugTrace (debug output)
  +-> OID__AllocObject (memory allocation wrapper)
  +-> CTexture__ctor (00556cc0)
  |     +-> CTextureBase__Init (004f2710)
  |     +-> CShaderBase__Init
  +-> CConsole__Printf (error logging)
  +-> CTexture__Release (00556f50)
```

## Cross-References

CTexture__FindTexture has **248 callers** - it's a core function used throughout:
- Model loading
- UI/HUD rendering
- Effects system
- Level loading

## Related
- Debug path string: 0x00632ef0
- Vtable: 0x005e59a0
- Parent: [../README.md](../README.md)
