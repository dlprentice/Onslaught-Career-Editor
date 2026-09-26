# __mkdir

> Address: `0x0055f347`
>
> Source: retail binary evidence; thin Windows API wrapper

## Identity (RE record audit, 2026-09-26)

Proven: `__mkdir`. Linked library code: __mkdir, from the static library Visual C++ 6.0 SP6 LIBCMT.LIB (SHA-256 a541c95e5ffdd6d5573d1976f5e5d0038f2c4fb0bcb02975c68948bf1d6e452a), member build\intel\mt_obj\mkdir.obj. The pristine bytes equal the library's object code apart from its relocation fields, and every relocation resolves consistently with the rest of the match (`tools/re_lib_match.py`; decision `relocations`). The Ghidra cohort `library-crt-20260926` applied the name ([Ghidra README](../../../../reverse-engineering/ghidra/README.md#re-audit-c-runtime-library-names--september-26)). Everything below predates the identification: its byte facts stand, and the labels it quotes are the labels saved before that cohort.

## Status
- **Named in Ghidra:** Yes
- **Signature Set:** Yes (Wave473)
- **Verified vs Source:** No direct source body; static retail-binary evidence only

## Signature
```c
int __cdecl Platform__CreateDirectoryWithErrno(char * path);
```

## Key Observations
- The wrapper calls `CreateDirectoryA(path, NULL)`.
- On failure, it calls `GetLastError`, forwards the Win32 error to `CRT__SetErrnoAndDosErrnoFromWinError_00567a35`, and returns `-1`.
- On success, it returns `0`.
- Caller evidence shows `Platform__CreateDirectoryPath` calls it for each path prefix, while `EnumerateSaveFiles_Main` calls it for the save-games directory string at `0x0063df94`.
- Callers clean the single stack argument, and the wrapper returns with plain `RET`, matching the saved `__cdecl` signature.

## Notes
- Wave473 replaced the stale `int __cdecl Platform__CreateDirectoryWithErrno(int param_1)` signature with a `char * path` parameter and bounded comment/tags.
- Exact CRT provenance, runtime filesystem behavior, errno consumers, BEA launch behavior, game patching, and rebuild parity remain deferred.

## Related
- [Platform__CreateDirectoryPath](Platform__CreateDirectoryPath.md)
