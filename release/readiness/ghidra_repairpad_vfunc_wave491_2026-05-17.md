# Ghidra RepairPadAI Vfunc Wave491 Readiness

Date: 2026-05-17

## Scope

- Hardened queue-head `0x004d6d10` from `CRepairPadAI__VFunc_11_004d6d10` to `CRepairPadAI__VFunc_11_UpdateDockCandidateReader`.
- Set the saved signature to `void * __fastcall CRepairPadAI__VFunc_11_UpdateDockCandidateReader(void * this)`.
- Preserved existing function boundary; no functions were created.

## Validation

- `py -3 -m py_compile tools\ghidra_repairpad_vfunc_wave491_probe.py`
- `py -3 tools\ghidra_repairpad_vfunc_wave491_probe.py --check`
- `cmd.exe /c npm run test:ghidra-repairpad-vfunc-wave491`
- `cmd.exe /c npm run test:ghidra-static-reaudit-queue`
- Refreshed static queue: `6068` functions, `3852` commentless, `1674` undefined signatures, `1537` `param_N` signatures.

## Evidence

- Apply/read-back artifacts: `subagents/ghidra-static-reaudit/wave491-repairpad-vfunc-004d6d10/`
- Clean apply/probe summary: dry `updated=0 skipped=1 would_rename=1`, apply `updated=1 skipped=0 renamed=1`, verify dry `updated=0 skipped=1 would_rename=0`.
- Read-back exports: `4` RepairPadAI context metadata rows, `4` tag rows, decompile exports, xref exports, instruction exports, and vtable-slot evidence for `0x005d8e08` slot 11.
- A first compile-only API mismatch made no Ghidra mutation. A first post-apply dry exposed a strict idempotence comparison issue; the final script compares signature components and verifies with `SKIP`.

## Backup

- `G:\GhidraBackups\BEA_20260517-081712_post_wave491_repairpad_vfunc_verified`
- Verified: `19` files, `157551495` bytes, missing `0`, extra `0`, hash differences `0`.

## Boundary

Static retail-binary evidence only. Exact source virtual name, concrete `CRepairPadAI` layout, runtime repair/docking behavior, BEA launch behavior, game patching, and rebuild parity remain unproven.
