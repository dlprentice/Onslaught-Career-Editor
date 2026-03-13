# imposter.cpp Functions

> Source File: imposter.cpp | Binary: BEA.exe
> Debug Path: 0x0062d3f0 (`C:\dev\ONSLAUGHT2\imposter.cpp`)

## Overview

Imposters are billboard sprites used to represent distant 3D objects efficiently. This is a common Level of Detail (LOD) optimization technique in games - when objects are far from the camera, they are rendered as simple 2D sprites instead of full 3D models, saving significant rendering resources.

The imposter system maintains a global linked list of imposter objects at `DAT_0067a678`. Each imposter is identified by a name string and several parameters (texture ID, dimensions, etc.).

## Functions

| Address | Name | Purpose | Size |
|---------|------|---------|------|
| 0x004888f0 | CImposter__FindOrCreate | Find existing or create new imposter | ~384 bytes |
| 0x00488a70 | CImposter__AddToList | Add imposter to global linked list | ~48 bytes |

## Function Details

### CImposter__FindOrCreate (0x004888f0)

**Signature:** `CImposter* CImposter__FindOrCreate(char* name, int param2, int param3, int param4, int param5, int param6, int param7)`

Main imposter management function. Searches the global imposter list for an existing imposter matching the given name and parameters. If found, returns the existing imposter; otherwise allocates and initializes a new one.

**Algorithm:**
1. Iterate through linked list at `DAT_0067a678`
2. Compare name using `stricmp` (0x00568390, was `FUN_00568390`)
3. If name matches, verify all 6 parameters match (at offsets +0x24, +0x30, +0x34, +0x40, +0x44, +0x48)
4. If exact match found, return existing imposter
5. If name matches but parameters differ, log warning "strange lack of imposter"
6. If no match found, allocate new 0x4C byte structure via memory manager
7. Initialize fields and add to linked list
8. Return new imposter pointer

**CImposter Structure (0x4C bytes):**
| Offset | Size | Field |
|--------|------|-------|
| 0x00 | 4 | Next pointer (linked list) |
| 0x04 | 32 | Name string (copied) |
| 0x24 | 4 | param2 value |
| 0x30 | 4 | param4 value |
| 0x34 | 4 | param7 value |
| 0x38 | 4 | Flags (zeroed on init) |
| 0x3C | 4 | Unknown |
| 0x40 | 4 | param3 value |
| 0x44 | 4 | param5 value |
| 0x48 | 4 | param6 value |

### CImposter__AddToList (0x00488a70)

**Signature:** `void __thiscall CImposter__AddToList(CImposter* this)`

Adds an imposter to the global linked list. Uses thiscall convention (imposter pointer in ECX).

**Algorithm:**
1. If list is empty (`DAT_0067a678 == NULL`), set as head
2. Otherwise, traverse to end of list and append
3. Set imposter's next pointer to NULL

## Global Data

| Address | Name | Purpose |
|---------|------|---------|
| 0x0067a678 | g_pImposterList | Head of imposter linked list |

## Related Strings

| Address | String | Usage |
|---------|--------|-------|
| 0x0062d3f0 | "C:\dev\ONSLAUGHT2\imposter.cpp" | Debug path for assertions |
| 0x0062d410 | "strange lack of imposter" | Warning when name matches but params differ |

## Related Files

- **DXImposter.cpp** (0x006508cc) - DirectX-specific imposter rendering
- Console variables for imposter system:
  - `cg_renderimposters` (0x0062c8cc) - Toggle imposter rendering
  - `cg_imposterfadestart` (0x0063211c) - Distance at which imposters start to fade in
  - `cg_imposterfadeend` (0x006320dc) - Distance at which imposters stop fading in
  - `cg_forceobjectimposters` (0x00632164) - Force use of object imposters

## Key Observations

1. **Linked List Structure**: Imposters are managed as a simple singly-linked list with the head at a global address
2. **Name-Based Lookup**: Imposters are identified primarily by name string, with additional parameters for exact matching
3. **Lazy Creation**: Uses find-or-create pattern - only allocates new imposters when no existing match is found
4. **Parameter Mismatch Warning**: The "strange lack of imposter" message indicates the code expects parameters to be consistent for a given name
5. **Small Footprint**: Only 2 functions in this source file; rendering logic is in DXImposter.cpp

---
*Discovered via Phase 1 xref analysis (Dec 2025)*
