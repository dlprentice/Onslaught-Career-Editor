# Ghidra Weapon Mode Value Tranche - 2026-05-12

Status: GREEN static Ghidra correction evidence.

## Scope

Wave 336 continued the `CPhysicsScriptStatements.cpp` static re-audit immediately after the component-copy helper pass. Fresh metadata, decompile, xref, instruction, and tag read-back selected nine existing weapon-mode/value-family functions with stale vfunc-style names, undefined factory return type, or extra `param_N` stack-argument debt.

This pass saved names, signatures, comments, and tags for nine existing functions:

| Address | Saved state | Evidence summary |
| --- | --- | --- |
| `0x00435010` | `void * __cdecl CPhysicsScriptStatements__CreateStatementType4(int valueType)` | Type-4 weapon-mode value factory over observed ids `0x1` through `0x26`. |
| `0x00435840` | `void __thiscall CWeaponBasedOn__ApplyToWeaponByName(void * this, char * weaponName)` | Looks up the target weapon in `DAT_008553e8`, then copies selected fields from the base/source weapon named by `this+0x8`. |
| `0x004359c0` | Superseded by Wave 337: `void __fastcall CPhysicsWeaponModeValue__dtor_base(void * this)` | Wave 336 initially described this as a constructor-base body. Wave 337 adjacent scalar-deleting destructor read-back at `0x00437080` corrected it to the base destructor body. |
| `0x00435b20` | `void __thiscall CPhysicsWeaponModeValue__LoadTwoScalarsFromMemBuffer(void * this, void * memBuffer)` | Shared load helper for two 4-byte scalar fields at `this+0x8` and `this+0xc`. |
| `0x00435c90` | `void __thiscall CWeaponLaunchAngle__LoadFromMemBuffer(void * this, void * memBuffer)` | Launch-angle load helper for three 4-byte fields at `this+0x8`, `this+0xc`, and `this+0x10`. |
| `0x00436130` | `void __thiscall CWeaponVolleySize__ApplyToWeaponModeByName(void * this, char * weaponModeName)` | Searches `DAT_008553ec` by weapon-mode name at record `+0x30`, rounds the scalar at `this+0x8`, and writes record `+0x48`. |
| `0x00436320` | `void __thiscall CWeaponPreFireEffect__ApplyToWeaponModeByName(void * this, char * weaponModeName)` | Replaces the pre-fire effect owned string at weapon-mode record `+0x20`. |
| `0x00436410` | `void __thiscall CWeaponMuzzleEffect__ApplyToWeaponModeByName(void * this, char * weaponModeName)` | Replaces the muzzle effect owned string at weapon-mode record `+0x1c`. |
| `0x00436500` | `void __thiscall CWeaponClip__ApplyToWeaponModeByName(void * this, char * weaponModeName)` | Replaces the clip string reference after matching the weapon-mode record name. |

No new function boundary was created in this wave.

## Evidence

- `ApplyWeaponModeValueTranche.java` dry run accepted all nine targets with `missing=0` and `bad=0`.
- `ApplyWeaponModeValueTranche.java` apply saved the tranche with `updated=9`, `renamed=8`, `missing=0`, and `bad=0`, with `REPORT: Save succeeded`; a comment-only reapply finished with `renamed=0`, `missing=0`, and `bad=0`.
- Final read-back verified `9/9` metadata rows, `9/9` decompile exports, `12` xref rows, `3789` instruction rows, and `9/9` tag rows.
- `cmd.exe /c npm run test:ghidra-weapon-mode-value-tranche` passed against the saved read-back artifacts.
- The refreshed whole-database queue reports `5904` functions, `937` commented functions, `4967` commentless functions, `1980` undefined signatures, and `2178` `param_N` signatures.
- The post-mutation live Ghidra backup was verified at `[maintainer-local-ghidra-backup-root]\BEA_20260512_100148_post_wave336_verified` with `19` files, `152210311` bytes, and `DiffCount=0`.
- Follow-up Wave 337 superseded the `0x004359c0` constructor-base wording after the adjacent `0x00437080` scalar-deleting destructor wrapper was re-read and saved.

## Claim Boundary

This is saved static Ghidra name/signature/comment/tag evidence only. It does not prove exact source identities, concrete weapon or weapon-mode record layouts, local variable recovery, structure typing, runtime physics-script behavior, BEA launch, game patching, asset or save mutation, or rebuild parity.

Raw machine-readable proof remains under ignored `subagents/ghidra-static-reaudit/weapon-mode-values-wave336/current/`.
