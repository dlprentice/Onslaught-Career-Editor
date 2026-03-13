# Sentinel.cpp - Function Mappings

> CSentinel class - AI-controlled defensive turret/sentinel unit
> Debug path: `C:\dev\ONSLAUGHT2\Sentinel.cpp` (0x0063221c)

## Overview

CSentinel is an AI-controlled defensive unit that can be activated/deactivated and has flamethrower weapons. It inherits from the game's unit hierarchy and uses animation states ("activate", "inactive") for visual feedback.

## Class Hierarchy

```
CThing
  CUnit
    CSentinel
```

## Functions

### CSentinel::CSentinel (Constructor)

| Property | Value |
|----------|-------|
| Address | 0x004dea50 |
| Status | **NEEDS MANUAL CREATION** |
| Ghidra Label | LAB_004dea50 |
| Calling Convention | thiscall |
| Returns | CSentinel* (this) |

**Notes:**
- Ghidra does not recognize this as a function - requires manual function creation at 0x004dea50
- References debug path at 0x004dead4 (push 0x63221c)
- Sets up vtable pointers at this+0 and this+4
- Initializes member variables including weapon slots
- Uses SEH (Structured Exception Handling) prologue: `mov eax, fs:[0]`
- Function ends at 0x004debf6 (ret 4)

**Xrefs TO this address:**
- 0x005e0904 (vtable entry)

---

### CSentinel::scalar_deleting_dtor

| Property | Value |
|----------|-------|
| Address | 0x004dec00 |
| Status | RENAMED |
| Ghidra Name | CSentinel__scalar_deleting_dtor |
| Calling Convention | thiscall |
| Parameters | byte param_1 (delete flag) |
| Returns | void |

**Decompiled:**
```cpp
void CSentinel__scalar_deleting_dtor(byte param_1)
{
    CSentinel__Destructor();
    if ((param_1 & 1) != 0) {
        operator_delete(this);
    }
}
```

**Notes:**
- Compiler-generated scalar deleting destructor
- Calls CSentinel__Destructor then optionally frees memory
- Referenced from vtable at 0x005deca0

---

### CSentinel::Destructor

| Property | Value |
|----------|-------|
| Address | 0x004dec20 |
| Status | RENAMED |
| Ghidra Name | CSentinel__Destructor |
| Calling Convention | thiscall |
| Returns | void |

**Decompiled:**
```cpp
void CSentinel__Destructor(void)
{
    this->vtable = &PTR_LAB_005d8d1c;  // Reset to base vtable

    // Clean up member at offset 0x28 (weapon/component)
    if ((this[10] != 0) && (*(int*)(this[10] + 4) != 0)) {
        CSPtrSet__Remove(this + 10);
    }

    // Clean up member at offset 0x24
    if ((this[9] != 0) && (*(int*)(this[9] + 4) != 0)) {
        CSPtrSet__Remove(this + 9);
    }

    // Clean up member at offset 0x0c
    if ((this[3] != 0) && (*(int*)(this[3] + 4) != 0)) {
        CSPtrSet__Remove(this + 3);
    }

    // Call base destructor
    CMonitor__Shutdown();  // formerly FUN_004bac40
}
```

**Notes:**
- Uses SEH exception handling
- Cleans up 3 member objects at offsets 0x0c, 0x24, 0x28
- Resets vtable to base class (0x005d8d1c)

---

### CSentinel::UpdateFlamethrowers

| Property | Value |
|----------|-------|
| Address | 0x004decc0 |
| Status | RENAMED |
| Ghidra Name | CSentinel__UpdateFlamethrowers |
| Calling Convention | thiscall |
| Returns | void |

**Decompiled:**
```cpp
void CSentinel__UpdateFlamethrowers(void)
{
    FUN_0047c970();  // Update base

    // Iterate through linked list at this+0x17c
    int* pList = *(int**)(this + 0x17c);
    int item = (pList != NULL) ? *pList : 0;

    while (item != 0) {
        // Check if item name matches "Sentinel Flamethrower"
        int result = strcmp("Sentinel Flamethrower", *(char**)(item + 0xa4));

        if ((result == 0) && (FUN_00509f70() != 0)) {
            int check = CSentinel__CheckWeaponSlot(item);
            if (check != 0) {
                FUN_00506010();  // Fire flamethrower
            }
        }

        // Move to next in list
        pList = (int*)pList[1];
        item = (pList != NULL) ? *pList : 0;
    }
}
```

**Notes:**
- Iterates through weapon list looking for "Sentinel Flamethrower" weapons
- Uses string comparison at 0x00568390 (likely strcmp)
- Fires flamethrowers that pass the weapon slot check

---

### CSentinel::Activate

| Property | Value |
|----------|-------|
| Address | 0x004ded30 |
| Status | RENAMED |
| Ghidra Name | CSentinel__Activate |
| Calling Convention | thiscall |
| Returns | void |

**Decompiled:**
```cpp
void CSentinel__Activate(void)
{
    // Get animation system
    int animSys = this[0];

    // Play "activate" animation (one-shot, not looping)
    (**(code**)(*(int*)this[0xc] + 0x24))("activate", 1, 0);

    // Get animation ID for "activate"
    int animId = FUN_004aa630("activate");

    // Trigger animation callback
    (**(code**)(animSys + 0xf0))(animId);
}
```

**Notes:**
- Plays the "activate" animation state
- Animation string at 0x00632260: "activate"
- Sets animation to play once (params: 1, 0)
- Referenced from vtable at offset 0x34

---

### CSentinel::Deactivate

| Property | Value |
|----------|-------|
| Address | 0x004ded60 |
| Status | RENAMED |
| Ghidra Name | CSentinel__Deactivate |
| Calling Convention | thiscall |
| Returns | undefined4 (always 0) |

**Decompiled:**
```cpp
undefined4 CSentinel__Deactivate(void)
{
    // Get current animation state
    int currentState = (**(code**)(this[2] + 0x58))();

    if (currentState != -1) {
        // Get "activate" animation ID
        (**(code**)(*(int*)this[0xc] + 0x24))("activate");
        int activateId = FUN_004aa630("activate");

        // If currently in "activate" state, switch to "inactive"
        if (currentState == activateId) {
            int animSys = this[0];

            // Play "inactive" animation (looping)
            (**(code**)(*(int*)this[0xc] + 0x24))("inactive", 1, 1);
            int inactiveId = FUN_004aa630("inactive");

            // Trigger animation callback
            (**(code**)(animSys + 0xf0))(inactiveId);

            FUN_004fd6a0();  // Notify state change
        }
    }
    return 0;
}
```

**Notes:**
- Transitions from "activate" to "inactive" animation state
- Animation strings: "activate" (0x00632260), "inactive" (0x0063223c)
- "inactive" animation loops (params: 1, 1)

---

### CSentinel::CheckWeaponSlot

| Property | Value |
|----------|-------|
| Address | 0x004dee00 |
| Status | RENAMED |
| Ghidra Name | CSentinel__CheckWeaponSlot |
| Calling Convention | thiscall |
| Parameters | int param_1 (weapon pointer) |
| Returns | undefined4 (1 = can fire, 0 = blocked) |

**Decompiled:**
```cpp
undefined4 CSentinel__CheckWeaponSlot(int weapon)
{
    int slotIndex = -1;

    // Map weapon type (at offset 0xac) to slot index
    switch(*(int*)(weapon + 0xac)) {
        case 2: slotIndex = 9; break;
        case 3: slotIndex = 10; break;
        case 4: slotIndex = 11; break;
        case 5: slotIndex = 12; break;
        case 6: slotIndex = 13; break;
        case 7: slotIndex = 14; break;
        case 8: slotIndex = 15; break;
        case 9: slotIndex = 16; break;
    }

    // Check against weapon list at this+0x19c
    int* pList = *(int**)(this + 0x19c);
    int* item = (pList != NULL) ? (int*)*pList : NULL;

    while (item != NULL) {
        // If weapon matches slot, return 0 (blocked)
        if ((*item != 0) && (*(int*)(*item + 0x270) == slotIndex)) {
            return 0;
        }

        pList = (int*)pList[1];
        item = (pList != NULL) ? (int*)*pList : NULL;
    }

    return 1;  // Can fire
}
```

**Notes:**
- Maps weapon type enum (2-9) to slot indices (9-16)
- Checks if slot is already occupied in weapon list
- Returns 1 if weapon can fire, 0 if blocked

---

## VTables

### CSentinel vtable (primary)

| Address | 0x005e0904 |
|---------|------------|

| Offset | Address | Function |
|--------|---------|----------|
| 0x00 | 0x004dea50 | CSentinel::Constructor (NEEDS CREATION) |
| 0x04 | 0x00405930 | (inherited) |
| 0x08 | 0x00405930 | (inherited) |
| 0x0c | 0x004014c0 | (inherited) |
| 0x10 | 0x00401420 | (inherited) |
| 0x14 | 0x004f43d0 | (inherited) |
| 0x18 | 0x004bfc60 | (inherited) |
| ... | ... | ... |
| 0x34 | 0x004ded30 | CSentinel::Activate |

### CSentinel vtable (secondary)

| Address | 0x005deca0 |
|---------|------------|

| Offset | Address | Function |
|--------|---------|----------|
| 0x00 | 0x004dec00 | CSentinel::scalar_deleting_dtor |
| 0x04 | 0x004bac00 | (inherited) |
| 0x08 | 0x004df1a0 | (unknown) |
| ... | ... | ... |

---

## Related Strings

| Address | String | Usage |
|---------|--------|-------|
| 0x0063221c | "C:\dev\ONSLAUGHT2\Sentinel.cpp" | Debug path |
| 0x0063223c | "inactive" | Deactivated animation state |
| 0x00632248 | "Sentinel Flamethrower" | Weapon name |
| 0x00632260 | "activate" | Activated animation state |

---

## Related Classes

- **CSentinelAI** (0x00632208) - AI controller for sentinel behavior
- **CSentinelBehaviourType** (0x00627c98) - Behavior type descriptor
- **CMCSentinel** (0x0062dfa8) - Motion controller for sentinel

---

## Summary

| Function | Address | Status |
|----------|---------|--------|
| CSentinel::Constructor | 0x004dea50 | **NEEDS MANUAL CREATION** |
| CSentinel::scalar_deleting_dtor | 0x004dec00 | RENAMED |
| CSentinel::Destructor | 0x004dec20 | RENAMED |
| CSentinel::UpdateFlamethrowers | 0x004decc0 | RENAMED |
| CSentinel::Activate | 0x004ded30 | RENAMED |
| CSentinel::Deactivate | 0x004ded60 | RENAMED |
| CSentinel::CheckWeaponSlot | 0x004dee00 | RENAMED |

**Total: 7 functions (6 renamed, 1 needs manual creation)**
