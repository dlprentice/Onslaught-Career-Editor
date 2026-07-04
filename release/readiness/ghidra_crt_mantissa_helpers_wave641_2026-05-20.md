# Ghidra CRT Mantissa Helpers Wave641

Status: read-back verified
Date: 2026-05-20

Wave641 hardened seven adjacent CRT long-double mantissa helper rows in the saved Ghidra project:

- `0x005696e9 CRT__AreHigherMaskBitsClear`
- `0x00569732 CRT__PropagateMaskCarryBackward`
- `0x00569788 CRT__BitMaskClearFromIndexWithCarry`
- `0x00569814 CRT__Copy3DWords`
- `0x0056982f CRT__Zero3DWords`
- `0x0056983b CRT__Are3DWordsZero`
- `0x00569856 CRT__ShiftMantissaRight96`

The pass saved signatures/comments/tags for all seven rows, made no renames, and made no function-boundary or executable-byte changes.

## Evidence

- Dry run: `updated=0 skipped=7 renamed=0 would_rename=0 signature_updated=0 missing=0 bad=0`
- Apply: `updated=7 skipped=0 renamed=0 would_rename=0 signature_updated=7 missing=0 bad=0`
- Final dry: `updated=0 skipped=7 renamed=0 would_rename=0 signature_updated=0 missing=0 bad=0`
- Post exports: `7` metadata rows, `7` tag rows, `14` xref rows, `1547` instruction rows, `7` decompile rows, plus `1` context decompile row for `CRT__ConvertLongDoubleByFormatSpec`
- Queue refresh: `6093` total, `3416` commented, `2677` commentless, `1217` exact-undefined signatures, `889` `param_N` signatures
- Strict clean-signature proxy: `3365/6093 = 55.23%`
- Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260520-133643_post_wave641_crt_mantissa_helpers_verified` (`19` files, `162564999` bytes, `DiffCount=0`)

The next high-signal queue head is `0x005698e3 CRT__ConvertLongDoubleByFormatSpec`.

## Limits

This is static saved-Ghidra evidence only. Exact MSVC CRT version, 80-bit/96-bit record layout, floating-point conversion edge cases, runtime numeric behavior, BEA patching, and rebuild parity remain unproven.
