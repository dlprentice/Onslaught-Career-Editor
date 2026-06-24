# Ghidra CRT/FPU/Format Wave627

Status: read-back verified
Date: 2026-05-20

Wave627 hardened eleven adjacent CRT/FPU/format helper rows in the saved Ghidra project:

- `0x00561618 CRT__ExtractFiniteExponentMaskOrPassThrough`
- `0x0056162e CRT__MathErrorHook_NoOp`
- `0x0056163b __math_exit`
- `0x00561679 CRT__HandleFpuExceptionForMathOp`
- `0x0056171c CRT__FlsBuf`
- `0x00561834 CRT__FormatOutputToStream`
- `0x00561f75 CRT__PutCharToStreamAndCount`
- `0x00561faa CRT__PutCharRepeatedToStream`
- `0x00561fdb CRT__PutStringToStream`
- `0x00562013 CRT__ReadIntAndAdvanceArgList`
- `0x00562020 CRT__ReadFormatWordAndAdvance`

The pass corrected two names, saved nine signatures, and intentionally left `CRT__MathErrorHook_NoOp` plus `__math_exit` as comment/tag-only custom-stack helpers. It made no function-boundary or executable-byte changes.

## Evidence

- Dry run: `updated=0 skipped=11 renamed=0 would_rename=2 signature_updated=0 missing=0 bad=0`
- Apply: `updated=11 skipped=0 renamed=2 would_rename=0 signature_updated=9 missing=0 bad=0`
- Final dry: `updated=0 skipped=11 renamed=0 would_rename=0 signature_updated=0 missing=0 bad=0`
- Post exports: `11` metadata rows, `11` tag rows, `63` xref rows, `979` instruction rows, `11` decompile rows
- Queue refresh: `6093` total, `3306` commented, `2787` commentless, `1217` exact-undefined signatures, `984` `param_N` signatures
- Strict clean-signature proxy: `3254/6093 = 53.41%`
- Verified backup: `G:\GhidraBackups\BEA_20260520-070942_post_wave627_crt_fpu_format_verified` (`19` files, `162106247` bytes, `DiffCount=0`)

The next high-signal queue head is `0x0056202e CRT__ReallocBase`.

## Limits

This is static saved-Ghidra evidence only. Exact CRT identity/version, exact FILE and va_list layouts, nonstandard stack cleanup semantics for the two math helpers, runtime FPU/printf/I/O behavior, BEA patching, and rebuild parity remain unproven.
