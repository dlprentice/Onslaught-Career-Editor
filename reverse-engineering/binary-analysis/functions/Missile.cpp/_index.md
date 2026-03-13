# Missile.cpp Functions

> Source File: Missile.cpp | Binary: BEA.exe
> Debug Path: 0x006309c0

## Overview

Missile weapon/projectile implementation. CMissile handles guided missile behavior, initialization from configuration paths, and tracking.

## Functions

| Address | Name | Purpose | Size |
|---------|------|---------|------|
| 0x004baae0 | CMissile__Init (TODO) | Initialize missile from path/config | ~400 bytes |

## Exception Handlers

| Address | Name | Line | Purpose |
|---------|------|------|---------|
| 0x005d3c50 | Unwind@005d3c50 | 11 | Cleanup for 0x428 byte allocation |

## Key Observations

- **Large allocation** - 0x428 bytes (1064 bytes) for missile data structure
- **Path-based init** - Loads from string at this+0xf0+0xc
- **Function pointers** - Sets up callbacks at 0x00403f40 and 0x00403f80
- **Pool ID 0x61** - Uses memory pool 97

## Related Files

- Round.cpp - CRound base class for projectiles
- BattleEngine.cpp - AddProjectile creates missiles

---
*Discovered via Phase 1 xref analysis (Dec 2025)*
