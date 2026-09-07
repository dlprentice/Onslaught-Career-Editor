# Event scheduler and active readers

Status: active — source map and bounded retail static contract
Last updated: 2026-09-07
Summary: event admission, dispatch order, recycling and reader lifetimes; exact
scheduler body checks support the Core implementation without establishing
whole-game runtime parity.
Evidence: MEASURED pristine instructions and focused Core tests;
SOURCE-INFORMED names from pinned `references/Onslaught` commit
`5352a81cdb838b145a57f7febc5d9fc4b0129ebb`. The separately retained runtime
contract below remains a candidate and was not replayed or promoted here.
Specimen: `local-lab/safe-copy-bea-pristine/BEA.exe.original.backup`, 2,506,752
bytes, SHA-256
`74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`.

## Owners and evidence

The pinned source owners are
[`eventmanager.cpp`](../../../references/Onslaught/eventmanager.cpp),
[`eventmanager.h`](../../../references/Onslaught/eventmanager.h),
[`event.h`](../../../references/Onslaught/event.h), and
[`scheduledevent.h`](../../../references/Onslaught/scheduledevent.h).
`CEvent` holds a destination reader and signed 16-bit event number;
`CScheduledEvent` adds a data reader, reuse flag and time/free-link union.
`CEventManager` owns their pool, ring and time-ordered overflow list.

The existing [scheduler semantic crosswalk](../../binary-analysis/event-manager-scheduler-semantics-2026-08-11.tsv)
records source/retail/demo body comparisons. The September 7 readback checked
these complete bodies against PE-mapped pristine bytes using retained
`local-lab/ghidra-fullpass-2026-07-23/exports/W003/instructions.tsv`:

| Body, half-open | Bytes / instruction rows | Raw body SHA-256 |
| --- | ---: | --- |
| `Init [0x0044b060,0x0044b185)` | 293 / 85 | `4b75a4fcc8bb250ed01a34d90def65a0ad268345670274f07af55983b9edc9b9` |
| Relative `AddEvent [0x0044b2d0,0x0044b303)` | 51 / 18 | `d57456182657dbf16c4a79e1ec5c1f348d7c18663bfc1f79c87ef3e54602f450` |
| `Flush [0x0044b640,0x0044b837)` | 503 / 191 | `84e5ad90944eb1b99461b10f839d1a3101b321f605094c959da57086ae93a2b4` |

All 294 selected instruction rows matched. No Ghidra project was opened.
This checks retained instruction bytes and static control flow; it does not
observe a live listener or recover a deleted recording.

The [absolute AddEvent contract](../../contracts/engine-world/CEventManager__AddEvent_AtTime__0044b370.md)
owns the earlier, bounded Level-100 queue observations and their refuters.
Those retained extracts are not new runtime validation, and their C2 candidate
status does not change with this static update.

## Admission and clock

`eventmanager.cpp:170-279` and the crosswalk identify the absolute scheduler
at `0x0044b370`. An invalid manager or null listener is rejected. For a valid
request, the branches are:

1. At or before `mTime + 0.051f`, append to the current ring slot. A negative
   request, including `NEXT_FRAME = -1.0f`, stores `mTime + 0.0001f` rounded
   to float32 as its due time.
2. On the later-time arm, reject requested times over `1,000,000.0f`.
   Otherwise compute `floor((requested - mTime - 0.001f) * 20)`.
3. Offsets below 198 select a wrapped ring slot. Offsets of 198 or greater
   enter the sorted overflow list. The ring has 200 slots, but its admission
   boundary is not a simple ten-second comparison.

The three ring lanes are `START_OF_FRAME = 0`, `MIDDLE_OF_FRAME = 1`, and
`END_OF_FRAME = 2`. They specify ordering inside `Flush`; these names do not
prove separate placement before physics, during update, or after rendering.
Ring insertion is FIFO within a lane. Overflow insertion begins at the current
processing cursor and puts a new event after existing equal-time events.

Relative `AddEvent` (`eventmanager.cpp:143-146`) adds the current manager time
on the x87 stack, then **stores the sum as float32 at `0x0044b2f6` before the
call at `0x0044b2fb`**. It is not an unrounded tail-call forwarder. The
absolute scheduler's delay calculation has no intermediate float32 stores;
Core uses double intermediates for the expected 53-bit precision mode. This
body alone does not establish every caller's runtime x87 control word.

`AdvanceTime` (`eventmanager.cpp:293-304`, `0x0044b600`) increments the frame
count, stores `frameCount * 0.05f` as float32, marks the old ring slot ready,
and rotates the current slot modulo 200. It does not accumulate repeated
`+0.05f`. Source returns `void`; an incidental register value after the modulo
operation is not a supported wrap-flag return contract. `Update` calls
`AdvanceTime` and then `Flush`.

## Dispatch and reuse

`eventmanager.cpp:311-411` and the checked `Flush` body establish this order:

1. Visit the ready ring slot's lanes 0, 1 and 2 in order.
2. Snapshot the overflow count **after ring callbacks and before overflow
   callbacks** (`mov edi,[ecx+8]` at `0x0044b6bf`). Walk from the overflow
   cursor while it is below that captured count and due time is **strictly
   less than** the current manager time. The loop compares the same `EDI`
   at `0x0044b6fb`; it does not reread the count after each callback.
3. Recycle visited ring records, then the visited overflow prefix, and update
   counters. An overflow record executes after all ring lanes regardless of
   its originally requested priority.

Each visited record has reuse cleared before the callback. The overflow
cursor advances before its callback, which constrains subsequent insertion.
A null destination skips the callback but still counts as processed.
Cleanup frees records that were not rearmed and decrements the live-event
count for every visited entry. Rearming through the supplied handle therefore
preserves the record without leaking the live count.

`Init` allocates `0x61a84 = 20,000 * 20 + 4` bytes, constructs 20,000 event
records, links 19,999 successors and terminates the free list with null.
This pool size was already measured in the earlier crosswalk and was checked
again here. It is not merely an unverified header constant. The pool avoids
per-record allocation; it does not prove that ring/list insertion or callbacks
perform no heap allocation. The reuse flag controls callback rearming, not a
general guarantee against all double frees.

## Active-reader lifetime boundary

[`activereader.cpp`](../../../references/Onslaught/activereader.cpp) and
[`activereader.h`](../../../references/Onslaught/activereader.h) describe
non-owning monitored references. Setting the same target is a no-op;
otherwise a reader unregisters from its old target, publishes the new pointer,
and registers with that target. A target's shutdown invalidates its registered
reader cells. An event checks its destination before calling it.

The [monitor owner](../../binary-analysis/functions/CMonitor.cpp.md) and
[deletion-list contract](../../contracts/engine-world/CMonitor__AddDeletionEvent__00401040.md)
retain the binary evidence and limits. The helper map is:

| Address | Operation |
| --- | --- |
| `0x00401000` | Set reader: detach old, assign, attach new |
| `0x00401040` | Add a reader cell to the monitor's lazily allocated deletion list |
| `0x0042d9b0` | Remove a reader cell from that list |
| `0x0044b1d0` | Reader destructor unregisters its cell |
| `0x004bac40` | Monitor shutdown nulls registered cells and releases its list |

A retail reader cell holds a 32-bit target pointer; the monitor's reverse-list
pointer is at `monitor+0x04`. The relationship appears in event destination
and data fields and in player, Battle Engine and camera references. It neither
owns the target nor makes unchecked dereferences universally safe.

These source owners define runtime pointers and scheduling records, not a
`.bes` byte layout. They provide no basis for writing pointer values into a
save or clearing unknown save bytes. Event-driven gameplay can still affect
results later saved by the career code; absence of event serialization is not
absence of indirect save effects. Save layout belongs to the
[save-format owner](../../save-file/save-format.md).

## Rebuild coverage and remaining limits

[`RetailEventScheduler`](../../../rebuild/OnslaughtRebuild.Core/RetailEventScheduler.cs)
models routing, the clock, dispatch and recycling with opaque listener IDs.
[`RetailActiveReaderGraph`](../../../rebuild/OnslaughtRebuild.Core/RetailActiveReaderGraph.cs)
models reader membership separately; it is not automatically wired into every
scheduler listener. Core's reusable `Init` also clears its containers; that
reset convenience is not proof that calling retail `Init` twice without
`Shutdown` is valid.

The focused `RetailEventSchedulerTests` fixture passed **32/32** on September 7.
`Flush_OverflowCallbacksCannotExtendTheCapturedVisitCount` failed before the
count-snapshot correction and passed afterward. It deliberately advances the
clock inside a caller-supplied callback so a newly appended event becomes due;
this distinguishes the static loop bound, not a witnessed retail listener
behavior. Logs are in
`local-data/test-runs/linux-route-20260906-af1sa_l9/scheduler-overflow-{red,green}.log`.
No broad Core result, native gameplay result, World-110 initialization closure,
or full parity claim follows from this focused check.
