# Ghidra CDXMemBuffer IO Wave606

Status: ready
Date: 2026-05-19

## Scope

Wave606 saved signature/comment/tag hardening for the next `CDXMemBuffer` buffered file-I/O tranche:

- `0x00547d40 CDXMemBuffer__SetBufferSize`
- `0x00547dc0 CDXMemBuffer__OpenWrite`
- `0x005482c0 CDXMemBuffer__GetFileSize`
- `0x00548820 CDXMemBuffer__ReadLine`
- `0x00548a70 CDXMemBuffer__WriteBytes`
- `0x00548d30 CDXMemBuffer__IsEOF`

The pass corrected the stale `DXMemBuffer__*` owner prefix to `CDXMemBuffer__*` on all six rows while preserving conservative retail-behavior labels. It used retail-binary evidence from xrefs, caller/callee instructions, decompiles, queue telemetry, and Stuart-source class/method context. Exact source-body identity remains unproven where retail behavior differs from the source names.

## What Changed

- `CDXMemBuffer__SetBufferSize` now has a `void __cdecl` signature with caller-popped `requested_size`; the body writes `DAT_00650f6c` as `0x100000` for zero and otherwise rounds the request up to a 1 MiB boundary.
- `CDXMemBuffer__OpenWrite` now has a `bool __thiscall` signature with `filename` and `mem_type`; it allocates the 0x100000 write buffer, opens with `CreateFileA`, and prepares the `.crc` sidecar state.
- `CDXMemBuffer__GetFileSize` now has a `uint __fastcall` signature with `this`; `CText__Init` uses its returned `EAX` value as the allocation size.
- `CDXMemBuffer__ReadLine` now has a `void __thiscall` signature with `output` and `max_chars`; it performs CR/LF-normalized line reads, updates the read cursor/EOF state, and enters the compressed `uncompress` path when needed.
- `CDXMemBuffer__WriteBytes` now has a `void __thiscall` signature with `data` and `size`; it buffers writes, flushes through raw `WriteFile` or the compressed `compress` path, and updates write cursor/count state.
- `CDXMemBuffer__IsEOF` now has a `bool __fastcall` signature with `this`; it returns the EOF flag at `this+0x24`.

## Evidence

- Apply script: `tools/ApplyCDXMemBufferIoWave606.java`
- Focused probe: `tools/ghidra_cdxmembuffer_io_wave606_probe.py`
- Scratch evidence: `subagents/ghidra-static-reaudit/wave606-dxmembuffer-io-00547d40/`
- Dry/apply/final dry:
  - dry: `updated=0 skipped=6 renamed=0 would_rename=6 missing=0 bad=0`
  - apply: `updated=6 skipped=0 renamed=6 would_rename=0 missing=0 bad=0`
  - final dry: `updated=0 skipped=6 renamed=0 would_rename=0 missing=0 bad=0`
- Read-back exports verified `6` metadata rows, `6` tag rows, 70 xref rows, 222 instruction rows, and `6` decompile rows.
- Process note: an initial post-export wrapper command used escaped PowerShell paths and produced `FileNotFoundException` logs; no Ghidra mutation happened in that step. The trusted post-state artifacts are the clean serialized `*-rerun.log` exports.
- Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260519-204906_post_wave606_dxmembuffer_io_verified`
  - `FileCount=19`
  - `TotalBytes=161352583`
  - `DiffCount=0`

## Queue Delta

Post-Wave606 queue telemetry:

- Total functions: `6093`
- Commented functions: `3109`
- Commentless functions: `2984`
- Exact-undefined signatures: `1305`
- `param_N` signatures: `1071`
- Comment-backed proxy: `3109/6093 = 51.03%`
- Strict clean-signature proxy: `3064/6093 = 50.29%`
- Next queue head: `0x00548ec0 CDXEngine__FreeLandscapeCellList_Debug`

Delta from Wave605:

- `+6` commented rows
- `-6` commentless rows
- `-6` exact-undefined signatures
- `0` `param_N` signatures

## Limits

This is static retail evidence only. Exact global ownership for `DAT_00650f6c`, compressed block/CRC semantics, runtime file-I/O behavior, exact `CDXMemBuffer` layout, exact source-body identity, BEA patching, and rebuild parity remain unproven.
