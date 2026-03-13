# DXSurf.cpp Functions

> Source file: `C:\dev\ONSLAUGHT2\DXSurf.cpp`
> Debug path address: `0x006525a0`
> Analysis date: 2025-12-16

## Overview

DXSurf.cpp implements the **CDXSurf** class, which handles DirectX surface rendering for water/wave effects. The class creates animated wave strips using vertex buffers filled with sine-based wave geometry.

## Class: CDXSurf

**VTable Address:** `0x005e59a0` (renamed to `CDXSurf__vtable`)

### VTable Layout

| Offset | Address | Function | Purpose |
|--------|---------|----------|---------|
| 0x00 | 0x00556d70 | CDXSurf__ScalarDeletingDestructor | Destructor with delete |
| 0x04 | 0x00557a90 | FUN_00557a90 | Virtual method (texture-related) |
| 0x08 | 0x00557060 | (not defined) | Virtual method |
| 0x0C | 0x005572c0 | FUN_005572c0 | Virtual method (resource release) |
| 0x10 | 0x00558600 | (not defined) | Virtual method |
| 0x14 | 0x00556e90 | (not defined) | Virtual method |
| 0x18 | 0x00556fc0 | CDXSurf__SetupSurface | Setup surface parameters |
| 0x1C | 0x00405930 | (base class) | Inherited method |

## Functions

### CDXSurf__Init
| Property | Value |
|----------|-------|
| Address | `0x00556460` |
| Returns | `void` |
| Calling Convention | thiscall (ECX = this) |

**Purpose:** Initializes a CDXSurf object by zeroing out 4 member variables.

**Pseudocode:**
```cpp
void CDXSurf::Init() {
    this[3] = 0;  // offset 0x0C
    this[0] = 0;  // offset 0x00
    this[2] = 0;  // offset 0x08
    this[1] = 0;  // offset 0x04
}
```

---

### CDXSurf__LoadWavesTexture
| Property | Value |
|----------|-------|
| Address | `0x00556470` |
| Returns | `void` |
| Calling Convention | thiscall (ECX = this) |

**Purpose:** Loads the wave texture "mixers\waves.tga" using CTexture::FindTexture.

**Pseudocode:**
```cpp
void CDXSurf::LoadWavesTexture() {
    this[2] = CTexture::FindTexture("mixers\\waves.tga", 5, 0, -1, 1, 1);
}
```

**Notable Strings:**
- `mixers\waves.tga` at `0x0065258c`

---

### CDXSurf__CreateSurfaceArray
| Property | Value |
|----------|-------|
| Address | `0x00556490` |
| Returns | `void` |
| Calling Convention | thiscall (ECX = this) |
| Debug Line | 0x38 (56) |

**Purpose:** Allocates an array of surface strip objects and initializes each one.

**Key Operations:**
1. Checks if count > 7 (minimum strips required)
2. Allocates array using `OID__AllocObject(count * 0x0C + 4, 0x35, ...)`
3. Stores count at start of array
4. Calls `CDXSurf__CreateSurfaceStrip` for each element
5. Sets `this[3] = 1` (initialized flag)

**Memory Allocation:**
- Type ID: `0x35` (OID type for surface strips)
- Element size: `0x0C` (12 bytes per strip)
- Array header: 4 bytes (count)

---

### CDXSurf__CreateSurfaceStrip
| Property | Value |
|----------|-------|
| Address | `0x005565d0` |
| Returns | `void` |
| Calling Convention | thiscall (ECX = this) |
| Debug Lines | 0xA8, 0xAB (168, 171) |

**Purpose:** Creates two vertex buffers for a single wave strip with sine-wave geometry.

**Key Operations:**
1. Allocates two vertex buffer objects (size 0x2C each, type 0x2C)
2. Creates vertex buffers via `CVBuffer__Create(count * 2 + 2, 0x20, 0x242)`
3. Locks both buffers
4. Generates sine-wave vertex positions using `fsin()`
5. Handles platform-specific UV coordinate ordering (`DAT_0082b4a4` flag)
6. Sets vertex colors: `0xFFFFFF` (white), `0xC0FFFFFF` (semi-transparent), `0xFF000000` (black)
7. Unlocks buffers

**Vertex Format:**
- Position (X, Y, Z)
- Diffuse color (ARGB)
- Texture coordinates (U, V) - swapped based on platform flag

**Wave Generation:**
```cpp
float t = 0.0f;
for (int i = 0; i <= count; i++) {
    float sinVal = sin(t * 0.5f) * 0.5f;
    // ... generate vertices with sine displacement
    t += 0.125f;  // 8 segments per wave cycle
}
```

---

### CDXSurf__DestroyBuffers
| Property | Value |
|----------|-------|
| Address | `0x005565b0` |
| Returns | `void` |
| Calling Convention | thiscall (ECX = this) |

**Purpose:** Destroys two vertex buffer objects via their virtual destructors.

**Pseudocode:**
```cpp
void CDXSurf::DestroyBuffers() {
    if (this[0] != NULL) {
        `this[0]->vtable[0](1);`  // Call destructor with delete flag
    }
    if (this[1] != NULL) {
        `this[1]->vtable[0](1);`
    }
}
```

---

### CDXSurf__Destroy
| Property | Value |
|----------|-------|
| Address | `0x005569e0` |
| Returns | `void` |
| Calling Convention | thiscall (ECX = this) |

**Purpose:** Frees the surface array and releases the texture reference.

**Key Operations:**
1. Sets `this[3] = 0` (clear initialized flag)
2. If array exists: call destructor on each element, free array memory
3. If texture exists: release texture reference via `FUN_004f27e0`

---

### CDXSurf__Render
| Property | Value |
|----------|-------|
| Address | `0x00556a30` |
| Returns | `void` |
| Calling Convention | thiscall (ECX = this) |
| Parameters | `char param_1` - render mode flag |

**Purpose:** Renders all wave strips using Direct3D primitive drawing.

**Key Operations:**
1. Checks if surface array exists (`this[1] != 0`)
2. Sets render state via `FUN_005514a0(4)`
3. Gets texture from `FUN_00558690()`
4. For each strip:
   - Sets stream source via `CVBuffer__SetStreamSource` or `CVBuffer__SetStreamSourceSimple`
   - Draws triangle strip via D3D device call at vtable offset 0x144
   - Primitive type 5 = D3DPT_TRIANGLESTRIP
5. Restores render state

**Global References:**
- `DAT_009cc1a0` - Simple rendering mode flag
- `DAT_00888a50` - D3D device pointer

---

### CDXSurf__dtor
| Property | Value |
|----------|-------|
| Address | `0x00556d90` |
| Returns | `void` |
| Calling Convention | thiscall (ECX = this) |

**Purpose:** Destructor - releases all textures and cleans up resources.

**Key Operations:**
1. Sets vtable to `CDXSurf__vtable` (0x005e59a0)
2. Calls `FUN_00512cc0` (base class cleanup)
3. Iterates through texture array at `this[0x2E]` to `this[0x4E]`
4. For each texture with refcount > 0, logs warning: "Texture: %s refcount %d"
5. Calls final cleanup functions

**Warning String:**
- `Texture: %s refcount %d` at `0x00652660`

---

### CDXSurf__ScalarDeletingDestructor
| Property | Value |
|----------|-------|
| Address | `0x00556d70` |
| Returns | `void` |
| Calling Convention | thiscall (ECX = this) |
| Parameters | `byte param_1` - delete flag |

**Purpose:** Scalar deleting destructor generated by compiler.

**Pseudocode:**
```cpp
void CDXSurf::scalar_deleting_destructor(byte flags) {
    this->~CDXSurf();  // Call destructor
    if (flags & 1) {
        operator delete(this);  // Free memory
    }
}
```

---

### CDXSurf__DestroyRenderTarget
| Property | Value |
|----------|-------|
| Address | `0x00556f80` |
| Returns | `void` |
| Calling Convention | thiscall (ECX = this) |

**Purpose:** Destroys the render target texture at offset 0x140.

**Pseudocode:**
```cpp
void CDXSurf::DestroyRenderTarget() {
    if (this[0x50] != 0) {  // offset 0x140
        FUN_00501310();
        if (this[0x50] != 0) {
            CVBufTexture::~CVBufTexture();
            operator delete(this[0x50]);
        }
        this[0x50] = 0;
    }
}
```

---

### CDXSurf__SetupSurface
| Property | Value |
|----------|-------|
| Address | `0x00556fc0` |
| Returns | `bool` |
| Calling Convention | thiscall (ECX = this) |
| Parameters | Multiple surface configuration parameters |

**Purpose:** Configures surface properties and calls virtual initialization.

**Key Operations:**
1. Copies default name from `DAT_00662b2c` to `this[2]`
2. Sets various surface parameters at offsets 0x2B, 0x2C, 0x4F, 0x51, 0x52, 0x53, 0x54
3. Increments reference counter at `this[0x29]`
4. Calls virtual method at vtable offset 0x04
5. Returns success if result >= 0

---

### CDXSurf__RenderSurface
| Property | Value |
|----------|-------|
| Address | `0x005563d0` |
| Returns | `void` |
| Calling Convention | cdecl |
| Parameters | 11 parameters (likely render state) |

**Purpose:** Wrapper function that calls the main surface rendering function with default UV coordinates.

**Pseudocode:**
```cpp
void CDXSurf_RenderSurface(p1, p2, p3, p4, p5, p6, p7, p8, p9, p10, p11) {
    FUN_00555be0(p1, p2, p3, p4, p8, p9, p10, p11, p5, p6, p7,
                 0, 1.0f, 0, 1.0f);  // Default UV range 0-1
}
```

---

## Class Structure (Partial)

```cpp
class CDXSurf {
    /* 0x00 */ void* pVBuffer1;           // First vertex buffer
    /* 0x04 */ void* pVBuffer2;           // Second vertex buffer
    /* 0x08 */ CTexture* pWavesTexture;   // "mixers\waves.tga"
    /* 0x0C */ int bInitialized;          // Initialization flag
    // ... more members
    /* 0xB8 */ void* pTextureArray[32];   // Texture references (0x2E-0x4D)
    /* 0x138 */ int nTextureCount;        // this[0x4E]
    /* 0x140 */ void* pRenderTarget;      // this[0x50]
};
```

## Exception Handlers (Compiler-Generated)

| Address | Source Line | Type |
|---------|-------------|------|
| 0x005d7cd0 | 0x38 | Unwind for CreateSurfaceArray |
| 0x005d7cf0 | 0xA8 | Unwind for CreateSurfaceStrip (buffer 1) |
| 0x005d7d09 | 0xAB | Unwind for CreateSurfaceStrip (buffer 2) |

These are SEH exception handlers generated by MSVC for stack unwinding.

## Related Constants

| Address | Value | Description |
|---------|-------|-------------|
| 0x0065258c | "mixers\waves.tga" | Wave texture path |
| 0x00652660 | "Texture: %s refcount %d" | Debug warning format |
| 0x0082b4a4 | DAT_0082b4a4 | Platform UV swap flag |
| 0x009cc1a0 | DAT_009cc1a0 | Simple rendering mode flag |
| 0x00888a50 | DAT_00888a50 | D3D device pointer |

## Summary

CDXSurf is a DirectX surface rendering class used for water/wave visual effects. It:

1. Creates animated wave strips using vertex buffers
2. Generates sine-based wave geometry for realistic water movement
3. Uses "mixers\waves.tga" texture for wave appearance
4. Supports platform-specific UV coordinate handling
5. Renders using D3D triangle strips

The class inherits from a base texture management class (evident from the vtable structure and destructor behavior) and integrates with the game's vertex buffer system (CVBuffer).

## Functions Summary Table

| Address | Name | Purpose |
|---------|------|---------|
| 0x00556460 | CDXSurf__Init | Initialize member variables to zero |
| 0x00556470 | CDXSurf__LoadWavesTexture | Load waves.tga texture |
| 0x00556490 | CDXSurf__CreateSurfaceArray | Allocate surface strip array |
| 0x005565b0 | CDXSurf__DestroyBuffers | Destroy vertex buffer pair |
| 0x005565d0 | CDXSurf__CreateSurfaceStrip | Create wave strip with sine geometry |
| 0x005569e0 | CDXSurf__Destroy | Free array and texture |
| 0x00556a30 | CDXSurf__Render | Draw all wave strips |
| 0x00556d70 | CDXSurf__ScalarDeletingDestructor | Destructor with delete |
| 0x00556d90 | CDXSurf__dtor | Destructor - cleanup textures |
| 0x00556f80 | CDXSurf__DestroyRenderTarget | Destroy render target |
| 0x00556fc0 | CDXSurf__SetupSurface | Configure surface parameters |
| 0x005563d0 | CDXSurf__RenderSurface | Render wrapper with default UVs |

**Total: 12 functions from DXSurf.cpp**
