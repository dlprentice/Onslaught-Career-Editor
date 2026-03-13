# SquadNormal.cpp Functions

> Source File: SquadNormal.cpp | Binary: BEA.exe
> Debug Path: 0x0063283c ("C:\dev\ONSLAUGHT2\SquadNormal.cpp")

## Overview

CSquadNormal class implementation - handles normal squad behavior for groups of AI units. This class manages squad member spawning, iteration, positioning, and lifetime. The class uses a linked list to track squad members.

## Functions

| Address | Name | Purpose | Status |
|---------|------|---------|--------|
| 0x004e6870 | CSquadNormal__Constructor | Initialize CSquadNormal instance, sets vtables and member arrays | Renamed |
| 0x004e6ac0 | CSquadNormal__ScalarDestructor | Scalar deleting destructor wrapper | Renamed |
| 0x004e6ae0 | CSquadNormal__Destructor | Clean up squad resources, destroy member lists | Renamed |
| 0x004e6bb0 | CSquadNormal__Init | Initialize squad with spawn point position and state | Renamed |
| 0x004e6ce0 | (Orphan code) | Virtual method, references line 129 (0x81) | NOT A FUNCTION |
| 0x004e6f70 | CSquadNormal__RemoveMember | Remove a unit from the squad member list | Renamed |
| 0x004e8ed0 | CSquadNormal__CreateIterator | Allocate 0x10-byte iterator object, iterate member list | Renamed |
| 0x004e91f0 | CSquadNormal__SpawnMembers | Spawn squad members at positions with timeout checks | Renamed |

## Exception Handlers (Unwind Functions)

| Address | Name | Line | Purpose |
|---------|------|------|---------|
| 0x005d4dd0 | Unwind@005d4dd0 | 129 (0x81) | Exception cleanup |
| 0x005d4e00 | Unwind@005d4e00 | 1079 (0x437) | Exception cleanup for CreateIterator |
| 0x005d4e30 | Unwind@005d4e30 | 1163 (0x48b) | Exception cleanup for SpawnMembers |

## Class Structure (Partial)

Based on decompiled code analysis:

```cpp
class CSquadNormal {
    /* 0x00 */ void* vtable1;           // PTR_LAB_005df0f4
    /* 0x04 */ unknown field_4;
    /* 0x08 */ void* vtable2;           // PTR_LAB_005df07c
    /* ... */
    /* 0x1c */ float position[4];       // X, Y, Z, W position vector
    /* ... */
    /* 0x7c */ int field_7c;            // State flag (values 0, 1, 6 observed)
    /* ... */
    /* 0xa4 */ void* memberListHead;    // Linked list of squad members
    /* 0xa8 */ unknown field_a8;
    /* 0xac */ void* currentMember;     // Current iteration pointer
    /* ... */
    /* 0xb4 */ int memberCount;         // Number of members in squad
    /* ... */
    /* 0xc4 */ void* field_c4;          // Resource pointer (cleaned in destructor)
    /* 0xc8 */ void* field_c8;          // Resource pointer (cleaned in destructor)
    /* ... */
    /* 0xe4 */ void* field_e4;          // Resource pointer
    /* 0xec */ void* field_ec;          // Resource pointer
    /* ... */
    /* 0xf4 */ float savedPosition[4];  // Saved position vector
    /* ... */
    /* 0x124 */ float position2[4];     // Secondary position vector
    /* 0x134 */ float position3[4];     // Tertiary position vector
    /* 0x148 */ CSquadNormal* ownerSquad; // Pointer to owning squad
};
```

## VTables

- **Primary vtable**: 0x005df0f4
- **Secondary vtable**: 0x005df07c (at offset 0x08)

## Key Observations

1. **Linked list member management** - Squad members stored in linked list starting at offset 0xa4
2. **Multiple position vectors** - Stores several position vectors for movement/spawning logic
3. **Dual vtables** - Uses two vtable pointers (multiple inheritance or COM-style interfaces)
4. **Timeout-based spawning** - SpawnMembers checks `currentTime - spawnTime < -5.0` for spawn timing
5. **Iterator pattern** - CreateIterator allocates 0x10-byte iterator objects for member traversal
6. **Memory allocation** - Uses OID__AllocObject (tracked allocation with source file/line debug info)

## Orphan Code at 0x004e6ce0

The xref at 0x004e6e52 points into code that Ghidra hasn't recognized as a function. This code:
- Is referenced from vtable at 0x005df0fc
- Pushes SquadNormal.cpp debug path with line 129 (0x81)
- Contains arithmetic operations suggesting positioning/movement calculations
- Likely a virtual method that wasn't auto-detected

## Source Line References

| Line | Hex | Location | Context |
|------|-----|----------|---------|
| 129 | 0x81 | Orphan (0x004e6e52) via unwind | Unknown method |
| 1079 | 0x437 | CSquadNormal__CreateIterator | Iterator allocation |
| 1163 | 0x48b | CSquadNormal__SpawnMembers | Member spawning |

## Related Functions (Called)

- OID__AllocObject - Memory allocation with debug tracking
- FUN_0047eb80 - Get current game time
- CSPtrSet__Init (`0x004e5840`) - Simple 3-dword zero-init helper (called during construction)
- CSPtrSet__AddToTail (`0x004e5b20`) - Set/list insertion helper (called during Init based on state)
- CSPtrSet__Remove - Remove member from set/list (returns node to pool)
- FUN_004e5da0 - Unknown (called during construction)
- FUN_004e5e70 - Unknown (called during Init)
- FUN_004e8100 - Unknown (called during Init)
- FUN_004e83b0 - Unknown (called during Init with param 1)
- FUN_0048dcf0 - Unknown (called during SpawnMembers)
- FUN_00409760 / FUN_00409780 - List iteration helpers
- OID__FreeObject - Memory deallocation

## Investigation Needed

1. Analyze vtable at 0x005df0f4 for complete method list
2. Create function at 0x004e6ce0 (orphan virtual method)
3. Identify remaining Squad methods (likely 0x004e5xxx - 0x004e6xxx range)
4. Cross-reference with Stuart's source code if SquadNormal.cpp is available
5. Document interaction with Unit classes (squad members are Units)

---
*Discovered via debug path xref analysis (Dec 2025)*
*Functions renamed in Ghidra via GhydraMCP*
