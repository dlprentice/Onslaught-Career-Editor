# CUnit__ApplyDamage

> Address: 0x004f9a90 | Source: Unit.cpp (source file not present in `references/Onslaught/` snapshot)

## Status
- **Named in Ghidra:** Yes
- **Signature Set:** Yes (headless postscript + read-back verified, 2026-03-01)
- **Verified vs Source:** Partial (damage flow only)

## Purpose

Damage calculation and application system. Handles all damage taken by a unit including shields, armor mitigation, character-specific multipliers, and special effects (invincibility, death states).

## Signature
```c
void __thiscall CUnit__ApplyDamage(void * this, float damageAmount, int damageType);
```

Read-back verified in `scratch/program_2026-03-01/phase5_signature_readback/index.tsv` (`status=OK`).

## Responsibilities

- **Shield calculation** - Reduce incoming damage by shield value
- **Armor mitigation** - Apply armor reduction multiplier
- **Character multipliers** - Different unit types take different damage
- **Invincibility check** - Bypass damage if god mode or vulnerability flags are set
- **Death handling** - Trigger death state when health reaches zero
- **Effect triggering** - Call audio/visual effects based on damage amount
- **State updates** - Update internal health/armor values

## Key Observations

- **Compact function** (~900 bytes) suggests focused damage logic
- **Shield/armor subsystem** - Separate from health bar rendering
- **Character-specific** - Kill type varies by unit, damage type also matters
- **God mode integration** - Player.cpp SetVulnerable() affects this
- **Effect coupling** - CUnit__TriggerEffect() likely called from here

## Notes

- Migrated from ghidra-analysis.md (Dec 2025)
- Related to Player.cpp: SetGodMode(), SetVulnerable()
- God mode test results (Dec 12, 2025): P2 invincibility worked in multiplayer; this is runtime state (Player/Unit vulnerability), not a known persisted `mIsGod[]` save field in the Steam build
- Invincibility bypass - ensures unlimited damage in developer builds
- Water hazards may be handled separately (environmental, not unit-based)

## Related Functions

- [CUnit__Init](./CUnit__Init.md) - Initializes health/armor values
- [CUnit__UpdateTransform](./CUnit__UpdateTransform.md) - Called after damage for position updates
- [CUnit__TriggerEffect](./CUnit__TriggerEffect.md) - Likely called from ApplyDamage for effects
- Player.cpp SetVulnerable() - Controls invincibility
- BattleEngine.cpp SetInfinateEnergy() - Related to energy drain
