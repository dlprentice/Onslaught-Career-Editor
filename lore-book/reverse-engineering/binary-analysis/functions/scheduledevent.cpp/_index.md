# scheduledevent.cpp

> Scheduled event object (`CScheduledEvent`) used by `CEventManager` for time-based dispatch.
> Last updated: 2026-02-12

## Overview

`CScheduledEvent` is a small pooled object used by `CEventManager`:

- Stores an `event_num` and a monitored `to_call` target (via `CActiveReader<CMonitor>`).
- Stores an optional monitored `data` pointer (also via ActiveReader).
- Stores either `time` (float) or a `nextFree` pointer when in the EventManager free list (union in source).

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

