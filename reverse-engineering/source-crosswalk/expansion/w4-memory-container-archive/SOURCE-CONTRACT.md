# W4 memory, container, and archive source contract

Status: review candidate — source-first receipt, not canonical crosswalk authority
Last updated: 2026-08-22
Summary: Stuart's pinned source defines the architecture and algorithms for the 94 omitted W4 definitions; retail evidence is used only to classify released-PC agreement, divergence, target exclusion, or remaining uncertainty.
Evidence: SOURCE — pinned Stuart definitions and target conditionals; MEASURED — tracked pristine-PC name/closure, promoted memory semantics, and full-pass body/ABI reviews; INFERRED — bounded rebuild routing and compiler-emission possibilities are labelled as such.
Specimen: pristine PC `BEA.exe.original.backup`, SHA-256 `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`, 2,506,752 bytes.

## Evidence boundary

This receipt is pinned to `references/Onslaught` commit
`5352a81cdb838b145a57f7febc5d9fc4b0129ebb` and the pristine PC retail
specimen SHA-256
`74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`.
The exact 94 stable keys come from the reviewed 634-definition partition whose
SHA-256 is
`bc36791975f43d5da6b584727df3eb7d29402e18c550dd3d96e01bba0c301fde`.
This branch does not edit the canonical crosswalk, the name table, the closure,
semantic tables, Ghidra, binaries, retail payloads, or user files.

The source is implementation evidence, not automatic retail equality. A
`SOURCE_ANALOG` row below therefore names a released function and the bounded
shape it corroborates without claiming byte- or body-identity. An empty VA is a
falsifiable bounded negative, never evidence that the compiler emitted no
body.

## Selected PC target

The retained headers describe several mutually exclusive builds. The released
specimen is the `_DIRECTX`, `TARGET == PC`, non-editor, non-debug product:

- `membuffer.h:23-26` selects `CDXMemBuffer` as `CMEMBUFFER`.
- `DXMemoryManager.cpp:62-66` selects the one-argument PC
  `CDXMemoryManager::Init(UINT)` at line 63. The three-argument line-65
  definition belongs to the non-PC branch and is retained as a distinct stable
  key.
- `DXMemoryManager.h:72-80` exposes texture- and vertex-buffer heap accessors
  only for `TARGET == XBOX`; those rows are not selected by the PC specimen.
- `Array.h:14-20` and `Array.h:24-36` preserve mutually exclusive vanilla,
  custom-manager, editor, and particle-editor alternatives. The custom manager
  exists in released PC, but that fact alone does not prove the macro selection
  of every template instantiation, so each line/signature remains separate.
- `Array.h:38-44` and `Array.h:62-66` distinguish debug checked subscripts from
  release inline unchecked references.

## Arrays and compact sets

`CArray<T>` stores `mItems` plus `mSize` (`Array.h:11-50`). Its selected
constructor allocates `sz` elements, destruction releases that allocation,
assignment copies exactly the receiver's `mSize` entries, `SetAll` fills that
range, and `Size` returns the stored count. `ReSize` replaces the allocation
with `size * sizeof(T)` bytes and then updates `mSize`; four source bodies keep
the custom-manager, vanilla, editor, and particle-editor branches explicit.
The release subscript returns `mItems[item]` without a check. The debug bodies
at `Array.h:103-127` log and assert on an out-of-range index.

`CSArray<T,size>` embeds all elements in the object (`Array.h:53-71`). Its copy,
fill, count, and subscript operations use the compile-time `size`. `COSet<T>`
adds `mEntries` and `mIterator` over `CArray` (`Array.h:75-90`): `Add` grows to
twice the new entry count when full, `First`/`Next` expose address-stable
iteration over the backing array, `Finalise` shrinks capacity to the live
entry count, and `Size` reports live entries rather than capacity.

No W4 row is promoted from a template-name resemblance. Template
instantiation, folding, and inlining remain compiler-emission questions until
a named body plus ABI/body evidence resolves a specific line/signature.

## Chunk framing and memory-buffer selection

`CChunker` owns a 256-entry nesting stack, an initially 256-KiB data pool, a
`CMEMBUFFER`, and a logical `Position` (`chunker.h:7-30`). The source writer
emits a four-byte tag, a four-byte payload size, then payload bytes; nested
chunks patch their sizes on `End`, and the pool grows in 256-KiB quanta. The W4
header row `CChunker::WhereAmI` only exposes `Position`.

`CChunkReader` stores current payload `Size`, a buffer pointer,
`ReadSinceChunk`, and an ownership flag (`chunker.h:33-50`). The W4 accessors
return the current size and buffer pointer. The already-mapped implementation
in `chunker.cpp:96-200` reads little-endian tag/size pairs, charges reads before
I/O, and skips the unsigned remainder. Retail static evidence at
`0x00423870`, `0x00423900`, `0x00423910`, `0x00423960`, and `0x00423990`
confirms that read-side framing while also exposing release-only over-read and
partial-header behavior. Those mapped bodies are context for the accessors;
they do not manufacture a separate accessor VA.

`IMemBuffer` is deliberately not a virtual interface: its three inline methods
only assert (`membuffer.h:9-19`), while target macros select a concrete buffer.
`CDXMemBuffer` exposes inline cursor/data laws (`DXMemBuffer.h:41-51`):
`IsMoreData` requires read mode and compares `mPtr` with `mData + mDataSize`,
`GetData` returns the backing pointer, and `WhereAmI` returns `mPos`.

The promoted PC memory/I/O table proves the released buffered reader/writer,
CRC, compression, and typed-manager bodies, not distinct emission of these
three inline accessors. It also records two material source-to-retail deltas:
retail chooses and rounds to 1-MiB read buffers rather than source's default
64 KiB/direct nonzero size, and retail adds compressed-block/CRC behavior to
the retained raw paths.

## Memory blocks, heaps, and routing

`MemoryManager.h:50-190` defines 129 allocation categories through
`MEMTYPE_LIMIT`; `MEMBLOCK_HEADER_SIZE` is 16 bytes outside debug builds, and
`MEM_MAGIC_HEADER` is `0x4f69ea21` (`MemoryManager.h:200-206`). A
`CMemoryBlock` stores magic, size/flags, memory type, and next pointer. Inline
accessors mask the low four size bits, derive the user pointer and neighboring
block by 16-byte header arithmetic, expose used/base flags in bits 0/1, and
validate the magic (`MemoryManager.h:218-254`).

`CMemoryHeap` tracks the base allocation, free lists, per-type bytes/blocks,
peak/used/free totals, merge policy, name, optional DirectX mutex, and a tiny
arena (`MemoryManager.h:256-371`). Its PC `Init` at
`MemoryManager.cpp:304-405`:

1. clears usage, block, type, and small-free counters;
2. rounds the heap size upward to a 16-byte boundary;
3. enables merging, copies the name, and links the heap into the global manager;
4. allocates and aligns the base storage, writes the initial block, and adds it
   to the free list; and
5. optionally builds a singly linked 16-byte tiny-block arena.

Released `CMemoryHeap__Init @ 0x004a13b0` has the same four-argument PC ABI and
bounded heap/tiny-heap/name/global-list/aligned-base shape. The tracked
adversarial plate explicitly limits that statement; it does not prove exact
source-body identity.

`CMemoryManager` owns the heap list plus optional memory-tag list
(`MemoryManager.h:392-427`). Its inline destructor deletes tag nodes. The
DirectX subclass creates default, dump, thing, and sound heaps and routes each
memory type through `mTypeHeap` (`DXMemoryManager.cpp:27-147`). Released PC
initialization uses the one-argument branch, a 0x4B000 tiny arena, and no Xbox
texture/VB heaps. Inline W4 accessors expose counters or heap pointers; the
Xbox-only accessors remain `NOT_IN_RETAIL` for this PC target.

The custom allocator is platform infrastructure, not deterministic simulation
truth. Its raw addresses, mutexes, fragmentation, and Win32 allocation policy
must not be copied into `OnslaughtRebuild.Core`.

## Small pointer sets

`GenericSPtrSet` is a singly linked insertion-ordered pointer set with
`mFirst`, `mLast`, an iterator cursor, and `mSize` (`SPtrSet.h:24-59`). A static
node block and free list back all instances. Source construction clears the
three instance fields; copy construction and assignment iterate the source and
append in order (`SPtrSet.cpp:24-63`). `Init` allocates the shared block and
threads its free list. `Add` inserts at the head, `Append` at the tail,
`Remove` unlinks only the first equal pointer, `RemoveAll` returns the complete
node chain to the free list, and `At` walks forward by index
(`SPtrSet.cpp:128-345`). Overflow nodes are dynamically allocated and are
selectively discarded by `ClearAnyDynamicCreatedNodes`.

The templated `SPtrSet<T>` methods at `SPtrSet.h:67-84` are typed forwarding
wrappers. `DeleteAll` deletes elements in iteration order before clearing the
nodes. `GenericListIterator` and `ListIterator<T>` keep cursor state outside the
container (`SPtrSet.h:90-109`). Managed reconstruction should preserve
observable ordering, first-match removal, and iteration invalidation where a
consumer depends on them; it should not reproduce raw pointer ownership or the
static allocator.

Tracked full-pass evidence gives bounded released analogs for the three omitted
out-of-line source rows: three-field initialization at `0x004e5840`,
copy-and-append at `0x004e5850`, and clear-then-append assignment at
`0x004e58a0`. The evidence explicitly leaves template-instantiation ownership
and runtime pool behavior unproved, so the receipt classifies them as analogs,
not exact bodies.

## CLI lifetime edge

`CCLIParams::~CCLIParams` is an empty inline destructor (`CLIParams.h:4-8`).
No distinct released body or deleting-wrapper relationship is proved. A
compiler-emitted wrapper, a folded empty body, and no emitted body remain
separate possibilities; the row stays a bounded negative with an explicit
falsifier.

## Open questions and cheapest falsifiers

- Resolve every array/template alternative with compile-command or emitted-body
  evidence before selecting one row and collapsing siblings.
- For empty destructors, require wrapper ABI/xrefs and body shape; a name alone
  cannot distinguish a source destructor from a scalar/vector deleting wrapper.
- For inline accessors, a new named retail entry must also match the owner,
  signature, field offset, and target branch before a VA is assigned.
- For pointer-set analogs, a contradicting ABI, field order, insertion order, or
  source-coordinate owner falsifies the mapping.
- For `CMemoryHeap__Init`, a body or call ABI that contradicts the four-argument
  PC heap/tiny-chain shape falsifies the bounded analogy.
