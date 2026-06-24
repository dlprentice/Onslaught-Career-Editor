# Ghidra Physics Unit/Weapon Apply Lifetime Wave949 Readiness Note

Status: complete read-only static evidence
Date: 2026-05-28
Scope: `physics-unit-weapon-apply-lifetime-wave949`

Mutation status: no mutation.

Wave949 re-reviewed ten `CPhysicsScriptStatements.cpp` unit/weapon value apply and lifetime rows after Wave947's adjacent boundary recovery. The pass was read-only: no Ghidra mutation, no rename, no signature change, no comment change, no function-boundary change, no executable-byte change, and no BEA launch.

Primary targets:

| Address | Evidence |
| --- | --- |
| `0x00432c00 CUnitSoundMaterial__ApplyToUnitData` | Vtable DATA xref `0x005d9cdc`; rounds scalar `this+0x8` and writes unit/init-like field `+0xe4`. |
| `0x00432c70 CUnitMaxLegsLifted__ApplyToUnitData` | Vtable DATA xref `0x005d9c14`; rounds scalar `this+0x8` and writes unit/init-like field `+0x140`. |
| `0x00434f20 CWeaponIconName__ApplyToWeaponByName` | Vtable DATA xref `0x005d9f20`; walks `DAT_008553e8` by weapon name and replaces the matching icon string from `this+0x8`. |
| `0x00435840 CWeaponBasedOn__ApplyToWeaponByName` | Vtable DATA xref `0x005da010`; walks `DAT_008553e8`, finds a base/source weapon by `this+0x8`, and copies selected weapon-record fields. |
| `0x00432a50 CUnitAlligence__scalar_deleting_dtor` | Vtable DATA xref `0x005d9d28`; calls `CUnitAlligence__dtor`, then optionally frees `this` when the delete flag is set. |
| `0x00432a70 CUnitAlligence__dtor` | Called by `0x00432a50`; deletes child pointer `+0x8` through vtable slot 0, then restores the `CPhysicsUnitValue` base vtable. |
| `0x00432fa0 CUnitNavMap__scalar_deleting_dtor` | Vtable DATA xref `0x005d9b98`; calls `CUnitNavMap__dtor`, then optionally frees `this` when the delete flag is set. |
| `0x00432fc0 CUnitNavMap__dtor` | Called by `0x00432fa0`; deletes child statement pointer `+0x8` through vtable slot 0, then restores the `CPhysicsUnitValue` base vtable. |
| `0x004330e0 CUnitBehaviour__scalar_deleting_dtor` | Vtable DATA xref `0x005d9d50`; calls `CUnitBehaviour__dtor`, then optionally frees `this` when the delete flag is set. |
| `0x00433100 CUnitBehaviour__dtor` | Called by `0x004330e0`; deletes child statement pointer `+0x8` through vtable slot 0, then restores the `CPhysicsUnitValue` base vtable. |

Context anchors include Wave947 neighbors `0x00432a20 CUnitAlligence__LoadFromMemBuffer`, `0x00432ac0 CPhysicsUnitValue__base_vtable_scalar_deleting_dtor`, `0x00432bd0 CUnitImportance__ApplyToUnitData`, `0x00432f50 CUnitNavMap__ApplyToUnitData`, `0x00433010 CUnitBehaviour__ApplyToUnitData`, `0x00434930 CWeaponConsumption__ApplyToWeaponByName`, `0x00434de0 CWeaponVersusAir__ApplyToWeaponByName`, and `0x004347b0 CPhysicsWeaponValue__base_vtable_scalar_deleting_dtor`, plus loader/factory anchors `0x00432f70`, `0x004330b0`, `0x0043e630`, `0x00431bb0`, `0x0043ddc0`, `0x0043e310`, and `0x0043e400`.

Read-back evidence:

- Primary exports: 10 metadata rows, 10 tag rows, 10 xref rows, 367 instruction rows, and 10 decompile rows.
- Context exports: 15 metadata rows, 15 tag rows, 16 xref rows, 1532 instruction rows, and 15 decompile rows.
- Vtable export: 9 vtable anchors, 360 slot rows, with primary targets present at slots including `0x005d9cdc`, `0x005d9c14`, `0x005d9f20`, `0x005da010`, `0x005d9d28`, `0x005d9b98`, and `0x005d9d50`.
- Wave911 focused re-audit progress after Wave949 is `257/1408 = 18.25%`.
- Static export-contract function-quality closure remains `6150/6150 = 100.00%`.
- Verified read-only backup: `G:\GhidraBackups\BEA_20260528-075331_post_wave949_physics_unit_weapon_apply_lifetime_review_verified`, 19 files, 173542279 bytes, `DiffCount=0`.

What remains unproven:

- Exact source method identity.
- Concrete unit/weapon/value/statement layouts.
- Runtime physics-script behavior.
- Runtime weapon icon or weapon inheritance behavior.
- Runtime gameplay, HUD, or visual behavior.
- BEA patching behavior.
- Rebuild parity.
