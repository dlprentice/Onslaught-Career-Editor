# CFEPLoadGame__Init

> Address: `0x00461c40` | Source: `references/Onslaught/FEPLoadGame.cpp`

## Status

- **Named in Ghidra:** Yes
- **Signature Set:** Yes
- **Verified vs Source:** Partial static source-correlation

## Signature

```c
bool __thiscall CFEPLoadGame__Init(void * this);
```

## Static Evidence

- Wave375 created the missing Ghidra function object for the FEPLoadGame vtable init slot.
- The saved comment records initialization of load-game selection fields, the selected save slot sentinel `-1`, and save-name head clearing.
- Vtable read-back links this target from the FEPLoadGame table at `0x005db948` slot `0`.

## Claim Boundary

This is saved static Ghidra boundary/signature/comment evidence. Exact FEPLoadGame layout, local variable types, runtime save-list behavior, and rebuild parity remain unproven.
