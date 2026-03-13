# GroundUnit.cpp Functions

> Source File: GroundUnit.cpp | Binary: BEA.exe
> Debug Path: 0x0062cb0c

## Overview

Base class for ground-based units. CGroundUnit handles thruster setup, collision geometry, and ground unit state. Parent class for CGroundVehicle.

## Functions

| Address | Name | Purpose | Size |
|---------|------|---------|------|
| 0x0047c730 | CGroundUnit__Init (TODO) | Constructor - thruster setup, base init | ~400 bytes |
| 0x0047c8e0 | CGroundUnit__CreateCollisionSphere (TODO) | Create collision geometry | ~100 bytes |

## Exception Handlers

| Address | Name | Line | Purpose |
|---------|------|------|---------|
| 0x005d2bb0 | Unwind@005d2bb0 | 35 | Cleanup for Init allocation (8 bytes, pool 0x10) |

## Key Observations

- **Thruster setup** - References "Thruster" string at 0x00623080
- **Two-phase init** - Basic setup, then collision/physics
- **Collision sphere** - 0x1c bytes, radius calculation with 0.8 scale factor
- **Parent of CGroundVehicle** - Called by CGroundVehicle__Init

## Class Hierarchy

```
CUnit
  └── CGroundUnit
        └── CGroundVehicle
```

## Related Files

- Unit.cpp - CUnit base class
- GroundVehicle.cpp - CGroundVehicle derived class

---
*Discovered via Phase 1 xref analysis (Dec 2025)*
