# DXFont.cpp - DirectX Font Rendering System

**Source File:** `C:\dev\ONSLAUGHT2\DXFont.cpp`
**Debug String Address:** `0x00650670`
**Analysis Date:** December 2025

## Overview

CDXFont is the DirectX font rendering class responsible for text display in Battle Engine Aquila. It supports two font creation modes:
1. **GDI Font Creation** - Dynamically generates font textures using Windows GDI (CreateFontA, ExtTextOutA)
2. **Texture-Based Font** - Loads pre-rendered font bitmaps from game assets

The class renders text by building vertex buffers with textured quads for each character.

## Functions Found (5 total)

| Address | Name | Size | Purpose |
|---------|------|------|---------|
| `0x0053f880` | `CDXFont__CreateFromTexture` | ~640 bytes | Initialize font from texture asset |
| `0x0053fb00` | `CDXFont__CreateGDIFont` | ~1296 bytes | Create font using Windows GDI |
| `0x00540010` | `CDXFont__DrawTextScaled` | ~1584 bytes | Render text with scaling |
| `0x00540640` | `CDXFont__DrawText` | ~64 bytes | Wrapper for DrawTextScaled (scale=1.0) |
| `0x00540680` | `CDXFont__GetTextExtent` | ~288 bytes | Calculate text dimensions |

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

**Xrefs (1 caller):** Convenience function for unscaled text.

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
| `0x00650670` | `"C:\dev\ONSLAUGHT2\DXFont.cpp"` | Debug path |
| `0x006251e8` | Character set template | Glyph iteration |

## Exception Handler

**Address:** `0x005d7830` (Unwind@005d7830)

Exception unwinding code for CreateGDIFont - calls `OID__FreeObject_Callback` to free allocated resources on failure.
