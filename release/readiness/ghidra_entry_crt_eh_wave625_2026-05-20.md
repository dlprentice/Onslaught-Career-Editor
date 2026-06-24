# Ghidra Entry/CRT EH Wave625 Readiness Note

Status: complete
Date: 2026-05-20

## Scope

Wave625 hardened eight adjacent process-entry, fatal-exit, and CRT C++ exception helper rows in the saved Ghidra project:

- `0x00560181 entry`
- `0x005602ae CDXTexture__ReportFatalAndExitProcess`
- `0x005605ca CRT__TypeMatchForCatch`
- `0x00560627 CRT__SehUnwindToTargetState`
- `0x00560740 CRT__CallCatchBlock`
- `0x00560885 CRT__BuildCatchObject`
- `0x00560a49 CRT__DestroyCatchObject`
- `0x00560ab0 CRT__AdjustPointerByPMD`

The pass saved bounded signatures, comments, and tags. It made no function-boundary changes, no renames, and no executable byte changes.

## Evidence

- Dry mode reported `updated=0 skipped=8 renamed=0 would_rename=0 missing=0 bad=0`.
- The first apply pass saved the metadata but exposed a script-side zero-parameter read-back mismatch for `entry`: Ghidra read back `void __cdecl entry(void)` while the script expected `void __cdecl entry()`. That mismatch log is preserved as `apply-wave625-apply-initial-readback-mismatch.log`.
- After correcting the script expectation, apply and final-dry reruns reported `updated=0 skipped=8 renamed=0 would_rename=0 missing=0 bad=0`, with `REPORT: Save succeeded`.
- Post-state exports verified `8` metadata rows, `8` tag rows, `15` xref rows, `968` instruction rows, and `8` clean decompile rows.
- Entry evidence covers SEH-frame setup, Win32 version capture, heap/TLS/file/argv/environment/static-init setup, startup show-command selection, `CLTShell__WinMain`, and `CRT__CExit`.
- Fatal-exit evidence covers runtime error reporting and `ExitProcess(0xff)`.
- CRT EH evidence covers catch-type matching, unwind-map walking, catch-block invocation, catch-object materialization/destruction, and pointer-to-member-displacement adjustment.
- Backup verified: `G:\GhidraBackups\BEA_20260520-061702_post_wave625_entry_crt_eh_verified` with `19` files, `162040711` bytes, and `DiffCount=0`.

## Queue Telemetry

Post-Wave625 queue telemetry:

- Total functions: `6093`
- Commented functions: `3278`
- Commentless functions: `2815`
- Exact `undefined` signatures: `1217`
- `param_N` signatures: `1003`
- Comment-backed proxy: `3278/6093 = 53.80%`
- Strict clean-signature proxy: `3226/6093 = 52.95%`

Delta from Wave624: `+8` commented, `-8` commentless, `-1` exact-undefined signature, `-7` `param_N`, and `+8` strict clean-signature rows.

The next high-signal queue head is `0x00560b80 CTexture__InitializeThreadLocalRecordDefaults`.

## Boundaries

This is static saved-Ghidra startup/CRT EH evidence only. Exact CRT identity/version, exact C++ exception metadata layouts, full process lifetime behavior, runtime exception/error behavior, BEA patching, and rebuild parity remain deferred.
