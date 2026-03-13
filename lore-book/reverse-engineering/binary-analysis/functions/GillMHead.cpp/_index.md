# GillMHead.cpp Functions

> Source File: GillMHead.cpp | Binary: BEA.exe
> Debug Path: 0x0062ca6c (`C:\dev\ONSLAUGHT2\GillMHead.cpp`)

## Overview

CGillMHead is a head/turret motion controller for the GillM enemy unit. It inherits from CWarspite (a base class for attachable sub-units) and handles position tracking and model setup for a multi-part enemy. The head follows a parent object and calculates its world position using a 100.0 multiplier for direction vectors.

**Object Size**: 100 bytes (0x64), Type ID: 0x16

**Inheritance**: CGillMHead -> CWarspite -> (base class at 0x004bac40)

## Functions

| Address | Name | Purpose | Size |
|---------|------|---------|------|
| 0x0047a760 | CGillMHead__Create | Factory function - allocates and initializes CGillMHead object | ~143 bytes |
| 0x0047a7f0 | CGillMHead__ScalarDeletingDestructor | Vtable destructor entry - calls dtor, optionally frees memory | ~32 bytes |
| 0x0047a810 | CGillMHead__Destructor | Main destructor - cleans up 3 sub-objects at offsets 0x0C, 0x24, 0x28 | ~159 bytes |
| 0x0047a8b0 | CGillMHead__TryTransitionIdleToOpen | Animation-state gate: transitions `idle -> open` when current state and unit conditions match | ~88 bytes |
| 0x0047a900 | CGillMHead__AdvanceOpenAttackCloseState | Animation-state advance helper for `open/attack/close/idle` cycle | ~180 bytes |
| 0x0047afc0 | CGillMHead__Update | Per-frame update - calculates head position from parent transform | ~197 bytes |
| 0x0047b090 | CGillMHead__SetupModel | Model initialization - gets node handles from parent model | ~108 bytes |
| 0x0047be30 | CGillMHead__ScalarDeletingDestructor2 | Alternate destructor entry (different vtable) | ~32 bytes |
| 0x0047be50 | CGillMHead__Destructor2 | Simpler destructor - cleans up sub-object at offset 0x2C only | ~93 bytes |
| 0x004d10b0 | CGillMHead__ResetAnimationStateAndPauseLatch | Pause/unpause reset path: clears runtime handles/timers and updates pause latch flag | ~109 bytes |

## Vtable Analysis

**Primary Vtable**: 0x005dbcec (set in CGillMHead__Create)

| Offset | Address | Function |
|--------|---------|----------|
| 0x00 | 0x004ff330 | (inherited) |
| 0x04 | 0x0047a7f0 | CGillMHead__ScalarDeletingDestructor |
| 0x08 | 0x004bacb0 | (inherited - CWarspite) |
| 0x0C | 0x0047afc0 | CGillMHead__Update |
| 0x10 | 0x0047b090 | CGillMHead__SetupModel |
| ... | ... | (additional inherited methods) |

**Secondary Vtable**: 0x005d8d1c (set in destructor)

## Key Observations

### Position Calculation (Update)
The Update function calculates the head's world position using:
```
pos.x = parent->direction.x * 100.0 + parent->pos.x
pos.y = parent->direction.y * 100.0 + parent->pos.y
pos.z = parent->direction.z * 100.0 + parent->pos.z
```
This positions the head 100 units along the parent's facing direction.

### Animation State Strings

The new semantic promotions at `0x0047a8b0` and `0x0047a900` are grounded by direct string usage:

- `idle` (`0x0062ca48`)
- `open` (`0x00623bb4`)
- `attack` (`0x00624438`)
- `close` (`0x006289e4`)

Observed behavior:
- `TryTransitionIdleToOpen` only arms `open` when current animation is `idle` and a unit-gate helper passes.
- `AdvanceOpenAttackCloseState` cycles between `open/attack/close/idle` using runtime gating checks.

### Pause-Latch Reset Hook

`CGillMHead__ResetAnimationStateAndPauseLatch` (`0x004d10b0`) is called from `CGame__UnPause` and resets internal animation state handles/timestamps before updating the pause latch field.

### Object Layout (partial)
| Offset | Type | Field |
|--------|------|-------|
| 0x00 | void* | vtable |
| 0x08 | ptr | Parent object pointer |
| 0x0C | ptr | Model/resource handle 1 |
| 0x10 | ptr | Enable flag (non-null = enabled) |
| 0x18 | int | Node index 1 |
| 0x1C | int | Node index 2 |
| 0x24 | ptr | Resource handle 2 |
| 0x28 | ptr | Resource handle 3 |
| 0x2C | ptr | Resource handle 4 (Destructor2 only) |
| 0x34 | vec3 | Transform data (passed to model) |
| 0x60 | int | Unknown (set to 0 in Create) |

### Parent Storage
The CGillMHead pointer is stored at offset 0x13c in the parent object (likely CGillM).

### Resource Cleanup
Uses CSPtrSet__Remove to unlink resource handles from an internal SPtrSet list (returns node to pool); callers still perform resource-specific teardown separately.

## Related Files

- **GillM.cpp** - Parent class, the main GillM enemy body
- **CWarspite** - Base class providing Init function (0x004fe710)

## Notes

- Two separate destructor paths suggest the class may be used in different contexts (embedded vs heap-allocated)
- The 100.0 multiplier constant is stored at 0x005db020
- DAT_006fbdfc appears to be a distance/visibility threshold for disabling updates

---
*Discovered via Phase 1 xref analysis (Dec 2025)*
