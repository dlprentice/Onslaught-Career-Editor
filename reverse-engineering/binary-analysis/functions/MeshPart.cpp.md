# MeshPart.cpp Functions

Status: active static function map
Last updated: 2026-08-12
Source File: `C:\dev\ONSLAUGHT2\MeshPart.cpp` (named by the shipped image; absent from `references/Onslaught/`) | Binary: BEA.exe, SHA-256 `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`

`C:\dev\ONSLAUGHT2\MeshPart.cpp` is named by the shipped image and is **absent
from the pinned GPL drop**, so everything here comes from bytes. It is the
largest documentation gap the PC-native source-coordinate instrument exposes;
see [that report](../pc-native-source-coordinates-2026-08-12.md).

## What this adds, and what it does not

Each row below carries **measured** facts only: the exact entry address, the
current Ghidra name, body size, callee-popped argument count from `ret imm`, the
`__FILE__`/`__LINE__` coordinates the compiler emitted inside the body, and the
heaviest direct callees. **No purpose is invented.** Where the existing name
already describes the function, that name is the claim and the evidence either
supports it or is silent — none of it is contradicted here.

Argument counts are callee-popped stack arguments; `this` travels in ECX and is
not counted.

| Address | Current name | Bytes | Stack args | Source lines | Heaviest callees |
| --- | --- | ---: | ---: | --- | --- |
| `0x004AE2B0` | `CMeshPart__CreatePolyBucket` | 383 | 0 | 233 | `CMesh__GetNameOrUnknown` ×3, `stricmp` ×2 |
| `0x004AE4B0` | `CMeshPart__Init` | 400 | 0 | 351 | `CDXMemoryManager__Alloc` ×2, `CDXMeshVB__ctor` |
| `0x004AE860` | `CMeshPart__AllocateGeometry` | 485 | 5 | 552 | `CDXMemoryManager__Alloc` ×4, `DebugTrace` ×3 |
| `0x004AF470` | `CMeshPart__LoadVerticesAndTriangles` | 1848 | 5 | 898, 988 | `CDXMemBuffer__Read` ×10, `Vec3__SetXYZ` ×2 |
| `0x004AFBB0` | `CMeshPart__LoadVerticesWithBones` | 3139 | 7 | 1174, 1176, 1178, 1221, 1223, 1262, 1353 | `CDXMemBuffer__Read` ×17, `CDXMemoryManager__Alloc` ×8 |
| `0x004B1A40` | `CMeshPart__CacheFrameData` | 750 | 0 | 1815 | `CDXMemoryManager__Alloc` ×2, `sprintf`, `DebugTrace` |
| `0x004B27A0` | `CMeshPart__LoadFromStream` | 2514 | 0 | 2425, 2431, 2442, 2446, 2452, 2602, 2742 | `CChunkReader__GetNext` ×19, `CChunkReader__Read` ×18 |
| `0x004B3180` | `CMeshPart__LoadMaterial` | 109 | 0 | 2857 | `CChunkReader__Read` ×4, `CChunkReader__GetNext` |
| `0x004B31F0` | `CMeshPart__OptimizePolygons` | 2418 | 0 | 2893, 2895 | `sprintf` ×3, `DebugTrace` ×3 |
| `0x004B3B70` | `CMeshPart__Clone` | 1751 | 0 | 3135, 3160, 3180, 3188, 3199, 3212 | `CDXMemoryManager__Alloc` ×11, `CMeshPart__Init`, `CMeshPart__AllocateGeometry` |
| `0x004B4250` | `CMeshPart__Merge` | 2139 | 1 | 3243, 3246, 3249 | `CDXMemoryManager__Alloc` ×3, `Vec3__DivideInPlaceByScalar` ×3 |

## Recovered file layout

The source lines are monotonic in address — 233, 351, 552, 898, 1174, 1815,
2425, 2857, 2893, 3135, 3243 — so the linker preserved definition order and
`MeshPart.cpp` is **at least 3,249 lines**. Construction and allocation sit at
the top, stream loading in the middle, and clone/merge at the end.

Two evidence joins worth keeping:

- `CMeshPart__Clone` calls both `CMeshPart__Init` and
  `CMeshPart__AllocateGeometry`, so cloning re-runs construction rather than
  copying raw memory.
- `LoadFromStream` and `LoadMaterial` are the only chunk-reader consumers here,
  and `LoadVerticesAndTriangles` and `LoadVerticesWithBones` read through
  `CDXMemBuffer` instead — two distinct input paths into the same object.

## Counting note

The source-coordinate report's per-file ranking counts **coordinate rows**, not
distinct functions: `MeshPart.cpp` shows 32 there and resolves to these **11**
functions, several carrying many coordinates each. Read that ranking as
allocation-site density, not as a function count.

## Open

- No behaviour is established. Argument counts, callees and line numbers do not
  give a contract; every one of these eleven still needs its own reading.
- The bone-weighted vertex path at seven arguments is the widest interface here
  and the natural first target.

Source File: `C:\dev\ONSLAUGHT2\MeshPart.cpp` (named by the shipped image; absent from `references/Onslaught/`) | Binary: BEA.exe, SHA-256 `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`
