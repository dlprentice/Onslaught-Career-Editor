# FEPSaveLoad__TransitionNotification

> Address: `0x00464b10` | Source: `references/Onslaught/FEPLoadGame.cpp`, `references/Onslaught/FEPSaveGame.cpp`

## Status

- **Named in Ghidra:** Yes
- **Signature Set:** Yes
- **Verified vs Source:** Partial static source-correlation

## Signature

```c
void __thiscall FEPSaveLoad__TransitionNotification(void * this, int from_page);
```

## Static Evidence

- Wave375 corrected the old broad `CFrontEndPage__TransitionNotification` label to a shared save/load transition helper.
- The saved comment records `PLATFORM__GetSysTimeFloat`, a transition-delay add, and a store at `this+0x4`.
- Vtable read-back links this target from both the FEPSaveGame table at `0x005db920` slot `6` and the FEPLoadGame table at `0x005db948` slot `6`.

## Claim Boundary

This is saved static Ghidra owner/name/signature/comment evidence. Exact owning class fold, concrete layout, runtime transition behavior, and rebuild parity remain unproven.
