# CFEPLoadGame__Render

> Address: `0x00461d90` | Source: `references/Onslaught/FEPLoadGame.cpp`

## Status

- **Named in Ghidra:** Yes
- **Signature Set:** Yes
- **Verified vs Source:** Partial static source-correlation

## Signature

```c
void __thiscall CFEPLoadGame__Render(void * this, float transition, int dest_page);
```

## Static Evidence

- Wave375 corrected the old generic `CFEPLoadGame__VFunc_05_00461d90` label to `CFEPLoadGame__Render`.
- The saved comment records `DrawSlidingTextBordersAndMask`, the load-game title token, overlay effects, and the shared help prompt.
- Vtable read-back links this target from the FEPLoadGame table at `0x005db948` slot `5`.

## Claim Boundary

This is saved static Ghidra name/signature/comment evidence. Exact visual parity, runtime UI behavior, concrete layout, local types, and rebuild parity remain unproven.
