# scheduledevent.cpp

> Scheduled event object (`CScheduledEvent`) used by `CEventManager` for time-based dispatch.
> Last updated: 2026-06-02

> **Queue status (2026-06-02):** Ghidra export-contract closure **6246/6246** (Wave1066: ScheduledEvent rows tag-normalized with EventManager scheduler review; not runtime proof or rebuild parity). Lines below that reference a "next raw commentless" row are **archival wave progress**, not open work.

## Overview

`CScheduledEvent` is a small pooled object used by `CEventManager`:

- Stores an `event_num` and a monitored `to_call` target (via `CActiveReader<CMonitor>`).
- Stores an optional monitored `data` pointer (also via ActiveReader).
- Stores either `time` (float) or a `nextFree` pointer when in the EventManager free list (union in source).

## Wave1066 Scheduler Re-Audit

Wave1066 (`event-manager-scheduler-review-wave1066`, `wave1066-readback-verified`) saved tag normalization for `0x004de1f0 CScheduledEvent__Set` and `0x004de230 CScheduledEvent__dtor` as part of the EventManager scheduler cluster. The paired EventManager evidence includes `0x0044afa0 CEventManager__ctor`, `0x0044b060 CEventManager__Init`, `0x0044b2d0 CEventManager__AddEvent_TimeFromNow`, `0x0044b310 CEventManager__AddEvent_ScheduledEvent`, `0x0044b600 CEventManager__AdvanceTime`, and `0x0044b640 CEventManager__Flush`.

Dry/apply/final-dry reported `updated=0 skipped=0 tags_added=166 missing=0 bad=0`, then `updated=13 skipped=0 tags_added=166 missing=0 bad=0`, then `updated=0 skipped=13 tags_added=0 missing=0 bad=0`. Fresh primary/context/post exports verified `13/13/47/549/13`, `11/11/573/993/11`, and `13/13/47/549/13` rows. Verified backup: `G:\GhidraBackups\BEA_20260602-000144_post_wave1066_event_manager_scheduler_review_verified`. Progress anchors: `812/1408 = 57.67%`, `1232/1560 = 78.97%`, `500/500 = 100.00%`, `6246/6246 = 100.00%`.

Runtime event scheduling/flush/reuse/dispatch behavior, exact event payload schema, exact `CScheduledEvent`/active-reader layout, exact source-body identity, BEA patching, gameplay outcomes, and rebuild parity remain separate proof.

## Mapped Functions (Verified In Ghidra)

| Address | Name | Status | Notes |
|---------|------|--------|-------|
| 0x004de1f0 | [CScheduledEvent__Set](./CScheduledEvent__Set.md) | DOCUMENTED | Source-aligned `CScheduledEvent::Set(...)` initializer. |
| 0x004de230 | [CScheduledEvent__dtor](./CScheduledEvent__dtor.md) | DOCUMENTED | Source-aligned `CScheduledEvent::~CScheduledEvent()`; decrements live counter and unregisters reader cells. |

## Struct Notes (Retail Observations)

The decompiled `CScheduledEvent__Set` implies the following layout (offsets relative to `this`):

| Offset | Type | Meaning |
|--------|------|---------|
| 0x00 | ActiveReader cell | `CEvent::mToCall` |
| 0x04 | `short` | `CEvent::mEventNum` |
| 0x08 | `short` | `CScheduledEvent::mBeingReused` |
| 0x0C | ActiveReader cell | `CScheduledEvent::mData` |
| 0x10 | `float` | `CScheduledEvent::mTime` (unioned with next-free pointer when on free list) |

The destructor decrements a global counter (in this build: `DAT_0083cde8`), corresponding to `CScheduledEvent::mNumCreated` in Stuart's source.

## Related

- `CEventManager` mappings: `reverse-engineering/binary-analysis/functions/eventmanager.cpp/_index.md`
- Source reference: `references/Onslaught/scheduledevent.h`, `references/Onslaught/scheduledevent.cpp`
