# ParticleSet.cpp Functions

Status: active static function map
Last updated: 2026-08-12
Source File: `C:\dev\ONSLAUGHT2\ParticleSet.cpp` (named by the shipped image; absent from `references/Onslaught/`) | Binary: BEA.exe, SHA-256 `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`

Three functions here carry source coordinates and had no prior documentation.
Rows are **measured** only: entry address, current Ghidra name, body size,
callee-popped argument count from `ret imm`, the compiler's own
`__FILE__`/`__LINE__` coordinates, and heaviest direct callees. No purpose is
invented.

| Address | Current name | Bytes | Args | Source lines | Heaviest callees |
| --- | --- | ---: | ---: | --- | --- |
| `0x004CC020` | `CParticleSet__CreateByType` | 2036 | 3 | 95–107 | `CDXMemoryManager__Alloc` ×13, `CParticleSet__Init` ×10 |
| `0x004CD7F0` | `CParticleSet__LoadFromArchive` | 617 | 1 | 315–348 | `CDXMemoryManager__Free` ×7, `CTokenArchive__ReadNextToken` ×5 |
| `0x004CDA60` | `CParticleSet__LoadParticleSetFile` | 297 | 1 | 437 | `CDXMemoryManager__Alloc`, `CDXMemBuffer__ctor` |

## Two joins worth keeping

**`CreateByType` is a thirteen-way factory.** Thirteen allocations paired with
ten `CParticleSet__Init` calls across source lines 95–107 — one allocation site
per line — is the shape of a type switch with a case per particle-set kind. The
count of distinct kinds is not established: 13 allocations and 10 inits do not
have to mean 13 or 10 types, since a case may allocate more than once.

**`LoadFromArchive` consumes `CTokenArchive__ReadNextToken`** ×5 with seven
frees. That is the same token reader whose exact static parser, corpus, factory
and direct-writer contract was admitted at C1 in **Generation 18**, and whose
171-byte consumer-bound dispatch-data partition closed a residual in
**Generation 14**. So this is a named consumer of an already-contracted parser —
a place where the campaign's TokenArchive work and the particle system meet.

That join is the useful part of this file: Generation 18 established what the
reader does, and this says who calls it and with what lifetime (seven frees in
617 bytes, so the loader releases as it goes rather than at the end).

## Open

- No behaviour and no particle semantics. The rebuild's particle work is
  separately evidenced and is not touched by this.
- How many particle-set kinds `CreateByType` actually distinguishes, and what
  its three stack arguments are.
- Whether `LoadParticleSetFile` and `LoadFromArchive` are alternative entry
  points for the same data or serve different containers.
