# CMech__InitLegMotion

> Address: 0x0049f940 | Source: Mech.cpp (source file not present in `references/Onslaught/` snapshot)

## Status
- **Named in Ghidra:** Yes
- **Signature Set:** Yes (headless postscript + read-back verified, 2026-03-01)
- **Verified vs Source:** Partial (behavior-level for player-mech path; source file is not present in current `references/Onslaught/` snapshot, and AI mechs do not use this leg-motion path)

## Purpose

Initialize the leg animation system for the player mech. Loads the "LegMotion" asset from the game archive and sets up the animation controller for walking/running/jumping leg movements. Called during player mech spawning in the cockpit view.

## Signature
```c
void __thiscall CMech__InitLegMotion(void * this);
```

Read-back verified in `scratch/program_2026-03-01/phase5_signature_readback/index.tsv` (`status=OK`).

## Responsibilities

- **Asset loading** - Load "LegMotion" animation data from AYA archive
- **Animation state setup** - Initialize leg animation controller/state machine
- **Motion parameters** - Configure walk/run/jump animation blend factors
- **Skeletal setup** - Link leg bones to animation system if applicable
- **Callback registration** - Register animation events (footstep sounds, dust effects)

## Key Observations

- **Small function** (~300 bytes) - Focused asset loading and setup
- **Asset-driven** - Uses external "LegMotion" animation data (AYA format)
- **Player mech only** - AI units don't have specialized leg animation
- **Animation state machine** - Likely integrates with movement system for smooth transitions
- **"LegMotion" asset name** - Suggests dedicated animation data for player legs specifically

## Notes

- Migrated from ghidra-analysis.md (Dec 2025)
- Called during CMech initialization (after base CUnit__Init)
- Asset loading may fail gracefully if "LegMotion" not found (feature not critical)
- Related to visual polish - not core gameplay mechanic
- Test with: Play campaign level, verify smooth leg animation in cockpit view

## Related Functions

- [CMech__InitCockpit](./CMech__InitCockpit.md) - Cockpit/camera setup (called adjacent)
- [CMech__InitTargeting](./CMech__InitTargeting.md) - Targeting reticle setup (called adjacent)
- [CUnit__Init](../Unit.cpp/CUnit__Init.md) - Base class initialization (called before leg motion)
