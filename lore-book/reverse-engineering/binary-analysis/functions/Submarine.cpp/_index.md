# Submarine.cpp Functions

> Source File: Submarine.cpp | Binary: BEA.exe
> Debug Path: 0x00632abc

## Overview

Submarine unit implementation. CSubmarine handles underwater vessel mechanics including AI behavior and guidance systems. Inherits from CUnit.

## Functions

| Address | Name | Purpose | Size |
|---------|------|---------|------|
| 0x004eec80 | CSubmarine__Init (TODO) | Constructor - creates SubmarineAI and SubmarineGuide | ~400 bytes |

## Exception Handlers

| Address | Name | Line | Purpose |
|---------|------|------|---------|
| 0x005d4fc0 | Unwind@005d4fc0 | 29 | Cleanup for CSubmarineAI allocation (0x60 bytes) |
| 0x005d4fd6 | Unwind@005d4fd6 | 30 | Cleanup for CSubmarineGuide allocation (0x20 bytes) |

## Key Observations

- **Component classes** - CSubmarineAI (AI behavior) and CSubmarineGuide (pathfinding)
- **Inherits CUnit** - Calls CUnit__Init as base class
- **RTTI found** - `.?AVCSubmarine@@`, `.?AVCSubmarineAI@@`, `.?AVCSubmarineGuide@@`
- **VTables** - Main: 0x005e14b4, AI: 0x005df404, Guide: 0x005df438

## Component Functions

| Address | Name | Purpose |
|---------|------|---------|
| 0x004fe710 | CWarspite__Init | Shared AI/base init helper invoked during `CSubmarine__Init` before the AI vtable is set to `0x005df404` (schedules fighting/waypoint events; name likely not final) |
| 0x004ef570 | CSubmarineGuide__CSubmarineGuide | Guidance/pathfinding constructor (sets vtable to `0x005df438`) |

## Related Files

- Unit.cpp - CUnit base class
- Boat.cpp - Related water vehicle (surface)

---
*Discovered via Phase 1 xref analysis (Dec 2025)*
