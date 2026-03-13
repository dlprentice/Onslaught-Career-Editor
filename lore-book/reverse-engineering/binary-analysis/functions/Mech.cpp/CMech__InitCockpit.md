# CMech__InitCockpit

> Address: 0x0049fa30 | Source: Mech.cpp (source file not present in `references/Onslaught/` snapshot)

## Status
- **Named in Ghidra:** Yes
- **Signature Set:** No
- **Verified vs Source:** Partial (struct size verified at 0x64 bytes)

## Purpose

Initialize the cockpit/camera system for the player mech. Sets up the first-person camera viewpoint, HUD overlays, and cockpit-specific rendering. This creates the "inside the mech" experience during gameplay.

## Signature
```c
// TODO: Add verified signature
void __thiscall CMech::InitCockpit(CMech *this);
```

## Responsibilities

- **Camera setup** - Initialize first-person camera position relative to mech head/cockpit
- **Cockpit struct allocation** - Create and configure 0x64-byte (100-byte) cockpit data structure
- **HUD rendering** - Register cockpit overlay, reticle, radar, status indicators
- **View frustum** - Set up camera FOV and clipping planes for cockpit view
- **Input mapping** - Cockpit camera may have separate mouse/controller input handling
- **Cockpit-specific callbacks** - Register events (damage effects, g-forces, etc.)

## Key Observations

- **100-byte struct** (0x64) - Moderately-sized cockpit configuration object
- **Player mech only** - Enemy mechs don't render cockpit (use follow-cam or no HUD)
- **First-person experience** - Fundamental to single-player campaign gameplay
- **Related to visual immersion** - Cockpit cockpits, lens flares, viewport distortions
- **Distinct from targeting** - Cockpit is view/camera, targeting is reticle/lock-on system

## Notes

- Migrated from ghidra-analysis.md (Dec 2025)
- Called during CMech initialization (after base CUnit__Init, alongside leg motion)
- Cockpit struct created with new/malloc - must be freed on mech destruction
- Related to PauseMenu rendering - pause menu must handle cockpit camera state
- Test with: Play campaign level, verify proper cockpit view and HUD rendering

## Related Functions

- [CMech__InitLegMotion](./CMech__InitLegMotion.md) - Leg animation setup (called adjacent)
- [CMech__InitTargeting](./CMech__InitTargeting.md) - Targeting reticle setup (called adjacent)
- [CUnit__Init](../Unit.cpp/CUnit__Init.md) - Base class initialization (called before cockpit)
