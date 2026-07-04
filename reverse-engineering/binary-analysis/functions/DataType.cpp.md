# DataType.cpp - Function Mappings

> Source file: `MissionScript/DataType.cpp`
> Debug path string: `0x0064cc80` ("[maintainer-local-source-export-root]\MissionScript\DataType.cpp")
> Header string: `0x0064c628` ("[maintainer-local-source-export-root]\MissionScript\DataType.h")
> Last updated: 2026-06-08

## Overview

DataType.cpp implements the **mission script data type system** - a polymorphic class hierarchy for representing different data types (int, float, bool, string, position, thing pointer) used by the mission scripting engine.

2026-06-08 VM/datatype/opcode schema proof: `missionscript-vm-datatype-opcode-schema-proof.md` and `missionscript-vm-datatype-opcode-schema.v1.json` now account for the finite static datatype factory inventory at `0x0052ec60 CDataType__CreateFromType`: `6` serialized datatype ids, `1..6`, covering int, float, string, bool, thing pointer, and position. The same schema links these datatype ids to the opcode/VM anchors `0x0052d3d0 CAsmInstruction__SpawnFromOpcode`, `0x00539b00 CScriptObjectCode__Run`, `0x0052ea40 CAsmInstruction__ExecuteCall`, `script_state+0x218`, and `script_object_code+0x68`; runtime datatype behavior, exact layouts, and rebuild parity remain separate proof.

## Wave576 String/Thing/Position Static Read-Back

Wave576 hardened the CStringDataType tail, CThingPtrDataType tail, shared CDataType scalar-deleting destructor wrapper, and CPositionDataType arithmetic slots with saved Ghidra signatures/comments/tags. This is static retail-binary evidence only; exact source identity, runtime MissionScript behavior, concrete layouts beyond observed fields, trailing CPosition dword semantics, and rebuild parity remain unproven.

| Address | Saved signature | Evidence |
| --- | --- | --- |
| `0x0052f2c0` | `void * __thiscall CStringDataType__Clone(void * this)` | Allocates an 8-byte CString object, installs vtable `0x005e4e4c`, allocates/copies a heap string from `this+0x04`, and null-terminates the clone buffer. |
| `0x0052f360` | `bool __thiscall CStringDataType__Equals(void * this, void * rhs)` | Reads rhs through datatype vtable slot `+0x38` and compares the returned string against `this+0x04`. |
| `0x0052f430` | `void __thiscall CStringDataType__Print(void * this, void * rhs)` | Calls rhs vtable slot `+0x40` and passes the returned reader cell to `CGenericActiveReader__SetReader` for the string field at `this+0x04`. |
| `0x0052f470` | `void * __thiscall CThingPtrDataType__Clone(void * this)` | Allocates an 8-byte thing-pointer datatype, copies `this+0x04`, registers the clone field with `CSPtrSet__AddToHead` when needed, and installs vtable `0x005e4df8`. |
| `0x0052f550` | `void * __thiscall CThingPtrDataType__ScalarDeletingDestructor(void * this, byte flags)` | Calls `CThingPtrDataType__Destructor` and frees `this` when `flags&1` is set. |
| `0x0052f570` | `void __thiscall CThingPtrDataType__Destructor(void * this)` | Removes `this+0x04` from the pointed object's `CSPtrSet` when present and restores base vtable pointer `0x005e4b4c`. |
| `0x0052f670` | `void * __thiscall CDataType__ScalarDeletingDestructor(void * this, byte flags)` | Shared CDataType scalar-deleting destructor wrapper reused by CInt/CFloat/CBool/CPosition vtable heads; calls `CDataType__Destructor` and frees `this` when `flags&1` is set. |
| `0x0052f690` | `void * __thiscall CStringDataType__InitFromString(void * this, char * source_text)` | Installs CString vtable `0x005e4e4c`, allocates/copies `source_text`, null-terminates it, and returns `this`. |
| `0x0052f720` | `void * __thiscall CStringDataType__ScalarDeletingDestructor(void * this, byte flags)` | Calls `CStringDataType__Destructor` and frees `this` when `flags&1` is set. |
| `0x0052f740` | `void __thiscall CStringDataType__Destructor(void * this)` | Frees the string buffer at `this+0x04` and restores base vtable pointer `0x005e4b4c`. |
| `0x0052f790` | `void * __thiscall CStringDataType__ReadFromBuffer(void * this, void * bytecode_reader)` | Reads a 4-byte length from the bytecode buffer, allocates `length+1`, reads string bytes, and appends a null terminator. |
| `0x0052f8a0` | `void * __thiscall CPositionDataType__SubtractPosition(void * this, void * rhs)` | Reads rhs through datatype vtable slot `+0x44`, allocates a 0x14-byte CPosition object, installs vtable `0x005e4da4`, and stores observed x/y/z differences. |
| `0x0052f920` | `void * __thiscall CPositionDataType__ScaleByFloat(void * this, void * rhs)` | Reads rhs float through datatype vtable slot `+0x34`, allocates a 0x14-byte CPosition object, installs vtable `0x005e4da4`, and stores observed x/y/z scaled values. |

## Wave575 Factory/Float Static Read-Back

Wave575 hardened `CDataType__CreateFromType` and the adjacent `CFloatDataType` arithmetic/comparison/assignment slots with saved Ghidra signatures/comments/tags. This is static retail-binary evidence only; exact source identity, runtime MissionScript behavior, concrete layouts beyond observed fields, exact type enum names, and rebuild parity remain unproven.

| Address | Saved signature | Evidence |
| --- | --- | --- |
| `0x0052ec60` | `void * __cdecl CDataType__CreateFromType(int type_id, void * bytecode_reader)` | Factory called from `CScriptObjectCode__ReadSymbolTable`; switches serialized `type_id` 1..6, installs observed datatype vtables, and reads initial payload bytes from `bytecode_reader`. Type 2 installs `CFloatDataType` vtable `0x005e4ea4`; type 4 installs the observed `CBoolDataType` vtable region `0x005e4d50`. |
| `0x0052ef50` | `void * __thiscall CFloatDataType__Add(void * this, void * rhs)` | Float add slot at data pointer `0x005e4ea8`; reads rhs through datatype vtable slot `+0x34`, allocates an 8-byte `CFloatDataType`, installs vtable `0x005e4ea4`, and stores the sum. |
| `0x0052efc0` | `void * __thiscall CFloatDataType__Subtract(void * this, void * rhs)` | Float subtract slot at data pointer `0x005e4eac`; reads rhs through slot `+0x34`, allocates an 8-byte `CFloatDataType`, and stores `this+0x04 - rhs`. |
| `0x0052f030` | `void * __thiscall CFloatDataType__Multiply(void * this, void * rhs)` | Float multiply slot at data pointer `0x005e4eb0`; reads rhs through slot `+0x34`, allocates an 8-byte `CFloatDataType`, and stores the product. |
| `0x0052f0a0` | `void * __thiscall CFloatDataType__Divide(void * this, void * rhs)` | Float divide slot at data pointer `0x005e4eb4`; reads rhs through slot `+0x34`, allocates an 8-byte `CFloatDataType`, and stores `this+0x04 / rhs`. |
| `0x0052f110` | `bool __thiscall CFloatDataType__Equals(void * this, void * rhs)` | Float equality slot at data pointer `0x005e4ebc`; reads rhs through slot `+0x34` and compares against `this+0x04`. |
| `0x0052f140` | `bool __thiscall CFloatDataType__NotEquals(void * this, void * rhs)` | Float inequality slot at data pointer `0x005e4ec0`; reads rhs through slot `+0x34` and compares against `this+0x04`. |
| `0x0052f170` | `void __thiscall CFloatDataType__Assign(void * this, void * rhs)` | Float assignment slot at data pointer `0x005e4eb8`; reads rhs through slot `+0x34` and stores the returned float at `this+0x04`. |
| `0x0052f190` | `bool __thiscall CFloatDataType__LessThan(void * this, void * rhs)` | Float less-than slot at data pointer `0x005e4ec4`; returns whether `this+0x04 < rhs`. |
| `0x0052f1c0` | `bool __thiscall CFloatDataType__GreaterThan(void * this, void * rhs)` | Float greater-than slot at data pointer `0x005e4ec8`; returns whether `this+0x04 > rhs`. |
| `0x0052f1f0` | `bool __thiscall CFloatDataType__LessOrEqual(void * this, void * rhs)` | Float less-or-equal slot at data pointer `0x005e4ecc`; returns whether `this+0x04 <= rhs`. |
| `0x0052f220` | `bool __thiscall CFloatDataType__GreaterOrEqual(void * this, void * rhs)` | Float greater-or-equal slot at data pointer `0x005e4ed0`; returns whether `this+0x04 >= rhs`. |

## Wave573 Static Read-Back

Wave573 hardened the CIntDataType arithmetic/comparison head and the base destructor with saved Ghidra signatures/comments/tags. This is retail-binary evidence only; exact source identity, runtime MissionScript behavior, concrete layouts beyond observed fields, and rebuild parity remain unproven.

| Address | Saved signature | Evidence |
| --- | --- | --- |
| `0x0052d0a0` | `void * __thiscall CIntDataType__Add(void * this, void * rhs)` | Reads `rhs` through vtable slot `+0x30`, allocates an 8-byte CInt object, and stores the sum. |
| `0x0052d110` | `void * __thiscall CIntDataType__Subtract(void * this, void * rhs)` | Reads `rhs` through slot `+0x30`, allocates an 8-byte CInt object, and stores the difference. |
| `0x0052d180` | `void * __thiscall CIntDataType__Multiply(void * this, void * rhs)` | Reads `rhs` through slot `+0x30`, allocates an 8-byte CInt object, and stores the product. |
| `0x0052d1f0` | `void * __thiscall CIntDataType__Divide(void * this, void * rhs)` | Reads `rhs` through slot `+0x30`, allocates an 8-byte CInt object, and stores the integer quotient. |
| `0x0052d260` | `bool __thiscall CIntDataType__Equals(void * this, void * rhs)` | Returns `this+0x04 == rhs_value`. |
| `0x0052d280` | `bool __thiscall CIntDataType__NotEquals(void * this, void * rhs)` | Returns `this+0x04 != rhs_value`. |
| `0x0052d2a0` | `void __thiscall CIntDataType__Assign(void * this, void * rhs)` | Stores the integer value returned by `rhs` at `this+0x04`. |
| `0x0052d2c0` | `bool __thiscall CIntDataType__LessThan(void * this, void * rhs)` | Returns `this+0x04 < rhs_value`. |
| `0x0052d2e0` | `bool __thiscall CIntDataType__GreaterThan(void * this, void * rhs)` | Returns `this+0x04 > rhs_value`. |
| `0x0052d300` | `bool __thiscall CIntDataType__LessOrEqual(void * this, void * rhs)` | Returns `this+0x04 <= rhs_value`. |
| `0x0052d320` | `bool __thiscall CIntDataType__GreaterOrEqual(void * this, void * rhs)` | Returns `this+0x04 >= rhs_value`. |
| `0x0052d390` | `void __thiscall CDataType__Destructor(void * this)` | Base destructor that restores the base CDataType vtable pointer. |

## Wave574 Bool Static Read-Back

Wave1208 current-risk re-read (`wave1208-cbooldatatype-current-risk-review`) refreshed the three bool datatype slots with fresh Ghidra export metadata/tag/xref/instruction/decompile evidence: `3 CBoolDataType current-risk rows`, `3 xref rows`, `99 instruction rows`, and `3 decompile rows`. The reviewed anchors are `CBoolDataType__Equals`, `CBoolDataType__NotEquals`, and `CBoolDataType__Assign`; active current-risk progress is `1092/1179 = 92.62%` with remaining active focused work: 87, current focused candidates: 1141, live regenerated current focused candidates: 1141, current risk candidates: 6166, unique-address accounting, continuity denominator, current-risk denominator, focused threshold `15`, not Wave911 reconstruction, and legacy additive counter is deprecated (`1123/1179`) with a 26 duplicate-address overcount and Wave1145 arithmetic overcount: 5. This was a read-only review with no mutation, no rename, no signature change, no comment change, no tag change, no function-boundary change, and no executable-byte change; Codex read-only consults used. Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260607-040938_post_wave1208_cbooldatatype_current_risk_review_verified`. Static closure remains `6411/6411 = 100.00%` with `0 / 0 / 0`. Active measurement paths: `static-reaudit-current-risk-ledger.json`, `static-reaudit-measurement-register.md`, and `wave1108-current-risk-rank`. This is rebuild-grade static contracts evidence for no noticeable difference planning only; runtime MissionScript behavior, runtime bool datatype behavior, exact bool ABI, exact datatype layout, exact source identity, BEA patching behavior, rebuild parity, and no-noticeable-difference parity remain separate proof.

Wave574 semantically renamed and hardened three adjacent boolean datatype vtable slots. Wave575 later confirmed the factory/type-id mapping at the saved-Ghidra evidence level: type 2 installs `CFloatDataType` vtable `0x005e4ea4`, while type 4 installs the observed CBoolDataType vtable region. This is static retail-binary evidence only; exact source identity, concrete datatype layouts beyond observed fields, runtime MissionScript behavior, and rebuild parity remain unproven.

| Address | Saved signature | Evidence |
| --- | --- | --- |
| `0x0052e420` | `bool __thiscall CBoolDataType__Equals(void * this, void * rhs)` | Bool equality slot at data pointer `0x005e4d68`; `RET 0x4`, rhs read through datatype vtable slot `+0x3c`, compare against the byte at `this+0x04`. |
| `0x0052e440` | `bool __thiscall CBoolDataType__NotEquals(void * this, void * rhs)` | Bool inequality slot at data pointer `0x005e4d6c`; `RET 0x4`, rhs read through datatype vtable slot `+0x3c`, compare against the byte at `this+0x04`. |
| `0x0052e460` | `void __thiscall CBoolDataType__Assign(void * this, void * rhs)` | Bool assignment slot at data pointer `0x005e4d64`; `RET 0x4`, rhs read through datatype vtable slot `+0x3c`, store returned byte at `this+0x04`. |

## Class Hierarchy (from RTTI)

```
CDataType                    (base class)
  +-- CIntDataType          (integer values)
  +-- CFloatDataType        (floating point; type-id 2 installs vtable 0x005e4ea4)
  +-- CBoolDataType         (boolean byte value; type-id 4 installs observed vtable region 0x005e4d50)
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
| CFloatDataType | 0x005e4ea4 | CDataType__ScalarDeletingDestructor |
| CStringDataType | 0x005e4e4c | CStringDataType__ScalarDeletingDestructor |
| CBoolDataType / boolean result (observed Wave574 vtable region) | 0x005e4d50 | CDataType__ScalarDeletingDestructor |
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
- 2 = CFloatDataType (size 8, vtable `0x005e4ea4`)
- 3 = CStringDataType (size 8, vtable 0x005e4e4c)
- 4 = CBoolDataType / boolean result (size 8, observed vtable region `0x005e4d50`; slots include `0x005e4d64`, `0x005e4d68`, and `0x005e4d6c`)
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

1. **Factory type-id mapping is saved for the observed retail binary** - Wave575 confirms type `2` installs `CFloatDataType` vtable `0x005e4ea4`, while type `4` installs the observed `CBoolDataType` region containing `CBoolDataType__Assign`, `CBoolDataType__Equals`, and `CBoolDataType__NotEquals`. Exact original enum spelling remains unproven.

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
