# chunker.cpp - CChunker System Analysis

**Source File**: `C:\dev\ONSLAUGHT2\chunker.cpp`
**Debug String Address**: `0x00624464`
**Analysis Date**: December 2025

## Overview

CChunker is a utility class used throughout the Battle Engine Aquila codebase for chunked resource loading. It appears to be a buffer management system that handles reading data in chunks from files or archives.

## Functions Found: 3

| Address | Name | Signature | Line |
|---------|------|-----------|------|
| `0x004237d0` | `CChunker__Create` | `CChunker* __thiscall Create()` | 98 (0x62) |
| `0x00547d70` | `CChunker__CChunker` | `void __thiscall CChunker()` | - |
| `0x00547d90` | `CChunker__Destructor` | `void __thiscall ~CChunker()` | - |

## Headless Semantic Wave105 Promotions (2026-02-26)

These helpers are chunker-stream utilities used by multiple resource deserializers (`CMesh__Deserialize`, `CWorld__DeserializeWorld`, `CCutscene__Load`, `CDXTexture__CreateMipmaps`, and `CResourceAccumulator__ReadResourceFile`).

| Address | Name | Behavior |
|---------|------|----------|
| `0x00423840` | `CChunkerStream__DestroyOwnedChunkerIfPresent` | If stream owns a chunker object, calls `CChunker__Destructor`, frees it, and clears the owner pointer. |
| `0x00423900` | `CChunkerStream__CloseDXMemBuffer_Status0OrMinus1` | Wraps `DXMemBuffer__Close` and normalizes return code to `0` / `-1`. |
| `0x00423990` | `CChunkerStream__SkipRemainingChunkBytes` | Advances stream cursor to chunk end by skipping `chunk_size - consumed_bytes`. |
| `0x004238c0` | `CChunkerStream__OpenReadAndGetChunker` | Initializes stream counters and opens DX memory-buffer read context; returns chunker pointer on success. |

## Function Details

### CChunker__Create (0x004237d0)

Factory method that creates and initializes a new CChunker object.

**Pseudocode**:
```cpp
CChunker* CChunker::Create() {
    void* mem = OID_AllocObject(0x134, 0x11, "chunker.cpp", 98);
    if (mem) {
        CChunker* chunker = new(mem) CChunker();
        this->pChunker = chunker;
    } else {
        this->pChunker = NULL;
    }
    this->field_0xC = 1;
    return this;
}
```

**Called By**:
- `CCutscene__Load` (0x0043ed80)
- `CMesh__Deserialize` (0x004aab90)
- `CResourceAccumulator__ReadResourceFile` (0x004d7200)
- Various other resource loading functions

### CChunker__CChunker (0x00547d70)

Default constructor that initializes member fields to zero.

**Pseudocode**:
```cpp
CChunker::CChunker() {
    this->field_04 = 0;
    this->field_0C = 0;
    this->field_10 = 0;
    this->field_14 = 0;
}
```

**Called By**: 20+ locations throughout the codebase, typically via `CChunker__Create` or direct allocation in various loader classes.

### CChunker__Destructor (0x00547d90)

Destructor that frees allocated memory buffers.

**Pseudocode**:
```cpp
CChunker::~CChunker() {
    FreeMemory(this->field_04);
    FreeMemory(this->field_0C);
}
```

**Called By**: 51+ locations (destructor is heavily used for cleanup)

## CChunker Object Layout

**Total Size**: 0x134 bytes (308 bytes)

| Offset | Size | Type | Name | Description |
|--------|------|------|------|-------------|
| `+0x00` | 4 | void* | (unknown) | Base pointer or vtable |
| `+0x04` | 4 | void* | pBuffer1 | Primary data buffer (freed in destructor) |
| `+0x08` | 4 | (unknown) | - | Unknown |
| `+0x0C` | 4 | void* | pBuffer2 | Secondary buffer (freed in destructor) |
| `+0x10` | 4 | int | field_10 | Initialized to 0 |
| `+0x14` | 4 | int | field_14 | Initialized to 0 |
| ... | ... | ... | ... | Remaining fields unknown |

## Memory Allocation

CChunker objects are allocated through the engine's memory management system:

```cpp
OID__AllocObject(size=0x134, category=0x11, file="chunker.cpp", line=98)
    -> CMemoryManager__Alloc(...)
```

The category `0x11` (17 decimal) likely represents a specific memory pool for resource loading buffers.

## Usage Pattern

CChunker is typically used in the following pattern:

1. **Create**: Allocate and initialize via `CChunker__Create`
2. **Use**: Load/process data through the chunker (methods not yet identified)
3. **Destroy**: Clean up via `CChunker__Destructor`

The class is used extensively for:
- Mesh loading (`CMesh__Deserialize`)
- Texture loading (`CTGALoader__Load`)
- Sound loading (`CSoundManager__LoadSoundDefinitions`)
- Particle set loading (`CParticleSet__LoadParticleSetFile`)
- Cutscene loading (`CCutscene__Load`)
- Sprite loading (`CByteSprite__Load`)
- Text/font loading (`CText__Init`)
- Generic resource loading (`CResourceAccumulator__ReadResourceFile`)

## Related Classes

- **DXMemBuffer** (`0x00547dc0`): Similar buffer class for DirectX-specific memory operations, distinct from CChunker despite similar constructor pattern.

## Notes

1. Only 2 debug string references exist for chunker.cpp, suggesting minimal ASSERT/debug macros in this file
2. The constructor and destructor are generic enough to be called by many different systems
3. Line 98 corresponds to the allocation in `CChunker__Create`, likely inside an `ASSERT` or `MONITOR_ALLOC` macro

## Cross-References Summary

| Function | Xrefs To | Xrefs From |
|----------|----------|------------|
| `CChunker__Create` | 4 callers | Memory allocator |
| `CChunker__CChunker` | 20+ callers | None |
| `CChunker__Destructor` | 51+ callers | Memory free function |
