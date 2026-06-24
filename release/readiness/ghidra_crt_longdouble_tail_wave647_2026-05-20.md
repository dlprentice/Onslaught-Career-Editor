# Ghidra CRT Long-Double Tail Wave647 Readiness Note

Date: 2026-05-20
Status: ready for public-safe release accounting

## Scope

Wave647 saved signatures, comments, and tags for six adjacent CRT long-double tail rows:

| Address | Saved state |
| --- | --- |
| `0x0056d525` | `void __cdecl CRT__LongDoubleShiftMantissaLeft1(void * longDouble80)` |
| `0x0056d553` | `void __cdecl CRT__LongDoubleShiftMantissaRight1(void * longDouble80)` |
| `0x0056d580` | `void __cdecl CRT__AccumulateDecimalDigitsToLongDouble(char * digitBytes, int digitCount, void * outLongDouble80)` |
| `0x0056d647` | `int __cdecl CRT__ConvertLongDoubleToDecimalRecordCore(uint longDoubleLow, uint longDoubleMid, uint signExponentWord, int requestedDigits, uint conversionFlags, void * outDecimalRecord)` |
| `0x0056d8da` | `void __cdecl CRT__LongDoubleMultiply10Byte(void * accumulatorLongDouble80, void * multiplierLongDouble80)` |
| `0x0056dafa` | `void __cdecl CRT__LongDoubleScaleByPowerOf10(void * longDouble80, int decimalExponent, int preserveMantissaFlag)` |

The pass corrected four suffix-style helper labels: `CRT__LongDoubleShiftMantissaLeft1_0056d525`, `CRT__LongDoubleShiftMantissaRight1_0056d553`, `CRT__AccumulateDecimalDigitsToLongDouble_0056d580`, and `CRT__ConvertLongDoubleToDecimalRecord_0056d647`. No function-boundary changes or executable-byte changes were made.

## Evidence

- Script: `tools/ApplyCrtLongDoubleTailWave647.java`
- Probe: `tools/ghidra_crt_longdouble_tail_wave647_probe.py`
- Scratch/read-back artifacts: `subagents/ghidra-static-reaudit/wave647-crt-longdouble-tail/`
- Dry/apply/final dry summaries:
  - `updated=0 skipped=6 renamed=0 would_rename=4 signature_updated=0 missing=0 bad=0`
  - `updated=6 skipped=0 renamed=4 would_rename=0 signature_updated=6 missing=0 bad=0`
  - `updated=0 skipped=6 renamed=0 would_rename=0 signature_updated=0 missing=0 bad=0`
- Post exports: `6` metadata rows, `6` tag rows, `17` xref rows, `606` instruction rows, and `6` decompile rows.
- Queue after Wave647: `6093` total functions, `3485` commented, `2608` commentless, `1217` exact-undefined signatures, and `821` `param_N` signatures.
- Comment-backed proxy: `3485/6093 = 57.20%`.
- Strict clean-signature proxy: `3435/6093 = 56.38%`.
- Next high-signal queue head: `0x0056db76 CRT__ChangeFileSizeByFd_NoLock`.
- Verified backup: `G:\GhidraBackups\BEA_20260520-162946_post_wave647_crt_longdouble_tail_verified`, `19` files, `162827143` bytes, `DiffCount=0`.

## Boundaries

This is static CRT long-double mantissa shift, decimal digit accumulation, decimal-record conversion, 10-byte multiply, and power-of-ten scaling evidence only. Exact MSVC CRT version, exact 80-bit/96-bit/decimal-record layouts, decimal rounding edge cases, parser input/cursor contract, runtime numeric/FPU side effects, BEA patching, and rebuild parity remain unproven.
