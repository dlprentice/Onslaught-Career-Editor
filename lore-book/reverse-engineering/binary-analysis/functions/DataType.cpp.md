# DataType.cpp - Function Mappings

> Source file: `MissionScript/DataType.cpp`
> Debug path string: `0x0064cc80` ("C:\dev\ONSLAUGHT2\MissionScript\DataType.cpp")
> Header string: `0x0064c628` ("C:\dev\ONSLAUGHT2\MissionScript\DataType.h")
> Last updated: 2025-12-16

## Overview

DataType.cpp implements the **mission script data type system** - a polymorphic class hierarchy for representing different data types (int, float, bool, string, position, thing pointer) used by the mission scripting engine.

## Class Hierarchy (from RTTI)

```
CDataType                    (base class)
  +-- CIntDataType          (integer values)
  +-- CFloatDataType        (floating point, CBoolDataType vtable)
  +-- CStringDataType       (null-terminated strings)
  +-- CPositionDataType     (3D vector positions)
  +-- CThingPtrDataType     (smart pointers to game things)
```

**RTTI Strings Found:**
- `.?AVCDataType@@` at 0x0064c598
- `.?AVCIntDataType@@` at 0x0064c5b0
- `.?AVCBoolDataType@@` at 0x0064cb20
- `.?AVCPositionDataType@@` at 0x0064cbe0
- `.?AVCFloatDataType@@` at 0x0064cc00
- `.?AVCThingPtrDataType@@` at 0x0064cc20
- `.?AVCStringDataType@@` at 0x0064cc40

## VTable Addresses

| Class | VTable Address | First Entry |
|-------|----------------|-------------|
| CIntDataType | 0x005e4af8 | CDataType__ScalarDeletingDestructor |
| CBoolDataType (CFloatDataType) | 0x005e4ea4 | CDataType__ScalarDeletingDestructor |
| CStringDataType | 0x005e4e4c | CStringDataType__ScalarDeletingDestructor |
| CFloatDataType | 0x005e4d50 | CDataType__ScalarDeletingDestructor |
| CThingPtrDataType | 0x005e4df8 | CThingPtrDataType__ScalarDeletingDestructor |
| CPositionDataType | 0x005e4da4 | CDataType__ScalarDeletingDestructor |
| CDataType (base) | 0x005e4b4c | (abstract base) |

## Functions (38 total)

### Factory Functions

| Address | Name | Purpose |
|---------|------|---------|
| 0x0052ec60 | CDataType__CreateFromType | Factory - creates data type from type ID (1-6 switch) |

**Type IDs in CreateFromType:**
- 1 = CIntDataType (size 8, vtable 0x005e4af8)
- 2 = CBoolDataType (size 8, vtable 0x005e4ea4)
- 3 = CStringDataType (size 8, vtable 0x005e4e4c)
- 4 = CFloatDataType (size 8, vtable 0x005e4d50)
- 5 = CThingPtrDataType (size 8, vtable 0x005e4df8)
- 6 = CPositionDataType (size 0x14, vtable 0x005e4da4)

### CDataType (Base Class)

| Address | Name | Purpose |
|---------|------|---------|
| 0x0052d390 | CDataType__Destructor | Base destructor - sets vtable to base |
| 0x0052f670 | CDataType__ScalarDeletingDestructor | Scalar deleting destructor wrapper |

### CIntDataType (Integer Values)

| Address | Name | Purpose |
|---------|------|---------|
| 0x0052d0a0 | CIntDataType__Add | Returns new CIntDataType with sum |
| 0x0052d110 | CIntDataType__Subtract | Returns new CIntDataType with difference |
| 0x0052d180 | CIntDataType__Multiply | Returns new CIntDataType with product |
| 0x0052d1f0 | CIntDataType__Divide | Returns new CIntDataType with quotient |
| 0x0052d260 | CIntDataType__Equals | Returns bool (this == other) |
| 0x0052d280 | CIntDataType__NotEquals | Returns bool (this != other) |
| 0x0052d2a0 | CIntDataType__Assign | Assigns value from other |
| 0x0052d2c0 | CIntDataType__LessThan | Returns bool (this < other) |
| 0x0052d2e0 | CIntDataType__GreaterThan | Returns bool (this > other) |
| 0x0052d300 | CIntDataType__LessOrEqual | Returns bool (this <= other) |
| 0x0052d320 | CIntDataType__GreaterOrEqual | Returns bool (this >= other) |

### CFloatDataType (Floating Point)

| Address | Name | Purpose |
|---------|------|---------|
| 0x0052ef50 | CFloatDataType__Add | Returns new CFloatDataType with sum |
| 0x0052efc0 | CFloatDataType__Subtract | Returns new CFloatDataType with difference |
| 0x0052f030 | CFloatDataType__Multiply | Returns new CFloatDataType with product |
| 0x0052f0a0 | CFloatDataType__Divide | Returns new CFloatDataType with quotient |
| 0x0052f110 | CFloatDataType__Equals | Returns bool (this == other) |
| 0x0052f140 | CFloatDataType__NotEquals | Returns bool (this != other) |
| 0x0052f170 | CFloatDataType__Assign | Assigns value from other |
| 0x0052f190 | CFloatDataType__LessThan | Returns bool (this < other) |
| 0x0052f1c0 | CFloatDataType__GreaterThan | Returns bool (this > other) |
| 0x0052f1f0 | CFloatDataType__LessOrEqual | Returns bool (this <= other) |
| 0x0052f220 | CFloatDataType__GreaterOrEqual | Returns bool (this >= other) |

### CStringDataType (Strings)

| Address | Name | Purpose |
|---------|------|---------|
| 0x0052f2c0 | CStringDataType__Clone | Creates copy of string data type |
| 0x0052f360 | CStringDataType__Equals | String comparison (strcmp) |
| 0x0052f430 | CStringDataType__Print | Print string value |
| 0x0052f690 | CStringDataType__InitFromString | Initialize from C string |
| 0x0052f720 | CStringDataType__ScalarDeletingDestructor | Scalar deleting destructor |
| 0x0052f740 | CStringDataType__Destructor | Frees string buffer |
| 0x0052f790 | CStringDataType__ReadFromBuffer | Read string from DXMemBuffer |

### CPositionDataType (3D Vectors)

| Address | Name | Purpose |
|---------|------|---------|
| 0x0052f8a0 | CPositionDataType__SubtractPosition | Returns new position (this - other) |
| 0x0052f920 | CPositionDataType__ScaleByFloat | Returns new position (this * scalar) |

### CThingPtrDataType (Smart Pointers)

| Address | Name | Purpose |
|---------|------|---------|
| 0x0052f470 | CThingPtrDataType__Clone | Creates copy with reference counting |
| 0x0052f550 | CThingPtrDataType__ScalarDeletingDestructor | Scalar deleting destructor |
| 0x0052f570 | CThingPtrDataType__Destructor | Releases thing reference |

## Struct Layouts

### CDataType (base, size 4)
```cpp
struct CDataType {
    void* vtable;       // +0x00 - Virtual function table
};
```

### CIntDataType / CFloatDataType / CBoolDataType (size 8)
```cpp
struct CIntDataType : CDataType {
    int value;          // +0x04 - Integer/float/bool value
};
```

### CStringDataType (size 8)
```cpp
struct CStringDataType : CDataType {
    char* str;          // +0x04 - Pointer to null-terminated string
};
```

### CPositionDataType (size 0x14)
```cpp
struct CPositionDataType : CDataType {
    float x;            // +0x04 - X coordinate
    float y;            // +0x08 - Y coordinate
    float z;            // +0x0C - Z coordinate
    float w;            // +0x10 - W component (unused?)
};
```

### CThingPtrDataType (size 8)
```cpp
struct CThingPtrDataType : CDataType {
    CThing* thing;      // +0x04 - Pointer to game thing (with refcount)
};
```

## Error Messages

| Address | String |
|---------|--------|
| 0x0064cc58 | "FATAL ERROR: unknown data type type %d" |
| 0x005fdc28 | "ERROR_INVALID_DATATYPE" |
| 0x005fe7e4 | "ERROR_DATATYPE_MISMATCH" |

## Related Functions (Not in DataType.cpp)

These functions reference DataType.cpp path but are from other source files:

| Address | Name | Source File | Notes |
|---------|------|-------------|-------|
| 0x0052d040 | CAsmInstruction__GetAttributeValue | AsmInstruction.cpp | Gets attribute, returns CIntDataType on error |
| 0x0052d3d0 | CAsmInstruction__SpawnFromOpcode | AsmInstruction.cpp | Creates instruction from opcode |

## Memory Allocation

All data types use `OID__AllocObject()` for allocation with:
- Pool ID: 0x18 (data types pool) or 0x76 (string data)
- Line number tracking for debugging

## Notes

1. **CBoolDataType uses CFloatDataType vtable** - In the binary, boolean values appear to be stored as floats (vtable 0x005e4ea4)

2. **Virtual method dispatch** - All operations (Add, Subtract, etc.) call virtual methods on the other operand via vtable offsets:
   - 0x30 = GetAsInt()
   - 0x34 = GetAsFloat()
   - 0x38 = GetAsString()
   - 0x40 = GetAsThing()
   - 0x44 = GetAsPosition()
   - 0x48 = Clone()

3. **Exception handling** - All functions set up SEH (Structured Exception Handling) via ExceptionList manipulation

4. **Unwind handlers** - 6 exception unwind handlers at 0x005d69c0-0x005d6a63 reference DataType.cpp for cleanup

## Discovery Method

Found via xrefs to debug path string at 0x0064cc80. 19 total references:
- 7 in CDataType__CreateFromType (factory cases)
- 6 in Unwind@ exception handlers
- 6 in other DataType class methods
