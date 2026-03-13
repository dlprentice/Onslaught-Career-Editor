# AirUnit.cpp Functions

> Source File: AirUnit.cpp | Binary: BEA.exe
> Debug Path: 0x00622cf4

## Overview

Base class for all aircraft units. Handles air unit initialization including visual effects for engine exhaust trails and thrust particles. CAirUnit extends CUnit with aircraft-specific features.

## Functions

| Address | Name | Purpose | Size |
|---------|------|---------|------|
| 0x00402ad0 | [CAirUnit__Init](./CAirUnit__Init.md) | Initialize air unit, create Trail and Engine effects | ~600 bytes |
| 0x0050f440 | CAirUnit__Helper_0050f440 | Destructor-adjacent helper: clears two owned pointer sets, detaches from particle manager list, then executes base unit deleting-dtor path | ~90 bytes |

## Exception Handlers

| Address | Name | Line | Purpose |
|---------|------|------|---------|
| 0x005d0f70 | Unwind@005d0f70 | 42 | Cleanup for Trail effect allocation |
| 0x005d0f86 | Unwind@005d0f86 | 54 | Cleanup for Engine effect allocation |

## Key Observations

- **Visual effects** - Creates "Trail" and "Engine" particle effects
- **Inherits from CUnit** - Calls CUnit__Init as base class constructor
- **Effect loops** - Processes effect data from config at offset 0x3bc
- **Related strings** - "Trail" at 0x00622d14, "Engine" at 0x00622cec

## Class Hierarchy

```
CUnit
  └── CAirUnit
        ├── CBomber
        ├── CDiveBomber
        └── CGroundAttackAircraft
```

## Related Files

- Unit.cpp - CUnit base class
- Bomber.cpp - CBomber derived class
- DiveBomber.cpp - CDiveBomber derived class
- GroundAttackAircraft.cpp - CGroundAttackAircraft derived class

---
*Discovered via Phase 1 xref analysis (Dec 2025)*
