# Plane.cpp Functions

> Source File: Plane.cpp | Binary: BEA.exe
> Debug Path: 0x00631630 (`C:\dev\ONSLAUGHT2\Plane.cpp`)

## Overview

CPlane is the **aircraft/fighter plane class** in the game's unit hierarchy. It inherits from CAirUnit (air unit base class) and represents player-controllable and AI-controlled aircraft.

Key characteristics discovered from the Init function:
- Inherits from `CAirUnit` (calls `CAirUnit__Init`)
- Can have a `CWarspite` component (a plane variant/type)
- Has engine hardpoints (iterates to find "Engine" attachment points)
- Supports launch sequences ("launch" animation state)
- Has random roll behavior (sets initial roll direction randomly)

## Functions

| Address | Name | Purpose | Size |
|---------|------|---------|------|
| 0x004d19d0 | CPlane__Init | Constructor/initializer - sets up aircraft, engines, and launch state | ~576 bytes |

## Detailed Analysis

### CPlane__Init (0x004d19d0)

**Signature:** `void __thiscall CPlane::Init(CPlane* this, int param_1)`

**Key Operations:**
1. Sets flag at offset 0x80 to 1 (marks as plane type)
2. Calls `CAirUnit__Init` to initialize base class
3. Allocates and initializes a component (stored at offset 0x208)
4. Allocates and initializes `CWarspite` component (stored at offset 0x13C)
5. Sets up "launch" animation based on launch type (offset 0x20 == 2 triggers alternate path)
6. Iterates through "Engine" hardpoints to set up engine effects
7. Randomly sets initial roll direction (offset 0x284) to +0.8 or -5.5

**Class Layout (partial):**
| Offset | Type | Field | Notes |
|--------|------|-------|-------|
| 0x80 | int | type_flag | Set to 1 for CPlane |
| 0x13C | CWarspite* | warspite | Plane variant component |
| 0x164 | void* | hardpoint_data | Contains engine attachment info |
| 0x208 | void* | component | Unknown component |
| 0x27C | int | launch_state | 0 or 1 depending on launch type |
| 0x280 | float | launch_timer | Time + 2.5 or 0 |
| 0x284 | float | roll_direction | +0.8 or -5.5 (random) |

**Memory Allocation:**
- Allocates 0x30 (48) bytes for component at line 0x13
- Allocates 0x64 (100) bytes for CWarspite at line 0x14
- Allocates 0x08 (8) bytes per engine at line 0x2A

**Exception Handlers:**
Three SEH unwind handlers exist for cleanup:
- `Unwind@005d4670` - Cleans up 48-byte allocation
- `Unwind@005d4686` - Cleans up 100-byte allocation (CWarspite)
- `Unwind@005d469c` - Cleans up 8-byte engine allocations

## Class Hierarchy

```
CGameObject
  └── CUnit
        └── CAirUnit
              └── CPlane (this file)
```

## Key Observations

1. **Single Function File**: Plane.cpp only contains the Init function - other CPlane methods are likely in separate files or inline.

2. **CWarspite Component**: The name "Warspite" (a famous WWII battleship) suggests this may be a specific plane variant or configuration system.

3. **Launch Mechanics**: Two distinct launch paths exist - one with a 2.5 second timer delay, suggesting carrier or runway launch variations.

4. **Random Roll**: Aircraft spawn with a random roll tendency, adding visual variety to formations.

5. **Engine Hardpoints**: Multiple engine attachment points are supported, iterating until a zero position is found.

## Related Functions

- `CAirUnit__Init` at 0x00402ad0 - Base class initializer
- `CWarspite__Init` at 0x004fe710 - Warspite component init
- Memory allocator at 0x005490e0 - Used for component allocation

## String References

| Address | String | Context |
|---------|--------|---------|
| 0x006243f8 | "launch" | Animation state name |
| 0x00622cec | "Engine" | Hardpoint attachment name |

---
*Discovered via Phase 1 xref analysis (Dec 2025)*
