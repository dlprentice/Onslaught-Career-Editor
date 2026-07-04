# Ghidra CRT DST/Floating-Point/Signal Wave646 Readiness Note

Date: 2026-05-20
Status: ready for public-safe release accounting

## Scope

Wave646 saved signatures, comments, and tags for eleven adjacent CRT runtime-helper rows:

| Address | Saved state |
| --- | --- |
| `0x0056ce69` | `bool __cdecl CRT__IsInDst_WrapperLocked(void * localTimeFields)` |
| `0x0056ce8a` | `bool __cdecl CRT__IsInDst(void * localTimeFields)` |
| `0x0056d036` | `int __cdecl CRT__ComputeDstTransitionDayMillis(int transitionKind, int ruleType, uint year, int monthIndex, int weekOfMonth, int dayOfWeek, int dayOfMonth, int hour, int minute, int second, int millisecond)` |
| `0x0056d176` | `bool __cdecl CRT__IsFiniteDoubleWords(double value)` |
| `0x0056d18a` | `int __cdecl CRT__ClassifyDoubleWords(double value)` |
| `0x0056d21c` | `int __cdecl CRT__IsDigitCharTypeMask_Thunk(int charValue)` |
| `0x0056d22d` | `int __cdecl CRT__IsCharTypeMaskOrLeadByte(int charValue, uint leadByteMask, int ctypeMask)` |
| `0x0056d25e` | `int __cdecl CRT__MessageBoxA_WithActivePopupFallback(char * messageText, char * captionText, uint styleFlags)` |
| `0x0056d2e7` | `int __cdecl CRT__RaiseSignal(int signalNumber)` |
| `0x0056d469` | `void * __cdecl CRT__FindSignalActionEntry(int signalNumber, void * signalTable)` |
| `0x0056d4a6` | `int __cdecl CRT__UIntAddWithOverflowCheck(uint lhs, uint rhs, uint * outSum)` |

The pass corrected the suffix-style `CRT__IsCharTypeMaskOrLeadByte_0056d22d` label to `CRT__IsCharTypeMaskOrLeadByte`. No function-boundary changes or executable-byte changes were made.

## Evidence

- Script: `tools/ApplyCrtDstFpSignalWave646.java`
- Probe: `tools/ghidra_crt_dst_fp_signal_wave646_probe.py`
- Scratch/read-back artifacts: `subagents/ghidra-static-reaudit/wave646-crt-dst-fp-signal/`
- Dry/apply/final dry summaries:
  - `updated=0 skipped=11 renamed=0 would_rename=1 signature_updated=0 missing=0 bad=0`
  - `updated=11 skipped=0 renamed=1 would_rename=0 signature_updated=11 missing=0 bad=0`
  - `updated=0 skipped=11 renamed=0 would_rename=0 signature_updated=0 missing=0 bad=0`
- Post exports: `11` metadata rows, `11` tag rows, `21` xref rows, `2431` instruction rows, and `11` decompile rows.
- Queue after Wave646: `6093` total functions, `3479` commented, `2614` commentless, `1217` exact-undefined signatures, and `826` `param_N` signatures.
- Comment-backed proxy: `3479/6093 = 57.10%`.
- Strict clean-signature proxy: `3428/6093 = 56.26%`.
- Next high-signal queue head: `0x0056d525 CRT__LongDoubleShiftMantissaLeft1_0056d525`.
- Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260520-160110_post_wave646_crt_dst_fp_signal_verified`, `19` files, `162761607` bytes, `DiffCount=0`.

## Boundaries

This is static CRT daylight-saving interval, transition-boundary calculation, floating-point classification, ctype digit/lead-byte, runtime MessageBox fallback, signal dispatch/table-scan, and unsigned-add overflow helper evidence only. Exact MSVC CRT version, full timezone/TZ rule/global layouts, DST edge cases, double class-code identity, ctype/codepage table layouts, signal table/thread-local layouts, runtime MessageBox/signal/timezone/numeric behavior, BEA patching, and rebuild parity remain unproven.
