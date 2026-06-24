# Ghidra Physics Statement Create/Size Review Wave1040 Readiness Note

Status: complete static read-back evidence with comment/tag correction
Date: 2026-06-01
Scope: `physics-statement-create-size-review-wave1040`

Wave1040 re-read sixteen Unit/Weapon/WeaponMode/Round PhysicsScript statement create/serialized-size/value-list lifecycle rows originally hardened by Waves331-332 and saved a bounded Ghidra comment/tag correction. The pass preserved all names and signatures, made no function-boundary changes, made no executable-byte changes, did not launch BEA, and did not mutate game files.

Representative anchors:

| Address | Evidence |
| --- | --- |
| `0x0042ede0 CUnitStatement__CreateUnitAndRecurse` | DATA vtable ref `0x005d987c`; creates/registers UnitAI by statement name and propagates the created context through child statement traversal. |
| `0x0042f230 CUnitStatement__GetSerializedSize` | DATA vtable ref `0x005d9880`; counts the statement name string, first value-list node payload size, and chained value-list sizes. |
| `0x0042f4b0 CPhysicsUnitValueList__scalar_deleting_dtor` | DATA vtable ref `0x005d988c`; stale OID-free wording corrected to `CDXMemoryManager__Free(&DAT_009c3df0, this)` via call `0x00549220`. |
| `0x0042f980 CPhysicsWeaponValueList__scalar_deleting_dtor` | DATA vtable ref `0x005d98a8`; same scalar-delete memory-manager free correction. |
| `0x0042fea0 CPhysicsWeaponModeValueList__scalar_deleting_dtor` | DATA vtable ref `0x005d98b0`; same scalar-delete memory-manager free correction. |
| `0x00430410 CPhysicsRoundValueList__scalar_deleting_dtor` | DATA vtable ref `0x005d98b8`; same scalar-delete memory-manager free correction. |

Correction:

- The four value-list scalar-deleting destructor comments previously implied `OID__FreeObject` ownership.
- Fresh instruction/decompile evidence shows each wrapper restores its value-list vtable, dispatches child/next-node destructors through vtable slot 0 when present, tests the scalar-delete flag, loads `ECX` with `0x009c3df0`, and calls `0x00549220 CDXMemoryManager__Free`.
- Context metadata for `0x00549220 CDXMemoryManager__Free` explicitly distinguishes memory-manager free behavior from OID object freeing.
- Wave1040 replaces the stale destructor wording and adds `physics-statement-create-size-review-wave1040` plus `wave1040-readback-verified` tags across the reviewed rows.

Read-back evidence:

- `ApplyPhysicsStatementCreateSizeReviewWave1040.java dry`: `updated=0 skipped=16 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=4 tags_added=52 missing=0 bad=0`
- `ApplyPhysicsStatementCreateSizeReviewWave1040.java apply`: `updated=16 skipped=0 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=4 tags_added=52 missing=0 bad=0`
- `ApplyPhysicsStatementCreateSizeReviewWave1040.java final dry`: `updated=0 skipped=16 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=0 tags_added=0 missing=0 bad=0`
- Post exports verified `16` metadata rows, `16` tag rows, `20` xref rows, `442` body-instruction rows, and `16` decompile rows.
- Context exports verified `1` metadata row and `1` decompile row for `0x00549220 CDXMemoryManager__Free`.
- Queue closure remains `6238/6238 = 100.00%`.
- Wave911 focused progress advances to `727/1408 = 51.63%`.
- Expanded static surface progress advances to `956/1493 = 64.03%`.
- Wave911 top-500 risk-ranked coverage remains `500/500 = 100.00%`.
- Verified backup: `G:\GhidraBackups\BEA_20260601-082926_post_wave1040_physics_statement_create_size_review_verified`, `19` files, `174001031` bytes, `DiffCount=0`, `HashDiffCount=0`.

What this proves:

- The sixteen reviewed statement/value-list rows exist in the saved Ghidra project with the expected names and signatures.
- The saved comments and tags include Wave1040 read-back evidence.
- The four value-list scalar-deleting destructors now document the observed `CDXMemoryManager__Free(&DAT_009c3df0, this)` path instead of stale `OID__FreeObject` wording.
- The create and size helpers remain statically tied to statement/value-list traversal and serialized-size evidence.

What remains separate proof:

- Runtime PhysicsScript behavior.
- Runtime lifetime behavior.
- Mission-script outcomes.
- Concrete statement/value-list record layouts beyond observed offsets.
- Exact source-body identity.
- BEA patching, gameplay outcomes, and rebuild parity.

Probe token anchor: Wave1040; physics-statement-create-size-review-wave1040; 0x0042ede0 CUnitStatement__CreateUnitAndRecurse; 0x0042f4b0 CPhysicsUnitValueList__scalar_deleting_dtor; 0x0042f980 CPhysicsWeaponValueList__scalar_deleting_dtor; 0x0042fea0 CPhysicsWeaponModeValueList__scalar_deleting_dtor; 0x00430410 CPhysicsRoundValueList__scalar_deleting_dtor; CDXMemoryManager__Free; 0x00549220; DAT_009c3df0; 727/1408 = 51.63%; 956/1493 = 64.03%; 500/500 = 100.00%; 6238/6238 = 100.00%; G:\GhidraBackups\BEA_20260601-082926_post_wave1040_physics_statement_create_size_review_verified; comment/tag correction.
