# DXFont.cpp - DirectX Font Rendering System

**Source File:** `[maintainer-local-source-export-root]\DXFont.cpp`
**Debug String Address:** `0x00650670`
**Analysis Date:** December 2025

## Overview
> **Queue status (2026-05-26):** Ghidra export-contract closure **6113/6113** (Wave900: every function commented; clean-signature proxy; not evidence-grade semantics). Lines below that reference a "next raw commentless" row are **archival wave progress**, not open work.

CDXFont is the DirectX font rendering class responsible for text display in Battle Engine Aquila. It supports two font creation modes:
1. **GDI Font Creation** - Dynamically generates font textures using Windows GDI (CreateFontA, ExtTextOutA)
2. **Texture-Based Font** - Loads pre-rendered font bitmaps from game assets

The class renders text by building vertex buffers with textured quads for each character.

## Wave801 Frontend/Render Helper Read-Back

Wave1005 (`help-text-display-review-wave1005`) re-read `0x00465710 CDXFont__DrawTextDynamic` as the direct HelpTextDisplay render dependency and `0x004659a0 CDXFont__DrawTextScaledWithShadow` as the related Wave801 top-500 text-render dependency. Fresh evidence confirmed `CHelpTextDisplay__RenderQueuedMessages` calls `CDXFont__DrawTextDynamic`, while `CDXFont__DrawTextScaledWithShadow` remains a broad frontend/game/HUD/message/menu helper with 43 xrefs and the same alpha-only `x+1/y+1` shadow draw followed by the foreground draw through `CDXFont__DrawTextScaled`. Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260531-132023_post_wave1005_help_text_display_review_verified`. Runtime text rendering, exact font/layout identity, visible UI output, BEA patching, and rebuild parity remain separate proof.

Wave1147 (`wave1147-frontend-game-shell-score20-current-risk-review`) re-read `0x004659a0 CDXFont__DrawTextScaledWithShadow` in the frontend/game shell score20 current-risk review. Fresh exports kept the saved shadow/foreground `CDXFont__DrawTextScaled` contract static-consistent with no mutation to this row. Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260605-182213_post_wave1147_frontend_game_shell_score20_current_risk_review_verified`.

Wave801 static read-back (`frontend-render-helpers-wave801`, `wave801-readback-verified`) saved current comments/tags for `0x00465710 CDXFont__DrawTextDynamic`, corrected stale `0x004659a0 CDXEngine__DrawTextScaledWithShadow` to `0x004659a0 CDXFont__DrawTextScaledWithShadow`, and hardened the shadow helper signature as `int __thiscall CDXFont__DrawTextScaledWithShadow(void * this, float x, float y, uint packed_argb, short * text, uint flags, float depth_z, float x_scale, float y_scale)`.

Static read-back shows `CDXFont__DrawTextDynamic` builds capped wide-text/per-character ARGB fade arrays before calling `CDXFont__DrawTextScaled`, and the corrected shadow helper forwards ECX to two `CDXFont__DrawTextScaled` calls: first alpha-only at `x+1/y+1`, then foreground. The same wave also saved `0x00465c10 CDXBitmapFont__BuildGlyphRemapTables` as the bitmap-font remap initializer over `DAT_005db5fc`, `DAT_00679af4`, `DAT_006799f4`, `DAT_006799d4`, and `DAT_005db738`. Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260524-073450_post_wave801_frontend_render_helpers_verified`.

This remains static retail Ghidra metadata only. Exact font class layout, runtime text rendering behavior, BEA patching, and rebuild parity remain deferred.

## Wave595 static read-back update

Wave595 saved Ghidra signatures/comments/tags for the DX bitmap/font queue head. The current saved signatures include:

```c
void * __fastcall CDXBitmapFont__ctor_base(void * this)
void __fastcall CDXBitmapFont__ReleaseFontResources(void * this)
void __thiscall CDXBitmapFont__InitNamedFontSlot(void * this, char * font_face, int font_size, int font_style_flags)
void __thiscall CDXBitmapFont__InitTextureFontSlot(void * this, char * texture_name, int glyph_cell_width)
void __fastcall CDXFont__CreateFromTexture(void * this)
void __fastcall CDXFont__CreateGDIFont(void * this)
int __thiscall CDXFont__DrawTextScaled(void * this, float x, float y, float depth_z, float x_scale, float y_scale, uint packed_argb, short * text, uint flags, float * per_char_argb)
void __thiscall CDXFont__DrawText(void * this, float x, float y, uint packed_argb, short * text, uint flags, float * per_char_argb, float depth_z)
```

Read-back boundaries: `CDXBitmapFont__InitNamedFontSlot` ends with `RET 0xc`, `CDXBitmapFont__InitTextureFontSlot` ends with `RET 0x8`, `CDXFont__DrawTextScaled` ends with `RET 0x24`, and `CDXFont__DrawText` ends with `RET 0x1c`. This is static saved-Ghidra evidence only; exact class layouts, runtime rendering behavior, BEA patching, and rebuild parity remain unproven.

## Wave596 static read-back update

Wave596 saved the next two DX bitmap/font-adjacent rows:

```c
void __thiscall CDXBitmapFont__Deserialize(void * this, void * chunk_reader)
int __fastcall CDXBitmapFont__HasAnimatedTexture(void * this)
```

`CDXBitmapFont__Deserialize` is called four times by `PCPlatform__DeserializeFontsAndAssets`. `RET 0x4` proves one stack parameter after `this`; the body reads serialized texture/font tables from the chunk reader, caches the texture at `this+0x170`, fills font metadata/glyph data, clears the GDI-font flag, and initializes CVBufTexture vertex/index formats. `CDXBitmapFont__HasAnimatedTexture` is called by `CConsole__RenderLoadingScreen` and checks the cached texture at `this+0x170` through `CDXTexture__GetAnimatedFrame`. This is static saved-Ghidra evidence only; exact layouts, runtime font deserialization/loading-screen behavior, BEA patching, and rebuild parity remain unproven.

## Functions Found (11 documented rows)

| Address | Name | Size | Purpose |
|---------|------|------|---------|
| `0x0053f730` | `CDXBitmapFont__ctor_base` | ~50 bytes | Initialize CDXBitmapFont vtable and cached fields |
| `0x0053f770` | `CDXBitmapFont__ReleaseFontResources` | ~88 bytes | Release cached font texture/resource fields without freeing object memory |
| `0x0053f7d0` | `CDXBitmapFont__InitNamedFontSlot` | ~88 bytes | Initialize Terminal/debug GDI font-face slot |
| `0x0053f830` | `CDXBitmapFont__InitTextureFontSlot` | ~66 bytes | Initialize texture-backed main/small/title font slot |
| `0x0053f880` | `CDXFont__CreateFromTexture` | ~640 bytes | Initialize font from texture asset |
| `0x0053fb00` | `CDXFont__CreateGDIFont` | ~1296 bytes | Create font using Windows GDI |
| `0x00540010` | `CDXFont__DrawTextScaled` | ~1584 bytes | Render text with scaling |
| `0x00540640` | `CDXFont__DrawText` | ~64 bytes | Wrapper for DrawTextScaled (scale=1.0) |
| `0x00540680` | `CDXFont__GetTextExtent` | ~288 bytes | Calculate text dimensions |
| `0x00540840` | `CDXBitmapFont__Deserialize` | ~304 bytes | Deserialize texture/font glyph tables from chunk data |
| `0x00540970` | `CDXBitmapFont__HasAnimatedTexture` | ~32 bytes | Predicate for non-null animated texture frame |

## Class Structure (Estimated)

Based on member access patterns in decompiled code:

```cpp
class CDXFont {
    // 0x00: vtable pointer
    // 0x04-0x50: Font name string (CString?)
    // 0x54: Character cell size
    // 0x58: Texture width (mTextureWidth)
    // 0x5C: Texture height (mTextureHeight)
    // 0x60-0x15C: Per-character glyph data (UV coords, widths)
    //   - Offset 0x60 + char*16: U1 coordinate
    //   - Offset 0x184 + char*16: V1 coordinate
    //   - Offset 0x188 + char*16: U2 coordinate
    //   - Offset 0x18C + char*16: V2 coordinate
    // 0x15C: Flag byte (determines GDI vs texture mode)
    // 0x160: Texture actual width
    // 0x164: Texture actual height
    // 0x170: CTexture* pointer (font texture)
    // 0x174: CVBufTexture* (vertex buffer texture handle)
    // 0x17C: Scale factor (float)
};
```

**Estimated struct size:** ~0x190 bytes (400 bytes)

## Function Details

### CDXBitmapFont__ctor_base (0x0053f730)

Constructor-style helper called by `PCPlatform__LoadFonts` and `PCPlatform__DeserializeFontsAndAssets` after allocating CDXBitmapFont-sized objects.

**Key Operations:**
- Uses ECX as `this` and returns `this`
- Clears cached fields at `this+0x168`, `this+0x16c`, `this+0x170`, `this+0x174`, and `this+0x178`
- Installs vtable `0x005e504c`
- Calls `CDXBitmapFont__BuildGlyphRemapTables`

### CDXBitmapFont__ReleaseFontResources (0x0053f770)

Resource-release helper called by `CPCPlatform__UnloadFonts` and `PCPlatform__DeserializeFontsAndAssets`.

**Key Operations:**
- Uses ECX as `this`
- Reinstalls vtable `0x005e504c`
- Releases and clears the cached field at `this+0x170` through the embedded `+8` counter path
- Releases and clears cached resources at `this+0x174` and `this+0x178`
- Returns without freeing the CDXBitmapFont object itself

### CDXBitmapFont__InitNamedFontSlot (0x0053f7d0)

Initializes the Terminal/debug font slot for the GDI/font-face path.

**Signature:** `void __thiscall CDXBitmapFont__InitNamedFontSlot(void * this, char * font_face, int font_size, int font_style_flags)`

**Key Operations:**
- `RET 0xc` proves three stack arguments after `this`
- Copies the scratch-buffer font face into `this+4`
- Stores font size at `this+0x54` and style flags at `this+0x58`
- Clears `this+0x170`
- Sets `this+0x15c` to select the GDI/font-face path

### CDXBitmapFont__InitTextureFontSlot (0x0053f830)

Initializes texture-backed main, small, and title font slots from PCPlatform font loading.

**Signature:** `void __thiscall CDXBitmapFont__InitTextureFontSlot(void * this, char * texture_name, int glyph_cell_width)`

**Key Operations:**
- `RET 0x8` proves two stack arguments after `this`
- Copies the texture name into `this+0x5c`
- Clears the GDI flag at `this+0x15c`
- Stores glyph cell width at `this+0x54`
- Clears `this+0x170`

### CDXFont__CreateFromTexture (0x0053f880)

Initializes font from a pre-rendered texture asset.

**Key Operations:**
- Calls `CTexture__FindTexture()` to load font bitmap
- Reads texture dimensions from loaded asset
- Scans texture pixels to calculate per-character glyph widths
- Stores UV coordinates for each printable character
- Iterates through character set using lookup table at `0x005db5fc`

**Called By:**
- `CDXFont__DrawTextScaled` (lazy initialization)
- `CDXFont__GetTextExtent` (lazy initialization)

### CDXFont__CreateGDIFont (0x0053fb00)

Dynamically creates a font texture using Windows GDI functions.

**Key Operations:**
1. Determines texture size based on font point size:
   - < 21pt: 256x256
   - < 41pt: 512x512
   - >= 41pt: 1024x1024
2. Allocates CTexture object via `OID__AllocObject()`
3. Creates compatible DC and DIB section
4. Uses `CreateFontA()` with parameters:
   - Font name from object member (offset 0x04)
   - Bold: bit 0 of flags (offset 0x16)
   - Italic: bit 1 of flags (offset 0x16)
5. Renders each character (0x20-0x7E) using `ExtTextOutA()`
6. Measures character widths with `GetTextExtentPoint32A()`
7. Copies bitmap to texture, converting to ARGB format
8. Sets texture name to "SystemFont"

**GDI Functions Used:**
- `CreateCompatibleDC`, `CreateDIBSection`
- `CreateFontA`, `SelectObject`
- `SetTextColor`, `SetBkColor`, `SetTextAlign`
- `GetDeviceCaps`, `MulDiv`, `SetMapMode`
- `GetTextExtentPoint32A`, `ExtTextOutA`
- `DeleteObject`, `DeleteDC`

**Called By:**
- `CDXFont__DrawTextScaled` (lazy initialization when flag at 0x15C is set)
- `CDXFont__GetTextExtent` (lazy initialization)

### CDXFont__DrawTextScaled (0x00540010)

Main text rendering function with support for scaling.

**Signature (reconstructed):**
```cpp
int CDXFont::DrawTextScaled(
    float x,           // Screen X position
    float y,           // Screen Y position
    float z,           // Z depth
    float scaleX,      // Horizontal scale
    float scaleY,      // Vertical scale
    DWORD color,       // Text color (ARGB)
    wchar_t* text,     // Wide string to render
    uint flags,        // Rendering flags
    float* perCharColors // Optional per-character colors
);
```

**Saved Ghidra signature:** `int __thiscall CDXFont__DrawTextScaled(void * this, float x, float y, float depth_z, float x_scale, float y_scale, uint packed_argb, short * text, uint flags, float * per_char_argb)`

**Key Operations:**
1. Counts printable characters (excludes CR/LF)
2. Lazy-initializes font texture if needed (calls CreateFromTexture or CreateGDIFont)
3. Sets up vertex buffer via `CVBufTexture__GetOrCreate()`
4. Optionally adjusts coordinates for screen resolution
5. Locks vertex buffer with `CFastVB__LockAligned()`
6. For each character:
   - Looks up glyph UV coordinates via vtable call
   - Builds textured quad (4 vertices, 28 bytes each)
   - Handles newline (0x0A) and carriage return (0x0D)
   - Applies color transformation if needed
7. Renders via `CFastVB__Render()`

**Flags:**
- Bit 3 (0x08): Skip depth test setup
- Bit 4 (0x10): Skip Y coordinate rounding

**Vertex Format:** Custom format (0x144/0x208) with position, RHW, color, and UV.

**Xrefs (12 callers):** Used throughout frontend and HUD rendering.

### CDXFont__DrawText (0x00540640)

Simple wrapper for DrawTextScaled with default scale values.

**Implementation:**
```cpp
void CDXFont::DrawText(float x, float y, DWORD color, wchar_t* text,
                       uint flags, float* perCharColors, float z) {
    DrawTextScaled(x, y, z, 1.0f, 1.0f, color, text, flags, perCharColors);
}
```

### CDXBitmapFont__Deserialize (0x00540840)

Deserializes a texture-backed bitmap font object from chunk data. `PCPlatform__DeserializeFontsAndAssets` calls this four times for font slots after object allocation/constructor setup.

**Saved Ghidra signature:** `void __thiscall CDXBitmapFont__Deserialize(void * this, void * chunk_reader)`

**Key Operations:**
- `RET 0x4` proves one stack argument after `this`.
- Reads the serialized texture through `CDXTexture__Deserialize`, caches it at `this+0x170`, bumps its embedded reference count, and moves it through the D3D buffer registry free-list path.
- Reads font-face/string and numeric metadata into `this+4`, `this+0x54`, `this+0x58`, `this+0x5c`, `this+0x160`, and `this+0x164`.
- Reads scale/glyph data into `this+0x17c` and `this+0x180`.
- Clears the GDI/font-face flag at `this+0x15c`.
- Initializes the cached CVBufTexture at `this+0x174` with vertex format `0x144/0x208/0x1c` and index format `0x65/0x208/2`.

### CDXBitmapFont__HasAnimatedTexture (0x00540970)

Loading-screen predicate reached by `CConsole__RenderLoadingScreen`.

**Saved Ghidra signature:** `int __fastcall CDXBitmapFont__HasAnimatedTexture(void * this)`

**Key Operations:**
- Uses ECX as `this`.
- Checks cached texture pointer `this+0x170`.
- Calls `CDXTexture__GetAnimatedFrame` and returns `1` only when the animated frame pointer is non-null.

**Xrefs:** High-fan-in convenience wrapper used by loading-screen, debug, interface, menu, heap, and overlay render paths.

### CDXFont__GetTextExtent (0x00540680)

Calculates the pixel dimensions of a text string without rendering.

**Signature (reconstructed):**
```cpp
int CDXFont::GetTextExtent(wchar_t* text, SIZE* outSize);
```

**Key Operations:**
1. Validates input parameters
2. Lazy-initializes font if needed
3. Iterates through string characters
4. Accumulates width, tracks maximum width across lines
5. Handles newline characters for multi-line text
6. Returns dimensions rounded to integers

**Returns:** 1 on success, 0 on failure (null inputs)

**Xrefs (95 callers):** Heavily used for text layout calculations.

## Text Rendering Pipeline

```
1. CDXFont::DrawText() or DrawTextScaled() called
         |
         v
2. Lazy font initialization if texture == NULL
   - If flag at 0x15C: CreateGDIFont()
   - Otherwise: CreateFromTexture()
         |
         v
3. Get/create vertex buffer texture handle
         |
         v
4. Lock vertex buffer (CFastVB__LockAligned)
         |
         v
5. For each character:
   - Get UV coords from glyph table
   - Build 4-vertex quad
   - Apply color
         |
         v
6. Render (CFastVB__Render)
```

## Related Systems

- **CTexture** - Font texture storage
- **CVBufTexture** - Vertex buffer management
- **CFastVB** - Fast vertex buffer rendering
- **FrontEnd.cpp** - Primary consumer for menu text
- **Hud.cpp** - In-game HUD text rendering

## Technical Notes

1. **Wide String Support**: Text parameter is `wchar_t*` (Unicode-aware)
2. **Character Range**: Supports ASCII 0x20 (space) through 0x7E (~)
3. **Multi-line Text**: Handles CR (0x0D) and LF (0x0A) characters
4. **Lazy Initialization**: Font texture created on first use, not construction
5. **Resolution Scaling**: Can adapt coordinates to current screen resolution
6. **Per-Character Coloring**: Optional array for rainbow/gradient text effects

## String References

| Address | String | Usage |
|---------|--------|-------|
| `0x00650664` | `"SystemFont"` | Default texture name for GDI fonts |
| `0x00650670` | `"[maintainer-local-source-export-root]\DXFont.cpp"` | Debug path |
| `0x006251e8` | Character set template | Glyph iteration |

## Exception Handler

**Address:** `0x005d7830` (Unwind@005d7830)

Exception unwinding code for CreateGDIFont - calls `OID__FreeObject_Callback` to free allocated resources on failure.
