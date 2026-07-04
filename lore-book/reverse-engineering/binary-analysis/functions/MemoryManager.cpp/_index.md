# MemoryManager.cpp Functions

> Source File: MemoryManager.cpp | Binary: BEA.exe
> Debug Path: 0x0062f590

## Overview

> **Queue status (2026-05-26):** Ghidra export-contract closure **6113/6113** (Wave900: every function commented; clean-signature proxy; not evidence-grade semantics). Lines below that reference a "next raw commentless" row are **archival wave progress**, not open work.

Core memory management system. `CMemoryHeap` owns heap internals and allocator/statistics helpers, `CMemoryManager` coordinates global heap-list dump/base-set/tag-list behavior, and `CDXMemoryManager` wraps the four PC retail heaps exposed to the broader engine. Wave438 and Wave439 corrected the `0x004a1390` through `0x004a2ff0` cluster away from stale generic `CMemoryManager` / `CDXEngine` labels toward source-parity heap, block, manager, and DX wrapper owners. Wave607 corrected the adjacent `0x00548ec0` through `0x00549400` cluster from stale landscape/OID/PolyBucket labels into CDXMemoryManager core allocation/lifecycle plus CMemoryManager tag-list cleanup. Wave812 corrected the stale `CLTShell__ValidateAndRollHeapDeltas` row to `CMemoryHeap__CalcAndShowDeltas`.

Wave909 engine/platform support static review (`engine-platform-support-static-review-wave909`) records the memory/allocator side of a static-coherent engine/platform/math/memory support core. Memory anchors include `CDXMemoryManager__Alloc` and `CMemoryHeap__Init`. Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260526-120420_post_wave909_engine_platform_support_static_review_verified`. Runtime allocator behavior and exact layouts remain separate proof.

## 2026-06-01 Wave1042 Memory Heap Allocator Review

Wave1042 static re-audit (`memory-heap-allocator-review-wave1042`) re-read eight source-backed `CMemoryHeap` allocator helpers originally corrected by Wave438 with no mutation. Fresh primary exports verified `8` metadata rows, `8` tag rows, `28` xref rows, `934` body-instruction rows, and `8` decompile rows; context exports verified `8` metadata rows, `8` tag rows, `2260` xref rows, `376` body-instruction rows, and `8` decompile rows.

The reviewed allocator rows remain coherent with Stuart `MemoryManager.cpp` source parity, heap-list anchor `DAT_009c3df0`, magic header `0x4f69ea21`, mutex slot `this+0x8bc`, tiny-heap range `this+0x8c0..0x8c8`, merge flag `this+0x874`, and CDX/global wrapper context including `0x00548f90 CDXMemoryManager__Init` and `0x005490e0 CDXMemoryManager__Alloc`. Reviewed anchors include `0x004a13b0 CMemoryHeap__Init`, `0x004a1810 CMemoryHeap__Alloc`, `0x004a1ca0 CMemoryHeap__Free`, and `0x004a1ea0 CMemoryHeap__SetMerge`.

Queue closure remains `6238/6238 = 100.00%`; Wave911 focused progress advances to `735/1408 = 52.20%`; expanded static surface progress advances to `968/1493 = 64.84%`; top-500 coverage remains `500/500 = 100.00%`. Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260601-094520_post_wave1042_memory_heap_allocator_review_verified`. Runtime allocator behavior, runtime out-of-memory behavior, complete concrete `CMemoryHeap` / `CMemoryBlock` / `CDXMemoryManager` layouts, exact memory-type enum/table identity, thread/mutex lifetime under runtime load, BEA patching, gameplay outcomes, and rebuild parity remain separate proof.

## 2026-05-25 Wave865 Render Tail Read-Back

Wave865 render tail static read-back (`render-tail-wave865`, `wave865-readback-verified`) hardened `0x00549310 CDXMemoryManager__LogDebugStats` as `void __thiscall CDXMemoryManager__LogDebugStats(void * this)`. `CLTShell__RunFrontEndAndGameLoop` and `CLTShell__RunStressTestLevelLoop` call this ECX-only memory debug logger on global `CDXMemoryManager` `0x009c3df0`; the body emits DebugTrace separators, calls `CMemoryHeap__LogStats` for heap subobjects at `this+0x214`, `this+0xae0`, and `this+0x13ac`, then formats default/thing heap peak and size lines. Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260525-160100_post_wave865_render_tail_verified`. Exact heap layout, debug-output completeness, runtime behavior, BEA patching, and rebuild parity remain deferred.

## Functions

| Address | Name | Purpose | Size |
|---------|------|---------|------|
| 0x004a1390 | CMemoryHeap__ctor | Initialize heap constructor state and create the retail heap mutex/HANDLE at `+0x8bc` | ~32 bytes |
| 0x004a13b0 | CMemoryHeap__Init | Initialize a heap, link it into the global heap list, seed the base free block, and optionally create the tiny heap | ~400 bytes |
| 0x004a1810 | CMemoryHeap__Alloc | Core mutex-guarded allocation path with tiny-heap, small-bucket, free-list, cleanup retry, OOM report, split/consume, and counter updates | ~500 bytes |
| 0x004a1ca0 | CMemoryHeap__Free | Free an allocated block, update counters, clear used/base-set flags, and reinsert through `CMemoryHeap__AddToFreeList` | ~100 bytes |
| 0x004a1c40 | CMemoryHeap__ReAlloc | Allocate replacement storage, copy `min(old_size, new_size)`, free the old block, and return the new allocation | ~100 bytes |
| 0x004a1c30 | CMemoryHeap__ReleaseMutexUnwindCleanup | Compiler EH cleanup helper that releases the mutex HANDLE stored through its argument | ~16 bytes |
| 0x004a1570 | CMemoryHeap__FreeTiny | Free a pointer in the 16-byte tiny heap range by pushing it onto the tiny free chain | ~48 bytes |
| 0x004a15a0 | CMemoryHeap__ReallocTiny | Reallocate a pointer that belongs to the 16-byte tiny heap free-chain range | ~100 bytes |
| 0x004a1d60 | CMemoryHeap__AddToFreeList | Return a free block to small buckets or the main free list, with optional adjacent-block coalescing | ~200 bytes |
| 0x004a1640 | CMemoryHeap__Cleanup | Rebuild free lists, coalesce adjacent free blocks, and optionally guard with the heap mutex | ~200 bytes |
| 0x004a1ea0 | CMemoryHeap__SetMerge | Enable/disable merge mode; when enabling, cleanup/coalesce then sort the main free list by block size | ~150 bytes |
| 0x004a1f60 | CMemoryHeap__OutputStats | Write per-heap memory statistics to `data\Memory\<filename>` through `CDXMemBuffer` | ~200 bytes |
| 0x004a2190 | CMemoryHeap__PrintStats | Draw per-heap statistics through the debug font path | ~300 bytes |
| 0x004a2460 | CMemoryHeap__LogStats | Print nonzero per-category heap statistics through the debug console/trace path | ~500 bytes |
| 0x004a25c0 | CMemoryHeap__CalcAndShowDeltas | Debug memory-delta trace helper that reports per-type counter deltas and rolls current counters into last-counter arrays | ~240 bytes |
| 0x004a2660 | CMemoryHeap__DumpMap | Serialize heap block-map data into the memory dump buffer | ~300 bytes |
| 0x004a2a20 | CMemoryManager__FlagAsBaseSet | Iterate heaps and mark allocated entries with the base-set debug bit (`| 2`) | ~96 bytes |
| 0x004a2a80 | CMemoryManager__DumpMemory | Build a numbered memory-dump file and ask each heap to append its block map | ~200 bytes |
| 0x004a2ff0 | CMemoryBlock__SetBaseSet | Set or clear the memory-block base-set flag bit | ~50 bytes |
| 0x00548d70 | CDXMemoryManager__ctor | Construct the DX memory manager wrapper, its heaps, and the 129 memory-type name slots | ~500 bytes |
| 0x00548ec0 | CMemoryManager__DeleteTagList_CtorUnwind | Constructor unwind/helper path that walks the CMemoryManager tag list and frees each tag | ~200 bytes |
| 0x00548f90 | CDXMemoryManager__Init | Global memory-manager heap bootstrap wrapper used from `CLTShell__WinMain` | ~300 bytes |
| 0x005490c0 | CDXMemoryManager__Shutdown | PC retail shutdown wrapper that clears `mInit` and tail-jumps to default heap shutdown | ~16 bytes |
| 0x005490e0 | CDXMemoryManager__Alloc | Global allocation fan-out dispatching by memory type to the selected heap and OOM code | ~200 bytes |
| 0x005491b0 | CDXMemoryManager__ReAlloc | Global reallocation fan-out using default/thing tiny realloc checks before type-heap realloc | ~100 bytes |
| 0x00549220 | CDXMemoryManager__Free | Free memory through `CMemoryHeap__FreeTiny` when possible, otherwise through `CMemoryHeap__Free` | ~64 bytes |
| 0x00549270 | MEM_MANAGER__Cleanup | Global cleanup wrapper used by load/restart paths (two coalesce passes) | ~16 bytes |
| 0x00549290 | CDXMemoryManager__PrintStats | Iterate heaps and dispatch `CMemoryHeap__PrintStats` with heap numbering | ~32 bytes |
| 0x005492b0 | CDXMemoryManager__OutputStats | Iterate heaps and dispatch `CMemoryHeap__OutputStats` for the supplied filename | ~32 bytes |
| 0x005492d0 | CDXMemoryManager__CalcAndShowDeltas | Debug memory-delta trace over default, dump, and thing heaps | ~300 bytes |
| 0x00549310 | CDXMemoryManager__LogDebugStats | Wave865 debug stats logger over CDX memory-manager heaps | read-back documented |
| 0x00549400 | CMemoryManager__DeleteTagList | Simple CMemoryManager tag-list delete helper reached from unwind metadata | ~200 bytes |

## Key Observations

- **Thread-safe** - Retail uses a mutex/HANDLE slot at offset 0x8bc in the reviewed heap methods
- **16-byte alignment** - All allocations aligned
- **Bucketed free lists** - 16 buckets for sizes < 256 bytes
- **Small block cache** - Fast path for < 16 bytes
- **Magic sentinel** - 0x4f69ea21 marks valid blocks
- **129 allocation categories** - Per-category statistics
- **OOM handling** - Prints "FATAL ERROR: Out of memory" and dumps report
- **Stats and dump split** - Per-heap stats live on `CMemoryHeap`; global dump orchestration lives on `CMemoryManager` / `CDXMemoryManager`
- **Global cleanup wrapper** - `MEM_MANAGER__Cleanup` provides the source-level `MEM_MANAGER.Cleanup()` call path through `CMemoryHeap__Cleanup`
- **Global init wrapper** - `CDXMemoryManager__Init` seeds default/dump/sound/thing heaps via `CMemoryHeap__Init` calls during shell startup
- **Global allocation wrapper** - `CDXMemoryManager__Alloc` is the high-fan-out allocator formerly misfiled as `OID__AllocObject`; OID, mesh, script, sound, and asset paths call through it.
- **Global reallocation wrapper** - `CDXMemoryManager__ReAlloc` is the allocator helper formerly misfiled as `CPolyBucket__ReallocFromPool`; PolyBucket/FlexArray callsites are callers, not owners.

## Wave438-439 Evidence

Wave438 saved name/signature/comment/tag corrections for ten allocator targets on 2026-05-16. Static retail decompile/xref evidence plus Stuart `references/Onslaught/MemoryManager.cpp` source parity supports the `CMemoryHeap` owner correction for `Init`, `ReallocTiny`, `Cleanup`, `Shutdown`, `Alloc`, `ReAlloc`, `Free`, `AddToFreeList`, and `SetMerge`. `0x004a1c30` is not a source-level heap method; it is the EH unwind cleanup helper that releases the allocator mutex.

Wave439 extended that correction through thirteen tail/wrapper targets. Static retail decompile/xref/string evidence plus Stuart source parity supports `CMemoryHeap__ctor`, `CMemoryHeap__FreeTiny`, `CMemoryHeap__OutputStats`, `CMemoryHeap__PrintStats`, `CMemoryHeap__LogStats`, `CMemoryHeap__DumpMap`, `CMemoryManager__FlagAsBaseSet`, `CMemoryManager__DumpMemory`, `CMemoryBlock__SetBaseSet`, `CDXMemoryManager__ctor`, `CDXMemoryManager__Free`, `CDXMemoryManager__PrintStats`, and `CDXMemoryManager__OutputStats`.

These waves are static evidence only. Runtime allocation/dump behavior, exact concrete `CMemoryHeap` / `CMemoryBlock` / `CDXMemoryManager` layouts beyond observed offsets, local variable names/types, exact Steam-vs-source mutex lifetime, adjacent destructor/tag-list cleanup ownership, and rebuild parity remain open.

## Wave607 CDXMemoryManager Core Evidence

Wave607 saved name/signature/comment/tag corrections for seven memory-manager core targets on 2026-05-19. Static retail decompile/xref/instruction evidence plus Stuart `references/Onslaught/DXMemoryManager.cpp` and `references/Onslaught/MemoryManager.*` source parity supports the owner correction.

| Address | Saved signature | Static behavior |
| --- | --- | --- |
| `0x00548ec0` | `void __thiscall CMemoryManager__DeleteTagList_CtorUnwind(void * this)` | Constructor EH/unwind tag-list cleanup path; walks `CMemoryManager::mFirstTag` at `this+0x4`, reads `CMemoryTag::mNext` at `+0x208`, and frees tags through the same memory-manager free path used by normal cleanup. |
| `0x00548f90` | `uint __thiscall CDXMemoryManager__Init(void * this, uint heap_size)` | `RET 0x4` and `CLTShell__WinMain` xref prove one stack `heap_size`; initializes default/dump/sound/thing heaps and memory-type heap routing. |
| `0x005490c0` | `void __thiscall CDXMemoryManager__Shutdown(void * this)` | Clears global `mInit` at `0x009c6334`, then tail-jumps to `CMemoryHeap__Shutdown` for the default heap at `this+0x214`. |
| `0x005490e0` | `void * __thiscall CDXMemoryManager__Alloc(void * this, uint size, int mem_type, char * source_file, uint line)` | High-fan-out global allocator; `RET 0x10`, 1384 xrefs, dispatch through `this+0x10 + mem_type*4`, and OOM codes `0xcd` through `0xd0` prove this is not OID-owned. |
| `0x005491b0` | `void * __thiscall CDXMemoryManager__ReAlloc(void * this, void * mem, uint new_size)` | Global realloc helper; tries default/thing tiny reallocs, then reads the memory type from the block header and dispatches to the selected heap. |
| `0x005492d0` | `void __thiscall CDXMemoryManager__CalcAndShowDeltas(void * this)` | Debug memory-delta trace over default, dump, and thing heaps; PC retail omits Xbox-only texture/VB heap delta calls present in source. |
| `0x00549400` | `void __thiscall CMemoryManager__DeleteTagList(void * this)` | Simple tag-list delete helper reached from memory-manager unwind metadata. |

Read-back evidence:

- `ApplyCDXMemoryManagerCoreWave607.java` dry/apply/final dry reported `updated=0 skipped=7 renamed=0 would_rename=6 missing=0 bad=0`, then `updated=7 skipped=0 renamed=6 would_rename=0 missing=0 bad=0`, then `updated=0 skipped=7 renamed=0 would_rename=0 missing=0 bad=0`, with `REPORT: Save succeeded`.
- Post exports verified `7` metadata rows, `7` tag rows, `1402` xref rows, `2695` instruction rows, and `7` decompile rows.
- Queue refresh after Wave607 reports `6093` total functions, `3116` commented, `2977` commentless, `1304` exact-undefined signatures, and `1065` `param_N` signatures. Strict clean-signature proxy is `3071/6093 = 50.40%`. The next queue head is `0x0054b800 CHudComponent__RenderPassEntry`.
- Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260519-211737_post_wave607_cdxmemorymanager_core_verified` with `19` files, `161418119` bytes, and `DiffCount=0`.

This is saved static retail Ghidra evidence only. Complete `CMemoryTag`/`CMemoryHeap`/`CDXMemoryManager` layouts, exact memory-type enum names, allocator statistics side effects, runtime allocation/OOM behavior, Xbox-only heap differences, BEA patching, and rebuild parity remain unproven.

## Wave812 memory heap deltas Evidence

Wave812 static read-back (`memory-heap-deltas-wave812`, `wave812-readback-verified`) corrected stale `0x004a25c0 CLTShell__ValidateAndRollHeapDeltas` to `0x004a25c0 CMemoryHeap__CalcAndShowDeltas`, hardened `void __thiscall CMemoryHeap__CalcAndShowDeltas(void * this)`, and made no function-boundary or executable-byte changes. The saved body iterates `0x81` memory-type counter rows, uses type-name table `0x009c2dd0` and format string `0x0062f6d0` (`Heap Delta`) to trace non-zero size/block deltas, then copies current counters into last-counter arrays. `CDXMemoryManager__CalcAndShowDeltas` calls the helper from `0x005492e6`, `0x005492f1`, and `0x005492fc` with `this+0x214`, `this+0xae0`, and `this+0x13ac`, matching default, dump, and thing heap subobjects in the Wave607/source-parity wrapper. Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260524-132640_post_wave812_memory_heap_deltas_verified`. Queue after Wave812 is `6098` total, `5587` commented, `511` commentless, `0` exact-undefined signatures, `0` `param_N`, and strict proxy `5587/6098 = 91.62%`; next raw commentless row is `0x004a52b0 CMesh__ClearAllUsageMarkers`.

This is saved static retail Ghidra and Stuart `MemoryManager.cpp`/`DXMemoryManager.cpp` parity evidence only. Exact `CMemoryHeap`/`CDXMemoryManager` layouts, full memory-type enum/table identity, runtime trace/delta behavior, BEA patching, and rebuild parity remain deferred.

## Wave756 MemoryManager.cpp Unwind Continuation

Wave756 static read-back (`unwind-continuation-wave756`, `wave756-readback-verified`) hardened MemoryManager.cpp-adjacent compiler-generated SEH unwind cleanup callbacks from `0x005d3540 Unwind@005d3540` through `0x005d35bc Unwind@005d35bc`. Evidence includes MemoryManager.cpp debug path `0x0062f590`, DATA scope-table xrefs `0x0061c29c` through `0x0061c31c`, two mutex-cleanup rows, one large stack-local `CDXMemBuffer` destructor row, and two allocation-cleanup rows. Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260523-112625_post_wave756_unwind_continuation_verified`. Exact parent source-body identity, runtime exception behavior, runtime cleanup behavior, BEA patching, and rebuild parity remain deferred.

| Address | Static read-back evidence |
| --- | --- |
| `0x005d3540 Unwind@005d3540` | `CMemoryHeap__ReleaseMutexUnwindCleanup(EBP-0x10)`, DATA xref `0x0061c29c`. |
| `0x005d3560 Unwind@005d3560` | `CMemoryHeap__ReleaseMutexUnwindCleanup(EBP-0x10)`, DATA xref `0x0061c2c4`. |
| `0x005d3580 Unwind@005d3580` | `CDXMemBuffer__dtor_base(EBP-0x6844)`, DATA xref `0x0061c2ec`. |
| `0x005d35a0 Unwind@005d35a0` | `OID__FreeObject_Callback(*(EBP-0x2210))`, MemoryManager.cpp line token `0x64`, allocation/type value `0x708`, DATA xref `0x0061c314`. |
| `0x005d35bc Unwind@005d35bc` | `OID__FreeObject_Callback(*(EBP-0x2210))`, MemoryManager.cpp line token `0x64`, allocation/type value `0x77a`, DATA xref `0x0061c31c`. |

## Memory Block Header (16 bytes)

| Offset | Size | Field | Notes |
|--------|------|-------|-------|
| 0x00 | 4 | Magic | 0x4f69ea21 = valid |
| 0x04 | 4 | Size/Flags | bits 4-31=size, bit0=allocated, bit1=debug |
| 0x08 | 4 | Category | Allocation category (0-128) |
| 0x0C | 4 | Next | Free list pointer |
| 0x10 | ... | User data | |

## CMemoryHeap Structure (Partial, Wave438-439)

| Offset | Field | Notes |
|--------|-------|-------|
| 0x00 | mNextHeap | Linked list of heaps |
| 0x04 | mBaseAddress | Heap base |
| 0x08 | mHeapSize | Total size |
| 0x4C | mFreeListHead | Main free list |
| 0x50 | mUsedBytes | Statistics |
| 0x54 | mFreeBytes | Statistics |
| 0x874 | mMerge | Merge/coalescing flag used by `CMemoryHeap__SetMerge` |
| 0x878 | mHeapName | Heap name string |
| 0x8B8 | mSupportSmallAllocs | Enables the 16 small-block buckets |
| 0x8BC | mMutex | Retail mutex/HANDLE slot used by allocator/free/cleanup paths |
| 0x8C0 | mTinyHeap | Tiny heap base |
| 0x8C4 | mTinyHeapFreePtr | Tiny heap free-chain head |
| 0x8C8 | mTinyHeapEnd | Tiny heap end pointer |

## Global Variables

| Address | Name | Notes |
|---------|------|-------|
| 0x009c3df0 | g_HeapList | Linked list of all heaps |
| 0x009c2dd0 | g_CategoryNames | 129 category names (32 bytes each) |

## Related Files

- engine.cpp - Uses memory manager for subsystems

---
*Updated through Wave1042 static Ghidra re-audit (June 1, 2026).*
