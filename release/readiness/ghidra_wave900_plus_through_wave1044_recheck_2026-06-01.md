# Ghidra Wave900+ Through Wave1044 Recheck

Status: structural static evidence recheck passed
Date: 2026-06-01
Scope: Wave900-Wave1044

This note extends the Wave900+ recheck gate after Wave1044. It is a structural evidence gate over saved readiness notes, focused probes, ignored evidence bases, backup references, apply-log coverage for mutation waves, direct focused-probe classifications for Wave982-Wave1044, and current queue closure.

Validation result: PASS. The gate covered 147 readiness notes across 145 waves, 143 package probe scripts, 143 evidence bases, 145 backup references, 42 apply scripts, and current queue closure at `6238/6238 = 100.00%`. Direct Wave982-Wave1044 probe classification recorded 63 results with 1 direct pass, 62 classified stale-current-state failures, and 0 disallowed evidence/unclassified failures.

Fresh validation command:

```powershell
npm run test:ghidra-wave900-plus-through-wave1044-recheck
```

Expected scope:

- Wave900-Wave981 remain covered by the earlier focused-probe sweep and evidence audit.
- Wave982-Wave1044 focused probes are rerun or classified by the current recheck gate.
- Wave910 and Wave911 remain queue/planning waves without per-wave Ghidra backup notes.
- Current live queue closure remains `6238/6238 = 100.00%`.

Wave1044 extension:

- Focused probe: `npm run test:ghidra-career-controller-residual-review-wave1044`
- Readiness note: `release/readiness/ghidra_career_controller_residual_review_wave1044_2026-06-01.md`
- Evidence base: `subagents/ghidra-static-reaudit/wave1044-career-controller-residual-review`
- Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260601-103855_post_wave1044_career_controller_residual_review_verified`
- Mutation status: no mutation.
- Progress accounting: Wave1044 targets are not Wave911 focused TSV rows, so Wave911 focused progress remains `735/1408 = 52.20%`; expanded static surface progress advances to `977/1493 = 65.44%`; top-500 risk-ranked coverage remains `500/500 = 100.00%`.

Boundary note: this recheck validates static evidence structure, backups, probe wiring, and current queue closure. It does not prove runtime save/progression behavior, runtime Goodies/controller/input behavior, exact source-layout identity, BEA patching, gameplay outcomes, or rebuild parity.

Probe token anchor: Wave1044; career-controller-residual-review-wave1044; 0x0041b740 CCareerNode__Blank; 0x0041c180 CCareer__UpdateThingsKilled; 0x0041c470 CCareer__UpdateGoodieStates; 0x004214e0 CCareer__SetSlot; 0x0042d640 CController__Init; 0x0042d8a0 CController__StartRecording; 0x0042d8c0 CController__StartPlayback; 0x0042d8e0 CController__dtor; 0x004f00d0 CController__dtor_Thunk; CCareer__GetGradeForWorld; CGrade__operator_gte; CDXMemBuffer__OpenWrite; CDXMemBuffer__InitFromFile; CMonitor__DeleteDeletionEvent; 735/1408 = 52.20%; 977/1493 = 65.44%; 500/500 = 100.00%; 6238/6238 = 100.00%; [maintainer-local-ghidra-backup-root]\BEA_20260601-103855_post_wave1044_career_controller_residual_review_verified; no mutation.
