# SPtrSet.cpp Functions

> Source File: SPtrSet.cpp | Binary: BEA.exe
> Debug Path: 0x00632730

## Overview

> **Queue status (2026-05-26):** Ghidra export-contract closure **6113/6113** (Wave900: every function commented; clean-signature proxy; not evidence-grade semantics). Lines below that reference a "next raw commentless" row are **archival wave progress**, not open work.

SPtrSet (Smart Pointer Set) is a container class implementing a singly-linked list for managing collections of smart pointers. It uses a **free list pool** pattern for efficient memory management - nodes are pre-allocated at initialization and recycled rather than individually allocated/freed.

Wave909 engine/platform support static review (`engine-platform-support-static-review-wave909`) records `CSPtrSet__Clear` as part of a static-coherent engine/platform/math/memory support core (`CSPtrSet 16` family rows in the slice). Verified backup: `G:\GhidraBackups\BEA_20260526-120420_post_wave909_engine_platform_support_static_review_verified`. Runtime safe-pointer container behavior remains separate proof.

**Key Data Structures:**
- Node size: 8 bytes (pointer + next link)
- CSPtrSet/GenericSPtrSet object: 16 bytes (`mFirst`, `mLast`, `mIterator`, `mSize` at offsets 0x0, 0x4, 0x8, 0xC)

**Global Variables:**
| Address | Name | Purpose |
|---------|------|---------|
| 0x0083d130 | g_SPtrSet_FreeListHead | Head of free node pool |
| 0x0083d134 | g_SPtrSet_PoolBase | Pool base pointer / init marker (0 if uninitialized) |
| 0x0083d138 | g_SPtrSet_PoolNodeCount | Number of nodes in the initial pool |
| 0x0083d13c | g_SPtrSet_OverflowAllocCount_AddToHead | Overflow allocation counter (AddToHead) |
| 0x0083d140 | g_SPtrSet_OverflowAllocCount_AddToTail | Overflow allocation counter (AddToTail) |

## Functions

| Address | Name | Purpose | Size |
|---------|------|---------|------|
| 0x0042f220 | CSPtrSet__Clear | Wave797 near-entry thunk/wrapper: unconditional jump to canonical `0x004e5c60 CSPtrSet__Clear` | 5 bytes |
| 0x00406d20 | CSPtrSet__First | Iterator begin (sets mIterator=mFirst; returns item) | ~30 bytes |
| 0x00406d30 | CSPtrSet__Next | Iterator next (mIterator=mIterator->mNext; returns item) | ~30 bytes |
| 0x00409760 | LinkedPtrCursor__MoveFirstAndGet | Cursor-style helper: move to first linked node and return item pointer/value | read-back documented |
| 0x00409780 | LinkedPtrCursor__MoveNextAndGet | Cursor-style helper: advance to next linked node and return item pointer/value | read-back documented |
| 0x004e5840 | CSPtrSet__Init | Constructor-like init (mFirst/mLast/mSize = 0; mIterator untouched) | ~20 bytes |
| 0x004e5850 | CSPtrSet__CopyCtorFromSource | Copy-constructor helper: initialize empty destination, append non-null items from source set | read-back documented |
| 0x004e58a0 | CSPtrSet__operator_assign | operator= (clear then append each element from other) | ~97 bytes |
| 0x004e5910 | CSPtrSet__Shutdown | Free pool block + any dynamically allocated nodes; reset globals | ~105 bytes |
| 0x004e5990 | CSPtrSet__ClearAnyDynamicCreatedNodes | Free any dynamically allocated nodes in free list (keep pool block) | ~140 bytes |
| 0x004e59f0 | CSPtrSet__Initialise | Initialize free list pool with N nodes | ~131 bytes |
| 0x004e5a80 | CSPtrSet__AddToHead | Add element to head of list (LIFO) | ~154 bytes |
| 0x004e5b20 | CSPtrSet__AddToTail | Add element to tail of list (FIFO) | ~166 bytes |
| 0x004e5c30 | CSPtrSet__Contains | Test whether the list contains an item pointer | read-back documented |
| 0x004e5bd0 | CSPtrSet__Remove | Remove first matching element; return node to pool | ~145 bytes |
| 0x004e5c60 | CSPtrSet__Clear | Clear all entries; return nodes to pool | ~70 bytes |
| 0x004e5c90 | CSPtrSet__At | Return the item at a zero-based index by walking node links | read-back documented |

## Wave744 unwind continuation callbacks

Wave744 unwind continuation saved `void __cdecl Unwind@...(void)` signatures, comments, and tags for the SPtrSet cleanup tail at `0x005d17b0 Unwind@005d17b0`, `0x005d17b8 Unwind@005d17b8`, `0x005d17e0 Unwind@005d17e0`, `0x005d17e8 Unwind@005d17e8`, `0x005d17f0 Unwind@005d17f0`, `0x005d1820 Unwind@005d1820`, and `0x005d1828 Unwind@005d1828`.

The saved rows call `CSPtrSet__Clear` on stack locals `EBP-0x1c` and `EBP-0x2c`, plus conditional clears of the pointer at `EBP+4` gated by flag words `EBP-0x20` or `EBP-0x30`. Scope-table DATA xrefs run from `0x0061a61c` through `0x0061a684`. The `0x005d1828 Unwind@005d1828` row closes the local set-clear pair immediately before the next Carrier.cpp allocation-cleanup cluster. Tags include `unwind-continuation-wave744` and `wave744-readback-verified`.

Verified backup: `G:\GhidraBackups\BEA_20260522-163423_post_wave744_unwind_continuation_verified`. After Wave744 the next high-signal queue head is `0x005d1840 Unwind@005d1840`; earliest raw commentless row remains `0x0042f220 CSPtrSet__Clear`. This is saved static retail Ghidra evidence only. Exact parent source body, runtime exception behavior, runtime cleanup behavior, BEA patching, and rebuild parity remain unproven.

## Function Details

### Wave797 SPtrSet clear thunk (0x0042f220)

Wave797 static read-back (`sptrset-clear-wave797`, `wave797-readback-verified`) saved the comment/tags for `0x0042f220 CSPtrSet__Clear`. Instruction evidence is a five-byte unconditional jump (`E9 3B 6A 0B 00`) to canonical `0x004e5c60 CSPtrSet__Clear`; the Ghidra decompile/read-back follows that canonical target. Post exports verified 1 metadata row, 1 tag row, 164 xref rows to the thunk, 65 instruction rows, 1 decompile row, 12 SPtrSet helper metadata rows, 686 helper xref rows, and 12 helper decompile rows. Verified backup: `G:\GhidraBackups\BEA_20260524-054154_post_wave797_sptrset_clear_verified`.

Post-Wave797 queue telemetry is `6098` total, `5545` commented, `553` commentless, `0` exact-undefined signatures, `0` `param_N` signatures, and strict clean-signature proxy `5545/6098 = 90.93%`. The next raw commentless row is `0x004404f0 CThing__NegateVec3ToOut`; commentless high-signal, signature, and name-confidence queues remain empty. Exact embedded-list owners, runtime pool behavior, exact source identity, BEA patching, and rebuild parity remain deferred.

### CSPtrSet__Initialise (0x004e59f0)

**Signature:** `void CSPtrSet__Initialise(int numNodes)`

Allocates and initializes the global free list pool. Called once at startup.

**Behavior:**
1. If already initialized (`g_SPtrSet_PoolBase != 0`), prints warning and returns
2. Allocates `numNodes * 8` bytes via `OID__AllocObject` (0x005490e0)
3. Links all nodes together into a free list chain
4. Sets last node's next pointer to NULL (sentinel)

**Warning String:** `"Warning: Initilise SptrSet twice"` (note: typo "Initilise" in original)

### CSPtrSet__Init (0x004e5840)

**Signature:** `void __thiscall CSPtrSet__Init(CSPtrSet* this)`

Initializes an empty set/list:
- `this->mFirst = NULL`
- `this->mLast = NULL`
- `this->mSize = 0`

Note: does **not** touch the dword at offset `+0x08` (`mIterator`).
In practice, `+0x08` is the iterator pointer (`mIterator`) used by `CSPtrSet__First`/`CSPtrSet__Next`.

### CSPtrSet__CopyCtorFromSource (0x004e5850)

**Signature:** `void * __thiscall CSPtrSet__CopyCtorFromSource(void * this, void * source_set)`

Wave506 corrected the stale `CCareerNode__ClonePtrSetFromSource` label. This is the generic SPtrSet copy-constructor helper used by `CCareerNode__GetChildLinks` / `CCareerNode__GetParentLinks` return-value flows:

- `RET 0x4` proves one explicit `source_set` argument after `ECX`.
- Initializes destination `mFirst`, `mLast`, and `mSize` to zero.
- Walks source nodes from `source_set->mFirst`.
- Appends each non-null item to the destination with `CSPtrSet__AddToTail`.

Static retail/source SPtrSet evidence only; exact template instantiation ownership, caller return-value mechanics, runtime behavior, BEA launch, patching, and rebuild parity remain open.

### CSPtrSet__operator_assign (0x004e58a0)

**Signature:** `void* __thiscall CSPtrSet__operator_assign(CSPtrSet* this, CSPtrSet* other)`

Assignment operator implementation:
1. Clears the current list (returns nodes to the global pool)
2. Iterates `other->mFirst` and appends each element via `CSPtrSet__AddToTail`
3. Returns `this`

### CSPtrSet__Shutdown (0x004e5910)

**Signature:** `void CSPtrSet__Shutdown(void)`

Frees pool resources at end-of-level/shutdown:
- Walks `g_SPtrSet_FreeListHead` and frees any dynamically allocated nodes (outside the initial pool block)
- Frees the initial pool block (`g_SPtrSet_PoolBase`)
- Zeros `g_SPtrSet_PoolBase` and `g_SPtrSet_FreeListHead`

### CSPtrSet__ClearAnyDynamicCreatedNodes (0x004e5990)

**Signature:** `void CSPtrSet__ClearAnyDynamicCreatedNodes(void)`

Walks the free list and frees nodes outside the initial pool block, fixing up the free-list links. This keeps the initial pool block intact.

### CSPtrSet__AddToHead (0x004e5a80)

**Signature:** `void __thiscall CSPtrSet__AddToHead(CSPtrSet* this, void* element)`

Adds an element to the head of the linked list (stack-like LIFO behavior).

**Behavior:**
1. Fatal error if pool not initialized
2. Gets node from free list, or allocates new 8-byte node if exhausted
3. Sets node->data = element, node->next = old head
4. Updates head pointer; if first element, also sets tail

**Warning String:** `"Warning: SPtrSet creating nodes dynamically"` (every 20 overflows)
**Error String:** `"FATAL ERROR: SptSet: Add when freelist not initialised"`

### CSPtrSet__AddToTail (0x004e5b20)

**Signature:** `void __thiscall CSPtrSet__AddToTail(CSPtrSet* this, void* element)`

Adds an element to the tail of the linked list (queue-like FIFO behavior).

**Behavior:**
1. Fatal error if pool not initialized
2. Gets node from free list, or allocates new 8-byte node if exhausted
3. Sets node->data = element, node->next = NULL
4. Links old tail to new node; updates tail pointer
5. If first element, also sets head

**Warning String:** `"Warning: SPtrSet creating nodes dynamically"` (every 20 overflows)

### CSPtrSet__Contains (0x004e5c30)

**Signature:** `bool __thiscall CSPtrSet__Contains(void * this, void * item)`

Walks `mFirst` through `node->mNext`, comparing `node->mItem` against `item`. Returns true on the first match and false when traversal ends. Wave506 removed stale extra stack parameters from the saved signature; the return is a retail 0/1 predicate and source-side `BOOL`/retail `bool` ABI naming remains a documentation caveat.

### CSPtrSet__Remove (0x004e5bd0)

**Signature:** `void __thiscall CSPtrSet__Remove(CSPtrSet* this, void* element)`

Removes the first node where `node->mItem == element`:
- Fixes up `mFirst`/`mLast`
- Decrements `mSize`
- Returns the removed node back to `g_SPtrSet_FreeListHead`

### CSPtrSet__Clear (0x004e5c60)

**Signature:** `void __thiscall CSPtrSet__Clear(CSPtrSet* this)`

If `mSize != 0`, returns the entire node chain to the global free list and resets:
- `this->mFirst = NULL`
- `this->mLast = NULL`
- `this->mSize = 0`

### CSPtrSet__At (0x004e5c90)

**Signature:** `void * __thiscall CSPtrSet__At(void * this, int index)`

Wave506 corrected the stale `LinkedPtrSet__GetValueAtIndex` owner label to the source-aligned `GenericSPtrSet::At(int)` helper. The body walks `index` node steps from `mFirst` and returns `node->mItem`. The retail body does not add bounds/null protection beyond the caller's preconditions.

## Key Observations

1. **Free List Pattern**: Pre-allocates nodes to avoid per-operation malloc overhead. Critical for game performance.

2. **Overflow Handling**: When free list is exhausted, nodes are dynamically allocated with a warning every 20 allocations. This suggests the pool size was tuned but edge cases exist.

3. **Separate Overflow Counters**: Head and tail operations track overflows independently (0x0083d13c vs 0x0083d140), suggesting different usage patterns were monitored.

4. **Thiscall Convention**: AddToHead and AddToTail use `__thiscall` (ECX = this pointer), confirming CSPtrSet is a C++ class.

5. **Remove/Clear Helpers Exist**: `CSPtrSet__Init`/`CSPtrSet__Remove`/`CSPtrSet__Clear` are small helpers that do not reference the `SPtrSet.cpp` debug-path string, but are used widely by systems that embed CSPtrSet-style lists.

6. **Memory Allocator**: All allocations go through `OID__AllocObject` (0x005490e0) with memory category 0x4c and source file/line for debugging.

## CSPtrSet Structure (Inferred)

```cpp
struct SPtrSetNode {
    void* mItem;          // +0x00: Stored element pointer
    SPtrSetNode* mNext;   // +0x04: Next node in list
};

class GenericSPtrSet {
    SPtrSetNode* mFirst;     // +0x00: First node (for iteration/pop)
    SPtrSetNode* mLast;      // +0x04: Last node (for append)
    SPtrSetNode* mIterator;  // +0x08: Iterator pointer (set by First/Next)
    int mSize;               // +0x0C: Number of elements
};
```

## Usage Context

SPtrSet is used by systems that need efficient object tracking:
- **SphereTrigger**: Tracks objects entering/leaving trigger volumes
- **Controller / ActiveReader monitor lists**: Tracks reader cells for safe pointer deletion (monitor.h / Monitor.h deletion-event system). Related helpers: `CMonitor__AddDeletionEvent` (`0x00401040`), `CGenericActiveReader__SetReader` (`0x00401000`), `CGenericActiveReader__dtor` (`0x0044b1d0`).
- **WorldPhysicsManager**: Manages global linked lists (weapons/components/spawners/etc.)
- **Object management**: General-purpose smart pointer collections

---
*Discovered via Phase 1 xref analysis (Dec 2025)*
