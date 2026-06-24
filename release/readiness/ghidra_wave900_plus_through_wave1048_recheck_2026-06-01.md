# Ghidra Wave900+ Through Wave1048 Recheck

Status: structural static evidence recheck passed
Date: 2026-06-01
Scope: Wave900-Wave1048

This note extends the Wave900+ recheck gate after Wave1048. It is a structural evidence gate over saved readiness notes, focused probes, ignored evidence bases, backup references, apply-log coverage for mutation waves, direct focused-probe classifications for Wave982-Wave1048, and current queue closure.

Validation result: PASS. The gate covered 151 readiness notes across 149 waves, 147 package probe scripts, 147 evidence bases, 149 backup references, 44 apply scripts, and current queue closure at `6246/6246 = 100.00%`. Direct Wave982-Wave1048 probe classification recorded 67 results with 1 direct pass, 66 classified stale-current-state or rolled-current-doc failures, and 0 disallowed evidence/unclassified failures.

Fresh validation command:

```powershell
npm run test:ghidra-wave900-plus-through-wave1048-recheck
```

Expected scope:

- Wave900-Wave981 remain covered by the earlier focused-probe sweep and evidence audit.
- Wave982-Wave1048 focused probes are rerun or classified by the current recheck gate.
- Wave910 and Wave911 remain queue/planning waves without per-wave Ghidra backup notes.
- Current live queue closure remains `6246/6246 = 100.00%`.

Wave1048 extension:

- Focused probe: `npm run test:ghidra-cunit-tail-linked-vfunc-review-wave1048`
- Readiness note: `release/readiness/ghidra_cunit_tail_linked_vfunc_review_wave1048_2026-06-01.md`
- Evidence base: `subagents/ghidra-static-reaudit/wave1048-cunit-tail-linked-vfunc-review`
- Verified backup: `G:\GhidraBackups\BEA_20260601-131919_post_wave1048_cunit_tail_linked_vfunc_review_verified`
- Mutation status: no mutation. Fresh evidence re-read the CUnit attached-node forwarders, recent segment-damage meter, linked-target activation/deactivation helpers, and vtable slots without rename, signature change, comment/tag change, function-boundary change, executable-byte change, BEA launch, or runtime/game-file mutation.
- Evidence counts: primary exports `6` metadata rows, `6` tag rows, `116` xref rows, `175` function-body instruction rows, and `6` decompile rows; context exports `10` metadata rows, `10` tag rows, `78` xref rows, `596` function-body instruction rows, and `10` decompile rows; vtable export `4` anchors and `528` slot rows.
- Progress accounting: Wave1048 adds four newly direct-reviewed Wave911 focused rows beyond earlier context coverage, so Wave911 focused progress advances to `744/1408 = 52.84%`; expanded static surface progress advances to `1002/1509 = 66.40%`; top-500 risk-ranked coverage remains `500/500 = 100.00%`.

Boundary note: this recheck validates static evidence structure, backups, probe wiring, direct-probe classifications, and current queue closure. It does not prove runtime activation/deactivation behavior, linked-reader side effects, recent segment-damage meter behavior, exact `CUnit` / attached-node / linked-reader / destructible-segment layouts, exact source-body identity, BEA patching, gameplay outcomes, or rebuild parity.

Probe token anchor: Wave1048; cunit-tail-linked-vfunc-review-wave1048; 0x004fce40 CUnit__ForwardAttachedNodeVFunc14IfPresent; 0x004fce80 CUnit__ForwardAttachedNodeVFunc18IfPresent; 0x004fcec0 CUnit__ForwardAttachedNodeVFunc1CIfPresent; 0x004fd5e0 CUnit__VFunc26_GetRecentSegmentDamageMeter; 0x004fd6a0 CUnit__VFunc22_ActivateLinkedTargetsAndChildren; 0x004fd700 CUnit__VFunc23_DeactivateLinkedTargetsAndChildren; CDestructableSegmentsController__GetSegmentLastDamageTimeByIndex; CDestructableSegmentsController__GetSegmentLastDamageAmountByIndex; 0x005d8d1c; 0x005e0b30; 0x005e297c; 0x005e32d4; 744/1408 = 52.84%; 1002/1509 = 66.40%; 500/500 = 100.00%; 6246/6246 = 100.00%; G:\GhidraBackups\BEA_20260601-131919_post_wave1048_cunit_tail_linked_vfunc_review_verified; no mutation.
