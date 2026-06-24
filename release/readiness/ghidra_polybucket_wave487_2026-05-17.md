# Ghidra CPolyBucket Wave487 Readiness

Date: 2026-05-17

## Scope

- Hardened `17` existing CPolyBucket signatures/comments/tags from `0x004d3b10` through `0x004d6210`.
- Covered the AABB helper, triangle cell test, bucket builder, compression/decompression helpers, point/line search iterators, random-triangle sampler, deserializer, debug renderer, and vertex-store helpers.
- No function objects were created and no names were changed.
- Deferred `0x005491b0 CPolyBucket__ReallocFromPool` to a separate allocator/helper pass.

## Validation

- `py -3 tools\ghidra_polybucket_wave487_probe_test.py`
- `py -3 tools\ghidra_polybucket_wave487_probe.py --check`
- `cmd.exe /c npm run test:ghidra-polybucket-wave487`
- `cmd.exe /c npm run test:ghidra-static-reaudit-queue`
- Refreshed static queue: `6057` functions, `3868` commentless, `1685` undefined signatures, `1541` `param_N` signatures.

## Backup

- `G:\GhidraBackups\BEA_20260517-063000_post_wave487_polybucket_verified`
- Verified: `19` files, `157387655` bytes, missing `0`, extra `0`, hash differences `0`.

## Boundary

Static retail-binary evidence only. Concrete CPolyBucket/CMeshPart layouts, exact stream/chunk contract, allocator ownership, exact source-body identity, runtime collision/render/debug behavior, BEA launch behavior, game patching, and rebuild parity remain unproven.
