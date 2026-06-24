# Ghidra Wave900+ Through Wave1047 Recheck

Status: structural static evidence recheck passed
Date: 2026-06-01
Scope: Wave900-Wave1047

This note extends the Wave900+ recheck gate after Wave1047. It is a structural evidence gate over saved readiness notes, focused probes, ignored evidence bases, backup references, apply-log coverage for mutation waves, direct focused-probe classifications for Wave982-Wave1047, and current queue closure.

Validation result: PASS. The gate covered 150 readiness notes across 148 waves, 146 package probe scripts, 146 evidence bases, 148 backup references, 44 apply scripts, and current queue closure at `6246/6246 = 100.00%`. Direct Wave982-Wave1047 probe classification recorded 66 results with 1 direct pass, 65 classified stale-current-state or rolled-current-doc failures, and 0 disallowed evidence/unclassified failures.

Fresh validation command:

```powershell
npm run test:ghidra-wave900-plus-through-wave1047-recheck
```

Expected scope:

- Wave900-Wave981 remain covered by the earlier focused-probe sweep and evidence audit.
- Wave982-Wave1047 focused probes are rerun or classified by the current recheck gate.
- Wave910 and Wave911 remain queue/planning waves without per-wave Ghidra backup notes.
- Current live queue closure remains `6246/6246 = 100.00%`.

Wave1047 extension:

- Focused probe: `npm run test:ghidra-physics-statement-create-recurse-review-wave1047`
- Readiness note: `release/readiness/ghidra_physics_statement_create_recurse_review_wave1047_2026-06-01.md`
- Evidence base: `subagents/ghidra-static-reaudit/wave1047-physics-statement-create-recurse-review`
- Verified backup: `G:\GhidraBackups\BEA_20260601-124915_post_wave1047_physics_statement_create_recurse_review_verified`
- Mutation status: comment/tag correction only. Fresh evidence corrected the statement create/recurse context wording for nine PhysicsScript rows without rename, signature change, function-boundary change, executable-byte change, BEA launch, or runtime/game-file mutation.
- Progress accounting: Wave1047 adds five newly direct-reviewed Wave911 focused rows beyond prior Wave1040 coverage, so Wave911 focused progress advances to `740/1408 = 52.56%`; expanded static surface progress advances to `998/1509 = 66.14%`; top-500 risk-ranked coverage remains `500/500 = 100.00%`.

Boundary note: this recheck validates static evidence structure, backups, probe wiring, direct-probe classifications, and current queue closure. It does not prove runtime PhysicsScript behavior, mission-script outcomes, exact statement/value-list/registry/UnitAI record layouts, exact source-body identity, BEA patching, gameplay outcomes, or rebuild parity.

Probe token anchor: Wave1047; physics-statement-create-recurse-review-wave1047; 0x0042ede0 CUnitStatement__CreateUnitAndRecurse; 0x0042f5b0 CWeaponStatement__CreateWeaponAndRecurse; 0x0042fa40 CWeaponModeStatement__CreateWeaponModeAndRecurse; 0x0042ff60 CRoundStatement__CreateRoundAndRecurse; 0x004304d0 CSpawnerStatement__CreateSpawnerAndRecurse; 0x004309a0 CExplosionStatement__CreateExplosionAndRecurse; 0x00430e20 CComponentStatement__CreateComponentAndRecurse; 0x00431310 CFeatureStatement__CreateFeatureAndRecurse; 0x00431760 CHazardStatement__CreateHazardAndRecurse; DAT_008553fc; CStatementChain__InvokeVFunc04OnNodes; 740/1408 = 52.56%; 998/1509 = 66.14%; 500/500 = 100.00%; 6246/6246 = 100.00%; G:\GhidraBackups\BEA_20260601-124915_post_wave1047_physics_statement_create_recurse_review_verified; comment/tag correction.
