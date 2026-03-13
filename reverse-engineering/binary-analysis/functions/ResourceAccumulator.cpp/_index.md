# ResourceAccumulator.cpp - Function Mapping

Source file: `C:\dev\ONSLAUGHT2\ResourceAccumulator.cpp`

## Overview

The ResourceAccumulator class handles loading and parsing of `.aya` resource archive files. It reads chunked binary data containing meshes, textures, goodies, shadows, and other game assets.

## Functions Found

| Address | Name | Status |
|---------|------|--------|
| 0x004d7200 | CResourceAccumulator__ReadResourceFile | Renamed |
| 0x004d6f70 | CResourceAccumulator__GetResourceFilename | Renamed |

## Function Details

### CResourceAccumulator__ReadResourceFile (0x004d7200)

**Purpose:** Main entry point for loading resource files. Parses chunked AYA archive format and dispatches to appropriate deserializers.

**Parameters:**
- `param_1` (int): Resource ID (-1=base, -2=frontend, -3=loading, >=0=level number, <-1000=goodie)
- `param_2` (int): Unknown flag (affects loading behavior)
- `param_3` (int): Unknown flag (skips certain chunk types when non-zero)

**Key Behavior:**
1. Gets resource filename via `GetResourceFilename()`
2. Opens and validates the AYA file
3. Reads chunk headers and dispatches based on 4-byte chunk ID
4. Times the load operation and logs duration

**Chunk IDs Handled:**
| Chunk ID | Handler | Description |
|----------|---------|-------------|
| `MESH` | CMesh__Deserialize | 3D mesh data |
| `GDIE` | CFEPGoodies__Deserialise | Goodie definitions |
| `SSHD` | CStaticShadows__LoadAll | Static shadow data |
| `DMKR` | CDamage__CreateTextureBuffer | Damage textures |
| `TEXT` | (chunk read) | Texture data |
| `ERES` | (chunk read) | Enemy resources |
| `WRES` | (chunk read) | Weapon resources |
| `IMPS` | (chunk read) | Impact effects |
| `LNDS` | (chunk read) | Landscape data |
| `VSDS` | (chunk read) | Vertex shader data |
| `PLAT` | (chunk read) | Platform-specific data |
| `SURF` | (chunk read) | Surface data |
| `PMIB` | (chunk read) | Unknown |

**Version Validation:**
The function validates multiple code-resource version stamps to ensure binary/resource compatibility:
- CVertexShader size
- Other struct sizes (at DAT_006317dc, DAT_006317e0, DAT_006317e4, DAT_006317e8, DAT_006317ec)

**Debug Output:**
```
CResourceAccumulator::ReadResources took %f seconds
Unknown chunk ID %s in resource file!
Resource file does not match code (CVertexShader size changed)!
```

### CResourceAccumulator__GetResourceFilename (0x004d6f70)

**Purpose:** Constructs the file path for a resource file based on resource ID and platform type.

**Parameters:**
- `param_1` (char*): Output buffer for filename
- `param_2` (int): Resource ID
- `param_3` (int): Platform type (1=PC, 2=PS2, 3=XBOX)

**Resource ID Mapping:**
| ID | Path Pattern |
|----|--------------|
| -1 | `data\Resources\base_res_<platform>.aya` |
| -2 | `data\Resources\Frontend_res_<platform>.aya` |
| -3 | `data\Resources\Loading_res_<platform>.aya` or `Loading_res_%s_%d.aya` |
| >= 0 | `data\Resources\%03d_res_%s.aya` (level resources) |
| < -1000 | `data\Resources\goodie_%02d_res_%s.aya` (goodie resources) |

**Platform Strings:**
- PC: "PC"
- PS2: "PS2"
- XBOX: "XBOX"

## Related Data

### Global Variables
| Address | Name | Purpose |
|---------|------|---------|
| 0x006317cc | DAT_006317cc | Current level number |
| 0x0083cb08 | DAT_0083cb08 | Resource filename buffer |
| 0x0066e8c0 | DAT_0066e8c0 | Loading flag |
| 0x0083d448 | DAT_0083d448 | Unknown flag |
| 0x0083d97c | g_LanguageIndex | Language index for localization (also referenced during resource loading) |

### String Constants
| Address | Value |
|---------|-------|
| 0x006317f4 | `data\Resources\goodie_%02d_res_%s.aya` |
| 0x0063181c | `data\Resources\%03d_res_%s.aya` |
| 0x0063183c | `data\Resources\Loading_res_` |
| 0x00631858 | `data\Resources\Loading_res_%s_%d.aya` |
| 0x00631880 | `data\Resources\Frontend_res_` |
| 0x006318a0 | `.aya` |
| 0x006318a8 | `data\Resources\base_res_` |
| 0x006318c4 | `PS2` |
| 0x006318cc | `XBOX` |
| 0x006318d0 | `PC` |
| 0x006318d4 | `CResourceAccumulator::ReadResources took %f seconds\n` |
| 0x0063190c | `Unknown chunk ID %s in resource file!\n` |
| 0x00631b7c | `C:\dev\ONSLAUGHT2\ResourceAccumulator.cpp` |

## AYA Resource File Format

The `.aya` files use a chunked format:
1. File header with version stamps
2. Sequential chunks, each with:
   - 4-byte ASCII chunk ID (e.g., "MESH", "GDIE")
   - Chunk data

The format supports multiple platforms (PC, PS2, XBOX) with platform-specific resource variants.

## Cross-References

Functions called by ReadResourceFile:
- `CMesh__Deserialize` - Mesh loading
- `CFEPGoodies__Deserialise` - Goodie system resource deserialize
- `CStaticShadows__LoadAll` - Shadow loading
- `CDamage__CreateTextureBuffer` - Damage texture setup
- Various unnamed deserializers for other chunk types

## Notes

- The Unwind function at 0x005d48d0 is an exception handler frame, not a real ResourceAccumulator method
- Resource loading is timed and logged for performance monitoring
- Version stamp validation prevents loading mismatched resources that could crash the game
