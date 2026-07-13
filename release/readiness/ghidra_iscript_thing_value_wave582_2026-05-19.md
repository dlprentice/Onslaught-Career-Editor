# Ghidra IScript Thing-Value Wave582 Readiness

<!-- ghidra-full-reaudit-20260713:start -->
> **2026-07-13 semantic revalidation:** Historical record; `0x00535560` comment correction. The original text below remains provenance rather than current semantic authority. Use the [closeout](../../reverse-engineering/binary-analysis/ghidra-full-reaudit-closeout-2026-07-13.md); exact records are in `reverse-engineering/binary-analysis/ghidra-full-reaudit-corrections-2026-07-13.json` and `reverse-engineering/binary-analysis/ghidra-targeted-revalidation-corrections-2026-07-13.json`.
<!-- ghidra-full-reaudit-20260713:end -->

Status: validated static Ghidra read-back
Date: 2026-05-19

Wave582 hardened six script-context IScript command handlers: `IScript__SetThingValueViaVFunc198_FromArg`, `IScript__SetThingValueViaVFunc19C_FromArg`, `IScript__SetThingValueViaEngineHelper4FE390_FromArg`, `IScript__SetThingValueViaEngineHelper4FE3F0_FromArg`, `IScript__SetThingFloatViaVFunc1C8_FromArg`, and `IScript__SetThingRefViaCUnitHelper4FD830_FromArg`.

The saved signatures use the `__thiscall` script-context shape: ECX is the command context and `RET 0xc` confirms the three stack arguments `script_args`, `unused_state`, and `out_result`. This differs from the prior fixed `__stdcall` command handlers, and the final apply read-back explicitly confirms the implicit Ghidra `this` plus three stack arguments.

Read-back evidence:

| Check | Result |
| --- | --- |
| Dry/apply/final dry | `updated=0 skipped=6`, then `updated=6 skipped=0`, then `updated=0 skipped=6`, all with `missing=0 bad=0` and `REPORT: Save succeeded` |
| Post exports | `6` metadata rows, `6` tag rows, `6` xref rows, `534` target instruction rows, `6` decompile rows, `32` vtable rows |
| Queue refresh | `6093` functions, `2950` commented, `3143` commentless, `1413` exact-undefined signatures, `1121` `param_N`; next head `0x00535330 CVM__VFunc_01_00535330` |
| Backup | `[maintainer-local-ghidra-backup-root]\BEA_20260519-082352_post_wave582_iscript_thing_value_verified`, `19` files, `160598919` bytes, `DiffCount=0` |

Bounded claims:

- The two vfunc handlers dispatch script-provided values to selected thing vtable slots `+0x198` and `+0x19c`.
- The engine helper handlers read a script-provided thing name through datatype getter slot `+0x38` and call `CEngine__EnableThingByNameFlag` / `CEngine__DisableThingByNameFlag`.
- The float setter reads through datatype getter slot `+0x34` and dispatches selected thing vtable slot `+0x1c8`.
- The Unit helper handler reads an integer/faction-like state through datatype getter slot `+0x30` and calls `CUnit__SetFactionForHierarchy`.

Not proven:

- runtime mission-script behavior remains unproven.
- Script corpus coverage remains unproven.
- Exact command descriptor layout, exact vtable slot semantics, exact faction/state enum naming, BEA patching, and rebuild parity remain deferred.
