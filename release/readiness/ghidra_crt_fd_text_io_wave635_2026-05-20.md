# Ghidra CRT Fd/Text I/O Wave635

Status: read-back verified
Date: 2026-05-20

Wave635 hardened seven adjacent CRT fd/text I/O and memory/error helper rows in the saved Ghidra project:

- `0x00567505 CRT__WriteFdTextMode_Locked`
- `0x0056756a CRT__WriteFdTextMode_NoLock`
- `0x00567700 CRT__MemMove`
- `0x00567a35 CRT__SetErrnoAndDosErrnoFromWinError`
- `0x00567aba CRT__ReadByteWithBufferRefill`
- `0x00567b96 CRT__ReadFdTextMode_Locked`
- `0x00567bfb CRT__ReadFdTextMode_NoLock`

The pass corrected `CRT__WriteFdTextMode_Locking_00567505` to `CRT__WriteFdTextMode_Locked`, corrected `CRT__MemMove_00567700` to `CRT__MemMove`, corrected `CRT__SetErrnoAndDosErrnoFromWinError_00567a35` to `CRT__SetErrnoAndDosErrnoFromWinError`, saved signatures/comments/tags for all seven rows, and made no function-boundary or executable-byte changes.

## Evidence

- Dry run: `updated=0 skipped=7 renamed=0 would_rename=3 signature_updated=0 varargs=0 missing=0 bad=0`
- Apply: `updated=7 skipped=0 renamed=3 would_rename=0 signature_updated=7 varargs=0 missing=0 bad=0`
- Final dry: `updated=0 skipped=7 renamed=0 would_rename=0 signature_updated=0 varargs=0 missing=0 bad=0`
- Post exports: `7` metadata rows, `7` tag rows, `35` xref rows, `1267` instruction rows, `7` decompile rows
- Queue refresh: `6093` total, `3377` commented, `2716` commentless, `1217` exact-undefined signatures, `919` `param_N` signatures
- Strict clean-signature proxy: `3323/6093 = 54.54%`
- Verified backup: `G:\GhidraBackups\BEA_20260520-111006_post_wave635_crt_fd_text_io_verified` (`19` files, `162401159` bytes, `DiffCount=0`)

The next high-signal queue head is `0x00567de0 CRT__StrCpyAligned`.

## Limits

This is static saved-Ghidra evidence only. Exact MSVC CRT version, exact FILE/fd-table/stream layout, text-mode flag names, lookahead slot semantics, runtime ReadFile/WriteFile behavior, BEA patching, and rebuild parity remain unproven.
