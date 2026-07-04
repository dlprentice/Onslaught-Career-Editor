# Ghidra CFastVB Tail Wave563 Readiness - 2026-05-18

## Scope

Wave563 hardened the CFastVB tail, five adjacent targets from `0x0051a270` through `0x0051a510`:

- `CFastVB__Create`
- `CFastVB__Destroy`
- `CFastVB__LockAligned`
- `CFastVB__Lock`
- `CFastVB__Render`

## Evidence

`ApplyCFastVBTailWave563.java` dry/apply/final dry ran serialized through headless Ghidra. Dry reported `updated=0 skipped=5 missing=0 bad=0`; apply reported `updated=5 skipped=0 missing=0 bad=0`; final dry reported `updated=0 skipped=5 missing=0 bad=0`, all with `REPORT: Save succeeded`.

Read-back exports verified `5` metadata rows, `5` tag rows, `17` xref rows, `1005` target instruction rows, and `5` decompile rows. The refreshed queue reports `6089` total functions, `2796` commented, `3293` commentless, `1498` exact-undefined signatures, `1185` `param_N` signatures, and strict clean-signature proxy `2742/6089 = 45.03%`.

The post-wave project backup verified at `[maintainer-local-ghidra-backup-root]\BEA_20260518-201201_post_wave563_cfastvb_tail_verified` with `19` files, `159845255` bytes, `MissingCount=0`, `ExtraCount=0`, and `HashDiffCount=0`.

## Limits

This is static saved-Ghidra evidence only. Runtime D3D device behavior, dynamic vertex-buffer lock semantics, shared index-buffer lifetime, exact CFastVB/CVBuffer/CIBuffer layouts, BEA launch behavior, patching, and rebuild parity remain unproven.
