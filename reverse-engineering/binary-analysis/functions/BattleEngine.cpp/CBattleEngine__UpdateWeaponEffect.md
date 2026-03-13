# CBattleEngine__UpdateWeaponEffect

> Address: 0x004063b0 | Source: `references/Onslaught/BattleEngine.cpp`

## Status
- **Named in Ghidra:** Yes
- **Signature Set:** No
- **Verified vs Source:** Partial (decompiler output matches pattern)

## Purpose

Updates weapon effect physics - creates a physics object for active weapon projectiles. Calculates speed and angular velocity based on current battle engine state.

**Core Logic:**
1. Query battle engine's current max life (health parameter)
2. Allocate 32-byte physics object (weapon effect structure)
3. Initialize physics object with:
   - Reference max life value
   - Squared max life (life * life)
   - Gravity modifier (0.5 * gravity)
4. Add physics object to weapon effects container

## Signature

```c
// thiscall - ecx = CBattleEngine*
void CBattleEngine::UpdateWeaponEffect(void);
```

## Decompiled Logic

```cpp
void CBattleEngine::UpdateWeaponEffect(void) {
  // Get max life from virtual function (offset 0x40)
  float maxLife = (*vftable[0x40])();

  // Allocate physics object (32 bytes)
  PhysicsObject *effect = allocate(0x20);

  if (effect != NULL) {
    // Get gravity from virtual function (offset 0xc0)
    float gravity = (*vftable[0xc0])();

    // Initialize physics fields
    effect->field1 = 0;
    effect->field2 = 0;
    effect->field3 = 0;
    effect->maxLife = maxLife;           // Offset +0x14
    effect->vftable = PhysicsVTable;     // Offset +0x00
    effect->sqMaxLife = maxLife * maxLife; // Offset +0x18
    effect->gravityMod = gravity * 0.5f;   // Offset +0x1c
  }

  // Add to weapon effects container
  AddToList(effect);
}
```

## Key Observations

### Physics Object Structure (32 bytes)
| Offset | Type | Field | Purpose |
|--------|------|-------|---------|
| +0x00 | void* | vftable | Physics object virtual function table |
| +0x04 | int | field1 | Unknown (set to 0) |
| +0x08 | int | field2 | Unknown (set to 0) |
| +0x0c | int | field3 | Unknown (set to 0) |
| +0x10 | int | unknown | Unknown (set to 0) |
| +0x14 | float | maxLife | Current battle engine max life |
| +0x18 | float | sqMaxLife | Squared max life (life * life) |
| +0x1c | float | gravityMod | Gravity * 0.5 |

### Virtual Function Calls
- **GetMaxLife()** at `[vftable + 0x40]` - Returns current max life/health
- **GetGravityMod()** at `[vftable + 0xc0]` - Returns gravity modifier
- Both called on CBattleEngine thiscall (ECX = this)

### Weapon Effects Container
- Added to container at offset **ECX+0xe** via virtual function at **[vftable + 0x24]**
- Suggests weapon effects are stored in an array or linked list
- May be iterated during update/render passes

## Binary Offsets (from ECX)
| Offset | Purpose |
|--------|---------|
| +0x00 | vftable (primary) |
| +0xe | Weapon effects container |
| +0x40 | GetMaxLife vfunc |
| +0xc0 | GetGravityMod vfunc |
| +0x294 | Active weapon list (used by AddProjectile) |

## Integration with AddProjectile

This function pairs with `CBattleEngine__AddProjectile` in the weapon system:
- **AddProjectile:** Creates weapon node structure, manages weapon list at ECX+0x294
- **UpdateWeaponEffect:** Creates physics object for weapon effects, manages container at ECX+0xe

Both allocate small structures (~20-32 bytes) and add to game object containers.

## Notes
- Relatively small, focused function (~40 LOC decompiled)
- Part of weapon system physics calculation pipeline
- Gravity modifier suggests altitude/terrain interaction
- Squared life value may be used for distance/range calculations

## Related Functions
- [CBattleEngine__Init](CBattleEngine__Init.md) - Initializes weapon systems
- [CBattleEngine__AddProjectile](CBattleEngine__AddProjectile.md) - Spawns weapon projectiles
- CBattleEngineWalkerPart - Walker physics subsystem
- CBattleEngineJetPart - Jet physics subsystem
