# Ghidra CRT fd/locale/itoa Wave648 Readiness Note

Status: current static read-back evidence, public-safe summary
Date: 2026-05-20

Wave648 saved Ghidra signatures, comments, and tags for seven adjacent CRT runtime helpers:

| Address | Saved function | Evidence |
| --- | --- | --- |
| `0x0056db76` | `CRT__ChangeFileSizeByFd_NoLock` | Saves/restores fd position, grows files with zero-filled writes after forcing binary mode, truncates with `SetEndOfFile`, and maps failures through CRT errno/doserrno state. |
| `0x0056dc9b` | `CRT__WriteWideCharToStream` | Writes one wide character to a CRT stream, preparing write mode and buffering, flushing pending bytes, and returning the low 16 bits or `0xffff` on failure. |
| `0x0056ddc2` | `CRT__GetLocaleInfoCopyOrInt` | Shared locale-info extractor used by date/time and monetary locale loaders; either parses a numeric locale field or allocates/copies multibyte locale text. |
| `0x0056e0bf` | `CRT__IntToAsciiBase` | Signed integer-to-ASCII wrapper over the unsigned formatter, emitting a minus sign for negative base-10 inputs and returning the caller buffer. |
| `0x0056e0ec` | `CRT__UIntToAsciiBase` | Unsigned base-N formatter that emits digits, terminates the buffer, and reverses the digit span in place. |
| `0x0056e148` | `CRT__UIntToAsciiBase_ReturnBuffer` | Convenience wrapper over the unsigned formatter that returns the caller buffer. |
| `0x0056e170` | `CRT__StrNICmpWithLocaleLock` | Corrects stale `CMCBuggy__StrnICmpWithLocaleLock` ownership to a generic CRT case-insensitive bounded string compare helper. |

Serialized headless dry/apply/final-dry evidence:

- Dry: `updated=0 skipped=7 renamed=0 would_rename=3 signature_updated=0 missing=0 bad=0`
- Apply: `updated=7 skipped=0 renamed=3 would_rename=0 signature_updated=7 missing=0 bad=0`
- Final dry: `updated=0 skipped=7 renamed=0 would_rename=0 signature_updated=0 missing=0 bad=0`

Read-back exports verified `7` metadata rows, `7` tag rows, `122` xref rows, `903` instruction rows, and `7` clean decompile rows. The refreshed static queue now reports `6093` total functions, `3492` commented, `2601` commentless, `1217` exact-undefined signatures, and `814` `param_N` signatures. Comment-backed proxy is `3492/6093 = 57.31%`; strict clean-signature proxy is `3442/6093 = 56.49%`.

Verified backup: `G:\GhidraBackups\BEA_20260520-205347_post_wave648_crt_fd_locale_itoa_verified` with `19` files, `162827143` bytes, and `DiffCount=0`.

Next queue head: `0x0056e271 CRT__GetEnvVarValuePointerCaseInsensitive_0056e271`.

Boundary: this is static retail CRT fd/stream/locale/numeric-format/string-compare evidence only. Exact MSVC CRT version, full fd-table/`FILE`/locale table layouts, Windows NLS edge cases, file I/O and stream runtime behavior, numeric formatting edge cases, locale comparison behavior, BEA patching, and rebuild parity remain deferred.
