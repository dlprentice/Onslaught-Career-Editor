# Ghidra CPlane Hit/Animation Wave485 Readiness

Date: 2026-05-17

## Scope

- Corrected `0x004d1f10` to `CPlane__Hit_CheckFatalDamageAndDie`.
- Corrected `0x004d1f90` to `CPlane__PlayWingOpenAnimationOnce`.
- Corrected `0x004d1fd0` to `CPlane__PlayWingCloseAnimationOnce`.
- Corrected `0x004d2010` to `CPlane__UpdateAttackLaunchAnimationState`.
- Evidence: post-readback metadata, tags, decompile, xrefs, instruction rows, raw-caller rows, vtable/RTTI rows, and focused probe.

## Validation

- `py -3 tools\ghidra_plane_hit_animation_wave485_probe_test.py`
- `py -3 tools\ghidra_plane_hit_animation_wave485_probe.py --check`
- `cmd.exe /c npm run test:ghidra-plane-hit-animation-wave485`
- `py -3 tools\ghidra_static_reaudit_queue_probe.py --check --json`
- Refreshed static queue: `6057` functions, `3889` commentless, `1701` undefined signatures, `1544` `param_N` signatures.

## Backup

- `G:\GhidraBackups\BEA_20260517-051553_post_wave485_plane_hit_animation_verified`
- Verified: `19` files, `157322119` bytes, missing `0`, extra `0`, hash differences `0`.

## Boundary

Static retail-binary evidence only. Exact CPlane layout, raw caller boundaries, runtime hit/death behavior, runtime wing/attack/launch animation behavior, source body identity, BEA launch behavior, game patching, and rebuild parity remain unproven.
