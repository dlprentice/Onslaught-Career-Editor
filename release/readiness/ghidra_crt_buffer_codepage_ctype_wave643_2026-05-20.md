# Ghidra CRT Buffer/Codepage/Ctype Wave643 Readiness Note

Date: 2026-05-20
Status: ready for public-safe release accounting

## Scope

Wave643 saved signatures, comments, and tags for twelve adjacent CRT stream-buffer, codepage conversion, and ctype rows:

| Address | Saved state |
| --- | --- |
| `0x00569d91` | `void __cdecl CRT__InitFileBuffer(void * stream)` |
| `0x00569dd5` | `int __cdecl CRT__IsFdCommitMode(uint fdIndex)` |
| `0x00569dfe` | `int __cdecl CRT__WideCharToCurrentCodePage_WithLocaleGuard(char * outBytes, int wideChar)` |
| `0x00569e57` | `int __cdecl CRT__WideCharToCurrentCodePage(char * outBytes, int wideChar)` |
| `0x00569f35` | `int __cdecl CRT__MultiByteToWideChar_ThreadSafe(void * outWideChar, char * inputBytes, uint inputByteCount)` |
| `0x00569f92` | `uint __cdecl CRT__MultiByteToWideChar_SingleToken(void * outWideChar, char * inputBytes, uint inputByteCount)` |
| `0x0056a05b` | `uint __cdecl CRT__IsAlpha(int charValue)` |
| `0x0056a089` | `uint __cdecl CRT__IsDigit(int charValue)` |
| `0x0056a0b1` | `uint __cdecl CRT__IsCharTypeMask0x80(int charValue)` |
| `0x0056a0de` | `uint __cdecl CRT__IsCharTypeMask0x08(int charValue)` |
| `0x0056a106` | `uint __cdecl CRT__GetCharClassMask(int charValue)` |
| `0x0056a15f` | `uint __cdecl CRT__UngetCharToStream(uint character, void * stream)` |

The pass corrected `CRT__IsAlpha_0056a05b` to `CRT__IsAlpha` and `CRT__IsDigit_0056a089` to `CRT__IsDigit`. No function-boundary changes or executable-byte changes were made.

## Evidence

- Script: `tools/ApplyCrtBufferCodepageCtypeWave643.java`
- Probe: `tools/ghidra_crt_buffer_codepage_ctype_wave643_probe.py`
- Scratch/read-back artifacts: `subagents/ghidra-static-reaudit/wave643-crt-buffer-codepage-ctype/`
- Dry/apply/final dry summaries:
  - `updated=0 skipped=12 renamed=0 would_rename=2 signature_updated=0 missing=0 bad=0`
  - `updated=12 skipped=0 renamed=2 would_rename=0 signature_updated=12 missing=0 bad=0`
  - `updated=0 skipped=12 renamed=0 would_rename=0 signature_updated=0 missing=0 bad=0`
- Post exports: `12` metadata rows, `12` tag rows, `53` xref rows, `3132` instruction rows, and `12` decompile rows.
- Queue after Wave643: `6093` total functions, `3437` commented, `2656` commentless, `1217` exact-undefined signatures, and `868` `param_N` signatures.
- Comment-backed proxy: `3437/6093 = 56.41%`.
- Strict clean-signature proxy: `3386/6093 = 55.57%`.
- Next high-signal queue head: `0x0056a7e7 CRT__ValidatePathAttributesForOpen`.
- Verified backup: `G:\GhidraBackups\BEA_20260520-143149_post_wave643_crt_buffer_codepage_ctype_verified`, `19` files, `162663303` bytes, `DiffCount=0`.

## Boundaries

This is static CRT I/O, codepage, and ctype evidence only. Exact MSVC CRT version, full `FILE`/fd-table layouts, locale/codepage/global layouts, Windows API parity, signed-char/EOF behavior, runtime stream/conversion side effects, BEA patching, and rebuild parity remain unproven.
