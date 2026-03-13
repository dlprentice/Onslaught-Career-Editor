# WaypointManager.cpp Functions

**Source file**: `C:\dev\ONSLAUGHT2\WaypointManager.cpp`
**Debug string address**: `0x0063d1f8`

## Overview

The WaypointManager handles loading and managing waypoints for AI navigation in the game world. Waypoints are loaded during world initialization and are used by entities for pathfinding.

## Functions Found (3)

| Address | Name | Called By | Description |
|---------|------|-----------|-------------|
| `0x00505960` | `CWaypointManager__LoadWaypoint` | `CWaypointManager__LoadWaypoints` | Loads a single waypoint from save data |
| `0x00505ae0` | `CWaypointManager__LoadWaypoints` | `CWorld__LoadWorld` | Main entry point - loads all waypoints |
| `0x005d5860` | `CWaypointManager__LoadWaypoints_unwind` | Exception handler | SEH unwind handler for cleanup |

## Function Details

### CWaypointManager__LoadWaypoint (0x00505960)

**Signature**: `void CWaypointManager__LoadWaypoint(char param_1, int param_2, int param_3)`

**Purpose**: Loads a single waypoint entry from serialized data.

**Analysis**:
- Uses `this` pointer in ECX (thiscall convention)
- Allocates memory for waypoint name string (size = param_1 + 1, allocation tag 0x25)
- Reads waypoint name character by character using `DXMemBuffer__ReadBytes` (stream read helper at `0x00548570`)
- Null-terminates the name string
- If param_2 < 0x21 (33): Iterates through a global linked list (`DAT_00855120`) to find and process entity by index
- If param_2 >= 0x21: Iterates through an entity array, checking flags at offset 0x34 for bit 0x1000
- Calls `CSPtrSet__AddToHead` to process/register matching entities with waypoints

**Key Data**:
- `DAT_00855120` / `DAT_00855128`: Global waypoint/entity linked list
- Format string at `0x0063d1f0`: `"%d %d"` (used for debug output)

**Decompiled Code**:
```c
void CWaypointManager__LoadWaypoint(char param_1, int param_2, int param_3)
{
  undefined4 uVar1;
  int iVar2;
  int in_ECX;  // this pointer
  int iVar3;
  int local_4;

  local_4 = in_ECX;
  DXMemBuffer__ReadBytes(&param_1, 1);  // Read 1 byte (name length)
  uVar1 = OID__AllocObject(param_1 + 1, 0x25, "C:\\dev\\ONSLAUGHT2\\WaypointManager.cpp", 0x1a);
  *(undefined4 *)(in_ECX + 4) = uVar1;  // Store name pointer at this+4

  // Read name string character by character
  iVar3 = 0;
  if ('\0' < param_1) {
    do {
      DXMemBuffer__ReadBytes(*(int *)(in_ECX + 4) + iVar3, 1);
      iVar3 = iVar3 + 1;
    } while (iVar3 < param_1);
  }
  *(undefined1 *)(*(int *)(in_ECX + 4) + iVar3) = 0;  // Null terminate

  if (param_2 < 0x21) {
    // Small index: iterate linked list
    DXMemBuffer__ReadBytes(&param_2, 2);
    iVar3 = 0;
    DAT_00855128 = DAT_00855120;
    // ... iterate and call CSPtrSet__AddToHead on matching entity
  }
  else {
    // Large index: iterate array
    DXMemBuffer__ReadBytes(&local_4, 4);
    // ... iterate array and call CSPtrSet__AddToHead on entities with flag 0x1000
  }
}
```

---

### CWaypointManager__LoadWaypoints (0x00505ae0)

**Signature**: `void CWaypointManager__LoadWaypoints(undefined4 param_1, undefined4 param_2, undefined4 param_3)`

**Purpose**: Main entry point for loading all waypoints. Called during world load.

**Analysis**:
- Sets up SEH (Structured Exception Handling) with unwind handler at `0x005d5876`
- Reads waypoint count (2-byte short) from stream
- Loops for each waypoint:
  - Allocates 0x18 (24) bytes for a waypoint object (allocation tag 0x25)
  - Initializes vtable pointer to `PTR_FUN_005dfc8c`
  - Calls `CSPtrSet__Init` (`0x004e5840`) (simple 3-dword zero-init helper used by multiple small structs)
  - Calls `CWaypointManager__LoadWaypoint` to load waypoint data
  - Calls `CSPtrSet__AddToTail` (`0x004e5b20`) to register/link the waypoint
- After loop, calls `CConsole__StatusDone` with "Loading waypoints" status message

**Key Data**:
- Status string at `0x0063d23c`: `"Loading waypoints"`
- Waypoint vtable at `0x005dfc8c`
- Waypoint object size: 0x18 (24) bytes

**Decompiled Code**:
```c
void CWaypointManager__LoadWaypoints(undefined4 param_1, undefined4 param_2, undefined4 param_3)
{
  undefined4 *puVar1;
  int local_10;
  void *local_c;
  undefined1 *puStack_8;
  undefined4 local_4;

  // SEH setup
  local_4 = 0xffffffff;
  puStack_8 = &LAB_005d5876;
  local_c = ExceptionList;
  ExceptionList = &local_c;

  DXMemBuffer__ReadBytes(&local_10, 2);  // Read waypoint count (short)

  while ((short)local_10 != 0) {
    // Allocate waypoint object (24 bytes)
    puVar1 = (undefined4 *)OID__AllocObject(0x18, 0x25,
               "C:\\dev\\ONSLAUGHT2\\WaypointManager.cpp", 0x72);
    local_4 = 0;

    if (puVar1 != NULL) {
      CSPtrSet__Init(puVar1);  // Simple zero-init helper (3 dwords)
      *puVar1 = &PTR_FUN_005dfc8c;  // Set vtable
      puVar1[1] = 0;
    }

    local_4 = 0xffffffff;
    CWaypointManager__LoadWaypoint(param_1, param_2, param_3);
    CSPtrSet__AddToTail(puVar1);  // Register waypoint (set pointer is in ECX)
    local_10 = local_10 + -1;
  }

  CConsole__StatusDone("Loading waypoints", 1);  // Status update
  ExceptionList = local_c;  // Restore SEH
}
```

---

### CWaypointManager__LoadWaypoints_unwind (0x005d5860)

**Signature**: `void CWaypointManager__LoadWaypoints_unwind(void)`

**Purpose**: SEH (Structured Exception Handling) unwind handler for cleanup during waypoint loading.

**Analysis**:
- Called automatically by Windows SEH when an exception occurs during `LoadWaypoints`
- Calls `OID__FreeObject_Callback` (wrapper around `OID__FreeObject`) to free the partially-constructed waypoint on exception
- Uses EBP+0xC to access the allocated waypoint object pointer
- Allocation tag 0x25 and line number 0x72 (114) match the allocation in `LoadWaypoints`

**Decompiled Code**:
```c
void CWaypointManager__LoadWaypoints_unwind(void)
{
  int unaff_EBP;

  // Clean up allocated waypoint on exception
  OID__FreeObject_Callback(*(undefined4 *)(unaff_EBP + 0xc));
}
```

## Related Functions

| Address | Name | Relationship |
|---------|------|--------------|
| `0x0050b9c0` | `CWorld__LoadWorld` | Caller of `LoadWaypoints` |
| `0x00548570` | `DXMemBuffer__ReadBytes` | Stream read function |
| `0x005490e0` | `OID__AllocObject` | Memory allocation with debug info |
| `0x00449d40` | `OID__FreeObject_Callback` | Memory deallocation callback wrapper |
| `0x004e5840` | `CSPtrSet__Init` | Simple 3-dword zero-init helper |
| `0x004e5a80` | `CSPtrSet__AddToHead` | Entity-waypoint linking |
| `0x004e5b20` | `CSPtrSet__AddToTail` | Waypoint registration (set insert) |
| `0x0042b800` | `CConsole__StatusDone` | Status message display |

## Global Data

| Address | Type | Description |
|---------|------|-------------|
| `0x00855120` | `int*` | Head of waypoint/entity linked list |
| `0x00855128` | `int*` | Current iterator for linked list |
| `0x005dfc8c` | `void**` | CWaypoint vtable pointer |

## Memory Allocation Tags

- **Tag 0x25 (37)**: Used for WaypointManager allocations
- **Line 0x1a (26)**: Waypoint name allocation in `LoadWaypoint`
- **Line 0x72 (114)**: Waypoint object allocation in `LoadWaypoints`

## Notes

1. **Waypoint object size**: 24 bytes (0x18), with vtable at offset 0 and next pointer at offset 4
2. **Entity flag 0x1000**: Entities with this flag at offset 0x34 are waypoint-compatible
3. **Index threshold 33 (0x21)**: Separates linked-list vs array-based entity lookup
4. The "Loading waypoints" message appears in the game's loading screen

## Additional Recovered Helpers (Headless 2026-02-26)

| Address | Name | Notes |
|---------|------|-------|
| 0x004e66d0 | CWaypoint__Process_NoOp | No-op process wrapper that tail-calls `CFrontEndPage__Process_NoOp`. |
| 0x004f7cd0 | StringScratch__CopyRotating4K | Copies input string into rotating 4-slot (0x1000-byte each) global scratch buffer and returns active slot pointer. |
| 0x004ffe00 | CWaypoint__RandomizeOffsetVectors | Initializes randomized signed waypoint offset vectors and mirrored pairs (`+0x48..+0x5c`). |
| 0x00501360 | CWaypoint__CleanupEndLevelVBufTextures | End-of-level cleanup/report pass for waypoint VBufTexture resources; frees inactive entries and emits debug trace lines. |
| 0x00505ab0 | CWaypointManager__ReleasePendingObjects | Drains global pending object set and releases each object via virtual destructor dispatch. |

---
*Generated: December 2025*
*Analysis tool: Ghidra + GhydraMCP*
