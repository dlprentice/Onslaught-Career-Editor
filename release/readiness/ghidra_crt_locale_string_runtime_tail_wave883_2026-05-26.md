# Ghidra CRT Locale/String Runtime Tail Wave883 Readiness Note

Status: complete static read-back evidence
Date: 2026-05-26
Scope: `crt-locale-string-runtime-tail-wave883`

Wave883 CRT locale/string/runtime tail saved comments/tags for twenty-three high-importance CRT locale/NLS/string/ctype/timezone/errno/file-table connector rows from `0x00563ad3 CRT__FpuTransDispatch2_ClearStatusAndHandle` through `0x0056defa CRT__GetStringTypeWideOrAnsiCompat_0056defa` after serialized headless dry/apply/read-back/final dry with the `crt-locale-string-runtime-tail-wave883` and `wave883-readback-verified` tags. Existing clean signatures were verified and preserved. It made no rename, made no function-boundary change, made no executable-byte change, did not launch BEA, and did not touch the installed game.

Representative anchors:

| Address | Evidence |
| --- | --- |
| `0x00563ad3 CRT__FpuTransDispatch2_ClearStatusAndHandle` | Reached from `__ctrandisp2` and `__ctrandisp1`; clears the frame status bit, tests exponent/status cases including `0x7ff0`, builds the exception payload, and calls `CRT__HandleFloatingPointException`. |
| `0x00565ee0 CRT__LCMapStringA_Compat` | `LCMapStringA` / `LCMapStringW` compatibility adapter using `MultiByteToWideChar`, `LCMapStringW`, `WideCharToMultiByte`, flags `0x220` / `0x400`, and xrefs from locale lower/upper and `CDXTexture__AsciiToLowerInPlace`. |
| `0x00567aa8 CRT__GetErrnoThreadPtr_00567aa8` | Returns `CRT__GetOrInitThreadLocalRecord() + 0x8`, the errno pointer slot; xrefs include CRT file, spawn/open, strtol, and FPU status paths. |
| `0x00568390 stricmp` | Case-insensitive compare with `217 xrefs`, ASCII folding path, and locale path through `CRT__ToLowerWithLocale`. |
| `0x0056a1cd CRT__ParseFloatTextToLongDouble` | Float text parser reached by float32/float64/status wrappers; uses decimal separator `DAT_00653aa0`, dispatch table `0x56a66e`, ctype checks, and mantissa scaling helpers. |
| `0x0056aff4 CRT__AllocOsHandleSlot` | CRT OS-handle slot allocator: lock index `0x12`, `0x20`-handle table blocks, per-slot critical sections, `0x480-byte` allocation blocks, and `CRT__LockFileHandleByIndex`. |
| `0x0056be17 CRT__InitCTypeTablesFromCodePage` | Ctype table initializer using `GetCPInfo`, `CRT__GetStringTypeACompat`, and `CRT__GetStringTypeWideOrAnsiCompat_0056defa`, with lead-byte marking via `0x8000`. |
| `0x0056cbe2 CRT__Tzset` | Timezone setup routine; handles `TZ`, `GetTimeZoneInformation`, `WideCharToMultiByte`, parsed offsets, timezone bias globals, and standard/daylight name buffers. |
| `0x0056defa CRT__GetStringTypeWideOrAnsiCompat_0056defa` | `GetStringTypeW` / `GetStringTypeA` bridge using `DAT_009d0c2c`, `WideCharToMultiByte`, flags `0x220`, and `CRT__MemMoveOverlapSafe`. |

Read-back evidence:

- `ApplyCrtLocaleStringRuntimeTailWave883.java dry`: `updated=0 skipped=23 renamed=0 would_rename=0 missing=0 bad=0`
- `ApplyCrtLocaleStringRuntimeTailWave883.java apply`: `updated=23 skipped=0 renamed=0 would_rename=0 missing=0 bad=0`, with `REPORT: Save succeeded`
- `ApplyCrtLocaleStringRuntimeTailWave883.java final dry`: `updated=0 skipped=23 renamed=0 would_rename=0 missing=0 bad=0`
- Post exports: `23` metadata rows, `23` tag rows, `319` xref rows, `1973` instruction rows, and `23` decompile rows.
- Queue after Wave883: `6113` total functions, `5966` commented, `147` commentless, `0` exact-undefined signatures, `0` `param_N`, comment-backed and strict clean-signature proxy `5966/6113 = 97.60%`.
- Next raw commentless row: `0x00569cb8 ControlsUI__AbortInvalidParameter`; commentless high-signal, signature, and name-confidence queues remain empty.
- Verified backup: `G:\GhidraBackups\BEA_20260526-005047_post_wave883_crt_locale_string_runtime_tail_verified`, `19` files, `172788615` bytes, `DiffCount=0`.

What this proves:

- The 23 target function rows exist in the saved Ghidra project.
- The saved comments and tags include `crt-locale-string-runtime-tail-wave883` and `wave883-readback-verified`.
- The existing clean signatures were preserved and verified by post decompile metadata.
- The observed CRT locale/NLS/string/ctype/timezone/errno/file-table bodies are static retail Ghidra evidence tied to body, xref, instruction, and decompile exports.

What remains unproven:

- Exact MSVC CRT helper/version identity.
- Exact CRT NLS, locale, ctype, multibyte, timezone, TLS, file-descriptor, and OS-handle table layouts.
- Runtime locale, timezone, NLS, string parsing, errno, file-table, or floating-point exception behavior.
- BEA patching behavior.
- Rebuild parity.
