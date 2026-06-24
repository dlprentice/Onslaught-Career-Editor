# Ghidra FEPWingmen Wave565 Readiness Note

Date: 2026-05-18
Status: PASS

## Scope

Wave565 hardened six existing FEPWingmen-adjacent rows:

| Address | Saved state | Evidence |
| --- | --- | --- |
| `0x00521650` | `char CFEPWingmen__GetWingmenCount(void)` | `CFEPBEConfig` render/button callers use it to scan `DAT_0089da6c` / `DAT_0089da74` for current level `DAT_0089d94c` and count nonzero wingman slots. |
| `0x00521a60` | `void __fastcall CFEPWingmen__Destroy(void * this)` | Vtable `0x005dba10` slot 1 cleanup path; frees `this+0x08/+0x0c/+0x10` frontend thing pointers and drains pointer set `this+0x28`. Signature convention remains deferred. |
| `0x00521ae0` | `void __thiscall CFEPWingmen__Load(void * this, void * stream)` | `RET 0x4`, `ECX` receiver storage, and stack stream use correct the stale `__stdcall` signature. |
| `0x00521c80` | `void __thiscall CFEPWingmen__Update(void * this, int state)` | Vtable slot 2 update path; updates timer/fade fields, calls the shared spinner helper, and references missing dev-mode slot target `0x00521d20`. |
| `0x005230c0` | `void __thiscall CFEPWingmen__TransitionNotification(void * this, int from_page)` | Renamed from `CFEPWingmen__VFunc_06_005230c0`; vtable slot 6 matches the frontend transition-notification convention and returns with `RET 0x4`. |
| `0x0046baf0` | `void __thiscall CFEPWingmen__UpdateSpinnerTransformAndPulse(void * this)` | Shared frontend spinner transform/pulse helper called by Wingmen, MultiplayerStart, and BEConfig paths. |

This class is retail-binary-first because `FEPWingmen.cpp` is not present in `references/Onslaught`; no `source-parity` tag was applied. Missing FEPWingmen vtable boundaries at `0x005216c0`, `0x00521d20`, `0x00522160`, and `0x00522190` remain deferred.

## Verification

- Dry pass: `updated=0 skipped=6 renamed=0 would_rename=1 missing=0 bad=0`, `REPORT: Save succeeded`
- Apply pass: `updated=6 skipped=0 renamed=1 missing=0 bad=0`, `REPORT: Save succeeded`
- Final dry: `updated=0 skipped=6 renamed=0 would_rename=0 missing=0 bad=0`, `REPORT: Save succeeded`
- Post exports: `6` metadata rows plus expected missing `0x005216c0`, `6` tag rows, `13` xref rows, `1015` focused instruction rows, `6` target decompiles, and `16` vtable rows
- Queue refresh: `6089` total functions, `2806` commented, `3283` commentless, `1498` exact-undefined signatures, `1180` `param_N` signatures
- Strict proxy: `2806 / 6089 = 46.09%`
- Backup: `G:\GhidraBackups\BEA_20260518-211003_post_wave565_fepwingmen_verified`
- Backup verification: `19` files, `159910791` bytes, source/destination manifest hash `F7B863819658321D9F8EDA2D6B8DD2FB963C23E3A92FE33789468440988667E4`

## Limits

This is saved static Ghidra evidence only. Runtime wingman selection behavior, concrete `CFEPWingmen` or record layouts, data-file schema, missing vtable-boundary identities, exact source identity, BEA launch, game patching, and rebuild parity remain unproven.
