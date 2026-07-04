# Ghidra Wave900+ Through Wave1067 Recheck

Status: current structural static evidence gate
Date: 2026-06-02
Scope: Wave900-Wave1067

This note extends the Wave900+ recheck gate through Wave1067 after the destructable-controller lookup/damage review. It is a structural validation gate over readiness notes, focused probes, ignored evidence bases, backup references, apply-script logs, and the current zero-debt queue. It is not runtime proof, exact source-layout proof, or rebuild parity.

Current extension:

- Wave1067 (`destructable-controller-lookup-damage-review-wave1067`) re-read sixteen existing `CDestructableSegmentsController__*` lookup, damage, health, cascade, and name-dispatch rows with no mutation.
- Representative anchors: `0x00443fc0 CDestructableSegmentsController__Ctor`, `0x00444030 CDestructableSegmentsController__DamageSegmentByIndexAndUpdateThreshold`, `0x00444160 CDestructableSegmentsController__ApplyRandomDamageBurstAndUpdateThreshold`, `0x004442d0 CDestructableSegmentsController__GetSegmentLastDamageTimeByIndex`, `0x00444300 CDestructableSegmentsController__GetSegmentLastDamageAmountByIndex`, `0x004443f0 CDestructableSegmentsController__TriggerCoreCascadeIfEligible`, `0x00444450 CDestructableSegmentsController__SetSegmentField0CByName`, `0x00444520 CDestructableSegmentsController__FindSegmentByName`, `0x004445b0 CDestructableSegmentsController__SetSegmentActiveFlagByName`, and `0x00444620 CDestructableSegmentsController__SetAllSegmentsActiveFlagAndRefreshMetric`.
- Primary exports verified `16` metadata rows, `16` tag rows, `17` xref rows, `590` function-body instruction rows, and `16` decompile rows.
- Context exports verified `20` metadata rows, `20` tag rows, `142` xref rows, `1757` function-body instruction rows, and `20` decompile rows.
- Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260602-003225_post_wave1067_destructable_controller_lookup_damage_review_verified`, `19` files, `174721927` bytes, `DiffCount=0`, `HashDiffCount=0`.
- Queue closure remains `6246/6246 = 100.00%`.
- Wave911 focused progress remains `812/1408 = 57.67%`.
- Expanded static surface progress advances to `1248/1560 = 80.00%`.
- Wave911 top-500 coverage remains `500/500 = 100.00%`.
- Mutation status: read-only review, no mutation.

Expected command:

```powershell
npm run test:ghidra-wave900-plus-through-wave1067-recheck
```

Expected validation output should report:

- PASS status.
- Covered waves through Wave1067.
- Current live queue closure at `6246/6246 = 100.00%` with `0` commentless, `0` undefined signatures, and `0` `param_N`.
- Prior Wave900-Wave981 audit coverage preserved.
- Wave982-Wave1067 direct probe classifications with `0` disallowed evidence/unclassified failures.
- Backup references present, including `[maintainer-local-ghidra-backup-root]\BEA_20260602-003225_post_wave1067_destructable_controller_lookup_damage_review_verified`.

Boundary:

This recheck validates static evidence structure and current zero-debt queue state. It does not prove runtime destructable-controller damage/cascade/name-dispatch behavior, runtime gameplay behavior, exact source-layout identity, BEA patching behavior, gameplay outcomes, or rebuild parity.

Probe token anchor: Wave1067; destructable-controller-lookup-damage-review-wave1067; 0x00443fc0 CDestructableSegmentsController__Ctor; 0x00444030 CDestructableSegmentsController__DamageSegmentByIndexAndUpdateThreshold; 0x00444160 CDestructableSegmentsController__ApplyRandomDamageBurstAndUpdateThreshold; 0x004442d0 CDestructableSegmentsController__GetSegmentLastDamageTimeByIndex; 0x00444300 CDestructableSegmentsController__GetSegmentLastDamageAmountByIndex; 0x004443f0 CDestructableSegmentsController__TriggerCoreCascadeIfEligible; 0x00444450 CDestructableSegmentsController__SetSegmentField0CByName; 0x00444520 CDestructableSegmentsController__FindSegmentByName; 0x004445b0 CDestructableSegmentsController__SetSegmentActiveFlagByName; 0x00444620 CDestructableSegmentsController__SetAllSegmentsActiveFlagAndRefreshMetric; 812/1408 = 57.67%; 1248/1560 = 80.00%; 500/500 = 100.00%; 6246/6246 = 100.00%; [maintainer-local-ghidra-backup-root]\BEA_20260602-003225_post_wave1067_destructable_controller_lookup_damage_review_verified; read-only review.
