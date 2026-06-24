# Platform__CreateDirectoryWithErrno

> Address: `0x0055f347`
>
> Source: retail binary evidence; thin Windows API wrapper

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
