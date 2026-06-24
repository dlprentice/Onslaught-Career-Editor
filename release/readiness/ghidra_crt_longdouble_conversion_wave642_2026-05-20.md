# Ghidra CRT Long-Double Conversion Wave642 Readiness Note

Date: 2026-05-20
Status: ready for public-safe release accounting

## Scope

Wave642 saved signatures, comments, and tags for nine adjacent CRT floating-point conversion rows:

| Address | Saved state |
| --- | --- |
| `0x005698e3` | `int __cdecl CRT__ConvertLongDoubleByFormatSpec(void * longDouble80, void * outBits, void * formatSpec)` |
| `0x00569a4f` | `void __cdecl CRT__ConvertLongDoubleToFloat32(void * longDouble80, void * outFloat32Bits)` |
| `0x00569a65` | `void __cdecl CRT__ConvertLongDoubleToFloat64(void * longDouble80, void * outFloat64Bits)` |
| `0x00569a7b` | `void __cdecl CRT__ParseFloatTextToFloat32(void * outFloat32Bits, int parseFlags)` |
| `0x00569aa8` | `void __cdecl CRT__ParseFloatTextToFloat64(void * outFloat64Bits, int parseFlags)` |
| `0x00569ad5` | `void __cdecl CRT__BuildRoundedMantissaDigits(char * outDigits, int requestedDigits, void * decimalRecord)` |
| `0x00569b4c` | `int * __cdecl CRT__ConvertLongDoubleToDecimalRecord(int inputLowBits, int inputHighBits, void * decimalRecord, char * digitsBuffer)` |
| `0x00569ba8` | `void __cdecl CRT__NormalizeLongDouble80MantissaExp(void * outLongDouble80, void * float64Bits)` |
| `0x00569cc1` | `void __cdecl CRT__HandleFloatingPointException(int unusedStatus, void * fpExceptionRecord, void * controlWordPtr)` |

No renames, function-boundary changes, or executable-byte changes were made.

## Evidence

- Script: `tools/ApplyCrtLongDoubleConversionWave642.java`
- Probe: `tools/ghidra_crt_longdouble_conversion_wave642_probe.py`
- Scratch/read-back artifacts: `subagents/ghidra-static-reaudit/wave642-crt-longdouble-conversion/`
- Dry/apply/final dry summaries:
  - `updated=0 skipped=9 renamed=0 would_rename=0 signature_updated=0 missing=0 bad=0`
  - `updated=9 skipped=0 renamed=0 would_rename=0 signature_updated=9 missing=0 bad=0`
  - `updated=0 skipped=9 renamed=0 would_rename=0 signature_updated=0 missing=0 bad=0`
- Post exports: `9` metadata rows, `9` tag rows, `16` xref rows, `2349` instruction rows, and `9` decompile rows.
- Queue after Wave642: `6093` total functions, `3425` commented, `2668` commentless, `1217` exact-undefined signatures, and `880` `param_N` signatures.
- Comment-backed proxy: `3425/6093 = 56.21%`.
- Strict clean-signature proxy: `3374/6093 = 55.37%`.
- Next high-signal queue head: `0x00569d91 CRT__InitFileBuffer`.
- Verified backup: `G:\GhidraBackups\BEA_20260520-140845_post_wave642_crt_longdouble_conversion_verified`, `19` files, `162597767` bytes, `DiffCount=0`.

## Boundaries

This is static CRT floating-point conversion evidence only. Exact MSVC CRT version, exact 80-bit/96-bit/decimal-record/control-word layouts, parser input/cursor contract, runtime numeric/rounding/FPU side effects, BEA patching, and rebuild parity remain unproven.
