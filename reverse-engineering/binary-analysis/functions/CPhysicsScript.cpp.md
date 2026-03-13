# CPhysicsScript.cpp - Function Mappings

> Binary-to-source function mappings for CPhysicsScript.cpp
> Last updated: 2025-12-16

## Overview

CPhysicsScript manages a collection of physics script statements that control scripted physics behavior for game objects. The system uses a factory pattern to create different types of physics script statements (9 types) and maintains them in a linked list.

**Debug Path:** `C:\dev\ONSLAUGHT2\CPhysicsScript.cpp` (0x0062568c)

**Related File:** `CPhysicsScriptStatements.cpp` (0x00625818) - Contains the 9 statement type implementations

## Global Variables

| Address | Name | Type | Purpose |
|---------|------|------|---------|
| 0x0066e99c | g_pPhysicsScript | CPhysicsScript* | Global singleton pointer to physics script manager |

## Class Structure

```cpp
// Size: 0x10 bytes (16 bytes)
// Object Type ID: 0x18
class CPhysicsScript {
    /* 0x00 */ void* pHead;           // Head of statement linked list (CSPtrSet)
    /* 0x04 */ void* pTail;           // Tail pointer
    /* 0x08 */ void* pCurrent;        // Current iteration pointer
    /* 0x0C */ int   field_0C;        // Unknown
};
```

## Functions (5 total)

| Address | Name | Status | Notes |
|---------|------|--------|-------|
| 0x0042e880 | CPhysicsScript__Create | RENAMED | Creates singleton, allocates via OID |
| 0x0042e8f0 | CPhysicsScript__Destroy | RENAMED | Destroys all statements, frees memory |
| 0x0042e950 | CPhysicsScript__Load | RENAMED | Loads physics script from DXMemBuffer |
| 0x0042ea60 | CPhysicsScript__Update | RENAMED | Updates all statements each frame |
| 0x0042eb90 | CPhysicsScript__CreateStatement | RENAMED | Factory for 9 statement types |

---

## Function Details

### CPhysicsScript__Create (0x0042e880)

**Purpose:** Creates the global CPhysicsScript singleton instance.

**Signature:** `void CPhysicsScript__Create(void)`

**Behavior:**
1. Allocates CPhysicsScript object (0x10 bytes) via `OID__AllocObject`
2. Object type ID: 0x18
3. Calls `CSPtrSet__Init` to initialize the internal pointer-set/list fields (head/tail/count)
4. Stores result in global `g_pPhysicsScript` (0x0066e99c)
5. Sets to NULL if allocation fails

**Decompiled:**
```cpp
void CPhysicsScript__Create(void) {
    int iVar1 = OID__AllocObject(0x10, 0x18, "CPhysicsScript.cpp", 0x10);
    if (iVar1 != 0) {
        CSPtrSet__Init((void *)iVar1);
        g_pPhysicsScript = iVar1;
        return;
    }
    g_pPhysicsScript = 0;
}
```

---

### CPhysicsScript__Destroy (0x0042e8f0)

**Purpose:** Destroys all physics script statements and frees the manager.

**Signature:** `void CPhysicsScript__Destroy(void)`

**Behavior:**
1. Iterates through all statements in the linked list
2. Calls each statement's destructor via `vtable[0](1)`
3. Unlinks statement from internal list via `CSPtrSet__Remove` (returns list node to pool)
4. Frees the CPhysicsScript object itself
5. Sets `g_pPhysicsScript` to NULL

**Pattern:** Uses CSPtrSet iteration pattern with head/current pointers

---

### CPhysicsScript__Load (0x0042e950)

**Purpose:** Loads physics script data from a buffered file stream.

**Signature:** `int CPhysicsScript__Load(int param_1)` - Returns 1 on success, 0 on failure

**Behavior:**
1. First destroys any existing physics script (calls Destroy)
2. Creates fresh CPhysicsScript instance
3. Reads 2-byte header, validates magic number 0x12
4. Loops reading statement type IDs and data:
   - Reads 4-byte type ID (terminates on -1)
   - Reads 4-byte data value
   - Creates statement via `CPhysicsScript__CreateStatement(typeID)`
   - If statement created: calls `vtable[3](data)`, adds to tail
   - If creation fails: calls `FUN_0043e630` (fallback/error handling)

**File Format:**
```
[2 bytes] Magic: 0x0012
[4 bytes] Statement type ID (1-9, or -1 to terminate)
[4 bytes] Statement data
... repeat until type == -1 ...
```

---

### CPhysicsScript__Update (0x0042ea60)

**Purpose:** Updates all physics script statements each frame.

**Signature:** `void CPhysicsScript__Update(void)`

**Behavior:**
1. Iterates through statement linked list
2. For each statement, calls vtable[1]() - the Update method
3. Uses standard CSPtrSet iteration pattern

**Called:** Every frame from main game loop

---

### CPhysicsScript__CreateStatement (0x0042eb90)

**Purpose:** Factory function that creates physics script statement objects by type ID.

**Signature:** `void* CPhysicsScript__CreateStatement(int typeID)` - Returns statement pointer or NULL

**Statement Types (9 total):**

| Type ID | Object Type | VTable | Size | Notes |
|---------|-------------|--------|------|-------|
| 1 | 0x11 | 0x005d9878 | 0x110 | Statement type 1 |
| 2 | 0x13 | 0x005d9850 | 0x110 | Statement type 2 |
| 3 | 0x12 | 0x005d9864 | 0x110 | Statement type 3 |
| 4 | 0x14 | 0x005d983c | 0x110 | Statement type 4 |
| 5 | 0x15 | 0x005d9828 | 0x110 | Statement type 5 |
| 6 | 0x16 | 0x005d9814 | 0x110 | Statement type 6 |
| 7 | 0x17 | 0x005d9800 | 0x110 | Statement type 7 |
| 8 | 0x18 | 0x005d97ec | 0x110 | Statement type 8 |
| 9 | 0x19 | 0x005d97d8 | 0x110 | Statement type 9 |

**Common Statement Structure:**
```cpp
// Size: 0x110 bytes (272 bytes)
class CPhysicsScriptStatement {
    /* 0x00 */ void** vtable;      // Virtual function table
    /* 0x04 */ int    typeID;      // Statement type (1-9)
    /* 0x08 */ void*  field_08;    // Initialized to 0
    /* 0x0C */ byte   field_0C;    // Initialized to 0
    /* 0x10C */ int   field_10C;   // (offset 0x43*4) Initialized to 0
    // ... other fields ...
};
```

**VTable Layout (common to all statement types):**
| Offset | Method | Purpose |
|--------|--------|---------|
| 0x00 | Destructor | Delete statement |
| 0x04 | Update | Frame update |
| 0x08 | Unknown | - |
| 0x0C | LoadData | Load from stream (called during Load) |

---

## Related Systems

- **CSPtrSet** - Smart pointer set used for linked list management
- **OID System** - Object ID allocation system
- **DXMemBuffer** - Buffered file I/O for loading
- **CPhysicsScriptStatements.cpp** - Contains the 9 statement type implementations (269 xrefs to debug path)

## Notes

1. The physics script system appears to be a data-driven scripting system for physics behaviors
2. All 9 statement types share the same size (0x110 bytes) but have different vtables
3. The magic number 0x12 in the file format suggests version 18 (decimal)
4. Statement type IDs (1-9) map to object type IDs (0x11-0x19) with offset of 0x10
5. Related to `CPhysicsScriptStatements.cpp` which has 269 xrefs - likely contains all the individual statement type implementations

## See Also

- [CPhysicsScriptStatements.cpp](CPhysicsScriptStatements.cpp.md) - Statement implementations (not yet documented)
- [SPtrSet.cpp](SPtrSet.cpp/_index.md) - Smart pointer set used for statement list
- [WorldPhysicsManager.cpp](WorldPhysicsManager.cpp/_index.md) - Physics entity factory
