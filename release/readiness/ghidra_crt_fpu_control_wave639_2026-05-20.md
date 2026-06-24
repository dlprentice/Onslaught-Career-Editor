# Ghidra CRT FPU Control Wave639

Status: read-back verified
Date: 2026-05-20

Wave639 hardened four adjacent CRT x87 FPU-control rows in the saved Ghidra project:

- `0x00569449 CRT__ControlFp`
- `0x0056947e CRT__ControlFpMasked`
- `0x00569494 CRT__FpuControlWordToPublicMask`
- `0x00569526 CRT__PublicMaskToFpuControlWord`

The pass corrected `CRT__ControlFpMasked_0056947e` to `CRT__ControlFpMasked`, corrected the reversed converter labels `CRT__ControlFpPublicToInternal` and `CRT__ControlFpInternalToPublic` to the observed x87/public-mask directions, saved signatures/comments/tags for all four rows, and made no function-boundary or executable-byte changes.

## Evidence

- Dry run: `updated=0 skipped=4 renamed=0 would_rename=3 signature_updated=0 missing=0 bad=0`
- Apply: `updated=4 skipped=0 renamed=3 would_rename=0 signature_updated=4 missing=0 bad=0`
- Final dry: `updated=0 skipped=4 renamed=0 would_rename=0 signature_updated=0 missing=0 bad=0`
- Post exports: `4` metadata rows, `4` tag rows, `7` xref rows, `484` instruction rows, `4` decompile rows
- Queue refresh: `6093` total, `3407` commented, `2686` commentless, `1217` exact-undefined signatures, `898` `param_N` signatures
- Strict clean-signature proxy: `3356/6093 = 55.08%`
- Verified backup: `G:\GhidraBackups\BEA_20260520-124847_post_wave639_crt_fpu_control_verified` (`19` files, `162532231` bytes, `DiffCount=0`)

The next high-signal queue head is `0x005695af CRT__ToLower_005695af`.

## Limits

This is static saved-Ghidra evidence only. Exact MSVC CRT version, complete x87/SSE control policy, denormal-mask API identity, full public flag contract, floating-point exception side effects, runtime numeric behavior, BEA patching, and rebuild parity remain unproven.
