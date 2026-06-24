# Ghidra ControlsUI Wide Format Wave632

Status: read-back verified
Date: 2026-05-20

Wave632 hardened five adjacent ControlsUI wide-format and CRT vararg-reader rows in the saved Ghidra project:

- `0x00565083 ControlsUI__FormatWideStringCore`
- `0x005657d0 ControlsUI__WriteWideCharAndCount`
- `0x005657f0 ControlsUI__WriteRepeatedWideChar`
- `0x00565821 ControlsUI__WriteWideStringAndCount`
- `0x0056585a CRT__ReadLongLongAndAdvanceArgList`

The pass corrected `CRT__MapWideCharsWithCallbackStopOnError` to the ControlsUI-specific `ControlsUI__WriteWideStringAndCount`, corrected `CRT__ReadIntAndAdvance8` to the 64-bit `CRT__ReadLongLongAndAdvanceArgList`, saved signatures/comments/tags for all five rows, and made no function-boundary or executable-byte changes.

## Evidence

- Dry run: `updated=0 skipped=5 renamed=0 would_rename=2 signature_updated=0 missing=0 bad=0`
- Apply: `updated=5 skipped=0 renamed=2 would_rename=0 signature_updated=5 missing=0 bad=0`
- Final dry: `updated=0 skipped=5 renamed=0 would_rename=0 signature_updated=0 missing=0 bad=0`
- Post exports: `5` metadata rows, `5` tag rows, `12` xref rows, `505` instruction rows, `5` decompile rows
- Queue refresh: `6093` total, `3344` commented, `2749` commentless, `1217` exact-undefined signatures, `948` `param_N` signatures
- Strict clean-signature proxy: `3292/6093 = 54.03%`
- Verified backup: `G:\GhidraBackups\BEA_20260520-094434_post_wave632_controlsui_wide_format_verified` (`19` files, `162302855` bytes, `DiffCount=0`)

The next high-signal queue head is `0x0056586a CRT__SetLocale`.

## Limits

This is static saved-Ghidra evidence only. Exact CRT identity/version, full wide-format and locale edge cases, concrete output descriptor and `va_list` layouts, runtime ControlsUI text behavior, BEA patching, and rebuild parity remain unproven.
