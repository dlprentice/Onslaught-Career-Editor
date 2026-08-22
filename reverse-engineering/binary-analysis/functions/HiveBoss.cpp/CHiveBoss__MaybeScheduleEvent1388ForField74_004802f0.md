# CHiveBoss__MaybeScheduleEvent1388ForField74_004802f0

> Address: `0x004802F0`

Status: active static function note
Last updated: 2026-08-22
Source File: none — `HiveBoss.cpp` is absent from `references/Onslaught/`
(checked 2026-08-22) | Binary: BEA.exe pristine specimen
`local-lab/safe-copy-bea-pristine/BEA.exe.original.backup`, SHA-256
`74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`
Summary: CHiveBoss's slot-50 destruction override. It returns 0 immediately
when `CUnit__MarkDestroyedAndCleanupLinks` reports an already-dying receiver.
On a fresh transition it optionally schedules event `0x1388` for the HiveBoss
at `NEXT_FRAME` when `[hiveBoss+0x74]` is live, then returns 1. Every teardown
side effect other than that schedule belongs to the shared CUnit callee.
Evidence: MEASURED — pristine SHA verified before complete-body disassembly
and hashing, whole-`.text` rel32 scan, image-wide imm32 census, RTTI/vtable
readback, and complete call/argument classification. No Ghidra or rebuild owner
changed.

## Contract (byte-exact)

Body `0x004802f0`–`0x00480331` inclusive through the complete plain `ret`,
**66 bytes / 26 instructions**, SHA-256
`97dfac69c4ae326b509e66edc15f1d5741b657b729681bce00682b2d82bb0a3c`.
It has **2 outbound direct `E8`, 0 `E9`, and 0 indirect calls**. Every branch
remains inside the body. Signature shape is
`int __thiscall ...(CHiveBoss *hiveBoss)`: no stack arguments are read. EAX is
0 on the shared callee's already-dying arm and explicit 1 after the fresh arm,
regardless of whether the optional event is scheduled.

## Stage law (byte-exact)

1. **Shared one-shot gate** (`0x004802f4`–`0x004802ff`): call
   [`CUnit__MarkDestroyedAndCleanupLinks`](../Unit.cpp/CUnit__MarkDestroyedAndCleanupLinks.md).
   If it returns 0, restore the saved registers and return that 0 without
   reading `[hiveBoss+0x74]` or scheduling an event.
2. **Optional HiveBoss event** (`0x00480300`–`0x00480325`): read
   `[hiveBoss+0x74]`. If null, skip the call. If live, call global event manager
   `0x00672fc8` at `CEventManager__AddEvent_AtTime 0x0044b370` with event number
   `0x1388`, the HiveBoss, exact float `-1.0f` (`0xbf800000`, `NEXT_FRAME`), and
   zero-valued remaining tuple slots.
3. **Fresh-transition result** (`0x0048032a`): set EAX to 1 and return.

The shared CUnit body fires its own script event id 5 before it returns and
before this wrapper's event `0x1388` is enqueued. The two event numbers and
their owners are distinct: event id 5 is shared teardown behavior; the
next-frame `0x1388` schedule is the only CHiveBoss-specific effect here.

## Outbound calls

| Site | Callee / role |
| --- | --- |
| `0x004802f4` | `CUnit__MarkDestroyedAndCleanupLinks 0x004fd140` |
| `0x00480325` | `CEventManager__AddEvent_AtTime 0x0044b370` |

## References and slot ownership

The whole-`.text` rel32 scan finds **zero** inbound `E8`/`E9` references.
The image-wide imm32 census finds exactly **one** dword containing
`0x004802f0`: `0x005e17a8`. It is byte offset `+0xc8`, slot 50, in vtable
`0x005e16e0`; the Complete Object Locator resolves `.?AVCHiveBoss@@`.
Therefore this is the direct CHiveBoss slot-50 body, reached virtually in this
image rather than by a direct rel32 call.

The destroyable-segments controller constructor has already proved CHiveBoss
as one of its two concrete owners. When shared cleanup calls that controller's
eligible core-cascade path, the nested ordinary controller callback to this
same slot is rejected by the TF_DYING one-shot gate. This wrapper adds no
second segment cascade.

## Shared versus subclass-specific law

The TF_DYING guard/store, sound stop, profile accounting, segment cascade,
script event id 5, active-reader clear, and linked-set drain all belong to the
shared CUnit callee. CHiveBoss adds only the live-`+0x74` test and next-frame
`0x1388` schedule. Unlike
[`CBuilding__VFunc_50_00417a40`](../Building.cpp/CBuilding__VFunc_50_00417a40.md)
and
[`CTentacle__VFunc_50_004f1050`](../Tentacle.cpp/CTentacle__VFunc_50_004f1050.md),
this body does not release child units, create an explosion, write a subclass
field, or dispatch an indirect initializer. Slot number 50 identifies
placement; the bytes establish the destruction semantics.

## Open questions

- The runtime handler and authored gameplay meaning of event `0x1388` are not
  established by this wrapper. Static evidence proves only the exact enqueue
  tuple and ordering.
- The reason the enqueue is gated by `[hiveBoss+0x74]` remains source-absent.
- This body never reads `[unit+0x88]`; the separate cooldown-reader question is
  not part of this family.

## Cheapest falsifier

Any one of:

- Body SHA-256 over `0x004802f0`–`0x00480331` is not
  `97dfac69…bb0a3c`, or the final instruction stops being plain `ret`.
- The reference census is not zero rel32 plus the single CHiveBoss slot-50
  dword at `0x005e17a8`.
- Shared cleanup returning 0 reaches the `+0x74` read, or a fresh transition
  returns anything other than 1.
- The event call stops using immediate `0x1388`, receiver `hiveBoss`, or exact
  `-1.0f` next-frame time.

## Receipts

- 2026-08-22 — official pristine specimen above, SHA verified before reading.
  Reproduced the complete body/hash, both direct calls, zero inbound rel32
  references, sole RTTI-backed slot-50 dword, result polarity, and exact event
  gate/order with the read-only PE/capstone probe.
- Related contracts:
  [`../Unit.cpp/CUnit__MarkDestroyedAndCleanupLinks.md`](../Unit.cpp/CUnit__MarkDestroyedAndCleanupLinks.md),
  [`../DestructableSegmentsController.cpp/CDestructableSegmentsController__TriggerCoreCascadeIfEligible.md`](../DestructableSegmentsController.cpp/CDestructableSegmentsController__TriggerCoreCascadeIfEligible.md).
