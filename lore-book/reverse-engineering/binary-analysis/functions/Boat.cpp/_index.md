# Boat.cpp Functions

> Source File: Boat.cpp | Binary: BEA.exe
> Debug Path: 0x00623990

## Overview

Water vehicle (boat) implementation. CBoat handles surface vessel mechanics. Constructor allocates two component objects and initializes boat-specific state.

## Functions

| Address | Name | Purpose | Size |
|---------|------|---------|------|
| 0x00414e50 | CBoat__Init (TODO) | Constructor - allocates 0x20 and 0x60 byte objects | ~300 bytes |

## Exception Handlers

| Address | Name | Line | Purpose |
|---------|------|------|---------|
| 0x005d1360 | Unwind@005d1360 | 30 | Cleanup for first allocation (0x20 bytes, pool 0x17) |
| 0x005d1376 | Unwind@005d1376 | 31 | Cleanup for second allocation (0x60 bytes, pool 0x16) |

## Key Observations

- **Two allocations** - 0x20 and 0x60 byte objects at lines 30-31
- **Member offsets** - Stores at +0x208 and +0x13c
- **State flags** - Sets +0x7c, +0x80 to 2, ORs +0x70 with 0x2100000
- **VTable** - Second object uses vtable at 0x005d8ce8
- **Zeroed fields** - Clears +0x260, +0x264, +0x268

## Related Files

- GroundUnit.cpp - Similar land-based unit
- Submarine.cpp - Related water vehicle (underwater)

---
*Discovered via Phase 1 xref analysis (Dec 2025)*
