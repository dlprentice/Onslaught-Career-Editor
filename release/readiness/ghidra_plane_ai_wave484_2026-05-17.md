# Ghidra CPlaneAI Wave484 Readiness

Date: 2026-05-17

## Scope

- Corrected `0x004d1c10` to `CPlaneAI__scalar_deleting_dtor`.
- Corrected `0x004d1c30` to `CPlaneAI__dtor_body`.
- Set signatures to `void * __thiscall CPlaneAI__scalar_deleting_dtor(void * this, byte flags)` and `void __fastcall CPlaneAI__dtor_body(void * this)`.
- Evidence: post-readback metadata, tags, decompile, xrefs, instruction rows, vtable/RTTI rows, and source-absence checks.

## Validation

- `py -3 tools\ghidra_plane_ai_wave484_probe_test.py`
- `cmd.exe /c npm run test:ghidra-plane-ai-wave484`
- `cmd.exe /c npm run test:ghidra-static-reaudit-queue`
- Refreshed static queue: `6057` functions, `3893` commentless, `1701` undefined signatures, `1548` `param_N` signatures.

## Backup

- `G:\GhidraBackups\BEA_20260517-044026_post_wave484_plane_ai_verified`
- Verified: `19` files, `157322119` bytes, missing `0`, extra `0`, hash differences `0`.

## Boundary

Static retail-binary evidence only. Exact `CPlaneAI` layout, linked-set semantics, allocator ownership, runtime AI destruction behavior, source body identity, BEA launch behavior, game patching, and rebuild parity remain unproven.
