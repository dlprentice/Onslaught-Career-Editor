# MemoryManager.cpp Functions

> Source File: MemoryManager.cpp | Binary: BEA.exe
> Debug Path: 0x0062f590

## Overview

Core memory management system. CMemoryManager implements custom heap allocation with thread safety, bucketed free lists, coalescing, and debug statistics.

## Functions

| Address | Name | Purpose | Size |
|---------|------|---------|------|
| 0x004a13b0 | CMemoryManager__Init (TODO) | Initialize heap with malloc | ~400 bytes |
| 0x004a1810 | CMemoryManager__Alloc (TODO) | Core allocation (thread-safe) | ~500 bytes |
| 0x004a1ca0 | CMemoryManager__Free (TODO) | Free allocated block | ~100 bytes |
| 0x004a1c40 | CMemoryManager__Realloc (TODO) | Reallocate with copy | ~100 bytes |
| 0x004a1c30 | CMemoryManager__ReleaseMutexCallback | Callback helper that releases heap mutex handles (`ReleaseMutex`) | ~16 bytes |
| 0x004a15a0 | CMemoryManager__ReallocFromPool | Realloc from small-block pool | ~100 bytes |
| 0x004a1d60 | CMemoryManager__AddToFreeList | Return to free list + coalesce | ~200 bytes |
| 0x004a1640 | CMemoryManager__Coalesce (TODO) | Merge adjacent free blocks | ~200 bytes |
| 0x004a1ea0 | CMemoryManager__EnableCoalescing | Enable/sort free list | ~150 bytes |
| 0x004a2460 | CMemoryManager__DumpStats (TODO) | Print memory statistics | ~200 bytes |
| 0x004a2660 | CMemoryManager__DumpHeapBlocks | Dump all blocks in heap | ~300 bytes |
| 0x004a2a20 | CMemoryManager__MarkAllocatedBlocksDebug | Iterates heap blocks and marks allocated entries with debug bit (`| 2`) | ~96 bytes |
| 0x004a2a80 | CMemoryManager__DumpMemoryReport | Full OOM report | ~200 bytes |
| 0x004a2ff0 | CMemoryManager__SetBlockFlag | Set/clear block flag | ~50 bytes |
| 0x004a1f60 | CMemoryManager__DumpStatsToFile | Write stats to file | ~200 bytes |
| 0x00548f90 | MEM_MANAGER__Init | Global memory-manager heap bootstrap wrapper used from `CLTShell__WinMain` | ~700 bytes |
| 0x00549270 | MEM_MANAGER__Cleanup | Global cleanup wrapper used by load/restart paths (two coalesce passes) | ~16 bytes |

## Key Observations

- **Thread-safe** - Uses mutex at offset 0x8bc
- **16-byte alignment** - All allocations aligned
- **Bucketed free lists** - 16 buckets for sizes < 256 bytes
- **Small block cache** - Fast path for < 16 bytes
- **Magic sentinel** - 0x4f69ea21 marks valid blocks
- **129 allocation categories** - Per-category statistics
- **OOM handling** - Prints "FATAL ERROR: Out of memory" and dumps report
- **Global cleanup wrapper** - `MEM_MANAGER__Cleanup` provides the source-level `MEM_MANAGER.Cleanup()` call path
- **Global init wrapper** - `MEM_MANAGER__Init` seeds default/dump/sound/thing heaps via `CMemoryManager__Init` calls during shell startup

## Memory Block Header (16 bytes)

| Offset | Size | Field | Notes |
|--------|------|-------|-------|
| 0x00 | 4 | Magic | 0x4f69ea21 = valid |
| 0x04 | 4 | Size/Flags | bits 4-31=size, bit0=allocated, bit1=debug |
| 0x08 | 4 | Category | Allocation category (0-128) |
| 0x0C | 4 | Next | Free list pointer |
| 0x10 | ... | User data | |

## CMemoryManager Structure (Partial)

| Offset | Field | Notes |
|--------|-------|-------|
| 0x00 | mNextHeap | Linked list of heaps |
| 0x04 | mBaseAddress | Heap base |
| 0x08 | mHeapSize | Total size |
| 0x4C | mFreeListHead | Main free list |
| 0x50 | mUsedBytes | Statistics |
| 0x54 | mFreeBytes | Statistics |
| 0x8BC | mMutex | Thread safety |
| 0x878 | mHeapName | Heap name string |

## Global Variables

| Address | Name | Notes |
|---------|------|-------|
| 0x009c3df0 | g_HeapList | Linked list of all heaps |
| 0x009c2dd0 | g_CategoryNames | 129 category names (32 bytes each) |

## Related Files

- engine.cpp - Uses memory manager for subsystems

---
*Discovered via Phase 1 xref analysis (Dec 2025)*
