# Ghidra EventManager Scheduler Review Wave1066 Readiness Note

<!-- ghidra-full-reaudit-20260713:start -->
> **2026-07-13 live correction closeout:** Historical record; `0x0046e910` comment correction. The original text below remains provenance rather than current semantic authority. It is superseded only where confirmed. Use the [closeout](../../reverse-engineering/binary-analysis/ghidra-full-reaudit-closeout-2026-07-13.md); final per-address decisions and exact before/after metadata are in `reverse-engineering/binary-analysis/ghidra-reviewed-correction-decisions-2026-07-13.jsonl` and `reverse-engineering/binary-analysis/ghidra-reviewed-correction-plan-2026-07-13.json`.
<!-- ghidra-full-reaudit-20260713:end -->

Status: complete static tag-normalization evidence
Date: 2026-06-02
Scope: `event-manager-scheduler-review-wave1066`

Wave1066 re-read the existing EventManager and ScheduledEvent scheduler surface, then saved tags for thirteen already named, commented, and signature-correct rows. Fresh exports confirmed the current comments/signatures align with `eventmanager.cpp`, `scheduledevent.cpp`, static instruction/decompile evidence, and scheduler callsite/xref context, so the wave made no semantic rename, no signature change, no comment change, no function-boundary change, no executable-byte change, and did not launch BEA or mutate runtime/game files.

The only Ghidra mutation was tag normalization with `event-manager-scheduler-review-wave1066` and `wave1066-readback-verified`.

Primary anchors:

| Address | Static evidence |
| --- | --- |
| `0x0044afa0 CEventManager__ctor` | Static init call at `0x0044af75`; body initializes 600 `CSPtrSet` buckets, vtable, overflow pointer, and valid flag state. |
| `0x0044afe0 CEventManager__scalar_deleting_dtor` | DATA xref `0x005db28c`; wrapper calls `CEventManager__dtor` and conditionally frees `this`. |
| `0x0044b060 CEventManager__Init` | Called from `CFrontEnd__Init` and `CGame__InitRestartLoop`; allocates overflow storage and the 20,000-entry scheduled-event pool/free-list. |
| `0x0044b1f0 CEventManager__Shutdown` | Called by `CLTShell__ShutdownRuntimeAndReleaseResources`, `CGame__ShutdownRestartLoop`, and the EventManager destructor; clears buffers and releases event storage. |
| `0x0044b2a0 CEventManager__GetNextFreeEvent` | Called by IScript sound-fade event helpers; pops the event free-list and retains fatal-on-exhaustion evidence. |
| `0x0044b2d0 CEventManager__AddEvent_TimeFromNow` | Broad callsite coverage from game/player/message/tree/round/unit flows; converts relative time to absolute time before forwarding. |
| `0x0044b310 CEventManager__AddEvent_ScheduledEvent` | Scheduled-event overload; forwards to absolute-time insertion and returns the temporary event to the free-list path. |
| `0x0044b5c0 CEventManager__Update` | Called by `CFrontEnd__Process`; invokes `AdvanceTime` then `Flush`. |
| `0x0044b600 CEventManager__AdvanceTime` | Called by `CGame__Update`; advances frame/time/ring-buffer state and returns the modulo wrap carry. |
| `0x0044b640 CEventManager__Flush` | Called by `CEventManager__Update` and `CGame__Update`; flushes due priority/overflow events and cleans active-reader event payloads. |
| `0x004de1f0 CScheduledEvent__Set` | Called by `CEventManager__AddEvent_AtTime` and IScript sound-fade helpers; initializes event number, target active-reader, time, reuse flag, and data active-reader. |
| `0x004de230 CScheduledEvent__dtor` | DATA refs from `CEventManager__Init` and `CEventManager__Shutdown`; unregisters active-reader cells and decrements the scheduled-event live counter. |

Context anchors:

- `0x0044b370 CEventManager__AddEvent_AtTime`
- `0x0046e910 CGame__Update`
- `0x0046ff10 CGame__HandleEvent`
- `0x0044d320 CFrontEnd__InitPageStateDefaults`
- `0x00466ba0 CFrontEnd__Process`
- `0x0044b1d0 CGenericActiveReader__dtor`
- `0x0042d9b0 CMonitor__DeleteDeletionEvent`
- `0x004e5840 CSPtrSet__Init`
- `0x004e5990 CSPtrSet__ClearAnyDynamicCreatedNodes`
- `0x00401000 CGenericActiveReader__SetReader`
- `0x00401040 CMonitor__AddDeletionEvent`

Read-back evidence:

- Pre primary exports: `13` metadata rows, `13` tag rows, `47` xref rows, `549` function-body instruction rows, and `13` decompile rows.
- Context exports: `11` metadata rows, `11` tag rows, `573` xref rows, `993` function-body instruction rows, and `11` decompile rows.
- Tag-normalization dry/apply/final-dry: `updated=0 skipped=0 tags_added=166 missing=0 bad=0`, then `updated=13 skipped=0 tags_added=166 missing=0 bad=0`, then `updated=0 skipped=13 tags_added=0 missing=0 bad=0`, with `REPORT: Save succeeded`.
- Post primary exports: `13` metadata rows, `13` tag rows, `47` xref rows, `549` function-body instruction rows, and `13` decompile rows.
- Queue closure remains `6246/6246 = 100.00%`.
- Wave911 focused progress remains `812/1408 = 57.67%`.
- Expanded static surface progress advances to `1232/1560 = 78.97%`.
- Wave911 top-500 coverage remains `500/500 = 100.00%`.
- Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260602-000144_post_wave1066_event_manager_scheduler_review_verified`, `19` files, `174721927` bytes, `DiffCount=0`, `HashDiffCount=0`.

What this proves:

- The thirteen primary EventManager/ScheduledEvent rows exist in the saved Ghidra project with expected names, signatures, comments, and Wave1066 tags.
- The exported instructions, decompile rows, xrefs, and context rows remain coherent with the existing static scheduler mapping.
- The saved database now records the EventManager scheduler review tags for later filtering and aggregate audit.

What remains unproven:

- Runtime event scheduling, flush ordering, reuse/free-list behavior, or dispatch outcomes.
- Exact event payload schema.
- Exact `CEventManager`, `CScheduledEvent`, `CMonitor`, or `CGenericActiveReader` layouts.
- Exact source-body identity beyond the static source-aligned mapping evidence.
- BEA patching behavior.
- Gameplay outcomes.
- Rebuild parity.

Next candidate note: continue with the next expanded static re-audit cluster; prefer read-only review first and mutate only when fresh evidence proves a correction or normalization need.

Probe token anchor: Wave1066; event-manager-scheduler-review-wave1066; 0x0044afa0 CEventManager__ctor; 0x0044b060 CEventManager__Init; 0x0044b2d0 CEventManager__AddEvent_TimeFromNow; 0x0044b310 CEventManager__AddEvent_ScheduledEvent; 0x0044b600 CEventManager__AdvanceTime; 0x0044b640 CEventManager__Flush; 0x004de1f0 CScheduledEvent__Set; 0x004de230 CScheduledEvent__dtor; 812/1408 = 57.67%; 1232/1560 = 78.97%; 500/500 = 100.00%; 6246/6246 = 100.00%; [maintainer-local-ghidra-backup-root]\BEA_20260602-000144_post_wave1066_event_manager_scheduler_review_verified; tag normalization.
