# CUnit__HandleEvent

> Address: `0x004F9820`

Status: active static function note
Last updated: 2026-08-22
Source File: none — `Unit.cpp` is absent from `references/Onslaught/`
(checked 2026-08-22) | Binary: BEA.exe pristine specimen
`local-lab/safe-copy-bea-pristine/BEA.exe.original.backup`, SHA-256
`74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`
Summary: shared CUnit slot-0 event handler. It switches on signed 16-bit event
IDs 4001–4005, with direct arms for 4001, 4003, 4004, and 4005; 4002 and all
other values fall through `CActor__HandleEvent`. Event `0x0fa4` (4004) calls
`CUnit__SpawnProfileDropPickup` and then virtual slot 14. The proved
CComponent/CGillMHead and CWarspite/CGillM/CThunderHead/CMech producer vtables
resolve that slot to `CComplexThing__AddShutdownEvent`, so their delayed 4004
is a drop-plus-shutdown-finalization trigger, not an unresolved no-op.
Evidence: MEASURED — pristine identity, complete-body decode/hash, jump-table
readback, whole-`.text` rel32 census, image-wide operand census, strict relevant
vtable reads, current 8,329-row name table, and existing manager/thing owners.
No Ghidra or rebuild owner changed.

## Contract (byte-exact)

Body `0x004f9820`–`0x004f9997` inclusive through the final `ret 4`,
**376 bytes / 122 instructions**, raw SHA-256
`89bc4639211037324016dcb9d7a20198cad82ce8e5981a936948ef4b4d513f13`.
It has **6 outbound direct `E8`, 0 outbound `E9`, and 2 indirect call sites**.
All branches remain in the body except the five-entry jump-table fetch from
`0x004f9998`. Signature shape is
`void __thiscall ...(CUnit *unit, CScheduledEvent *event)`: it reads the signed
word at `[event+0x04]`, consumes one stack argument with `ret 4`, and returns no
status.

The dispatch index is `event_num - 4001`; values above unsigned index 4 use the
default. The exact jump table is:

| ID | Target | Bounded arm |
| ---: | --- | --- |
| 4001 (`0x0fa1`) | `0x004f9844` | call `CUnit__UpdateFireControlYawAndQueueEvent` |
| 4002 (`0x0fa2`) | `0x004f9988` | default to `CActor__HandleEvent` |
| 4003 (`0x0fa3`) | `0x004f98a8` | update `+0x110` from the bounded nearby/global scan, then reschedule 4003 through `AddEvent_TimeFromNow` |
| 4004 (`0x0fa4`) | `0x004f9972` | profile-drop pickup, then receiver slot 14 |
| 4005 (`0x0fa5`) | `0x004f9854` | decrement `+0x218` by `+0x21c`, reschedule 4005 for `NEXT_FRAME` while positive, else clear it |

The table describes static branch/callee effects; it does not assign missing
source enum spellings to 4001, 4003, or 4005.

## Event 0x0FA4 handler (byte-exact)

At `0x004f9972`–`0x004f9985` the handler:

1. calls `CUnit__SpawnProfileDropPickup 0x004fd230` on the receiver;
2. reloads the receiver vtable and calls byte offset `+0x38` (slot 14);
3. returns `void` with `ret 4`.

Relevant strict vtable reads are:

| Class / vtable | Slot 0 | Slot 14 |
| --- | --- | --- |
| CComponent / `0x005e3d40` | `CUnit__HandleEvent 0x004f9820` | `CComplexThing__AddShutdownEvent 0x004f43d0` |
| CGillMHead / `0x005e41f8` | `CUnit__HandleEvent 0x004f9820` | `CComplexThing__AddShutdownEvent 0x004f43d0` |
| CPod / `0x005dff8c` | `CUnit__HandleEvent 0x004f9820` | `CComplexThing__AddShutdownEvent 0x004f43d0` |
| CWarspite / `0x005e0684` | `CUnit__HandleEvent 0x004f9820` | `CComplexThing__AddShutdownEvent 0x004f43d0` |
| CGillM / `0x005e0b30` | `CUnit__HandleEvent 0x004f9820` | `CComplexThing__AddShutdownEvent 0x004f43d0` |
| CThunderHead / `0x005e0fe0` | `CUnit__HandleEvent 0x004f9820` | `CComplexThing__AddShutdownEvent 0x004f43d0` |
| CMech / `0x005e3074` | `CUnit__HandleEvent 0x004f9820` | `CComplexThing__AddShutdownEvent 0x004f43d0` |

The CComponent scheduler therefore reaches this exact arm after its 7.0-second
manager-clock delay. The separately closed
[`CMech__VFunc_50_004a00a0`](../Mech.cpp/CMech__VFunc_50_004a00a0.md)
producer reaches it after 3.5 seconds for each of the four Mech-family vtables
above. The slot-14 callee calls the script event-id-3/delete path when
applicable, sets TF_DECLARED_SHUTDOWN, and schedules thing-event 2000 at
`NEXT_FRAME`; that downstream tuple and 2000 consumer are owned by
[`CComplexThing.cpp.md`](../CComplexThing.cpp.md).

## Event-4004 producer census

The pristine image contains three little-endian `a4 0f 00 00` occurrences:

| Immediate site | Owner / classification | Exact tuple context |
| --- | --- | --- |
| `0x0042898d` | [`CComponent__HandleTriggerEventAndMoveToOffset`](../Component.cpp/CComponent__HandleTriggerEventAndMoveToOffset.md) | `AddEvent_AtTime(4004, component, mTime+7.0f, 0, null, null)` at `0x00428997` |
| `0x004a0103` | [`CMech__VFunc_50_004a00a0`](../Mech.cpp/CMech__VFunc_50_004a00a0.md) | after fresh `CGroundUnit__MarkDestroyedAndResetState` and `CUnit__ReleaseChildUnits`, `AddEvent_AtTime(4004, mech, mTime+3.5f, 0, null, null)` at `0x004a010d` |
| `0x005c6928` | `HResultToString` | `mov ecx,0xfa4` in an HRESULT switch; not an event or scheduler call |

Thus there are exactly **two** event-4004 producers in pristine `.text`, both
self-targeting Unit-family destruction paths, and one unrelated HRESULT
constant. This supports the behavioral label “delayed profile-drop plus
shutdown finalization”; no absent `Unit.cpp` enum spelling is claimed.

## Event-2000 default chain used by the cleanup helper

[`CUnit__ResetDeploymentGraphAndScheduleEvent`](CUnit__ResetDeploymentGraphAndScheduleEvent.md)
queues 2000 against the same CUnit. That value misses this 4001–4005 switch and
uses the default call at `0x004f998b`:

```text
CUnit__HandleEvent
  -> CActor__HandleEvent 0x004019e0 (2000 misses 3000/3001)
  -> CComplexThing__HandleEvent 0x004f4300
  -> 2000 SHUTDOWN arm
  -> receiver virtual slot 2
```

CComponent, CGillMHead, CPod, CWarspite, CGillM, CThunderHead, and CMech slot-2
entries are `CUnit__VFunc02_CleanupWorldLinksAndForward 0x004f95d0`. The shared event
manager only delivers slot 0; the ID interpretation and these class effects
belong to the handler chain.

## Outbound calls

| Site | Callee / role |
| --- | --- |
| `0x004f9847` | `CUnit__UpdateFireControlYawAndQueueEvent 0x004fb280` |
| `0x004f9889` | `CEventManager__AddEvent_AtTime 0x0044b370` (4005) |
| `0x004f9924` | `Random__NextLCGAbs 0x004de8d0`, used by the 4003 delay calculation |
| `0x004f9964` | `CEventManager__AddEvent_TimeFromNow 0x0044b2d0` (4003) |
| `0x004f9974` | `CUnit__SpawnProfileDropPickup 0x004fd230` (4004) |
| `0x004f998b` | `CActor__HandleEvent 0x004019e0` (default) |
| `0x004f98d3` | indirect global-object slot 0 in the bounded 4003 scan |
| `0x004f997d` | receiver slot 14 in the 4004 arm |

## References and slot ownership

The whole-`.text` rel32 census finds four direct callers:

| Site | Current name-table owner |
| --- | --- |
| `0x0040c29b` | `CBattleEngine__HandleEvent` default |
| `0x0041512d` | `CBoat__VFunc_0_00415120` |
| `0x00417e27` | `SharedUnitVFunc__HandleType1388Field74Resource_00417df0` |
| `0x0044e250` | `CFenrir__VFunc_0_0044e240` |

Scheduled events normally arrive virtually, not through those calls. The
image-wide operand census finds **28** `.rdata` dwords equal to `0x004f9820`,
all slot-0 entries in the current static closure; the relevant CComponent,
CGillMHead, CPod, and four Mech-family entries are listed above.

## Manager boundary and failure behavior

The manager delivers due records with `target->vtable[0](target, event)` and
owns queue allocation/ordering. This handler owns numeric interpretation and
Unit effects. All handler arms are source-void. A prior scheduler failure is
not observable here because `AddEvent_AtTime` returns no success flag; likewise,
this handler does not report whether its downstream slot-14 shutdown event was
successfully queued.

## Open questions

- `Unit.cpp` and its event enum are absent, so the authored names of 4001,
  4003, 4004, and 4005 remain unavailable. The 4004 behavioral effect is
  byte-closed without inventing that spelling.
- The profile-drop callee's concrete authored table/loot meaning and runtime
  outcome remain bounded to its existing named static owner.
- Runtime frequency and exact gameplay presentation of either 4004 producer,
  and direct rebuild parity, are not established by this static chain.

## Cheapest falsifier

Any one of:

- Raw body SHA-256 over `0x004f9820`–`0x004f9997` is not
  `89bc4639…d513f13`, the body is not 376 bytes / 122 instructions, or the
  final instruction stops being `ret 4`.
- Jump-table entry 3 stops targeting `0x004f9972`, or that arm stops calling
  `CUnit__SpawnProfileDropPickup` followed by receiver slot 14.
- The 4004 operand census stops being the two scheduler pushes plus the one
  unrelated HRESULT constant above.
- CComponent/CGillMHead or any of the four Mech-family slot 0 / slot 14 pairs no
  longer resolves to the named handler/callee pair above.
- Event 2000 no longer follows the Unit → Actor → ComplexThing shutdown chain.

## Reproduction

Run read-only from the repository root after verifying the official specimen:

```text
sha256sum C:/Users/david/source/Onslaught-Career-Editor/local-lab/safe-copy-bea-pristine/BEA.exe.original.backup
py -3 tools/disasm_va.py C:/Users/david/source/Onslaught-Career-Editor/local-lab/safe-copy-bea-pristine/BEA.exe.original.backup 0x004f9820 --count 122 --bytes
py -3 tools/pe_read_va.py C:/Users/david/source/Onslaught-Career-Editor/local-lab/safe-copy-bea-pristine/BEA.exe.original.backup 0x004f9998 --count 20 --as u32
py -3 tools/call_xref_scan.py C:/Users/david/source/Onslaught-Career-Editor/local-lab/safe-copy-bea-pristine/BEA.exe.original.backup 0x004f9820 0x004019e0 0x004f4300
py -3 tools/operand_scan.py C:/Users/david/source/Onslaught-Career-Editor/local-lab/safe-copy-bea-pristine/BEA.exe.original.backup 0x00000fa4 0x004f9820 --window 8
```
