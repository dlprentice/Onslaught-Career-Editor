# Ghidra CRT Locale Head Wave633

Status: read-back verified
Date: 2026-05-20

Wave633 hardened ten adjacent CRT locale, allocation callback, PE-version, and heap-selector bridge rows in the saved Ghidra project:

- `0x0056586a CRT__SetLocale`
- `0x00565ab0 CRT__SetLocaleCategory`
- `0x00565bcb CRT__BuildCompositeLocaleString`
- `0x00565c84 CRT__ResolveLocaleNameAndMetadata`
- `0x00565d9c CRT__StrCatVarArgs`
- `0x00565dc1 CRT__ParseLocaleSpecifierTriple`
- `0x00565e8d CRT__ComposeLocaleSpecifierFromTriple`
- `0x00566104 CRT__InvokeNewHandler`
- `0x0056611f CRT__ReadMainModulePeVersionBytes`
- `0x0056614c CRT__SelectHeapStrategy`

The pass corrected the stale `CRT__InvokeLocaleValidationCallback` label to the allocation new-handler shim `CRT__InvokeNewHandler`, saved signatures/comments/tags for all ten rows, set the varargs state on `CRT__StrCatVarArgs`, and made no function-boundary or executable-byte changes.

## Evidence

- Dry run: `updated=0 skipped=10 renamed=0 would_rename=1 signature_updated=0 varargs=0 missing=0 bad=0`
- Apply: `updated=10 skipped=0 renamed=1 would_rename=0 signature_updated=10 varargs=1 missing=0 bad=0`
- Final dry: `updated=0 skipped=10 renamed=0 would_rename=0 signature_updated=0 varargs=0 missing=0 bad=0`
- Post exports: `10` metadata rows, `10` tag rows, `23` xref rows, `1450` instruction rows, `10` decompile rows
- Queue refresh: `6093` total, `3354` commented, `2739` commentless, `1217` exact-undefined signatures, `940` `param_N` signatures
- Strict clean-signature proxy: `3302/6093 = 54.19%`
- Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260520-101020_post_wave633_crt_locale_head_verified` (`19` files, `162368391` bytes, `DiffCount=0`)

The next high-signal queue head is `0x00566294 CRT__InitializeHeapSubsystem`.

## Limits

This is static saved-Ghidra evidence only. Exact MSVC CRT version, complete locale table/triple layout, exact new-handler API identity, heap strategy environment grammar, runtime locale/OOM/heap-selection behavior, BEA patching, and rebuild parity remain unproven.
