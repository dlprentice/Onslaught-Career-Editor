# CPlaneAI Destructor Pair

> Source File: Plane.cpp | Binary: BEA.exe
> Wave: 484 | Evidence: saved Ghidra metadata, decompile, xrefs, vtable/RTTI rows, instruction rows, tags, and focused probe

## Functions

| Address | Name | Saved signature |
| --- | --- | --- |
| `0x004d1c10` | `CPlaneAI__scalar_deleting_dtor` | `void * __thiscall CPlaneAI__scalar_deleting_dtor(void * this, byte flags)` |
| `0x004d1c30` | `CPlaneAI__dtor_body` | `void __fastcall CPlaneAI__dtor_body(void * this)` |

## Evidence

- `CPlaneAI` vtable `0x005de73c` slot 1 points to `0x004d1c10`.
- The RTTI COL for `0x005de73c` resolves to `CPlaneAI`.
- Base vtable `0x005d8d1c` resolves to `CUnitAI`; its slot 1 remains `CUnitAI__scalar_deleting_dtor`.
- `0x004d1c10` calls `0x004d1c30`, tests scalar-delete flags bit 0, optionally calls `CDXMemoryManager__Free(&DAT_009c3df0, this)`, returns `this`, and ends with `RET 0x4`.
- `0x004d1c30` restores vtable `0x005d8d1c`, removes linked cells at `this+0x28`, `this+0x24`, and `this+0x0c` through `CSPtrSet__Remove` when present, then calls `CMonitor__Shutdown`.

## Boundary

Static retail-binary evidence only. The current Stuart source snapshot does not contain a `Plane.cpp` or `CPlaneAI` source body. Exact `CPlaneAI` layout, linked-set semantics, allocator ownership, runtime AI destruction behavior, BEA launch behavior, game patching, and rebuild parity remain unproven.
