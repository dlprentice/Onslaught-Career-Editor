# Wave579 IScript Slot/Goodie Static Ghidra Readiness

Date: 2026-05-19

## Scope

Wave579 saved a bounded static Ghidra correction tranche for six fixed-ABI IScript command handlers at `0x005338a0..0x00533aa0`.

Targets:

| Address | Saved state |
| --- | --- |
| `0x005338a0` | `void __stdcall IScript__SetPlayerLives(void * script_args, void * unused_state, void * out_result)` |
| `0x005338d0` | `void __stdcall IScript__SetSlot(void * script_args, void * unused_state, void * out_result)` |
| `0x00533900` | `void __stdcall IScript__SetSlotSave(void * script_args, void * unused_state, void * out_result)` |
| `0x005339a0` | `void __stdcall IScript__GetSlotBitValue(void * script_args, void * unused_state, void * out_result)` |
| `0x00533a70` | `void __stdcall IScript__SetGoodieState(void * script_args, void * unused_state, void * out_result)` |
| `0x00533aa0` | `void __stdcall IScript__GetGoodieState(void * script_args, void * unused_state, void * out_result)` |

## Evidence

- `ApplyIScriptSlotGoodieWave579.java` dry run: `updated=0 skipped=6 renamed=0 would_rename=0 missing=0 bad=0`.
- Apply run: `updated=6 skipped=0 renamed=0 would_rename=0 missing=0 bad=0`.
- Final dry read-back: `updated=0 skipped=6 renamed=0 would_rename=0 missing=0 bad=0`.
- Each headless run reported `REPORT: Save succeeded`.
- Post exports verified `6` metadata rows, `6` tag rows, `6` xref rows, `1326` target instruction rows, `6` decompile rows, and `24` vtable rows.
- All six targets are registered by `ScriptCommandRegistry__InitBuiltins` and return with `RET 0xc`, matching the fixed three-stack-argument command ABI.
- The tranche distinguishes runtime `SetSlot` from persistent `SetSlotSave`, and documents the goodie handlers' 1-based script index over `g_Career_mGoodies[index-1]`.

## Queue Telemetry

Post-Wave579 static re-audit queue:

| Metric | Value |
| --- | ---: |
| Function objects | 6093 |
| Commented functions | 2933 |
| Commentless functions | 3160 |
| Exact `undefined` signatures | 1420 |
| `param_N` signatures | 1131 |
| Comment-backed proxy | `2933/6093 = 48.14%` |
| Strict comment-plus-clean-signature proxy | `2884/6093 = 47.33%` |

Next queue head: `0x00533b70 IScript__Create3PointPanCamera`.

## Backup

Verified Ghidra project backup:

- Path: `[maintainer-local-ghidra-backup-root]\BEA_20260519-041839_post_wave579_iscript_slot_goodie_verified`
- Files: `19`
- Bytes: `160467847`
- Diff count: `0`
- Manifest SHA-256: `186890AA3E40A41994E7EE75B1A6C6438169527715E3CB4D379C475E2FDF2FA5`

## Validation

- `py -3 tools\ghidra_iscript_slot_goodie_wave579_probe.py --check --json`: PASS (`failureCount=0`).
- `cmd.exe /c npm run test:ghidra-iscript-slot-goodie-wave579`: PASS.

## Not Proven

- runtime mission-script behavior remains unproven.
- Script corpus coverage for the slot/goodie handlers remains a separate evidence lane.
- Exact command descriptor layout and exact result datatype class labels remain unproven.
- BEA executable patching and rebuild parity remain unproven.
