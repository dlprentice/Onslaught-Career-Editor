# MeshCollisionVolume.cpp Functions

> Source File: MeshCollisionVolume.cpp | Binary: BEA.exe
> Debug Path: `C:\dev\ONSLAUGHT2\MeshCollisionVolume.cpp` at 0x0062fe40

## Overview

Mesh-based collision volume system for physics calculations. This file handles the creation and management of collision bounding volumes for mesh parts, used in the game's physics and collision detection systems.

The main function allocates collision volume data structures (0x74 bytes per mesh part) and computes bounding box information for each mesh component.

## Functions

| Address | Name | Purpose | Size |
|---------|------|---------|------|
| 0x004ac000 | CMeshCollisionVolume__InitDirectionLookupTable | Initializes direction lookup table used by collision-volume setup paths | ~1536 bytes |
| 0x004ac140 | CMeshCollisionVolume__TestSweptSphereAgainstBounds | Swept-sphere versus bounds test with early reject/accept hit-state updates | ~864 bytes |
| 0x004ac4a0 | CMeshCollisionVolume__TestSweptSphereAgainstMeshPart | Iterates mesh-part candidates and tests swept-sphere collisions | ~1040 bytes |
| 0x004acf30 | CMeshCollisionVolume__ResolveContactNormalAndPlane | Builds contact normal/plane output from candidate axes and fallback rules | ~944 bytes |
| 0x004acde0 | CMeshCollisionVolume__InitContactOutputRecord | Initializes contact-output record fields and sets active/result flag | ~64 bytes |
| 0x004ad600 | CMeshCollisionVolume__SetPartBounds | Allocates and initializes collision bounds for mesh parts | ~456 bytes |
| 0x005d3980 | CMeshCollisionVolume__SetPartBounds_Unwind | Exception handler for SetPartBounds memory cleanup | ~25 bytes |

## Follow-up Recovery Notes (Wave56 Prep)

- `0x004ac6b0`: headless create probe failed (`createFunction returned null after disassemble`); function object still missing and queued for targeted retry.
- `0x004acde0`: function object created in wave56 prep and promoted in wave57 to `CMeshCollisionVolume__InitContactOutputRecord`.


## Semantic Promotion Follow-up (Wave63)

| Address | Name | Purpose |
|---------|------|---------|
| 0x0058546f | CMeshCollisionVolume__UnpackTexels_Bits16_16_16_16_ToFloat4 | Dispatch-table sibling in texture-unpack family; unpacks 16-16-16-16 packed texels into float4 channels. |

## Function Details

### CMeshCollisionVolume__SetPartBounds (0x004ad600)

**Signature:** `void __thiscall CMeshCollisionVolume::SetPartBounds(CMesh* mesh, int partIndex, float unknown)`

**Purpose:** Initializes collision volume data for a specific mesh part. Allocates memory for collision structures if not already allocated, then computes and stores bounding box data.

**Key Operations:**
1. **Memory Allocation** (lines 0x229 referenced):
   - Allocates `numParts * 0x74` bytes for collision data array
   - Each collision entry is 0x74 (116) bytes containing two 4x4 matrices and additional data
   - Uses memory allocator ID 0x6c

2. **Collision Data Structure** (per part, 0x74 bytes):
   - Offset 0x00: First 4x3 matrix (0x30 bytes) - likely world-space bounds
   - Offset 0x30: Second 4x3 matrix (0x30 bytes) - likely local-space bounds
   - Offset 0x60: 4x float vector (0x10 bytes) - bounding info
   - Offset 0x70: float value initialized to -1.0f (0xBF800000)

3. **Bounds Calculation:**
   - If `this->field_0x1c == 0`: calls `FUN_004b4de0` for standard mesh bounds
   - If `this->field_0x1c != 0`: calls `FUN_004b0fb0` for alternative bounds calculation
   - Both paths write matrix data and bounding info to the collision structure

4. **Error Handling:**
   - Logs error "Error: Can't find mesh part in..." (string at 0x0062fe20) if mesh part lookup fails

**Class Fields Used:**
- `this+0x14`: Pointer to mesh/model data
- `this+0x1c`: Mode flag (determines bounds calculation method)
- `this+0x24`: Pointer to collision data array (allocated on first call)

### CMeshCollisionVolume__SetPartBounds_Unwind (0x005d3980)

**Signature:** `void CMeshCollisionVolume::SetPartBounds_Unwind(void* ptr)`

**Purpose:** SEH exception handler that frees memory allocated in SetPartBounds if an exception occurs during initialization.

**Key Operations:**
- Calls memory deallocator `OID__FreeObject_Callback` (caller passes alloc tag 0x6c for context)
- Same line number (0x229) as the allocation, indicating paired alloc/dealloc

## Key Observations

1. **Memory Management Pattern:** Uses structured exception handling (SEH) with paired allocator/deallocator (0x6c) for safe memory management during collision volume setup.

2. **Lazy Initialization:** Collision data is only allocated on first use (`this+0x24 == 0` check), not during object construction.

3. **Per-Part Storage:** Each mesh part gets a dedicated 0x74-byte collision structure, allowing independent collision calculations per mesh segment.

4. **Dual Bounds Modes:** The `field_0x1c` flag switches between two different bounds calculation methods, possibly for static vs. animated meshes or different collision precision levels.

5. **Float Sentinel Value:** The -1.0f (0xBF800000) initialization at offset 0x70 likely indicates "unprocessed" or "invalid" state.

6. **Matrix Storage:** Two 4x3 matrices (48 bytes each) suggest storage of both local and world-space oriented bounding boxes for efficient collision testing.

## Related Functions

- `FUN_004b4de0` - Standard mesh bounds calculation
- `FUN_004b0fb0` - Alternative bounds calculation
- `OID__AllocObject` - Memory allocator
- `OID__FreeObject_Callback` - Memory deallocator callback wrapper
- `FUN_004011b0` - Matrix/vector initialization

## Data Structures

```cpp
// Collision volume entry (0x74 bytes per mesh part)
struct MeshPartCollision {
    float matrix1[12];    // 0x00: 4x3 matrix (world bounds?)
    float matrix2[12];    // 0x30: 4x3 matrix (local bounds?)
    float boundingInfo[4]; // 0x60: bounding sphere/box data
    float status;         // 0x70: -1.0f = unprocessed
};
```

---
*Discovered via Phase 1 xref analysis (Dec 2025)*
