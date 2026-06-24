# CFEPSaveGame__Process

> Address: `0x00464730` | Source: `references/Onslaught/FEPSaveGame.cpp`

## Status

- **Named in Ghidra:** Yes
- **Signature Set:** Yes
- **Verified vs Source:** Partial static source-correlation

## Signature

```c
void __thiscall CFEPSaveGame__Process(void * this, int state);
```

## Static Evidence

- Wave375 created the missing Ghidra function object for the FEPSaveGame process vtable slot.
- The saved comment records active/no-message-box dispatch to `CFEPSaveGame__CreateSave` and message-box overwrite/delete handling for save prompts.
- Vtable read-back links this target from the FEPSaveGame table at `0x005db920` slot `2`.

## Claim Boundary

This is saved static Ghidra boundary/signature/comment evidence. Exact message-box state enum semantics, concrete layout, runtime save behavior, and rebuild parity remain unproven.
