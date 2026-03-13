# CScheduledEvent__dtor

- **Address:** `0x004de230`
- **Status:** Renamed, signature set, commented in Ghidra (read-back verified)
- **Signature:** `void CScheduledEvent__dtor(void *this)`
- **Source Alignment:** `CScheduledEvent::~CScheduledEvent()` in `references/Onslaught/scheduledevent.cpp`.

## Behavior

1. Decrements the global live-instance counter (`CScheduledEvent::mNumCreated` in source; a global in retail).
2. Unregisters ActiveReader cells from monitor deletion lists:
   - `mData` cell (at `this+0x0C`)
   - `mToCall` cell (base at `this+0x00`)

## Notes

- In this retail build, the dtor includes explicit list removals (`CSPtrSet__Remove`) rather than relying on a separate ActiveReader dtor helper.

## Related

- `CScheduledEvent__Set` (`0x004de1f0`)
- Monitor helpers: `CMonitor__AddDeletionEvent` (`0x00401040`), `CMonitor__DeleteDeletionEvent` (`0x0042d9b0`)

