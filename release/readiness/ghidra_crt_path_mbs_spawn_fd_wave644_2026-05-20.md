# Ghidra CRT Path/MBCS/Spawn/Fd Wave644 Readiness Note

Date: 2026-05-20
Status: ready for public-safe release accounting

## Scope

Wave644 saved signatures, comments, and tags for twelve adjacent CRT path, multibyte-string, spawn, and file-descriptor rows:

| Address | Saved state |
| --- | --- |
| `0x0056a7e7` | `int __cdecl CRT__ValidatePathAttributesForOpen(char * path, uint openFlags)` |
| `0x0056a82d` | `char * __cdecl CRT__MbsChr(char * text, uint charValue)` |
| `0x0056a8c4` | `char * __cdecl CRT__MbsRChr(char * text, uint charValue)` |
| `0x0056a936` | `int __cdecl CRT__SpawnVe(int spawnMode, char * resolvedPath, char * commandLineBlock, char * environmentBlock)` |
| `0x0056ab1f` | `int __cdecl CRT__BuildSpawnCommandAndEnv(char * * argvVector, char * * envVector, char * * commandLineOut, char * * environmentBlockOut)` |
| `0x0056ad25` | `uint __cdecl CRT__OpenFd(char * path, uint openFlags, uint shareMode, uint permissionFlags)` |
| `0x0056b117` | `int __cdecl CRT__SetOsHandle(uint fdIndex, int osHandle)` |
| `0x0056b193` | `int __cdecl CRT__FreeOsHandle(uint fdIndex)` |
| `0x0056b212` | `int __cdecl CRT__GetOsFileHandleByIndex(uint fdIndex)` |
| `0x0056b254` | `void __cdecl CRT__LockFileHandleByIndex(uint fdIndex)` |
| `0x0056b2b3` | `void __cdecl CRT__UnlockFileHandleByIndex(uint fdIndex)` |
| `0x0056b2d5` | `int __cdecl CRT__CommitFileHandle(uint fdIndex)` |

The pass corrected `CRT__SpawnVe_0056a936` to `CRT__SpawnVe` and `CRT__BuildSpawnCommandAndEnv_0056ab1f` to `CRT__BuildSpawnCommandAndEnv`. No function-boundary changes or executable-byte changes were made.

## Evidence

- Script: `tools/ApplyCrtPathMbsSpawnFdWave644.java`
- Probe: `tools/ghidra_crt_path_mbs_spawn_fd_wave644_probe.py`
- Scratch/read-back artifacts: `subagents/ghidra-static-reaudit/wave644-crt-path-mbs-spawn-fd/`
- Dry/apply/final dry summaries:
  - `updated=0 skipped=12 renamed=0 would_rename=2 signature_updated=0 missing=0 bad=0`
  - `updated=12 skipped=0 renamed=2 would_rename=0 signature_updated=12 missing=0 bad=0`
  - `updated=0 skipped=12 renamed=0 would_rename=0 signature_updated=0 missing=0 bad=0`
- Post exports: `12` metadata rows, `12` tag rows, `35` xref rows, `3372` instruction rows, and `12` decompile rows.
- Queue after Wave644: `6093` total functions, `3449` commented, `2644` commentless, `1217` exact-undefined signatures, and `856` `param_N` signatures.
- Comment-backed proxy: `3449/6093 = 56.61%`.
- Strict clean-signature proxy: `3398/6093 = 55.77%`.
- Next high-signal queue head: `0x0056b368 CRT__WriteWideCharToStreamWithConversion`.
- Verified backup: `G:\GhidraBackups\BEA_20260520-145509_post_wave644_crt_path_mbs_spawn_fd_verified`, `19` files, `162696071` bytes, `DiffCount=0`.

## Boundaries

This is static CRT path/open, MBCS string-search, spawn/environment, fd-table, fd-lock, and fd-commit evidence only. Exact MSVC CRT version, full open/spawn/share flag mapping, command-line quoting equivalence, environment-block layout/lifetime, full `FILE`/fd-table layouts, Windows filesystem/process/file-I/O edge cases, runtime `CreateProcessA`/`CreateFileA`/`FlushFileBuffers` behavior, BEA patching, and rebuild parity remain unproven.
