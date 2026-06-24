# CFEPSaveGame__RemovedMUWhinge

> Address: `0x00464b30` | Source: `references/Onslaught/FEPSaveGame.cpp`

## Status

- **Named in Ghidra:** Yes
- **Signature Set:** Yes
- **Verified vs Source:** Partial static source-correlation

## Signature

```c
void __cdecl CFEPSaveGame__RemovedMUWhinge(int reason_token);
```

## Static Evidence

- Wave375 corrected the old `CFEPLoadGame__ResolveTextByToken` label to `CFEPSaveGame__RemovedMUWhinge`.
- Callsite read-back shows callers from `CFEPLoadGame__DoLoad` and `CFEPVirtualKeyboard__Process`.
- The saved comment records localized storage-message resolution, `DAT_00677614` clearing, standard dialog-layout setup, and dialog state reset.

## Claim Boundary

This is saved static Ghidra owner/name/signature/comment evidence. Exact text-token enum values, concrete dialog layout, runtime dialog behavior, and rebuild parity remain unproven.
