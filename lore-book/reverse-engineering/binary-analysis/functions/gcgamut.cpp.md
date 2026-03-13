# gcgamut.cpp

> Graphics Context Gamut - view frustum visibility culling system
> Debug path: `C:\dev\ONSLAUGHT2\gcgamut.cpp` (0x0062c968)

## Overview

gcgamut.cpp implements the CGamut class, which handles view frustum visibility calculations for the rendering system. The "gamut" determines which grid cells are visible from the camera's perspective, enabling efficient culling of off-screen objects.

The system works by:
1. Computing the camera's view frustum as a set of 5 corner points
2. Calculating plane intersection equations for each edge of the frustum
3. Rasterizing the visible area onto a 64x64 grid
4. Storing min/max height values per grid cell for visibility testing

## Console Variables

The CGamut system registers three console variables:

| CVar Name | Address | Type | Description |
|-----------|---------|------|-------------|
| `cg_gamutlocked` | 0x0067a070 | bool | When true, prevents gamut recalculation as camera moves |
| `cg_showgamut` | 0x0067a071 | bool | When true, displays the gamut visualization |
| `cg_renderimposters` | 0x0062c8c4 | bool | Controls imposter (billboard) rendering |

## Classes

### CGamut

Main class for view frustum culling calculations.

**Structure (inferred from decompilation):**
```cpp
struct CGamut {
    void* vtable;              // +0x00: Virtual table pointer (if any)
    void* unknown04;           // +0x04
    int gridSize;              // +0x08: Grid dimension (64 = 0x40)
    void* heightBuffer;        // +0x0C: Height data buffer (0x2000 bytes = 8KB)
    void* visibilityBuffer;    // +0x10: Per-cell visibility flags (0x1000 bytes = 4KB)
    int cellSize;              // +0x14: Cell size (8)
    int minX;                  // +0x18: Visible region min X
    int minY;                  // +0x1C: Visible region min Y
    int maxX;                  // +0x20: Visible region max X
    int maxY;                  // +0x24: Visible region max Y
    float cameraPos[4];        // +0x28-0x34: Camera position (x,y,z,w)
    // Total size: ~0x38+ bytes
};
```

**Buffer Layout:**
- `heightBuffer` (0x0C): 64x64 grid of 2-byte height pairs (min/max per cell)
- `visibilityBuffer` (0x10): 64x64 grid of 1-byte visibility flags

## Functions (4 total)

| Address | Name | Size | Notes |
|---------|------|------|-------|
| 0x004741b0 | CGamut__Init | 0xA8 | Constructor, allocates buffers, registers cvars |
| 0x00474260 | CGamut__Destroy | 0x3E | Destructor, frees allocated buffers |
| 0x004742a0 | CGamut__ComputePlanes | ~0x27E0 | Complex plane intersection math (very large function) |
| 0x00476a20 | CGamut__Calculate | ~0x580 | Main calculation entry point, calls ComputePlanes |

## Function Details

### CGamut__Init (0x004741b0)

**Signature:** `CGamut* __thiscall CGamut__Init(CGamut* this, int param)`

**Called from:** CEngine__Init (0x00449acb)

**Purpose:** Initializes the gamut system with memory buffers and registers console variables.

**Key Operations:**
1. Sets cell size to 8 at offset +0x14
2. Sets grid dimension to 64 (0x40) at offset +0x08
3. Allocates height buffer: 0x2000 bytes (8KB) via OID__AllocObject
4. Allocates visibility buffer: 0x1000 bytes (4KB) via OID__AllocObject
5. Registers three console variables with CConsole__RegisterVariable

**Memory allocations:**
- Height buffer: `64 * 64 * 2 = 8,192 bytes` (2 bytes per cell: min + max)
- Visibility buffer: `64 * 64 = 4,096 bytes` (1 byte per cell)

**Decompiled (cleaned):**
```cpp
CGamut* __thiscall CGamut__Init(CGamut* this, int param) {
    this->cellSize = 8;
    this->gridSize = 64;
    this->heightBuffer = OID__AllocObject(0x2000, 0x36, "gcgamut.cpp", 0x39);
    this->visibilityBuffer = OID__AllocObject(0x1000, 0x36, "gcgamut.cpp", 0x3A);

    CConsole__RegisterVariable("cg_gamutlocked",
        "Determines if the gamut gets recalculated as the camera moves",
        3, &DAT_0067a070, 0, 0);
    CConsole__RegisterVariable("cg_showgamut",
        "Determines if the gamut is displayed",
        3, &DAT_0067a071, 0, 0);
    CConsole__RegisterVariable("cg_renderimposters",
        &DAT_00662b2c, 3, &DAT_0062c8c4, 0, 0);

    return this;
}
```

### CGamut__Destroy (0x00474260)

**Signature:** `void __thiscall CGamut__Destroy(CGamut* this)`

**Called from:** FUN_00449890 (likely CEngine destructor)

**Purpose:** Frees the allocated height and visibility buffers.

**Decompiled (cleaned):**
```cpp
void __thiscall CGamut__Destroy(CGamut* this) {
    if (this->heightBuffer != NULL) {
        OID__FreeObject(this->heightBuffer);
        this->heightBuffer = NULL;
    }
    if (this->visibilityBuffer != NULL) {
        OID__FreeObject(this->visibilityBuffer);
        this->visibilityBuffer = NULL;
    }
}
```

### CGamut__Calculate (0x00476a20)

**Signature:** `void __thiscall CGamut__Calculate(CGamut* this, float* viewMatrix, float nearPlane, float leftPlane, float rightPlane, float* cameraPos)`

**Called from:** FUN_0053e2e0 (rendering pipeline)

**Purpose:** Main entry point for gamut calculation. Computes the visible region based on camera parameters.

**Key Operations:**
1. Checks `cg_gamutlocked` (DAT_0067a070) - if set, skips recalculation
2. Stores camera position at this+0x28
3. Computes 5 frustum corner points from view matrix and near/far planes
4. Calls helper functions for coordinate transformation (FUN_00401ec0, FUN_0040d120)
5. Calculates min/max X and Y bounds for visible region
6. Clamps bounds to grid size (0-63)
7. Calls CGamut__ComputePlanes to rasterize visibility
8. Fills visibility buffer based on height comparisons

**Frustum Setup:**
- Uses 5 corner points indexed as param_1[0..19] (5 vectors of 4 floats)
- Corners define near plane quad + camera position
- Near plane offset: 4.0 units from camera for margin

### CGamut__ComputePlanes (0x004742a0)

**Signature:** `void __thiscall CGamut__ComputePlanes(CGamut* this, float* frustumCorners)`

**Called from:** CGamut__Calculate (0x00476f81)

**Purpose:** Performs the heavy mathematical computation for plane intersections and visibility rasterization. This is an extremely large and complex function (~10KB of code).

**Algorithm Overview:**
1. Computes 4 edge plane normals from frustum corners
2. Normalizes each plane normal using SQRT
3. Computes line equations for X and Y scanlines through frustum
4. Handles 16 different sign combinations of plane orientations
5. For each grid cell in visible region:
   - Computes min/max height from 4 plane intersections
   - Converts to signed byte values (-127 to +127)
   - Stores in height buffer as 2-byte pairs

**Mathematical Constants:**
- `127.0 * 0.016666668` = height scale factor (converts world units to byte range)
- `1.41 * 0.5 = 0.705` = diagonal offset for cell corners
- `-9999.0 / 9999.0` = sentinel values for invalid planes

**Sign Combination Cases:**
The function has 16 code paths based on the signs of 4 plane intersection determinants:
- `local_158 > 0, local_164 > 0, local_168 > 0, local_13c > 0` (all positive)
- `local_158 > 0, local_164 > 0, local_168 > 0, local_13c < 0`
- ... (14 more combinations)
- `local_158 < 0, local_164 < 0, local_168 < 0, local_13c < 0` (all negative)

Each path computes min/max heights differently based on which planes contribute to visibility.

## Xrefs to Debug Path (0x0062c968)

| Address | Function | Line# | Context |
|---------|----------|-------|---------|
| 0x004741b5 | CGamut__Init | 0x39 | OID__AllocObject for height buffer |
| 0x004741db | CGamut__Init | 0x3A | OID__AllocObject for visibility buffer |

## Call Graph

```
CEngine__Init (0x00449acb)
    -> CGamut__Init (0x004741b0)
        -> OID__AllocObject x2
        -> CConsole__RegisterVariable x3

Render Pipeline (0x0053e2e0)
    -> CGamut__Calculate (0x00476a20)
        -> FUN_00401ec0 (coordinate transform) x5
        -> FUN_0040d120 (unknown)
        -> FUN_00401ee0 (unknown)
        -> CGamut__ComputePlanes (0x004742a0)

CEngine Destructor (0x00449890)
    -> CGamut__Destroy (0x00474260)
        -> OID__FreeObject x2
```

## Related Strings

| Address | String | Usage |
|---------|--------|-------|
| 0x0062c8cc | "cg_renderimposters" | Console variable name |
| 0x0062c8e0 | "cg_showgamut" | Console variable name |
| 0x0062c8f0 | "Determines if the gamut is displayed" | CVar description |
| 0x0062c918 | "cg_gamutlocked" | Console variable name |
| 0x0062c928 | "Determines if the gamut gets recalculated as the camera moves" | CVar description |
| 0x0062c968 | "C:\\dev\\ONSLAUGHT2\\gcgamut.cpp" | Debug path |

## Related Systems

- **CEngine** (engine.cpp) - Owns the CGamut instance, initializes during engine startup
- **imposter.cpp** - Imposter system controlled by `cg_renderimposters` cvar
- **DXLandscape.cpp** - Likely consumer of gamut visibility data for terrain culling
- **CConsole** (console.cpp) - Console variable registration system

## Notes

1. **"gc" prefix:** The "gc" in "gcgamut" likely stands for "Graphics Context" rather than "Gamma Correction" - this is a view frustum culling system, not color-related.

2. **Large function:** CGamut__ComputePlanes is one of the largest functions in the binary (~10KB). The extensive code duplication for 16 sign combinations could have been simplified with better abstraction.

3. **Grid system:** The 64x64 grid with 8-unit cells covers a 512x512 world unit area centered on the camera.

4. **Memory pattern:** Uses OID allocation type 0x36 which appears to be for render-related buffers.

5. **Optimization opportunity:** The `cg_gamutlocked` cvar allows developers to freeze gamut updates for debugging or performance testing.
