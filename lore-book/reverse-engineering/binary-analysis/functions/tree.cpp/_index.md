# tree.cpp - Environmental Tree System

**Source file:** `C:\dev\ONSLAUGHT2\tree.cpp`
**Debug path address:** `0x00633a84`
**Functions identified:** 3
**Last updated:** 2025-12-16

## Overview

The `tree.cpp` source file implements the CTree class - environmental vegetation objects in the game world. Trees are destructible scenery that can be knocked down by units (mechs, vehicles). When hit, trees fall with physics simulation and trigger particle effects on ground impact.

## Related Classes (from RTTI)

| Class | RTTI Address | Purpose |
|-------|--------------|---------|
| `CTree` | 0x00630b98 | Main tree object class |
| `CTreeDetail` | 0x006313a8 | Tree detail/LOD system |
| `CTreeInitThing` | 0x0062d760 | Tree initialization helper |
| `CRTTree` | 0x006321b0 | Runtime tree instance |
| `CUnitKnockTrees` | 0x00626338 | Unit-tree collision handler |
| `CRoundTreeCollision` | 0x00626f00 | Round collision shape for trees |
| `CDXTrees` | 0x006529a0 | DirectX tree renderer (see DXTrees.cpp) |

## Functions

### CTree__CreateFallingTree
| Property | Value |
|----------|-------|
| Address | `0x004f69b0` |
| Source Line | 240 (0xf0) |
| Allocation Size | 0xc0 bytes (192 bytes) |
| Calling Convention | thiscall (ECX = this) |

**Purpose:** Creates a falling tree object when a standing tree is knocked down. Allocates memory for the falling tree data structure (0xc0 bytes), initializes it via `CTree__InitFallingTreeData`, and starts the falling animation.

**Decompiled signature:**
```c
void __thiscall CTree__CreateFallingTree(CTree *this, float param_1);
```

**Key operations:**
1. Checks if tree already has falling data at `this+0x48`
2. Copies 12 dwords from global tree type data at `DAT_008406b8 + treeType * 0x30`
3. Allocates 0xc0 bytes via memory manager (OID__AllocObject)
4. Calls `CTree__InitFallingTreeData` to initialize the falling tree
5. Stores falling tree pointer at `this+0x48`
6. Sets initial velocity value at `fallingTree+0xbc` to -1.0f
7. Schedules update callback via FUN_0044b2d0 (event ID 0xbb9 = 3001)
8. Calls `CTree__UpdateFallingTree` for initial physics step

**Called by:**
- `0x0044775b` - Unknown function (likely collision handler)
- `0x0044776c` - Unknown function
- `0x004f699c` - Tree helper function
- `0x004f6b6f` - Another tree-related function

---

### CTree__InitFallingTreeData
| Property | Value |
|----------|-------|
| Address | `0x004f5f60` |
| Calling Convention | thiscall (ECX = falling tree data) |

**Purpose:** Initializes the falling tree data structure with transformation matrices and physics parameters.

**Decompiled signature:**
```c
void __thiscall CTree__InitFallingTreeData(FallingTreeData *this, float *matrix, float scale, float *position);
```

**Key operations:**
1. Copies 12-dword matrix data to three locations: offsets 0x5c, 0x2c, 0x8c
2. Zeroes velocity components at offsets 0x4 and 0x8
3. Copies position data to offsets 0xc-0x18
4. Calculates perpendicular direction vector (cross product with up)
5. Normalizes the direction vector
6. Sets angular velocity constant `0x3ca3d70a` (0.02f) at offset 0x8

**Called by:**
- `CTree__CreateFallingTree` at 0x004f6a38

---

### CTree__UpdateFallingTree
| Property | Value |
|----------|-------|
| Address | `0x004f6b80` |
| Calling Convention | thiscall (ECX = this) |

**Purpose:** Updates the physics simulation for a falling tree each frame. Handles:
- Tree tilting/rotation physics (sin/cos-based rotation matrix)
- Ground collision detection via raycasting
- Particle effect spawning on ground impact ("Tree Ground Hit Effect")
- Bounce physics on collision
- Final rest state detection

**Decompiled signature:**
```c
void __thiscall CTree__UpdateFallingTree(CTree *this);
```

**Key operations:**
1. Retrieves falling tree data from `this+0x48`
2. Copies current matrix from offset 0x5c to 0x8c (previous frame)
3. If velocity > 0 (still falling):
   - Performs raycast from tree position downward
   - On ground hit with sufficient velocity (>0.05, >3.0 distance):
     - Spawns "Tree Ground Hit Effect" particle via CParticleManager
     - Calculates impact rotation using atan2
     - Updates visual effect orientation
   - Applies bounce: reduces velocity by 0.5, reverses with 0.2 damping
4. Checks for rest state (velocity < 0.01 and ground contact)
5. If still moving:
   - Updates tilt angle: `angle += velocity`
   - Applies gravity: `velocity += 0.005`
   - Builds rotation matrix using angle, sin, cos
   - Schedules next update via FUN_0044b370 (event ID 3000, delay -1.0)

**Called by:**
- `CTree__CreateFallingTree` at 0x004f6a7b
- Unknown function at 0x004f7078

**References:**
- `s_Tree_Ground_Hit_Effect` at 0x00633aa0 - Particle effect name

---

## Related Strings

| Address | String | Usage |
|---------|--------|-------|
| 0x00633a84 | `C:\dev\ONSLAUGHT2\tree.cpp` | Debug path |
| 0x00633aa0 | `Tree Ground Hit Effect` | Particle effect name |
| 0x0062d7a0 | `DefaultTree0` | Default tree type name |
| 0x00630c3c | `CTree` | Class name for factory |
| 0x0063d418 | `Loading trees` | Loading screen message |

## Memory Layout

### CTree Object (partial)
| Offset | Size | Type | Description |
|--------|------|------|-------------|
| 0x00 | 4 | vtable* | Virtual function table |
| 0x1c | 16 | float[4] | Position/transform data |
| 0x40 | 4 | int | Tree type index |
| 0x48 | 4 | FallingTreeData* | Falling tree data (NULL if standing) |

### FallingTreeData Structure (0xc0 bytes)
| Offset | Size | Type | Description |
|--------|------|------|-------------|
| 0x00 | 4 | float | Scale/size |
| 0x04 | 4 | float | Current tilt angle |
| 0x08 | 4 | float | Angular velocity |
| 0x0c | 16 | float[4] | Direction vector |
| 0x1c | 4 | float | X component |
| 0x20 | 4 | float | Y component |
| 0x24 | 4 | float | Z component |
| 0x2c | 48 | float[12] | Initial rotation matrix |
| 0x5c | 48 | float[12] | Current rotation matrix |
| 0x8c | 48 | float[12] | Previous rotation matrix |
| 0xbc | 4 | float | Rest state flag (-1.0 = active) |

## Global Data

| Address | Type | Description |
|---------|------|-------------|
| 0x008406b8 | TreeTypeData[] | Array of tree type definitions (0x30 bytes each) |
| 0x00840ce8-cf4 | float[4] | Default particle effect parameters |
| 0x00672fd0 | float | Rest state value |
| 0x00672fc8 | void* | Event manager instance |

## Event System Integration

Trees use the game's event/callback system for updates:

| Event ID | Purpose |
|----------|---------|
| 0xbb9 (3001) | Initial falling tree setup callback |
| 0x7d2 (2002) | Final rest state callback |
| 3000 | Continuous update callback |

## Unwind Handlers

Exception handlers for tree.cpp allocations:

| Address | Line | Size | Purpose |
|---------|------|------|---------|
| 0x005d5320 | 0x8f (143) | 0x5c | Cleanup for small tree allocation |
| 0x005d5350 | 0xf0 (240) | 0x07 | Cleanup for FallingTreeData |

## Cross-References

### Files that use trees
- `InitThing.cpp` - `InitThing__CreateThingByType` creates trees from level data
- `World.cpp` - `CWorld__LoadWorld` loads tree instances

### Related source files
- `DXTrees.cpp` (0x006529b0) - DirectX rendering for trees
- Collision system files - Tree collision handling
