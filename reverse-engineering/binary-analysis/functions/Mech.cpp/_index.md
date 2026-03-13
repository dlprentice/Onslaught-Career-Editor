# Mech.cpp Functions

> Source File: Mech.cpp | Binary: BEA.exe

## Overview

Player mech specialization extending CUnit base class. This file handles player-specific features including leg animation, cockpit/camera systems, and targeting reticle. Focuses on features unique to player-controlled mechs vs. other unit types.

## Functions

| Address | Name | Purpose | Size |
|---------|------|---------|------|
| 0x0049f940 | [CMech__InitLegMotion](./CMech__InitLegMotion.md) | Leg animation setup, loads "LegMotion" asset | ~300 bytes |
| 0x0049fa30 | [CMech__InitCockpit](./CMech__InitCockpit.md) | Cockpit/camera setup, 100-byte struct | ~250 bytes |
| 0x0049faa0 | [CMech__InitTargeting](./CMech__InitTargeting.md) | Head/targeting reticle setup, 0x48-byte struct | ~200 bytes |

## Key Observations

- **CMech is subclass of CUnit** - Inherits health, damage, transform, effects
- **Focused on player experience** - Cockpit camera, targeting reticle, leg animation
- **Asset-driven** - Loads external "LegMotion" animation data
- **Smaller functions** - Each ~200-300 bytes (vs CUnit ~400-2000 bytes)
- **Not used for enemies** - AI units use CUnit directly without mech-specific features
- **Player mech only** - All three functions are player-specific initialization

## Related Files

- Unit.cpp - Base class functions (CUnit__Init, CUnit__ApplyDamage, etc.)
- Career.cpp - Kill tracking (player kills tracked as TK_MECHS)
- Player.cpp - Player-specific invincibility (runtime `CPlayer::mIsGod` / `SetVulnerable(FALSE)`; cheat-gated in retail)
- World.cpp - Level data, asset loading ("LegMotion" from AYA archive)

---
*Migrated from ghidra-analysis.md (Dec 2025)*
