# CFEPSaveGame__AskIfYouWantToDelete

> Address: `0x00464bc0` | Source: `references/Onslaught/FEPSaveGame.cpp`

## Status

- **Named in Ghidra:** Yes
- **Signature Set:** Yes
- **Verified vs Source:** Partial static source-correlation

## Signature

```c
void __thiscall CFEPSaveGame__AskIfYouWantToDelete(void * this, int career_in_progress, int because_4096, int no_space_for_bea);
```

## Static Evidence

- Wave375 corrected the old `CFEPSaveGame__DrawLocalizedStatusPrompt` label to `CFEPSaveGame__AskIfYouWantToDelete`.
- Caller stack evidence and the saved `RET 0x0c` body shape support three stack arguments plus the receiver.
- The saved comment records that the current retail body uses `because_4096` to choose the localized prompt while the other modeled arguments are not directly read in the checked body.

## Claim Boundary

This is saved static Ghidra owner/name/signature/comment evidence. Exact message-box semantics, concrete dialog state layout, runtime save behavior, and rebuild parity remain unproven.
