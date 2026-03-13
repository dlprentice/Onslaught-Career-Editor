# TokenArchive.cpp - Function Analysis

**Source file:** `C:\dev\ONSLAUGHT2\TokenArchive.cpp`
**Analysis date:** December 2025
**Functions found:** 8

## Overview

TokenArchive is a serialization system for reading and writing tokenized data archives. In BEA, this is specifically used for **particle system configuration files** (`.ptc` or similar). The system uses a token-based format where each data field is identified by a string token name followed by its value.

The format appears to be: `TokenName Value` pairs, parsed line-by-line or whitespace-separated.

## Token Types

The system supports 124 (0x7C) different token types, primarily for particle system parameters:

| Range | Category | Examples |
|-------|----------|----------|
| 0-5 | File header | `ParticleSystemEd_File`, `File_Version`, `Num_Particle_Descriptors` |
| 6-27 | Basic particle params | `Radius`, `Gravity`, `Bounce`, `Texture`, `Blend_Mode` |
| 28-44 | Velocity/emission | `Initial_Velocity_X/Y/Z`, `Emit_Per_Turn`, `Particle_Descriptor` |
| 45-48 | Probability | `Probability_0` through `Probability_3` |
| 49-57 | Color | `Start_Red/Green/Blue`, `End_Red/Green/Blue`, `Transition_*` |
| 58-67 | Shape/geometry | `Ring_Axis`, `Hemisphere`, `Num_Particles`, `Hollow` |
| 68-81 | Trail/ribbon | `Width`, `Num_Points`, `Wiggle_Factor`, `Disperse_Rate` |
| 82-95 | Animation/function | `Yaw_Function`, `Pitch_Function`, `Param_A/B/C/D` |
| 96-111 | Cylinder params | `Cylinder_NumPtsAxial`, `Cylinder_Radius`, `Cylinder_Length` |
| 112-123 | Sphere params | `Sphere_NumPtsAx`, `Sphere_Latitude_Start/End`, `Sphere_Longitude_*` |

## Functions

### CTokenArchive__GetTokenName
| Property | Value |
|----------|-------|
| Address | `0x004f52b0` |
| Returns | `char*` (token name string) |
| Parameters | `int tokenId` |
| Calling Convention | cdecl |

Converts a token ID (0-123) to its string name. Returns `"**Unknown Token**"` for invalid IDs.

**Token examples:**
- 0 = `"ParticleSystemEd_File  C 2000 Lo"` (file header)
- 1 = `"File_Version"`
- 6 = `"Radius"`
- 8 = `"Gravity"`
- 0x31 = `"Start_Red"`

---

### CTokenArchive__ReadNextToken
| Property | Value |
|----------|-------|
| Address | `0x004f57b0` |
| Returns | `int` (1 = success, 0 = failure) |
| Parameters | `int* outTokenId, float* outFloat, float* outFloat2, char* outString` |
| Calling Convention | thiscall (ECX = this) |
| Line refs | 0x138 (312), 0x16a (362) |

Main token parsing function. Reads from internal buffer, parses token name and value(s).

**Behavior by token type:**
- **Cases 0, 5**: Header tokens - no value parsing needed
- **Cases 1, 7, 0x13, etc.**: Float tokens - parse single float into `outFloat2`
- **Cases 2, 3, 8, 9, etc.**: Integer tokens - parse into `outFloat`
- **Cases 4, 0xb, 0x65**: String tokens - copy string to `outString`
- **Cases 6, 0x18, 0x1a, etc.**: Float + string reference - allocates memory for string storage
- **Cases 0xc, 0x10, 0x1c, etc.**: String reference - stores in internal pointer array

Uses sscanf with format `"%s %s"` to parse token/value pairs.

Special handling for color values (tokens 0x31-0x39): multiplies by `0.003921569` (1/255) to normalize 0-255 to 0.0-1.0.

---

### CTokenArchive__ResolveReferences
| Property | Value |
|----------|-------|
| Address | `0x004f5ba0` |
| Returns | `void` |
| Parameters | `int** linkedList` |
| Calling Convention | thiscall (ECX = this) |
| Line refs | 0x1c2 (450) |

Post-parsing phase that resolves string references to object pointers.

**Algorithm:**
1. Count items in linked list (follows offset +0x38 for next pointer)
2. Allocate array of pointers
3. For each stored string reference, use bsearch to find matching object
4. Replace string with object pointer (or NULL if not found)
5. Free temporary string allocations
6. Reset reference counter to 0

---

### CTokenArchive__WriteInt
| Property | Value |
|----------|-------|
| Address | `0x004f5c90` |
| Returns | `void` |
| Parameters | `int tokenId, int value` |
| Calling Convention | cdecl |

Writes an integer token to output buffer using format `"%s %d"`.

---

### CTokenArchive__WriteFloat
| Property | Value |
|----------|-------|
| Address | `0x004f5cd0` |
| Returns | `void` |
| Parameters | `int tokenId, float value` |
| Calling Convention | cdecl |

Writes a float token to output buffer using format `"%s %f"`.

---

### CTokenArchive__WriteString
| Property | Value |
|----------|-------|
| Address | `0x004f5d10` |
| Returns | `void` |
| Parameters | `int tokenId, char* value` |
| Calling Convention | cdecl |

Writes a string token to output buffer using format `"%s %s"`.

---

### CTokenArchive__WritePointer
| Property | Value |
|----------|-------|
| Address | `0x004f5d50` |
| Returns | `void` |
| Parameters | `int tokenId, void* ptr` |
| Calling Convention | cdecl |

Writes a pointer reference token. If pointer is NULL, writes `"%s NONE"`, otherwise writes the object's name (at ptr+4) using format `"%s %s"`.

---

### CTokenArchive__WriteFloatPointer
| Property | Value |
|----------|-------|
| Address | `0x004f5dc0` |
| Returns | `void` |
| Parameters | `int tokenId, float* data` |
| Calling Convention | cdecl |

Writes a float value with an associated pointer reference. data[0] is the float, data[1] is treated as a pointer.
- If pointer is NULL: format `"%s %f NONE"`
- If pointer is valid: format `"%s %f %s"` (with object name)

## CTokenArchive Class Layout (Partial)

Based on decompilation analysis:

| Offset | Type | Field | Notes |
|--------|------|-------|-------|
| +0x00 | void* | vtable? | |
| +0x08 | int | mNumStrings | Count of stored string references |
| +0x9C4C | char*[] | mStrings | Array of allocated string pointers (up to ~10000) |

## Related Systems

- **ParticleDescriptor.cpp** - Uses TokenArchive for particle type definitions
- **ParticleSet.cpp** - Uses TokenArchive for particle system configurations
- **ParticleManager.cpp** - Manages loading/saving of particle archives

## Format Strings Used

| Address | Format | Usage |
|---------|--------|-------|
| 0x00625274 | `"%s %s"` | Token/value parsing |
| 0x00633a24 | `"%f"` | Float value scanning |
| 0x00625098 | `"%f"` | Float value scanning (alternate) |
| 0x00633a28 | `"%s %d"` | Integer output |
| 0x00633a30 | `"%s %f"` | Float output |
| 0x00633a38 | `"%s %s"` | String output |
| 0x00633a40 | `"%s NONE"` | Null pointer output |
| 0x00633a4c | `"%s %f NONE"` | Float with null pointer |
| 0x00633a5c | `"%s %f %s"` | Float with pointer reference |

## Memory Allocation

Uses custom allocator `OID__AllocObject` (likely `operator new` or memory pool) with parameters:
- Size in bytes
- Allocation type/tag (0x61, 0x80)
- Source file path
- Line number

Corresponding free function: `OID__FreeObject`
