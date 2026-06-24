# Ghidra CRT Command-Line/Runtime Wave638

Status: read-back verified
Date: 2026-05-20

Wave638 hardened eleven adjacent CRT command-line, environment, runtime-error, and pointer-probe rows in the saved Ghidra project:

- `0x00568dc6 CRT__ParseCommandLineToken`
- `0x00568e1e CRT__BuildEnvironTable`
- `0x00568ed7 CRT__BuildArgvTable`
- `0x00568f70 CRT__ParseCommandLineToArgv`
- `0x00569124 CRT__GetEnvironmentStringsDupA`
- `0x00569256 CRT__ReportRuntimeErrorIfCriticalMode`
- `0x0056928f CRT__ReportRuntimeError`
- `0x005693e2 CRT__IsReadablePtr`
- `0x005693fe CRT__IsWritablePtr`
- `0x0056941a CRT__IsExecutablePtr`
- `0x00569432 CRT__FatalRuntimeErrorAndExit`

The pass corrected `CRT__GetEnvironmentStringsDupA_00569124` to `CRT__GetEnvironmentStringsDupA`, saved signatures/comments/tags for all eleven rows, and made no function-boundary or executable-byte changes.

## Evidence

- Dry run: `updated=0 skipped=11 renamed=0 would_rename=1 signature_updated=0 varargs=0 missing=0 bad=0`
- Apply: `updated=11 skipped=0 renamed=1 would_rename=0 signature_updated=11 varargs=0 missing=0 bad=0`
- Final dry: `updated=0 skipped=11 renamed=0 would_rename=0 signature_updated=0 varargs=0 missing=0 bad=0`
- Post exports: `11` metadata rows, `11` tag rows, `26` xref rows, `1331` instruction rows, `11` decompile rows
- Queue refresh: `6093` total, `3403` commented, `2690` commentless, `1217` exact-undefined signatures, `902` `param_N` signatures
- Strict clean-signature proxy: `3352/6093 = 55.01%`
- Verified backup: `G:\GhidraBackups\BEA_20260520-122438_post_wave638_crt_commandline_runtime_verified` (`19` files, `162532231` bytes, `DiffCount=0`)

The next high-signal queue head is `0x00569449 CRT__ControlFp`.

## Limits

This is static saved-Ghidra evidence only. Exact MSVC CRT version, full command-line quoting/multibyte equivalence, environment and argv global startup-state layouts, environment-block lifetime, codepage policy, runtime-error table identity, UI/console behavior, Windows pointer-probe reliability, callback ABI, process-start/spawn/exception/process-exit behavior, BEA patching, and rebuild parity remain unproven.
