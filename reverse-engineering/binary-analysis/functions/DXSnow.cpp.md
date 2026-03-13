# DXSnow.cpp Functions

> Source File: DXSnow.cpp | Binary: BEA.exe
> Debug Path String: 0x00652534 (`C:\dev\ONSLAUGHT2\DXSnow.cpp`)

## Overview

CDXSnow is a DirectX-based particle system for rendering snow effects. It creates 1000 snowflake quads plus 50 additional particles with configurable behavior via console variables.

## Functions

| Address | Name | Purpose | Size |
|---------|------|---------|------|
| 0x0055515e | CDXSnow__Init | Initialize snow particle system, register cvars | ~512 bytes |

## Function Details

### CDXSnow__Init (0x0055515e)

**Signature:** `void __thiscall CDXSnow__Init(CDXSnow* this)`

Initializes the snow particle rendering system.

**Behavior:**
1. Allocates CVBufTexture (0x68 bytes) via `OID__AllocObject(0x68, 0x1f, debug_path)`
   - Pool ID 0x1f (31) = CVBufTexture pool
2. Calls `CVBufTexture__CVBufTexture()` constructor
3. Sets vertex buffer format: `SetVBFormat(format | 0x40, 0x14, 1)`
4. Sets index buffer format: `SetIBFormat(0x65, format, 2)`
5. Calls `SetPersist()` to mark buffers as persistent
6. Registers 4 console variables for snow control
7. **Loop 1 (1000 iterations):** Creates snowflake quads
   - Random X, Y, Z positions: `rand() * 5.0 * 3.051851e-05` (range 0-5)
   - Random fall offset: `rand() * 200.0 * -3.051851e-05` (range 0 to -200)
   - Vertex color: 0x80808080 (50% gray, 50% alpha)
   - Creates 4 vertices per quad, 6 indices (2 triangles)
8. **Loop 2 (50 iterations):** Creates additional particles
   - Random X, Z: `rand() * 15.0 * 3.051851e-05 - 7.5` (range -7.5 to +7.5)
   - Y position: -7.5 (fixed)
   - W component: 0.0
9. Unlocks vertex and index buffers

**Console Variables Registered:**
| CVar | String Address | Description | Type | Offset |
|------|----------------|-------------|------|--------|
| `cg_snow` | 0x00652474 | "Snow enable/disable" | 3 (int) | this+0x14 |
| `cg_snow_period` | 0x006524f0 | "Snow period, ie time a flake falls" | 4 (float) | this+0x388 |
| `cg_snow_scale` | 0x006524c4 | "Snow scale, ie flake size" | 4 (float) | this+0x3a0 |
| `cg_snow_fadedistance` | 0x00652490 | "Snow flake fade distance" | 4 (float) | this+0x38c |

**Memory Allocations:**
- CVBufTexture: 0x68 (104) bytes via OID pool 0x1f
- Total vertices: 4000 (1000 quads × 4 vertices)
- Total indices: 6000 (1000 quads × 6 indices)

## CDXSnow Class Layout

```
CDXSnow (estimated size ~0x3a4 bytes)
  +0x08: CVBufTexture* pVBufTexture
  +0x14: int cg_snow (enable flag)
  +0x68: float[50][4] secondary particles (50 × 16 bytes = 0x320)
  +0x388: float cg_snow_period
  +0x38c: float cg_snow_fadedistance
  +0x3a0: float cg_snow_scale
```

**Snowflake Vertex Structure (20 bytes each):**
```cpp
struct SnowVertex {
    float x, y, z;      // Position (random 0-5 range)
    float fallOffset;   // Vertical offset (0 to -200)
    DWORD color;        // 0x80808080 (gray, 50% alpha)
};
```

## Quad Index Pattern

Each snowflake quad uses 6 indices for 2 triangles:
```
Vertex indices: [base, base+1, base+2, base+3]
Triangle 1: base, base+1, base+2
Triangle 2: base+2, base+3, base
```

## Console Commands

To enable snow effects in-game (if console is accessible):
```
cg_snow 1
cg_snow_period 2.0
cg_snow_scale 1.5
cg_snow_fadedistance 500
```

## Related Files

- Atmospherics.cpp - Weather system integration (rain, lightning, wind)
- DXParticleTexture.cpp - Particle texture management
- vbuftexture.cpp - CVBufTexture base class
- oids.cpp - OID__AllocObject memory allocation

## Technical Notes

1. **Debug Path:** `C:\dev\ONSLAUGHT2\DXSnow.cpp` at 0x00652534
2. **OID Pool:** 0x1f (31) for CVBufTexture allocations
3. **Random scaling:** 3.051851e-05 = 1/32768 (converts rand() 0-32767 to 0-1)
4. **Vertex format flag:** 0x40 indicates textured vertices
5. **Index buffer format:** 0x65 (101) with 2-byte indices

## Integration with Weather System

CDXSnow is likely controlled by the Atmospherics system:
- `CAtmospherics::SetWeather()` may enable/disable snow
- Weather conditions per-level defined in world files
- Snow levels: Alpine missions, winter environments

---
*Discovered via Phase 1 xref analysis (Dec 2025)*
*Function manually created in Ghidra by user at 0x0055515e*
*Renamed to CDXSnow__Init via MCP*
