# mesh.cpp Function Mappings

> Functions from mesh.cpp mapped to BEA.exe binary
> Debug path: C:\dev\ONSLAUGHT2\mesh.cpp (at 0x0062f8e8)

## Overview
- **Functions Mapped:** 15
- **Status:** NEW (Dec 2025)
- **Classes:** CMesh

## Function List

| Address | Name | Status | Description |
|---------|------|--------|-------------|
| 0x004a5020 | CMesh__Init | NAMED | Initialize mesh instance, allocate resources, link to global mesh list |
| 0x004a5200 | CMesh__InitStatic | NAMED | Static initialization, loads default texture (meshtex\default.tga) |
| 0x004a5b70 | CMesh__Load | NAMED | Large mesh loading function (~18KB), handles file format parsing and validation |
| 0x004aa6e0 | CMesh__FindOrCreate | NAMED | Find existing mesh by name or create new one, increments refcount |
| 0x004aab90 | CMesh__Deserialize | NAMED | Deserialize mesh from binary stream, loads from AYA archive |
| 0x004ab360 | CMesh__OptimizeParts | NAMED | Optimize mesh parts by merging compatible parts, removes redundant parts |
| 0x004a52b0 | CMesh__ClearAllUsageMarkers | NAMED | Clears usage-marker flags across mesh usage arrays/tables |
| 0x004a5430 | CMesh__FreeUnusedAndReportLeaks | NAMED | Frees currently unused resources and emits leak/report diagnostics |
| 0x004aa410 | CMesh__FindTextureByNameSuffixHint | NAMED | Resolves texture entry using suffix-hint matching |
| 0x004aa5a0 | CMesh__GetPartField40ByFlatIndex | NAMED | Returns part field `+0x40` via flattened part index lookup |
| 0x004aa5e0 | CMesh__FindEntryByInclusiveRangeTable | NAMED | Resolves entry by inclusive range-table traversal |
| 0x004aa7e0 | CMesh__FindEntryValueByTypeId | NAMED | Resolves typed entry value from mesh lookup tables |
| 0x004aa900 | CMesh__CreatePolyBucketsForAllParts | NAMED | Builds polygon bucket structures across all mesh parts |
| 0x004ab330 | CMesh__FindByRuntimeId | NAMED | Finds mesh entry by runtime id/key |

## Function Details

### CMesh__Init (0x004a5020)
- **Calling Convention:** thiscall (ECX = this)
- **Purpose:** Initialize a CMesh instance
- **Key Operations:**
  - Zeroes out mesh fields (positions, counts, pointers)
  - Sets default LOD value (0x3f000000 = 0.5f)
  - Allocates internal resource buffer (0x28 bytes)
  - Links mesh to global mesh list via DAT_00704ad8

### CMesh__InitStatic (0x004a5200)
- **Purpose:** One-time static initialization for mesh system
- **Key Operations:**
  - Cleans up any existing default mesh data
  - Allocates new mesh texture storage
  - Loads "meshtex\default.tga" as fallback texture
- **Global State:** Uses DAT_00704adc for default mesh texture

### CMesh__Load (0x004a5b70)
- **Purpose:** Main mesh loading function from file/stream
- **Size:** ~18KB of code (largest mesh function)
- **Key Features:**
  - Validates mesh file format magic numbers
  - Supports multiple mesh format versions
  - Handles mesh parts, emitters, textures, and bones
  - Contains 27 debug assertions referencing mesh.cpp
- **Note:** This function timed out during decompilation due to size

### CMesh__FindOrCreate (0x004aa6e0)
- **Purpose:** Mesh resource manager - find cached or create new
- **Parameters:**
  - param_1: Mesh name string
  - param_2: Resource context
- **Key Operations:**
  - Iterates global mesh list (DAT_00704ad8) searching by name
  - If found, increments reference count at offset 0x170
  - If not found, allocates new mesh (0x174 bytes) and loads it
  - Logs warning "Mesh '%s' not found in level resource file" if not in level resources

### CMesh__Deserialize (0x004aab90)
- **Purpose:** Load mesh from serialized binary data
- **Key Operations:**
  - Reads mesh name (300 char buffer)
  - Opens AYA archive from "data\resources\meshes\m_%s.aya"
  - Allocates arrays for mesh parts, emitters, materials
  - Tracks total emitter memory usage (DAT_00704ae8)
  - Supports recursive mesh loading for chained meshes
- **Debug Strings:**
  - "Skipping deserialisation of mesh %s as it is unnecessary"
  - "%dK total in emitters so far"

### CMesh__OptimizeParts (0x004ab360)
- **Purpose:** Runtime mesh optimization
- **Calling Convention:** thiscall (ECX = this)
- **Key Operations:**
  - Iterates all mesh parts looking for merge candidates
  - Parts must have compatible properties (same type, single vertex buffer)
  - Transforms vertices when merging parts with different local transforms
  - Removes redundant intermediate parts
  - Tracks statistics in DAT_00704af0 (total parts) and DAT_00704af4 (removed parts)
- **Debug Strings:**
  - "Optimising mesh %s parts"
  - "Removing part %s"
  - "OptimiseParts : removed %d of %d"
  - Checks for "Nexus" parts (excluded from merging)

## CMesh Structure (Partial)

Based on function analysis:

| Offset | Type | Name | Notes |
|--------|------|------|-------|
| 0x00 | ptr | pMaterials | Material array pointer |
| 0x04 | int | materialCount | Number of materials |
| 0x14 | ptr | pVertices | Vertex buffer pointer |
| 0x18 | ptr | pIndices | Index buffer pointer |
| 0x1C | int | numEmitters | Emitter count |
| 0x20 | ptr | pEmitters | Emitter array pointer |
| 0x24 | char[300] | name | Mesh name string |
| 0x150 | ptr | pTextureList | Texture list pointer |
| 0x154 | int | unknown | |
| 0x158 | ptr | pNextMesh | Next mesh in global list |
| 0x15C | int | numParts | Number of mesh parts |
| 0x160 | ptr* | pParts | Array of part pointers |
| 0x164 | float | lodDistance | LOD distance threshold |
| 0x168 | int | flags | Mesh flags |
| 0x170 | int | refCount | Reference counter |
| 0x174 | | | Struct size = 0x174 bytes |

## Global Variables

| Address | Type | Name | Purpose |
|---------|------|------|---------|
| 0x00704ad8 | CMesh* | g_pMeshList | Head of global mesh linked list |
| 0x00704adc | void* | g_pDefaultMeshTex | Default mesh texture data |
| 0x00704ae0 | int | g_bMeshDebugLog | Enable mesh debug logging |
| 0x00704ae4 | char | g_bMeshArchiveOpen | Flag: AYA archive currently open |
| 0x00704ae8 | int | g_nEmitterMemory | Total emitter memory allocated |
| 0x00704af0 | int | g_nTotalParts | Total mesh parts (pre-optimize) |
| 0x00704af4 | int | g_nRemovedParts | Parts removed by optimization |

## Cross-References

The mesh.cpp debug string at 0x0062f8e8 has 54 total cross-references:
- 6 main functions (documented above)
- 48 Unwind exception handlers (compiler-generated cleanup code)

## Related Strings

| Address | String | Usage |
|---------|--------|-------|
| 0x0062f8d4 | "unknown mesh name" | Default name for unnamed meshes |
| 0x0062f904 | "No mesh resource leaks!" | Shutdown validation message |
| 0x0062f938 | "Mesh '%s' leaked : refcount=%d" | Memory leak warning |
| 0x0062fa00 | "Mesh end-of-level resource leaks" | Level cleanup validation |
| 0x0062fadc | "data\Meshes\" | Mesh file path prefix |
| 0x0062fb28 | "Meshes/%s/Emitters" | Emitter data path |
| 0x0062fb5c | "Error loading chained mesh!" | Chain loading failure |
| 0x0062fc1c | "meshtex\%s" | Mesh texture path format |
| 0x0062fc80 | "Mesh '%s' not found in level resource file" | Missing resource warning |
| 0x0062fd28 | "data\resources\meshes\m_%s.aya" | AYA archive path format |

## Related
- Debug Path: `C:\dev\ONSLAUGHT2\mesh.cpp`
- Parent: [../README.md](../README.md)
