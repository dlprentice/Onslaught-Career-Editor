# Ghidra CWeapon / Burst Context Wave552 Readiness Note

Date: 2026-05-18

## Scope

Wave552 hardened two static Ghidra functions from the old Wave133 CEngine-labeled cluster:

| Address | Saved symbol |
| --- | --- |
| `0x005068f0` | `void __fastcall CWeapon__AdvanceChargeProgressIfAnySlotAssigned(void * weapon)` |
| `0x005078b0` | `int __thiscall ProjectileBurstPreset__GetListEntryIdByIndex(void * this, int entry_index)` |

## Evidence

- `0x005068f0` is called by `CGeneralVolume__DispatchMode3BurstProgressAndSpawn` and `CBattleEngineWalkerPart__ChargeWeapon`, both with the current weapon/current-entry pointer in `ECX`.
- The `0x005068f0` body loads `weapon +0xa4` weapon-data, scans assigned-slot dwords at `+0x10..+0x1c` for any value other than `-1`, and when `weapon +0x60` is below `DAT_005db358`, adds `weapon-data +0x08` into `weapon +0x60`.
- `0x005078b0` is called by `ProjectileBurst__SpawnFromCurrentPreset` after wrapping `burstContext +0x70` against preset count `+0x58`; the caller pushes only that one index argument.
- `0x005078b0` ends with `RET 0x4`, proving one explicit stack argument after `this`; the older second stack parameter was a Ghidra artifact.
- `0x005078b0` walks the linked-list head at `this +0x4c` until `entry_index`, returns the selected entry id dword, and returns zero when the list/index is missing.

## Read-Back

- Dry: `updated=0 skipped=2 renamed=0 would_rename=2 missing=0 bad=0`.
- Apply: `updated=2 skipped=0 renamed=2 would_rename=0 missing=0 bad=0`.
- Verify dry: `updated=0 skipped=2 renamed=0 would_rename=0 missing=0 bad=0`.
- Ghidra save reported `REPORT: Save succeeded`.
- Post exports verified `2` metadata rows, `2` tag rows, `3` xref rows, `162` target instruction rows, `45` focused callsite instruction rows, `2` target decompile exports, and `4` caller decompile exports.
- Focused probe: `py -3 tools\ghidra_cweapon_burst_context_wave552_probe.py --check` PASS.
- npm wrapper: `cmd.exe /c npm run test:ghidra-cweapon-burst-context-wave552` PASS.
- Queue refresh: PASS with `6089` total functions, `2664` commented, `3425` commentless, `1535` exact-undefined signatures, and `1278` `param_N` signatures.
- Backup: `[maintainer-local-ghidra-backup-root]\BEA_20260518-134428_post_wave552_cweapon_burst_context_verified`, `19` files, `159353735` bytes, `MissingCount=0`, `ExtraCount=0`, `HashDiffCount=0`.

## Not Proven

- Exact source method/class identity for either helper.
- Concrete CWeapon, weapon-data, projectile-burst preset, linked-list, or entry layouts.
- Runtime charge/fire behavior, runtime projectile behavior, stealth behavior, BEA launch behavior, game patching, or rebuild parity.
