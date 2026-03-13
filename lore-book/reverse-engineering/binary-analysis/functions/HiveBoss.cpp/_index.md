# HiveBoss.cpp Functions

> Source File: HiveBoss.cpp | Binary: BEA.exe
> Debug Path: 0x0062cc98

## Overview

Hive Boss enemy implementation. CHiveBoss is a boss-type unit that inherits from CUnit and uses the "core2" model.

## Functions

| Address | Name | Purpose | Size |
|---------|------|---------|------|
| 0x0047fe30 | CHiveBoss__Init (TODO) | Initialize boss with sub-objects | ~400 bytes |

## Exception Handlers

| Address | Name | Line | Purpose |
|---------|------|------|---------|
| 0x005d2cb0 | Unwind@005d2cb0 | 33 | Cleanup for 48-byte allocation |
| 0x005d2cc6 | Unwind@005d2cc6 | 34 | Cleanup for 120-byte allocation |
| 0x005d2cdc | Unwind@005d2cdc | 40 | Cleanup for 44-byte allocation |

## Key Observations

- **Inherits CUnit** - Calls CUnit__Init during initialization
- **"core2" model** - Loads model via FUN_00444520("core2")
- **Factory pattern** - Function pointer at 0x005e1704
- **Three sub-objects** - Dynamically allocated components

## Memory Allocations

| Line | Size | Type ID | Offset | Purpose |
|------|------|---------|--------|---------|
| 33 | 48 bytes | 0x55 | +0x178 | Sub-object #1 |
| 34 | 120 bytes | 0x1B | +0x70 | Sub-object #2 |
| 40 | 44 bytes | 0x17 | +0x208 | Sub-object #3 (vtable 0x5DBE08) |

## Float Constants

| Value | Float | Offset | Purpose |
|-------|-------|--------|---------|
| 0x41200000 | 10.0f | +0x12C | Initial value |
| 0x41F00000 | 30.0f | +0x2A0 | Range/distance |
| 0xBF800000 | -1.0f | +0x268 | Unset/invalid state |
| 0x3CA3D70A | 0.02f | sub-object | Rate/speed |

## Class Hierarchy

```
CUnit
  └── CHiveBoss (uses "core2" model)
```

## Related Files

- Unit.cpp - CUnit base class
- BattleEngine.cpp - Combat system

---
*Discovered via Phase 1 xref analysis (Dec 2025)*
