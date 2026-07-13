# Ghidra Wave900+ Through Wave1097 Recheck Note

<!-- ghidra-full-reaudit-20260713:start -->
> **2026-07-13 semantic revalidation:** Historical record; `0x004df520` → `CActor__dtor_base_Thunk` (was `CActor__dtor_base`). The original text below remains provenance rather than current semantic authority. Use the [closeout](../../reverse-engineering/binary-analysis/ghidra-full-reaudit-closeout-2026-07-13.md); exact records are in `reverse-engineering/binary-analysis/ghidra-full-reaudit-corrections-2026-07-13.json` and `reverse-engineering/binary-analysis/ghidra-targeted-revalidation-corrections-2026-07-13.json`.
<!-- ghidra-full-reaudit-20260713:end -->

Status: aggregate validation passed
Date: 2026-06-04
Scope: `wave900-plus-through-wave1097-recheck`

This note extends the post-Wave900 recheck chain through Wave1097. The intended local validation gate is:

```powershell
npm run test:ghidra-wave900-plus-through-wave1097-recheck
```

Wave1097 (`cunit-dtor-thunk-lifecycle-review-wave1097`) re-read twelve saved CUnit/CActor/CComplexThing destructor, scalar-deleting destructor, lifecycle cleanup, owner-link, child-unit, deployment-reset, and destruction helper rows with no Ghidra mutation. The focused readiness note is [`ghidra_cunit_dtor_thunk_lifecycle_review_wave1097_2026-06-04.md`](ghidra_cunit_dtor_thunk_lifecycle_review_wave1097_2026-06-04.md).

Coverage anchors:

- Static function-quality closure remains `6410/6410 = 100.00%`.
- Wave911 focused re-audit progress remains `812/1408 = 57.67%`.
- Expanded static surface progress remains `1560/1560 = 100.00%`.
- Wave911 top-500 risk-ranked coverage remains `500/500 = 100.00%`.
- Representative rows include `0x004bfe00 CUnit__dtor_base_Thunk_004bfe00`, `0x004f84c0 CUnit__VFunc01_ScalarDeletingDtor`, `0x004f84e0 CUnit__dtor_base`, `0x0050ee90 CUnit__scalar_deleting_dtor`, `0x004f95d0 CUnit__VFunc02_CleanupWorldLinksAndForward`, `0x004fcfa0 CUnit__ClearSpawnerSet`, `0x004fcfe0 CUnit__ReleaseChildUnits`, `0x004fd040 CUnit__ResetDeploymentGraphAndScheduleEvent`, `0x004fd140 CUnit__MarkDestroyedAndCleanupLinks`, `0x004cb0b0 ParticleEffectLink__SetHandleStateAndClear`, `0x004013d0 CActor__dtor_base`, and `0x004f3f00 CComplexThing__dtor_base`.
- Fresh read-only exports verified `12` metadata rows, `12` tag rows, `190` xref rows, `656` instruction rows, and `12` decompile rows.
- Caller/context evidence ties the row group to the saved CUnit destructor-base and scalar-deleting wrappers, CUnit slot-2 cleanup, active-reader/set cleanup, child-unit release, deployment reset/event scheduling, destruction marking, particle/effect owner-link clearing, and Actor/ComplexThing destructor tails.
- Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260604-182217_post_wave1097_cunit_dtor_thunk_lifecycle_review_verified`, `19` files, `175541127` bytes, `DiffCount=0`.

Boundary: this is static Ghidra/documentation/probe coverage evidence only. Runtime destruction, cleanup order, event scheduling, child-unit release, particle/effect behavior, exact CUnit/CActor/CComplexThing/reader/set/owner-link/controller/script layouts, exact source-body identity, BEA patching behavior, gameplay outcomes, and rebuild parity remain separate proof.

Validation result:

- `npm run test:ghidra-wave900-plus-through-wave1097-recheck`: PASS.
- Focused Wave1097 probe: PASS.
- Readiness notes: `200`.
- Covered waves: `198`.
- Package probe scripts: `196`.
- Evidence bases: `196`.
- Backup references: `198`.
- Apply scripts: `72`.
- Wave982-Wave1097 direct probes: `resultCount=116`, `passCount=1`, `failCount=115`, `disallowedFailureCount=0`.
- Current queue: `6410` total, `0` commentless, `0` exact-undefined signatures, `0` `param_N`, status `PASS`.

Probe token anchor: Wave1097; cunit-dtor-thunk-lifecycle-review-wave1097; 0x004bfe00 CUnit__dtor_base_Thunk_004bfe00; 0x004f84c0 CUnit__VFunc01_ScalarDeletingDtor; 0x004f84e0 CUnit__dtor_base; 0x0050ee90 CUnit__scalar_deleting_dtor; 0x004f95d0 CUnit__VFunc02_CleanupWorldLinksAndForward; 0x004fcfa0 CUnit__ClearSpawnerSet; 0x004fcfe0 CUnit__ReleaseChildUnits; 0x004fd040 CUnit__ResetDeploymentGraphAndScheduleEvent; 0x004fd140 CUnit__MarkDestroyedAndCleanupLinks; 0x004cb0b0 ParticleEffectLink__SetHandleStateAndClear; 0x004013d0 CActor__dtor_base; 0x004f3f00 CComplexThing__dtor_base; 1560/1560 = 100.00%; 812/1408 = 57.67%; 500/500 = 100.00%; 6410/6410 = 100.00%; [maintainer-local-ghidra-backup-root]\BEA_20260604-182217_post_wave1097_cunit_dtor_thunk_lifecycle_review_verified; read-only review.
