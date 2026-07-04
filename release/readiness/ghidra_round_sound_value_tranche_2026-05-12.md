# Ghidra Round / Sound Value Tranche - 2026-05-12

Status: GREEN static Ghidra correction evidence.

## Scope

Wave 337 continued the `CPhysicsScriptStatements.cpp` static re-audit immediately after the weapon-mode value tranche. It saved names, signatures, comments, and tags for seven existing round/sound value-family functions and created no new function boundaries.

This wave explicitly corrects Wave 336's `0x004359c0` wording: fresh adjacent destructor-wrapper read-back showed `0x004359c0` is the `CPhysicsWeaponModeValue` base destructor body, not a constructor-base body.

| Address | Saved state | Evidence summary |
| --- | --- | --- |
| `0x004359c0` | `void __fastcall CPhysicsWeaponModeValue__dtor_base(void * this)` | Base destructor body called by the adjacent scalar-deleting destructor wrapper. This supersedes the Wave 336 constructor-base wording. |
| `0x00437080` | `void * __thiscall CPhysicsWeaponModeValue__scalar_deleting_dtor(void * this, int flags)` | Calls `0x004359c0`, optionally frees `this` through `OID__FreeObject` when flags bit 0 is set, and returns `this`. |
| `0x004370a0` | `void __thiscall CWeaponRound__ApplyToWeaponModeByName(void * this, char * weaponModeName)` | Searches `DAT_008553ec` by weapon-mode name and `DAT_008553f0` by round name, then writes the selected round reader/index. |
| `0x004371c0` | `void __thiscall CWeaponLaunchSound__ApplyToWeaponModeByName(void * this, char * weaponModeName)` | Replaces the owned launch-sound string at weapon-mode record `+0x24`. |
| `0x004372b0` | `void __thiscall CWeaponPreFireSound__ApplyToWeaponModeByName(void * this, char * weaponModeName)` | Replaces the owned pre-fire sound string at weapon-mode record `+0x28`. |
| `0x004373a0` | `void __thiscall CWeaponPostFireSound__ApplyToWeaponModeByName(void * this, char * weaponModeName)` | Replaces the owned post-fire sound string at weapon-mode record `+0x2c`. |
| `0x00437490` | `void * __cdecl CPhysicsScriptStatements__CreateStatementType5(int valueType)` | Type-5/round value factory over observed ids `0x1` through `0x26`. |

## Evidence

- Initial read-only exports verified `7/7` metadata rows, `7/7` decompile exports, `44` xref rows, `8575` instruction rows, and `7/7` tag rows.
- `tools/ApplyRoundSoundValueTranche.java` dry run accepted all seven targets with `updated=7`, `skipped=0`, `renamed=0`, `missing=0`, and `bad=0`.
- `tools/ApplyRoundSoundValueTranche.java` apply saved the tranche with `updated=7`, `skipped=0`, `renamed=6`, `missing=0`, and `bad=0`, with `REPORT: Save succeeded`.
- Final read-back verified `7/7` metadata rows, `7/7` decompile exports, `44` xref rows, `8575` instruction rows, and `7/7` tag rows.
- `py -3 tools\ghidra_round_sound_value_tranche_probe_test.py` passed `3/3`; `py -3 -m py_compile tools\ghidra_round_sound_value_tranche_probe.py tools\ghidra_round_sound_value_tranche_probe_test.py` passed.
- `cmd.exe /c npm run test:ghidra-round-sound-value-tranche` passed against the saved read-back artifacts.
- The refreshed whole-database queue reports `5904` functions, `943` commented functions, `4961` commentless functions, `1979` undefined signatures, and `2173` `param_N` signatures.
- The post-mutation live Ghidra backup was verified at `[maintainer-local-ghidra-backup-root]\BEA_20260512_105859_post_wave337_verified` with `19` files, `152210311` bytes, and `DiffCount=0`.

## Claim Boundary

This is saved static Ghidra name/signature/comment/tag evidence only. It does not prove exact source identities, concrete round or weapon-mode record layouts, local variable recovery, structure typing, runtime physics-script behavior, BEA launch, game patching, asset or save mutation, or rebuild parity.

Raw machine-readable proof remains under ignored `subagents/ghidra-static-reaudit/round-sound-values-wave337/current/`.
