# W4 memory, container, and archive rebuild delta

Status: review candidate — implementation routing only; no rebuild code changed
Last updated: 2026-08-22
Summary: the read-side chunk cursor is already carried in deterministic Core; writer framing and ordered-set semantics are bounded future slices, while the retail allocator remains platform infrastructure that must not enter Core.
Evidence: SOURCE — pinned chunk/container/memory implementations; MEASURED — tracked pristine-PC chunk and pointer-set/allocator static contracts; INFERRED — ranked future implementation slices, explicitly separated from carried behavior.
Specimen: pristine PC `BEA.exe.original.backup`, SHA-256 `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`, 2,506,752 bytes.

## Current owners inspected

- `rebuild/OnslaughtRebuild.Core/RetailChunkReader.cs` owns the in-memory
  `RetailMemBuffer` and `RetailChunkReader` behavior. It already exposes the
  buffer cursor, EOF state, remaining bytes, chunk size, per-chunk byte charge,
  little-endian header walk, over-read wrap behavior, and close convention.
- `rebuild/OnslaughtRebuild.Core.Tests/RetailChunkReaderTests.cs` pins the
  source/retail read-side laws, including strict end comparison, partial header
  mutation, unsigned over-read, ownership-preserving open, and `0/-1` close.
- `rebuild/PARITY.md` carries the retail over-read contract and its mutation.
- No generic `CArray`, `CMemoryHeap`, `CDXMemoryManager`, `GenericSPtrSet`, or
  `CChunker` writer owner exists in Core. That is not automatically a gap:
  managed arrays/collections replace storage plumbing, and raw allocator policy
  is outside deterministic simulation ownership.
- `rebuild/OnslaughtRebuild.Core/RetailBattleEngineConfigurations.cs` names
  `CSPtrSet<CBattleEngineData>` only as pointer plumbing around a higher-level
  catalog law; it is not a generic pointer-set implementation.

## Already-ported laws and stale gap traps

The chunk-reader accessors in this wave are not evidence that the whole framing
layer is missing. `CChunkReader::GetSize` is `RetailChunkReader.Size`,
`CChunkReader::WhereAmI` is `RetailChunkReader.WhereAmI`, and the selected
DirectX buffer cursor is `RetailMemBuffer.WhereAmI`. `GetMemBuffer` is
intentionally encapsulated as the private buffer reference rather than exposed
as a raw pointer. Any dated synthesis that lists the read-side chunk cursor as
absent is stale.

`CDXMemBuffer::IsMoreData` is represented by the resident-buffer state exposed
through `Remaining`/`EndOfFile`; `GetData` should not become a managed raw-array
escape solely to imitate a pointer accessor. The source's `IMemBuffer` assert
stubs are target-selection scaffolding, not behavior to port.

The source allocator's 16-byte headers, address arithmetic, mutex, free lists,
and fragmentation are not deterministic gameplay laws. Core must stay free of
OS allocation, mutex, clock, filesystem, and raw pointer dependencies. A
player-visible allocation failure or capacity boundary would need a separate
retail contract before any deterministic simulation model is justified.

## Ranked coherent slices

### 1. Closed: resident chunk-reader/accessor parity

Owner: `RetailChunkReader.cs` plus `RetailChunkReaderTests.cs`.

The high-readiness read-side slice is already implemented and tested against
source plus pristine retail addresses. Do not respawn it. Future changes should
only add a carried contract when new behavior is observed, not create a second
reader abstraction.

### 2. Source-first deterministic chunk writer

Proposed owner: a new Core writer adjacent to `RetailChunkReader`, only when a
current rebuild consumer needs to emit an internal chunk stream.

Port the source `CChunker` shape first: little-endian tag/size framing, nesting
stack, size backpatch, logical position, and 256-KiB growth. Use managed storage
and round-trip tests against the existing reader; do not add filesystem I/O.
The released writer bodies still lack a reviewed named mapping, so this slice
would be source-backed rather than retail-exact. Its falsifier is a retained
retail writer body or data fixture that contradicts framing, nesting, growth,
or error behavior.

### 3. Consumer-scoped ordered pointer-set adapter

Proposed owner: the first concrete Core system whose observable behavior needs
head/tail insertion, first-match removal, stable traversal order, or external
iterator state.

Use a managed ordered collection with stable logical identities. Pin `Add`
(head), `Append` (tail), first-match `Remove`, ordered copy/assignment, and
iteration behavior. Do not reproduce the global node pool, overflow allocation,
raw pointer deletion, or accidental use-after-free surface. The tracked
`0x004e5840`/`0x004e5850`/`0x004e58a0` analogs make the basic shape
adjudication-ready, but no utility should be introduced without a concrete
consumer and focused parity test.

## Explicit deferrals

- Do not port `CMemoryHeap` or `CDXMemoryManager` into Core. If diagnostics ever
  need allocation-category telemetry, place a presentation/client adapter
  outside Core and do not claim retail fragmentation or address parity.
- Do not expose a mutable backing array merely to mimic `GetData`.
- Do not implement empty destructors or assert-only interface stubs as managed
  runtime features.
- Do not generalize source-only template bodies into released-PC equality until
  a specific emitted body, ABI, and target branch are proved.
