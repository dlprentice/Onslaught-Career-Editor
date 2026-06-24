# CHazard__VFunc02_CleanupWorldSoundAndLinkedState

> Address: `0x0047e6e0`

## Status

- **Named in Ghidra:** Yes, corrected in Wave396
- **Signature Set:** Yes
- **Verified vs Source:** No exact source-body match claimed

## Signature

```c
void __fastcall CHazard__VFunc02_CleanupWorldSoundAndLinkedState(void * this);
```

## Static Evidence

Wave396 corrected the older address-suffixed `CHazard__VFunc_02_0047e6e0` label to a bounded cleanup name. Read-back shows the function releases sound-sample state, cleans linked state around the `+0x80` family, removes world occupancy-grid state, and then dispatches the base cleanup path.

## Boundaries

- This is saved static Ghidra name/signature/comment/tag evidence.
- It does not prove runtime hazard behavior, exact source virtual name, concrete `CHazard` layout, local variable names, local types, or rebuild parity.
