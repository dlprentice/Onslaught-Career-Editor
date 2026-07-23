# ScriptEventNB.cpp - Function Mappings

> Source file: `MissionScript/ScriptEventNB.cpp`
> Debug path: `[maintainer-local-source-export-root]\MissionScript\ScriptEventNB.cpp` (0x0064fe98)
> Last updated: 2026-05-19

## Overview

Non-blocking script event system for mission scripting. "NB" stands for "Non-Blocking" - these are script events that execute without pausing the game loop, allowing waypoint following, message handling, and event posting to continue in parallel.

**Key Classes:**
- `CScriptEventNB` - Non-blocking script event manager
- Related to `CEventFunction` (event callbacks) and `CRelaxedSquad` (base class)

**Inheritance:**
- `CScriptEventNB` inherits from a base class with vtable at 0x005e4f34
- Uses `CSPtrSet` for managing event listener lists

---

## Functions (13 total)

| Address | Name | Status | Notes |
|---------|------|--------|-------|
| 0x00538760 | CScriptEventNB__Init | WAVE586 | `void __fastcall ... (void * event_nb)`; sets vtable, zeroes fields |
| 0x005386d0 | CScriptEventNB__Destructor | WAVE586 | `void __fastcall ... (void * event_nb)`; cleans up listener set and monitor base |
| 0x005386b0 | CScriptEventNB__ScalarDeletingDestructor | WAVE586 | `void * __thiscall ... (void * this, byte delete_flags)` |
| 0x00538780 | CScriptEventNB__ScalarDeletingDestructor2 | WAVE586 | `void * __thiscall ... (void * this, byte delete_flags)` |
| 0x00538950 | CScriptEventNB__BaseDestructor | WAVE586 | `void __fastcall ... (void * event_nb)`; restores vtable and shuts down monitor base |
| 0x00538860 | CScriptEventNB__CreateEventListener | WAVE586 | `void __fastcall ... (void * event_nb)`; allocates the listener set |
| 0x00538960 | CScriptEventNB__RegisterEventListener | WAVE586 | `void * __thiscall ... (void * this, void * event_name_ref, void * event_function)` |
| 0x005387b0 | CScriptEventNB__ClearEventListeners | WAVE586 | `void __fastcall ... (void * listener_entry)`; clears one listener entry |
| 0x005388d0 | CScriptEventNB__DestroyAllEvents | WAVE586 | `void __fastcall ... (void * event_nb)`; destroys all listener entries |
| 0x00538470 | CScriptEventNB__UpdateWaypointFollowing | WAVE586 | `void __fastcall ... (void * event_nb)`; waypoint following logic with distance checks |
| 0x005385e0 | CScriptEventNB__HandleMessage | WAVE586 | `void __thiscall ... (void * this, void * message)`; message IDs 2000, 0x7d1, 0x7d2 |
| 0x00538b70 | CScriptEventNB__PostEvent | WAVE586 | `void __thiscall ... (void * this, char * event_name)`; posts event to matching listeners |
| 0x00538c70 | CScriptEventNB__HandleEventMessage | WAVE586 | `void __thiscall ... (void * this, void * message)`; handles event-manager payload message 2000 |

Note: `0x00538ea0` and `0x00538ec0` were previously attributed to this file, but they are now mapped to `CScriptObjectCode` destructor/constructor rows (see `ScriptObjectCode.cpp.md`).

2026-06-08 event/object-code lifecycle schema proof: `missionscript-event-object-code-lifecycle-proof.md` and `missionscript-event-object-code-lifecycle.v1.json` now preserve the static event-manager bridge for this owner file. The schema ties `CScriptEventNB__RegisterEventListener`, `CScriptEventNB__PostEvent`, and `CScriptEventNB__HandleEventMessage` to `IScript__ScheduleEvent`, message id `2000`, `DAT_00855190`, `DAT_0089c590`, `CEventFunction__Execute`, `CScriptObjectCode__CallEvent`, `CScriptObjectCode__CallEventDirect`, and `795` loose event-name counts as corpus context. This is static listener/posting lifecycle accounting only, not runtime event outcomes, exact listener/payload layout, live loose-MSL loading, patch, Godot, rebuild, or no-noticeable-difference proof.

## Wave586 Static Read-Back

Wave586 hardened the CScriptEventNB listener/event-manager tranche at `0x00538470` through `0x00538c70`. The saved signatures classify ECX-only helpers as `__fastcall`, one-stack-argument methods as `__thiscall`, deleting destructor wrappers with a `byte delete_flags` parameter, and the named event post method with a `char * event_name` argument.

Read-back evidence: `ApplyScriptEventNBWave586.java` dry/apply/final dry reported `updated=0 skipped=13 renamed=0 would_rename=0 missing=0 bad=0`, then `updated=13 skipped=0 renamed=0 would_rename=0 missing=0 bad=0`, then `updated=0 skipped=13 renamed=0 would_rename=0 missing=0 bad=0`, with `REPORT: Save succeeded`. Post exports verified `13` metadata rows, `13` tag rows, `18` xref rows, `5577` instruction rows, `13` decompile rows, and `72` vtable rows. The queue refresh after Wave586 reports `6093` functions, `2978` commented, `3115` commentless, `1387` exact-undefined signatures, `1116` `param_N` signatures, and next queue head `0x00538ea0 CScriptObjectCode__scalar_deleting_dtor`.

The bounded evidence is static retail Ghidra state only. Runtime mission-script behavior remains unproven, script corpus coverage remains separate evidence, exact `CScriptEventNB`/listener/message/payload/waypoint layouts remain open, and 0x00538ea0 and 0x00538ec0 remain CScriptObjectCode rows rather than ScriptEventNB rows.

---

## Function Details

### CScriptEventNB__Init (0x00538760)

**Constructor** - Initializes the CScriptEventNB object.

```cpp
// Decompiled (cleaned up)
void CScriptEventNB::Init() {
    this->field_0x04 = 0;       // in_ECX[1]
    this->field_0x08 = 0;       // in_ECX[2]
    this->vtable = &CScriptEventNB_vtable;  // 0x005e4f44
}
```

**Key Details:**
- Very simple initialization - sets vtable and zeroes two fields
- Vtable pointer: 0x005e4f44

---

### CScriptEventNB__Destructor (0x005386d0)

**Destructor** - Cleans up the event listener and calls base destructor.

```cpp
// Decompiled (cleaned up)
void CScriptEventNB::~CScriptEventNB() {
    this->vtable = &PTR_LAB_005e4f34;  // Reset to base vtable

    if (this->field_0x08 != NULL) {
        // Call destructor on child object
        (*(code*)**(undefined4**)this->field_0x08)(1);
        this->field_0x08 = 0;
    }

    CSPtrSet__Remove(this);  // Additional cleanup
    CMonitor__Shutdown();      // Base monitor cleanup (formerly FUN_004bac40)
}
```

**Key Details:**
- Resets vtable to base class before cleanup
- Cleans up field_0x08 if allocated
- Calls base monitor shutdown helper CMonitor__Shutdown (formerly FUN_004bac40)

---

### CScriptEventNB__CreateEventListener (0x00538860)

**Creates Event Listener** - Allocates a new CRelaxedSquad event listener.

```cpp
// Decompiled (cleaned up)
void CScriptEventNB::CreateEventListener() {
    // Allocate object (size 0x10, type 0x76)
    int* obj = OID__AllocObject(0x10, 0x76,
        "[maintainer-local-source-export-root]\\MissionScript\\ScriptEventNB.cpp", 0x42);

    if (obj != NULL) {
        CRelaxedSquad::Init();
        this->field_0x08 = obj;
    } else {
        this->field_0x08 = NULL;
    }
}
```

**Key Details:**
- Allocates 0x10 (16) bytes for a CRelaxedSquad object
- Object type: 0x76
- Line number: 0x42 (66) in source file
- Stores result at this+0x08

---

### CScriptEventNB__RegisterEventListener (0x00538960)

**Registers Event Listener** - Complex function that registers a listener by matching event names.

```cpp
// Decompiled (cleaned up - partial)
int* CScriptEventNB::RegisterEventListener(undefined4* param_1, int param_2) {
    int* local_14 = NULL;

    // Get first event from list
    undefined4* puVar2 = (undefined4*)**(int**)(this + 8);
    (*(int**)(this + 8))[2] = (int)puVar2;

    int* piVar8 = (puVar2 != NULL) ? (int*)*puVar2 : NULL;

    // Iterate through events looking for name match
    while (piVar8 != NULL) {
        // Get name via vtable call at offset 0x38
        byte* eventName = (**(code**)(*(int*)*piVar8 + 0x38))();
        byte* targetName = (**(code**)(*param_1[0] + 0x38))();

        if (strcmp(eventName, targetName) == 0) {
            local_14 = piVar8;  // Found match
        }

        // Move to next
        puVar2 = *(undefined4**)(*(int*)(*(int*)(this + 8) + 8) + 4);
        // ... continue iteration
    }

    if (local_14 != NULL) {
        // Found existing listener - add to its list
        int* wrapper = OID__AllocObject(4, 0x76,
            "[maintainer-local-source-export-root]\\MissionScript\\ScriptEventNB.cpp", 0x19);
        if (wrapper != NULL) {
            *wrapper = param_2;
            if (param_2 != 0) {
                // Lazily allocate the monitor deletion list at param_2+0x04 (monitor.h)
                if (*(int*)(param_2 + 4) == 0) {
                    int obj = OID__AllocObject(0x10, 0x5e,
                        "[maintainer-local-source-export-root]\\MissionScript\\ScriptFunctionManager.cpp", 0x18);
                    if (obj != 0) {
                        CSPtrSet__Init(obj);
                    }
                    *(int*)(param_2 + 4) = obj;
                }
                CSPtrSet__AddToHead(*(void**)(param_2 + 4), wrapper);
            }
        }
    } else {
        // No existing listener - create new one
        local_14 = OID__AllocObject(0x18, 0x76,
            "[maintainer-local-source-export-root]\\MissionScript\\ScriptEventNB.cpp", 0x68);
        if (local_14 != NULL) {
            CSPtrSet__Init(local_14 + 1);
            // Clone the event name
            int nameClone = (**(code**)(*param_1[0] + 0x48))();
            *local_14 = nameClone;
            // Create wrapper and add
            int* wrapper = OID__AllocObject(4, 0x76,
                "[maintainer-local-source-export-root]\\MissionScript\\ScriptEventNB.cpp", 0x11);
            if (wrapper != NULL) {
                *wrapper = param_2;
                if (param_2 != 0) {
                    CMonitor__AddDeletionEvent(param_2, wrapper);
                }
            }
            CSPtrSet__AddToTail(local_14 + 1, wrapper);
            *(undefined1*)(local_14 + 5) = 0;
        }
    }

    CSPtrSet::AddToTail(local_14);
    return local_14;
}
```

**Key Details:**
- Creates listeners with size 0x18 (24) bytes, type 0x76
- Creates wrappers with size 4 bytes
- Line numbers: 0x19 (25), 0x68 (104), 0x11 (17) in source file
- Uses string comparison via vtable call at offset 0x38 (GetName)
- Clone function at vtable offset 0x48

---

### CScriptEventNB__UpdateWaypointFollowing (0x00538470)

**Waypoint Following Update** - Updates the entity following a waypoint path.

```cpp
// Decompiled (cleaned up)
void CScriptEventNB::UpdateWaypointFollowing() {
    int* entity = *(int**)(this + 8);
    float waypointX = *(float*)(*(int*)(this + 0x14) + 0x1c);
    float waypointY = *(float*)(*(int*)(this + 0x14) + 0x20);

    float entityX = (float)entity[7];
    float entityY = (float)entity[8];

    // Calculate distance to waypoint
    float dx = waypointX - entityX;
    float dy = waypointY - entityY;
    float distance = sqrt(dx*dx + dy*dy);

    // Determine arrival threshold based on entity flags
    float threshold = 2.0f;  // Default
    if ((entity[0xd] & 0x10) != 0) {
        // Call vtable function to get custom threshold
        threshold = (**(code**)(*entity + 0x178))();
    } else if ((entity[0xd] & 0x20000000) != 0) {
        threshold = 4.0f;  // Larger threshold for certain units
    }

    if (distance < threshold) {
        // Arrived at waypoint - get next
        int nextWaypoint = *(int*)(*(int*)(this + 0x14) + 0x3c);

        if (nextWaypoint == *(int*)(this + 0x14)) {
            // ERROR: Waypoint points to itself (infinite loop)
            CConsole__Printf(&DAT_0066f580,
                "ERROR: Waypoint points to previous");
            *(undefined4*)(this + 0x14) = 0;
        } else {
            *(int*)(this + 0x14) = nextWaypoint;
        }

        int currentWaypoint = *(int*)(this + 0x14);
        if (currentWaypoint == 0) {
            // Reached end of path
            *(undefined4*)(this + 0x18) = 0;
            (**(code**)(**(int**)(this + 8) + 0x100))();  // Notify entity

            if (*(int*)(this + 0x1c) == 0) {
                IScript::CreateThingRef(*(undefined4*)(this + 0x24));
            } else {
                // Cleanup and trigger next action
                *(undefined4*)(this + 0x1c) = 0;
                FUN_00539910(*(undefined4*)(this + 0x20));
                CSPtrSet__Remove(*(undefined4*)(this + 0x20));
                // ... state transitions
            }
        } else {
            // Move to next waypoint
            (**(code**)(**(int**)(this + 8) + 0xf4))(
                *(undefined4*)(currentWaypoint + 0x1c),  // FVector lane 0
                *(undefined4*)(currentWaypoint + 0x20),  // FVector lane 1
                *(undefined4*)(currentWaypoint + 0x24),  // FVector lane 2
                *(undefined4*)(currentWaypoint + 0x28),  // FVector lane 3
                0);
        }
    }

    // Schedule event ID 2000 (0x7d0) for the next frame.
    float nextFrame = -1.0f;
    FUN_0044b370(2000, this, &nextFrame, 0, 0, 0);
}
```

**Key Details:**
- Calculates 2D distance to current waypoint
- Arrival thresholds: 2.0f (default), 4.0f (large units), or custom via vtable
- Schedules event ID `2000` for `NEXT_FRAME` (`-1.0f`), so this is a
  next-frame waypoint check rather than a 2000 ms timer
- Detects infinite waypoint loops
- Error message at 0x0064fe50: "ERROR: Waypoint points to previous"

---

### CScriptEventNB__HandleMessage (0x005385e0)

**Message Handler** - Handles three message types.

```cpp
// Decompiled (cleaned up)
void CScriptEventNB::HandleMessage(int param_1) {
    short msgId = *(short*)(param_1 + 4);

    if (msgId == 2000) {
        // Event 2000 - update waypoint following
        UpdateWaypointFollowing();
    }
    else if (msgId == 0x7d1) {  // 2001
        // Object destroyed message
        int* obj = *(int**)(param_1 + 0xc);
        if (obj != NULL) {
            FUN_00539910(obj);
            CSPtrSet__Remove(obj);
            if (obj != NULL) {
                (**(code**)(*obj + 4))(1);  // Call destructor
            }
            // Trigger state transition
            if (DAT_008a9ac0 == 4) {
                FUN_00539980();
            } else {
                FUN_00539ae0(DAT_0089c7f4);
            }
        }
    }
    else if (msgId == 0x7d2 && DAT_0089c7f0 == 0) {  // 2002
        // Unknown message type
        if (DAT_008a9ac0 == 4) {
            FUN_00539980();
        } else {
            FUN_00539990(*(undefined4*)(this + 0xc), 2, &DAT_0089c528, 0);
        }
    }
}
```

**Key Details:**
- Message ID 2000: next-frame waypoint update event
- Message ID 0x7d1 (2001): Object destroyed notification
- Message ID 0x7d2 (2002): Unknown purpose, state-dependent
- Global state variable DAT_008a9ac0 controls behavior

---

### CScriptEventNB__PostEvent (0x00538b70)

**Posts Event** - Posts a named event to all registered listeners.

```cpp
// Decompiled (cleaned up)
void CScriptEventNB::PostEvent(byte* eventName) {
    // Check if game is playing (warning if not)
    if (*(int*)(*(int*)(this + 8) + 0xc) == 0) {
        if (strcmp("game playing", eventName) != 0) {
            CConsole__Printf(&DAT_0066f580,
                "Warning: No listeners for posted event '%s'", eventName);
        }
    }

    // Get first listener from list
    undefined4* listNode = (undefined4*)**(int**)(this + 8);
    undefined4* listener = (listNode != NULL) ? (undefined4*)*listNode : NULL;

    while (listener != NULL) {
        // Get listener's event name via vtable call
        byte* listenerName = (**(code**)(*(int*)*listener + 0x38))();

        if (strcmp(listenerName, eventName) == 0) {
            // Found matching listener - mark as triggered
            *(undefined1*)(listener + 5) = 1;

            // Execute all event functions for this listener
            undefined4* funcNode = (undefined4*)listener[1];
            int* func = (funcNode != NULL) ? (int*)*funcNode : NULL;

            while (func != NULL) {
                if (*func != 0) {
                    CEventFunction::Execute();
                }
                funcNode = (undefined4*)funcNode[1];
                func = (funcNode != NULL) ? (int*)*funcNode : NULL;
            }
        }

        // Move to next listener
        listNode = (undefined4*)listNode[1];
        listener = (listNode != NULL) ? (undefined4*)*listNode : NULL;
    }
}
```

**Key Details:**
- Warns if posting event when not "game playing"
- Uses string comparison to find matching listeners
- Sets triggered flag at listener+0x14 (offset 5 in int* terms)
- Iterates through all CEventFunction objects and executes them
- Warning message at 0x0064fecc: "Warning: No listeners for posted event '%s'"
- Special event name: "game playing" (at 0x0062c258)

---

### Moved Mapping: CScriptObjectCode Constructor (0x00538ec0)

Older notes attributed `0x00538ec0` to a `CScriptEventNB__LoadFromBuffer` row. Current Ghidra state maps this function to `CScriptObjectCode__CScriptObjectCode`, with `0x00538ea0` as the adjacent `CScriptObjectCode__scalar_deleting_dtor`. Keep the bytecode/symbol-table/load-from-buffer details in `ScriptObjectCode.cpp.md`, not in this file.

---

## Related Data

### Vtables

| Address | Name | Notes |
|---------|------|-------|
| 0x005e4f34 | CScriptEventNB base-vtable prefix | Prefix includes no-op/delete wrapper/monitor slots plus `HandleEventMessage`, `ScalarDeletingDestructor2`, and `DestroyAllEvents` |
| 0x005e4f44 | CScriptEventNB main-vtable prefix | Set by `CScriptEventNB__Init`; slots 0-2 are `HandleEventMessage`, `ScalarDeletingDestructor2`, and `DestroyAllEvents` |
| 0x005e4f54 | Adjacent CScriptObjectCode vtable/data region | Not a proven CScriptEventNB derived vtable; current function ownership moves to `ScriptObjectCode.cpp.md` |

Wave586 vtable exports deliberately treat only the listed CScriptEventNB prefix slots as evidence. Later raw pointer rows enter adjacent data/vtable regions and must not be counted as CScriptEventNB slots without a separate boundary pass.

### Vtable at 0x005e4f34 (Base)

| Offset | Address | Function |
|--------|---------|----------|
| 0x00 | 0x004014c0 | (scalar deleting destructor wrapper) |
| 0x04 | 0x005386b0 | ScalarDeletingDestructor |
| 0x08 | 0x004bac40 | Base class function |
| 0x0c | 0x006196a8 | (unknown) |
| 0x10 | 0x00538c70 | HandleEventMessage |
| 0x14 | 0x00538780 | ScalarDeletingDestructor2 |
| 0x18 | 0x005388d0 | DestroyAllEvents |
| ... | ... | ... |

### Vtable at 0x005e4f44 (Main)

| Offset | Address | Function |
|--------|---------|----------|
| 0x00 | 0x00538c70 | HandleEventMessage |
| 0x04 | 0x00538780 | ScalarDeletingDestructor2 |
| 0x08 | 0x005388d0 | DestroyAllEvents |
| ... | ... | ... |

---

## Class Layout (Partial)

### CScriptEventNB

| Offset | Type | Name | Notes |
|--------|------|------|-------|
| 0x00 | void* | vtable | Virtual function table |
| 0x04 | int | field_0x04 | Unknown, zeroed in Init |
| 0x08 | void* | eventListener | CRelaxedSquad event listener |
| 0x0c | void* | field_0x0c | List pointer |
| 0x14 | void* | currentWaypoint | Current waypoint in path |
| 0x18 | int | field_0x18 | Waypoint state flag |
| 0x1c | int | field_0x1c | State flag |
| 0x20 | void* | field_0x20 | Associated object |
| 0x24 | void* | thingRef | IScript thing reference |
| ... | ... | ... | ... |

Offsets formerly listed from `0x58` through `0x6c` came from the now-moved `CScriptObjectCode__CScriptObjectCode` row and are not retained here as CScriptEventNB layout evidence.

---

## Message IDs

| ID | Hex | Purpose |
|----|-----|---------|
| 2000 | 0x7d0 | Next-frame waypoint update event |
| 2001 | 0x7d1 | Object destroyed notification |
| 2002 | 0x7d2 | Unknown state-dependent action |

---

## Error Messages

| Address | Message | Context |
|---------|---------|---------|
| 0x0064fe50 | "ERROR: Waypoint points to previous" | Waypoint infinite loop detected |
| 0x0064fecc | "Warning: No listeners for posted event '%s'" | Event posted with no listeners |

---

## Strings

| Address | String | Usage |
|---------|--------|-------|
| 0x0062c258 | "game playing" | Special event name - no warning |
| 0x0064fe98 | "[maintainer-local-source-export-root]\\MissionScript\\ScriptEventNB.cpp" | Debug path |
| 0x0064fe80 | ".?AVCScriptEventNB@@" | RTTI class name |

---

## Cross-References

### Called By
| Address | Function | Notes |
|---------|----------|-------|
| Various | Script system | Part of mission scripting |

### Calls
| Address | Function | Notes |
|---------|----------|-------|
| 0x00549220 | OID__FreeObject | Memory deallocation |
| 0x004e5bd0 | CSPtrSet__Remove | Remove entry from list (returns node to pool) |
| 0x004e5c60 | CSPtrSet__Clear | List cleanup |
| 0x004bac40 | CMonitor__Shutdown | Base monitor cleanup helper (formerly `FUN_004bac40`) |
| 0x0044b370 | FUN_0044b370 | Event scheduling; this call uses `NEXT_FRAME` |
| 0x00441740 | CConsole__Printf (`FUN_00441740`) | Debug/error output |

---

## Notes

1. **Non-Blocking Design**: The "NB" suffix indicates these script events don't
   block the game loop. Waypoint following and event posting happen
   asynchronously; the waypoint update reschedules event ID `2000` for the next
   frame.

2. **Event System**: The system uses a publisher-subscriber pattern where events are posted by name and listeners execute their CEventFunction callbacks when their name matches.

3. **Waypoint System**: Entities can follow waypoint paths with arrival detection based on distance thresholds. Different unit types have different thresholds (2.0f default, 4.0f for large units).

4. **Memory Management**: Uses OID__AllocObject with type 0x76 for most allocations. Objects are typically 0x10 (16), 0x18 (24), or 0x20 (32) bytes.

5. **RTTI**: The ".?AVCScriptEventNB@@" string at 0x0064fe80 is MSVC RTTI type information for the class.

6. **Related Files**: Works closely with ScriptFunctionManager.cpp (0x00650040) and EventFunction.cpp for the complete scripting system.
