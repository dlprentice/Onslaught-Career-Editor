# ThunderHead.cpp Functions

> Source File: ThunderHead.cpp | Binary: BEA.exe
> Debug Path: 0x00633240

## Overview

CThunderHead is a large bipedal enemy mech unit - the "Thunderhead" boss mech. This file handles initialization of its subsystems including leg motion (walking animation), Warspite AI controller (combat behavior), and guidance system (targeting). The ThunderHead appears to be one of the larger enemy mechs in the game, using similar systems to the player mech but configured for AI control.

## Functions

| Address | Name | Purpose | Size |
|---------|------|---------|------|
| 0x004f4730 | [CThunderHead__CreateLegMotion](./CThunderHead__CreateLegMotion.md) | Creates leg animation system, loads "LegMotion" asset | ~256 bytes |
| 0x004f4830 | [CThunderHead__CreateWarspite](./CThunderHead__CreateWarspite.md) | Creates Warspite AI controller for combat | ~112 bytes |
| 0x004f48a0 | [CThunderHead__CreateGuide](./CThunderHead__CreateGuide.md) | Creates guidance/targeting system | ~96 bytes |

## Exception Handlers

| Address | Name | Line | Purpose |
|---------|------|------|---------|
| 0x005d5280 | Unwind@005d5280 | 0x20 (32) | Cleanup for leg motion (0xf0/240 byte allocation) |
| 0x005d52a0 | Unwind@005d52a0 | 0x2b (43) | Cleanup for Warspite (0x60/96 byte allocation) |
| 0x005d52c0 | Unwind@005d52c0 | 0x31 (49) | Cleanup for guide (0x30/48 byte allocation) |

## Key Observations

- **CThunderHead inherits from CUnit** - Uses standard unit infrastructure (transform, effects, etc.)
- **Three main subsystems**:
  1. **Leg Motion** (240 bytes) - Walking animation system, same "LegMotion" asset as player mech
  2. **Warspite AI** (96 bytes) - Combat AI controller (see Warspite.cpp)
  3. **Guide** (48 bytes) - Targeting/guidance system
- **VTable at 0x005e11b0** - Contains pointers to these three creation methods
- **Memory allocation** - Uses pool IDs 0x1b, 0x16, 0x17 for the three subsystems
- **Position data** - CreateLegMotion reads position/rotation from param_1+0x3bc struct

## CThunderHead Object Layout (Partial)

| Offset | Field | Notes |
|--------|-------|-------|
| 0x00 | vtable | Virtual function table |
| 0x08 | (inherited) | CUnit base class fields |
| 0x30 | mSomeController | Pointer to controller with method at +0x24 |
| 0x70 | mLegMotion | Pointer to leg motion system (240 bytes) |
| 0x13c | mWarspite | Pointer to CWarspite AI controller (96 bytes) |
| 0x208 | mGuide | Pointer to guidance system (48 bytes) |

## Related Classes

- **CMCThunderHead** (`.?AVCMCThunderHead@@` at 0x00633228) - Mission Control variant
- **CThunderHeadBehaviourType** (0x00627d88) - AI behavior type definition
- **CThunderheadGuide** (0x00633288) - Guidance system class

## Related Strings

- `"LegMotion"` (0x00623074) - Animation asset name
- `"Thunderhead Main Gun"` (0x006247e0) - Weapon name
- `"Thunderhead Flamethrower"` (0x00633264) - Secondary weapon
- `"m_thunderhead.msh"` (0x0062d304) - Mesh file name
- `"CThunderHead"` (0x0063d868) - Class name string

## Related Files

- Mech.cpp - Player mech uses similar leg motion system
- Warspite.cpp - CWarspite AI controller implementation
- Unit.cpp - Base class for all units
- BattleEngine.cpp - Combat system integration

---
*Discovered via ThunderHead.cpp xref analysis (Dec 2025)*
