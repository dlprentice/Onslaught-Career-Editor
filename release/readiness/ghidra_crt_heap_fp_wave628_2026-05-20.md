# Ghidra CRT Heap/FPU Wave628

Status: read-back verified
Date: 2026-05-20

Wave628 hardened eleven adjacent CRT heap and floating-point helper rows in the saved Ghidra project:

- `0x0056202e CRT__ReallocBase`
- `0x0056235d CRT__MsizeByPointer`
- `0x0056244b CRT__HandleDomainErrorAndReturnInput`
- `0x005627ea CRT__AdjustFloatingPointForFormatFlags`
- `0x00562a01 CRT__HandleFpStatusAndReturnDouble`
- `0x00562a89 CRT__SetErrnoForFpSourceKind`
- `0x00562ab1 CRT__MapFpStatusToErrorCode`
- `0x00562ad6 CRT__MapFormatFlagsToSourceKind`
- `0x00562b15 CRT__BuildNormalizedDoubleFromParts`
- `0x00562b3e CRT__ClassifyDoubleWordsCore`
- `0x00562b98 CRT__Frexp`

The pass corrected three stale labels (`CDXTexture__ValidateSourceAndSetLoadErrorClass`, `CDXTexture__SetLoadErrorClassBySourceKind`, and `CFastVB__ClassifyDoubleWords`), saved eleven signatures/comments/tags, and made no function-boundary or executable-byte changes.

## Evidence

- Dry run: `updated=0 skipped=11 renamed=0 would_rename=3 signature_updated=0 missing=0 bad=0`
- Apply: `updated=11 skipped=0 renamed=3 would_rename=0 signature_updated=11 missing=0 bad=0`
- Final dry: `updated=0 skipped=11 renamed=0 would_rename=0 signature_updated=0 missing=0 bad=0`
- Post exports: `11` metadata rows, `11` tag rows, `23` xref rows, `2871` instruction rows, `11` decompile rows
- Queue refresh: `6093` total, `3317` commented, `2776` commentless, `1217` exact-undefined signatures, `973` `param_N` signatures
- Strict clean-signature proxy: `3265/6093 = 53.59%`
- Verified backup: `G:\GhidraBackups\BEA_20260520-074256_post_wave628_crt_heap_fp_verified` (`19` files, `162139015` bytes, `DiffCount=0`)

The next high-signal queue head is `0x00562cef CRT__InputFormatCore`.

## Limits

This is static saved-Ghidra evidence only. Exact CRT identity/version, exact small-block heap, FILE, FPU, errno, qnan, and format-parser semantics, runtime heap/FPU/printf/input behavior, BEA patching, and rebuild parity remain unproven.
