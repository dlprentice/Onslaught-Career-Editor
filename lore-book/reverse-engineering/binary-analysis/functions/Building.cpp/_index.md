# Building.cpp Functions

> Source File: Building.cpp | Binary: BEA.exe
> Debug Path: 0x00623af4

## Overview

Building/structure implementation. CBuilding handles destructible buildings including special types like repair pads with AI behavior.

## Functions

| Address | Name | Purpose | Size |
|---------|------|---------|------|
| 0x00417390 | CBuilding__CreateRepairPadAI (TODO) | Create repair pad AI component | ~150 bytes |

## Exception Handlers

| Address | Name | Line | Purpose |
|---------|------|------|---------|
| 0x005d1490 | Unwind@005d1490 | 50 | Cleanup for 128-byte allocation |
| 0x005d14a9 | Unwind@005d14a9 | 51 | Cleanup for 128-byte allocation |
| 0x005d14d0 | Unwind@005d14d0 | 100 | Cleanup for CRepairPadAI allocation |
| 0x005d14e6 | Unwind@005d14e6 | 104 | Cleanup for CRepairPadAI allocation |

## Key Observations

- **CRepairPadAI** - 96-byte (0x60) AI component for repair buildings
- **"Forseti Repair Pad"** - Special handling for this building type
- **VTable at 0x005d8e08** - CRepairPadAI virtual function table
- **String comparison** - Uses strcmp to check model name

## CBuilding Member Offsets

| Offset | Size | Field | Notes |
|--------|------|-------|-------|
| 0x13c | 4 | mAI | AI component pointer |
| 0x164 | 4 | pLevelData | Level data pointer |
| 0x1f4 | 4 | mHasRepairPad | Repair pad flag (set to TRUE) |

## Level Data Offsets

| Offset | Field | Notes |
|--------|-------|-------|
| 0xb0 | mModelName | Model name string pointer |

## Related Classes

```
CBuilding
  └── CRepairPadAI (component, 96 bytes)
```

## Related Files

- Unit.cpp - Base unit class (CBuilding likely inherits from CUnit)
- Component.cpp - Component system (also uses CRepairPadAI vtable)

---
*Discovered via Phase 1 xref analysis (Dec 2025)*
