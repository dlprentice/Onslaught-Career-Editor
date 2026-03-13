# CUnit__Init

> Address: 0x004f86d0 | Source: Unit.cpp (source file not present in `references/Onslaught/` snapshot)

## Status
- **Named in Ghidra:** Yes
- **Signature Set:** Yes (headless postscript + read-back verified, 2026-03-01)
- **Verified vs Source:** Partial (structure only)

## Purpose

Complete unit initialization for any interactive actor in the game. Called when spawning a unit into the world - sets up weapons, turrets, equipment, and initial state. This is the master initialization function for the CUnit class.

## Signature
```c
void __thiscall CUnit__Init(void * this);
```

Read-back verified in `scratch/program_2026-03-01/phase5_signature_readback/index.tsv` (`status=OK`).

## Responsibilities

- **Weapon setup** - Initialize primary weapon system with ammo/energy
- **Turret initialization** - Load turret models and targeting systems
- **Equipment configuration** - Shields, armor, special equipment
- **Kill classification** - Set unit type (AIRCRAFT, VEHICLE, MECH, INFANTRY, EMPLACEMENT)
- **Health/damage state** - Initialize armor/shield values
- **Collision setup** - Register with physics/collision system
- **Audio/visual setup** - Prepare effects triggers and sound categories

## Key Observations

- **Large function** (~2KB) indicates complex initialization sequence
- Distinguishes unit types - directly affects kill count category
- Weapon system integration - determines which kills count as AIRCRAFT vs VEHICLE kills
- Turret system - separate from main weapon (e.g., mech secondary turrets)
- Equipment slots - armor/shield configuration tied to unit class

## Notes

- Migrated from ghidra-analysis.md (Dec 2025)
- Related to kill tracking: TK_AIRCRAFT, TK_VEHICLES, TK_MECHS, TK_INFANTY (typo), TK_EMPLACEMENTS
- Called during world load when enemy units spawn
- Player mech initialization goes through CMech subclass (which calls CUnit__Init)
- Test with gold save: enemies spawn and accumulate correct kill types

## Related Functions

- [CMech__InitLegMotion](../Mech.cpp/CMech__InitLegMotion.md) - Player mech-specific leg setup
- [CMech__InitCockpit](../Mech.cpp/CMech__InitCockpit.md) - Player mech cockpit/camera
- [CUnit__ApplyDamage](./CUnit__ApplyDamage.md) - Called when unit takes damage
- [CUnit__UpdateTransform](./CUnit__UpdateTransform.md) - Called each frame for position/rotation
