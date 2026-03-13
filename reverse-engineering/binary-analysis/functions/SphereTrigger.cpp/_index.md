# SphereTrigger.cpp Functions

> Source File: SphereTrigger.cpp | Binary: BEA.exe
> Debug Path: 0x0063270c (`C:\dev\ONSLAUGHT2\SphereTrigger.cpp`)

## Overview

CSphereTrigger implements volume-based triggers that fire when objects enter a spherical region. Used for triggering events, cutscenes, objectives, and scripted sequences during gameplay.

The trigger system works by:
1. Maintaining a list of objects currently within the sphere
2. Checking each frame if new objects have entered
3. Firing the associated effect/event when triggered
4. Spawning a "Sphere_Trigger_Effect" particle when activated

## Functions

| Address | Name | Purpose | Size |
|---------|------|---------|------|
| 0x004e5540 | CSphereTrigger__OnTriggered | Fires trigger effect and spawns particle | ~313 bytes |
| 0x004e5700 | CSphereTrigger__Update | Main update loop - checks objects in sphere | ~315 bytes |

## Function Details

### CSphereTrigger__OnTriggered (0x004e5540)

**Purpose:** Called when an object enters the trigger sphere. Spawns the visual "Sphere_Trigger_Effect" particle and updates the triggered object's position data.

**Key Operations:**
- Calls virtual function at vtable+0x68 to validate trigger
- Spawns "Sphere_Trigger_Effect" particle via `CParticleManager__CreateEffect`
- Updates triggered object's position vectors (current, previous, target)
- Handles position interpolation for smooth transitions

**Decompiled Signature:**
```cpp
void CSphereTrigger::OnTriggered(void)  // thiscall, ECX = this
```

**String References:**
- `"Sphere_Trigger_Effect"` at 0x006326f4

**Called Functions:**
- `FUN_004cb0b0` - Setup/preparation
- `FUN_004cd7a0` - Effect name lookup
- `CParticleManager__CreateEffect` at 0x004cb3d0

---

### CSphereTrigger__Update (0x004e5700)

**Purpose:** Main frame update function. Iterates through potential trigger targets, checks if they're within the sphere radius, and manages the trigger state.

**Key Operations:**
- Calls parent class update via `FUN_004f4480`
- Checks flag at param+0x34 (bit 0x10) to see if trigger is active
- Compares cached timestamp at this+0x88 against global time
- Iterates through object list using iterator pattern
- Uses monitor.h / ActiveReader deletion tracking for safe references (allocates `CSPtrSet` at `monitor+0x04` when needed; see `reverse-engineering/binary-analysis/functions/monitor.h/_index.md`)
- Manages SPtrSet linked list for object tracking

**Decompiled Signature:**
```cpp
void CSphereTrigger::Update(int param_1, undefined4 param_2)  // thiscall, ECX = this
```

**String References:**
- Debug path `"C:\dev\ONSLAUGHT2\SphereTrigger.cpp"` at 0x0063270c (line 0x53 = 83)
- `"C:\dev\ONSLAUGHT2\monitor.h"` at 0x0062551c (line 0x18 = 24)

**Called Functions:**
- `FUN_004f4480` - Parent class update (CTrigger::Update?)
- `CSPtrSet__First` / `CSPtrSet__Next` - Iterator begin/next
- `CGenericActiveReader__dtor` (0x0044b1d0) - Unregister active reader from monitored object's deletion list (used before free)
- `OID__FreeObject` - Memory deallocation (frees temp objects)
- `CSPtrSet__Clear` - Clear trigger list (SPtrSet::Clear; returns nodes to pool)
- `OID__AllocObject` - Memory allocation (new operator)
- `CSPtrSet__Init` - Initialize empty set (head/tail/count = 0)
- `CSPtrSet__AddToHead` - Add entry to head of list
- `CSPtrSet__AddToTail` - Add entry to tail of list

## Related Classes

### SPtrSet (Smart Pointer Set)

The trigger uses SPtrSet for managing the list of objects within the sphere:

| Address | Function | Purpose |
|---------|----------|---------|
| 0x004e5840 | CSPtrSet__Init | Constructor-like init (mFirst/mLast/mSize = 0; mIterator untouched) |
| 0x004e5a80 | CSPtrSet__AddToHead | Add to head of list |
| 0x004e5b20 | CSPtrSet__AddToTail | Add to tail of list |
| 0x004e5c60 | CSPtrSet__Clear | Clear set and return nodes to pool |

**Note:** These functions are `SPtrSet.cpp` utilities (debug-path xref at 0x00632730), not SphereTrigger.cpp.

## Class Layout (Partial)

```cpp
class CSphereTrigger : public CTrigger {
    // Inherited from CTrigger...

    // +0x1C: Vector3 position (16 bytes)
    // +0x7C: Particle effect data
    // +0x80: Associated object pointer
    // +0x88: float lastUpdateTime (cached timestamp)
    // +0x8C: SPtrSet objectsInSphere (linked list of objects)
};
```

## Key Observations

1. **Trigger Validation:** Uses virtual function at vtable+0x68 to check if trigger should fire
2. **Time-Based Caching:** Stores timestamp at offset 0x88 to avoid redundant updates in same frame
3. **Memory Management:** Uses `OID__AllocObject`/`OID__FreeObject` with debug file/line strings for allocations (including `monitor.h`)
4. **Particle Effect:** Always spawns "Sphere_Trigger_Effect" when triggered - visual feedback
5. **Position Tracking:** Updates triggered object's position in multiple buffers (current, previous, interpolated)
6. **Exception Handling:** Update function has SEH exception handler for robustness

## Global Data References

| Address | Type | Purpose |
|---------|------|---------|
| 0x00672fd0 | float | Global game time / timestamp |
| 0x0083d120-0x0083d12c | float[4] | Default particle effect parameters |
| 0x009c3df0 | object | Global memory manager instance |
| 0x009c63e8 | object | Global particle manager instance |
| 0x0082b400 | object | Effect name lookup table |

## Usage Context

SphereTriggers are placed in levels by designers to:
- Trigger objective completion when player reaches location
- Start cutscenes or scripted events
- Spawn enemies when player enters an area
- Activate/deactivate game elements
- Trigger audio/visual effects

The trigger checks each frame for objects entering the sphere and fires once per object entry.

---
*Discovered via Phase 1 xref analysis (Dec 2025)*
