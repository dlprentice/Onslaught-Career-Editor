# Ghidra CDXLandscape Head Wave601

Status: ready
Date: 2026-05-19

## Scope

Wave601 saved signature/comment/tag hardening for the CDXLandscape head lifecycle/resource tranche:

- `0x00544770 CDXLandscape__ReleaseOwnedResources`
- `0x005447d0 CDXLandscape__FreeObjectCallback`
- `0x005447e0 CDXLandscape__CreateMipLevels`
- `0x00544a00 CDXLandscape__Constructor`
- `0x00544a40 CDXLandscape__ScalarDeletingDestructor`
- `0x00544a60 CDXLandscape__Destructor`
- `0x00544af0 CDXLandscape__Init`
- `0x00544eb0 CDXLandscape__ReleaseBuffers`
- `0x00544f10 CDXLandscape__Shutdown`

No function renames were made. The pass used retail-binary evidence from xrefs, vtable slots, call-site instructions, decompiles, and debug path strings for `DXLandscape.cpp` / `DXLandscape.h`.

## What Changed

- `CDXLandscape__ReleaseOwnedResources` now records the resource-record cleanup pattern: release slot `+0`, destroy a vector of `0xc`-byte entries through `CDXLandscape__FreeObjectCallback`, free the 4-byte vector header, and free/clear the scratch buffer at `+0x04`.
- `CDXLandscape__FreeObjectCallback` now names the record parameter and documents the `object_record+0` free path.
- `CDXLandscape__CreateMipLevels` now has a `void __thiscall` signature with `mip_level_count`; `RET 0x4` confirms one stack argument after ECX.
- `CDXLandscape__Constructor`, scalar deleting destructor, destructor, init, release-buffers, and shutdown now have comments and signatures tied to constructor/destructor call sites, vtable `0x005e50d0`, vtable slot 4 at `0x005e50e0`, and `CEngine__Init` / `CEngine__Shutdown` callers.
- `CDXLandscape__Init` is documented conservatively as receiving `engine+0x49c` as `init_context`; the exact field semantics remain unresolved.

## Evidence

- Apply script: `tools/ApplyCDXLandscapeHeadWave601.java`
- Focused probe: `tools/ghidra_cdxlandscape_head_wave601_probe.py`
- Scratch evidence: `subagents/ghidra-static-reaudit/wave601-cdxlandscape-head-00544770/`
- Dry/apply/final dry:
  - dry: `updated=0 skipped=9 renamed=0 would_rename=0 missing=0 bad=0`
  - apply: `updated=9 skipped=0 renamed=0 would_rename=0 missing=0 bad=0`
  - final dry: `updated=0 skipped=9 renamed=0 would_rename=0 missing=0 bad=0`
- Read-back exports verified `9` metadata rows, `9` tag rows, `25` xref rows, `2061` instruction rows, and `9` decompile rows.
- Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260519-181626_post_wave601_cdxlandscape_head_verified`
  - `fileCount=19`
  - `totalBytes=161221511`
  - `DiffCount=0`
  - `manifestHash=85163222f6735243e7c38d289b7f40795f8c9ab1952f39c6c21dfc3fd8312657`

## Queue Delta

Post-Wave601 queue telemetry:

- Total functions: `6093`
- Commented functions: `3088`
- Commentless functions: `3005`
- Exact-undefined signatures: `1324`
- `param_N` signatures: `1073`
- Comment-backed proxy: `3088/6093 = 50.68%`
- Strict clean-signature proxy: `3043/6093 = 49.94%`
- Next queue head: `0x00544fc0 CDXLandscape__BuildVertexBuffer`

Delta from Wave600:

- `+9` commented rows
- `-9` commentless rows
- `-7` exact-undefined signatures
- `-2` `param_N` signatures

## Limits

This is static retail evidence only. Runtime terrain rendering, resource ownership under lost-device/reset conditions, exact CDXLandscape/CLandscape/CLandscapeTexture/CVBuffer/CIBuffer/CDXSurf layouts, exact source-body identity, BEA patching, and rebuild parity remain unproven.
