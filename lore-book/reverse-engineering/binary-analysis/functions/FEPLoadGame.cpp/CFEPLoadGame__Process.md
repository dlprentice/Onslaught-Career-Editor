# CFEPLoadGame__Process

> Address: `0x00461d60` | Source: `references/Onslaught/FEPLoadGame.cpp`

## Status

- **Named in Ghidra:** Yes
- **Signature Set:** Yes
- **Verified vs Source:** Partial static source-correlation

## Signature

```c
void __thiscall CFEPLoadGame__Process(void * this, int state);
```

## Static Evidence

- Wave375 corrected the old generic `CFEPLoadGame__VFunc_02_00461d60` label to `CFEPLoadGame__Process`.
- The saved comment records a non-inactive-state update-like helper call and active/no-message-box dispatch to `CFEPLoadGame__DoLoad`.
- Vtable read-back links this target from the FEPLoadGame table at `0x005db948` slot `2`.

## Claim Boundary

This is saved static Ghidra name/signature/comment evidence. The exact identity of the update-like helper at `0x0041a200`, runtime save-load behavior, and rebuild parity remain unproven.
