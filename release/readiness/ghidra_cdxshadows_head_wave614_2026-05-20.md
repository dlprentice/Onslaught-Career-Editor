# Ghidra CDXShadows Head Wave614

Status: ready
Date: 2026-05-20

## Scope

Wave614 saved signature/comment/tag hardening for the CDXShadows head lifecycle and blob-shadow resource setup:

- `0x00552060 CDXShadows__Destructor`
- `0x005520f0 CDXShadows__Init`
- `0x00552330 CDXShadows__InitBlobShadows`

The pass made no renames and did not create or repair function boundaries. The evidence is static retail Ghidra decompile, instruction, xref, callsite, and post-save tag read-back. Runtime shadow behavior, runtime blob-shadow rendering, concrete D3D output, BEA patching, and rebuild parity remain unproven.

## What Changed

- `CDXShadows__Destructor` now records the ECX receiver ABI, `CEngine__Shutdown` callsite at `0x004498a4`, the count field at `+0x5bc`, texture pointer release loop at `+0x640`, blob texture/resource fields `+0x5b4/+0x5b8`, vtable slot `+0x0c`, and `CShaderBase` list unlink.
- `CDXShadows__Init` now records the ECX receiver ABI, `CEngine__Init` callsite at `0x00449d05`, shadow-map count selection `0x10/0x20` from `DAT_00662f10`, per-shadow `CUMTexture` allocation/configuration from `DXShadows.cpp` line `0x69`, and the `cg_ShowShadowMap`, `cg_ShowShadowExtents`, `cg_Shadows`, `cg_BlobShadows`, and `cg_BlobShadowFadeDist` console-variable registrations.
- `CDXShadows__InitBlobShadows` now records the ECX receiver ABI, `CEngine__InitResources` callsite at `0x00449d62`, `shadowblob.tga` lookup through `CTexture__FindTexture`, storage at `+0x5b4`, `0x68`-byte `CVBufTexture` allocation from `DXShadows.cpp` line `0x97`, storage at `+0x5b8`, and VB/IB format setup calls.

## Evidence

- Apply script: `tools/ApplyCDXShadowsHeadWave614.java`
- Focused probe: `tools/ghidra_cdxshadows_head_wave614_probe.py`
- Scratch evidence: `subagents/ghidra-static-reaudit/wave614-cdxshadows-head-00552060-00552330/`
- Initial clean dry: `updated=0 skipped=3 renamed=0 would_rename=0 missing=0 bad=0`
- Apply: `updated=3 skipped=0 renamed=0 would_rename=0 missing=0 bad=0`
- Final dry: `updated=0 skipped=3 renamed=0 would_rename=0 missing=0 bad=0`
- Read-back exports verified `3` metadata rows, `3` tag rows, `3` xref rows, `783` instruction rows, `3` decompile rows, and `141` callsite instruction rows.
- Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260520-004026_post_wave614_cdxshadows_head_verified`
  - `sourceFileCount=19`
  - `destFileCount=19`
  - `sourceBytes=161614727`
  - `destBytes=161614727`
  - `DiffCount=0`

## Queue Delta

Post-Wave614 queue telemetry:

- Total functions: `6093`
- Commented functions: `3159`
- Commentless functions: `2934`
- Exact-undefined signatures: `1272`
- `param_N` signatures: `1056`
- Comment-backed proxy: `3159/6093 = 51.85%`
- Strict clean-signature proxy: `3114/6093 = 51.11%`
- Next queue head: `0x0055515e CDXSnow__Init`

Delta from Wave613:

- `+3` commented rows
- `-3` commentless rows
- `-3` exact-undefined signatures
- `0` `param_N` signatures
- `+3` strict clean rows

## Limits

This is static retail evidence only. Exact `CDXShadows`, `CUMTexture`, `CVBufTexture`, texture-resource, render-list, and console-variable layouts remain partial. The vtable slot names at `+0x08` and `+0x0c` remain deferred. Runtime shadow behavior, runtime blob-shadow rendering, concrete D3D output, source-body identity, BEA patching, and rebuild parity remain unproven.
