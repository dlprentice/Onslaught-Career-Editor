# SquadRelaxed.cpp Functions

> Source File: SquadRelaxed.cpp | Binary: BEA.exe
> Debug Path: 0x00632918 (`C:\dev\ONSLAUGHT2\SquadRelaxed.cpp`)

## Overview

CRelaxedSquad is an AI squad behavior state representing the idle/patrol mode for enemy squads. This is the counterpart to CSquadNormal which handles active combat. When enemies are not engaged with the player, they operate in the "relaxed" state with less aggressive behavior patterns.

**Class Name:** `CRelaxedSquad` (from RTTI at 0x0063d928)
**Display Name:** "Relaxed Squad" (string at 0x0063293c)

## Functions

| Address | Name | Purpose | Size |
|---------|------|---------|------|
| 0x004ea8d0 | CRelaxedSquad__Create | Factory method - allocates and initializes relaxed squad state | ~150 bytes |
| 0x004e5840 | CSPtrSet__Init | Initialize empty pointer-set (head/tail/count = 0) | ~20 bytes |
| 0x004ea4d0 | (undefined) | Vtable entry +0x04 - likely destructor or state handler | ~unknown |
| 0x004ea780 | (undefined) | Vtable entry +0x08 - contains debug path xref | ~unknown |
| 0x004ea840 | (undefined) | Vtable entry +0x14 - member access pattern | ~unknown |
| 0x004ea980 | (undefined) | Vtable entry +0x1C - uses FPU, accesses member list | ~unknown |
| 0x004eaa5c | (undefined) | Uses "Relaxed Squad" display string | ~unknown |

## Vtable Analysis

**Vtable Address:** 0x005e3ad0

| Offset | Address | Notes |
|--------|---------|-------|
| +0x00 | 0x00405930 | Base class (shared with other squad types) |
| +0x04 | 0x004ea4d0 | CRelaxedSquad-specific |
| +0x08 | 0x004ea780 | CRelaxedSquad-specific (has debug path xref) |
| +0x0C | 0x004014c0 | Base class |
| +0x10 | 0x00405930 | Base class |
| +0x14 | 0x004ea840 | CRelaxedSquad-specific |
| +0x18 | 0x0043e9f0 | Possibly inherited |
| +0x1C | 0x004ea980 | CRelaxedSquad-specific |
| +0x20 | 0x004e8cd0 | Possibly shared |
| +0x24 | 0x0050f600 | Possibly inherited |

A second vtable reference exists at 0x005e3b10, suggesting class hierarchy or multiple inheritance.

## Key Observations

- **State Machine Pattern**: CRelaxedSquad is one state in the squad AI system. Squads transition between relaxed (patrol/idle) and normal (combat) states.
- **Member List at +0xa4**: The Create function iterates through a linked list at `this+0xa4`, adding each member to a set via `CSPtrSet__AddToHead`.
- **Memory Allocation**: Uses `OID__AllocObject(0x10, 8, ...)` pattern - allocates 16 bytes with type 8.
- **Exception Handling**: Create function sets up SEH with unwind handler at `Unwind@005d4e60`.
- **Undefined Code Region**: Most vtable entries point to code that hasn't been disassembled in Ghidra (0x004ea4d0-0x004eaa5c range). These need manual function creation.

## Related Files

- SquadNormal.cpp - Combat squad state (counterpart to relaxed)
- Squad.cpp - Base squad class
- Unit.cpp - Individual unit behavior (squad members)

## Strings

| Address | Value | Usage |
|---------|-------|-------|
| 0x00632918 | `C:\dev\ONSLAUGHT2\SquadRelaxed.cpp` | Debug path for assertions |
| 0x0063293c | `Relaxed Squad` | Display name |
| 0x0063d900 | `.?AVCRelaxedSquad@@` | RTTI type descriptor |
| 0x0063d928 | `CRelaxedSquad` | Class name |

---
*Discovered via Phase 1 xref analysis (Dec 2025)*
