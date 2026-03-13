# RTCutscene.cpp Functions

> Source File: RTCutscene.cpp | Binary: BEA.exe
> Debug Path: 0x00631e2c ("C:\dev\ONSLAUGHT2\RTCutscene.cpp")
> RTTI: 0x00631e18 (".?AVCRTCutscene@@")

## Overview

Real-time cutscene system. CRTCutscene handles cutscenes that play during gameplay without interrupting the action, as opposed to CCutscene which takes full control. Used for in-mission scripted events and cinematics.

## Functions Found via Debug Path Xrefs

The debug path string at 0x00631e2c is referenced 3 times, all from `CRTCutscene__Init`:

| Address | Name | Purpose | Status |
|---------|------|---------|--------|
| 0x004dbd80 | CRTCutscene__Init | Initialize RT cutscene from data | NAMED |

## Vtable Functions (0x005dea38)

Additional functions discovered via vtable analysis:

| Address | Name | Purpose | Status |
|---------|------|---------|--------|
| 0x004dbb60 | CRTCutscene__CRTCutscene | Default constructor, sets vtable | NAMED |
| 0x004dbc30 | CRTCutscene__Destructor | Destructor entry point (vfunc 0) | NAMED |
| 0x004dbc50 | CRTCutscene__DestructorImpl | Destructor implementation with cleanup | NAMED |
| 0x004dbe90 | CRTCutscene__Reset | Reset cutscene state, free resources | NAMED |
| 0x004dbf70 | CRTCutscene__SetCurrentIndex | Set current playback index | NAMED |

## Vtable Layout (0x005dea38)

| Index | Address | Name/Description |
|-------|---------|------------------|
| 0 | 0x004dbc30 | Destructor |
| 1 | 0x004dbd80 | Init |
| 2 | 0x004dbec0 | Unknown (not analyzed) |
| 3 | 0x0040c640 | Unknown (base class?) |
| 4 | 0x00405930 | Unknown (base class?) |
| 5 | 0x00405940 | Unknown (base class?) |
| 6 | 0x004dbfb0 | Unknown |
| 7 | 0x004dbb80 | Unknown |
| 8 | 0x004dbbe0 | Unknown |
| 9 | 0x004dbf80 | Unknown |
| 10 | 0x00405930 | Unknown (base class?) |
| 11 | 0x00459990 | Unknown |
| 12 | 0x004dbe50 | Unknown |
| 13 | 0x004dbe90 | Reset |
| 14 | 0x004dbfc0 | Unknown |
| 15 | 0x004014a0 | Unknown (base class?) |
| 16 | 0x004014a0 | Unknown (base class?) |
| 17 | 0x004dbff0 | Unknown |
| 18 | 0x004d6b20 | Unknown (parent class) |
| 19 | 0x004dbc10 | Unknown |

## CRTCutscene Class Structure (Partial)

Based on decompilation analysis:

| Offset | Size | Field | Notes |
|--------|------|-------|-------|
| 0x000 | 4 | vtable | CRTCutscene vtable (0x005dea38) |
| 0x004 | 4 | playbackSpeed | Float, initialized to 1.0f (0x3f800000) |
| 0x010 | 4 | parentObject | Pointer to parent (offset 0x10 in constructor ptr) |
| 0x014 | 4 | elementStates | Array of element state pointers |
| 0x018 | 4 | numElements | Number of cutscene elements |
| 0x01c | 4 | elementNames | Array of element name strings |
| 0x020 | 1 | isActive | Active flag (bool) |
| 0x024 | 4 | currentIndex | Current playback index, -1 = none |

## Function Details

### CRTCutscene__Init (0x004dbd80)

Initializes the RT cutscene from loaded cutscene data:
- Calls parent class init at 0x004d6a30
- Allocates element state array (numElements * 4 bytes)
- Allocates element name array (numElements * 4 bytes)
- Copies element names (256 bytes each) from source data
- Sets playbackSpeed to 1.0f
- Sets isActive to false
- Sets currentIndex to -1

Memory allocations use debug allocator (OID__AllocObject) with:
- Line 0x29 (41): Element states array
- Line 0x2a (42): Element names array
- Line 0x32 (50): Individual name buffers (256 bytes each)

### CRTCutscene__CRTCutscene (0x004dbb60)

Default constructor:
- Sets vtable to 0x005dea38
- Clears parentObject (offset 0x10)
- Clears numElements (offset 0x18)

### CRTCutscene__Destructor (0x004dbc30)

Destructor entry point:
- Calls DestructorImpl
- If param_1 & 1, frees the object memory

### CRTCutscene__DestructorImpl (0x004dbc50)

Full cleanup implementation:
- Resets vtable
- If active, frees elementStates and resets state
- Frees each element name buffer
- Frees element names array
- Calls parent destructor if parentObject exists

### CRTCutscene__Reset (0x004dbe90)

Resets cutscene to initial state:
- Only acts if isActive is true
- Frees elementStates if allocated
- Sets isActive to false
- Sets currentIndex to -1

### CRTCutscene__SetCurrentIndex (0x004dbf70)

Simple setter for currentIndex field at offset 0x24.

## Memory Allocator

Uses debug memory allocator at 0x005490e0 with signature:
```c
void* DebugAlloc(size_t size, int allocType, const char* file, int line)
```

Allocator type 0x1d (29) used for all allocations.

## Related Files

- [Cutscene.cpp](../Cutscene.cpp/_index.md) - Full-screen cutscene system
- Parent class at 0x004d6a30 (likely CCutsceneBase or similar)

## Outstanding Work

- Analyze remaining vtable functions (0x004dbec0, 0x004dbfb0, etc.)
- Identify parent class hierarchy
- Map relationship to CCutscene class
- Find callers of CRTCutscene methods

---
*Discovered via Phase 1 xref analysis (Dec 2025)*
