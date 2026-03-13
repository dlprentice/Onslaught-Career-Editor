# ParticleSet.cpp Functions

> Source File: ParticleSet.cpp | Binary: BEA.exe
> Debug Path: 0x00630fb0 (`C:\dev\ONSLAUGHT2\ParticleSet.cpp`)

## Overview

ParticleSet manages collections of related particles that form visual effects (explosions, smoke trails, sparks, etc.). Each particle set contains multiple particle descriptors and handles their lifecycle. The system uses a factory pattern with 13 different particle set types, each with distinct vtables and initialization parameters.

Key data files referenced:
- `data/ParticleSets/MainSet.par` - Main game particle sets
- `data/ParticleSets/Frontend.par` - Frontend/menu particle sets

## Functions

| Address | Name | Size | Purpose |
|---------|------|------|---------|
| 0x004cc020 | CParticleSet__CreateByType | ~2000 bytes | Factory method - creates particle set by type ID (1-13) |
| 0x004cc850 | CParticleSet__Init | ~40 bytes | Base class initialization - sets vtable and clears fields |
| 0x004cd290 | CParticleSet__InitType11 | ~64 bytes | Type 11 particle set constructor |
| 0x004cd2d0 | CParticleSet__InitType12 | ~48 bytes | Type 12 particle set constructor |
| 0x004cd3c0 | CParticleSet__InitType13 | ~260 bytes | Type 13 particle set constructor (largest, most fields) |
| 0x004cd7f0 | CParticleSet__LoadFromArchive | ~624 bytes | Loads particle sets from tokenized archive format |
| 0x004cda60 | CParticleSet__LoadParticleSetFile | ~352 bytes | High-level loader - selects .par file and triggers load |

**Total: 7 functions**

## Particle Set Types

The factory method `CreateByType` supports 13 particle set types with different allocation sizes:

| Type ID | Alloc Size | Vtable | Notes |
|---------|------------|--------|-------|
| 1 | 0xD0 (208) | PTR_FUN_005ddf60 | Standard particles |
| 2 | 0xB4 (180) | PTR_FUN_005ddef8 | Velocity-based particles |
| 3 | 0x5C (92) | PTR_FUN_005dde90 | Minimal particle set |
| 4 | 0x7C (124) | PTR_FUN_005dde28 | With 4-element array |
| 5 | 0xB0 (176) | PTR_FUN_005dddc0 | RGB color particles |
| 6 | 0xD8 (216) | PTR_FUN_005ddd58 | Array-based (10 elements) |
| 7 | 0x84 (132) | PTR_FUN_005ddcf0 | Timed particles |
| 8 | 0xD0 (208) | PTR_FUN_005ddc88 | Complex with scale |
| 9 | 0x7C (124) | PTR_FUN_005ddc20 | Simple clearing type |
| 10 | 0x94 (148) | PTR_FUN_005ddbb8 | Position-based |
| 11 | 0x7C (124) | PTR_FUN_005ddb3c | Via InitType11 helper |
| 12 | 0x68 (104) | PTR_FUN_005ddfc8 | Via InitType12 helper |
| 13 | 0xE4 (228) | PTR_FUN_005de030 | Via InitType13 helper (largest) |

## Key Constants (Float Hex Values)

Common float constants found in initialization:
- `0x3f800000` = 1.0f
- `0x3f000000` = 0.5f
- `0x41200000` = 10.0f
- `0x41a00000` = 20.0f
- `0x40a00000` = 5.0f
- `0x43340000` = 180.0f
- `0x43b40000` = 360.0f
- `0xbdcccccd` = -0.1f
- `0x3dcccccd` = 0.1f

## CParticleSet Base Class Layout

Based on common initialization patterns:

| Offset | Size | Field | Notes |
|--------|------|-------|-------|
| 0x00 | 4 | vtable | Virtual function table pointer |
| 0x04 | 0x31 | name | Particle set name (strncpy, null-terminated at +0x35) |
| 0x38 | 4 | next | Linked list pointer to next particle set |
| 0x3C | 4 | [field_0xf] | Cleared during init |
| 0x40 | 4 | [field_0x10] | Cleared during init |
| 0x48 | 4 | [field_0x12] | Cleared during init |
| 0x50 | 4 | [field_0x14] | Cleared during init |
| 0x54 | 4 | [field_0x15] | Cleared during init |
| 0x5C+ | varies | type-specific | Type-specific particle parameters |

## Global Variables

| Address | Type | Name | Purpose |
|---------|------|------|---------|
| 0x0082b450 | CParticleSet* | g_pLastParticleSet | Most recently created/accessed particle set |
| 0x0082b3f8 | int* | g_pParticleSetListPtr | Pointer into particle set linked list |

## Loading Process

1. `LoadParticleSetFile(mode)` is called with mode:
   - 0 = Load MainSet.par
   - 1 = Load Frontend.par
   - 2 = Load MainSet.par (alternate path)

2. Allocates 200-byte filename buffer

3. Opens file via archive system (`FUN_0048ddd0`)

4. Calls `LoadFromArchive` which:
   - Destroys existing particle sets via vtable destructor calls
   - Allocates 0x1388C (80,012) bytes for particle data pool
   - Parses tokenized archive format (tokens 0-4 for structure)
   - For each particle set entry:
     - Allocates 1000-byte name buffer
     - Reads name and type from archive
     - Calls `CreateByType` to instantiate
     - Calls virtual method at vtable+0x18 to complete loading

## Exception Handlers

13 Unwind handlers at 0x005d41xx reference this source file for structured exception handling cleanup during particle set operations.

## Key Observations

1. **Factory Pattern**: Single `CreateByType` function handles all 13 particle types via switch statement, each with unique vtable and struct size.

2. **Linked List Management**: Particle sets form a linked list (next pointer at offset 0x38), managed via global pointers.

3. **Name Storage**: Each particle set stores its name at offset 0x04, max 49 chars (0x31) plus null terminator.

4. **Memory Pools**: Loading allocates large pools (80KB for particle data, 1KB per name) suggesting pre-allocation strategy.

5. **Two-Phase Init**: Types 11-13 use separate init functions rather than inline initialization in the switch.

6. **Archive Format**: Uses tokenized archive with 5 token types (0-4) for structured particle set data.

---
*Discovered via Phase 1 xref analysis (Dec 2025)*
