# Ghidra RTCutscene Wave489 Readiness

Date: 2026-05-17

## Scope

- Hardened `20` RTCutscene/CRenderThing/shared-vfunc targets around vtable `0x005dea38`.
- Created or recovered `10` compact/vtable function boundaries, including `0x00405940`, `0x004dbb80`, `0x004dbbe0`, `0x004dbc10`, `0x004dbe50`, `0x004dbec0`, `0x004dbf80`, `0x004dbfb0`, `0x004dbfc0`, and `0x004dbff0`.
- Corrected stale destructor/base-helper names, including `CRTCutscene__scalar_deleting_dtor`, `CRTCutscene__dtor`, `CRenderThing__dtor`, and `CRenderThing__scalar_deleting_dtor`.
- Kept shared return/clear-output helpers owner-neutral where broad vtable/xref evidence prevents a narrow RTCutscene-only label.

## Validation

- `py -3 -m py_compile tools\ghidra_rtcutscene_wave489_probe.py`
- `py -3 tools\ghidra_rtcutscene_wave489_probe.py --check`
- `cmd.exe /c npm run test:ghidra-rtcutscene-wave489`
- `py -3 tools\ghidra_static_reaudit_queue_probe_test.py`
- `py -3 tools\ghidra_static_reaudit_queue_probe.py --check`
- Refreshed static queue: `6068` functions, `3855` commentless, `1676` undefined signatures, `1538` `param_N` signatures.

## Evidence

- Apply/read-back artifacts: `subagents/ghidra-static-reaudit/wave489-rtcutscene-renderthing-004d6a30/`
- Clean apply/probe summary: dry `updated=0 skipped=20`, idempotent apply `updated=20 skipped=0`, verify dry `updated=0 skipped=20`.
- Read-back exports: `20` metadata rows, `20` tag rows, `20` vtable rows, `115` xref rows, `3380` instruction rows, and `20` decompile exports.

## Backup

- `G:\GhidraBackups\BEA_20260517-073006_post_wave489_rtcutscene_verified`
- Verified: `19` files, `157518727` bytes, missing `0`, extra `0`, hash differences `0`.

## Boundary

Static retail-binary evidence only. Exact source identity, concrete `CRTCutscene`/`CRenderThing` layouts, mesh-entry/output-record structures, runtime cutscene rendering behavior, BEA launch behavior, game patching, and rebuild parity remain unproven.
