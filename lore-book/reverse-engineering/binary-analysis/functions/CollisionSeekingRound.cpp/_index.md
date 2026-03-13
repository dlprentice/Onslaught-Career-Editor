# CollisionSeekingRound.cpp Functions

> Source File: CollisionSeekingRound.cpp | Binary: BEA.exe
> Debug Paths:
> - 0x00624630: `C:\dev\ONSLAUGHT2\CollisionSeekingRound.cpp`
> - 0x006246d8: `C:\dev\ONSLAUGHT2\collisionseekingthing.cpp`

## Overview

CCollisionSeekingRound is a projectile type that seeks targets while performing collision avoidance. This is likely used for homing missiles or guided projectiles that need to navigate around obstacles while tracking a target.

The class inherits from a base projectile class and uses a companion "thing" object (`CCollisionSeekingThing`) for tracking/seeking behavior.

## Vtable

Located at **0x005de95c**:

| Offset | Address | Function | Status |
|--------|---------|----------|--------|
| +0x00 | 0x00425b50 | Update (virtual) | UNDEFINED - needs function creation |
| +0x04 | 0x00402d20 | (inherited) | Not analyzed |
| +0x08 | 0x00426a00 | (virtual method) | UNDEFINED |
| +0x0C | 0x004264a0 | (virtual method) | UNDEFINED |
| +0x10 | 0x00425e30 | (virtual method) | UNDEFINED |
| +0x14 | 0x00425c60 | (virtual method) | UNDEFINED |
| +0x18 | 0x00426370 | (virtual method) | UNDEFINED |
| +0x1C | 0x00426920 | (virtual method) | Not analyzed |

## Functions

| Address | Name | Purpose | Size |
|---------|------|---------|------|
| 0x00425b50 | (LAB_00425b50) | Main update/tick function - contains CollisionSeekingRound.cpp reference | ~0x600 bytes (UNDEFINED) |
| 0x00426150 | CCollisionSeekingRound__Init | Initialize the seeking round with parameters | ~0x190 bytes |
| 0x00426360 | CCollisionSeekingRound__SetVtable | Sets vtable pointer to base class | ~0x10 bytes |
| 0x004263f0 | CCollisionSeekingRound__Destructor | Destructor - cleans up child objects | ~0x70 bytes |
| 0x00426460 | CCollisionSeekingRound__ScalarDeletingDestructor | MSVC scalar deleting destructor | ~0x20 bytes |
| 0x00426480 | CCollisionSeekingRound__SetCollisionMask | Sets collision mask flags (offset 0x10) | ~0x20 bytes |
| 0x00426900 | CCollisionSeekingRound__CheckCollisionFlags | Checks collision flags against target | ~0x20 bytes |
| 0x004269b0 | CCollisionSeekingRound__InitWithSound | Init with sound effect (3000ms duration) | ~0x90 bytes |
| 0x00426a40 | CCollisionSeekingRound__CreateEffect | Creates visual effect for the round | ~0x190 bytes |
| 0x004d9dc0 | CCollisionSeekingRound__Destructor | Duplicate destructor (identical code) | ~0x70 bytes |

## Class Layout (Partial)

Based on decompiled code analysis:

```cpp
class CCollisionSeekingRound {
    /* 0x00 */ void* vtable;
    /* 0x04 */ unknown;
    /* 0x08 */ CUnit* pOwner;           // Owner unit pointer
    /* 0x0C */ uint32_t flags;          // Collision/state flags
    /* 0x10 */ uint32_t collisionMask;  // What to collide with
    /* 0x14 */ CSeekingThing* pSeeker;  // Seeking behavior object
    /* 0x18 */ void* pSecondarySeeker;  // Secondary seeking object (for cluster?)
    /* 0x1C */ float radius;            // Collision radius
    /* 0x20 */ float targetData;        // Target-related data
    // ... more fields
};
```

## Flag Bits (offset 0x0C)

| Bit | Hex | Purpose |
|-----|-----|---------|
| 8 | 0x100 | Collision mask set |
| 10 | 0x400 | Cleared by InitWithSound |
| 17 | 0x20000 | Checked in Update |
| 3 | 0x08 | Checked in Update |

## References to collisionseekingthing.cpp (0x006246d8)

The `collisionseekingthing.cpp` debug path is referenced in memory allocation calls within the CCollisionSeekingRound class. These allocations create `CCollisionSeekingThing` helper objects that provide seeking behavior:

| From Addr | Function | Alloc Size | Line | Purpose |
|-----------|----------|------------|------|---------|
| 0x004261be | CCollisionSeekingRound__Init | 0x1c (28 bytes) | 0x28 (40) | Primary seeker object with vtable at 0x5d95e8 |
| 0x0042627a | CCollisionSeekingRound__Init | 0x28 (40 bytes) | 0x39 (57) | Secondary seeker object with vtable at 0x5d95c8 |
| 0x00426ad3 | CCollisionSeekingRound__CreateEffect | 0x34 (52 bytes) | 0x13a (314) | Effect object with vtable at 0x5d8bfc |

**Note:** The allocator function `OID__AllocObject` takes (size, category?, debug_path, line_number) parameters for debug tracking.

## Key Observations

1. **Undefined Code Region**: The main update function at 0x00425b50 is not recognized as a function by Ghidra despite being referenced in the vtable. Manual function creation failed, possibly due to complex control flow.

2. **Dual Seeker System**: The class appears to support two seeking objects (offsets 0x14 and 0x18), possibly for primary target tracking and secondary cluster/swarm behavior.

3. **Sound Integration**: The `InitWithSound` variant sets up a 3000ms sound effect, suggesting these projectiles have audible tracking sounds.

4. **Memory Allocation**: Uses custom allocator `OID__AllocObject` for creating child objects, with debug file/line info passed for debugging.

5. **Inheritance**: Based on destructor calling pattern, inherits from at least one monitor-capable base class (`CMonitor__Shutdown` / former `FUN_004bac40` called in destructor).

## Undefined Functions Needing Analysis

The following addresses in the vtable need function creation in Ghidra:

- 0x00425b50 - Main update (has CollisionSeekingRound.cpp debug ref)
- 0x00426a00
- 0x004264a0
- 0x00425e30
- 0x00425c60
- 0x00426370

---
*Discovered via Phase 1 xref analysis (Dec 2025)*
