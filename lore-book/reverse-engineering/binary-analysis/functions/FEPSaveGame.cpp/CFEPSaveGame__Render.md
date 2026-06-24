# CFEPSaveGame__Render

> Address: `0x00464a80` | Source: `references/Onslaught/FEPSaveGame.cpp`

## Status

- **Named in Ghidra:** Yes
- **Signature Set:** Yes
- **Verified vs Source:** Partial static source-correlation

## Signature

```c
void __thiscall CFEPSaveGame__Render(void * this, float transition, int dest_page);
```

## Static Evidence

- Wave375 corrected the old generic `CFEPSaveGame__VFunc_05_00464a80` label to `CFEPSaveGame__Render`.
- The saved comment records `DrawSlidingTextBordersAndMask`, the save-game title token, overlay effects, and the shared help prompt.
- Vtable read-back links this target from the FEPSaveGame table at `0x005db920` slot `5`.

## Claim Boundary

This is saved static Ghidra name/signature/comment evidence. Exact visual parity, runtime UI behavior, concrete layout, local types, and rebuild parity remain unproven.
