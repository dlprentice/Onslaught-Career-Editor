# eventmanager.cpp

> Event scheduling system (`CEventManager`) from BEA.exe.

## Overview

The Steam retail build keeps the same core architecture as Stuart's source:
- 20,000 preallocated `CScheduledEvent` entries
- 200-frame ring buffer at 20 FPS (`CLOCK_TICK = 0.05`)
- Overflow list for far-future events
- Per-frame flush with 3 priority buckets

**Debug path string**: `C:\dev\ONSLAUGHT2\eventmanager.cpp` at `0x00628d3c`

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
| 0x005d24e0 | Unwind@005d24e0 | Allocation unwind helper during `CEventManager__Init`. |
| 0x005d24f6 | Unwind@005d24f6 | Pool-allocation unwind helper during `CEventManager__Init`. |

## Cross-References

- Source reference: `references/Onslaught/eventmanager.cpp`
- Related helpers inferred from EventManager callsites:
  - `CScheduledEvent__Set` (`0x004de1f0`)
  - `CScheduledEvent__dtor` (`0x004de230`)
- Runtime caller examples:
  - `CFrontEnd__Init` / `CGame__InitRestartLoop` call `CEventManager__Init`
  - `CGame__Update` calls `CEventManager__AdvanceTime` and `CEventManager__Flush`
