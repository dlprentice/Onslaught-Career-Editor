# Ghidra CRT String/Codepage Wave636

Status: read-back verified
Date: 2026-05-20

Wave636 hardened five adjacent CRT string and multibyte codepage rows in the saved Ghidra project:

- `0x00567de0 CRT__StrCpyAligned`
- `0x00567df0 CRT__StrCatAligned`
- `0x00567f92 CRT__SetMultibyteCodePage`
- `0x0056813f CRT__ResolveMultibyteCodePage`
- `0x00568189 CRT__MapCodePageToLocaleId`

The pass corrected `CRT__SetMultibyteCodePage_00567f92` to `CRT__SetMultibyteCodePage`, corrected `CRT__ResolveMultibyteCodePage_0056813f` to `CRT__ResolveMultibyteCodePage`, corrected `CRT__MapCodePageToLocaleId_00568189` to `CRT__MapCodePageToLocaleId`, saved signatures/comments/tags for all five rows, and made no function-boundary or executable-byte changes.

## Evidence

- Dry run: `updated=0 skipped=5 renamed=0 would_rename=3 signature_updated=0 varargs=0 missing=0 bad=0`
- Apply: `updated=5 skipped=0 renamed=3 would_rename=0 signature_updated=5 varargs=0 missing=0 bad=0`
- Final dry: `updated=0 skipped=5 renamed=0 would_rename=0 signature_updated=0 varargs=0 missing=0 bad=0`
- Post exports: `5` metadata rows, `5` tag rows, `38` xref rows, `905` instruction rows, `5` decompile rows
- Queue refresh: `6093` total, `3382` commented, `2711` commentless, `1217` exact-undefined signatures, `914` `param_N` signatures
- Strict clean-signature proxy: `3328/6093 = 54.62%`
- Verified backup: `G:\GhidraBackups\BEA_20260520-113139_post_wave636_crt_string_codepage_verified` (`19` files, `162401159` bytes, `DiffCount=0`)

The next high-signal queue head is `0x00568667 CRT__PowSpecialCaseCore`.

## Limits

This is static saved-Ghidra evidence only. Exact MSVC CRT version, exact multibyte table layouts, caller string buffer capacities, overlap behavior, Windows NLS/API edge cases, runtime locale/string behavior, BEA patching, and rebuild parity remain unproven.
