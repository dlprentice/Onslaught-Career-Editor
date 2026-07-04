# Ghidra CRT Input-Scan Wave629

Status: read-back verified
Date: 2026-05-20

Wave629 hardened nine adjacent CRT input-scan, stream, ctype, and float-parser helper rows in the saved Ghidra project:

- `0x00562cef CRT__InputFormatCore`
- `0x00563714 CRT__NormalizeDigitForBase`
- `0x0056374b CRT__GetCharFromStream`
- `0x00563765 CRT__UngetCharIfNotEof`
- `0x0056377c CRT__GetNonSpaceCharFromStream`
- `0x0056381b CRT__EnsureStdStreamBufferForCommitMode`
- `0x005638a8 CRT__FlushStreamIfWritePending`
- `0x005638d2 CRT__ParseFloatTextToFloatAndStatus`
- `0x00563951 CRT__GetCharTypeMask_Compat`

The pass saved nine signatures/comments/tags, corrected `CRT__GetCharTypeMask_Compat` from a stale ECX/EDI-inflated signature to the observed two stack arguments, and made no function-boundary or executable-byte changes.

## Evidence

- Dry run: `updated=0 skipped=0 renamed=0 would_rename=0 signature_updated=0 missing=0 bad=0`
- Apply: `updated=9 skipped=0 renamed=0 would_rename=0 signature_updated=9 missing=0 bad=0`
- Final dry: `updated=0 skipped=9 renamed=0 would_rename=0 signature_updated=0 missing=0 bad=0`
- Post exports: `9` metadata rows, `9` tag rows, `68` xref rows, `333` instruction rows, `9` decompile rows
- Queue refresh: `6093` total, `3326` commented, `2767` commentless, `1217` exact-undefined signatures, `964` `param_N` signatures
- Strict clean-signature proxy: `3274/6093 = 53.73%`
- Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260520-081613_post_wave629_crt_input_scan_verified` (`19` files, `162204551` bytes, `DiffCount=0`)

The next high-signal queue head is `0x00564486 CRT__FmodReduceCore`.

## Limits

This is static saved-Ghidra evidence only. Exact CRT identity/version, exact FILE/va_list/locale/scanset/float parse-record layouts, runtime scanf/stdio behavior, BEA patching, and rebuild parity remain unproven.
