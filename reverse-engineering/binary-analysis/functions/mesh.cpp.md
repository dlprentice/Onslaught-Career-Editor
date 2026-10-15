# mesh.cpp Functions

Status: active static function map
Last updated: 2026-08-12
Source File: `C:\dev\ONSLAUGHT2\mesh.cpp` (named by the shipped image; absent from `references/Onslaught/`) | Binary: BEA.exe, SHA-256 `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`

Four functions here carry source coordinates and had no prior documentation.
Rows are **measured** only: entry address, current Ghidra name, body size,
callee-popped argument count from `ret imm`, the compiler's own
`__FILE__`/`__LINE__` coordinates, and heaviest direct callees. No purpose is
invented.

| Address | Current name | Bytes | Args | Source lines | Heaviest callees |
| --- | --- | ---: | ---: | --- | --- |
| `0x004A5200` | `CMesh__InitStatic` | 171 | 0 | 145 | `CMesh__ReleaseEmbeddedResources`, `CDXMemoryManager__Free` |
| `0x004A5B70` | `CMesh__Load` | **18546** | 2 | 565–1534 | `CDXMemBuffer__Read` ×82, `CDXMemoryManager__Alloc` ×25 |
| `0x004AA6E0` | `CMesh__FindOrCreate` | 246 | 0 | 1877 | `stricmp`, `CDXMemoryManager__Alloc` |
| `0x004AB360` | `CMesh__OptimizeParts` | 2559 | 0 | 3670 | `sprintf` ×3, `DebugTrace` ×3 |

## `CMesh__Load` is the largest body the instrument touches

18,546 bytes across source lines **565–1534** — roughly 970 source lines in a
single function — with **82** `CDXMemBuffer__Read` calls against 25 allocations.
That is a monolithic format reader, and its span makes `mesh.cpp` at least 3,670
lines.

It is worth separating two things that this document does **not** claim. The 82
reads say the mesh format has many fields; they do not say how many chunks,
versions, or optional blocks exist, and the coordinate list is the set of
allocation sites only, not a field map. Recovering the format needs the body
read against the shipped `.CMSH` payloads, which is a substantially larger task
and is untouched here.

`CMesh__FindOrCreate` calling `stricmp` indicates a name-keyed cache lookup
before allocation — the usual find-or-insert shape — and `CMesh__InitStatic`
calling `ReleaseEmbeddedResources` then `Free` is a teardown-before-init
ordering worth noting when reasoning about static lifetime.

## Related

`MeshPart.cpp` is documented separately at
[`MeshPart.cpp.md`](MeshPart.cpp.md); its `LoadFromStream` uses `CChunkReader`
while `CMesh__Load` here uses `CDXMemBuffer` directly, so the two levels of the
mesh hierarchy read through different mechanisms.

## Open

- No behaviour, no format, no field semantics. `CMesh__Load`'s 82 reads are a
  count, not a schema.
- `CMesh__OptimizeParts` is 2,559 bytes whose only distinctive callees are
  `sprintf` and `DebugTrace`, i.e. its logic is inline and unread here.
