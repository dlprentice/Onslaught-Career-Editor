# DiveBomber.cpp Functions

> Source File: DiveBomber.cpp | Binary: BEA.exe
> Debug Path: 0x006289c0

## Overview

Dive bomber aircraft AI implementation. Contains target selection logic for dive bombing runs. CDiveBomber likely inherits from CAirUnit.

## Functions

| Address | Name | Purpose | Status |
|---------|------|---------|--------|
| 0x00445070 | [CDiveBomber__SelectTarget](./CDiveBomber__SelectTarget.md) | AI target selection for dive bombing | RENAMED |

## Exception Handlers

| Address | Name | Line | Purpose |
|---------|------|------|---------|
| 0x005d2250 | Unwind@005d2250 | 18, 22 | Debug assertion handler |
| 0x005d2266 | Unwind@005d2266 | 19, 23 | Debug assertion handler |

## Key Observations

- **Target selection AI** - Iterates through vehicles, checks state, selects highest priority
- **Distance filtering** - Uses offset 0x10 for health/distance calculations
- **Entity validation** - Checks dive bomber entities at offset 0x88
- **Debug assertions** - Lines 18, 19, 22, 23 contain runtime checks
- **No direct constructor found** - May be inlined or in assertion-only code

## Related Files

- AirUnit.cpp - CAirUnit base class
- Bomber.cpp - Related bomber class
- BattleEngine.cpp - Combat system integration

---
*Discovered via Phase 1 xref analysis (Dec 2025)*
