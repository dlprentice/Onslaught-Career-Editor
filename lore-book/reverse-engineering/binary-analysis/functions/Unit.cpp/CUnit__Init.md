# CUnit__Init

> Address: 0x004f86d0 | Source: Unit.cpp (source file not present in `references/Onslaught/` snapshot)

## Status
- **Named in Ghidra:** Yes
- **Signature Set:** Yes (Wave526 headless postscript + focused instruction read-back verified, 2026-05-18)
- **Verified vs Source:** Partial (structure and ownership only)

## Purpose

Core unit initialization for interactive actor subclasses. Static retail read-back shows a `this` pointer plus one init/profile-style argument and a large setup body for Unit state, linked readers, weapons/effects, and follow-on helper calls.

## Signature
```c
void __thiscall CUnit__Init(void * this, void * init);
```

Current read-back is Wave526 authority:

- `subagents/ghidra-static-reaudit/wave526-unit-core-tail-004f84c0/post_metadata.tsv`
- `subagents/ghidra-static-reaudit/wave526-unit-core-tail-004f84c0/post_instructions_init_full.tsv`
- Focused instruction evidence shows `0x004f91ef RET 0x4`, proving one explicit stack argument after `ECX`.

The older 2026-03-01 high-impact snapshot recorded this function as no-stack-argument `thiscall`; Wave526 supersedes that signature.

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
- Wave526 `RET 0x4` evidence proves one init/profile argument. Exact concrete layout and source-body identity remain open.

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
