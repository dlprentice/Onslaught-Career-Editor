# damage.cpp

> Damage system functions from BEA.exe - visual damage/decal rendering system

**Debug path string**: `C:\dev\ONSLAUGHT2\damage.cpp` at `0x006282dc`

## Functions

| Address | Name | Status | Notes |
|---------|------|--------|-------|
| 0x00440b90 | CDamage__Init | RENAMED | Initialize damage system, load default texture |
| 0x00440c00 | CDamage__FreeOwnedDamageObjects | RENAMED | Release nested owned damage-object pointers and null them |
| 0x00440c40 | CDamage__ResetDamageTables | RENAMED | Clear damage lookup/work tables and restore init flags |
| 0x00440c70 | CDamage__LoadDamageTexture | RENAMED | Load and process TGA damage texture with mipmaps |
| 0x00441000 | CDamage__CreateTextureBuffer | RENAMED | Allocate texture buffer memory |

## Details

### CDamage__Init (0x00440b90)

- **Purpose**: Initializes the damage rendering system
- **Xref**: Found via debug path at 0x006282dc (line 0x16 = 22)
- **Behavior**:
  - Checks if system already initialized via `this[0x5623]` flag
  - Allocates 12 bytes for damage texture info struct
  - Calls `CDamage__LoadDamageTexture` with path `"data/textures/mixers/damage0.tga"`
  - Clears two large arrays:
    - 20,000 dwords (80,000 bytes) starting at `this+4`
    - 2,048 dwords (8,192 bytes) starting at `this+0x4e21*4`
  - Sets flags at `this[0x5622]` and `this[0x5621]` to 1
- **Calling convention**: thiscall (ECX = CDamage instance pointer)

### CDamage__FreeOwnedDamageObjects (0x00440c00)

- **Purpose**: Releases owned nested damage objects and clears pointers.
- **Behavior**:
  - If `this->ptr0` points to an owned wrapper/object pair, frees inner object then zeros pointer.
  - Frees outer owned object pointer and zeros `this->ptr0`.
- **Notes**:
  - Used as a cleanup helper before reinitialization/destruction paths.
  - Semantics verified from decompile behavior and immediate headless read-back.

### CDamage__ResetDamageTables (0x00440c40)

- **Purpose**: Resets damage runtime tables to defaults.
- **Behavior**:
  - Clears 20,000 dwords starting at object base (`0x13880` bytes).
  - Clears additional 0x800 dwords starting at `this+0x13884`.
  - Sets flags at `this+0x15884` and `this+0x15888` to `1`.
- **Notes**:
  - Mirrors the table-clear/default-seed behavior seen from `CDamage__Init`.
  - Semantics verified from decompile behavior and immediate headless read-back.

### CDamage__LoadDamageTexture (0x00440c70)

- **Purpose**: Loads a TGA texture file and generates mipmaps for damage decals
- **Xref**: Found via debug path at 0x006282dc (line 0x4e = 78)
- **Parameters**: `param_1` - texture file path string
- **Behavior**:
  - Calls `FUN_004f2c60` to load TGA file into local buffer
  - Determines mipmap level based on texture size:
    - 4x4 -> level 2
    - 8x8 -> level 3
    - 16x16 -> level 4
    - 32x32 -> level 5
    - 64x64 -> level 6
  - Allocates memory for texture data using size from lookup table at `DAT_0062829c`
  - Copies and inverts pixel data from source (reads every 3rd byte, inverts with `255 - value`)
  - Generates mipmaps by averaging 2x2 pixel blocks with formula: `(a + b + c + d) * 64 / 256`
  - Post-processes all pixels: `32 - (pixel * 3 / 64)`
- **Calling convention**: thiscall (ECX = CDamage instance pointer)
- **Related data**:
  - `DAT_0062829c` - mipmap size lookup table
  - `DAT_00628298` - mipmap offset lookup table

### CDamage__CreateTextureBuffer (0x00441000)

- **Purpose**: Allocates memory buffers for damage texture rendering
- **Xref**: Found via debug path at 0x006282dc (lines 0xc6 = 198, 0x75 = 117)
- **Behavior**:
  - Allocates 12 bytes for texture info struct
  - Calls `FUN_00423960` (memory set/init) to initialize buffer
  - Looks up texture size from table at `DAT_0062829c`
  - Allocates additional buffer for texture pixel data
  - Sets initialization flag at `this[0x5623]` to 1
- **Calling convention**: thiscall (ECX = CDamage instance pointer)

## CDamage Class Structure (Partial)

Based on the decompiled code, the CDamage class appears to have:

| Offset | Size | Field | Notes |
|--------|------|-------|-------|
| 0x0000 | 4 | pTextureInfo | Pointer to texture info struct |
| 0x0004 | 80000 | damageArray1[20000] | Large array cleared on init |
| 0x13884 | 4 | field_5621 | Flag set to 1 on init |
| 0x13888 | 4 | field_5622 | Flag set to 1 on init |
| 0x1388C | 4 | bInitialized | Initialization check flag (offset 0x5623*4) |

## Texture Info Struct (12 bytes)

| Offset | Size | Field | Notes |
|--------|------|-------|-------|
| 0x00 | 4 | pPixelData | Pointer to texture pixel buffer |
| 0x04 | 4 | mipmapLevel | Mipmap level (2-6 based on size) |
| 0x08 | 4 | bufferSize | Total buffer size from lookup table |

## Related Strings

- `"data/textures/mixers/damage0.tga"` at 0x006282b8 - default damage texture

## Memory Allocation

All allocations use `OID__AllocObject` with parameters:
- Size in bytes
- Allocation type (0x35 = heap identifier?)
- Source file path (for debugging)
- Source line number
