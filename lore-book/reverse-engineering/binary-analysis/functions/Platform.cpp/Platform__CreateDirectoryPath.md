# Platform__CreateDirectoryPath

> Address: `0x004d2600`
>
> Source: retail binary evidence; source implementation not present in the current Stuart source snapshot

## Status
- **Named in Ghidra:** Yes
- **Signature Set:** Yes (Wave473)
- **Verified vs Source:** No direct source body; static retail-binary evidence only

## Signature
```c
void __stdcall Platform__CreateDirectoryPath(char * path, int strip_filename);
```

## Key Observations
- The retail body copies `path` into a 260-byte stack buffer, using the stack argument loaded from `[ESP + 0x110]` after local allocation and saved registers.
- The second stack argument, loaded from `[ESP + 0x114]`, gates an optional `_strrchr(buffer, '\\')` truncation that NUL-terminates after the final backslash.
- The function walks path components with `_strchr(buffer, '\\')`, temporarily writes `NUL` over each separator, calls `Platform__CreateDirectoryWithErrno`, restores `'\\'`, and advances to the next separator.
- `CLIParams__ParseCommandLine` calls this helper at `0x00424091` after pushing `strip_filename = 1` and the destination path buffer at `0x00662cb0`.
- The function returns with `RET 0x8`, confirming the two stack arguments are callee-cleaned.

## Notes
- Wave473 replaced the stale `undefined Platform__CreateDirectoryPath(void)` signature with an explicit `__stdcall` two-argument signature and bounded comment/tags.
- Runtime filesystem behavior, path length safety, exact CLI caller intent, BEA launch behavior, game patching, and rebuild parity remain deferred.

## Related
- [Platform__CreateDirectoryWithErrno](Platform__CreateDirectoryWithErrno.md)
