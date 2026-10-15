# CFEPLoadGame__ButtonPressed

> Address: `0x00461c60` | Source: `references/Onslaught/FEPLoadGame.cpp`

## Status

- **Named in Ghidra:** Yes
- **Signature Set:** Yes
- **Verified vs Source:** Partial static source-correlation

## Signature

```c
void __thiscall CFEPLoadGame__ButtonPressed(void * this, int button, float value);
```

## Static Evidence

- Wave375 created the missing Ghidra function object for the FEPLoadGame button vtable slot.
- The saved comment records frontend directional/select/back button handling, selection-field clamping, frontend sound calls, and back navigation through `CFrontEnd__SetPage`.
- Vtable read-back links this target from the FEPLoadGame table at `0x005db948` slot `3`.

## Claim Boundary

This is saved static Ghidra boundary/signature/comment evidence. Exact input enum semantics, concrete field layout, runtime UI behavior, and rebuild parity remain unproven.
