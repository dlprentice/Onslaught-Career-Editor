# CFEPSaveGame__Init

> Address: `0x00464620` | Source: `references/Onslaught/FEPSaveGame.cpp`

## Status

- **Named in Ghidra:** Yes
- **Signature Set:** Yes
- **Verified vs Source:** Partial static source-correlation

## Signature

```c
bool __thiscall CFEPSaveGame__Init(void * this);
```

## Static Evidence

- Wave375 created the missing Ghidra function object for the FEPSaveGame vtable init slot.
- The saved comment records save-game selection-field initialization and a true return.
- Vtable read-back links this target from the FEPSaveGame table at `0x005db920` slot `0`.

## Claim Boundary

This is saved static Ghidra boundary/signature/comment evidence. Exact FEPSaveGame layout, local variable types, runtime save-list behavior, and rebuild parity remain unproven.
