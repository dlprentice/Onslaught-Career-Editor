# DXTexture.cpp - DirectX Texture Management

**Source File:** `C:\dev\ONSLAUGHT2\DXTexture.cpp`
**Debug Path Address:** `0x0065269c`

## Overview

DXTexture.cpp implements DirectX-specific texture management functionality for the Battle Engine Aquila renderer. This module handles texture loading from AYA resource archives, texture format conversion, mipmap generation, and texture serialization/deserialization.

## Functions (5 total)

| Address | Name | Purpose |
|---------|------|---------|
| `0x00557300` | `CDXTexture__LoadTextureFromFile` | Load texture from file path in AYA archive |
| `0x005586e0` | `CDXTexture__DumpTextureToRGBA` | Convert texture to RGBA format for debugging |
| `0x00559410` | `CDXTexture__CreateMipmaps` | Generate mipmap chain for texture |
| `0x00559be0` | `CDXTexture__Deserialize` | Load texture from serialized data |
| `0x005d7dc0` | `CDXTexture__Deserialize_Unwind` | Exception handler for Deserialize |

## Recent Headless Semantic Promotions (2026-02-26)

| Address | Symbol | Purpose |
|---------|--------|---------|
| `0x0057ca3a` | `CDXTexture__DecodeBmpFromMemory` | Validates BMP memory headers and dispatches in-memory BMP decode path |
| `0x0057ca6a` | `CDXTexture__DecodeFromMemory_WithFallbackCodecs` | Tries multiple in-memory codecs and keeps first successful decode result |
| `0x00591340` | `CDXTexture__PumpDecoderStreamAndFinalize` | Pumps decoder stream callbacks/state machine and finalizes decode state |
| `0x0057d244` | `CDXTexture__Downsample2x2Average32` | Software 2x2 box filter over 32-bit pixels for mip/downscale fallback paths |
| `0x005818b7` | `CDXTexture__PrepareDxtScaleAndQuantizedUV` | Detects DXT2/DXT3 scale mode and quantizes UV-related fields to codec grid |
| `0x00582ef8` | `CDXTexture__PackTexels_Dither_Bits2_10_10_10` | Dithered texel packer for 2-10-10-10 packed output |
| `0x00583041` | `CDXTexture__PackTexels_Dither_Bits8888` | Dithered texel packer for 8-8-8-8 packed output |
| `0x0058318a` | `CDXTexture__PackTexels_Dither_Bits888` | Dithered texel packer for 8-8-8 packed output |
| `0x005832af` | `CDXTexture__PackTexels_Dither_Bits1616` | Dithered texel packer for 16-16 packed output |
| `0x005833a6` | `CDXTexture__PackTexels_Dither_Bits2_10_10_10_Alt` | Dithered texel packer for alternate 2-10-10-10 channel-order output |
| `0x005834ef` | `CDXTexture__PackTexels_Dither_Bits16_16_16_16` | Dithered texel packer for 16-16-16-16 packed output (two dwords per texel) |
| `0x00583670` | `CDXTexture__PackTexels_Dither_PaletteIndexA8` | Palette-distance quantizer writing palette-index plus 8-bit alpha |
| `0x005837b7` | `CDXTexture__PackTexels_Dither_PaletteIndex8` | Palette-distance quantizer writing 8-bit palette-index output |
| `0x00582244` | `CFastVB__PackTexels_Dither_Bits8_8_8_BGR` | Dithered texel packer writing B,G,R byte output |
| `0x00582355` | `CFastVB__PackTexels_Dither_Bits8_8_8_8_ARGB` | Dithered texel packer writing packed ARGB8888 output |
| `0x0058249e` | `CFastVB__PackTexels_Dither_Bits8_8_8_RGB` | Dithered texel packer writing R,G,B byte output |
| `0x005825c3` | `CFastVB__PackTexels_Dither_Bits5_6_5` | Dithered texel packer writing RGB565 output |
| `0x005826e8` | `CFastVB__PackTexels_Dither_Bits5_5_5` | Dithered texel packer writing RGB555 output |
| `0x0058280d` | `CFastVB__PackTexels_Dither_A1R5G5B5` | Dithered texel packer writing A1R5G5B5 output |
| `0x00582950` | `CFastVB__PackTexels_Dither_A4R4G4B4` | Dithered texel packer writing A4R4G4B4 output |
| `0x00583891` | `CFastVB__PackTexels_Dither_L8` | Dithered texel packer writing 8-bit luminance output |
| `0x00583979` | `CFastVB__PackTexels_Dither_A8L8` | Dithered texel packer writing 16-bit A8L8 output |
| `0x0056f260` | `CFastVB__ReleaseBufferAndResetTriplet_0056f260` | Releases owned buffer pointer and clears local span fields (`+0x04/+0x08/+0x0c`) |
| `0x0056f520` | `CFastVB__ReleaseBufferAndResetTriplet_0056f520` | Releases owned buffer pointer and clears local span fields (`+0x04/+0x08/+0x0c`) |
| `0x00573310` | `CFastVB__CountDwordsFromPointerSpan` | Returns dword count from pointer span (`(end - begin) >> 2`) with null guard |
| `0x005759c9` | `CFastVB__ConvertFloat32ArrayToFloat16` | Converts float32 source array into 16-bit half-float destination elements |
| `0x00575dc9` | `CFastVB__HermiteInterpolateVec3` | Cubic Hermite interpolation over four vec3 inputs at parameter `t` |
| `0x005759b6` | `CFastVB__DispatchIndirect_00657014` | Guarded indirect-dispatch thunk calling global function pointer `DAT_00657014` |
| `0x00575a58` | `CFastVB__DispatchIndirect_00657018` | Guarded indirect-dispatch thunk calling global function pointer `DAT_00657018` |
| `0x00575cae` | `CFastVB__DispatchIndirect_00656ff0_ReturnInt` | Guarded indirect-dispatch thunk forwarding args to `DAT_00656ff0` and returning int |
| `0x0057609c` | `CFastVB__DispatchIndirect_00657028` | Guarded indirect-dispatch thunk calling global function pointer `DAT_00657028` |
| `0x00576154` | `CFastVB__DispatchIndirect_00656f58` | Guarded indirect-dispatch thunk calling global function pointer `DAT_00656f58` |
| `0x00576698` | `CFastVB__DispatchIndirect_00656f38` | Guarded indirect-dispatch thunk calling global function pointer `DAT_00656f38` |
| `0x0057674a` | `CFastVB__DispatchIndirect_00657034` | Guarded indirect-dispatch thunk calling global function pointer `DAT_00657034` |
| `0x00574296` | `CFastVB__ComputeFormatMatchPenalty` | Computes weighted mismatch score between format candidates; returns `-1` when incompatible |
| `0x0057437a` | `CFastVB__SelectBestFormatHandler` | Scans format-handler table and selects best candidate using compatibility probes + penalty score |
| `0x005768f1` | `CFastVB__DispatchIndirect_00656f3c` | Guarded indirect-dispatch thunk calling global function pointer `DAT_00656f3c` |
| `0x00576b3a` | `CFastVB__DispatchIndirect_00656fc4` | Guarded indirect-dispatch thunk calling global function pointer `DAT_00656fc4` |
| `0x00576dfd` | `CFastVB__DispatchIndirect_00656f78` | Guarded indirect-dispatch thunk calling global function pointer `DAT_00656f78` |
| `0x005771af` | `CFastVB__DispatchIndirect_00656fb4` | Guarded indirect-dispatch thunk calling global function pointer `DAT_00656fb4` with 4 args |
| `0x005775b0` | `CFastVB__DispatchIndirect_00656fc8` | Guarded indirect-dispatch thunk calling global function pointer `DAT_00656fc8` |
| `0x005776d3` | `CFastVB__DispatchIndirect_00656fcc` | Guarded indirect-dispatch thunk calling global function pointer `DAT_00656fcc` |
| `0x005776e4` | `CFastVB__DispatchIndirect_00656fd4_ReturnInt` | Guarded indirect-dispatch thunk forwarding args to `DAT_00656fd4` and returning int |
| `0x0057798e` | `CFastVB__DispatchIndirect_00656fa4` | Guarded indirect-dispatch thunk calling global function pointer `DAT_00656fa4` with 3 args |
| `0x00577a0a` | `CFastVB__DispatchIndirect_00656f94` | Guarded indirect-dispatch thunk calling global function pointer `DAT_00656f94` with 4 args |
| `0x005784a9` | `CFastVB__DispatchIndirect_00657044` | Guarded indirect-dispatch thunk calling global function pointer `DAT_00657044` |
| `0x00579184` | `CFastVB__NormalizeQuaternionCopy` | Normalizes quaternion source (or zeroes near-zero input) and copies into destination |
| `0x00591050` | `CFastVB__ReleaseOwnedObjectAndReset` | Releases owned sub-object via vfunc(`+0x28`) and clears local state fields (`+0x04`, `+0x14`) |
| `0x00592b00` | `CFastVB__ParserContext_Shutdown` | Parser-context shutdown path performing virtual cleanup, release/reset helper, and terminal callback dispatch |
| `0x00592c50` | `CFastVB__ParserContext_Init` | Parser-context constructor/init path seeding callback table and default `"Bogus message code"` diagnostic string |
| `0x00599258` | `CFastVB__ComputeNodeSpanAndStride` | Recursively computes node span/stride aggregates across node-kind tree branches |
| `0x00599878` | `CFastVB__CloneNodeTreeWithAddRef` | Allocates and clones node tree while AddRef-copying child/interface references with failure cleanup |
| `0x00598a56` | `CFastVB__InitNodeType9` | Initializes node-type 9 record fields and binds vtable `0x005ef250` |
| `0x00598f82` | `CFastVB__NodeType9_scalar_deleting_dtor` | Scalar-deleting destructor for node-type 9 object (`vtable 0x005ef250`) |
| `0x00598b48` | `CFastVB__InitNodeType10` | Initializes node-type 10 record fields and binds vtable `0x005ef260` |
| `0x00598b81` | `CFastVB__NodeType10_dtor` | Destructor body for node-type 10 releasing owned children/resources then base cleanup |
| `0x00598fa4` | `CFastVB__NodeType10_scalar_deleting_dtor` | Scalar-deleting wrapper for node-type 10 destructor with optional free flag |
| `0x005988f5` | `CFastVB__CompareNodeValuesByTagAndPayload` | Typed payload comparator handling scalar/string/pointer payload forms by node tag |
| `0x00598873` | `CFastVB__CloneNodeChainWithAddRef` | Clones linked node chain and AddRef-copies referenced payload objects with failure rollback |
| `0x00598d6b` | `CFastVB__InitNodeType13` | Initializes node-type 13 storage defaults and binds vtable `0x005ef270` |
| `0x00599b13` | `CFastVB__SetParseErrorAndMarkStateDirty` | Emits parse diagnostic message and marks parser state/error flags dirty |
| `0x00599b69` | `CFastVB__NodeTreeHasBitFlag0x200` | Recursively walks node tree and returns whether payload bit `0x200` is present |
| `0x00584724` | `CDXTexture__PackTexels_CallbackPerTexel_RepeatA` | Counted callback-dispatch wrapper invoking per-texel conversion callback in repeat path A |
| `0x00584786` | `CDXTexture__PackTexels_CallbackPerTexel_RepeatB` | Counted callback-dispatch wrapper invoking per-texel conversion callback in repeat path B |
| `0x005847e9` | `CDXTexture__PackTexels_CallbackPerTexel_Once` | Single-call callback-dispatch wrapper invoking per-texel conversion callback |
| `0x00584831` | `CDXTexture__PackTexels_CopyRaw32` | Raw copy packer writing first 32 bits from each 16-byte source texel |
| `0x00584886` | `CDXTexture__PackTexels_CopyRaw64` | Raw copy packer writing first 64 bits from each 16-byte source texel |
| `0x005848e3` | `CDXTexture__PackTexels_CopyRaw128` | Raw copy packer writing full 128-bit source texel records |
| `0x00584936` | `CDXTexture__PackTexels_NoDither_A16L16` | Non-dither packer writing A16L16 packed output |
| `0x00585576` | `CDXTexture__UnpackTexels_Bits332ToFloat4` | Unpacks 8-bit 3-3-2 packed texels into float4 RGBA channels (alpha=1.0) |
| `0x0058562d` | `CDXTexture__UnpackTexels_A8ToFloat4_ZeroRGB` | Unpacks alpha-only 8-bit texels with RGB zeroed and alpha from source |
| `0x005856b8` | `CDXTexture__UnpackTexels_Bits332A8ToFloat4` | Unpacks paired 3-3-2 + 8-bit alpha texels into float4 RGBA channels |
| `0x00585da3` | `CDXTexture__UnpackTexels_Signed5_5_A6_ToFloat4` | Unpacks signed 5-5 plus alpha6 packed texels into float4 channels |
| `0x00585e9f` | `CDXTexture__UnpackTexels_Signed8_8_A8_ToFloat4_RG` | Unpacks signed 8-8 plus alpha8 texels into float4 RG lanes with scalar alpha |
| `0x005861b4` | `CDXTexture__UnpackTexels_Signed2_10_10_10_ToFloat4` | Unpacks signed 2-10-10-10 packed texels into float4 channels with sign expansion |
| `0x00586305` | `CDXTexture__UnpackTexels_Signed16_16_16_16_ToFloat4` | Unpacks signed 16-16-16-16 packed texels into float4 channels |
| `0x00586609` | `CDXTexture__UnpackTexels_CallbackPerTexel_Stride2_SetRGBAOne` | Callback wrapper for stride-2 records with post-write RGBA defaults |
| `0x0058677b` | `CDXTexture__UnpackTexels_CallbackSingleTexel` | Single-texel callback wrapper for helper-dispatched unpack conversion |
| `0x00581d49` | `CDXTexture__ProbeTexelProfileSample` | Probes profile callback behavior using temporary sample context swap |
| `0x0058864a` | `CDXTexture__InitMappedFileContext` | Initializes mapped-file context fields and decode-open bookkeeping |
| `0x0058865c` | `CDXTexture__OpenMappedFileReadOnly` | Opens mapped file read-only and binds map-view pointers for decode helpers |
| `0x00588cc6` | `CDXTexture__ProjectPointToPlaneAndScale` | Projects 3D point to plane-basis coordinates and scales output for texture-space math |
| `0x005890f1` | `CDXTexture__CpuHasMmxFeature` | CPUID helper returning MMX feature-bit availability |
| `0x00589116` | `CDXTexture__IsMmxEnabledBySystemConfig` | Registry/system-gated MMX enable probe with cached global result |
| `0x00589367` | `CTexture__ReleaseIncludeNodeTreeRecursive` | Recursively releases include-node interfaces and child chains |
| `0x005893d1` | `CTexture__FreeChildIncludeNodeChainRecursive` | Recursively frees child include-node chain through `+0x0c` links |
| `0x005893e9` | `CTexture__IncludeNodeChain_scalar_deleting_dtor` | Scalar-deleting destructor wrapper for include-node chain object |
| `0x00589438` | `CTexture__CleanupIncludeContextRecursive` | Recursive include-context teardown releasing mapped-file/resources and callbacks |
| `0x00589689` | `CTexture__FreeIncludeFileChainRecursive` | Recursively frees include-file chain through `+0x04` links |
| `0x00589cab` | `CTexture__HandleDirective_Include` | Preprocessor `#include` handler with nested-depth guard and source-open dispatch |
| `0x00589e73` | `CTexture__HandleDirective_Error` | Preprocessor `#error` handler with line-continuation folding and diagnostic emit |
| `0x0058b3c7` | `CTexture__ExecuteDirectiveParserAction` | Executes directive-parser reduction actions and preprocessor evaluation stack operations |
| `0x0058b812` | `CTexture__RunDirectiveParser` | Runs table-driven YACC-style directive parser loop and reduction dispatch |
| `0x0058bd25` | `CTexture__InitializePreprocessorStateFromMemorySpan` | Initializes preprocessor state from memory span and seeds base macro definitions |
| `0x0058bd87` | `CTexture__GetNextTokenWithPreprocessor` | Returns next token while applying preprocessor stack/include transitions and directive parsing |
| `0x0058c3fe` | `CTexture__SkipLineContinuationAndAdvance` | Scanner helper that skips escaped newline continuations and advances line counters |
| `0x0058d2ad` | `CTexture__ReadNextLexToken` | Core lexer/token reader that classifies next token and advances source/token metadata state |
| `0x0058c2b9` | `CTexture__AppendDiagnosticTextLine` | Appends formatted diagnostic text lines into the preprocessor/compiler message buffer |
| `0x0058c457` | `CTexture__ParseFloatingLiteral` | Parses float literal text (including exponent form) and optionally emits numeric value |
| `0x0058c5d3` | `CTexture__ParseIdentifierToken` | Parses identifier token text and stores/returns allocated token string |
| `0x0058c652` | `CTexture__ParseOperatorToken` | Parses one/two/three-char operator and punctuator tokens (`==`, `<=`, `>>=`, `##`, etc.) |
| `0x0058d18b` | `CTexture__ParseCharLiteralToken` | Parses single-quoted character literal token and validates closing quote |
| `0x0058d1ca` | `CTexture__ParseStringLiteralToken` | Parses quoted/include-style string token with escape handling and diagnostic checks |
| `0x0058d419` | `CTexture__ParseVertexSemanticUsageToken` | Parses vertex semantic usage token names (`POSITION/NORMAL/TEXCOORD/...`) and usage index |

---

## Function Details

### CDXTexture__LoadTextureFromFile (0x00557300)

**Signature:** `int CDXTexture__LoadTextureFromFile(int mipLevel)`

**Purpose:** Loads a texture from the AYA resource archive system, supporting multiple texture formats and DXT compression.

**Key Behaviors:**
- Constructs resource paths like `data/resources/textures/%s_%d_%s` or `data/resources/dxtntextures/%s`
- Replaces backslashes with `%` in texture names for path construction
- Appends `.aya` extension to resource paths
- Supports texture format selection based on `DAT_009cc134` (32-bit textures flag)
- Uses `OID__AllocObject` to allocate memory (0x500000 bytes at line 0x1a2)
- Handles mip level shifting based on texture quality settings

**Texture Format Switch (at ECX+0x144):**

| Case | D3D Format Code | Format Name |
|------|-----------------|-------------|
| 0 | 0x00 | Unknown/Default |
| 1 | 0x19 | D3DFMT_A1R5G5B5 |
| 2 | 0x1a | D3DFMT_X1R5G5B5 |
| 3 | 0x16 | D3DFMT_A4R4G4B4 |
| 4 | 0x15 | D3DFMT_X4R4G4B4 |
| 5 | 0x17 | D3DFMT_R5G6B5 |
| 6 | 0x31545844 | DXT1 ('DXT1') |
| 7 | 0x32545844 | DXT2 ('DXT2') |
| 8 | 0x34545844 | DXT4 ('DXT4') |
| 9 | 0x3c | D3DFMT_A8 |
| 10 | 0x3f | D3DFMT_L8 |

**String References:**
- `s_mouse_tga_00640058` - Special case for mouse cursor texture
- `s_data_resources_textures_%s_%d_%s_006526e8` - Standard texture path format
- `s_data_resources_textures_mustbe_006526bc` - Required texture path format
- `s_data_resources_dxtntextures_%s_00652710` - DXT compressed texture path

**Called Functions:**
- `FUN_00528af0()` - Texture quality check
- `FUN_00547ec0()` - File open in AYA archive
- `DXMemBuffer__ReadBytes` (`0x00548570`) - Read file data
- `FUN_005758e6()` - Create DirectX texture surface
- `CChunker__CChunker()` / `CChunker__Destructor()` - Memory chunking

---

### CDXTexture__DumpTextureToRGBA (0x005586e0)

**Signature:** `void CDXTexture__DumpTextureToRGBA(void)` (thiscall, ECX = this)

**Purpose:** Converts a texture to RGBA format for debugging/export purposes. Handles different source pixel formats.

**Key Behaviors:**
- Allocates output buffer: `width * height * 4` bytes (line 0x3a1)
- Reads texture surface data via vtable calls (offsets 0x44, 0x4c, 0x50)
- Converts pixels based on source format

**Pixel Format Conversion:**

| Format Code | Bits/Pixel | Conversion Logic |
|-------------|------------|------------------|
| 0x15, 0x16 | 32-bit | Direct byte extraction (R at byte 0, G at byte 1, B at byte 2) |
| 0x17 | 16-bit RGB565 | R = (val >> 11) << 3, G = (val >> 5) << 2, B = val << 3 |
| 0x19 | 16-bit ARGB1555 | R = (val >> 10) << 3, G = (val >> 5) << 3, B = val << 3 |

**Warning String:** `s_WARNING___Attempt_to_dump_textur_006528ac` - Displayed for unsupported formats

**Called Functions:**
- `OID__AllocObject()` - Allocate RGBA buffer
- `ImageIO__WriteTGA24()` - Write output data (24-bit TGA export)
- `OID__FreeObject()` - Free allocated memory

---

### CDXTexture__CreateMipmaps (0x00559410)

**Signature:** `void CDXTexture__CreateMipmaps(uint* param_1, int mipIndex, int mipCount)` (thiscall)

**Purpose:** Generates a complete mipmap chain for a texture, with format conversion support.

**Key Behaviors:**
- Uses `GlobalMemoryStatus()` to check available system memory
- Reduces texture resolution if dimensions exceed `DAT_00888aac` (max width) or `DAT_00888ab0` (max height)
- Creates DirectX texture via `FUN_00513a10()`
- Handles format conversion between ARGB4444 and RGB565

**Debug String:** `s______________lose_res_texture____00652904` - Logged when reducing texture resolution

**Memory Allocations (via OID__AllocObject):**
- Line 0xb7a: Temporary buffer for ARGB4444 to RGB565 conversion
- Line 0xb92: Temporary buffer for format conversion (16-bit)
- Line 0xbbf: Standard mipmap buffer

**Format Conversion Cases:**
1. **ARGB4444 (format 4) to RGB1555 (format 2):** Converts 32-bit ARGB to 16-bit with alpha bit
2. **X4R4G4B4 (format 3) to RGB565 (format 5):** Converts to 16-bit without alpha
3. **Same format:** Direct memory copy with optional downsampling

**Downsampling Algorithm:**
- 2x2 box filter averaging for ARGB formats
- Each component: `(TL + TR + BL + BR) >> 2` with 0x3f3f3f3f mask to prevent overflow

---

### CDXTexture__Deserialize (0x00559be0)

**Signature:** `CTexture* CDXTexture__Deserialize(char useStreamData, uint* surfaceDesc)` (thiscall)

**Purpose:** Main texture loading entry point that deserializes texture data from the AYA archive system.

**Key Behaviors:**
- Allocates 0x158 bytes (344 bytes) for CTexture object (line 0xc25)
- Calls `CTexture__ctor()` to initialize the texture object
- Iterates through all texture surfaces (`puVar3[0x4e]` = surface count)
- Tracks texture size distribution in histogram at `0x9cc058`

**Loading Paths:**
1. **Standard Load (param_1 == 0):** Calls `CDXTexture__LoadTextureFromFile()`
2. **Stream Load (param_1 != 0):** Creates texture directly via `FUN_00513a10()`, falls back to `CDXTexture__CreateMipmaps()` on failure

**Debug Logging:**
- `s_Textures__s_Deserialised___dx_dx_00652970` - Texture load success message
- `s_leaker__00652928` - Memory leak warning
- `s_Warning___Texture__s_in_resource_00652934` - Duplicate texture warning

**Texture Linked List:**
- `DAT_0083d9b0` - Head of global texture list
- Each texture links to next via offset 0x28 (`puVar3[0x28]`)
- Checks for duplicate textures with same name (offset 0x2a for some identifier)

**Exception Handling:**
- Uses structured exception handling with `ExceptionList`
- Unwind handler at `LAB_005d7ddc`

---

### CDXTexture__Deserialize_Unwind (0x005d7dc0)

**Signature:** `void CDXTexture__Deserialize_Unwind(void)`

**Purpose:** Exception unwinding handler for `CDXTexture__Deserialize`. Cleans up memory allocations on exception.

**Key Behaviors:**
- Calls `OID__FreeObject_Callback()` to free the allocated texture object
- Accesses stack frame via `unaff_EBP - 0x168` to get allocation pointer
- Same allocation parameters as Deserialize: type=2, file=DXTexture.cpp, line=0xc25

---

## Data Structures

### CTexture Layout (estimated from offsets)

| Offset | Size | Field | Description |
|--------|------|-------|-------------|
| 0x00 | 4 | vtable/flags | Virtual table or state flags |
| 0x04 | 4 | unknown | |
| 0x08 | 160 | name | Texture name string |
| 0xAC | 4 | width | Texture width |
| 0xB0 | 2 | height | Texture height |
| 0xB2 | 2 | mipShift | Mip level shift count |
| 0xB8 | 32 | surfaces[8] | Direct3D surface pointers |
| 0xA0 | 4 | next | Linked list pointer |
| 0xA4 | 4 | identifier | Texture identifier for duplicate check |
| 0x138 | 4 | surfaceCount | Number of surfaces (0x4E * 4) |
| 0x144 | 4 | format | Internal format enum |
| 0x148 | 4 | type | Texture type |
| 0x150 | 4 | flags | Texture flags |
| 0x154 | 1 | hasDXT | DXT compression flag |
| 0x155 | 1 | qualityFlags | Quality/filtering flags |
| 0x156 | 2 | mipCount | Number of mip levels |

**Total Size:** 0x158 bytes (344 bytes)

---

## Global Variables

| Address | Name | Purpose |
|---------|------|---------|
| `0x009cc058` | TextureSizeHistogram | Array tracking texture sizes (indexed by log2 of width) |
| `0x009cc0e4` | TextureQualitySetting1 | Texture quality level |
| `0x009cc0f4` | TextureQualitySetting2 | Alternative quality setting |
| `0x009cc104` | MipReductionLevel1 | Mip reduction factor |
| `0x009cc114` | MipReductionLevel2 | Alternative mip reduction |
| `0x009cc134` | Force32BitTextures | Flag to force 32-bit texture formats |
| `0x00663064` | UseDXTTextures | Flag to enable DXT compression |
| `0x00888aac` | MaxTextureWidth | Maximum allowed texture width |
| `0x00888ab0` | MaxTextureHeight | Maximum allowed texture height |
| `0x0083d9b0` | TextureListHead | Head of global texture linked list |

---

## Technical Notes

### DXT Compression Support
The engine supports DXT1, DXT2, and DXT4 compression formats (identified by FourCC codes). DXT textures are stored in a separate path (`dxtntextures/`) from regular textures.

### Texture Quality System
Multiple quality settings control texture resolution:
- `DAT_009cc0e4/0f4`: Primary quality settings (0-2)
- `DAT_009cc104/114`: Mip reduction levels
- Textures can be downscaled at load time to save VRAM

### Memory Management
All allocations go through `OID__AllocObject()` with tracking parameters:
- Type: 2 = texture data, 0x61/0x62 = temporary buffers
- Source file and line number for debugging

### Special Cases
- `mouse.tga` texture has special handling (forced to specific format)
- Textures starting with `*` are excluded from duplicate checking
- Frontend textures (`FE_BEA_title_nav_sym`) tracked for leak detection

---

## Semantic Wave75 Promotions (Headless 2026-02-26)

| Address | Symbol | Notes |
|---------|--------|-------|
| 0x0056c70a | CRT__InitLocaleDefaults | Initializes locale defaults from user LCID and seeds CRT locale state. |
| 0x0056c724 | CRT__ResolveLocaleCodePageToken | Resolves `ACP`/`OCP` or explicit codepage token strings into numeric codepage values. |
| 0x0056c78a | CRT__IsCodePageSupportedByLocaleMap | Checks codepage id against CRT locale support/exclusion map. |
| 0x0056c80b | CRT__IsWindowsNtPlatform | Returns true when running on NT-class Windows. |
| 0x0056c841 | CRT__GetLocaleInfoACompatFallback | Compatibility `GetLocaleInfoA` wrapper with CRT fallback table lookup. |
| 0x0056c981 | CRT__StrToLong | Wrapper entry for CRT signed integer parser (`strtol`-style behavior). |
| 0x0056d176 | CRT__IsFiniteDoubleWords | Bitwise finite check for IEEE-754 double word-pair representation. |
| 0x0056d18a | CRT__ClassifyDoubleWords | Classifies IEEE-754 double word-pair into CRT floating class codes. |
| 0x0056e0ec | CRT__UIntToAsciiBase | Converts unsigned integer to ASCII text in caller-selected radix. |
| 0x0056e148 | CRT__UIntToAsciiBase_ReturnBuffer | Wrapper around `CRT__UIntToAsciiBase` returning destination pointer. |

## Semantic Wave76 Promotions (Headless 2026-02-26)

| Address | Symbol | Notes |
|---------|--------|-------|
| 0x0056614c | CRT__SelectHeapStrategy | Chooses CRT heap strategy from OS/version checks and `__MSVCRT_HEAP_SELECT` environment parsing. |
| 0x00566294 | CRT__InitializeHeapSubsystem | Creates process heap, selects strategy, and dispatches heap-subsystem initialization path. |
| 0x005662f1 | CRT__InitSmallBlockHeap | Allocates and initializes small-block heap descriptor table and related globals. |
| 0x00566339 | CRT__FindSmallBlockHeapEntryForPtr | Scans small-block heap region records and returns the matching entry for a pointer range. |
| 0x00569449 | CRT__ControlFp | Applies floating-point control-word mask/update (`(old & ~mask) | (new & mask)`) and writes back state. |
| 0x0056aff4 | CRT__AllocOsHandleSlot | Allocates/initializes a lowio slot entry and returns its handle index. |
| 0x0056b117 | CRT__SetOsHandle | Stores OS handle into a lowio slot and updates std handle aliases for slots 0/1/2. |
| 0x0056b193 | CRT__FreeOsHandle | Releases lowio slot handle state and clears std handle aliases for slots 0/1/2. |
| 0x0056cbb4 | CRT__EnsureTzsetInitialized | One-time lock-gated wrapper that ensures timezone globals are initialized. |
| 0x0056cbe2 | CRT__Tzset | Populates timezone/daylight globals from `TZ` env string or Win32 `GetTimeZoneInformation` fallback. |
