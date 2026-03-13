# CScheduledEvent__Set

- **Address:** `0x004de1f0`
- **Status:** Renamed, signature set, commented in Ghidra (read-back verified)
- **Signature:** `void CScheduledEvent__Set(void *this, short event_num, float *time, void *to_call, void *data)`
- **Source Alignment:** `CScheduledEvent::Set(int event_num, const float& time, CMonitor* to_call, CMonitor* data)` in `references/Onslaught/scheduledevent.cpp`.

## Behavior

Initializes one scheduled event instance:

1. Stores `event_num` into the base `CEvent` field (`short`).
2. Copies the referenced `time` float into the event’s `mTime` field.
3. Sets the `mToCall` ActiveReader to `to_call`.
4. Clears the “being reused” flag.
5. Sets the `mData` ActiveReader to `data`.

## Notes

- The retail build passes `time` as a pointer (`float *`) consistent with a C++ `const float&` parameter lowering.
- Both `to_call` and `data` behave as monitored pointers (`CMonitor*`) via the ActiveReader deletion-event system.

## Related

- `CScheduledEvent__dtor` (`0x004de230`)
- `CEventManager__AddEvent_AtTime` (`0x0044b370`)

