# Ghidra Import Thunks Wave619 Readiness Note

Status: complete
Date: 2026-05-20

## Scope

Wave619 hardened the contiguous external import-thunk island from `0x0055d5e0` through `0x0055d69a` in the saved Ghidra project:

- DirectSound: `DirectSoundCreate8`, `DirectSoundEnumerateA`
- VFW capture: `AVIStreamWrite`
- zlib: `uncompress`, `compress`
- libogg: `ogg_sync_*`, `ogg_stream_*`, `ogg_page_*`
- libvorbis: `vorbis_*` decode helpers
- Version APIs: `VerQueryValueA`, `GetFileVersionInfoA`, `GetFileVersionInfoSizeA`

The pass saved comments and tags for all 32 thunks. It saved conservative API-shaped signatures for the first 29 rows and retained the existing WinAPI signatures for the three Version APIs. It made no function renames, no function-boundary changes, and no executable byte changes.

## Evidence

- Dry/apply/final-dry logs reported `updated=0 skipped=32 renamed=0 would_rename=0 missing=0 bad=0`, then `updated=32 skipped=0 renamed=0 would_rename=0 missing=0 bad=0`, then `updated=0 skipped=32 renamed=0 would_rename=0 missing=0 bad=0`, with `REPORT: Save succeeded`.
- Post-state exports verified `32` metadata rows, `32` tag rows, `61` xref rows, `96` instruction rows, and `32` decompile rows.
- Every target instruction is a six-byte import thunk (`JMP dword ptr [IAT]`). The island tail is `0x0055d69a GetFileVersionInfoSizeA`; the next instruction at `0x0055d6a0` begins `CRT__SehPopExceptionFrameAndJump`.
- Prototype evidence came from local Windows SDK headers for DirectSound/VFW/Version APIs, repo/reference zlib headers, and local Ogg/Vorbis headers; opaque pointer types were kept where exact third-party struct layouts are outside the current Ghidra typing scope.
- Backup verified: `[maintainer-local-ghidra-backup-root]\BEA_20260520-032435_post_wave619_import_thunks_verified` with `19` files, `161745799` bytes, and `DiffCount=0`.

## Queue Telemetry

Post-Wave619 queue telemetry:

- Total functions: `6093`
- Commented functions: `3217`
- Commentless functions: `2876`
- Exact `undefined` signatures: `1218`
- `param_N` signatures: `1056`
- Comment-backed proxy: `3217/6093 = 52.80%`
- Strict clean-signature proxy: `3169/6093 = 52.01%`

Delta from Wave618: `+32` commented, `-32` commentless, `-29` exact-undefined signatures, `0` `param_N`, and `+29` strict clean-signature rows.

The next queue head is `0x0055d6a0 CRT__SehPopExceptionFrameAndJump`.

## Boundaries

This is static saved-Ghidra import-thunk/API evidence only. Runtime audio, video capture, compression, Ogg/Vorbis decode, version-resource behavior, concrete third-party library versions, exact DirectSound/VFW/zlib/Ogg/Vorbis structure layouts, BEA patching, and rebuild parity remain deferred.
