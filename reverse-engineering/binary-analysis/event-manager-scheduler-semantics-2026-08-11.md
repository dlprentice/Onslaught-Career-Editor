# Event-manager scheduler semantic recovery

Status: active, bounded semantic recovery
Last updated: 2026-08-11
Evidence: MEASURED — complete pristine retail bodies, constants, branch
predicates, call order, state writes, and fourteen normalized-identical PC demo
twins; SOURCE — pinned `eventmanager.cpp`, `eventmanager.h`, `event.h`, and
`scheduledevent.h`; UNKNOWN — callback runtime coverage and platform timing
jitter outside the fixed game clock.
Verdict: the twelve manager functions and two scheduled-event record functions
have recovered identities, and the released 20 Hz ring/overflow scheduling law
is closed statically.

Specimen: pristine PC retail `BEA.exe`, SHA-256
`74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`;
PC demo `BEA.exe`, SHA-256
`d8637dd755b21c720c0cb8f71923f94d2a04a184d90f5343c2e868ce8606e5c2`.

## Result

The subsystem covers 2,186 retail bytes and 747 decoded instructions. Every
body has an independently linked demo twin with zero normalized instruction
differences; only 146 raw bytes differ, all inside encoded immediate or
displacement spans. The machine-readable result is
[`event-manager-scheduler-semantics-2026-08-11.tsv`](event-manager-scheduler-semantics-2026-08-11.tsv).
That 3,622-byte table has SHA-256
`73587c4b138a6310a3139012ec6db2384aa6903acb3a63d5b52e2fa9c970c7b6`.

The retained implementation is `references/Onslaught/eventmanager.cpp`, 14,523
bytes, SHA-256
`613f4628471bbc3206f61dcfa9718dc6799f56e759fa7776a5fad204ba7af893`.
Its interface is `references/Onslaught/eventmanager.h`, 3,491 bytes, SHA-256
`57f39c8c9b3c413c16d0fc2b75237b1b045cd1754fd7245f871639b7518f5afc`.
The event-record setters/destructor are independently fixed by
`references/Onslaught/scheduledevent.cpp`, 907 bytes, SHA-256
`510107937400260de4bb233483da6b01a6dd5da4b1584bd3c2e8f32118ad447e`.
Released decompiles are retained under
`local-lab/ghidra-fullpass-2026-07-23/exports/W003/decompile/` and
`local-lab/ghidra-fullpass-2026-07-23/exports/W007/decompile/`.

## Released scheduler law

Initialization allocates 20,000 `CScheduledEvent` records of exactly 20 bytes,
links them into an intrusive free list, creates the sorted overflow container,
zeros all counters, and marks the manager valid. Shutdown clears every one of
the 200 frame buckets at each of three priorities, destroys overflow storage
and the pool, and invalidates the manager.

Each 20-byte record carries two deletion-aware `CActiveReader` links, a 16-bit
event number, a 16-bit reuse flag, and a union holding either execution time or
the next free-list pointer. `CScheduledEvent::Set` registers the destination and
data readers and clears reuse; destruction unregisters both readers and
decrements the static record count.

Absolute scheduling at `0x0044B370` uses these exact branches:

- an invalid manager or null destination is rejected;
- times no later than `current_time + 0.051` enter the current ring bucket;
- negative time is normalized to `current_time + 0.0001`;
- times above `1,000,000` seconds are discarded;
- other delays compute `floor((time - current_time - 0.001) * 20)`;
- offsets `0..197` enter `(current_buffer + offset) % 200` at priority
  `0`, `1`, or `2`; offsets `>=198` enter the time-sorted overflow list;
- a reused event keeps ownership with the callback path, while a new event is
  popped from the fixed free list. Pool exhaustion is reported and the event is
  not scheduled.

`Update` always advances time before flushing. `AdvanceTime` increments the
frame counter, derives time as `frame_count * 0.05`, marks the old current
bucket ready, and advances the insertion bucket modulo 200. The retail
decompiler exposes the division quotient as a return value, but retained source
and all callers establish a source-void method; that register value is not an
interface contract.

`Flush` executes the ready ring bucket in priority order `0`, `1`, `2`. Before
each callback it clears the event's reuse flag. A callback may reschedule that
same record, setting reuse again; cleanup returns only non-reused records to the
free list. Due overflow events execute after all three ring priorities and use
the strict predicate `event_time < current_time`, not `<=`. This explains why a
long-delay event exactly aligned to a nominal tick can cross on the following
flush, while ordinary ring events use their selected frame bucket. Processed,
live, frame, and total-dispatch counters are updated separately, and developer
mode verifies that overflow entries remain time-sorted.

## Boundary

This closes scheduler structure, ordering, thresholds, ownership, and clock
arithmetic. It does not prove that every registered callback executes in a
particular gameplay trace, nor does it assign semantics to each numeric event
ID. OS scheduling jitter is irrelevant to the fixed manager clock but can still
affect how many game updates a presentation frame performs. PS2/Xbox compiler
output has not yet been paired instruction-for-instruction.
