# Ghidra Wave900+ Through Wave1052 Recheck

Status: structural static evidence recheck passed
Date: 2026-06-01
Scope: Wave900-Wave1052

This note extends the Wave900+ recheck gate after Wave1052. It is a structural evidence gate over saved readiness notes, focused probes, ignored evidence bases, backup references, apply-log coverage for mutation waves, direct focused-probe classifications for Wave982-Wave1052, and current queue closure.

Validation result: PASS. The gate covered 155 readiness notes across 153 waves, 151 package probe scripts, 151 evidence bases, 153 backup references, 46 apply scripts, and current queue closure at `6246/6246 = 100.00%`. Direct Wave982-Wave1052 probe classification recorded 71 results with 1 direct pass, 70 classified stale-current-state or rolled-current-doc failures, and 0 disallowed evidence/unclassified failures.

Fresh validation command:

```powershell
npm run test:ghidra-wave900-plus-through-wave1052-recheck
```

Expected scope:

- Wave900-Wave981 remain covered by the earlier focused-probe sweep and evidence audit.
- Wave982-Wave1052 focused probes are rerun or classified by the current recheck gate.
- Wave910 and Wave911 remain queue/planning waves without per-wave Ghidra backup notes.
- Current live queue closure remains `6246/6246 = 100.00%`.

Wave1052 extension:

- Focused probe: `npm run test:ghidra-cworld-line-trace-review-wave1052`
- Readiness note: `release/readiness/ghidra_cworld_line_trace_review_wave1052_2026-06-01.md`
- Evidence base: `subagents/ghidra-static-reaudit/wave1052-cworld-line-trace-review`
- Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260601-154511_post_wave1052_cworld_line_trace_review_verified`
- Mutation status: read-only static review; no rename, no signature change, no comment/tag change, no function-boundary change, no executable-byte change, no BEA launch, and no runtime/game-file mutation.
- Evidence counts: primary exports `1` metadata row, `1` tag row, `12` xref rows, `321` function-body instruction rows, and `1` decompile row; context exports `13` metadata rows, `13` tag rows, `105` xref rows, `4547` function-body instruction rows, and `13` decompile rows.
- Progress accounting: Wave911 focused progress advances to `745/1408 = 52.91%`; expanded static surface progress advances to `1033/1509 = 68.46%`; top-500 risk-ranked coverage remains `500/500 = 100.00%`.

Boundary note: this recheck validates static evidence structure, backups, probe wiring, direct-probe classifications, and current queue closure. It does not prove concrete `CLine` / `CWorldLineColReport` layouts, runtime collision/targeting/line-of-sight behavior, exact source-body identity, BEA patching, gameplay outcomes, or rebuild parity.

Probe token anchor: Wave1052; cworld-line-trace-review-wave1052; 0x0050b030 CWorld__FindFirstThingToHitLine; CHeightField__TraceLineAgainstHeightfield; CMapWho__GetFirstEntryWithinLine; CMapWho__GetNextEntryWithinLine; CThing__GetPersistentCollisionSeekingThing; CBattleEngine__CalcUnitOverCrossHair; CBattleEngine__HandleAutoAim; CUnit__ApplyDamage; CDXEngine__Render; references/Onslaught/BattleEngine.cpp; references/Onslaught/DXEngine.cpp; references/Onslaught/PCEngine.cpp; 745/1408 = 52.91%; 1033/1509 = 68.46%; 500/500 = 100.00%; 6246/6246 = 100.00%; [maintainer-local-ghidra-backup-root]\BEA_20260601-154511_post_wave1052_cworld_line_trace_review_verified; no mutation.
