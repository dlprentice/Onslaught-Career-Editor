# collisionseekingthing.cpp Functions

> Source File: collisionseekingthing.cpp | Binary: BEA.exe
> Debug Path: 0x006246d8 (`C:\dev\ONSLAUGHT2\collisionseekingthing.cpp`)

## Overview

Collision-seeking thing system - base class or component for entities that seek targets while avoiding collisions.

**Status: STUB - Needs xref analysis via Ghidra MCP**

## Debug Path Location

- **Address**: 0x006246d8
- **String**: `C:\dev\ONSLAUGHT2\collisionseekingthing.cpp`

## Functions

| Address | Name | Purpose | Status |
|---------|------|---------|--------|
| - | - | No functions discovered | Pending xref analysis |

## Related Files

- CollisionSeekingRound.cpp - Seeking projectiles (documented, 9 functions)
- Missile.cpp - Guided missiles (documented)
- Round.cpp - Projectile base class (documented)

## Notes

This file likely provides base functionality for collision-seeking behavior used by:
- Homing missiles
- Seeking projectiles
- AI pathfinding that avoids obstacles

May be companion file to `CollisionSeekingRound.cpp` which has full documentation.

## TODO

1. [ ] Find xrefs to debug path string 0x006246d8
2. [ ] Analyze class relationship with CollisionSeekingRound
3. [ ] Document collision avoidance algorithms

---

*Stub created: 2025-12-17*
