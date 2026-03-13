# CMech__InitTargeting

> Address: 0x0049faa0 | Source: Mech.cpp (source file not present in `references/Onslaught/` snapshot)

## Status
- **Named in Ghidra:** Yes
- **Signature Set:** No
- **Verified vs Source:** Partial (struct size verified at 0x48 bytes)

## Purpose

Initialize the targeting system for the player mech's head unit. Sets up the targeting reticle, lock-on system, and head orientation tracking. This controls the crosshair display and which enemies are currently in the targeting cone.

## Signature
```c
// TODO: Add verified signature
void __thiscall CMech::InitTargeting(CMech *this);
```

## Responsibilities

- **Head unit linkage** - Link targeting system to mech's head transform
- **Targeting struct allocation** - Create and configure 0x48-byte (72-byte) targeting data
- **Reticle setup** - Initialize targeting crosshair/reticle rendering and movement
- **Lock-on system** - Register target tracking and acquisition callbacks
- **Head orientation** - Link head pitch/yaw to targeting cone direction
- **Target filtering** - Set up targeting priorities (mechs, vehicles, helicopters, etc.)

## Key Observations

- **0x48-byte struct** (72 bytes) - Compact targeting configuration object
- **Head-mounted targeting** - Targeting direction follows head orientation (NOT weapon facing)
- **Player mech only** - AI units have simpler targeting (not player-facing HUD reticle)
- **Reticle rendering** - Visual feedback system for lock-on and leading
- **Distinct from cockpit** - Cockpit is first-person view, targeting is reticle overlay system

## Notes

- Migrated from ghidra-analysis.md (Dec 2025)
- Called during CMech initialization (after base CUnit__Init, alongside leg motion and cockpit)
- Targeting struct created with new/malloc - must be freed on mech destruction
- Head unit reference likely stored as member variable (used for transform updates)
- Test with: Play campaign level, verify reticle follows head movement and targets lock on

## Related Functions

- [CMech__InitLegMotion](./CMech__InitLegMotion.md) - Leg animation setup (called adjacent)
- [CMech__InitCockpit](./CMech__InitCockpit.md) - Cockpit/camera setup (called adjacent)
- [CUnit__Init](../Unit.cpp/CUnit__Init.md) - Base class initialization (called before targeting)
- [CUnit__UpdateTransform](../Unit.cpp/CUnit__UpdateTransform.md) - Position/rotation calc (reticle follows head)
