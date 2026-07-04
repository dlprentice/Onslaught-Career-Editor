# Ghidra CRT/SEH Head Wave620 Readiness Note

Status: complete
Date: 2026-05-20

## Scope

Wave620 hardened the first seven CRT/SEH helper rows after the Wave619 import-thunk island in the saved Ghidra project:

- `0x0055d6a0 CRT__SehPopExceptionFrameAndJump`
- `0x0055d6d4 CRT__InvokeCallbackWithLockGuards`
- `0x0055d6db CRT__SehLockUnlockAndJump`
- `0x0055d6e2 CRT__SehRtlUnwindAndRestoreFrame`
- `0x0055d7bb CRT__SehCallback_Call_005602d2`
- `0x0055d896 CRT__SehFilterCppException`
- `0x0055d90b CRT__GetRangeOfTryBlocksForState`

The pass saved bounded comments and tags only. It made no function renames, no signature changes, no function-boundary changes, and no executable byte changes.

## Evidence

- Dry/apply/final-dry logs reported `updated=0 skipped=7 renamed=0 would_rename=0 missing=0 bad=0`, then `updated=7 skipped=0 renamed=0 would_rename=0 missing=0 bad=0`, then `updated=0 skipped=7 renamed=0 would_rename=0 missing=0 bad=0`, with `REPORT: Save succeeded`.
- Post-state exports verified `7` metadata rows, `7` tag rows, `10` xref rows, `259` instruction rows, and `7` decompile rows.
- Instruction evidence covers FS exception-list frame popping/restoration, indirect jumps through EAX/frame callbacks, `RtlUnwind` at `0x005d04e6`, callback wrapper argument marshaling into `0x005602d2`, exception flag checks, and a 0x14-byte try-block range walker.
- Xrefs tie the rows into adjacent CRT/EH helpers including `CRT__SehUnwindAndResumeSearch`, `CRT__BuildCatchObject`, `CRT__DestroyCatchObject`, `CRT__SehInvokeCallSettingFrame12`, `CRT__CallExceptionTranslator`, `CRT__SehLookupAndInvokeScopeHandler`, and `CRT__ValidateCatchHandlersForThrow`.
- Backup verified: `[maintainer-local-ghidra-backup-root]\BEA_20260520-035125_post_wave620_crt_seh_head_verified` with `19` files, `161811335` bytes, and `DiffCount=0`.

## Queue Telemetry

Post-Wave620 queue telemetry:

- Total functions: `6093`
- Commented functions: `3224`
- Commentless functions: `2869`
- Exact `undefined` signatures: `1218`
- `param_N` signatures: `1056`
- Comment-backed proxy: `3224/6093 = 52.91%`
- Strict clean-signature proxy: `3169/6093 = 52.01%`

Delta from Wave619: `+7` commented, `-7` commentless, `0` exact-undefined signatures, `0` `param_N`, and `0` strict clean-signature rows.

The next queue head is `0x0055dac5 type_info__ctor_like_0055dac5`.

## Boundaries

This is static saved-Ghidra CRT/SEH helper evidence only. Exact MSVC CRT version, exact C++ exception metadata layouts, runtime exception behavior, BEA patching, and rebuild parity remain deferred.
