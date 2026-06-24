# eventmanager.cpp

> Event scheduling system (`CEventManager`) from BEA.exe.

> **Queue status (2026-06-02):** Ghidra export-contract closure **6246/6246** (Wave1066: EventManager scheduler rows tag-normalized; not runtime proof or rebuild parity). Lines below that reference a "next raw commentless" row are **archival wave progress**, not open work.

## Overview

The Steam retail build keeps the same core architecture as Stuart's source:
- 20,000 preallocated `CScheduledEvent` entries
- 200-frame ring buffer at 20 FPS (`CLOCK_TICK = 0.05`)
- Overflow list for far-future events
- Per-frame flush with 3 priority buckets

**Debug path string**: `C:\dev\ONSLAUGHT2\eventmanager.cpp` at `0x00628d3c`

## Wave1066 Scheduler Re-Audit

Wave1066 (`event-manager-scheduler-review-wave1066`, `wave1066-readback-verified`) saved tag normalization for the existing EventManager scheduler rows from `0x0044afa0 CEventManager__ctor` through `0x0044b640 CEventManager__Flush`, plus the paired `CScheduledEvent` helpers in `scheduledevent.cpp`. Dry/apply/final-dry reported `updated=0 skipped=0 tags_added=166 missing=0 bad=0`, then `updated=13 skipped=0 tags_added=166 missing=0 bad=0`, then `updated=0 skipped=13 tags_added=0 missing=0 bad=0`.

Exact Wave1066 anchors: `0x0044afa0 CEventManager__ctor`, `0x0044b060 CEventManager__Init`, `0x0044b2d0 CEventManager__AddEvent_TimeFromNow`, `0x0044b310 CEventManager__AddEvent_ScheduledEvent`, `0x0044b600 CEventManager__AdvanceTime`, `0x0044b640 CEventManager__Flush`, `0x004de1f0 CScheduledEvent__Set`, and `0x004de230 CScheduledEvent__dtor`.

Fresh primary/context/post exports verified `13/13/47/549/13`, `11/11/573/993/11`, and `13/13/47/549/13` rows for metadata/tags/xrefs/instructions/decompile. Verified backup: `G:\GhidraBackups\BEA_20260602-000144_post_wave1066_event_manager_scheduler_review_verified`. Progress anchors: `812/1408 = 57.67%`, `1232/1560 = 78.97%`, `500/500 = 100.00%`, `6246/6246 = 100.00%`.

This proves saved static tag/read-back evidence only. Runtime event scheduling/flush/reuse/dispatch behavior, exact event payload schema, exact `CEventManager`/active-reader layouts, exact source-body identity, BEA patching, gameplay outcomes, and rebuild parity remain separate proof.

## Mapped Functions (Verified in Ghidra)

| Address | Name | Status | Notes |
|---------|------|--------|-------|
| 0x0044afa0 | CEventManager__ctor | RENAMED | Constructor: initializes 600 `CSPtrSet` buckets and sets vtable/flags. |
| 0x0044afe0 | CEventManager__scalar_deleting_dtor | RENAMED | MSVC scalar deleting dtor wrapper (`dtor` + optional free). |
| 0x0044b000 | CEventManager__dtor | RENAMED | Destructor body; calls `Shutdown()`. |
| 0x0044b060 | CEventManager__Init | RENAMED | Initializes counters, allocates overflow buffer + 20,000 event pool. |
| 0x0044b1f0 | CEventManager__Shutdown | RENAMED | Clears ring buckets, resets/deletes overflow container, frees pool. |
| 0x0044b2a0 | CEventManager__GetNextFreeEvent | RENAMED | Pops free-list head (`this+0x28`), logs fatal if exhausted. |
| 0x0044b2d0 | CEventManager__AddEvent_TimeFromNow | RENAMED | Relative-time overload, forwards to absolute-time path. |
| 0x0044b310 | CEventManager__AddEvent_ScheduledEvent | RENAMED | Scheduled-event overload; forwards + returns temp event to free-list path. |
| 0x0044b370 | CEventManager__AddEvent_AtTime | RENAMED | Main scheduler: ring-buffer insertion + overflow insertion logic. |
| 0x0044b5c0 | CEventManager__Update | RENAMED | `AdvanceTime()` then `Flush()`. |
| 0x0044b600 | CEventManager__AdvanceTime | RENAMED | Retail variant returns wrap flag (`iVar2 / 200`) while advancing frame/time/buffer index. |
| 0x0044b640 | CEventManager__Flush | RENAMED | Executes due events, cleans up non-reused events, updates counters, sanity-checks overflow ordering. |

## Retail vs Source Notes

- Stuart source declares `AdvanceTime()` as `void`; retail code at `0x0044b600` returns an integer wrap indicator while still performing the expected time/buffer advance.
- Source has a distinct `FreeEvent()` method, but retail emits equivalent free-list cleanup inline in multiple paths (notably `AddEvent_ScheduledEvent` and `Flush`).
- `LogEvent()` / `LogEventManager()` source paths are mostly debug-guarded; no separate high-signal runtime mapping was required for gameplay scheduling flow.
- Pre-comments were added at `0x0044af75` and `0x0044af95` to mark static init/shutdown callsites that construct/destruct the global event manager.

## Exception / Unwind Helpers

| Address | Name | Purpose |
|---------|------|---------|
| 0x005d24b0 | Unwind@005d24b0 | Wave749 `unwind-continuation-wave749` eventmanager-adjacent vector cleanup callback; calls `CRT__EhVectorDestructorIterator_WithUnwind` over `(*(EBP-0x10))+0x30` with `CSPtrSet__Clear`. |
| 0x005d24e0 | Unwind@005d24e0 | Wave750 `unwind-continuation-wave750` allocation unwind helper; calls `OID__FreeObject_Callback` for eventmanager.cpp debug path `0x00628d3c`, line `0x43`, allocation/type value `0x34`. |
| 0x005d24f6 | Unwind@005d24f6 | Wave750 `unwind-continuation-wave750` pool-allocation unwind helper; calls `OID__FreeObject_Callback` for eventmanager.cpp debug path `0x00628d3c`, line `0x43`, allocation/type value `0x37`. |
| 0x005d2520 | Unwind@005d2520 | Wave750 eventmanager-adjacent active-reader cleanup; calls `CGenericActiveReader__dtor` for `*(EBP-0x24)`. |
| 0x005d2528 | Unwind@005d2528 | Wave750 eventmanager-adjacent active-reader cleanup; calls `CGenericActiveReader__dtor` for `*(EBP-0x14)`. |
| 0x005d2540 | Unwind@005d2540 | Wave750 eventmanager-adjacent particle-list cleanup; calls `CParticleManager__RemoveFromGlobalList_Thunk` for stack-local manager/list node `EBP-0x44`. |
| 0x005d2560 | Unwind@005d2560 | Wave750 eventmanager-adjacent monitor cleanup; calls `CMonitor__Shutdown` for `*(EBP-0x10)`. |
| 0x005d2580 | Unwind@005d2580 | Wave750 eventmanager-adjacent descriptor cleanup; calls `CDXLandscape__DestroyResourceDescriptorArray_Thunk` for the stack-local descriptor array at `EBP-0x434`. |

Wave750 saved `0x005d24e0 Unwind@005d24e0` through `0x005d2580 Unwind@005d2580` as `void __cdecl Unwind@...(void)` with static Ghidra comments/tags and backup `G:\GhidraBackups\BEA_20260522-193422_post_wave750_unwind_continuation_verified`. Wave749 previously saved `0x005d24b0 Unwind@005d24b0` with backup `G:\GhidraBackups\BEA_20260522-190133_post_wave749_unwind_continuation_verified`. Exact parent source-body identity, runtime exception behavior, runtime cleanup behavior, BEA patching, and rebuild parity remain deferred.

## Cross-References

- Source reference: `references/Onslaught/eventmanager.cpp`
- Related helpers inferred from EventManager callsites:
  - `CScheduledEvent__Set` (`0x004de1f0`)
  - `CScheduledEvent__dtor` (`0x004de230`)
- Runtime caller examples:
  - `CFrontEnd__Init` / `CGame__InitRestartLoop` call `CEventManager__Init`
  - `CGame__Update` calls `CEventManager__AdvanceTime` and `CEventManager__Flush`
