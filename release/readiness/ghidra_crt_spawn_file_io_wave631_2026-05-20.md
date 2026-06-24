# Ghidra CRT Spawn/File I/O Head Wave631

Status: read-back verified
Date: 2026-05-20

Wave631 corrected and hardened thirteen adjacent CRT spawn, stdio, fd-table, stream-flush, and SEH helper rows in the saved Ghidra project:

- `0x0055e412 CRT__SpawnPathVarargsNoEnv_Thunk`
- `0x0055e45f CRT__OpenFileByModeString_AutoUnlock`
- `0x005638a8 CRT__FlushStreamIfWritePending`
- `0x00564a0b CRT__SpawnSearchPathWithFallbackExtensions`
- `0x00564b54 CRT__SpawnResolvedPathWithBuiltCommandEnv`
- `0x00564ba5 CRT__UnhandledExceptionFilterDispatch`
- `0x00564c09 CRT__OpenFileByModeString`
- `0x00564d79 CRT__AcquireFileStreamSlot`
- `0x00564e41 CRT__CloseFd`
- `0x00564e9e CRT__CloseFd_NoLock`
- `0x00564f4c CRT__FlushAndCommitFileStream`
- `0x00564f7a CRT__FlushWriteStreamSegment`
- `0x00564fdf CRT__FlushAllFileStreamsByMode`

The pass corrected stale `CDXTexture` owner labels on the spawn/path and stream-flush helpers, corrected the overbroad `CRT__FlushOrCloseAllFileHandles` label, saved signatures/comments/tags for all thirteen rows, and made no function-boundary or executable-byte changes.

## Evidence

- Dry run: `updated=0 skipped=0 renamed=0 would_rename=5 signature_updated=0 missing=0 bad=0`
- Apply: `updated=13 skipped=0 renamed=5 would_rename=0 signature_updated=12 missing=0 bad=0`
- Final dry: `updated=0 skipped=13 renamed=0 would_rename=0 signature_updated=0 missing=0 bad=0`
- Post exports: `13` metadata rows, `13` tag rows, `24` xref rows, `1313` instruction rows, `13` decompile rows
- Queue refresh: `6093` total, `3339` commented, `2754` commentless, `1217` exact-undefined signatures, `953` `param_N` signatures
- Strict clean-signature proxy: `3287/6093 = 53.95%`
- Verified backup: `G:\GhidraBackups\BEA_20260520-092034_post_wave631_crt_spawn_file_io_verified` (`19` files, `162302855` bytes, `DiffCount=0`)

The next high-signal queue head is `0x00565083 ControlsUI__FormatWideStringCore`.

## Limits

This is static saved-Ghidra evidence only. Exact CRT identity/version, exact FILE/fd-table/environment/command-line layout, PATH-search equivalence, runtime CreateProcess/file I/O/flush/close/exception behavior, BEA patching, and rebuild parity remain unproven.
