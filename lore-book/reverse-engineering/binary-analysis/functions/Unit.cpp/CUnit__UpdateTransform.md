# CUnit__UpdateTransform

> Address: 0x004fc4e0 | Source: Unit.cpp (source file not present in `references/Onslaught/` snapshot)

## Status
- **Named in Ghidra:** Yes
- **Signature Set:** No
- **Verified vs Source:** Partial (transform only)

## Purpose

World-space position and rotation calculation. Called every frame to update unit location based on velocity, current heading, and physics calculations. Integrates with collision detection and terrain.

## Signature
```c
// TODO: Add verified signature
void __thiscall CUnit::UpdateTransform(CUnit *this, float deltaTime);
```

## Responsibilities

- **Position update** - Apply velocity to current position
- **Rotation update** - Adjust heading/pitch/roll based on movement direction
- **Terrain integration** - Snap unit to ground level, handle slopes
- **Collision response** - Adjust position if hitting obstacles
- **Animation synchronization** - Update animation playback based on movement
- **Visual updates** - Ensure D3D mesh position matches world position

## Key Observations

- **Compact function** (~400 bytes) indicates streamlined calculation
- **Frame-rate independent** - Uses deltaTime for smooth physics
- **Terrain-aware** - Integrates with World.cpp terrain system
- **Called every frame** - Performance-critical function
- **Visual/physics sync** - Ensures no position mismatch between collision and rendering

## Notes

- Migrated from ghidra-analysis.md (Dec 2025)
- Called from battle engine main loop each frame
- Terrain height calculation tied to World.cpp heightmap
- Animation frame advance may be driven by position change
- Critical for smooth unit movement in levels

## Related Functions

- [CUnit__Init](./CUnit__Init.md) - Sets initial position/velocity
- [CUnit__ApplyDamage](./CUnit__ApplyDamage.md) - May trigger movement state changes
- World.cpp CWorld__LoadWorld - Provides terrain heightmap
- BattleEngine.cpp - Calls UpdateTransform each frame
