# Ghidra Physics Statement Create/Recurse Review Wave1047

Status: complete static comment/tag correction
Date: 2026-06-01
Scope: `physics-statement-create-recurse-review-wave1047`

Wave1047 re-read nine top-level PhysicsScript statement create/recurse vtable rows from `0x0042ede0 CUnitStatement__CreateUnitAndRecurse` through `0x00431760 CHazardStatement__CreateHazardAndRecurse`. Fresh decompile, instruction, xref, metadata, and tag evidence showed the prior comments were too broad about the context passed into child statement recursion. The wave saved comment/tag corrections only: no rename, signature change, function-boundary change, executable-byte change, BEA launch, or runtime/game-file mutation occurred.

Reviewed rows:

| Address | Saved row | DATA xref | Corrected static evidence |
| --- | --- | --- | --- |
| `0x0042ede0` | `CUnitStatement__CreateUnitAndRecurse` | `0x005d987c` | Calls `CUnitAI__CreateAndRegisterByName`, resolves the matching UnitAI record from `DAT_008553fc` by name, then passes the resolved UnitAI context through child statement slot `+0x4` and `CStatementChain__InvokeVFunc04OnNodes`. |
| `0x0042f5b0` | `CWeaponStatement__CreateWeaponAndRecurse` | `0x005d9854` | Calls `CWeaponStatement__Create` with the statement name, then passes the statement name/string context through child statement slot `+0x4` and `CStatementChain__InvokeVFunc04OnNodes`. |
| `0x0042fa40` | `CWeaponModeStatement__CreateWeaponModeAndRecurse` | `0x005d9868` | Calls `CWeaponModeStatement__Create` with the statement name, then passes the statement name/string context through child recursion. |
| `0x0042ff60` | `CRoundStatement__CreateRoundAndRecurse` | `0x005d9840` | Calls `CRoundStatement__Create` with the statement name, then passes the statement name/string context through child recursion. |
| `0x004304d0` | `CSpawnerStatement__CreateSpawnerAndRecurse` | `0x005d982c` | Calls `CSpawnerData__CreateAndRegisterByName` with the statement name, then passes the statement name/string context through child recursion. |
| `0x004309a0` | `CExplosionStatement__CreateExplosionAndRecurse` | `0x005d9818` | Calls `CExplosionStatement__Create` with the statement name, then passes the statement name/string context through child recursion. |
| `0x00430e20` | `CComponentStatement__CreateComponentAndRecurse` | `0x005d9804` | Calls `CComponentStatement__CreateAndRegisterByName` with the statement name, then passes the statement name/string context through child recursion. |
| `0x00431310` | `CFeatureStatement__CreateFeatureAndRecurse` | `0x005d97f0` | Calls `CFeatureStatement__CreateAndRegisterByName` with the statement name, then passes the statement name/string context through child recursion. |
| `0x00431760` | `CHazardStatement__CreateHazardAndRecurse` | `0x005d97dc` | Calls `CHazardStatement__CreateAndRegisterByName` with the statement name, then passes the statement name/string context through child recursion. |

Read-back evidence:

- `ApplyPhysicsStatementCreateRecurseReviewWave1047.java dry`: `updated=0 skipped=9 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=9 tags_added=36 missing=0 bad=0`
- `ApplyPhysicsStatementCreateRecurseReviewWave1047.java apply`: `updated=9 skipped=0 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=9 tags_added=36 missing=0 bad=0`
- `ApplyPhysicsStatementCreateRecurseReviewWave1047.java final dry`: `updated=0 skipped=9 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=0 tags_added=0 missing=0 bad=0`
- Pre/post primary exports verified `9` metadata rows, `9` tag rows, `9` DATA xref rows, `250` function-body instruction rows, and `9` decompile rows.
- Context exports verified `18` metadata rows, `18` tag rows, `26` xref rows, `1708` function-body instruction rows, and `18` decompile rows for paired load/create/factory context.
- Queue closure remains `6246/6246 = 100.00%`, with `0` commentless rows, `0` exact-undefined signatures, and `0` `param_N` signatures.
- Wave1047 adds five newly direct-reviewed Wave911 focused rows beyond prior Wave1040 coverage, so Wave911 focused progress advances to `740/1408 = 52.56%`; expanded static surface progress advances to `998/1509 = 66.14%`; top-500 risk-ranked coverage remains `500/500 = 100.00%`.
- Verified backup: `G:\GhidraBackups\BEA_20260601-124915_post_wave1047_physics_statement_create_recurse_review_verified`, 19 files, 174590855 bytes, `DiffCount=0`, `HashDiffCount=0`.

What this proves:

- The nine reviewed statement create/recurse rows still exist as saved Ghidra function objects in the loaded database.
- The saved names and signatures remain unchanged and coherent with vtable DATA xrefs.
- The saved comments and tags now distinguish the UnitAI resolved-object recursion context from the non-unit statement name/string recursion context.
- The correction is static Ghidra evidence only, tied to metadata/tags/xrefs/instructions/decompile and serialized dry/apply/read-back logs.

What remains separate proof:

- Runtime PhysicsScript behavior and mission-script outcomes.
- Exact statement, value-list, registry, and UnitAI record layouts beyond observed offsets.
- Exact source-body identity.
- BEA patching behavior, gameplay outcomes, and rebuild parity.

Probe token anchor: Wave1047; physics-statement-create-recurse-review-wave1047; 0x0042ede0 CUnitStatement__CreateUnitAndRecurse; 0x0042f5b0 CWeaponStatement__CreateWeaponAndRecurse; 0x0042fa40 CWeaponModeStatement__CreateWeaponModeAndRecurse; 0x0042ff60 CRoundStatement__CreateRoundAndRecurse; 0x004304d0 CSpawnerStatement__CreateSpawnerAndRecurse; 0x004309a0 CExplosionStatement__CreateExplosionAndRecurse; 0x00430e20 CComponentStatement__CreateComponentAndRecurse; 0x00431310 CFeatureStatement__CreateFeatureAndRecurse; 0x00431760 CHazardStatement__CreateHazardAndRecurse; DAT_008553fc; CStatementChain__InvokeVFunc04OnNodes; 740/1408 = 52.56%; 998/1509 = 66.14%; 500/500 = 100.00%; 6246/6246 = 100.00%; G:\GhidraBackups\BEA_20260601-124915_post_wave1047_physics_statement_create_recurse_review_verified; comment/tag correction.
