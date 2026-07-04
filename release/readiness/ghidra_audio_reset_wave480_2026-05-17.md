# Ghidra Audio Reset Wave480 Readiness

Date: 2026-05-17

## Scope
- Corrected `0x004cddf0` from stale `CEngine__RestoreAudioAfterDeviceReset` to `Audio__ReinitializeSoundAndRestoreMusic`.
- Hardened `0x00517f10` as `void __thiscall CSoundManager__ReinitializeAfterDeviceLoss(void * this)`.
- Evidence: `OptionsTail_Read`, wrapper/callee xrefs, post-readback decompile/instruction rows, source sound/music references, and read-only raw config-change thunk ranges.

## Validation
- `py -3 tools\ghidra_audio_reset_wave480_probe_test.py`
- `py -3 tools\ghidra_audio_reset_wave480_probe.py --check`
- `cmd.exe /c npm run test:ghidra-audio-reset-wave480`
- Refreshed static queue: `6057` functions, `3898` commentless, `1702` undefined signatures, `1552` `param_N` signatures.

## Backup
- `[maintainer-local-ghidra-backup-root]\BEA_20260517-023240_post_wave480_audio_reset_verified`
- Verified: `19` files, `157289351` bytes, missing `0`, extra `0`, hash differences `0`.

## Boundary
Static retail-binary evidence only. Runtime audio behavior, exact source identity, raw thunk boundaries, BEA launch behavior, patching, and rebuild parity remain unproven.
