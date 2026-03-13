# Round.cpp Functions

> Source File: Round.cpp | Binary: BEA.exe
> Debug Path: 0x00631d38

## Overview

Projectile/round base class implementation. CRound handles generic projectile behavior including distance calculations, raycasts, and gameplay mode handling.

## Functions

| Address | Name | Purpose | Size |
|---------|------|---------|------|
| 0x004d8410 | CRound__Init (TODO) | Initialize round/projectile state | ~2000 bytes |

## Exception Handlers

| Address | Name | Line | Purpose |
|---------|------|------|---------|
| 0x005d4970 | Unwind@005d4970 | 98 | Cleanup for 0x1c byte allocation |
| 0x005d4989 | Unwind@005d4989 | 108 | Cleanup for 0x3c byte allocation |
| 0x005d49e8 | Unwind@005d49e8 | 531 | Cleanup for late allocation |

## Key Observations

- **Large function** - ~2000 bytes, complex initialization
- **Multiple allocations** - Lines 98, 108, 531 in original source
- **Distance/raycast** - Uses SQRT operations for collision
- **Gameplay modes** - Handles different projectile behaviors
- **Base class** - Parent for CMissile and other projectile types

## Related Files

- Missile.cpp - CMissile derived class
- BattleEngine.cpp - Creates rounds via AddProjectile

---
*Discovered via Phase 1 xref analysis (Dec 2025)*
