# Ghidra CRT Locale/String Tail Wave645 Readiness Note

<!-- ghidra-full-reaudit-20260713:start -->
> **2026-07-13 semantic revalidation:** Historical record; `0x0056c684` comment correction. The original text below remains provenance rather than current semantic authority. Use the [closeout](../../reverse-engineering/binary-analysis/ghidra-full-reaudit-closeout-2026-07-13.md); exact records are in `reverse-engineering/binary-analysis/ghidra-full-reaudit-corrections-2026-07-13.json` and `reverse-engineering/binary-analysis/ghidra-targeted-revalidation-corrections-2026-07-13.json`.
<!-- ghidra-full-reaudit-20260713:end -->

Date: 2026-05-20
Status: ready for public-safe release accounting

## Scope

Wave645 saved signatures, comments, and tags for twenty adjacent CRT locale/string rows:

| Address | Saved state |
| --- | --- |
| `0x0056b368` | `uint __cdecl CRT__WriteWideCharToStreamWithConversion(uint wideChar, void * stream)` |
| `0x0056b4f2` | `uint __cdecl CRT__LoadTimeLocaleInfoTable(void * timeLocaleInfo)` |
| `0x0056bba5` | `void __cdecl CRT__NormalizeLocaleGroupingStringInPlace(char * groupingText)` |
| `0x0056bca7` | `uint __cdecl CRT__LoadMonetaryLocaleInfoTable(void * monetaryLocaleInfo)` |
| `0x0056bdc9` | `void __cdecl CRT__FreeLocaleBufferSet(void * localeBufferSet)` |
| `0x0056c060` | `int __cdecl CRT__StrCSpn(char * text, char * rejectSet)` |
| `0x0056c0a0` | `char * __cdecl CRT__StrPBrk(char * text, char * acceptSet)` |
| `0x0056c0da` | `int __cdecl CRT__ResolveLocaleNameAndMetadata_NlsCore(char * localeTriple, ushort * outLocaleIds, char * outResolvedTriple)` |
| `0x0056c257` | `void __cdecl CRT__LocaleAliasBinarySearchRemap(void * aliasTable, int highIndex, char * * nameSlot)` |
| `0x0056c336` | `int __stdcall CRT__EnumLocalesCallback_MatchLanguageCountry(char * localeIdText)` |
| `0x0056c590` | `int __stdcall CRT__EnumLocalesCallback_MatchLanguageOnly(char * localeIdText)` |
| `0x0056c684` | `int __stdcall CRT__ValidateCodePageAgainstLocale(char * localeIdText)` |
| `0x0056c724` | `int __cdecl CRT__ResolveLocaleCodePageToken(char * codePageToken)` |
| `0x0056c78a` | `int __cdecl CRT__IsCodePageSupportedByLocaleMap(int localeId)` |
| `0x0056c7a9` | `int __cdecl CRT__ValidateLocaleLanguageMatch(int localeId, int requireExactLanguage)` |
| `0x0056c841` | `int __stdcall CRT__GetLocaleInfoACompatFallback(uint localeId, int localeInfoType, char * outBuffer, int outChars)` |
| `0x0056c927` | `int __cdecl CRT__ParseHexLocaleIdString(char * localeIdText)` |
| `0x0056c960` | `int __cdecl CRT__CountAlphaPrefix(char * text)` |
| `0x0056c981` | `int __cdecl CRT__StrToLong(char * text, char * * endPtr, int base)` |
| `0x0056cb9d` | `int __cdecl CRT__StrToLongWithBaseAndLocaleCType_Mode1Thunk(char * text, char * * endPtr, int base)` |

The pass corrected stale `CFastVB` owner labels on the locale grouping/monetary rows, removed address suffixes from supported string/locale helpers, and renamed the low-level locale resolver to an NLS-core label to keep it distinct from the earlier setlocale wrapper. No function-boundary changes or executable-byte changes were made.

## Evidence

- Script: `tools/ApplyCrtLocaleStringTailWave645.java`
- Probe: `tools/ghidra_crt_locale_string_tail_wave645_probe.py`
- Scratch/read-back artifacts: `subagents/ghidra-static-reaudit/wave645-crt-locale-string-tail/`
- Dry/apply/final dry summaries:
  - `updated=0 skipped=20 renamed=0 would_rename=13 signature_updated=0 missing=0 bad=0`
  - `updated=20 skipped=0 renamed=13 would_rename=0 signature_updated=20 missing=0 bad=0`
  - `updated=0 skipped=20 renamed=0 would_rename=0 signature_updated=0 missing=0 bad=0`
- Post exports: `20` metadata rows, `20` tag rows, `33` xref rows, `6420` instruction rows, and `20` decompile rows.
- Queue after Wave645: `6093` total functions, `3469` commented, `2624` commentless, `1217` exact-undefined signatures, and `836` `param_N` signatures.
- Comment-backed proxy: `3469/6093 = 56.93%`.
- Strict clean-signature proxy: `3418/6093 = 56.10%`.
- Next high-signal queue head: `0x0056ce69 CRT__IsInDst_WrapperLocked`.
- Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260520-152241_post_wave645_crt_locale_string_tail_verified`, `19` files, `162761607` bytes, `DiffCount=0`.

## Boundaries

This is static CRT wide-stream conversion, date/time and monetary locale-info loading, locale grouping normalization, locale alias/NLS resolution, string bitmap search, codepage-token parsing, compatibility `GetLocaleInfoA`, and string-to-long wrapper evidence only. Exact MSVC CRT version, full locale table/triple/global layouts, complete Windows NLS/API edge-case behavior, `EnumLocalesA` runtime callback ordering, full `lconv`/`LC_TIME` layout identity, string-to-long overflow/errno semantics, runtime stream conversion behavior, BEA patching, and rebuild parity remain unproven.
