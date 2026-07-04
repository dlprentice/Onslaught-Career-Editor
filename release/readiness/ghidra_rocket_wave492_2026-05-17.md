# Ghidra CRocket Wave492 Readiness

Date: 2026-05-17

## Scope

- Hardened queue-head `0x004d7b10` from `CRocket__VFunc_09_004d7b10` to `CRocket__Init`.
- Hardened `0x004d8040` from `CRocket__VFunc_22_004d8040` to `CRocket__VFunc_22_CreateBigRocketEngineEffects`.
- Set saved signatures to `void __thiscall CRocket__Init(void * this, void * init)` and `void __fastcall CRocket__VFunc_22_CreateBigRocketEngineEffects(void * this)`.
- Preserved existing function boundaries; no functions were created.

## Validation

- `py -3 -m py_compile tools\ghidra_rocket_wave492_probe.py`
- `py -3 tools\ghidra_rocket_wave492_probe.py --check`
- `cmd.exe /c npm run test:ghidra-rocket-wave492`
- `cmd.exe /c npm run test:ghidra-static-reaudit-queue`
- Refreshed static queue: `6068` functions, `3850` commentless, `1674` undefined signatures, `1535` `param_N` signatures.

## Evidence

- Apply/read-back artifacts: `subagents/ghidra-static-reaudit/wave492-rocket-round-004d7b10/`
- Clean apply/probe summary: dry `updated=0 skipped=2 would_rename=2`, apply `updated=2 skipped=0 renamed=2`, verify dry `updated=0 skipped=2 would_rename=0`.
- Read-back exports: `7` CRocket/Round context metadata rows, `7` tag rows, decompile exports, xref exports, instruction exports, and vtable-slot evidence for CRocket vtable `0x005dd458` slots 9 and 22.
- Static behavior evidence includes `m_rocket.msh` descriptor setup, `PCRTID__CreateObject(1)`, `CActor__Init`, `Big Rocket Engine Effect` lookup, and four `CParticleManager__CreateEffect` calls.

## Backup

- `[maintainer-local-ghidra-backup-root]\BEA_20260517-084058_post_wave492_rocket_verified`
- Verified: `19` files, `157584263` bytes, missing `0`, extra `0`, hash differences `0`.

## Boundary

Static retail-binary evidence only. Exact source virtual names, concrete `CRocket` / init / particle-handle layouts, runtime rocket launch/render/effect behavior, BEA launch behavior, game patching, and rebuild parity remain unproven.
