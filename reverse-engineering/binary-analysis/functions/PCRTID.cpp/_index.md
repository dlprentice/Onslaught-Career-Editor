# PCRTID.cpp - PC Runtime ID System

**Source File:** `C:\dev\ONSLAUGHT2\PCRTID.cpp`
**Debug String Address:** `0x0063e284`

## Overview

PCRTID.cpp implements the PC Runtime ID factory system - a central factory pattern that creates different types of runtime objects used for rendering game entities. The "CRT" prefix stands for "C Runtime" objects, which are platform-specific rendering wrappers.

## Functions Found

| Address | Name | Size | Purpose |
|---------|------|------|---------|
| `0x00516580` | `PCRTID__CreateObject` | ~0x90 | Factory function - creates CRT objects by type ID |

## Type ID Mapping

The factory function uses a switch statement on a type ID parameter to create different object types:

| Type ID | Class | Size (bytes) | Vtable | Notes |
|---------|-------|--------------|--------|-------|
| 1 | `CRTMesh` | 0x50 (80) | `0x005deb1c` | Base mesh rendering object |
| 2 | `CRTTree` | 0x34 (52) | `0x005deb9c` | Tree rendering (smaller, specialized) |
| 4 | `CRTBuilding` | 0x5c (92) | `0x005de9c0` | Building rendering (inherits CRTMesh) |
| 5 | `CRTCutscene` | 0x28 (40) | N/A | Cutscene rendering object |

**Note:** Type ID 3 is not implemented in this factory.

## Class Hierarchy

```
CRTMesh (base class, 0x50 bytes)
  |
  +-- CRTBuilding (derived, 0x5c bytes)
```

`CRTTree` and `CRTCutscene` appear to be independent classes (not derived from CRTMesh).

## Related Functions (by vtable)

### CRTMesh (Type ID 1)
| Address | Name | Purpose |
|---------|------|---------|
| `0x004dc370` | `CRTMesh__Init` | Initialize mesh |
| `0x004dc950` | `CRTMesh__Destructor` | Destructor |
| `0x004dcb00` | `CRTMesh__FreePoseData` | Free pose data |
| `0x004dcb70` | `CRTMesh__ScalarDeletingDestructor` | Scalar deleting destructor |
| `0x004dd0c0` | `CRTMesh__CleanupAllEffects` | Cleanup effects |
| `0x004dd6b0` | `CRTMesh__SetQualityLevel` | Set quality level |
| `0x004dd770` | `CRTMesh__GetQualityLevel` | Get quality level |

### CRTTree (Type ID 2)
| Address | Name | Purpose |
|---------|------|---------|
| `0x004ddfd0` | `CRTTree__Destructor` | Destructor |

### CRTBuilding (Type ID 4)
| Address | Name | Purpose |
|---------|------|---------|
| `0x004db850` | `CRTBuilding__Destructor` | Destructor (calls CRTMesh__Destructor) |

### CRTCutscene (Type ID 5)
| Address | Name | Purpose |
|---------|------|---------|
| `0x004dbb60` | `CRTCutscene__CRTCutscene` | Constructor |
| `0x004dbc30` | `CRTCutscene__Destructor` | Destructor |
| `0x004dbc50` | `CRTCutscene__DestructorImpl` | Destructor implementation |
| `0x004dbd80` | `CRTCutscene__Init` | Initialize cutscene |
| `0x004dbe90` | `CRTCutscene__Reset` | Reset cutscene |
| `0x004dbf70` | `CRTCutscene__SetCurrentIndex` | Set current index |

## RTTI Type Names

Found at these addresses (MSVC mangled names):
- `0x00631db8`: `.?AVCRTMesh@@`
- `0x00631dd0`: `.?AVCRTBuilding@@`
- `0x00631e18`: `.?AVCRTCutscene@@`
- `0x006321b0`: `.?AVCRTTree@@`

## Factory Function Details

### PCRTID__CreateObject (0x00516580)

```c
void* PCRTID__CreateObject(int typeId)
{
    switch(typeId) {
    case 1:  // CRTMesh
        obj = MemAlloc(0x50, 0x3b, "PCRTID.cpp", 0x11);
        if (obj) {
            obj->next = NULL;
            obj->vtable = &CRTMesh_vtable;
        }
        return obj;

    case 2:  // CRTTree
        obj = MemAlloc(0x34, 0x3b, "PCRTID.cpp", 0x12);
        if (obj) {
            obj->next = NULL;
            obj->vtable = &CRTTree_vtable;
        }
        return obj;

    case 4:  // CRTBuilding
        obj = MemAlloc(0x5c, 0x3b, "PCRTID.cpp", 0x14);
        if (obj) {
            obj->next = NULL;
            obj->vtable = &CRTBuilding_vtable;
        }
        return obj;

    case 5:  // CRTCutscene
        obj = MemAlloc(0x28, 0x3b, "PCRTID.cpp", 0x15);
        if (obj) {
            return CRTCutscene__CRTCutscene();
        }
        return NULL;
    }
    return NULL;
}
```

**Memory Allocation Tags:**
- Pool ID: `0x3b` (59) - Likely a specific memory pool for runtime objects
- Line numbers in source: 0x11 (17), 0x12 (18), 0x14 (20), 0x15 (21)

## Callers (17 call sites)

The factory is called from various game systems:
- `CBattleEngine__Init` (0x00404dd0) - 2 calls
- `CMissile__Init` (0x004baae0)
- `CUnit__Init` (0x004f86d0)
- Various other initialization functions

## Technical Notes

1. **Common Object Layout**: All CRT objects appear to share a common header:
   - Offset 0x00: vtable pointer
   - Offset 0x10: next pointer (linked list, set to NULL on creation)

2. **Exception Handling**: The factory uses SEH (Structured Exception Handling) to protect allocations.

3. **CRTBuilding Inheritance**: `CRTBuilding__Destructor` explicitly calls `CRTMesh__Destructor`, confirming inheritance.

4. **CRTCutscene Special Case**: Type ID 5 is unique - it calls the actual constructor `CRTCutscene__CRTCutscene()` after allocation, while other types just set the vtable.

## Discovery Date

December 2025 - Ghidra MCP analysis
