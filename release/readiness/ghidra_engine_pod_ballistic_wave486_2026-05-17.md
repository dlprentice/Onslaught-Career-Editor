# Ghidra Engine / CPOD / Ballistic Wave486 Readiness

Date: 2026-05-17

## Scope

- Hardened `0x004d3020` as `CEngine__SetOptionValueAndNotifyTarget`.
- Corrected `0x004d3630` to `CPod__VFunc_66_UpdateMotionAndAccumulateScalar`.
- Hardened `0x004d36c0` as `CUnit__InitBallisticAimState`.
- Hardened `0x004d3730` as `CUnit__ComputeBallisticLaunchVelocity`.
- Evidence: post-readback metadata, tags, decompile, xrefs, instruction rows, raw-caller rows, CPOD RTTI/vtable rows, and focused probe.

## Validation

- `py -3 tools\ghidra_engine_pod_ballistic_wave486_probe_test.py`
- `py -3 tools\ghidra_engine_pod_ballistic_wave486_probe.py --check`
- `cmd.exe /c npm run test:ghidra-engine-pod-ballistic-wave486`
- `cmd.exe /c npm run test:ghidra-static-reaudit-queue`
- Refreshed static queue: `6057` functions, `3885` commentless, `1701` undefined signatures, `1541` `param_N` signatures.

## Backup

- `G:\GhidraBackups\BEA_20260517-054050_post_wave486_engine_pod_ballistic_verified`
- Verified: `19` files, `157322119` bytes, missing `0`, extra `0`, hash differences `0`.

## Boundary

Static retail-binary evidence only. Exact owner/source identities, concrete layouts, CPOD slot contract, target vfunc identities, runtime options/god behavior, runtime motion/ballistic behavior, BEA launch behavior, game patching, and rebuild parity remain unproven.
