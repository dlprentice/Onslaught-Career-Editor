# GillM.cpp Functions

> Source File: GillM.cpp | Binary: BEA.exe
> Debug Path: 0x0062c9e8

## Overview

CGillM is a motion controller class, likely controlling a specific enemy unit or boss character named "Gill". The class manages multiple sub-components including leg motion, Warspite-related functionality, and additional control systems. The "M" suffix follows the pattern of other motion controllers (MCMech, MCTentacle) suggesting this is a specialized motion controller.

The class appears to manage complex multi-part creature/vehicle motion with separate systems for legs and other components.

## Functions

| Address | Name | Purpose | Size |
|---------|------|---------|------|
| 0x00479a50 | CGillM__InitLegMotion | Creates and initializes leg motion controller (0xF0 byte object) | ~237 bytes |
| 0x00479b60 | CGillM__InitWarspiteComponent | Creates Warspite-related component (0x60 byte object) | ~132 bytes |
| 0x00479cb0 | CGillM__InitComponent208 | Creates auxiliary component (0x20 byte object) at offset 0x208 | ~96 bytes |

## Function Details

### CGillM__InitLegMotion (0x00479a50)

Initializes the leg motion system for the Gill unit.

**Key operations:**
- Searches for "LegMotion" string via virtual call at `[this+0x30]->vtable[0x24]`
- Allocates 0xF0 (240) byte object via memory allocator
- Calls sub-initialization at 0x004983b0
- Sets vtable pointer to 0x005dbc74
- Stores leg motion object at `this+0x70`
- Initializes motion parameters from entity data at `param_1+0x3bc`:
  - Uses float constants: 0x4059999a (3.4f), 0x3f7d70a4 (0.99f)
  - Reads position/rotation data from offsets 0x140-0x150

**Allocation info:** Type 0x1B, line 0x2D (45)

### CGillM__InitWarspiteComponent (0x00479b60)

Initializes a Warspite-related component. "Warspite" may be a ship or large vehicle class.

**Key operations:**
- Allocates 0x60 (96) byte object
- Calls initialization function at 0x004fe710 (similar to CWarspite__Init pattern)
- Sets vtable pointer to 0x005dbcb4
- Stores component at `this+0x13c`

**Allocation info:** Type 0x16, line 0x38 (56)

### CGillM__InitComponent208 (0x00479cb0)

Initializes an auxiliary component stored at offset 0x208.

**Key operations:**
- Allocates 0x20 (32) byte object
- Calls initialization at 0x004f1ec0
- Stores result at `this+0x208`

**Allocation info:** Type 0x17, line 0x3E (62)

## Class Layout (Partial)

Based on the initialization functions:

| Offset | Size | Member | Description |
|--------|------|--------|-------------|
| 0x30 | 4 | pAnimController | Pointer to animation/model controller |
| 0x70 | 4 | pLegMotion | Leg motion controller (0xF0 byte object) |
| 0x13c | 4 | pWarspiteComponent | Warspite-related component (0x60 byte object) |
| 0x208 | 4 | pComponent208 | Auxiliary component (0x20 byte object) |

## Related Files

- **GillMHead.cpp** - Head motion controller (separate source file nearby at 0x0062ca08)
- **MCMech.cpp** - Similar motion controller pattern for mechs
- **MCTentacle.cpp** - Similar motion controller pattern for tentacles

## Key Observations

1. **Multi-component architecture**: CGillM manages at least 3 sub-components (leg motion, Warspite, aux)
2. **Warspite connection**: References to CWarspite suggest this may be a large naval vessel or amphibious unit
3. **Motion controller pattern**: Follows the MC* naming convention for motion controllers
4. **Memory allocation tracking**: All allocations use debug allocator with type IDs and line numbers
5. **Exception handling**: All functions use SEH (Structured Exception Handling) via FS segment

## Vtable References

| Address | Component |
|---------|-----------|
| 0x005dbc74 | LegMotion vtable |
| 0x005dbcb4 | WarspiteComponent vtable |

---
*Discovered via Phase 1 xref analysis (Dec 2025)*
