# Wave1144 PhysicsScript Unit/Weapon Value Current-Risk Review

Status: complete static read-only evidence
Date: 2026-06-05
Scope: `wave1144-physics-unit-weapon-value-current-risk-review`

Wave1144 re-read fifteen current-risk PhysicsScript unit/weapon value and factory rows from the Wave1108 current focused denominator. The review used fresh Ghidra metadata, tag, xref, instruction, and decompile exports. No Ghidra mutation was warranted.

## Coverage

| Address | Evidence |
| --- | --- |
| `0x00432a50 CUnitAlligence__scalar_deleting_dtor` | DATA vtable xref `0x005d9d28`; wrapper calls `CUnitAlligence__dtor`, checks scalar-delete flag, optionally frees through `OID__FreeObject`, and returns `this`. The `Alligence` spelling is retained from current binary/source-adjacent evidence. |
| `0x00432a70 CUnitAlligence__dtor` | Reached from `0x00432a53`; deletes the child value pointer at `+0x8` through slot 0 when present, then restores the `CPhysicsUnitValue` base vtable. |
| `0x00432c00 CUnitSoundMaterial__ApplyToUnitData` | DATA vtable xref `0x005d9cdc`; rounds scalar `this+0x8` and writes the unit data/init-like field at `+0xe4`. |
| `0x00432c70 CUnitMaxLegsLifted__ApplyToUnitData` | DATA vtable xref `0x005d9c14`; rounds scalar `this+0x8` and writes the unit data/init-like field at `+0x140`. |
| `0x00432fa0 CUnitNavMap__scalar_deleting_dtor` | DATA vtable xref `0x005d9b98`; wrapper calls `CUnitNavMap__dtor`, checks scalar-delete flag, optionally frees through `OID__FreeObject`, and returns `this`. |
| `0x00432fc0 CUnitNavMap__dtor` | Reached from `0x00432fa3`; deletes the child statement pointer at `+0x8` through slot 0 when present, then restores the `CPhysicsUnitValue` base vtable. |
| `0x004330b0 CUnitBehaviour__LoadFromMemBuffer` | DATA vtable xref `0x005d9d5c`; reads a child statement type from `CDXMemBuffer`, dispatches `CPhysicsScriptStatements__CreateStatementType12`, and stores the loaded child statement at `+0x8`. |
| `0x004330e0 CUnitBehaviour__scalar_deleting_dtor` | DATA vtable xref `0x005d9d50`; wrapper calls `CUnitBehaviour__dtor`, checks scalar-delete flag, optionally frees through `OID__FreeObject`, and returns `this`. |
| `0x00433100 CUnitBehaviour__dtor` | Reached from `0x004330e3`; deletes the child statement pointer at `+0x8` through slot 0 when present, then restores the `CPhysicsUnitValue` base vtable. |
| `0x00434f20 CWeaponIconName__ApplyToWeaponByName` | DATA vtable xref `0x005d9f20`; searches global weapon list `DAT_008553e8` by weapon name and replaces the matching record icon string with the string at `this+0x8`. |
| `0x00435840 CWeaponBasedOn__ApplyToWeaponByName` | DATA vtable xref `0x005da010`; searches `DAT_008553e8` for the target weapon and the base/source name at `this+0x8`, then copies selected weapon-record fields. |
| `0x0043a860 CPhysicsScriptStatements__CreateStatementType7` | Called by `CExplosionStatement__LoadFromMemBuffer` and `CPhysicsExplosionValueList__LoadFromMemBuffer`; type-7 explosion-value factory over observed ids `0x1..0xf`, vtables `0x005da6c4` through `0x005da7dc`. |
| `0x0043b990 CPhysicsScriptStatements__CreateStatementType8` | Called by `CFeatureStatement__LoadFromMemBuffer` and `CPhysicsFeatureValueList__LoadFromMemBuffer`; type-8 feature-value factory over observed ids `0x1..0x7`, vtables `0x005da804` through `0x005da87c`. |
| `0x0043c0b0 CPhysicsScriptStatements__CreateStatementType9` | Called by `CHazardStatement__LoadFromMemBuffer` and `CPhysicsHazardValueList__LoadFromMemBuffer`; type-9 hazard-value factory over observed ids `0x1..0x4`, vtables `0x005da8a4` through `0x005da8e0`. |
| `0x0043c500 CPhysicsScriptStatements__CreateStatementType10` | Called by `CComponentStatement__LoadFromMemBuffer` and `CPhysicsComponentValueList__LoadFromMemBuffer`; type-10 component-value factory over observed ids `0x1..0x19` except `0x5`, vtables `0x005da908` through `0x005daad4`. |

## Evidence Counts

- Primary exports: `15` metadata rows, `15` tag rows, `19` xref rows, `1037` instruction rows, and `15` decompile rows.
- Backup: `[maintainer-local-ghidra-backup-root]\BEA_20260605-165322_post_wave1144_physics_unit_weapon_value_current_risk_review_verified`; `19` files, `175967111` bytes, `DiffCount=0`, `HashDiffCount=0`.
- Previous completed backup: `[maintainer-local-ghidra-backup-root]\BEA_20260605-161338_post_wave1143_physics_statement_dtor_current_risk_review_verified`.
- Codex subagent usage: one read-only Codex consult recommended the same 15-row slice and read-only mutation posture; Codex root audited that recommendation against the fresh exports.

## Progress

- Static Ghidra function-quality closure: `6411/6411 = 100.00%`.
- Static debt: `0 / 0 / 0` commentless / exact-undefined / `param_N`.
- Expanded post-100 static surface: `1560/1560 = 100.00%`.
- Wave911 focused historical residual: `812/1408 = 57.67%`.
- Wave911 top-500: `500/500 = 100.00%`.
- Wave1108 current focused accounting: `285/1179 = 24.17%`.
- Current risk candidates: 6166.
- Current focused candidates: 1178.
- Live regenerated current focused candidates: 1178.
- Remaining active focused work: 894.

## Boundary

Wave1144 is static Ghidra evidence only. It does not prove runtime PhysicsScript behavior, runtime unit/weapon value behavior, runtime factory behavior, serialized file-format completeness, mission-script outcomes, exact layouts, exact source-body identity, BEA patching behavior, gameplay outcomes, visual QA, or rebuild parity.

Probe token anchor: Wave1144; wave1144-physics-unit-weapon-value-current-risk-review; 285/1179 = 24.17%; 15 current-risk rows; current focused candidates: 1178; live regenerated current focused candidates: 1178; remaining active focused work: 894; current risk candidates: 6166; PhysicsScript unit/weapon value and factory current-risk review; fresh Ghidra export; unit/weapon value rows; factory type 7-10 rows; read-only review; no mutation; Codex read-only consult; 0 / 0 / 0; 6411/6411 = 100.00%; CUnitAlligence__scalar_deleting_dtor; CUnitAlligence__dtor; CUnitSoundMaterial__ApplyToUnitData; CUnitMaxLegsLifted__ApplyToUnitData; CUnitNavMap__scalar_deleting_dtor; CUnitNavMap__dtor; CUnitBehaviour__LoadFromMemBuffer; CUnitBehaviour__scalar_deleting_dtor; CUnitBehaviour__dtor; CWeaponIconName__ApplyToWeaponByName; CWeaponBasedOn__ApplyToWeaponByName; CPhysicsScriptStatements__CreateStatementType7; CPhysicsScriptStatements__CreateStatementType8; CPhysicsScriptStatements__CreateStatementType9; CPhysicsScriptStatements__CreateStatementType10; [maintainer-local-ghidra-backup-root]\BEA_20260605-165322_post_wave1144_physics_unit_weapon_value_current_risk_review_verified; [maintainer-local-ghidra-backup-root]\BEA_20260605-161338_post_wave1143_physics_statement_dtor_current_risk_review_verified; wave1108-current-risk-rank; current-risk denominator; focused threshold `15`; not Wave911 reconstruction.
