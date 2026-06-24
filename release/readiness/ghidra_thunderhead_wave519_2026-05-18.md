# Ghidra ThunderHead Wave519 Readiness

Status: static read-back complete
Date: 2026-05-18

## Scope

Wave519 saved signature/comment/tag hardening for 5 ThunderHead/ThunderheadGuide targets:

- `0x004f4730` `CThunderHead__CreateLegMotion`
- `0x004f4830` `CThunderHead__CreateWarspite`
- `0x004f48a0` `CThunderHead__CreateGuide`
- `0x004f4e00` `CThunderheadGuide__Init`
- `0x004f4e40` `CThunderheadGuide__VFunc_03_004f4e40`

The pass corrected two stale `undefined` signatures and one stale `param_N` signature, renamed `CThunderheadGuide_Init` to `CThunderheadGuide__Init`, and recovered the missing CThunderheadGuide vtable slot-3 function boundary at `0x004f4e40`. Focused boundary read-back shows that function returns at `0x004f51b4` before the following non-function data-initializer block at `0x004f51c0`.

## Evidence

- Pre-state exports: `subagents/ghidra-static-reaudit/wave519-thunderhead-004f4730/pre_*`.
- Mutation script: `tools/ApplyThunderHeadWave519.java`.
- Dry run: `updated=0 skipped=5 renamed=0 would_rename=1 created=0 would_create=1 missing=0 bad=0`.
- Apply run: `updated=5 skipped=0 renamed=1 would_rename=0 created=1 would_create=0 missing=0 bad=0`.
- Verify dry run: `updated=0 skipped=5 renamed=0 would_rename=0 created=0 would_create=0 missing=0 bad=0`.
- Post read-back: `5` metadata rows, `5` tag rows, `5` xref rows, `1425` instruction rows, `345` focused boundary rows, `5` decompile exports, and `256` vtable-slot rows.
- Focused probe: `tools/ghidra_thunderhead_wave519_probe.py --check`.
- Queue refresh after Wave519: `6079` functions, `2457` commented, `3622` commentless, `1598` exact-undefined signatures, and `1394` `param_N` signatures.
- Current whole-project telemetry proxy: comment-backed `2457/6079 = 40.42%`; strict comment-plus-clean-signature proxy `2400/6079 = 39.48%`.
- Backup verified at `G:\GhidraBackups\BEA_20260517-222357_post_wave519_thunderhead_verified` with `19` files, `158567303` bytes, `MissingCount=0`, `ExtraCount=0`, and `HashDiffCount=0`.

## Claim Boundary

This is static Ghidra metadata and boundary evidence only. It improves readability around ThunderHead factory setup and CThunderheadGuide slot-3 dispatch. It does not prove runtime targeting behavior, runtime combat AI behavior, concrete ThunderHead/ThunderheadGuide layouts, exact virtual method name for `0x004f4e40`, source-body identity, BEA patching, or rebuild parity.
