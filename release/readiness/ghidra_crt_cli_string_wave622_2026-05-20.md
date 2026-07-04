# Ghidra CRT/CLI String Wave622 Readiness Note

Status: complete
Date: 2026-05-20

## Scope

Wave622 hardened ten CRT/CLI string, parser, wide-string, and locale helper rows in the saved Ghidra project:

- `0x0055e14f CRT__SscanfFromString`
- `0x0055e183 CRT__PrintfStdoutLocked`
- `0x0055e1c4 CRT__ParseDoubleSkippingWhitespace`
- `0x0055e21b CRT__ParseDecimalIntA`
- `0x0055e2a6 CRT__ParseDecimalIntA_Thunk`
- `0x0055e598 ControlsUI__FormatWideStringSafe`
- `0x0055e624 CRT__WStrCat`
- `0x0055e64e CRT__WStrCpy`
- `0x0055e673 CRT__ToUpperWithLocaleLock`
- `0x0055e6e2 CRT__ToUpperWithLocale`

The pass saved bounded signatures, comments, and tags. It corrected five stale or too-narrow labels: `CLIParams__ScanFormatFromString`, `CFastVB__DispatchLockedRoute_6533e0`, `CConsole__ParseFloatSkippingWhitespace`, `CSoundManager__ParseDecimalToken`, and `ControlsUI__WideStrCat`. It made no function-boundary changes and no executable byte changes.

## Evidence

- Dry/apply/final-dry logs reported `updated=0 skipped=10 renamed=0 would_rename=5 varargs=0 missing=0 bad=0`, then `updated=10 skipped=0 renamed=5 would_rename=0 varargs=3 missing=0 bad=0`, then `updated=0 skipped=10 renamed=0 would_rename=0 varargs=0 missing=0 bad=0`, with `REPORT: Save succeeded`.
- Post-state exports verified `10` metadata rows, `10` tag rows, `198` xref rows, `610` instruction rows, and `10` decompile rows.
- String scan evidence covers an input descriptor built from the input pointer and `_strlen(input)`, then a call into `CRT__InputFormatCore` with the format pointer and varargs.
- Formatted output evidence covers the route-key `0x6533e0` lock/format/flush/unlock wrapper over `CRT__FormatOutputToStream`.
- Parser evidence covers whitespace-skipping float parsing, decimal integer sign/digit handling, and a broad decimal parser thunk used outside the old sound-manager owner label.
- Wide-string evidence covers ControlsUI wide-format output, broad `WStrCat`, and broad `WStrCpy` use across frontend/game-interface/message/ControlsUI callers.
- Locale evidence covers the uppercase fast path, lock index `0x13`, ctype checks, and the `CRT__LCMapStringA_Compat` path.
- Backup verified: `[maintainer-local-ghidra-backup-root]\BEA_20260520-045112_post_wave622_cli_crt_string_verified` with `19` files, `161909639` bytes, and `DiffCount=0`.

## Queue Telemetry

Post-Wave622 queue telemetry:

- Total functions: `6093`
- Commented functions: `3244`
- Commentless functions: `2849`
- Exact `undefined` signatures: `1218`
- `param_N` signatures: `1036`
- Comment-backed proxy: `3244/6093 = 53.24%`
- Strict clean-signature proxy: `3192/6093 = 52.39%`

Delta from Wave621: `+10` commented, `-10` commentless, `0` exact-undefined signatures, `-10` `param_N`, and `+10` strict clean-signature rows.

The next high-signal queue head is `0x0055e7ae Sort__QuickSortGeneric`.

## Boundaries

This is static saved-Ghidra CRT/CLI string helper evidence only. Exact CRT identity/version, full format/parser/locale semantics, runtime command-line/UI text behavior, BEA patching, and rebuild parity remain deferred.
