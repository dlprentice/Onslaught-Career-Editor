# HeightField.cpp Function Mappings

> Functions from HeightField.cpp mapped to BEA.exe binary
> Debug path: C:\dev\ONSLAUGHT2\HeightField.cpp (at 0x0062cbd0)

## Overview
- **Functions Mapped:** 2
- **Status:** NEW (Dec 2025) - discovered via debug string xrefs
- **Classes:** CHeightField

## Discovery Method
Found via cross-references to debug path string at 0x0062cbd0. The CHeightField class manages terrain heightfield data, including loading from level resources and initializing color gradient tables for rendering.

## Function List

| Address | Name | Status | Link |
|---------|------|--------|------|
| 0x0047f750 | CHeightField__Load | NAMED | [View](CHeightField__Load.md) |
| 0x0047e8e0 | CHeightField__InitColorGradient | NAMED | [View](CHeightField__InitColorGradient.md) |

## CHeightField Structure (Partial)

Based on decompilation analysis, the CHeightField class has these known member offsets:

| Offset | Type | Name | Notes |
|--------|------|------|-------|
| 0x0024 | void* | pUnknown1 | Freed in Load, purpose unknown |
| 0x1028 | void* | pHeightData | 0xa2000 (663,552) bytes allocated |
| 0x1030 | byte | unknown1030 | |
| 0x1038 | int | xShift | Bit shift for X dimension |
| 0x103c | int | zShift | Bit shift for Z dimension |
| 0x107c | uint | colorBase | Base color (ARGB) |
| 0x108c | uint | colorMod | Color modifier (ARGB) |
| 0x1090 | byte | unknown1090 | |
| 0x1091 | byte | unknown1091 | |
| 0x1094 | byte | unknown1094 | |
| 0x1095 | byte | unknown1095 | |
| 0x10bc | int | xSize | 1 << xShift |
| 0x10c0 | int | zSize | 1 << zShift |
| 0x10c4 | int | xMask | xSize - 1 |
| 0x10c8 | int | zMask | zSize - 1 |
| 0x10cc | int | xzMask | zMask << xShift |
| 0x10d0 | int[192] | colorGradient | 64 RGB triplets for terrain shading |
| 0x13c4 | int[3] | fogColorSrc | Source fog colors |
| 0x13d0 | int[3] | fogColorDst | Destination fog colors (copied from src) |

**Struct Size:** 0x13dc (5084) bytes - validated in Load function

## Related Strings

| Address | String | Usage |
|---------|--------|-------|
| 0x0062cbd0 | "C:\dev\ONSLAUGHT2\HeightField.cpp" | Memory allocation debug tag |
| 0x0062cbf4 | "Got size %d, expected %d" | Size validation error |
| 0x006319f4 | "Resource file does not match code (CHeightfield size changed)!" | Version mismatch |

## Notes
- Height data is stored as 16-bit values (shorts)
- The 0xa2000 byte allocation suggests 331,776 height samples
- Nested loops read 9x9 blocks (81 values) repeatedly
- Color gradient table uses 64 entries with RGB565-like packing
- Related to CResourceAccumulator for level loading

## Related
- Source: Not present in our `references/Onslaught/` snapshot; current mapping is binary-only via debug-path xrefs.
- Called by: Map deserialization (FUN_00491060)
- Parent: [../README.md](../README.md)
