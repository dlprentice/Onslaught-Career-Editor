# CHazard__Shutdown

Status: active function identity reference; earlier behavior claims retain their limits
Last updated: 2026-09-26 (virtual-method identity refresh; earlier behavioral evidence keeps its stated limits)
Source File: unavailable in the pinned partial source; identity is from retail RTTI/byte evidence | Binary: pristine BEA.exe, SHA-256 `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`
Summary: current method identities with preserved historical evidence and superseded labels.

> Address: `0x0047e6e0`

## September 26 virtual-method identity correction

The [reviewed virtual-identity cohort](../../../ghidra/README.md#re-audit-thing-family-virtual-identities--september-26) updates the current labels
asserted below from pristine bytes and fixed RTTI slot identities. Earlier labels
in dated prose and filenames are retained aliases; the cohort manifest preserves
their exact mapping. This correction does not re-verify the rest of this note
or certify its prototypes or runtime behavior.

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
