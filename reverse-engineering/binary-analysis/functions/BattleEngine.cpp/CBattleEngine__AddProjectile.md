# CBattleEngine__AddProjectile

> Address: 0x00406fc0 | Source: `references/Onslaught/BattleEngine.cpp`

## Status
- **Named in Ghidra:** Yes
- **Signature Set:** No
- **Verified vs Source:** Partial (decompiler output matches pattern)

## Purpose

Spawn projectiles into the battle engine's active weapon list. Manages weapon projectiles with:

1. Weapon enable/disable flag checking
2. Duplicate prevention (checks if weapon already in active list)
3. Weapon node structure allocation (20 bytes)
4. Physics parameter assignment (timing, duration, type)
5. Addition to weapon effects container

**Key Feature:** Prevents duplicate weapons by traversing the active weapon list before allocating.

## Signature

```c
// thiscall - ecx = CBattleEngine*
void CBattleEngine::AddProjectile(
  int weaponType,      // param_1: Weapon type/ID
  float duration,      // param_2: Projectile duration/lifetime
  undefined4 param_3   // param_3: Unknown (projectile data or type flag)
);
```

## Decompiled Logic

```cpp
void CBattleEngine::AddProjectile(int weaponType, float duration, undefined4 param_3) {
  // Check weapon disabled flag
  if ((*(byte *)(weaponType + 0x2c) & 4) == 0) {

    // Get active weapon list head
    WeaponNode *head = *(WeaponNode **)(ecx + 0x294);

    // Traverse list to check for duplicates
    WeaponNode *current = head;
    while (current != NULL) {
      if (current->weaponId == weaponType) {
        return;  // Already in list, don't add again
      }
      current = current->next;
    }

    // Allocate new weapon node (20 bytes)
    WeaponNode *newNode = allocate(0x14);

    if (newNode != NULL) {
      // Initialize weapon node
      newNode->weaponId = 0;
      newNode->field3 = 0;  // offset +0xc

      // Set physics parameters
      newNode->duration = DAT_00672fd0;      // Current time reference
      newNode->field1 = DAT_00672fd0;        // offset +0x04
      newNode->type = param_3;               // offset +0x10
      newNode->lifetime = DAT_00672fd0 + duration;  // offset +0x08
    }

    // Add to weapon effects container
    AddToList(newNode);
  }
}
```

## Key Observations

### Weapon Disabled Flag Check
- Tests flag at `weaponType + 0x2c` & 4
- Bit 2 indicates weapon is disabled (0 = enabled, 1 = disabled)
- Function returns early if weapon is disabled

### Active Weapon List
- Maintains list at offset **ECX+0x294**
- Each node has `next` pointer at offset +0x04
- List is traversed to prevent duplicates
- If weapon already exists, function returns without allocation

### Weapon Node Structure (20 bytes)
| Offset | Type | Field | Purpose |
|--------|------|-------|---------|
| +0x00 | int | weaponId | Weapon type/ID |
| +0x04 | float/int | duration | Time reference (DAT_00672fd0) |
| +0x08 | float | lifetime | End time (duration + param_2) |
| +0x0c | int | unknown | Set to 0 |
| +0x10 | undefined4 | type | Projectile type (param_3) |

### Time Reference
- `DAT_00672fd0` appears to be a global time counter (game ticks or seconds)
- Used as both start time and base for calculating lifetime
- Lifetime = current_time + duration_param

### Integration Pattern
- Weapon list at ECX+0x294 is primary active list
- Physical effects list at ECX+0xe (via UpdateWeaponEffect)
- AddProjectile manages weapon nodes, UpdateWeaponEffect manages physics
- Both add to containers via `CSPtrSet__AddToTail` (`0x004e5b20`) (generic add-to-list helper)

## Binary Offsets (from ECX)
| Offset | Purpose |
|--------|---------|
| +0x294 | Active weapon list head |
| +0x29c | Weapon list iterator (scratch) |
| +0xe | Weapon effects container |

## Comparison with UpdateWeaponEffect

| Aspect | AddProjectile | UpdateWeaponEffect |
|--------|---------------|--------------------|
| **Allocates** | Weapon node (20 bytes) | Physics object (32 bytes) |
| **Stores at** | ECX+0x294 | ECX+0xe |
| **Key parameter** | weaponType, duration | (none - uses ECX state) |
| **Duplicate check** | Yes (traverse list) | No |
| **Timestamp** | Uses DAT_00672fd0 | Calls GetMaxLife() |

## Exception Handling
- Uses Windows SEH pattern (try/finally)
- All allocations guarded against NULL
- Early return if weapon disabled (no cleanup needed)

## Notes
- Medium-sized function (~50 LOC decompiled)
- Efficient duplicate prevention via list traversal
- Global time variable (DAT_00672fd0) suggests frame-synchronized timing
- Weapon disabled flag suggests per-weapon enable/disable control (e.g., ammo depletion)

## Related Functions
- [CBattleEngine__Init](CBattleEngine__Init.md) - Initializes weapon systems
- [CBattleEngine__UpdateWeaponEffect](CBattleEngine__UpdateWeaponEffect.md) - Updates weapon physics
- CBattleEngineWalkerPart - Walker weapon subsystem
- CBattleEngineJetPart - Jet weapon subsystem
