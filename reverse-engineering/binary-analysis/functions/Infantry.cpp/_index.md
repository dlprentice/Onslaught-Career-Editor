# Infantry.cpp Functions

> Source File: Infantry.cpp | Binary: BEA.exe
> Debug Path: 0x0062d4a8

## Overview

Infantry unit implementation. Handles foot soldier spawning, movement, and initialization. Infantry units have smaller scale factors and use angle-based heading calculation.

## Functions

| Address | Name | Purpose | Size |
|---------|------|---------|------|
| 0x00488bb0 | [CInfantry__Init](./CInfantry__Init.md) | Constructor/initialization, allocates three child objects | ~1000 bytes |
| 0x0048a4e0 | CInfantryGuide__dtor | Infantry guide helper destructor body (reader/unregister + monitor shutdown) | ~160 bytes |
| 0x0048ac80 | CInfantryGuide__SelectTargetAndScheduleRecheck | Infantry guide target selection plus delayed recheck scheduling helper | ~80 bytes |
| 0x0048ace0 | CInfantryGuide__SelectNearestTargetReader | Infantry guide target-selection helper over nearby map-who entries | ~544 bytes |

## Exception Handlers

| Address | Name | Line | Purpose |
|---------|------|------|---------|
| 0x005d2e10 | Unwind@005d2e10 | 28 | Cleanup for first allocation (0x38 bytes, type 0xb) |
| 0x005d2e2e | Unwind@005d2e2e | 70 | Cleanup for second allocation (0x48 bytes, type 0x17) |
| 0x005d2e44 | Unwind@005d2e44 | 71 | Cleanup for third allocation (0x60 bytes, type 0x16) |

## Key Observations

- **Three-stage initialization** - Allocates 0x38, 0x48, and 0x60 byte objects
- **Scale factor** - Sets scale to 4.0f at offset 0x260 (or 1.0f with special flag)
- **Heading calculation** - Uses fpatan() to compute initial facing from X/Y
- **State flags** - Sets flags at 0x80 to 1, 0x70 to 0x2000010
- **Position from parent** - Reads spawn position from offset 0x3bc
- **VTable references** - Uses vtables at 0x5dbf48 and 0x5dbf14

## Related Files

- Unit.cpp - CInfantry likely inherits from CUnit
- Player.cpp - Kill tracking counts infantry kills (TK_INFANTY index 3; typo preserved)

---
*Discovered via Phase 1 xref analysis (Dec 2025)*
