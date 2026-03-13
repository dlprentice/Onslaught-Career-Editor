# WarspiteDome.cpp Functions

> Source File: WarspiteDome.cpp | Binary: BEA.exe
> Debug Path: 0x0063d170

## Overview

Dome component for the Warspite battleship boss. CWarspiteDome is a destructible component attached to the main CWarspite battleship, representing one of its protective dome structures. Inherits from CGroundUnit and contains a nested CWarspite AI controller.

## Functions

| Address | Name | Purpose | Size |
|---------|------|---------|------|
| 0x005047e0 | CWarspiteDome__Init | Initialize dome with AI controller | ~432 bytes |
| 0x00504990 | CWarspiteDome__ScalarDeletingDestructor | MSVC scalar deleting destructor | ~32 bytes |
| 0x005049b0 | CWarspiteDome__Destructor | Cleanup dome resources | ~160 bytes |

## Exception Handlers

| Address | Name | Line | Purpose |
|---------|------|------|---------|
| 0x005d57c0 | Unwind@005d57c0 | 0x19 (25) | Cleanup for 32-byte allocation (pool 0x17) |
| 0x005d57d6 | Unwind@005d57d6 | 0x1a (26) | Cleanup for 96-byte allocation (pool 0x16) |
| 0x005d57ec | Unwind@005d57ec | 0x1d (29) | Cleanup for 12-byte allocation (pool 0x1b) |

## Key Observations

- **Composite pattern** - CWarspiteDome contains a CWarspite AI controller (mAI at offset 0x13c)
- **Inherits from CGroundUnit** - Calls `CGroundUnit__Init(param_1)` during initialization
- **Multiple memory pools used**:
  - Pool 0x17 (23): 32 bytes (0x20) - Unknown component
  - Pool 0x16 (22): 96 bytes (0x60) - CWarspite AI controller
  - Pool 0x1b (27): 12 bytes (0x0c) - Small utility object
- **VTable at 0x005dfc14** - CWarspiteDome virtual function table
- **Parent VTable at 0x005d8d1c** - Set during destruction (base class vtable)
- **Flags 0x0a000120** - OR'd into unit flags at offset 0x70

## CWarspiteDome Object Layout (Partial)

| Offset | Field | Type | Notes |
|--------|-------|------|-------|
| 0x00 | vtable | void* | -> 0x005dfc14 |
| 0x70 | mFlags | uint32 | Unit flags, OR'd with 0x0a000120 |
| 0x7c | mField7C | int | Set to 2 |
| 0x80 | mField80 | int | Set to 2 |
| 0x12c | mField12C | int | Set to 0 |
| 0x130 | mField130 | int | Set to 0 |
| 0x134 | mField134 | int | Set to 0 |
| 0x13c | mAI | CWarspite* | Nested AI controller |
| 0x208 | mField208 | void* | Component from pool 0x17 |
| 0x260 | mField260 | int | Set to 0 |
| 0x264 | mField264 | int | Set to 0 |
| 0x268 | mArray268[6] | int[6] | Array zeroed on init |
| 0x280 | mField280 | int | Set to 0 |
| 0x284 | mField284 | int | Set to 0 |
| 0x288 | mArray288[6] | int[6] | Array zeroed on init (offset +0x20 from 0x268) |
| 0x3bc | mParentPtr | void* | Parent object pointer |

## Initialization Flow

1. Set fields 0x7c and 0x80 to 2
2. OR flags at 0x70 with 0x0a000120
3. Set parent->0x1a0 to 1
4. Call `CGroundUnit__Init()`
5. Allocate 32-byte component (pool 0x17), store at 0x208
6. Allocate 96-byte CWarspite AI (pool 0x16), call `CWarspite__Init()`, store at 0x13c
7. Allocate 12-byte object (pool 0x1b), store at 0x70
8. Call `FUN_0050b010()` - additional initialization
9. Zero out arrays at 0x268 and 0x288 (6 elements each)

## Destruction Flow

1. Set vtable to parent class (0x005d8d1c)
2. Release component at offset 0x28 if valid
3. Release component at offset 0x24 if valid
4. Release component at offset 0x0c if valid
5. Call base monitor shutdown helper (`CMonitor__Shutdown`, former `FUN_004bac40`)

## Related Files

- Warspite.cpp - Parent AI controller class
- GroundUnit.cpp - Base class for ground-based units
- BattleEngine.cpp - Combat system

## Class Hierarchy

```
CGroundUnit
    |
    +-- CWarspiteDome (contains CWarspite AI)
```

---
*Discovered via Phase 1 xref analysis (Dec 2025)*
