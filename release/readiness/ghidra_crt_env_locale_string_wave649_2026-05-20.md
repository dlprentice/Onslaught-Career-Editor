# Ghidra CRT env/locale/string Wave649 Readiness Note

Status: current static read-back evidence, public-safe summary
Date: 2026-05-20

Wave649 saved Ghidra signatures, comments, and tags for eleven adjacent CRT runtime helpers:

| Address | Saved function | Evidence |
| --- | --- | --- |
| `0x0056e271` | `CRT__GetEnvVarValuePointerCaseInsensitive` | Removes the suffix-style name; scans the CRT environment table for a case-insensitive `NAME=` match and returns the value pointer. |
| `0x0056e2ee` | `CRT__SetFdTextBinaryModeFlag_NoLock` | Toggles the observed fd-table text/binary mode bit for valid mode constants and returns the previous mode. |
| `0x0056e34f` | `CRT__GetLocaleInfoAsWide` | Uses `GetLocaleInfoW` when available, otherwise queries ANSI locale info and converts it to wide output. |
| `0x0056e462` | `CRT__GetLocaleInfoAsMultiByte` | Uses `GetLocaleInfoA` when available, otherwise queries wide locale info and converts it to multibyte output. |
| `0x0056e5bf` | `CRT__ProcessWideEnvTableToMultibyte` | Corrects stale `Argv` wording; walks the wide environment table, converts entries to multibyte text, and feeds them through the putenv updater. |
| `0x0056e62d` | `CRT__CompareLocaleStringsWithMBCSFallback` | CompareString helper reached from `__mbsnbicoll`, with ANSI and wide-conversion comparison paths plus observed lead-byte edge handling. |
| `0x0056e8aa` | `CRT__StrNLen` | Bounded strlen helper returning the terminator distance or `maxChars`. |
| `0x0056e8d5` | `CRT__PutEnvStringAndUpdateProcessEnv` | Putenv-style CRT environment-table updater that can mirror changes through `SetEnvironmentVariableA`. |
| `0x0056ea5c` | `CRT__FindEnvVarIndexOrInsertionPoint` | Case-insensitive environment name table scan returning a matching index or negative insertion index. |
| `0x0056eab4` | `CRT__CloneEnvironmentTable` | Allocates a new environment pointer table and duplicates each `NAME=value` row. |
| `0x0056eb1b` | `CRT__StrDup` | `strdup`-style helper using `strlen`, allocation, and aligned string copy. |

Serialized headless dry/apply/final-dry evidence:

- Dry: `updated=0 skipped=11 renamed=0 would_rename=2 signature_updated=0 missing=0 bad=0`
- Apply: `updated=11 skipped=0 renamed=2 would_rename=0 signature_updated=11 missing=0 bad=0`
- Final dry: `updated=0 skipped=11 renamed=0 would_rename=0 signature_updated=0 missing=0 bad=0`

Read-back exports verified `11` metadata rows, `11` tag rows, `19` xref rows, `3091` instruction rows, and `11` clean decompile rows. The refreshed static queue now reports `6093` total functions, `3503` commented, `2590` commentless, `1217` exact-undefined signatures, and `805` `param_N` signatures. Comment-backed proxy is `3503/6093 = 57.49%`; strict clean-signature proxy is `3453/6093 = 56.67%`.

Verified backup: `G:\GhidraBackups\BEA_20260520-222000_post_wave649_crt_env_locale_string_verified` with `19` files, `162925447` bytes, and `DiffCount=0`.

Next queue head: `0x0056eb50 CDXMeshVB__SetTriangleStripDebugFlag`.

Boundary: this is static retail CRT environment, locale-info, string-compare, string-length, and string-allocation evidence only. Exact MSVC CRT version, full environment table/fd-table/`FILE`/locale/codepage layouts, Windows NLS edge cases, runtime environment mutation behavior, locale comparison behavior, BEA patching, and rebuild parity remain deferred.
