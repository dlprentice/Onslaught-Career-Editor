# DXCompass.cpp - DirectX Compass HUD

**Source File:** `C:\dev\ONSLAUGHT2\DXCompass.cpp`
**Debug String Address:** `0x00650454`
**Functions Found:** 7
**Analysis Date:** December 2025

## Overview

CDXCompass is the DirectX-based compass HUD element that displays:
- Threat direction indicators (enemy positions)
- Damage flash indicators (incoming damage direction)
- Bar line markers
- Objective markers (mission waypoints)

The compass is a circular ring rendered at the top of the screen, with markers positioned using trigonometric calculations (sin/cos) around the circumference.

## Functions

| Address | Name | Size | Description |
|---------|------|------|-------------|
| `0x0053be40` | `CDXCompass__Init` | ~0x390 | Main initialization - allocates textures, vertex buffers, builds ring geometry |
| `0x0053c1d0` | `CDXCompass__BuildRingGeometry` | ~0x130 | Generates circular ring vertices using sin/cos |
| `0x004270e0` | `CDXCompass__InitMarkerArrays` | ~0x30 | Zeroes marker tracking arrays (30 markers x 2 players) |
| `0x00427110` | `CDXCompass__LoadTextures` | ~0x80 | Loads HUD textures via CTexture::FindTexture |
| `0x00427190` | `CDXCompass__DestroyTextures` | ~0x70 | Releases texture references |
| `0x00427200` | `CDXCompass__Reset` | ~0x10 | Resets compass state flag at offset 0x3c10 |
| `0x00427210` | `CDXCompass__Render` | ~0xB70 | Main render function - draws all compass elements |

## Class Layout (Partial)

The CDXCompass data is embedded in a larger object (likely CHud). Offsets from `this` pointer:

| Offset | Type | Name | Description |
|--------|------|------|-------------|
| `0x3c08` | CByteSprite* | mCompassSprite | Sprite for compass ring |
| `0x3c10` | int | mState | Compass state flag |
| `0x3c24` | MarkerData[30][2] | mMarkers | Marker tracking (30 slots x 2 players) |
| `0x3ef4` | CTexture* | mThreatFlashTex | "hud\\v2\\ThreatFlash.tga" |
| `0x3ef8` | CTexture* | mDamageFlashTex | "hud\\v2\\DamageFlash.tga" |
| `0x3efc` | CTexture* | mBarLineTex | "hud\\v2\\BarLine.tga" |
| `0x3f00` | CTexture* | mObjectiveMarkerTex | "hud\\v2\\CompassObjectiveMarker.tga" |
| `0x3f04` | CTexture*[2] | mRingTextures | Ring textures (2 per player) |
| `0x3f0c` | CVBuffer* | mOuterRingVB | Vertex buffer for outer ring |
| `0x3f10` | CVBuffer* | mInnerRingVB | Vertex buffer for inner ring |

## Function Details

### CDXCompass__Init (0x0053be40)

Main initialization function called from `CHud::Init`.

**Key Operations:**
1. Allocates CByteSprite for compass rendering (0x20 bytes, type 0x4d)
2. Loads compass sprite data (16x16, 20 frames, 4 columns)
3. Adjusts texture dimensions based on GPU capabilities (DAT_00888a90 flags)
4. Creates 2 CTexture objects per player (4 total) for ring rendering
5. Allocates CVBuffer objects for outer ring (0x66 vertices) and inner ring (0x52 vertices)
6. Calls `CDXCompass__BuildRingGeometry` to populate vertex buffers
7. Sets target rendering parameters (512x512, 30 fps)

**Global Data References:**
- `DAT_00888a90` - GPU capability flags (bit 5 = texture size limit)
- `DAT_0089c924` - Additional GPU flag
- `DAT_00888aac` - Max texture width
- `DAT_00888ab0` - Max texture height
- `DAT_00650424/28/2c/30` - Texture dimensions for compass rings

### CDXCompass__BuildRingGeometry (0x0053c1d0)

Generates vertex data for the circular compass ring.

**Parameters:**
- `param_1` (float*) - Output vertex buffer
- `param_2` (int) - Texture width
- `param_3` (int) - Texture height
- `param_4` (int) - Number of segments (vertices)
- `param_5` (int) - Ring thickness percentage
- `param_6` (float) - UV scale factor

**Algorithm:**
- Uses `2*PI` (6.2831855) for full circle
- Inner radius = `(1 - scale) * thickness * 0.01`
- Outer radius = `(1 + scale) * thickness * 0.01`
- Generates triangle strip with 10 floats per vertex pair (position, UV, etc.)

### CDXCompass__Render (0x00427210)

Main rendering function - the largest and most complex function.

**Rendering Passes:**
1. **Threat indicators** - Red markers showing enemy directions (uses mThreatFlashTex)
2. **Damage indicators** - Flash markers showing incoming damage (uses mDamageFlashTex)
3. **Bar line markers** - 4 directional markers for N/S/E/W (uses mBarLineTex)
4. **Objective markers** - Yellow markers for mission objectives (uses mObjectiveMarkerTex)

**Key Constants:**
- `6.2831855` - 2*PI for angle calculations
- `111.5` / `95.0` - Outer ring radius (normal/split-screen)
- `96.0` / `80.0` - Middle ring radius
- `110.0` / `100.0` - Inner ring radius
- `0x1e` (30) - Maximum markers per player

**Split-Screen Support:**
- Checks player index via `FUN_004725d0()`
- Adjusts vertical center (0.5x or 1.5x) based on which player
- Uses different marker array slot based on player

## Texture Assets

| File | Usage |
|------|-------|
| `hud\v2\ThreatFlash.tga` | Enemy threat direction indicator |
| `hud\v2\DamageFlash.tga` | Incoming damage direction flash |
| `hud\v2\BarLine.tga` | Compass cardinal direction markers |
| `hud\v2\CompassObjectiveMarker.tga` | Mission objective waypoint marker |

## Call Hierarchy

```
CHud__Init (0x00481450)
  -> CDXCompass__InitMarkerArrays (0x004270e0)
       -> CDXCompass__Init (0x0053be40)
            -> CByteSprite::Init
            -> CByteSprite::Load
            -> CTexture::ctor (x4)
            -> CVBuffer::Create (x2)
            -> CDXCompass__BuildRingGeometry (x2)

FUN_00481650 (HUD texture loader)
  -> CDXCompass__LoadTextures (0x00427110)
       -> CTexture::FindTexture (x4)

[Unknown destructor]
  -> CDXCompass__DestroyTextures (0x00427190)

[Per-frame render]
  -> CDXCompass__Render (0x00427210)
       -> CFastVB::Render (multiple times)
       -> FUN_00555be0 (sprite rendering)
```

## Technical Notes

1. **Memory Allocation**: Uses `OID__AllocObject` with type IDs:
   - `0x4d` - CByteSprite
   - `0x02` - CTexture
   - `0x2c` - CVBuffer

2. **Angle Normalization**: All angles are normalized to [0, 2*PI] range using loops

3. **Alpha Blending**: Marker alpha calculated from distance/time, encoded as ARGB color

4. **Aspect Ratio**: Uses `DAT_00888a40` for Y-axis scaling to maintain circular appearance

5. **Exception Handling**: Uses structured exception handling (SEH) with unwind handlers at 0x005d77xx
