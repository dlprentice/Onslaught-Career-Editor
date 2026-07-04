# Ghidra RadarWarningReceiver Wave488 Readiness

Date: 2026-05-17

## Scope

- Hardened `5` CRadarWarningReceiver signatures/comments/tags: `0x00405a20`, `0x004d65a0`, `0x004d6600`, `0x004d66b0`, and `0x004d6a10`.
- Created the missing Ghidra function boundary at `0x004d6a10` as `CRadarWarningReceiver__VFunc_00_UpdateOnEvent4000`.
- Preserved the shared inherited helper `0x0044a830 VFuncSlot_03_0044a830` from Wave365 and used it as init-call context only.
- Left vtable slot `0x0060c5a0` unresolved; Wave488 did not create or name that inherited target.

## Validation

- `py -3 -m py_compile tools\ghidra_radarwarning_wave488_probe.py tools\ghidra_radarwarning_wave488_probe_test.py`
- `py -3 tools\ghidra_radarwarning_wave488_probe_test.py`
- `py -3 tools\ghidra_radarwarning_wave488_probe.py --check`
- `cmd.exe /c npm run test:ghidra-radarwarning-wave488`
- `cmd.exe /c npm run test:ghidra-static-reaudit-queue`
- Refreshed static queue: `6058` functions, `3865` commentless, `1682` undefined signatures, `1541` `param_N` signatures.

## Backup

- `[maintainer-local-ghidra-backup-root]\BEA_20260517-064445_post_wave488_radarwarning_verified`
- Verified: `19` files, `157387655` bytes, missing `0`, extra `0`, hash differences `0`.

## Boundary

Static retail-binary evidence only. Exact source identity, concrete CRadarWarningReceiver/threat-entry layouts beyond observed offsets, runtime HUD/audio scheduling behavior, full vtable ownership, BEA launch behavior, game patching, and rebuild parity remain unproven.
