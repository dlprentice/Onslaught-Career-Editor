# Ghidra Memory Heap Allocator Review Wave1042

Status: complete static read-only evidence
Date: 2026-06-01
Scope: `memory-heap-allocator-review-wave1042`

Wave1042 re-read eight source-backed `CMemoryHeap` allocator helpers originally corrected by Wave438. The pass made no mutation: no rename, no signature change, no comment/tag write, no function-boundary change, no executable-byte change, no BEA launch, and no runtime/game-file mutation.

Reviewed rows:

| Address | Evidence |
| --- | --- |
| `0x004a13b0 CMemoryHeap__Init` | Initializes heap state, clears stats/free lists, copies heap name, links into `DAT_009c3df0`, creates aligned base block with magic `0x4f69ea21`, and optionally builds the 16-byte tiny heap chain at `this+0x8c0..0x8c8`. |
| `0x004a15a0 CMemoryHeap__ReallocTiny` | Checks the tiny heap range, pushes the old tiny block back to `this+0x8c4`, allocates replacement storage through `CMemoryHeap__Alloc`, copies `min(new_size, 16)`, and writes `out_result`. |
| `0x004a1640 CMemoryHeap__Cleanup` | Optionally waits on mutex slot `this+0x8bc`, clears small/free lists, walks heap blocks, coalesces adjacent free blocks, rebuilds the small buckets or size-sorted free list, and releases the mutex. |
| `0x004a1810 CMemoryHeap__Alloc` | Mutex-guarded allocation path: rounds to 16 bytes, tries tiny/small buckets, pulls from the main free list, retries after cleanup, emits out-of-memory diagnostics through `CMemoryManager__DumpMemory`, splits or consumes a block, and updates counters. |
| `0x004a1c40 CMemoryHeap__ReAlloc` | Allocates replacement storage with the old memory type, copies `min(old_size, new_size)` from `block+0x10`, frees the old block, and returns the new allocation. |
| `0x004a1ca0 CMemoryHeap__Free` | Waits on mutex slot `this+0x8bc`, updates free/used/per-type counters from the block header, clears used/base-set flag bits, reinserts through `CMemoryHeap__AddToFreeList`, and releases the mutex. |
| `0x004a1d60 CMemoryHeap__AddToFreeList` | Routes small blocks under `0x100` into the sixteen small buckets when enabled, otherwise optionally coalesces adjacent main-list blocks when merge flag `this+0x874` is set, then reinserts by size. |
| `0x004a1ea0 CMemoryHeap__SetMerge` | When enabling merge from disabled state, calls `CMemoryHeap__Cleanup`, selection-sorts the main free list by block size, then stores merge flag `this+0x874`. |

Context anchors:

- `0x00548f90 CDXMemoryManager__Init` calls `CMemoryHeap__Init` four times for default, dump, sound, and thing heaps.
- `0x005490e0 CDXMemoryManager__Alloc`, `CDXMemoryManager__ReAlloc`, `CDXMemoryManager__Free`, `MEM_MANAGER__Cleanup`, `CMemoryManager__DeleteTagList`, `CLTShell__ShutdownRuntimeAndReleaseResources`, and `CGame__Shutdown` keep the allocator cluster tied to the global memory-manager wrapper and shutdown paths.
- Stuart source parity anchors: `references/Onslaught/MemoryManager.cpp` lines around `CMemoryHeap::Init`, `ReallocTiny`, `Alloc`, `ReAlloc`, `Free`, `AddToFreeList`, `SetMerge`, and `Cleanup`; `references/Onslaught/MemoryManager.h` defines `MEM_MAGIC_HEADER 0x4f69ea21` and merge flag/member context.

Read-back evidence:

- Primary exports: 8 metadata rows, 8 tag rows, 28 xref rows, 934 body-instruction rows, and 8 decompile rows.
- Context exports: 8 metadata rows, 8 tag rows, 2260 xref rows, 376 body-instruction rows, and 8 decompile rows.
- Queue after Wave1042: 6238 total, 6238 commented, 0 commentless, 0 exact-undefined signatures, 0 `param_N`, strict clean-signature proxy `6238/6238 = 100.00%`.
- Re-audit progress after Wave1042: Wave911 focused `735/1408 = 52.20%`, expanded static surface `968/1493 = 64.84%`, top-500 risk-ranked `500/500 = 100.00%`.
- Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260601-094520_post_wave1042_memory_heap_allocator_review_verified`, 19 files, 174263175 bytes, `DiffCount=0`, `HashDiffCount=0`.

What remains separate proof:

- Runtime allocator behavior.
- Runtime out-of-memory behavior.
- Complete concrete `CMemoryHeap` / `CMemoryBlock` / `CDXMemoryManager` layouts.
- Exact memory-type enum/table identity.
- Thread/mutex lifetime under runtime load.
- BEA patching behavior.
- Gameplay outcomes.
- Rebuild parity.
