# EventFunction.cpp - Function Mappings

> Source file: `MissionScript/EventFunction.cpp`
> Debug path: `C:\dev\ONSLAUGHT2\MissionScript\EventFunction.cpp` (0x0064cce0)
> Last updated: 2025-12-16

## Overview

Event function system for mission scripting. Handles event-triggered script functions that respond to game events during missions.

**Key Classes:**
- `CEventFunction` - Event function container, holds list of event string parameters
- `CEventFunctionParam` - Parameter wrapper for event function arguments

**Inheritance:**
- `CEventFunction` inherits from `CRelaxedSquad` (idle/patrol AI state base class)
- Uses `CSPtrSet` for managing parameter lists

---

## Functions (5 total)

| Address | Name | Status | Notes |
|---------|------|--------|-------|
| 0x0052fa70 | CEventFunction__CEventFunction | RENAMED | Constructor - reads from DXMemBuffer |
| 0x0052fbb0 | CEventFunction__Clone | RENAMED | Clone/copy constructor with symbol table lookup |
| 0x0052fda0 | CEventFunction__Execute | RENAMED | Execute event function with parameters |
| 0x0052f9a0 | CEventFunction__Destructor | RENAMED | Destructor - cleans up parameter list |
| 0x0052fa50 | CEventFunction__ScalarDeletingDestructor | RENAMED | Scalar deleting destructor |

---

## Function Details

### CEventFunction__CEventFunction (0x0052fa70)

**Constructor** - Creates a new CEventFunction from serialized data.

```cpp
// Decompiled (cleaned up)
void CEventFunction::CEventFunction(int param_1, undefined4 param_2) {
    this->field_0x04 = 0;
    this->vtable = &CRelaxedSquad_vtable;  // 0x005d92d4

    CRelaxedSquad::Init();

    this->vtable = &CEventFunction_vtable;  // 0x005e4ef8
    this->field_0x1c = param_1;  // Store parent reference

    DXMemBuffer::ReadBytes(&this->field_0x08, 4);  // Read some config

    int count;
    DXMemBuffer::ReadBytes(&count, 4);  // Read parameter count

    for (int i = 0; i < count; i++) {
        DXMemBuffer::ReadBytes(&param_2, 4);  // Read param ID
        int result = FUN_00539760(param_2);   // Lookup in symbol table
        int* obj = *(int**)(result + 8);

        int type = (**(code**)(obj[0] + 0x4c))();  // Get object type
        if (type == 3) {  // Expected type: string
            // Allocate wrapper object (size 8, type 0x18)
            undefined4* wrapper = OID__AllocObject(8, 0x18,
                "C:\\dev\\ONSLAUGHT2\\MissionScript\\EventFunction.cpp", 0x40);
            if (wrapper != NULL) {
                wrapper[0] = obj;   // Store object pointer
                wrapper[1] = 0;     // Initialize next pointer
                CSPtrSet::AddToTail(wrapper);
            }
        } else {
            // Fatal error: expected string type
            CConsole__Printf(&DAT_0066f580,
                "FATAL ERROR: Event Function was expecting a string");
        }
    }
}
```

**Key Details:**
- Allocates parameter wrappers with size 8 bytes, type 0x18
- Expects all parameters to be strings (type 3)
- Stores parameters in a linked list via CSPtrSet
- Line number 0x40 (64) in source file

---

### CEventFunction__Clone (0x0052fbb0)

**Clone Constructor** - Creates a copy of an event function, resolving symbol references.

```cpp
// Decompiled (cleaned up)
undefined4* CEventFunction::Clone(undefined4* dest) {
    // Allocate new CEventFunction (size 0x20 = 32 bytes, type 0x18)
    undefined4* newObj = OID__AllocObject(0x20, 0x18,
        "C:\\dev\\ONSLAUGHT2\\MissionScript\\EventFunction.cpp", 0x4e);

    if (newObj != NULL) {
        // Initialize as CRelaxedSquad then CEventFunction
        newObj[1] = 0;
        newObj[0] = &CRelaxedSquad_vtable;
        newObj[2] = this->field_0x08;
        CRelaxedSquad::Init();
        newObj[0] = &CEventFunction_vtable;
        newObj[7] = dest;
    }

    // Get symbol table
    int symbolTable = *(int*)(*(int*)(this + 0x1c) + 0x58);
    if (symbolTable == 0) {
        FatalError("FATAL ERROR: Could not find symbol table in clone");
        return NULL;
    }

    int tableSize = *(int*)(symbolTable + 8);

    // Iterate through source parameters
    undefined4* srcParam = *(undefined4**)(this + 0xc);
    this->field_0x14 = srcParam;

    while (srcParam != NULL) {
        int* paramObj = (int*)*srcParam;

        // Find matching symbol in table
        for (int i = 0; i < tableSize; i++) {
            int entry = FUN_00539760(i);
            if (entry != 0 && *(int*)(entry + 8) != 0 &&
                *(int*)(entry + 8) == *paramObj) {

                // Verify type is string (3)
                int type = (**(code**)(*paramObj + 0x4c))();
                if (type != 3) {
                    FatalError("FATAL ERROR: Data type wrong type in clone for event function");
                    break;
                }

                // Compare string names
                byte* srcName = (**(code**)(**(int**)(entry + 8) + 0x38))();
                byte* dstName = (**(code**)(*paramObj + 0x38))();
                if (strcmp(srcName, dstName) == 0) {
                    // Create parameter wrapper
                    int* wrapper = OID__AllocObject(8, 0x18,
                        "C:\\dev\\ONSLAUGHT2\\MissionScript\\EventFunction.cpp", 0x1b);
                    if (wrapper != NULL) {
                        wrapper[0] = (int)paramObj;
                        wrapper[1] = 0;
                        CSPtrSet::AddToTail(wrapper);
                    }
                }
                break;
            }
        }

        // Move to next parameter
        srcParam = *(undefined4**)(srcParam + 4);
    }

    return newObj;
}
```

**Key Details:**
- CEventFunction object size: 32 bytes (0x20)
- Line numbers: 0x4e (78), 0x1b (27) in source
- Performs symbol table lookup to resolve references
- Validates string type (type == 3) before adding parameters

**Error Messages:**
- `"FATAL ERROR: Could not find symbol table in clone"` - Missing symbol table
- `"FATAL ERROR can't find event string in symbol table"` - Symbol not found
- `"FATAL ERROR: Data type wrong type in clone for event function"` - Type mismatch

---

### CEventFunction__Execute (0x0052fda0)

**Execute** - Executes the event function with its parameters.

```cpp
// Decompiled (cleaned up)
void CEventFunction::Execute() {
    int* paramNode = *(int**)(this + 0xc);  // Parameter list head
    int count = 0;
    undefined4 params[10];  // Local parameter array

    int paramData = (paramNode != NULL) ? *paramNode : 0;

    while (paramData != 0) {
        // Create CEventFunctionParam for each parameter
        undefined4* paramObj = OID__AllocObject(8, 0x18,
            "C:\\dev\\ONSLAUGHT2\\MissionScript\\EventFunction.cpp", 0x96);

        if (paramObj != NULL) {
            undefined1 value = *(undefined1*)(*(int*)(paramData + 4) + 0x14);
            paramObj[0] = &CEventFunctionParam_vtable;  // 0x005e4d50
            *(undefined1*)(paramObj + 1) = value;
        }

        params[count] = paramObj;

        // Move to next parameter
        paramNode = (int*)paramNode[1];
        count++;
        paramData = (paramNode != NULL) ? *paramNode : 0;
    }

    // Call the actual function with parameters
    FUN_00539a60(*(undefined4*)(this + 0x1c),
                 *(undefined4*)(this + 0x08),
                 params, count);
}
```

**Key Details:**
- Maximum 10 parameters (local array size)
- Creates CEventFunctionParam wrappers for each parameter
- Line number 0x96 (150) in source file
- Calls FUN_00539a60 which is the actual script execution function

---

### CEventFunction__Destructor (0x0052f9a0)

**Destructor** - Cleans up parameter list and releases resources.

```cpp
// Decompiled (cleaned up)
void CEventFunction::~CEventFunction() {
    this->vtable = &CEventFunction_vtable;  // 0x005e4ef8

    undefined4* paramNode = this->field_0x0c;  // Parameter list
    this->field_0x14 = paramNode;

    while (paramNode != NULL) {
        undefined4* obj = (undefined4*)*paramNode;
        if (obj != NULL) {
            obj[0] = 0;  // Clear vtable
            obj[1] = 0;  // Clear next pointer
            OID__FreeObject(obj);  // Free object
        }

        // Move to next
        paramNode = *(undefined4**)(this->field_0x14 + 4);
        this->field_0x14 = paramNode;
    }

    // Destroy internal lists
    CSPtrSet__Clear();  // CSPtrSet cleanup
    CSPtrSet__Clear();  // CSPtrSet cleanup
    CMonitor__Shutdown();  // Base class monitor cleanup (formerly FUN_004bac40)
}
```

**Key Details:**
- Iterates through parameter list freeing each wrapper
- Calls CSPtrSet cleanup twice (likely for two internal lists)
- Inherits from CRelaxedSquad, calls its cleanup

---

### CEventFunction__ScalarDeletingDestructor (0x0052fa50)

**Scalar Deleting Destructor** - MSVC-generated destructor wrapper.

```cpp
void CEventFunction::`scalar deleting destructor`(byte flags) {
    CEventFunction::~CEventFunction();
    if ((flags & 1) != 0) {
        OID__FreeObject(this);  // operator delete
    }
}
```

---

## Related Data

### Vtables

| Address | Name | Size | Notes |
|---------|------|------|-------|
| 0x005e4ef8 | CEventFunction__vtable | 40 bytes | CEventFunction virtual function table |
| 0x005e4d50 | CEventFunctionParam__vtable | 32 bytes | CEventFunctionParam virtual function table |
| 0x005d92d4 | CRelaxedSquad__vtable | - | Base class vtable |

### CEventFunction Vtable Entries (0x005e4ef8)

| Offset | Address | Function |
|--------|---------|----------|
| 0x00 | 0x004014c0 | (unknown) |
| 0x04 | 0x0052fa50 | ScalarDeletingDestructor |
| 0x08 | 0x004bacb0 | (inherited) |
| ... | ... | ... |

### CEventFunctionParam Vtable Entries (0x005e4d50)

| Offset | Address | Function |
|--------|---------|----------|
| 0x00 | 0x0052f670 | ScalarDeletingDestructor |
| 0x04 | 0x00405940 | (unknown) |
| 0x08 | 0x00405940 | (unknown) |
| ... | ... | ... |

---

## Class Layout

### CEventFunction (32 bytes / 0x20)

| Offset | Type | Name | Notes |
|--------|------|------|-------|
| 0x00 | void* | vtable | CEventFunction__vtable |
| 0x04 | int | field_0x04 | Unknown, initialized to 0 |
| 0x08 | int | field_0x08 | Read from DXMemBuffer |
| 0x0c | void* | paramList | CSPtrSet parameter list head |
| 0x10 | int | field_0x10 | Unknown |
| 0x14 | void* | paramIterator | Current iteration position |
| 0x18 | int | field_0x18 | Unknown |
| 0x1c | void* | parentRef | Parent object reference |

### CEventFunctionParam (8 bytes)

| Offset | Type | Name | Notes |
|--------|------|------|-------|
| 0x00 | void* | vtable | CEventFunctionParam__vtable |
| 0x04 | byte | value | Parameter value from source object |

---

## Error Messages

| Address | Message | Context |
|---------|---------|---------|
| 0x0064cd38 | "FATAL ERROR: Event Function was expecting a string" | Constructor - wrong param type |
| 0x0064cd6c | "FATAL ERROR can't find event string in symbol table" | Clone - symbol not found |
| 0x0064cda0 | "FATAL ERROR: Data type wrong type in clone for event function" | Clone - type mismatch |
| 0x0064cde0 | "FATAL ERROR: Could not find symbol table in clone" | Clone - no symbol table |

---

## Cross-References

### Callers

| Address | Function | Notes |
|---------|----------|-------|
| 0x00538fe4 | FUN_00538ec0 | Calls constructor |
| 0x0053913f | FUN_00539040 | Calls Clone |
| 0x00538c3b | FUN_00538b70 | Calls Execute |
| 0x00538d68 | FUN_00538c70 | Calls Execute |

### Dependencies

| Address | Function | Notes |
|---------|----------|-------|
| 0x00539760 | FUN_00539760 | Symbol table lookup |
| 0x00539a60 | FUN_00539a60 | Script execution |
| 0x00549220 | OID__FreeObject | operator delete |
| 0x004e5c60 | CSPtrSet__Clear | CSPtrSet cleanup |
| 0x004bac40 | CMonitor__Shutdown | Base monitor cleanup (formerly `FUN_004bac40`) |

---

## Related Functions (CEventFunctionParam)

| Address | Name | Status | Notes |
|---------|------|--------|-------|
| 0x0052f670 | CEventFunctionParam__ScalarDeletingDestructor | RENAMED | Destructor wrapper |

---

## Notes

1. **Mission Scripting System**: CEventFunction is part of the mission scripting system, handling event-triggered script callbacks during gameplay.

2. **Parameter Type 3**: The system expects all parameters to be string type (type == 3). This likely represents event names or script function names.

3. **Symbol Table**: The Clone function performs extensive symbol table lookups, suggesting this system resolves script references at runtime.

4. **Maximum Parameters**: The Execute function uses a local array of 10 parameters, implying a limit on event function arguments.

5. **Memory Management**: Uses OID__AllocObject for memory allocation with type 0x18 for both CEventFunction and CEventFunctionParam objects.
