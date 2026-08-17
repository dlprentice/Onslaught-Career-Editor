# CEventManager / CScheduledEvent function map

Status: active static function map
Last updated: 2026-08-17
Source File: `C:\dev\ONSLAUGHT2\EventManager.cpp` (SEH `__FILE__` pointer `0x005d250c` in `Init`; see the map below) | Binary: BEA.exe, SHA-256 `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`
Evidence: MEASURED — every byte below was re-read from the pristine specimen at
file offset VA − 0x400000. The rebuild already owns one of these laws
(`CEventManager::AddEvent(CScheduledEvent*)` → `RetailEventScheduler.AddEvent`,
a REBUILD_READY row): the event number is a 16-bit word.

## Functions

| Address | Name | Byte evidence | Contract (confidence) |
| --- | --- | --- | --- |
| `0x0044b060` | `CEventManager__Init` | `6aff 680c255d00 64a100000000 … 6a34 8bf1 683c8d6200 33ff 6a43 6a10 b9f03d9c00 … 897e08 897e10 897e14 …` | SEH prologue with `__FILE__`/`__LINE__`, allocates **0x34** bytes from pool `0x009c3df0`, and zeroes the three heads at `+0x08`, `+0x10`, `+0x14`. HIGH: a constructor/init that allocates the 52-byte manager and clears its three lists. |
| `0x0044b2a0` | `CEventManager__GetNextFreeEvent` | `56 8b7128 85f6 740a 8b4610 894128 8bc6 5ec3 68608d6200 6880f56600 e87f64ffff …` | Pops the free-list head at `+0x28`, advances it through `+0x10`, and returns the node; on empty it prints via two string references (`0x00628d60`, `0x0066f580`). HIGH: free-list pop with an error path. |
| `0x0044b2d0` | `CEventManager__AddEvent_TimeFromNow` | `8b442404 8b542418 d94108 d800 8b442414 … 50 e870000000 c21800` | Adds the argument float to the manager's current time (`fld [ecx+8]; fadd st0`), re-packs the tuple, and forwards to `AddEvent_AtTime` (+0x70). HIGH: a time-offset wrapper. |
| `0x0044b370` | `CEventManager__AddEvent_AtTime` | `83ec08 535556 8bf1 57 8b4604 85c0 751c 68948d6200 6880f56600 e8b163ffff … 8b6c2420 85ed 0f8403020000` | Validates the head pointer (`+0x04`), asserts on null, then enters a ~0x200-byte insertion scan by time. MEDIUM-HIGH: ordered-ring insertion by timestamp; the exact comparison axis needs one more witness. |
| `0x0044b5c0` | `CEventManager__Update` | `83ec08 8b4114 56 40 bec8000000 894114 … 99 df6c2404 f7fe d80d78855d00 d95908 895110 e8…` | Increments the tick counter at `+0x14`, converts to time via divide-by-200 and subtract of the constant at `0x005d8578`, stores the float at `+0x08` and the remainder at `+0x10`, then calls onward. HIGH: tick→time update; the callee chain after the conversion remains open. |
| `0x0044b600` | `CEventManager__AdvanceTime` | `83ec08 8b4114 56 40 bec8000000 894114 … d80d78855d00 d95908 5e 895110 83…` | The same tick→time conversion body as `Update` (tick/200 minus `0x005d8578`), without `Update`'s trailing call. HIGH: the advance half of the pair; note the two functions share the conversion and differ in the dispatch tail. |
| `0x0044b640` | `CEventManager__Flush` | `83ec08 535556 8bf1 33ed 57 8b5e1c 8b460c 89442414 896e24 8d0c5b … c1e104 8d7c3138 8b47f8 3bc5 8907 …` | Walks the ring at `+0x0C`/`+0x1C` with stride 0x10 and visits each node, clearing the `+0x24` flag as it goes. MEDIUM: a ring flush/scan; which events fire during the walk remains open. |
| `0x004de1f0` | `CScheduledEvent__Set` | `668b442404 56 8bf1 8b4c240c 66894604 8b442410 8b11 50 8bce 895610 e8ef2df2ff … 66c746080000 51 8d4e0c e8dc2df2ff` | Stores the event number as a **16-bit word** at `+0x04` (`mov [esi+4],ax`), copies a dword into `+0x10`, and zeroes the word at `+0x08` — the byte witness behind the already-landed REBUILD_READY `AddEvent` law. HIGH: direct corroboration of the rebuild's int16 event-number contract. |

## Open questions (cheapest falsifier first)

- `Update` vs `AdvanceTime`: capture the call graph once (the trailing call target
  of `Update`) to separate the dispatch tail from the shared conversion.
- The epoch constant at `0x005d8578` and the 200 ticks/unit scale — read the
  float and pin a focused parity test in `RetailEventScheduler`.
- The insertion-comparison axis in `AddEvent_AtTime` and the flush semantics in
  `Flush` — a retained-trace call-entry probe would name both.
