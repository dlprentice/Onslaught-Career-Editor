# Ghidra Wave900+ Through Wave1066 Recheck

Status: current structural static evidence gate
Date: 2026-06-02
Scope: Wave900-Wave1066

This note extends the Wave900+ recheck gate through Wave1066 after the EventManager scheduler review. It is a structural validation gate over readiness notes, focused probes, ignored evidence bases, backup references, apply-script logs, and the current zero-debt queue. It is not runtime proof, exact source-layout proof, or rebuild parity.

Current extension:

- Wave1066 (`event-manager-scheduler-review-wave1066`) saved tag normalization for thirteen existing EventManager/ScheduledEvent scheduler rows.
- Representative anchors: `0x0044afa0 CEventManager__ctor`, `0x0044b060 CEventManager__Init`, `0x0044b2d0 CEventManager__AddEvent_TimeFromNow`, `0x0044b310 CEventManager__AddEvent_ScheduledEvent`, `0x0044b600 CEventManager__AdvanceTime`, `0x0044b640 CEventManager__Flush`, `0x004de1f0 CScheduledEvent__Set`, and `0x004de230 CScheduledEvent__dtor`.
- Pre primary exports verified `13` metadata rows, `13` tag rows, `47` xref rows, `549` function-body instruction rows, and `13` decompile rows.
- Context exports verified `11` metadata rows, `11` tag rows, `573` xref rows, `993` function-body instruction rows, and `11` decompile rows.
- Post primary exports verified `13` metadata rows, `13` tag rows, `47` xref rows, `549` function-body instruction rows, and `13` decompile rows.
- Tag-normalization dry/apply/final-dry: `updated=0 skipped=0 tags_added=166 missing=0 bad=0`, then `updated=13 skipped=0 tags_added=166 missing=0 bad=0`, then `updated=0 skipped=13 tags_added=0 missing=0 bad=0`, with `REPORT: Save succeeded`.
- Verified backup: `G:\GhidraBackups\BEA_20260602-000144_post_wave1066_event_manager_scheduler_review_verified`, `19` files, `174721927` bytes, `DiffCount=0`, `HashDiffCount=0`.
- Queue closure remains `6246/6246 = 100.00%`.
- Wave911 focused progress remains `812/1408 = 57.67%`.
- Expanded static surface progress advances to `1232/1560 = 78.97%`.
- Wave911 top-500 coverage remains `500/500 = 100.00%`.
- Mutation status: tag normalization only.

Expected command:

```powershell
npm run test:ghidra-wave900-plus-through-wave1066-recheck
```

Expected validation output should report:

- PASS status.
- Covered waves through Wave1066.
- Current live queue closure at `6246/6246 = 100.00%` with `0` commentless, `0` undefined signatures, and `0` `param_N`.
- Prior Wave900-Wave981 audit coverage preserved.
- Wave982-Wave1066 direct probe classifications with `0` disallowed evidence/unclassified failures.
- Backup references present, including `G:\GhidraBackups\BEA_20260602-000144_post_wave1066_event_manager_scheduler_review_verified`.

Boundary:

This recheck validates static evidence structure and current zero-debt queue state. It does not prove runtime event scheduling behavior, runtime gameplay behavior, exact source-layout identity, BEA patching behavior, gameplay outcomes, or rebuild parity.

Probe token anchor: Wave1066; event-manager-scheduler-review-wave1066; 0x0044afa0 CEventManager__ctor; 0x0044b060 CEventManager__Init; 0x0044b2d0 CEventManager__AddEvent_TimeFromNow; 0x0044b310 CEventManager__AddEvent_ScheduledEvent; 0x0044b600 CEventManager__AdvanceTime; 0x0044b640 CEventManager__Flush; 0x004de1f0 CScheduledEvent__Set; 0x004de230 CScheduledEvent__dtor; 812/1408 = 57.67%; 1232/1560 = 78.97%; 500/500 = 100.00%; 6246/6246 = 100.00%; G:\GhidraBackups\BEA_20260602-000144_post_wave1066_event_manager_scheduler_review_verified; tag normalization.
