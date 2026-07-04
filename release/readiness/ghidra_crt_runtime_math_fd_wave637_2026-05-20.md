# Ghidra CRT Runtime/Math/Fd Wave637

Status: read-back verified
Date: 2026-05-20

Wave637 hardened ten adjacent CRT runtime/math/fd/SEH rows in the saved Ghidra project:

- `0x00568667 CRT__PowSpecialCaseCore`
- `0x00568797 CRT__PowClassifyIntegralExponent`
- `0x005687fc CRT__InitializeFileDescriptorTable`
- `0x005689b8 CRT__CallocWithRetry`
- `0x00568a51 CRT__UnlockHeap9_SbAllocPath`
- `0x00568ada CRT__UnlockHeap9_DeferredAllocPath`
- `0x00568b76 CRT__LseekFd`
- `0x00568bdb CRT__LseekFd_NoLock`
- `0x00568c4e CRT__StructuredExceptionFilterDispatch`
- `0x00568d8c CRT__FindExceptionActionEntry`

The pass corrected `CRT__CallocWithRetry_005689b8` to `CRT__CallocWithRetry` and corrected stale `CDXTexture__FindKeyedTripletEntry` to `CRT__FindExceptionActionEntry`, saved signatures/comments/tags for all ten rows, and made no function-boundary or executable-byte changes.

## Evidence

- Dry run: `updated=0 skipped=10 renamed=0 would_rename=2 signature_updated=0 varargs=0 missing=0 bad=0`
- Apply: `updated=10 skipped=0 renamed=2 would_rename=0 signature_updated=10 varargs=0 missing=0 bad=0`
- Final dry: `updated=0 skipped=10 renamed=0 would_rename=0 signature_updated=0 varargs=0 missing=0 bad=0`
- Post exports: `10` metadata rows, `10` tag rows, `28` xref rows, `370` instruction rows, `10` decompile rows
- Queue refresh: `6093` total, `3392` commented, `2701` commentless, `1217` exact-undefined signatures, `907` `param_N` signatures
- Strict clean-signature proxy: `3338/6093 = 54.78%`
- Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260520-115724_post_wave637_crt_runtime_math_fd_verified` (`19` files, `162499463` bytes, `DiffCount=0`)

The next high-signal queue head is `0x00568f70 CRT__ParseCommandLineToArgv`.

## Limits

This is static saved-Ghidra evidence only. Exact MSVC CRT version, complete pow edge-case equivalence, FPU status behavior, exact fd-table/exception-action/heap layouts, inherited handle semantics, large-file seek behavior, runtime math/file/process-start/exception/allocation behavior, BEA patching, and rebuild parity remain unproven.
