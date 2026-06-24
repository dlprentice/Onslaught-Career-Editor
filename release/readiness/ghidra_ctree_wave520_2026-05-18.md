# Ghidra CTree Wave520 Readiness

Status: static read-back complete
Date: 2026-05-18

## Scope

Wave520 saved signature/comment/tag hardening for 8 CTree targets:

- `0x004f5f60` `CTree__InitFallingTreeData`
- `0x004f63c0` `CTree__dtor_base`
- `0x004f6430` `CTree__ComputeLodBucket`
- `0x004f68e0` `CTree__VFunc_28_CreateFallingTreeAfterDelay`
- `0x004f69b0` `CTree__CreateFallingTree`
- `0x004f6aa0` `CTree__VFunc_27_CreateFallingTreeFromThing`
- `0x004f6b80` `CTree__UpdateFallingTree`
- `0x004f7050` `CTree__HandleEvent`

The pass corrected the CTree destructor-body label, recovered three missing CTree vtable-backed function boundaries, hardened five existing CTree signatures/comments, corrected three exact-undefined signatures, and reduced two `param_N` signatures.

## Evidence

- Pre-state exports: `subagents/ghidra-static-reaudit/wave520-tree-004f5f60/pre_*`.
- Mutation script: `tools/ApplyCTreeWave520.java`.
- Dry run: `updated=0 skipped=8 renamed=0 would_rename=1 created=0 would_create=3 missing=0 bad=0`.
- Apply run: `updated=8 skipped=0 renamed=1 would_rename=0 created=3 would_create=0 missing=0 bad=0`.
- Verify dry run: `updated=0 skipped=8 renamed=0 would_rename=0 created=0 would_create=0 missing=0 bad=0`.
- Post read-back: `8` metadata rows, `8` tag rows, `12` xref rows, `1544` instruction rows, `1155` focused boundary rows, `8` decompile exports, and `144` vtable-slot rows.
- Focused probe: `tools/ghidra_ctree_wave520_probe.py --check`.
- Queue refresh after Wave520: `6082` functions, `2465` commented, `3617` commentless, `1595` exact-undefined signatures, and `1392` `param_N` signatures.
- Current whole-project telemetry proxy: comment-backed `2465/6082 = 40.53%`; strict comment-plus-clean-signature proxy `2403/6082 = 39.51%`.
- Backup verified at `G:\GhidraBackups\BEA_20260517-225110_post_wave520_ctree_verified` with `19` files, `158632839` bytes, `MissingCount=0`, `ExtraCount=0`, and `HashDiffCount=0`.

## Claim Boundary

This is static Ghidra metadata, xref, instruction, decompile, and vtable evidence only. It improves readability around CTree falling-tree allocation, vtable event/collision/timer entry points, LOD helper behavior, and falling-tree update scheduling. It does not prove runtime falling-tree physics, runtime particle behavior, exact CTree/FallingTreeData layouts, exact virtual method names for recovered slots, source-body identity, BEA patching, or rebuild parity.
