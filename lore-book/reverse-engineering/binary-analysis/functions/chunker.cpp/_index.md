# chunker.cpp - Chunk Reader System Analysis

**Source File**: `[maintainer-local-source-export-root]\chunker.cpp`
**Debug String Address**: `0x00624464`
**Last updated**: 2026-05-10

> **Queue status (2026-05-31):** Ghidra export-contract closure **6222/6222** (Wave983: every currently exported function object commented with clean-signature proxy; not evidence-grade semantics). Lines below that reference a "next raw commentless" row are **archival wave progress**, not open work.

## Overview

`chunker.cpp` contains the source-backed `CChunkReader` helpers used by resource deserializers to read tagged chunks from a `CMEMBUFFER` / `CDXMemBuffer` file buffer. Wave 319 supersedes older labels that treated these bodies as generic `CChunker`, `CChunkerStream`, `CMeshPart`, or `CResourceAccumulator` functions.

The current saved Ghidra names are reader-focused:

- `CChunkReader__ctor` allocates and owns a backing `CDXMemBuffer`-style object.
- `CChunkReader__OpenExistingBuffer` binds an existing `CMEMBUFFER`.
- `CChunkReader__OpenFile` initializes the owned `CDXMemBuffer` from a filename.
- `CChunkReader__GetNext`, `Read`, and `Skip` implement the shared chunk-id/size and payload cursor behavior used by many loaders.

Wave983 (`cchunkreader-resource-review-wave983`) re-reviewed these rows against fresh metadata/tags/xrefs/instructions/decompile and source context, saved Wave983 comments/tags, verified signatures, and normalized stale docs that still used `CChunkerStream__...`, `FUN_00423910`, `FUN_00423960`, or `memcpy_wrapper` wording. Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260531-001624_post_wave983_cchunkreader_resource_review_verified`. Static closure remains `6222/6222 = 100.00%`; Wave911 focused progress is `384/1408 = 27.27%`; expanded static surface progress is `443/1478 = 29.97%`. Exact `CChunkReader` structure layout, runtime archive/resource I/O behavior, exact archive schema coverage, BEA patching, and rebuild parity remain unproven. The next slice is a Wave900+ recheck before a new candidate cluster.

## Functions Found

| Address | Current name | Current signature | Boundary |
|---------|--------------|-------------------|----------|
| `0x004237d0` | `CChunkReader__ctor` | `void * __fastcall CChunkReader__ctor(void * this)` | Allocates a `0x134`-byte `CDXMemBuffer` / `CMEMBUFFER`, stores it at `+0x4`, sets `mOwnFile`, and returns `this`. |
| `0x00423840` | `CChunkReader__dtor_base` | `void __fastcall CChunkReader__dtor_base(void * this)` | Frees the owned file buffer when `mOwnFile` and `File` are set. |
| `0x00423870` | `CChunkReader__OpenExistingBuffer` | `void * __thiscall CChunkReader__OpenExistingBuffer(void * this, void * existingBuffer)` | Source-parity `Open(CMEMBUFFER*)`: resets counters, drops owned buffer if needed, stores the provided buffer, and marks ownership false. |
| `0x004238c0` | `CChunkReader__OpenFile` | `void * __thiscall CChunkReader__OpenFile(void * this, char * filename)` | Source-parity `Open(char*)`: resets counters and calls `CDXMemBuffer__InitFromFile`. |
| `0x00423900` | `CChunkReader__Close` | `int __fastcall CChunkReader__Close(void * this)` | Wraps the file-buffer close and returns `0` or `-1`. |
| `0x00423910` | `CChunkReader__GetNext` | `uint __fastcall CChunkReader__GetNext(void * this)` | Reads a 4-byte chunk id and 4-byte chunk size, then resets `ReadSinceChunk`. |
| `0x00423960` | `CChunkReader__Read` | `bool __thiscall CChunkReader__Read(void * this, void * outBuffer, int size, int count)` | Reads `size * count` bytes through `CDXMemBuffer__Read` and accumulates `ReadSinceChunk`. |
| `0x00423990` | `CChunkReader__Skip` | `int __fastcall CChunkReader__Skip(void * this)` | Skips `Size - ReadSinceChunk` bytes through `CDXMemBuffer__Skip`. |

## Superseded Labels

Wave 319 explicitly replaces these older saved labels:

| Address | Superseded label | Current label |
|---------|------------------|---------------|
| `0x004237d0` | `CChunker__Create` | `CChunkReader__ctor` |
| `0x00423840` | `CChunkerStream__DestroyOwnedChunkerIfPresent` | `CChunkReader__dtor_base` |
| `0x00423870` | `CResourceAccumulator__ResetChunkerSlotAndAssignSource` | `CChunkReader__OpenExistingBuffer` |
| `0x004238c0` | `CChunkerStream__OpenReadAndGetChunker` | `CChunkReader__OpenFile` |
| `0x00423900` | `CChunkerStream__CloseDXMemBuffer_Status0OrMinus1` | `CChunkReader__Close` |
| `0x00423910` | `CMeshPart__ReadHeaderPairAndResetByteCount` | `CChunkReader__GetNext` |
| `0x00423960` | `CMeshPart__ReadBlockAndAccumulateByteCount` | `CChunkReader__Read` |
| `0x00423990` | `CChunkerStream__SkipRemainingChunkBytes` | `CChunkReader__Skip` |

The `0x00547d70` and `0x00547d90` bodies previously described here as `CChunker` constructor/destructor are now corrected to `CDXMemBuffer__ctor` and `CDXMemBuffer__dtor_base`; see [`DXMemBuffer.cpp.md`](../DXMemBuffer.cpp.md).

## Usage Pattern

Resource loaders generally follow this pattern:

1. Construct a `CChunkReader`.
2. Bind it to an existing `CMEMBUFFER` or open a filename-backed `CDXMemBuffer`.
3. Loop through `GetNext`, `Read`, and `Skip` while processing chunk payloads.
4. Close or destruct the reader, freeing owned file-buffer state when applicable.

Known consumers include mesh, texture, cutscene, byte-sprite, text/font, sound-definition, particle-set, world, and generic resource loading paths. This document records static source/read-back evidence only; it does not prove runtime archive coverage or exact loader behavior.

## Exception Handlers

Wave745 saved static Ghidra comments/tags/signatures for the chunker/resource portion of the `unwind-continuation-wave745` tranche:

| Address | Name | Evidence boundary |
|---------|------|-------------------|
| `0x005d1940` | `Unwind@005d1940` | DATA scope-table xref `0x0061a7a4`; calls `OID__FreeObject_Callback` on `EBP-0x10` with chunker.cpp debug path `0x00624464`, line `0x62`, memtype `0x11`. |
| `0x005d1960` | `Unwind@005d1960` | DATA scope-table xref `0x0061a7cc`; calls `CMonitor__Shutdown` on the large stack-local pointer at `EBP-0x468`. |
| `0x005d196b` | `Unwind@005d196b` | DATA scope-table xref `0x0061a7d4`; calls the descriptor-table cleanup thunk now saved by Wave982 as `CResourceDescriptorTable__DestroyEmbeddedDescriptor_Thunk` on stack local `EBP-0x434`. The older `CDXLandscape__DestroyResourceDescriptorArray_Thunk` wording is historical. |
| `0x005d1980` | `Unwind@005d1980` | DATA scope-table xref `0x0061a7fc`; calls `CMonitor__Shutdown` on `EBP-0x10`. |
| `0x005d19a0` | `Unwind@005d19a0` | DATA scope-table xref `0x0061a824`; calls `CMonitor__Shutdown` on `EBP-0x10`. |
| `0x005d19c0` | `Unwind@005d19c0` | DATA scope-table xref `0x0061a84c`; calls `CLine__SetBaseVtable_00426360` on stack local `EBP-0x40`. |

The full Wave745 tranche spans `0x005d1840 Unwind@005d1840` through `0x005d1a98 Unwind@005d1a98`, leaves raw commentless head `0x0042f220 CSPtrSet__Clear`, moves the high-signal head to `0x005d1aa3 Unwind@005d1aa3`, and has verified backup `[maintainer-local-ghidra-backup-root]\BEA_20260522-170426_post_wave745_unwind_continuation_verified`. Exact parent source-body identity, runtime exception behavior, runtime cleanup behavior, BEA patching, and rebuild parity remain unproven.
