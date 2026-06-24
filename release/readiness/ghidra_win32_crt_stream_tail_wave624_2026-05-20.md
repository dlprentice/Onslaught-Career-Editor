# Ghidra Win32/CRT Stream Tail Wave624 Readiness Note

Status: complete
Date: 2026-05-20

## Scope

Wave624 hardened fourteen adjacent Win32, CRT, stream, locale, math, and texture helper rows in the saved Ghidra project:

- `0x0055f5ee Win32__FindFirstFileWithMeta`
- `0x0055f6bb Win32__FindNextFileWithMeta`
- `0x0055f783 Win32__FindCloseWithErrno`
- `0x0055f807 CRT__MbsNcpy_LocaleLock`
- `0x0055f8a1 CRT__MbsIcmp_LocaleLock`
- `0x0055fa62 CRT__PowCoreWithFpuGuards`
- `0x0055fc5d CD3DApplication__ReadLineFromStreamLocked`
- `0x0055fe26 CRT__LockRouteByAddress`
- `0x0055fe55 CRT__LockRouteByIndex`
- `0x0055fe78 CRT__UnlockRouteByAddress`
- `0x0055fea7 CRT__UnlockRouteByIndex`
- `0x0055feca CRT__FTellWithRouteLock`
- `0x0055feec CRT__FTellAdjusted`
- `0x0056004d CDXTexture__AsciiToLowerInPlace`

The pass saved bounded signatures, comments, and tags. It corrected one stale address-suffixed label: `CRT__PowCore_0055fa62` is now `CRT__PowCoreWithFpuGuards`. It made no function-boundary changes and no executable byte changes.

## Evidence

- Dry/apply/final-dry logs reported `updated=0 skipped=14 renamed=0 would_rename=1 missing=0 bad=0`, then `updated=14 skipped=0 renamed=1 would_rename=0 missing=0 bad=0`, then `updated=0 skipped=14 renamed=0 would_rename=0 missing=0 bad=0`, with `REPORT: Save succeeded`.
- Post-state exports verified `14` metadata rows, `14` tag rows, `51` xref rows, `1470` instruction rows, and `14` decompile index rows. Thirteen target decompiles exported cleanly; `0x0055fa62 CRT__PowCoreWithFpuGuards` remains decompile-limited with overlapping input varnodes, so its saved comment is instruction-backed rather than clean-decompile-backed.
- Win32 find evidence covers `FindFirstFileA`, `FindNextFileA`, and `FindClose` wrappers used by save-file enumeration, including file metadata packing and CRT errno mapping.
- Locale/string evidence covers multibyte strncpy and case-insensitive compare helpers under CRT locale lock route `0x19`.
- Math evidence covers the x87 pow core behind `CRT__PowDispatch_ST0_ST1`, including FPU-control checks and pow-domain edge handling.
- Stream evidence covers locked stream line reading, route lock/unlock helpers, locked ftell, and adjusted ftell text-mode/newline accounting.
- Texture evidence covers `CDXTexture__AsciiToLowerInPlace`, including ASCII fast-path folding and locale-aware `LCMapStringA` fallback.
- Backup verified: `G:\GhidraBackups\BEA_20260520-054923_post_wave624_win32_crt_stream_verified` with `19` files, `161942407` bytes, and `DiffCount=0`.

## Queue Telemetry

Post-Wave624 queue telemetry:

- Total functions: `6093`
- Commented functions: `3270`
- Commentless functions: `2823`
- Exact `undefined` signatures: `1218`
- `param_N` signatures: `1010`
- Comment-backed proxy: `3270/6093 = 53.67%`
- Strict clean-signature proxy: `3218/6093 = 52.81%`

Delta from Wave623: `+14` commented, `-14` commentless, `0` exact-undefined signatures, `-14` `param_N`, and `+14` strict clean-signature rows.

The next high-signal queue head is `0x00560181 entry`.

## Boundaries

This is static saved-Ghidra Win32/CRT/stream/texture helper evidence only. Exact CRT identity/version, exact stream/file metadata layouts, full locale/math/text-mode semantics, runtime save enumeration/audio/cardid/texture-path behavior, BEA patching, and rebuild parity remain deferred.
