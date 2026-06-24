# Wave1143 PhysicsScript Statement Destructor Current-Risk Readiness Note

Status: complete static read-only evidence
Date: 2026-06-05
Scope: `wave1143-physics-statement-dtor-current-risk-review`

Wave1143 re-read nine PhysicsScript statement destructor current-risk rows with fresh Ghidra exports and made no mutation: no rename, signature change, comment/tag change, function-boundary change, executable-byte change, BEA launch, installed-game mutation, save mutation, or runtime-file mutation.

Probe token anchor: Wave1143; wave1143-physics-statement-dtor-current-risk-review; 270/1179 = 22.90%; 9 current-risk rows; current focused candidates: 1178; live regenerated current focused candidates: 1178; remaining active focused work: 909; current risk candidates: 6166; PhysicsScript statement destructor current-risk review; fresh Ghidra export; statement destructor bodies; scalar-deleting wrapper xrefs; read-only review; no mutation; 0 / 0 / 0; 6411/6411 = 100.00%; CUnitStatement__dtor; CWeaponStatement__dtor; CWeaponModeStatement__dtor; CRoundStatement__dtor; CSpawnerStatement__dtor; CExplosionStatement__dtor; CComponentStatement__dtor; CFeatureStatement__dtor; CHazardStatement__dtor; G:\GhidraBackups\BEA_20260605-161338_post_wave1143_physics_statement_dtor_current_risk_review_verified; G:\GhidraBackups\BEA_20260605-153716_post_wave1142_mixed_score22_current_risk_review_verified; wave1108-current-risk-rank; current-risk denominator; focused threshold `15`; not Wave911 reconstruction.

Fresh evidence:

- `pre-metadata.tsv`: `9` rows, `targets=9 found=9 missing=0`.
- `pre-tags.tsv`: `9` rows, `missing=0`.
- `pre-xrefs.tsv`: `9` rows.
- `pre-instructions.tsv`: `207` instruction rows, `targets=9 missing=0`.
- `pre-decompile/index.tsv`: `9` rows, `targets=9 dumped=9 missing=0 failed=0`.
- Verified backup: `G:\GhidraBackups\BEA_20260605-161338_post_wave1143_physics_statement_dtor_current_risk_review_verified`, `19` files, `175967111` bytes, `DiffCount=0`, `HashDiffCount=0`.
- Previous completed backup: `G:\GhidraBackups\BEA_20260605-153716_post_wave1142_mixed_score22_current_risk_review_verified`.

Reviewed rows:

| Address | Static read-back |
| --- | --- |
| `0x0042f510 CUnitStatement__dtor` | Child pointer `this+0x10c` conditional slot-0 delete, then base vtable restore. |
| `0x0042f9e0 CWeaponStatement__dtor` | Same statement destructor pattern. |
| `0x0042ff00 CWeaponModeStatement__dtor` | Same statement destructor pattern. |
| `0x00430470 CRoundStatement__dtor` | Same statement destructor pattern. |
| `0x00430940 CSpawnerStatement__dtor` | Same statement destructor pattern. |
| `0x00430dc0 CExplosionStatement__dtor` | Same statement destructor pattern. |
| `0x004312b0 CComponentStatement__dtor` | Same statement destructor pattern. |
| `0x00431700 CFeatureStatement__dtor` | Same statement destructor pattern. |
| `0x00431b50 CHazardStatement__dtor` | Same statement destructor pattern. |

Accounting after Wave1143:

- Static closure: `6411/6411 = 100.00%`.
- Static debt: `0 / 0 / 0`.
- Expanded post-100 static surface: `1560/1560 = 100.00%`.
- Wave911 focused: `812/1408 = 57.67%`.
- Wave911 top-500: `500/500 = 100.00%`.
- Wave1108 current focused accounting: `270/1179 = 22.90%`.
- Current risk candidates: 6166.
- Current focused candidates: 1178.
- Live regenerated current focused candidates: 1178.
- Remaining active focused work: 909.

This is static Ghidra evidence only. Runtime PhysicsScript behavior, runtime statement destruction behavior, serialized file-format completeness, mission-script outcomes, exact layouts, BEA patching behavior, gameplay outcomes, visual QA, and rebuild parity remain separate proof.
