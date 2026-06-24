# CSimpleGameMenu__scalar_deleting_dtor

> Address: `0x004d1730` | Source: PauseMenu.cpp / compact game-menu tail (source body not present in `references/Onslaught/` snapshot)

## Status

- **Named in Ghidra:** Yes (Wave474 correction)
- **Signature Set:** Yes
- **Verified vs Source:** No source-body match; static retail-binary evidence only

## Signature

```c
void * __thiscall CSimpleGameMenu__scalar_deleting_dtor(void * this, int flags);
```

## Evidence

- Wave474 corrected the prior `CSimpleGameMenu__VFunc_01_004d1730` label to the scalar-deleting destructor wrapper.
- The body calls `CSimpleGameMenu__dtor_base` at `0x004d1733`.
- It tests `flags` bit 0 at `0x004d1738`, frees `this` through `CDXMemoryManager__Free` when set, returns `this`, and ends with `RET 0x4`.
- Vtable xref at `0x005de720` anchors this as a `CSimpleGameMenu` vtable target.

## Not Proven

Exact class layout, source method identity, allocator ownership beyond the observed flag path, runtime UI behavior, BEA launch behavior, game patching, and rebuild parity remain unproven.
