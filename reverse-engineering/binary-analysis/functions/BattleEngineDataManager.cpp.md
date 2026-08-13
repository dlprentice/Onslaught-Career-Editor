# BattleEngineDataManager.cpp Functions

Status: active static function map
Last updated: 2026-08-12
Source File: `C:\dev\ONSLAUGHT2\BattleEngineDataManager.cpp` (named by the shipped image; present in `references/Onslaught/` as `BattleEngineDataManager.cpp`) | Binary: BEA.exe, SHA-256 `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`

Two functions carry every source coordinate this file emits. Rows below are
**measured** only — entry address, current Ghidra name, body size, callee-popped
argument count from `ret imm`, the compiler's own `__FILE__`/`__LINE__`
coordinates, and heaviest direct callees. No purpose is invented.

| Address | Current name | Bytes | Stack args | Source lines | Heaviest callees |
| --- | --- | ---: | ---: | --- | --- |
| `0x0040F590` | `CBattleEngineData__Initialise` | 759 | 0 | 36, 40, 41, 45, 46, 50, 51, 61, 67, 70 | `CDXMemoryManager__Alloc` ×13, `CSPtrSet__AddToHead` ×4 |
| `0x0040F980` | `CBattleEngineData__LoadFromMemBuffer` | 1939 | 1 | 192, 193, 207, 208, 222, 223, 237, 238, 252, 253, 268, 298, 304, 324, 325, 347, 348, 402, 417, 432, 438 | `CDXMemBuffer__Read` ×42, `CDXMemoryManager__Alloc` ×21, `CSPtrSet__AddToHead` ×5 |

## What the coordinates show

`Initialise` allocates thirteen times across lines 36–70 — a dense constructor
run, with four of the results appended to pointer sets. `LoadFromMemBuffer`
performs 42 buffer reads against 21 allocations across lines 192–438, and its
line numbers arrive in tight pairs (192/193, 207/208, 222/223, 237/238, 252/253,
324/325, 347/348). Paired allocation lines two apart is the shape of a repeated
read-then-store block, which is consistent with a table of like-typed records
rather than a flat struct read.

**This file is present in the pinned GPL drop**, unlike `MeshPart.cpp`, so these
two are the rare case where the coordinates can be checked directly against
source rather than standing alone. That comparison is not done here.

## Counting note

The per-file ranking in
[the coordinate report](../pc-native-source-coordinates-2026-08-12.md) shows
`BattleEngineDataManager.cpp` at 31, which is **coordinate rows, not functions**.
It resolves to these **two**. `MeshPart.cpp` likewise showed 32 and resolved to
11. The ranking is allocation-site density and must not be read as a function
count — confirmed twice now, and the correction is recorded in that report.

## Open

- No behaviour is established. Two functions, both well named already; the
  coordinates say where they are, not what they do.
- The obvious next step is the source comparison this file uniquely permits.
