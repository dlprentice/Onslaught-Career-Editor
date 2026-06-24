# Ghidra Wave900+ Through Wave1043 Recheck

Status: structural static evidence recheck passed
Date: 2026-06-01
Scope: Wave900-Wave1043

This note extends the Wave900+ recheck gate after Wave1043. It is a structural evidence gate over saved readiness notes, focused probes, ignored evidence bases, backup references, apply-log coverage for mutation waves, direct focused-probe classifications for Wave982-Wave1043, and current queue closure.

Fresh validation command:

```powershell
npm run test:ghidra-wave900-plus-through-wave1043-recheck
```

Expected scope:

- Wave900-Wave981 remain covered by the earlier focused-probe sweep and evidence audit.
- Wave982-Wave1043 focused probes are rerun or classified by the current recheck gate.
- Wave910 and Wave911 remain queue/planning waves without per-wave Ghidra backup notes.
- Current live queue closure remains `6238/6238 = 100.00%`.

Wave1043 extension:

- Focused probe: `npm run test:ghidra-physics-statement-load-review-wave1043`
- Readiness note: `release/readiness/ghidra_physics_statement_load_review_wave1043_2026-06-01.md`
- Evidence base: `subagents/ghidra-static-reaudit/wave1043-physics-statement-load-review`
- Verified backup: `G:\GhidraBackups\BEA_20260601-100128_post_wave1043_physics_statement_load_review_verified`
- Mutation status: no mutation.
- Progress accounting: Wave1043 consolidates rows already reviewed by Wave917 and Wave933, so unique re-audit counters remain `735/1408 = 52.20%` and `968/1493 = 64.84%`.

Boundary note: this recheck validates static evidence structure, backups, probe wiring, and current queue closure. It does not prove runtime PhysicsScript behavior, serialized file-format completeness, exact source-layout identity, BEA patching, gameplay outcomes, or rebuild parity.

Probe token anchor: Wave1043; physics-statement-load-review-wave1043; 0x0042f2b0 CUnitStatement__LoadFromMemBuffer; 0x0042f780 CWeaponStatement__LoadFromMemBuffer; 0x0042fca0 CWeaponModeStatement__LoadFromMemBuffer; 0x00430210 CRoundStatement__LoadFromMemBuffer; 0x004306e0 CSpawnerStatement__LoadFromMemBuffer; 0x00431050 CComponentStatement__LoadFromMemBuffer; 0x004318f0 CHazardStatement__LoadFromMemBuffer; CPhysicsScriptStatements__CreateStatementType2; CPhysicsScriptStatements__CreateStatementType10; CDXMemBuffer__Read; CDXMemoryManager__Alloc; 735/1408 = 52.20%; 968/1493 = 64.84%; 500/500 = 100.00%; 6238/6238 = 100.00%; G:\GhidraBackups\BEA_20260601-100128_post_wave1043_physics_statement_load_review_verified; no mutation.
