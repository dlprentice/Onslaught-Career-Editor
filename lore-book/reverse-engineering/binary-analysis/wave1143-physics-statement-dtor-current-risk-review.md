# Wave1143 PhysicsScript Statement Destructor Current-Risk Review

Status: complete static read-only evidence
Date: 2026-06-05
Scope: `wave1143-physics-statement-dtor-current-risk-review`

Wave1143 re-read nine current-risk PhysicsScript top-level statement destructor bodies from the Wave1108 current focused denominator. The review used fresh Ghidra metadata, tag, xref, instruction, and decompile exports. No Ghidra mutation was warranted.

## Coverage

| Address | Evidence |
| --- | --- |
| `0x0042f510 CUnitStatement__dtor` | Reached from `0x0042f4f3 CUnitStatement__scalar_deleting_dtor`; sets vtable `0x005d9878`, conditionally calls child pointer `this+0x10c` through slot 0, then restores base vtable `0x005d9894`. |
| `0x0042f9e0 CWeaponStatement__dtor` | Reached from `0x0042f9c3 CWeaponStatement__scalar_deleting_dtor`; same child-delete/base-vtable-restore pattern, derived vtable `0x005d9850`. |
| `0x0042ff00 CWeaponModeStatement__dtor` | Reached from `0x0042fee3 CWeaponModeStatement__scalar_deleting_dtor`; same pattern, derived vtable `0x005d9864`. |
| `0x00430470 CRoundStatement__dtor` | Reached from `0x00430453 CRoundStatement__scalar_deleting_dtor`; same pattern, derived vtable `0x005d983c`. |
| `0x00430940 CSpawnerStatement__dtor` | Reached from `0x00430923 CSpawnerStatement__scalar_deleting_dtor`; same pattern, derived vtable `0x005d9828`. |
| `0x00430dc0 CExplosionStatement__dtor` | Reached from `0x00430da3 CExplosionStatement__scalar_deleting_dtor`; same pattern, derived vtable `0x005d9814`. |
| `0x004312b0 CComponentStatement__dtor` | Reached from `0x00431293 CComponentStatement__scalar_deleting_dtor`; same pattern, derived vtable `0x005d9800`. |
| `0x00431700 CFeatureStatement__dtor` | Reached from `0x004316e3 CFeatureStatement__scalar_deleting_dtor`; same pattern, derived vtable `0x005d97ec`. |
| `0x00431b50 CHazardStatement__dtor` | Reached from `0x00431b33 CHazardStatement__scalar_deleting_dtor`; same pattern, derived vtable `0x005d97d8`. |

## Evidence Counts

- Primary exports: `9` metadata rows, `9` tag rows, `9` xref rows, `207` instruction rows, and `9` decompile rows.
- Backup: `[maintainer-local-ghidra-backup-root]\BEA_20260605-161338_post_wave1143_physics_statement_dtor_current_risk_review_verified`; `19` files, `175967111` bytes, `DiffCount=0`, `HashDiffCount=0`.
- Previous completed backup: `[maintainer-local-ghidra-backup-root]\BEA_20260605-153716_post_wave1142_mixed_score22_current_risk_review_verified`.

## Progress

- Static Ghidra function-quality closure: `6411/6411 = 100.00%`.
- Static debt: `0 / 0 / 0` commentless / exact-undefined / `param_N`.
- Expanded post-100 static surface: `1560/1560 = 100.00%`.
- Wave911 focused historical residual: `812/1408 = 57.67%`.
- Wave911 top-500: `500/500 = 100.00%`.
- Wave1108 current focused accounting: `270/1179 = 22.90%`.
- Current risk candidates: 6166.
- Current focused candidates: 1178.
- Live regenerated current focused candidates: 1178.
- Remaining active focused work: 909.

## Boundary

Wave1143 is static Ghidra evidence only. It does not prove runtime PhysicsScript behavior, runtime statement destruction behavior, serialized file-format completeness, mission-script outcomes, exact layouts, BEA patching behavior, gameplay outcomes, visual QA, or rebuild parity.

Probe token anchor: Wave1143; wave1143-physics-statement-dtor-current-risk-review; 270/1179 = 22.90%; 9 current-risk rows; current focused candidates: 1178; live regenerated current focused candidates: 1178; remaining active focused work: 909; current risk candidates: 6166; PhysicsScript statement destructor current-risk review; fresh Ghidra export; statement destructor bodies; scalar-deleting wrapper xrefs; read-only review; no mutation; 0 / 0 / 0; 6411/6411 = 100.00%; CUnitStatement__dtor; CWeaponStatement__dtor; CWeaponModeStatement__dtor; CRoundStatement__dtor; CSpawnerStatement__dtor; CExplosionStatement__dtor; CComponentStatement__dtor; CFeatureStatement__dtor; CHazardStatement__dtor; [maintainer-local-ghidra-backup-root]\BEA_20260605-161338_post_wave1143_physics_statement_dtor_current_risk_review_verified; [maintainer-local-ghidra-backup-root]\BEA_20260605-153716_post_wave1142_mixed_score22_current_risk_review_verified; wave1108-current-risk-rank; current-risk denominator; focused threshold `15`; not Wave911 reconstruction.
