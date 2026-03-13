# Bomber.cpp Functions

> Source File: Bomber.cpp | Binary: BEA.exe
> Debug Path: 0x00623a78

## Overview

Bomber aircraft implementation. **NOTE: Bomber.cpp is NOT in Stuart's source code dump** - this is a newly discovered source file from the binary only.

## Functions

| Address | Name | Purpose | Status |
|---------|------|---------|--------|
| 0x004160e4 | CBomber__Constructor_1 | First constructor stage | NOT A FUNCTION (inline code) |
| 0x0041611d | CBomber__Constructor_2 | Second constructor stage | NOT A FUNCTION (inline code) |

**Note:** The constructor code at 0x004160e4 and 0x0041611d is not recognized as standalone functions by Ghidra. These appear to be inline code blocks within a larger initialization routine.

## Exception Handlers

| Address | Name | Line | Purpose |
|---------|------|------|---------|
| 0x005d1400 | Unwind@005d1400 | 17 | Exception cleanup for line 17 |
| 0x005d1416 | Unwind@005d1416 | 22 | Exception cleanup for line 22 |

## Key Observations

- **Global instance** - References global CBomber object at 0x9c3df0
- **VTable pointer** - Uses vtable at 0x5D8DBC
- **Multi-stage init** - Constructor split across multiple code blocks
- **Missing source** - Bomber.cpp is not present in the current public source snapshot and may contain unique mechanics
- **Line numbers** - Debug info shows lines 17, 18, 22 in original source

## Investigation Needed

1. Find the parent function containing 0x004160e4
2. Determine if CBomber inherits from CAirUnit or similar
3. Check if Stuart has Bomber.cpp (request if missing)
4. Analyze vtable at 0x5D8DBC for other CBomber methods

## Related Files

- AirUnit.cpp - Likely parent class (debug path at 0x00622cf4)
- DiveBomber.cpp - Related bomber variant (debug path at 0x006289c0)
- GroundAttackAircraft.cpp - Similar aircraft class (debug path at 0x0062cadc)

---
*Discovered via Phase 1 xref analysis (Dec 2025)*
*Note: Source file NOT in Stuart's code dump - binary-only discovery*
