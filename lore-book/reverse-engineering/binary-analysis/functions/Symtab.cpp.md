# Symtab.cpp - Function Mappings

> Symbol Table for Mission Scripting System
> Source: `MissionScript/Symtab.cpp`
> Debug path string: `C:\dev\ONSLAUGHT2\MissionScript\Symtab.cpp` at 0x00650134

## Overview

The symbol table (CSymtab) stores variable names and their data types for the mission scripting system. Each script has its own symbol table that maps variable names to their runtime values. This enables scripts to reference variables by name and provides type safety during script execution.

**Key Classes:**
- `CSymtab` - Symbol table container (20 bytes, 0x14)
- `CSymtabEntry` - Individual symbol entry (24 bytes, 0x18)

## Functions Found: 2

| Address | Name | Size | Purpose |
|---------|------|------|---------|
| 0x005395b0 | CScriptObjectCode__CloneSymbolTable | ~0x196 | Clone symbol table during script cloning |
| 0x00539770 | CScriptObjectCode__ReadSymbolTable | ~0x121 | Deserialize symbol table from buffer |

---

## Function Details

### CScriptObjectCode__CloneSymbolTable (0x005395b0)

**Purpose:** Creates a deep copy of a symbol table when cloning a script.

**Signature:** `CSymtab* __thiscall CSymtab__Clone(CSymtab* sourceSymtab)`

**Called by:**
- `FUN_00539040` (Script.cpp) - Script cloning operation at line 0x53 (83)

**Key Operations:**
1. Allocates new CSymtab (0x14 bytes) via `OID__AllocObject` at line 180 (0xb4)
2. Initializes CFlexArray with growth factor 16
3. Iterates through source symbol table entries
4. For each entry:
   - Gets data type via virtual call at vtable+0x48 (Clone method)
   - Allocates CSymtabEntry (0x18 bytes) at line 45 (0x2d)
   - Copies name string via `CStringDataType__InitFromString`
   - Copies data type reference, index, and flags
5. Checks for duplicate names before adding (strcmp loop)
6. Adds entry to new symbol table via `CFlexArray__Add`

**Decompiled (cleaned):**
```cpp
CSymtab* CSymtab::Clone(CSymtab* source) {
    CSymtab* newSymtab = OID__AllocObject(0x14, 0x18, "Symtab.cpp", 180);
    if (newSymtab) {
        CFlexArray__InitWithGrowth(newSymtab, 16, 1);
        newSymtab->count = 0;
    }

    int numEntries = source->count;
    for (int i = 0; i < numEntries; i++) {
        CSymtabEntry* srcEntry = source->entries[i];

        // Clone data type if present
        CDataType* clonedType = nullptr;
        if (srcEntry->dataType) {
            clonedType = srcEntry->dataType->Clone();  // vtable+0x48
        }

        // Create new entry
        CSymtabEntry* newEntry = OID__AllocObject(0x18, 0x18, "Symtab.cpp", 45);
        if (newEntry) {
            newEntry->name.InitFromString(srcEntry->GetName());  // vtable+0x38
            newEntry->index = srcEntry->index;
            newEntry->dataType = clonedType;
            newEntry->refCount = 0;
            newEntry->flags = 0;
        }

        // Check for duplicates by name
        const char* newName = newEntry->GetName();
        bool found = false;
        for (int j = 0; j < newSymtab->count; j++) {
            if (strcmp(newSymtab->entries[j]->GetName(), newName) == 0) {
                found = true;
                break;
            }
        }

        if (!found) {
            newEntry->index = newSymtab->count;
            CFlexArray__Add(newSymtab, newEntry);
            newSymtab->count++;
        }
    }

    return newSymtab;
}
```

---

### CScriptObjectCode__ReadSymbolTable (0x00539770)

**Purpose:** Deserializes a symbol table from a binary buffer (used when loading scripts).

**Signature:** `void __thiscall CSymtab__ReadFromBuffer(CSymtab* this, DXMemBuffer* buffer)`

**Called by:**
- `FUN_00538ec0` (Script.cpp) - Script loading operation at line 0x39 (57)

**Key Operations:**
1. Initializes CFlexArray with growth factor 16
2. Reads entry count (4 bytes)
3. For each entry:
   - Allocates CSymtabEntry (0x18 bytes) at line 289 (0x121)
   - Reads name string via `CStringDataType__ReadFromBuffer`
   - Reads data type ID (4 bytes)
   - If type ID != 0, creates data type via `CDataType__CreateFromType`
   - Reads index (offset 0x0C, 4 bytes)
   - Reads refCount (offset 0x10, 4 bytes)
   - Reads flags (offset 0x14, 4 bytes)
4. Adds entry to symbol table via `CFlexArray__Add`
5. Reads total count into this+0x10

**Decompiled (cleaned):**
```cpp
void CSymtab::ReadFromBuffer(DXMemBuffer* buffer) {
    CFlexArray__InitWithGrowth(this, 16, 1);

    int entryCount;
    buffer->ReadBytes(&entryCount, 4);

    for (int i = 0; i < entryCount; i++) {
        CSymtabEntry* entry = OID__AllocObject(0x18, 0x18, "Symtab.cpp", 289);
        if (entry) {
            entry->name.ReadFromBuffer(buffer);

            int typeId;
            buffer->ReadBytes(&typeId, 4);
            if (typeId == 0) {
                entry->dataType = nullptr;
            } else {
                entry->dataType = CDataType::CreateFromType(typeId, buffer);
            }

            buffer->ReadBytes(&entry->index, 4);      // offset 0x0C
            buffer->ReadBytes(&entry->refCount, 4);   // offset 0x10
            buffer->ReadBytes(&entry->flags, 4);      // offset 0x14
        }

        CFlexArray__Add(this, entry);
    }

    buffer->ReadBytes(&this->totalCount, 4);  // offset 0x10
}
```

---

## Class Structures

### CSymtab (0x14 bytes / 20 bytes)

```cpp
class CSymtab {
    /* 0x00 */ void** vtable;           // Virtual function table
    /* 0x04 */ CSymtabEntry** entries;  // CFlexArray data pointer
    /* 0x08 */ int capacity;            // CFlexArray capacity
    /* 0x0C */ int arrayCount;          // CFlexArray count
    /* 0x10 */ int count;               // Total symbol count
};
```

### CSymtabEntry (0x18 bytes / 24 bytes)

```cpp
class CSymtabEntry {
    /* 0x00 */ void** vtable;           // Virtual function table (CStringDataType)
    /* 0x04 */ char* name;              // Symbol name string
    /* 0x08 */ CDataType* dataType;     // Associated data type
    /* 0x0C */ int index;               // Symbol index in table
    /* 0x10 */ int refCount;            // Reference count
    /* 0x14 */ byte flags;              // Symbol flags
    /* 0x15 */ byte padding[3];         // Alignment padding
};
```

---

## Related Functions (Not in Symtab.cpp)

These functions are called by CSymtab but are defined elsewhere:

| Address | Name | Source File | Purpose |
|---------|------|-------------|---------|
| 0x0052f690 | CStringDataType__InitFromString | StringDataType.cpp | Initialize string from char* |
| 0x0052f790 | CStringDataType__ReadFromBuffer | StringDataType.cpp | Read string from buffer |
| 0x0052ec60 | CDataType__CreateFromType | DataType.cpp | Factory for data types |
| 0x004241a0 | CFlexArray__InitWithGrowth | flexarray.cpp | Init array with growth |
| 0x004241f0 | CFlexArray__Add | flexarray.cpp | Add element to array |
| 0x005490e0 | OID__AllocObject | oids.cpp | Object allocator |

---

## Exception Handlers

Three Unwind functions reference Symtab.cpp for exception cleanup:

| Address | Name | Parent Function | Purpose |
|---------|------|-----------------|---------|
| 0x005d7590 | Unwind@005d7590 | CSymtab__Clone | Free CSymtab on exception (line 180) |
| 0x005d75a9 | Unwind@005d75a9 | CSymtab__Clone | Free CSymtabEntry on exception (line 45) |
| 0x005d75d8 | Unwind@005d75d8 | CSymtab__ReadFromBuffer | Free CSymtabEntry on exception (line 289) |

These are compiler-generated cleanup handlers for RAII/exception safety.

---

## Cross-References

**Debug path xrefs to 0x00650134:**
1. 0x005395d3 - CSymtab__Clone (OID__AllocObject for CSymtab, line 180)
2. 0x00539656 - CSymtab__Clone (OID__AllocObject for CSymtabEntry, line 45)
3. 0x005397cc - CSymtab__ReadFromBuffer (OID__AllocObject for CSymtabEntry, line 289)
4. 0x005d7595 - Unwind@005d7590 (exception cleanup)
5. 0x005d75ab - Unwind@005d75a9 (exception cleanup)
6. 0x005d75dd - Unwind@005d75d8 (exception cleanup)

**Callers:**
- CSymtab__Clone called by: FUN_00539040 (Script.cpp Clone operation)
- CSymtab__ReadFromBuffer called by: FUN_00538ec0 (Script.cpp ReadFromBuffer)

---

## Notes

1. **Symbol Table Role:** The symbol table is essential for the scripting system's variable management. Scripts can look up variables by name and get/set their typed values.

2. **Duplicate Prevention:** CSymtab__Clone performs string comparison to avoid duplicate symbol names - this suggests scripts can reference variables from parent scopes.

3. **Data Type System:** Each symbol entry has an associated CDataType that determines how the value is stored, cloned, and serialized. See DataType.cpp.md for the type system.

4. **Memory Management:** Both functions use OID__AllocObject with specific size parameters and line numbers for debugging memory leaks.

5. **Related Source Files:**
   - Script.cpp - Contains CScript class that owns CSymtab
   - DataType.cpp - Data type base class and factory
   - StringDataType.cpp - String data type implementation

---

## Ghidra Renames Applied

| Old Name | New Name | Address |
|----------|----------|---------|
| FUN_005395b0 | CScriptObjectCode__CloneSymbolTable | 0x005395b0 |
| FUN_00539770 | CScriptObjectCode__ReadSymbolTable | 0x00539770 |

---

*Last updated: 2025-12-16*
*Analysis method: static binary analysis using Ghidra-derived evidence*
