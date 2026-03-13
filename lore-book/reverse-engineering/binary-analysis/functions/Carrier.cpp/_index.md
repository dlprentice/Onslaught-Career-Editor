# Carrier.cpp Functions

> Source File: Carrier.cpp | Binary: BEA.exe
> Debug Path: 0x006243bc

## Overview

Aircraft carrier/transport vessel implementation. Handles carrier mechanics including object allocation for carrier components. The carrier appears to integrate with the BattleEngine UI system.

## Functions

| Address | Name | Purpose | Size |
|---------|------|---------|------|
| 0x00421a80 | [CCarrier__Init](./CCarrier__Init.md) | Constructor/initialization, allocates two child objects | ~200 bytes |

## Exception Handlers

| Address | Name | Line | Purpose |
|---------|------|------|---------|
| 0x005d1840 | Unwind@005d1840 | 26 | Cleanup for first allocation (0x20 bytes) |
| 0x005d1856 | Unwind@005d1856 | 27 | Cleanup for second allocation (0x60 bytes) |

## Key Observations

- **Two-stage initialization** - Allocates 0x20 and 0x60 byte objects
- **VTable pointers** - Sets vtables at 0x005d940c and 0x005d93d4
- **Member offsets** - Stores child pointers at this+0x208 and this+0x13c
- **BattleEngine integration** - Called from FUN_0044d6f0 (likely UI/menu code)
- **Exception safe** - Unwind handlers ensure cleanup on allocation failure

## Related Files

- BattleEngine.cpp - Carrier is initialized during battle engine setup
- Unit.cpp - Carrier likely inherits from CUnit base class

---
*Discovered via Phase 1 xref analysis (Dec 2025)*
