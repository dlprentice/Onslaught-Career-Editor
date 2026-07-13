# Wave580 IScript Camera/Objective Static Read-Back

<!-- ghidra-full-reaudit-20260713:start -->
> **2026-07-13 semantic revalidation:** Historical record; `0x005345d0` comment correction. The original text below remains provenance rather than current semantic authority. Use the [closeout](../../reverse-engineering/binary-analysis/ghidra-full-reaudit-closeout-2026-07-13.md); exact records are in `reverse-engineering/binary-analysis/ghidra-full-reaudit-corrections-2026-07-13.json` and `reverse-engineering/binary-analysis/ghidra-targeted-revalidation-corrections-2026-07-13.json`.
<!-- ghidra-full-reaudit-20260713:end -->

Status: PASS on 2026-05-19

## Scope

Wave580 hardened six adjacent MissionScript `IScript` command handlers in the saved Ghidra project:

| Address | Function | Saved signature |
| --- | --- | --- |
| `0x00533b70` | `IScript__Create3PointPanCamera` | `void __stdcall IScript__Create3PointPanCamera(void * script_args, void * unused_state, void * out_result)` |
| `0x00533eb0` | `IScript__Create4PointPanCamera` | `void __stdcall IScript__Create4PointPanCamera(void * script_args, void * unused_state, void * out_result)` |
| `0x005343e0` | `IScript__PrimaryObjectiveComplete` | `void __stdcall IScript__PrimaryObjectiveComplete(void * script_args, void * unused_state, void * out_result)` |
| `0x00534410` | `IScript__SecondaryObjectiveComplete` | `void __stdcall IScript__SecondaryObjectiveComplete(void * script_args, void * unused_state, void * out_result)` |
| `0x00534440` | `IScript__PrimaryObjectiveFailed` | `void __stdcall IScript__PrimaryObjectiveFailed(void * script_args, void * unused_state, void * out_result)` |
| `0x00534470` | `IScript__SecondaryObjectiveFailed` | `void __stdcall IScript__SecondaryObjectiveFailed(void * script_args, void * unused_state, void * out_result)` |

All six rows are registered by `ScriptCommandRegistry__InitBuiltins` and return with `RET 0xc`, matching the fixed three-stack-argument script command ABI. No renames were applied.

## Evidence

- `IScript__Create3PointPanCamera` gets a thing through argument vtable slot `+0x40`, reports null thing string `0x0064fa9c`, transforms three vector arguments through the thing matrix or `DAT_0083d9c0`, builds a `CSPtrSet`/`CBSpline`, constructs a `CPanCamera`, and calls `CGame__SetCurrentCamera(&DAT_008a9a98,0,camera,1)`.
- `IScript__Create4PointPanCamera` follows the same pan-camera path with four vector arguments and null thing string `0x0064fad8`.
- The primary objective handlers write text ids to `DAT_008a9ae0 + index*8` and state values to `DAT_008a9adc + index*8`.
- The secondary objective handlers write text ids to `DAT_008a9b30 + index*8` and state values to `DAT_008a9b2c + index*8`.
- Complete handlers write state `1`; failed handlers write state `2`.

Read-back artifacts:

- Dry/apply/final dry: `updated=0 skipped=6 renamed=0 would_rename=0 missing=0 bad=0`, then `updated=6 skipped=0 renamed=0 would_rename=0 missing=0 bad=0`, then `updated=0 skipped=6 renamed=0 would_rename=0 missing=0 bad=0`.
- Post exports verified `6` metadata rows, `6` tag rows, `6` xref rows, `5454` instruction rows, `6` decompile rows, and `36` vtable rows.
- Backup verified: `[maintainer-local-ghidra-backup-root]\BEA_20260519-044247_post_wave580_iscript_camera_objective_verified`, `19` files, `160500615` bytes, `DiffCount=0`, manifest hash `83E6EF0DFB8B3CE5A29E8A55C7F02A8DD40A3C6E8A1BAD5826A0722E4496C0B1`.

## Queue Telemetry

After Wave580:

| Metric | Value |
| --- | ---: |
| Total functions | `6093` |
| Commented functions | `2939` |
| Commentless functions | `3154` |
| Exact `undefined` signatures | `1418` |
| `param_N` signatures | `1127` |
| Comment-backed proxy | `2939/6093 = 48.24%` |
| Strict clean-signature proxy | `2890/6093 = 47.43%` |

Next high-signal queue head: `0x005345d0 IScript__GetVectorLength`.

## Not Proven

- runtime mission-script behavior remains unproven.
- Runtime mission-objective UI behavior remains unproven.
- script corpus coverage remains unproven.
- Exact command descriptor layout remains unproven.
- BEA patching and rebuild parity remain unproven.
