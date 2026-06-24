# Ghidra DInput/CRT Tail Wave740 Readiness Note

Status: passed
Date: 2026-05-22

Wave740 DInput/CRT tail saved comments/tags/signatures for ten adjacent DirectInput, frontend-save wide-string, and CRT helper rows with the `dinput-crt-tail-wave740` and `wave740-readback-verified` tags. The pass hardened ten signatures, made no renames, made no function-boundary changes, and made no executable-byte changes.

| Address | Saved signature | Static evidence |
| --- | --- | --- |
| `0x005d04e0 DirectInput8Create` | `int __stdcall DirectInput8Create(void * hinstance, uint directinput_version, void * riid_directinput8, void * * directinput_out, void * outer_unknown)` | Six-byte `DINPUT8.DLL` import thunk through IAT pointer `0x005d8020`; `PlatformInput__InitDirectInput` callsite `0x00513178` pushes hinstance, version `0x800`, IID pointer `0x0060c14c`, interface output `ESI`, and null outer pointer before checking returned EAX. |
| `0x005d04ec CFEPSaveGame__WideStrCaseInsensitiveCompare` | `int __cdecl CFEPSaveGame__WideStrCaseInsensitiveCompare(ushort * left_wide, ushort * right_wide)` | Xrefs from `EnumerateSaveFiles_Main` and `CFEPSaveGame__CreateSave` push two wide-string pointers; the body folds ASCII A-Z or calls `CFEPSaveGame__WideCharToLowerCompat` for locale-aware comparison. |
| `0x005d070f CRT__VsnprintfAndTerminate_005d070f` | `int __cdecl CRT__VsnprintfAndTerminate_005d070f(char * out_buffer, int out_buffer_size, char * format, void * va_list_args)` | Texture and CFastVB diagnostic xrefs push output buffer, size, format, and va_list pointer; the body routes through `CRT__FormatOutputToStream` and terminates the buffer. |
| `0x005d075f CRT__FormatToBufferAndTerminate` | `int __cdecl CRT__FormatToBufferAndTerminate(char * out_buffer, int out_buffer_size, char * format)` | Texture diagnostic callsites push output buffer, size, and format before the hidden caller varargs tail consumed from `stack0x00000010`; the body terminates the output buffer. |
| `0x005d07f4 CRT__FSeek_Locked` | `int __cdecl CRT__FSeek_Locked(void * stream, int offset, int origin)` | Locked fseek wrapper that calls `CRT__FSeek_UnlockedCore` with stream, offset, and origin, then unlocks by stream address. |
| `0x005d0820 CRT__FSeek_UnlockedCore` | `int __cdecl CRT__FSeek_UnlockedCore(void * stream, int offset, int origin)` | Validates stream flags and origin 0/1/2, writes errno `0x16` on invalid input, adjusts origin 1 through `CRT__FTellAdjusted`, calls `CRT__LseekFd`, and returns 0 or -1. |
| `0x005d09e4 CRT__IncrementDotSuffixCounter` | `int __cdecl CRT__IncrementDotSuffixCounter(char * path_buffer)` | `CRT__TmpFile_OpenUniqueBinaryStream` helper that finds the last dot, parses a base `0x20` suffix, increments it below `0x7fff`, and writes it back. |
| `0x005d0a2a CFEPSaveGame__WideCharToLowerCompat` | `uint __cdecl CFEPSaveGame__WideCharToLowerCompat(uint wide_char)` | Preserves `0xffff`, folds ASCII A-Z when locale globals are inactive, otherwise checks type through `CRT__GetCharTypeMaskCompat` before `CRT__LCMapStringW_AnsiCompat`. |
| `0x005d0e88 CRT__WcsNLen` | `int __cdecl CRT__WcsNLen(ushort * wide_string, int max_chars)` | `CRT__LCMapStringW_AnsiCompat` pushes a wide string and maximum count; the body returns measured 16-bit character count or `max_chars`. |
| `0x005d0eb8 CRT__GetCharTypeMaskCompat` | `uint __cdecl CRT__GetCharTypeMaskCompat(uint wide_char, uint mask)` | `CFEPSaveGame__WideCharToLowerCompat` calls it with mask `1`; the body returns 0 for `0xffff`, uses `PTR_DAT_00653894` for byte-range type lookups, or falls back to `CRT__GetStringTypeWideOrAnsiCompat_0056defa`. |

Validation evidence:

- Dry/apply/final dry reported `updated=0 skipped=10 renamed=0 would_rename=0 signature_updated=10 comment_only_updated=0 missing=0 bad=0`, then `updated=10 skipped=0 renamed=0 would_rename=0 signature_updated=10 comment_only_updated=0 missing=0 bad=0`, then final dry `updated=0 skipped=10 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=0 missing=0 bad=0`, with `REPORT: Save succeeded`.
- Post exports verified `10` metadata rows, `10` tag rows, `30` xref rows, `1250` target instruction rows, `10` decompile rows, and `630` xref-site instruction rows.
- Queue refresh passed with `6098` total functions, `4361` commented, `1737` commentless, `1214` exact-undefined signatures, `27` `param_N` signatures, comment-backed proxy `4361/6098 = 71.51%`, and strict clean-signature proxy `4303/6098 = 70.56%`.
- Earliest raw commentless row is `0x0042f220 CSPtrSet__Clear`; next commentless high-signal row is `0x005d0f10 Unwind@005d0f10`.
- Verified backup: `G:\GhidraBackups\BEA_20260522-141639_post_wave740_dinput_crt_tail_verified`, `19` files, `166988679` bytes, `DiffCount=0`.

Scope boundary: this wave proves saved static retail Ghidra metadata only. Imported DirectInput runtime behavior, device enumeration behavior, save enumeration runtime behavior, runtime diagnostic text behavior, runtime file positioning/filesystem behavior, runtime locale behavior, exact CRT version, exact CRT `FILE` layout, exact locale table identity, BEA patching, and rebuild parity remain deferred.

Probe anchors: `Wave740 DInput/CRT tail`, `dinput-crt-tail-wave740`, `0x005d04e0 DirectInput8Create`, `0x005d04ec CFEPSaveGame__WideStrCaseInsensitiveCompare`, `0x005d070f CRT__VsnprintfAndTerminate_005d070f`, `0x005d075f CRT__FormatToBufferAndTerminate`, `0x005d07f4 CRT__FSeek_Locked`, `0x005d0820 CRT__FSeek_UnlockedCore`, `0x005d09e4 CRT__IncrementDotSuffixCounter`, `0x005d0a2a CFEPSaveGame__WideCharToLowerCompat`, `0x005d0e88 CRT__WcsNLen`, `0x005d0eb8 CRT__GetCharTypeMaskCompat`, `0x005d0f10 Unwind@005d0f10`, `0x0042f220 CSPtrSet__Clear`, `G:\GhidraBackups\BEA_20260522-141639_post_wave740_dinput_crt_tail_verified`.
