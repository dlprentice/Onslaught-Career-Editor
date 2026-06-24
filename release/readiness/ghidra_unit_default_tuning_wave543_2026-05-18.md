# Ghidra Unit Default Tuning Wave543 Readiness Note

Date: 2026-05-18

## Scope

Wave543 saved a static Ghidra signature/comment/tag hardening pass for one CUnit default tuning-block helper:

| Address | Saved name | Saved signature |
| --- | --- | --- |
| `0x004eb9a0` | `CUnit__InitDefaultTuningBlock` | `void __fastcall CUnit__InitDefaultTuningBlock(void * tuning_block)` |

The helper is a register-only initializer that writes fixed dword defaults to the block passed in `ECX` across offsets `+0x00..+0x84`. The observed constants include `1.0` at `+0x00/+0x04/+0x08/+0x0c/+0x1c/+0x50/+0x60`, `0.1` at `+0x40`, `0.8` at `+0x54/+0x58/+0x5c`, and zero elsewhere. A raw thunk at `0x004eb1d0` loads `ECX` with `0x0083d248` and jumps to the helper, indicating at least one global-default instance.

## Evidence

- Apply script: `tools/ApplyUnitDefaultTuningWave543.java`.
- Probe: `tools/ghidra_unit_default_tuning_wave543_probe.py`.
- Read-back artifacts: `subagents/ghidra-static-reaudit/wave543-cunit-default-tuning-004eb9a0/`.
- Dry run: `updated=0 skipped=1 renamed=0 would_rename=0 missing=0 bad=0`.
- Apply: `updated=1 skipped=0 renamed=0 would_rename=0 missing=0 bad=0`, with `REPORT: Save succeeded`.
- Verify dry: `updated=0 skipped=1 renamed=0 would_rename=0 missing=0 bad=0`.
- Post read-back verified `1` metadata row, `1` tag row, `1` xref row from raw/no-function caller `0x004eb1d5`, `145` target instruction rows, `97` caller instruction rows, and `1` decompile export.
- Focused probe: `py -3 tools\ghidra_unit_default_tuning_wave543_probe.py --check` PASS.
- Npm wrapper: `cmd.exe /c npm run test:ghidra-unit-default-tuning-wave543` PASS.
- Queue refresh: `py -3 tools\ghidra_static_reaudit_queue_probe.py --check --json` PASS after refreshing the live quality snapshot.
- Backup: `G:\GhidraBackups\BEA_20260518-100152_post_wave543_unit_default_tuning_verified`, `19` files, `159320967` bytes, `MissingCount=0`, `ExtraCount=0`, `HashDiffCount=0`.

## Queue Snapshot

Fresh queue telemetry after Wave543:

| Metric | Value |
| --- | ---: |
| Function objects | `6089` |
| Commented functions | `2649` |
| Commentless functions | `3440` |
| Exact-undefined signatures | `1535` |
| `param_N` signatures | `1292` |
| Comment-backed proxy | `2649/6089 = 43.51%` |
| Strict comment-plus-clean-signature proxy | `2595/6089 = 42.62%` |

This is telemetry only, not a completion milestone.

## Not Proven

- Exact struct field names for the tuning block.
- Exact source identity or source-body parity.
- Runtime tuning behavior or global-default ownership beyond the observed raw thunk.
- BEA launch, executable patching, and rebuild parity.
