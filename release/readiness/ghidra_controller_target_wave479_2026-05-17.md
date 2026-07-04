# Ghidra Controller-Target Helper Wave479 Readiness

Date: 2026-05-17

## Scope
- Corrected `0x004cdd70` from stale `CRocket__RelinquishControllerOwnership` to `GameControllers__RelinquishControlForTarget`.
- Saved signature: `void __fastcall GameControllers__RelinquishControlForTarget(void * controlled_target)`.
- Evidence: target disassembly, `CMessageLog__HandleInputCommand`, raw caller `0x0048ffcc`, `CGame__GetController`, `CController__GetToControl`, and `CController__RelinquishControl`.

## Validation
- `py -3 tools\ghidra_controller_target_wave479_probe_test.py`
- `py -3 tools\ghidra_controller_target_wave479_probe.py --check`
- `cmd.exe /c npm run test:ghidra-controller-target-wave479`
- Refreshed static queue: `6057` functions, `3900` commentless, `1702` undefined signatures, `1553` `param_N` signatures.

## Backup
- `[maintainer-local-ghidra-backup-root]\BEA_20260517-020552_post_wave479_controller_target_verified`
- Verified: `19` files, `157256583` bytes, missing `0`, extra `0`, hash differences `0`.

## Boundary
Static retail-binary evidence only. Exact Stuart-source identity, concrete control-target type, runtime input/menu behavior, BEA launch behavior, patching, and rebuild parity remain unproven.
