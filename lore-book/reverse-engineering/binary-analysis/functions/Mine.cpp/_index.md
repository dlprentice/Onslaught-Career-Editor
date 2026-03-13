# Mine.cpp Functions

> Source File: Mine.cpp | Binary: BEA.exe
> Debug Path: 0x006309a4

## Overview

Mine/explosive implementation. CMine is a ground-based unit that handles explosive mine placement, orientation, and water depth checks. Inherits from CGroundUnit.

## Functions

| Address | Name | Purpose | Size |
|---------|------|---------|------|
| 0x004ba150 | CMine__Init (TODO) | Initialize mine with orientation/position | ~600 bytes |

## Exception Handlers

| Address | Name | Line | Purpose |
|---------|------|------|---------|
| 0x005d3c10 | Unwind@005d3c10 | 31 | Cleanup for 0x10 byte allocation |
| 0x005d3c30 | Unwind@005d3c30 | 88 | Cleanup for secondary allocation |

## Key Observations

- **Inherits CGroundUnit** - Calls CGroundUnit__Init
- **3D orientation** - Complex sin/cos calculations for placement
- **Water depth check** - Compares against DAT_006fbdfc threshold
- **Vector math** - Normalizes forward/up vectors
- **State flags** - Sets at offsets 0x70, 0x260, 0x264

## Class Hierarchy

```
CUnit
  └── CGroundUnit
        └── CMine
```

## Related Files

- GroundUnit.cpp - CGroundUnit parent class
- Unit.cpp - CUnit base class

---
*Discovered via Phase 1 xref analysis (Dec 2025)*
