# CSimpleGameMenu__dtor_base

> Address: `0x004d1750` | Source: PauseMenu.cpp / compact game-menu tail (source body not present in `references/Onslaught/` snapshot)

## Status

- **Named in Ghidra:** Yes (Wave474 correction)
- **Signature Set:** Yes
- **Verified vs Source:** No source-body match; static retail-binary evidence only

## Signature

```c
void __fastcall CSimpleGameMenu__dtor_base(void * simple_game_menu);
```

## Evidence

- Wave474 corrected the prior suffixed scalar-deleting label to the destructor body reached by `CSimpleGameMenu__scalar_deleting_dtor`.
- The body restores the shared no-op vtable pointer `0x005de71c`.
- It walks the active-reader set rooted at `+0x3c`, calls `CGenericActiveReader__dtor`, and frees each reader node.
- It clears the set, destroys the embedded `CMenuItemRange` at `+0x0c`, and finishes through `CMonitor__Shutdown`.
- Raw disassembly for `0x004d1730..0x004d1805` records the destructor wrapper call, flag test, active-reader cleanup, `CMenuItemRange__Destructor`, and monitor shutdown call.

## Not Proven

Concrete `CSimpleGameMenu` layout, exact source method identity, runtime UI behavior, BEA launch behavior, game patching, and rebuild parity remain unproven.
