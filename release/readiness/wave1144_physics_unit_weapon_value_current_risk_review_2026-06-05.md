# Wave1144 PhysicsScript Unit/Weapon Value Current-Risk Readiness Note

Status: complete static read-only evidence
Date: 2026-06-05
Scope: `wave1144-physics-unit-weapon-value-current-risk-review`

Wave1144 re-read fifteen PhysicsScript unit/weapon value and factory current-risk rows with fresh Ghidra exports and made no mutation: no rename, signature change, comment/tag change, function-boundary change, executable-byte change, BEA launch, installed-game mutation, save mutation, or runtime-file mutation.

Probe token anchor: Wave1144; wave1144-physics-unit-weapon-value-current-risk-review; 285/1179 = 24.17%; 15 current-risk rows; current focused candidates: 1178; live regenerated current focused candidates: 1178; remaining active focused work: 894; current risk candidates: 6166; PhysicsScript unit/weapon value and factory current-risk review; fresh Ghidra export; unit/weapon value rows; factory type 7-10 rows; read-only review; no mutation; Codex read-only consult; 0 / 0 / 0; 6411/6411 = 100.00%; CUnitAlligence__scalar_deleting_dtor; CUnitAlligence__dtor; CUnitSoundMaterial__ApplyToUnitData; CUnitMaxLegsLifted__ApplyToUnitData; CUnitNavMap__scalar_deleting_dtor; CUnitNavMap__dtor; CUnitBehaviour__LoadFromMemBuffer; CUnitBehaviour__scalar_deleting_dtor; CUnitBehaviour__dtor; CWeaponIconName__ApplyToWeaponByName; CWeaponBasedOn__ApplyToWeaponByName; CPhysicsScriptStatements__CreateStatementType7; CPhysicsScriptStatements__CreateStatementType8; CPhysicsScriptStatements__CreateStatementType9; CPhysicsScriptStatements__CreateStatementType10; [maintainer-local-ghidra-backup-root]\BEA_20260605-165322_post_wave1144_physics_unit_weapon_value_current_risk_review_verified; [maintainer-local-ghidra-backup-root]\BEA_20260605-161338_post_wave1143_physics_statement_dtor_current_risk_review_verified; wave1108-current-risk-rank; current-risk denominator; focused threshold `15`; not Wave911 reconstruction.

Fresh evidence:

- `pre-metadata.tsv`: `15` rows, `targets=15 found=15 missing=0`.
- `pre-tags.tsv`: `15` rows, `missing=0`.
- `pre-xrefs.tsv`: `19` rows.
- `pre-instructions.tsv`: `1037` instruction rows, `targets=15 missing=0`.
- `pre-decompile/index.tsv`: `15` rows, `targets=15 dumped=15 missing=0 failed=0`.
- Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260605-165322_post_wave1144_physics_unit_weapon_value_current_risk_review_verified`, `19` files, `175967111` bytes, `DiffCount=0`, `HashDiffCount=0`.
- Previous completed backup: `[maintainer-local-ghidra-backup-root]\BEA_20260605-161338_post_wave1143_physics_statement_dtor_current_risk_review_verified`.
- Codex subagent usage: one read-only Codex consult recommended the same 15-row slice and read-only mutation posture; Codex root audited that recommendation against the fresh exports.

Reviewed rows:

| Address | Static read-back |
| --- | --- |
| `0x00432a50 CUnitAlligence__scalar_deleting_dtor` | Scalar-deleting wrapper for `CUnitAlligence__dtor`; `Alligence` spelling retained from current binary/source-adjacent evidence. |
| `0x00432a70 CUnitAlligence__dtor` | Deletes child value pointer at `+0x8`, then restores `CPhysicsUnitValue` base vtable. |
| `0x00432c00 CUnitSoundMaterial__ApplyToUnitData` | Rounds scalar `this+0x8` and writes unit data/init-like field `+0xe4`. |
| `0x00432c70 CUnitMaxLegsLifted__ApplyToUnitData` | Rounds scalar `this+0x8` and writes unit data/init-like field `+0x140`. |
| `0x00432fa0 CUnitNavMap__scalar_deleting_dtor` | Scalar-deleting wrapper for `CUnitNavMap__dtor`. |
| `0x00432fc0 CUnitNavMap__dtor` | Deletes child statement pointer at `+0x8`, then restores `CPhysicsUnitValue` base vtable. |
| `0x004330b0 CUnitBehaviour__LoadFromMemBuffer` | Reads child statement type from `CDXMemBuffer`, dispatches type-12 factory, and stores child statement at `+0x8`. |
| `0x004330e0 CUnitBehaviour__scalar_deleting_dtor` | Scalar-deleting wrapper for `CUnitBehaviour__dtor`. |
| `0x00433100 CUnitBehaviour__dtor` | Deletes child statement pointer at `+0x8`, then restores `CPhysicsUnitValue` base vtable. |
| `0x00434f20 CWeaponIconName__ApplyToWeaponByName` | Searches `DAT_008553e8` by weapon name and replaces the matching weapon icon string from `this+0x8`. |
| `0x00435840 CWeaponBasedOn__ApplyToWeaponByName` | Searches `DAT_008553e8` for target/base names and copies selected weapon-record fields. |
| `0x0043a860 CPhysicsScriptStatements__CreateStatementType7` | Explosion-value factory, observed ids `0x1..0xf`. |
| `0x0043b990 CPhysicsScriptStatements__CreateStatementType8` | Feature-value factory, observed ids `0x1..0x7`. |
| `0x0043c0b0 CPhysicsScriptStatements__CreateStatementType9` | Hazard-value factory, observed ids `0x1..0x4`. |
| `0x0043c500 CPhysicsScriptStatements__CreateStatementType10` | Component-value factory, observed ids `0x1..0x19` except `0x5`. |

Accounting after Wave1144:

- Static closure: `6411/6411 = 100.00%`.
- Static debt: `0 / 0 / 0`.
- Expanded post-100 static surface: `1560/1560 = 100.00%`.
- Wave911 focused: `812/1408 = 57.67%`.
- Wave911 top-500: `500/500 = 100.00%`.
- Wave1108 current focused accounting: `285/1179 = 24.17%`.
- Current risk candidates: 6166.
- Current focused candidates: 1178.
- Live regenerated current focused candidates: 1178.
- Remaining active focused work: 894.

This is static Ghidra evidence only. Runtime PhysicsScript behavior, runtime unit/weapon value behavior, runtime factory behavior, serialized file-format completeness, mission-script outcomes, exact layouts, exact source-body identity, BEA patching behavior, gameplay outcomes, visual QA, and rebuild parity remain separate proof.
