# Ghidra CRT Case Conversion Wave640

Status: read-back verified
Date: 2026-05-20

Wave640 hardened two adjacent CRT lowercase/case-conversion rows in the saved Ghidra project:

- `0x005695af CRT__ToLowerWithLocaleLock`
- `0x0056961e CRT__ToLowerWithLocale`

The pass corrected `CRT__ToLower_005695af` to `CRT__ToLowerWithLocaleLock`, corrected stale `CMCBuggy__ToLowerLocaleAware` to `CRT__ToLowerWithLocale`, saved signatures/comments/tags for both rows, and made no function-boundary or executable-byte changes.

## Evidence

- Dry run: `updated=0 skipped=2 renamed=0 would_rename=2 signature_updated=0 missing=0 bad=0`
- Apply: `updated=2 skipped=0 renamed=2 would_rename=0 signature_updated=2 missing=0 bad=0`
- Final dry: `updated=0 skipped=2 renamed=0 would_rename=0 signature_updated=0 missing=0 bad=0`
- Post exports: `2` metadata rows, `2` tag rows, `14` xref rows, `178` instruction rows, `2` decompile rows
- Queue refresh: `6093` total, `3409` commented, `2684` commentless, `1217` exact-undefined signatures, `896` `param_N` signatures
- Strict clean-signature proxy: `3358/6093 = 55.11%`
- Verified backup: `G:\GhidraBackups\BEA_20260520-131150_post_wave640_crt_case_conversion_verified` (`19` files, `162532231` bytes, `DiffCount=0`)

The next high-signal queue head is `0x005696e9 CRT__AreHigherMaskBitsClear`.

## Limits

This is static saved-Ghidra evidence only. Exact MSVC CRT version, full locale/codepage behavior, `LCMapStringA` edge-case equivalence, runtime parser/texture/comparison behavior, BEA patching, and rebuild parity remain unproven.
