# Ghidra CRT Fmod/FPU Head Wave630

Status: read-back verified
Date: 2026-05-20

Wave630 hardened five adjacent CRT FPU/fmod helper rows in the saved Ghidra project:

- `0x00563ada CRT__FpuIntDispatch2_Handle`
- `0x00563c0b __ctrandisp1`
- `0x00563c3e __fload`
- `0x00564486 CRT__FmodReduceCore`
- `0x0056468c CRT__FmodCore`

The pass saved comments/tags only. It intentionally made no signature, rename, function-boundary, or executable-byte changes because the tranche includes Visual Studio library helpers and custom FPU/stack-convention rows.

## Evidence

- Dry run: `updated=0 skipped=5 renamed=0 would_rename=0 missing=0 bad=0`
- Apply: `updated=5 skipped=0 renamed=0 would_rename=0 missing=0 bad=0`
- Final dry: `updated=0 skipped=5 renamed=0 would_rename=0 missing=0 bad=0`
- Post exports: `5` metadata rows, `5` tag rows, `9` xref rows, `505` instruction rows, `5` decompile rows
- Queue refresh: `6093` total, `3329` commented, `2764` commentless, `1217` exact-undefined signatures, `964` `param_N` signatures
- Strict clean-signature proxy: `3276/6093 = 53.77%`
- Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260520-084254_post_wave630_crt_fmod_verified` (`19` files, `162204551` bytes, `DiffCount=0`)

The next high-signal queue head is `0x00564a0b CDXTexture__LoadFromPathWithFallbackExtensions`.

## Limits

This is static saved-Ghidra evidence only. Exact CRT identity/version, custom FPU stack payload layout, runtime fmod/transcendental behavior, BEA patching, and rebuild parity remain unproven.
