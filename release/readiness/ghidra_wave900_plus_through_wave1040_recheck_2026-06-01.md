# Ghidra Wave900+ Through Wave1040 Recheck

Status: ready for local validation
Date: 2026-06-01
Scope: Wave900 through Wave1040 static re-audit evidence

This note extends the Wave900+ structural recheck through Wave1040. It keeps the earlier Wave900-Wave1039 records historical and adds the Wave1040 focused probe/readiness/evidence/backup extension.

Current extension:

- Focused package script: `test:ghidra-physics-statement-create-size-review-wave1040`
- Aggregate package script: `test:ghidra-wave900-plus-through-wave1040-recheck`
- Focused readiness note: `release/readiness/ghidra_physics_statement_create_size_review_wave1040_2026-06-01.md`
- Focused probe: `tools/ghidra_physics_statement_create_size_review_wave1040_probe.py`
- Apply script: `tools/ApplyPhysicsStatementCreateSizeReviewWave1040.java`
- Evidence base: `subagents/ghidra-static-reaudit/wave1040-physics-statement-create-size-review`
- Verified backup: `G:\GhidraBackups\BEA_20260601-082926_post_wave1040_physics_statement_create_size_review_verified`

Wave1040 summary:

Wave1040 (`physics-statement-create-size-review-wave1040`) re-read sixteen Unit/Weapon/WeaponMode/Round PhysicsScript statement create/serialized-size/value-list lifecycle rows and saved a comment/tag correction. Representative anchors are `0x0042ede0 CUnitStatement__CreateUnitAndRecurse`, `0x0042f4b0 CPhysicsUnitValueList__scalar_deleting_dtor`, `0x0042f980 CPhysicsWeaponValueList__scalar_deleting_dtor`, `0x0042fea0 CPhysicsWeaponModeValueList__scalar_deleting_dtor`, and `0x00430410 CPhysicsRoundValueList__scalar_deleting_dtor`. The correction replaces stale destructor `OID__FreeObject` wording with observed `CDXMemoryManager__Free(&DAT_009c3df0, this)` evidence via call `0x00549220`. Fresh post exports verified `16` metadata rows, `16` tag rows, `20` xref rows, `442` body-instruction rows, and `16` decompile rows. Queue closure remains `6238/6238 = 100.00%`; Wave911 focused progress is `727/1408 = 51.63%`; expanded static surface progress is `956/1493 = 64.03%`; top-500 coverage remains `500/500 = 100.00%`.

Expected validation:

- `npm run test:ghidra-physics-statement-create-size-review-wave1040`
- `npm run test:ghidra-wave900-plus-through-wave1040-recheck`
- `npm run test:ghidra-static-reaudit-queue`

Boundary note:

This is structural static evidence validation. It checks focused probe coverage, readiness/evidence/backup structure, apply-log coverage, and live static queue closure. It does not prove runtime PhysicsScript behavior, runtime lifetime behavior, mission-script outcomes, exact source-body identity, concrete layouts, BEA patching, gameplay outcomes, or rebuild parity.

Probe token anchor: Wave1040; physics-statement-create-size-review-wave1040; 0x0042ede0 CUnitStatement__CreateUnitAndRecurse; 0x0042f4b0 CPhysicsUnitValueList__scalar_deleting_dtor; 0x0042f980 CPhysicsWeaponValueList__scalar_deleting_dtor; 0x0042fea0 CPhysicsWeaponModeValueList__scalar_deleting_dtor; 0x00430410 CPhysicsRoundValueList__scalar_deleting_dtor; CDXMemoryManager__Free; 0x00549220; DAT_009c3df0; 727/1408 = 51.63%; 956/1493 = 64.03%; 500/500 = 100.00%; 6238/6238 = 100.00%; G:\GhidraBackups\BEA_20260601-082926_post_wave1040_physics_statement_create_size_review_verified; comment/tag correction.
