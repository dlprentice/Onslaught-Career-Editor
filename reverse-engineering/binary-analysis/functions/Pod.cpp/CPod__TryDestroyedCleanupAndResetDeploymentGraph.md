# CPod__TryDestroyedCleanupAndResetDeploymentGraph

> Address: `0x004D38C0`

Status: active static function note
Last updated: 2026-08-22
Source File: none — `Pod.cpp` is absent from `references/Onslaught/`
(checked 2026-08-22) | Binary: BEA.exe pristine specimen
`local-lab/safe-copy-bea-pristine/BEA.exe.original.backup`, SHA-256
`74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`
Summary: CPod's slot-50 destruction override. It calls
`CUnit__MarkDestroyedAndCleanupLinks` first and returns 0 unchanged when the Pod
is already dying. On a fresh transition it invokes
`CUnit__ResetDeploymentGraphAndScheduleEvent` and returns 1. The helper, not
this wrapper, owns the deployment-node/script/drop work and queues thing-event
2000 (`SHUTDOWN`) for this Pod at `mTime+0.05f`.
Evidence: MEASURED — pristine SHA verified before complete-body disassembly and
raw hashing, whole-`.text` rel32 scan, image-wide aligned-imm32 census, strict
MSVC RTTI/vtable readback, and complete call classification. No Ghidra or
rebuild owner changed.

## Contract (byte-exact)

Body `0x004d38c0`–`0x004d38db` inclusive through the complete plain `ret`,
**28 bytes / 12 instructions**, raw SHA-256
`3ad54ca8234b0dcb6716a828eae6a387492d977bc114afa8787ffd556f2d776f`.
It has **2 outbound direct `E8`, 0 outbound `E9`, and 0 indirect calls**. Both
branches remain inside the body. Signature shape is
`int __thiscall ...(CPod *pod)`: no stack arguments are read. EAX is the shared
cleanup's 0 on the already-dying arm and explicit 1 after the fresh helper call.

## Stage law (byte-exact)

1. **Shared one-shot gate** (`0x004d38c3`–`0x004d38cd`): call
   [`CUnit__MarkDestroyedAndCleanupLinks`](../Unit.cpp/CUnit__MarkDestroyedAndCleanupLinks.md).
   If it returns 0, restore ESI and return that 0 without entering the
   deployment-graph helper.
2. **Pod-specific continuation** (`0x004d38ce`–`0x004d38d4`): on a fresh
   transition, call current saved
   [`CUnit__ResetDeploymentGraphAndScheduleEvent`](../Unit.cpp/CUnit__ResetDeploymentGraphAndScheduleEvent.md)
   `0x004fd040` on the same Pod.
3. **Fresh-transition result** (`0x004d38d5`–`0x004d38db`): set EAX to 1,
   restore ESI, and return. The helper's incidental EAX does not escape.

The separately named 250-byte helper walks/removes its deployment-node set,
clears readers/links, performs the profile-drop and attached-script teardown,
then schedules `(event=0x07d0, target=this, time=&local(mTime+slot112()),
priority=0, data=null, reuse=null)`. CPod vtable `0x005dff8c` resolves slot 112
to `CUnit__ReturnFloat005d8578_00405ea0`, whose exact body returns `0.05f`.
Those operations and the source-void queue failure boundary are helper-owned;
this 28-byte wrapper proves only fresh-only invocation and ordering after shared
CUnit teardown.

## Outbound calls

| Site | Callee / role |
| --- | --- |
| `0x004d38c3` | `CUnit__MarkDestroyedAndCleanupLinks 0x004fd140` |
| `0x004d38d0` | [`CUnit__ResetDeploymentGraphAndScheduleEvent`](../Unit.cpp/CUnit__ResetDeploymentGraphAndScheduleEvent.md) `0x004fd040` |

## References and slot ownership

The whole-`.text` rel32 scan finds **zero** inbound `E8`/`E9` references. The
image-wide aligned-dword census finds exactly **one** copy of `0x004d38c0`:
`0x005e0054`. The strict RTTI census resolves it as byte offset `+0xc8`, slot
50, in CPod vtable `0x005dff8c`. Therefore this is the direct CPod slot-50 body,
reached virtually in the pristine image.

## Shared versus Pod-specific law

The TF_DYING guard/store, sound stop, profile accounting, destroyable-segment
cascade, script event id 5, active-reader clear, and linked-set drain belong to
the shared CUnit callee. CPod adds only the fresh-only call to the separate
deployment-graph/event helper. It does not directly release child units, clear
a Pod field, create an effect, or schedule an event in this wrapper. Shared
result 0 suppresses the helper; every fresh completion returns explicit 1.

## Event-2000 dispatch boundary

`CEventManager__Flush` delivers the helper's due record through the Pod's slot
0, `CUnit__HandleEvent 0x004f9820`. Event 2000 misses the Unit 4001–4005 switch,
then misses `CActor__HandleEvent`'s 3000/3001 switch and reaches
`CComplexThing__HandleEvent`'s source-named `SHUTDOWN` arm. Because the helper
already nulled Pod `+0x74`, that arm cannot repeat the optional script callback;
it calls Pod slot 2, `CUnit__VFunc02_CleanupWorldLinksAndForward 0x004f95d0`.
The exact route is owned by
[`CUnit__HandleEvent`](../Unit.cpp/CUnit__HandleEvent.md).

The manager owns fixed 20 Hz time, ring placement, allocation, and failure
handling. The helper supplies one-tick absolute due time. The Pod wrapper still
returns 1 if the manager is invalid or its free-event pool is exhausted,
because the scheduler is source-void and the wrapper does not observe status.

## Open questions

- The authored Pod states that populate the helper-owned deployment graph are
  not established by this wrapper.
- Event `0x07d0` and the Pod virtual delay are now statically closed as
  `SHUTDOWN` at `mTime+0.05f`; runtime presentation and rebuild parity remain
  unproved.

## Cheapest falsifier

Any one of:

- Raw body SHA-256 over `0x004d38c0`–`0x004d38db` is not
  `3ad54ca8…2d776f`, or the final instruction stops being plain `ret`.
- The reference census is not zero rel32 plus the sole CPod slot-50 dword at
  `0x005e0054`.
- Shared cleanup returning 0 reaches the helper, the helper moves before shared
  cleanup, or a fresh transition returns anything other than 1.
- CPod slot 112 stops returning `0.05f`, slot 0 stops reaching the Unit/Actor/
  ComplexThing 2000 shutdown chain, or slot 2 stops resolving to `0x004f95d0`.

## Receipts

- 2026-08-22 — official pristine specimen above, SHA verified before reading.
  Reproduced the complete body/hash, both direct calls, zero inbound rel32
  references, sole strict slot-50 entry, result polarity, and helper ordering
  with read-only PE/capstone/RTTI probes.
- 2026-08-22 event-chain closure — re-read the helper's complete body/hash,
  exact queue tuple, CPod slot-112 `0.05f`, manager delivery, and the named
  Unit → Actor → ComplexThing `SHUTDOWN` consumer chain.
- Related contract:
  [`../Unit.cpp/CUnit__MarkDestroyedAndCleanupLinks.md`](../Unit.cpp/CUnit__MarkDestroyedAndCleanupLinks.md).
