# Ghidra CPlane Init Wave483 Readiness

Date: 2026-05-17

## Scope

- Hardened `0x004d19d0 CPlane__Init`.
- Set signature to `void __thiscall CPlane__Init(void * this, void * init_thing)`.
- Evidence: post-readback metadata, tags, decompile, xrefs, instruction rows, callee metadata, and source-absence checks.
- Corrected stale doc/comment shape from `this+0x80` to `init_thing+0x80`; final probe guards that distinction.

## Validation

- `py -3 tools\ghidra_plane_init_wave483_probe_test.py`
- `cmd.exe /c npm run test:ghidra-plane-init-wave483`
- `cmd.exe /c npm run test:ghidra-static-reaudit-queue`
- Refreshed static queue: `6057` functions, `3895` commentless, `1701` undefined signatures, `1550` `param_N` signatures.

## Backup

- `[maintainer-local-ghidra-backup-root]\BEA_20260517-040832_post_wave483_plane_init_verified`
- Verified: `19` files, `157322119` bytes, missing `0`, extra `0`, hash differences `0`.

## Boundary

Static retail-binary evidence only. Exact `CPlane` layout, `init_thing` field meaning, `CWarspite` semantics/signature, runtime flight/launch behavior, source body identity, BEA launch behavior, game patching, and rebuild parity remain unproven.
