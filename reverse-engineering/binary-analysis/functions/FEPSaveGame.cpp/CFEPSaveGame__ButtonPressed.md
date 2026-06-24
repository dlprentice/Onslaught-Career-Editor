# CFEPSaveGame__ButtonPressed

> Address: `0x00464630` | Source: `references/Onslaught/FEPSaveGame.cpp`

## Status

- **Named in Ghidra:** Yes
- **Signature Set:** Yes
- **Verified vs Source:** Partial static source-correlation

## Signature

```c
void __thiscall CFEPSaveGame__ButtonPressed(void * this, int button, float value);
```

## Static Evidence

- Wave375 created the missing Ghidra function object for the FEPSaveGame button vtable slot.
- The saved comment records frontend directional/select/back button handling, selection-field clamping, frontend sound calls, and back navigation through `CFrontEnd__SetPage`.
- Vtable read-back links this target from the FEPSaveGame table at `0x005db920` slot `3`.

## Claim Boundary

This is saved static Ghidra boundary/signature/comment evidence. Exact input enum semantics, concrete field layout, runtime UI behavior, and rebuild parity remain unproven.
