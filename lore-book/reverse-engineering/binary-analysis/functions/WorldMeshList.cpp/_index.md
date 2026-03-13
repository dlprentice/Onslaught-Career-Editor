# WorldMeshList.cpp Function Analysis

**Source file:** `C:\dev\ONSLAUGHT2\WorldMeshList.cpp`
**Header file:** `C:\dev\ONSLAUGHT2\WorldMeshList.h`
**Analysis date:** December 2025

## Overview

The `CWorldMeshList` class manages a linked list of mesh names used in the game world. It provides functionality for:
- Adding meshes by name (with recursive child mesh processing)
- Clearing all registered meshes
- Marking meshes as "used" for tracking purposes

This system appears to be used during world loading to track which meshes need to be instantiated or have already been processed.

## Global Data

| Address | Name | Purpose |
|---------|------|---------|
| `0x00855358` | `g_WorldMeshList` | Head of the mesh list (linked list) |
| `0x00855360` | `g_WorldMeshListIterator` | Current iterator position for traversal |

## Functions (3 total)

| Address | Name | Signature | Purpose |
|---------|------|-----------|---------|
| `0x0050d9e0` | `CWorldMeshList__Add` | `void Add(char* meshName)` | Add mesh by name recursively |
| `0x0050d9a0` | `CWorldMeshList__Clear` | `void Clear(void)` | Clear all entries and free memory |
| `0x0050dc20` | `CWorldMeshList__MarkUsed` | `void MarkUsed(char* meshName)` | Mark a mesh entry as used |

## Function Details

### CWorldMeshList__Add (0x0050d9e0)

**Purpose:** Adds a mesh to the world mesh list by name, recursively processing child meshes.

**Algorithm:**
1. Check if mesh name already exists in the list (strcmp loop)
2. If found, return early (no duplicates)
3. If not found, search the thing list for matching mesh name at offset `+0xB0`
4. Allocate new node (8 bytes) and copy mesh name string
5. Add node to list via `CSPtrSet__AddToHead`
6. Recursively process child meshes from offset `+0x4C` (child list)

**Called by:**
- `CSpawnerThng__Init` (0x004e3010) - When spawner initializes
- `CWorld__LoadWorld` (0x0050b9c0) - During world loading
- Self (recursive) - For child mesh processing
- `FUN_005392a0` (0x005392a0) - Unknown context

**Key observations:**
- Uses exception handling (SEH) with unwind handler at `0x005d5d00`
- Memory allocation via `OID__AllocObject` (custom allocator with debug info)
- Mesh name stored at offset `+0x00`, flags at offset `+0x04`

### CWorldMeshList__Clear (0x0050d9a0)

**Purpose:** Destroys all entries in the world mesh list, freeing allocated memory.

**Algorithm:**
1. Reset iterator to list head
2. Loop through all entries:
   - Unlink entry from list via `CSPtrSet__Remove` (returns list node to pool)
   - Call `OID__FreeObject` on mesh name string (free string)
   - Call `OID__FreeObject` on entry object (free entry)
3. Exit when list is empty

**Notes:**
- Simple cleanup function with no parameters
- Uses same globals as other WorldMeshList functions

### CWorldMeshList__MarkUsed (0x0050dc20)

**Purpose:** Finds a mesh by name and sets its "used" flag to 1.

**Algorithm:**
1. Reset iterator to list head
2. Loop through entries comparing mesh names (strcmp)
3. When found, set `entry[1] = 1` (used flag at offset +4)
4. Return

**Notes:**
- The "used" flag at offset +4 is checked by other functions to determine if a mesh has been processed
- Used for tracking which meshes need instantiation vs which already exist

## Mesh List Node Structure

```c
struct WorldMeshNode {
    char*  meshName;    // +0x00: Allocated string with mesh name
    uint32 usedFlag;    // +0x04: 0 = not used, 1 = used/processed
    // Next pointer managed by CSPtrSet
};
```

## Related Functions (not from WorldMeshList.cpp)

| Address | Name | Notes |
|---------|------|-------|
| `0x0050dcb0` | Unknown | Uses same globals but calls WorldPhysicsMap functions |
| `0x0050df80` | WorldPhysicsMap factory | Creates physics managers by type |
| `0x00549220` | Memory free | General memory deallocation |
| `0x005490e0` | Memory alloc | Custom allocator with debug file/line info |

## Cross-References

**Debug strings found:**
- `0x0063d488`: `"C:\dev\ONSLAUGHT2\WorldMeshList.cpp"` (line 0x2E = 46)
- `0x0063d464`: `"C:\dev\ONSLAUGHT2\WorldMeshList.h"` (line 0x11 = 17)

The line numbers in allocation calls suggest:
- Line 46 in .cpp: Node allocation in `Add()`
- Line 17 in .h: String allocation (possibly inline or macro in header)
