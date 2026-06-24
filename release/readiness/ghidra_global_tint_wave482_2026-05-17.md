# Ghidra Global Tint Wave482 Readiness

Date: 2026-05-17

## Scope

- Hardened `0x004d1710 CDXEngine__SetGlobalTintColorOpaque`.
- Set signature to `void __cdecl CDXEngine__SetGlobalTintColorOpaque(uint tint_payload)`.
- Evidence: post-readback metadata, tags, decompile, xrefs, instruction rows, exact global operand refs, caller decompile, and callsite pushed constants.

## Validation

- `py -3 tools\ghidra_global_tint_wave482_probe_test.py`
- `cmd.exe /c npm run test:ghidra-global-tint-wave482`
- `cmd.exe /c npm run test:ghidra-static-reaudit-queue`
- Refreshed static queue: `6057` functions, `3896` commentless, `1702` undefined signatures, `1550` `param_N` signatures.

## Backup

- `G:\GhidraBackups\BEA_20260517-032754_post_wave482_global_tint_verified`
- Verified: `19` files, `157289351` bytes, missing `0`, extra `0`, hash differences `0`.

## Boundary

Static retail-binary evidence only. Exact global layout, palette/color packing, consumer path, runtime visual behavior, source identity, BEA launch behavior, game patching, and rebuild parity remain unproven.
