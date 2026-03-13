# CUnit__TriggerEffect

> Address: 0x004fe030 | Source: Unit.cpp (source file not present in `references/Onslaught/` snapshot)

## Status
- **Named in Ghidra:** Yes
- **Signature Set:** No
- **Verified vs Source:** Partial (effects only)

## Purpose

Sound and visual effects system driven by unit health state. Triggers explosion sounds, damage sparks, fire effects, and environmental interactions based on damage taken and unit status.

## Signature
```c
// TODO: Add verified signature
void __thiscall CUnit::TriggerEffect(CUnit *this, int effectType, const D3DVECTOR *position);
```

## Responsibilities

- **Sound effects** - Play hit/impact/explosion sounds based on damage type
- **Visual effects** - Spawn particle effects at damage location
- **Fire effects** - Progressive damage smoke/flames as unit burns
- **Explosion effects** - Large effects when unit is destroyed
- **Environmental effects** - Sparks, ricochets, impact craters
- **Health state feedback** - Intensity scales with damage amount

## Key Observations

- **Compact function** (~500 bytes) - data-driven effect lookup
- **Position-based** - Effects spawned at specific world locations
- **Health-state driven** - Different effects for light/medium/critical damage
- **Audio integration** - Sound categories tied to unit type
- **Particle system** - Likely uses shared particle engine

## Notes

- Migrated from ghidra-analysis.md (Dec 2025)
- Called from CUnit__ApplyDamage when taking damage
- Effect types correlate with damage categories (projectile, melee, explosive, environmental)
- Visual feedback critical for player awareness in combat
- Audio queues likely from shared sound system used by BattleEngine.cpp

## Related Functions

- [CUnit__ApplyDamage](./CUnit__ApplyDamage.md) - Calls TriggerEffect when damage applied
- [CUnit__Init](./CUnit__Init.md) - Sets health thresholds for effect triggers
- BattleEngine.cpp - Audio engine integration
- World.cpp - Particle system, terrain integration for effects
