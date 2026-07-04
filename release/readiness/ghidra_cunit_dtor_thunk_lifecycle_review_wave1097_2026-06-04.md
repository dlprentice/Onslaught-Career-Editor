# Ghidra CUnit Destructor Thunk Lifecycle Review Wave1097 Readiness Note

Status: complete static read-back evidence
Date: 2026-06-04
Scope: `cunit-dtor-thunk-lifecycle-review-wave1097`

Wave1097 re-read twelve saved CUnit/CActor/CComplexThing destructor, scalar-deleting destructor, lifecycle cleanup, owner-link, child-unit, deployment-reset, and destruction helper rows as a focused post-100 static system review. The pass was read-only: no Ghidra names, signatures, comments, tags, function boundaries, or executable bytes were changed; BEA was not launched; no installed-game/runtime file was mutated.

Representative anchors:

| Address | Evidence |
| --- | --- |
| `0x004bfe00 CUnit__dtor_base_Thunk_004bfe00` | One-instruction jump thunk to `0x004f84e0 CUnit__dtor_base`; reached by the scalar-deleting wrapper and unwind cleanup paths. |
| `0x004f84c0 CUnit__VFunc01_ScalarDeletingDtor` | Vfunc-slot wrapper calls `CUnit__dtor_base`, checks `flags & 1`, optionally frees through `CDXMemoryManager__Free`, returns `this`, and ends with `RET 0x4`. |
| `0x004f84e0 CUnit__dtor_base` | Destructor-base resets observed CUnit vtable pointers, clears particle/effect owner-link cells through `ParticleEffectLink__SetHandleStateAndClear`, clears/removes several set/list fields, then delegates to `CActor__dtor_base`. |
| `0x0050ee90 CUnit__scalar_deleting_dtor` | Scalar-deleting wrapper calls `CUnit__dtor_base_Thunk_004bfe00`, checks `flags & 1`, optionally frees through `CDXMemoryManager__Free`, returns `this`, and ends with `RET 0x4`. |
| `0x004f95d0 CUnit__VFunc02_CleanupWorldLinksAndForward` | Slot-2 cleanup path kills sounds, clears active readers and linked sets, releases particle/effect links, removes global unit-set links, frees the destructible-segment controller, releases controller `+0x208`, updates observed counters, and forwards to `CComplexThing__Shutdown`. |
| `0x004fcfa0 CUnit__ClearSpawnerSet` | Clears active reader `+0x144`, drains linked set `+0x18c`, removes each value from the set, and invokes value vfunc `+0x8`. |
| `0x004fcfe0 CUnit__ReleaseChildUnits` | Drains child reader nodes at `+0x19c`, dispatching child vfunc `+0x8` or `+0xc8` depending on destroyed flag bit 2, then removes and frees each reader node. |
| `0x004fd040 CUnit__ResetDeploymentGraphAndScheduleEvent` | Releases child readers, clears active reader/set fields, reinitializes deployment-related state through `CExplosionInitThing__ctor_like_004fd230`, calls script event id 3/reset on `+0x74`, and schedules event 2000 relative to `DAT_00672fd0`. |
| `0x004fd140 CUnit__MarkDestroyedAndCleanupLinks` | Returns 0 when destroyed flag bit 2 is already set; otherwise kills sounds, marks destroyed, updates observed type/side counters, triggers destructible-segment cascade, calls script event id 5, clears reader/set links, and returns 1. |
| `0x004cb0b0 ParticleEffectLink__SetHandleStateAndClear` | Shared particle/effect owner-link cell helper, not a whole-CUnit object helper; xrefs come from CUnit, BattleEngine, Mine, particle descriptor, RTMesh, trigger, projectile, and raw cleanup contexts. |
| `0x004013d0 CActor__dtor_base` | Resets Actor vtable pointers and delegates to `CComplexThing__dtor_base`. |
| `0x004f3f00 CComplexThing__dtor_base` | Deletes mission script `+0x74`, animation `+0x6c`, and motion controller `+0x70` when present, then chains into the CThing destructor-base path. |

Read-back evidence:

- Fresh exports verified `12` metadata rows, `12` tag rows, `190` xref rows, `656` instruction rows, and `12` decompile rows.
- Export logs reported `targets=12 found=12 missing=0`, `rows=12 missing=0`, `Wrote 190 rows`, `Wrote 656 function-body instruction rows`, and `targets=12 dumped=12 missing=0 failed=0`.
- Static function-quality closure remains `6410/6410 = 100.00%`, expanded static surface remains `1560/1560 = 100.00%`, Wave911 focused progress remains `812/1408 = 57.67%`, and Wave911 top-500 risk-ranked coverage remains `500/500 = 100.00%`.
- Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260604-182217_post_wave1097_cunit_dtor_thunk_lifecycle_review_verified`, `19` files, `175541127` bytes, `DiffCount=0`.

What this proves:

- The twelve target function rows exist in the saved Ghidra project with saved names, signatures, and comments.
- The observed bodies and caller relationships are static retail Ghidra metadata/tag/xref/instruction/decompile evidence for the CUnit destructor/thunk/lifecycle cleanup graph and its Actor/ComplexThing tail.
- This wave connects older Wave460/Wave477/Wave517/Wave525/Wave526 saved rows into one fresh CUnit lifecycle read-back slice without changing the saved Ghidra database.

What remains unproven:

- Runtime destruction, cleanup order, event scheduling, child-unit release, or particle/effect behavior.
- Exact CUnit, CActor, CComplexThing, reader, set, owner-link, particle/effect, controller, script, or counter layouts.
- Exact Unit.cpp source-body identity.
- BEA patching behavior.
- Gameplay outcomes.
- Rebuild parity.

Probe token anchor: Wave1097; cunit-dtor-thunk-lifecycle-review-wave1097; 0x004bfe00 CUnit__dtor_base_Thunk_004bfe00; 0x004f84c0 CUnit__VFunc01_ScalarDeletingDtor; 0x004f84e0 CUnit__dtor_base; 0x0050ee90 CUnit__scalar_deleting_dtor; 0x004f95d0 CUnit__VFunc02_CleanupWorldLinksAndForward; 0x004fcfa0 CUnit__ClearSpawnerSet; 0x004fcfe0 CUnit__ReleaseChildUnits; 0x004fd040 CUnit__ResetDeploymentGraphAndScheduleEvent; 0x004fd140 CUnit__MarkDestroyedAndCleanupLinks; 0x004cb0b0 ParticleEffectLink__SetHandleStateAndClear; 0x004013d0 CActor__dtor_base; 0x004f3f00 CComplexThing__dtor_base; 1560/1560 = 100.00%; 812/1408 = 57.67%; 500/500 = 100.00%; 6410/6410 = 100.00%; [maintainer-local-ghidra-backup-root]\BEA_20260604-182217_post_wave1097_cunit_dtor_thunk_lifecycle_review_verified; read-only review.
