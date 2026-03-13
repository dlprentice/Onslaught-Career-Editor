# GroundVehicle.cpp Functions

> Source File: GroundVehicle.cpp | Binary: BEA.exe
> Debug Path: 0x0062cb30

## Overview

Ground vehicle implementation. CGroundVehicle handles wheeled/tracked vehicle mechanics including wheel motion animation. Inherits from CGroundUnit.

## Functions

| Address | Name | Purpose | Size |
|---------|------|---------|------|
| 0x0047cfd0 | CGroundVehicle__Init (TODO) | Constructor - wheel motion, component setup | ~400 bytes |

## Exception Handlers

| Address | Name | Line | Purpose |
|---------|------|------|---------|
| 0x005d2bd0 | Unwind@005d2bd0 | 28 | Cleanup for alternate path |
| 0x005d2be6 | Unwind@005d2be6 | 33 | Cleanup for first assertion |
| 0x005d2bfc | Unwind@005d2bfc | 35 | Cleanup for second object |
| 0x005d2c12 | Unwind@005d2c12 | 37 | Cleanup for third object |

## Key Observations

- **WheelMotion** - References "WheelMotion" string at 0x0062cb54
- **Inherits CGroundUnit** - Calls CGroundUnit__Init (0x0047c730) as parent
- **Multiple components** - Creates objects at +0x70, +0x208, +0x13c, +0x260
- **Four allocations** - Lines 28, 33, 35, 37 with corresponding unwind handlers

## Class Hierarchy

```
CUnit
  └── CGroundUnit
        └── CGroundVehicle
```

## Related Files

- GroundUnit.cpp - CGroundUnit parent class
- Unit.cpp - CUnit base class

---
*Discovered via Phase 1 xref analysis (Dec 2025)*
