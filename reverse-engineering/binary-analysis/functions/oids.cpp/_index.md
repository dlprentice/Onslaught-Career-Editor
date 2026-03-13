# oids.cpp - Object ID Factory System

**Source File:** `C:\dev\ONSLAUGHT2\oids.cpp`
**Debug String Address:** `0x00630c20`
**Analysis Date:** December 2025

## Overview

The `oids.cpp` file implements the **Object ID (OID) Factory System** - a central factory pattern for creating game objects based on numeric OID values. This is the core object instantiation system used throughout the game engine.

## Functions Found

| Address | Name | Size | Purpose |
|---------|------|------|---------|
| `0x004bf090` | `OID__CreateObject` | ~2048 bytes | Main factory - creates objects by OID |
| `0x005490e0` | `OID__AllocObject` | ~192 bytes | Memory allocation wrapper with error handling |
| `0x004bfa60` | `OID__InitTargetData` | ~32 bytes | Initialize target tracking data |
| `0x004bfd20` | `OID__InitBaseObject` | ~32 bytes | Initialize base object vtable |
| `0x004bf9e0` | `OID__InitInfluenceMapObject` | ~48 bytes | Initialize influence map object |

**Total Functions:** 5 functions renamed

## OID__CreateObject (0x004bf090)

This is the main object factory function. It takes an OID as a parameter and returns a newly allocated and initialized object of the corresponding type.

### Signature
```cpp
void* OID__CreateObject(int objectId);
```

### OID Mapping

The function uses a large switch statement to map OID values to object types:

| OID | Hex | Object Size | Object Type (Inferred) |
|-----|-----|-------------|------------------------|
| 3 | 0x03 | 0x63C (1596) | Complex game entity with squad support |
| 7 | 0x07 | 0x4C (76) | Simple map entity |
| 10 | 0x0A | 0x284 (644) | Medium entity |
| 11 | 0x0B | 0xE4 (228) | Base object type |
| 15 | 0x0F | 0x44C (1100) | Large entity |
| 16 | 0x10 | 0x10C (268) | Entity with callback system |
| 17 | 0x11 | 0xE4 (228) | Base object type |
| 18 | 0x12 | 0x40 (64) | Small map entity |
| 19 | 0x13 | 0x46C (1132) | Influence map entity |
| 21 | 0x15 | 0x210 (528) | Medium entity |
| 25 | 0x19 | 0x26C (620) | Medium entity |
| 26 | 0x1A | 0xD74 (3444) | Very large entity |
| 27 | 0x1B | 0x7C (124) | Small entity |
| 29 | 0x1D | 0xE0 (224) | Medium entity |
| 31 | 0x1F | 0x84 (132) | Small entity |
| 36 | 0x24 | 0x9C (156) | Entity with squad support |
| 37 | 0x25 | 0x80 (128) | Small entity |
| 38 | 0x26 | 0x440 (1088) | Influence map entity |
| 41 | 0x29 | 0x44C (1100) | Influence map entity |
| 43 | 0x2B | 0xE8 (232) | Entity with target tracking |

### Initialization Hierarchy

Objects are initialized through a class hierarchy:

```
FUN_004f3e10 (Base Thing Init)
    |
    +-- FUN_004f33e0 (Simple Thing Init)
    |       |
    |       +-- CMapWhoEntry__Invalidate
    |
    +-- FUN_004f7e90 (Complex Entity Init)
    |       |
    |       +-- CSPtrSet__Init (6x)
    |       +-- FUN_004f8140
    |       +-- FUN_0044adb0
    |
    +-- OID__InitBaseObject (Base Object Init)
    |       |
    |       +-- Sets vtable PTR_FUN_005d844c
    |
    +-- OID__InitInfluenceMapObject
    |       |
    |       +-- CInfluenceMap__Init
    |
    +-- OID__InitTargetData
            |
            +-- Sets target tracking fields
```

## OID__AllocObject (0x005490e0)

Memory allocation wrapper that uses `CMemoryManager__Alloc` and handles out-of-memory conditions for different memory pools.

### Signature
```cpp
void* OID__AllocObject(int size, int poolId, const char* sourceFile, int lineNumber);
```

### Parameters
- `size`: Allocation size in bytes
- `poolId`: Memory pool identifier (5 = general, 7 = map entities)
- `sourceFile`: Debug source file path
- `lineNumber`: Debug line number for tracking

### Error Handling
On allocation failure, triggers error codes:
- `0xCD`: Pool 1 exhausted
- `0xCE`: Pool 2 exhausted
- `0xCF`: Pool 3 exhausted
- `0xD0`: Pool 4 exhausted

## OID__InitTargetData (0x004bfa60)

Initializes target tracking data for entities that can be targeted.

### Memory Layout
```cpp
struct TargetData {
    int field_0;    // = 0
    int field_4;    // = 0xFFFFFFFF (-1)
    int field_8;    // = 0
    float field_C;  // = -1.0f (0xBF800000)
};
```

## OID__InitBaseObject (0x004bfd20)

Initializes the base object type with appropriate vtable pointers.

### Vtables Set
- Primary vtable: `PTR_FUN_005d844c`
- Secondary vtable (offset +8): `PTR_FUN_005d83d4`

## OID__InitInfluenceMapObject (0x004bf9e0)

Initializes objects that participate in the AI influence map system.

### Initialization
- Calls `CInfluenceMap__Init`
- Sets vtable to `PTR_LAB_005dc1c0`
- Clears field at offset `0x3BC` (0xEF * 4)

## Related Classes (from RTTI)

Based on RTTI strings found in the binary, these classes are likely created via the OID system:

- `CSquad`, `CNormalSquad`, `CRelaxedSquad` - Squad management
- `CInfluenceMap`, `CInfluenceNode` - AI influence system
- `CUnit`, `CBattleEngine`, `CMCMech` - Game units
- `CBuilding`, `CBuildingNamedMesh` - Structures
- `CCamera` variants - Camera types
- `CGuide`, `CAirGuide`, `CBoatGuide` - Pathfinding
- Various AI classes (`CUnitAI`, `CBoatAI`, `CBomberAI`, etc.)

## Exception Handlers

The file contains 20 exception unwind handlers (`Unwind@005d3cb0` through `Unwind@005d3f53`) at addresses in the `0x005d3xxx` range. These are compiler-generated C++ exception handling code for proper object destruction on exception.

## Technical Notes

1. **Memory Management**: Uses custom `CMemoryManager` with multiple memory pools
2. **Pool ID 5**: General game objects (most common)
3. **Pool ID 7**: Map-related objects (simpler entities)
4. **Vtable Pattern**: All objects have dual vtables at offsets 0 and 8
5. **thiscall Convention**: Most initialization functions use `__thiscall` (ECX = this pointer)

## Cross-References

The debug path string at `0x00630c20` is referenced from:
- 20 locations in `OID__CreateObject` (allocation calls with line numbers)
- 20 exception unwind handlers

## See Also

- `CSPtrSet__Init` - SPtrSet init helper (zeros head/tail/count)
- `CInfluenceMap__Init` - Influence map system
- `CMemoryManager__Alloc` - Memory allocation
